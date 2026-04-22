"""Controller Storico — Logica Pagina 3."""

from datetime import date
from pathlib import Path

from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QMessageBox, QFileDialog

from views.history_view import HistoryView
from core.app_state import AppState
from core.period import get_period_for_date, clamp_day_to_month
from models.storage import Storage
from models.settings_model import SettingsModel
from models.model_model import ModelModel
from models.salary_model import SalaryModel
from models.expense_model import ExpenseModel

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


class HistoryController(QObject):
    """Controller per la pagina Storico.

    Gestisce:
    - Visualizzazione storico stipendi
    - Configurazione salary_day
    - Grafici comparativi (barre e linee)
    - Analisi trend per categoria
    """

    def __init__(self, view: HistoryView, data_path: Path, parent=None):
        super().__init__(parent)
        self._view = view
        self._data_path = data_path

        # Inizializza modelli
        self._storage = Storage(data_path)
        self._settings_model = SettingsModel(self._storage)
        self._model_model = ModelModel(self._storage)
        self._salary_model = SalaryModel(self._storage)
        self._expense_model = ExpenseModel(self._storage)

        # Ottieni riferimento all'AppState
        self._app_state = AppState.instance()

        # Stato corrente
        self._current_months: int = 3  # default 3 mesi

        # Configura la view
        self._setup_view()

        # Connetti ai segnali AppState
        self._app_state.settings_changed.connect(self.refresh)
        self._app_state.expenses_changed.connect(self.refresh)

    def _setup_view(self) -> None:
        """Collega i segnali della view ai metodi del controller."""
        self._view.salary_day_changed.connect(self._on_salary_day_changed)
        self._view.months_changed.connect(self._on_months_changed)
        self._view.export_requested.connect(self._on_export_requested)

    def refresh(self) -> None:
        """Aggiorna la view con i dati correnti."""
        # Ricarica i dati dal disco per avere spese aggiornate
        self._expense_model._load()
        self._salary_model._load()
        
        # Imposta salary_day
        salary_day = self._settings_model.get_salary_day()
        self._view.set_salary_day(salary_day)

        # Aggiorna storico stipendi
        self._update_salaries_table()

        # Aggiorna categorie
        self._update_categories()

        # Aggiorna grafici e tabelle
        self._update_charts_and_tables()

    def _update_salaries_table(self) -> None:
        """Aggiorna la tabella degli stipendi."""
        salaries = self._salary_model.get_all_salaries()

        # Prepara i dati per la view
        salaries_data = []
        for sal in reversed(salaries):  # Dal più recente
            try:
                sal_date = date.fromisoformat(sal["date"])
                period_start, period_end = get_period_for_date(
                    sal_date, self._settings_model.get_salary_day()
                )
                period_label = f"{period_start.strftime('%d/%m/%Y')} - {period_end.strftime('%d/%m/%Y')}"
                date_label = sal_date.strftime("%d/%m/%Y")
            except (ValueError, KeyError):
                period_label = "—"
                date_label = sal.get("date", "—")

            # Ottieni nome modello
            model = self._model_model.get_model_by_id(sal.get("model_id", ""))
            model_name = model["name"] if model else "Sconosciuto"

            salaries_data.append({
                "period": period_label,
                "date": date_label,
                "amount": sal.get("amount", 0),
                "model_name": model_name,
                "note": sal.get("note", "")
            })

        self._view.set_salaries(salaries_data)

    def _update_categories(self) -> None:
        pass  # rimosso — selettore categoria non più presente

    def _update_charts_and_tables(self) -> None:
        """Aggiorna grafici e tabelle in base ai filtri selezionati."""
        # Ottieni tutti gli stipendi ordinati per data (dal più recente)
        all_salaries = self._salary_model.get_all_salaries()
        
        # Ordina per data decrescente (più recente prima)
        all_salaries_sorted = sorted(
            all_salaries,
            key=lambda s: s.get("date", ""),
            reverse=True
        )
        
        # Prendi gli ultimi N stipendi (corrispondenti agli ultimi N mesi/periodi)
        salaries_in_range = all_salaries_sorted[:self._current_months]

        if not salaries_in_range:
            self._view.set_bar_chart_data([], [], [])
            return

        # Prepara dati per grafico a barre (ordina cronologicamente per il grafico)
        salaries_in_range.reverse()  # Dal più vecchio al più recente per il grafico
        self._update_bar_chart(salaries_in_range)

    def _update_bar_chart(self, salaries: list[dict]) -> None:
        """Aggiorna il grafico a barre."""
        periods = []
        budget_values = []
        spent_values = []

        for sal in salaries:
            try:
                sal_date = date.fromisoformat(sal["date"])
                period_start, period_end = get_period_for_date(
                    sal_date, self._settings_model.get_salary_day()
                )
                # Mesi italiani
                month_names = {
                    1: "Gen", 2: "Feb", 3: "Mar", 4: "Apr",
                    5: "Mag", 6: "Giu", 7: "Lug", 8: "Ago",
                    9: "Set", 10: "Ott", 11: "Nov", 12: "Dic"
                }
                period_label = f"{month_names[period_end.month]} {period_end.year}"
            except ValueError:
                continue

            periods.append(period_label)
            budget_values.append(sal["amount"])

            # Calcola totale speso per questo periodo
            total_spent = self._expense_model.get_total_by_period(sal["id"])
            spent_values.append(total_spent)

        self._view.set_bar_chart_data(periods, budget_values, spent_values)

    def _on_salary_day_changed(self, day: int) -> None:
        """Gestisce il cambio di salary_day."""
        self._settings_model.set_salary_day(day)
        self._app_state.settings_changed.emit()
        QMessageBox.information(
            self._view,
            "Impostazioni salvate",
            f"Il giorno dello stipendio è stato aggiornato a {day}."
        )

    def _on_months_changed(self, months: int) -> None:
        """Gestisce il cambio del numero di mesi."""
        self._current_months = months
        self._update_charts_and_tables()

    def _on_export_requested(self, months: int) -> None:
        """Gestisce la richiesta di esportazione PDF dello storico."""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        # Chiedi dove salvare il file
        file_path, _ = QFileDialog.getSaveFileName(
            self._view,
            "Esporta Storico",
            f"storico_{months}_mesi.pdf",
            "PDF Files (*.pdf)"
        )
        if not file_path:
            return

        try:
            self._generate_pdf(file_path, months)
            QMessageBox.information(
                self._view,
                "Esportazione completata",
                f"Lo storico è stato salvato in:\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self._view,
                "Errore",
                f"Errore durante l'esportazione:\n{str(e)}"
            )

    def _generate_pdf(self, file_path: str, months: int) -> None:
        """Genera il PDF con lo storico degli ultimi N mesi."""
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Stile personalizzato per il titolo
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20
        )

        # Stile per sottotitoli
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15
        )

        # Stile per normale testo
        normal_style = styles['Normal']

        # Ottieni tutti gli stipendi
        all_salaries = self._salary_model.get_all_salaries()
        all_salaries_sorted = sorted(all_salaries, key=lambda s: s.get("date", ""), reverse=True)
        salaries_in_range = all_salaries_sorted[:months]

        if not salaries_in_range:
            elements.append(Paragraph("Nessuno storico disponibile.", normal_style))
            doc.build(elements)
            return

        # Ordina cronologicamente (dal più vecchio al più recente)
        salaries_in_range.reverse()

        salary_day = self._settings_model.get_salary_day()

        for sal in salaries_in_range:
            try:
                sal_date = date.fromisoformat(sal["date"])
                period_start, period_end = get_period_for_date(sal_date, salary_day)
                period_label = f"{period_start.strftime('%d/%m/%Y')} - {period_end.strftime('%d/%m/%Y')}"
            except ValueError:
                continue

            # Titolo del periodo
            elements.append(Paragraph(
                f"Periodo: {period_label}",
                subtitle_style
            ))

            # Budget del periodo
            budget_text = f"Budget: € {sal['amount']:.2f}"
            elements.append(Paragraph(budget_text, normal_style))
            elements.append(Spacer(1, 10))

            # Spese del periodo
            expenses = self._expense_model.get_expenses_by_period(sal["id"])

            if expenses:
                # Crea tabella spese
                table_data = [["Data", "Descrizione", "Categoria", "Importo"]]
                category_names = {cat["id"]: cat["name"] for cat in self._model_model.get_categories_for_model(sal.get("model_id", ""))}

                for exp in expenses:
                    try:
                        exp_date = date.fromisoformat(exp["date"]).strftime("%d/%m/%Y")
                    except (ValueError, KeyError):
                        exp_date = "—"
                    cat_name = category_names.get(exp.get("category_id", ""), "—")
                    table_data.append([
                        exp_date,
                        exp.get("description", "—")[:40],
                        cat_name,
                        f"€ {exp.get('amount', 0):.2f}"
                    ])

                table = Table(table_data, colWidths=[4*cm, 7*cm, 4*cm, 3*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2196F3")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f5f5f5")),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
                ]))
                elements.append(table)

                # Totale speso
                total_spent = sum(exp.get("amount", 0) for exp in expenses)
                remaining = sal["amount"] - total_spent
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(f"Totale speso: € {total_spent:.2f}", normal_style))
                elements.append(Paragraph(f"Residuo: € {remaining:.2f}", normal_style))
            else:
                elements.append(Paragraph("Nessuna spesa registrata in questo periodo.", normal_style))

            elements.append(Spacer(1, 20))

        doc.build(elements)
