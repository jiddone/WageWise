"""Controller Spese — Logica Pagina 2."""

from datetime import date
from pathlib import Path

from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QMessageBox

from views.expenses_view import ExpensesView
from core.app_state import AppState
from core.period import get_current_period, format_period_label
from core.validators import validate_amount, validate_date_in_period
from models.storage import Storage
from models.settings_model import SettingsModel
from models.model_model import ModelModel
from models.salary_model import SalaryModel
from models.expense_model import ExpenseModel


class ExpensesController(QObject):
    """Controller per la pagina Registro Spese.

    Gestisce:
    - Inserimento e eliminazione spese
    - Visualizzazione residui per categoria
    - Avvisi per sforamenti budget
    - Filtro spese per categoria
    """

    def __init__(self, view: ExpensesView, data_path: Path, parent=None):
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
        self._current_salary_id: str = ""
        self._current_categories: list[dict] = []
        self._current_filter: str = "all"

        # Configura la view
        self._setup_view()

        # Connetti ai segnali AppState
        self._app_state.salary_changed.connect(self._on_salary_changed)
        self._app_state.model_changed.connect(self._on_model_changed)
        self._app_state.expenses_changed.connect(self.refresh)

    def _setup_view(self) -> None:
        """Collega i segnali della view ai metodi del controller."""
        self._view.expense_add_requested.connect(self._on_add_expense)
        self._view.expense_delete_requested.connect(self._on_delete_expense)
        self._view.filter_changed.connect(self._on_filter_changed)

    def refresh(self) -> None:
        """Aggiorna la view con i dati correnti."""
        # Ricarica i dati dal disco per avere categorie aggiornate
        self._model_model._load()
        self._salary_model._load()

        # Calcola il periodo corrente
        salary_day = self._settings_model.get_salary_day()
        period_start, period_end = get_current_period(salary_day)
        self._app_state.current_period = (period_start, period_end)

        # Aggiorna label periodo
        period_text = f"Periodo: {format_period_label(period_start, period_end)}"
        self._view.set_period_label(period_text)

        # Carica lo stipendio del periodo corrente
        salary = self._salary_model.get_salary_for_period(period_start, period_end)
        if salary:
            self._current_salary_id = salary["id"]
            self._app_state.current_salary = salary["amount"]
            self._view.set_add_button_enabled(True)

            # Usa il modello attivo dall'AppState (aggiornato dal DashboardController)
            active_model_id = self._app_state.current_model_id
            if not active_model_id:
                active_model_id = self._settings_model.get_active_model_id()
            self._current_categories = self._model_model.get_categories_for_model(active_model_id)
        else:
            self._current_salary_id = ""
            self._app_state.current_salary = 0.0
            self._view.set_add_button_enabled(False)
            QMessageBox.warning(
                self._view,
                "Nessuno stipendio",
                "Nessuno stipendio registrato per questo periodo.\nVai alla Dashboard per registrare lo stipendio."
            )
            # Se non c'è stipendio, usa il modello attivo dall'AppState
            active_model_id = self._app_state.current_model_id
            if not active_model_id:
                active_model_id = self._settings_model.get_active_model_id()
            self._current_categories = self._model_model.get_categories_for_model(active_model_id)

        # Aggiorna categorie nella view
        categories_for_combo = [
            {"id": cat["id"], "name": cat["name"], "color": cat["color"]}
            for cat in self._current_categories
        ]
        self._view.set_categories(categories_for_combo)

        # Aggiorna le card delle categorie
        self._update_category_cards()

        # Aggiorna la lista spese
        self._update_expenses_list()

        # Aggiorna riepilogo globale
        self._update_global_summary()

    def _update_category_cards(self) -> None:
        """Aggiorna le card delle categorie con i dati correnti."""
        if not self._current_salary_id:
            self._view.set_category_cards([])
            return

        # Ottieni lo stipendio
        salary = self._salary_model.get_salary_by_id(self._current_salary_id)
        if not salary:
            self._view.set_category_cards([])
            return

        salary_amount = salary["amount"]

        # Prepara i dati per le card
        cards_data = []
        for cat in self._current_categories:
            budget = (salary_amount * cat["percentage"]) / 100
            spent = self._expense_model.get_total_by_category(
                self._current_salary_id, cat["id"]
            )
            cards_data.append({
                "id": cat["id"],
                "name": cat["name"],
                "color": cat["color"],
                "budget": budget,
                "spent": spent
            })

        self._view.set_category_cards(cards_data)

    def _update_expenses_list(self) -> None:
        """Aggiorna la lista delle spese nella view."""
        if not self._current_salary_id:
            self._view.set_expenses([])
            return

        # Ottieni tutte le spese del periodo
        expenses = self._expense_model.get_expenses_by_period(self._current_salary_id)

        # Crea mappa id -> nome categoria
        category_names = {cat["id"]: cat["name"] for cat in self._current_categories}

        # Filtra se necessario
        if self._current_filter != "all":
            expenses = [e for e in expenses if e["category_id"] == self._current_filter]

        # Prepara i dati per la view
        expenses_data = []
        for exp in expenses:
            # Formatta la data
            try:
                exp_date = date.fromisoformat(exp["date"])
                formatted_date = exp_date.strftime("%d/%m/%Y")
            except ValueError:
                formatted_date = exp["date"]

            expenses_data.append({
                "id": exp["id"],
                "date": formatted_date,
                "description": exp.get("description", ""),
                "category_name": category_names.get(exp["category_id"], "Sconosciuta"),
                "amount": exp["amount"]
            })

        self._view.set_expenses(expenses_data)

    def _update_global_summary(self) -> None:
        """Aggiorna il riepilogo globale."""
        if not self._current_salary_id:
            self._view.set_global_summary(0, 0)
            return

        salary = self._salary_model.get_salary_by_id(self._current_salary_id)
        if not salary:
            self._view.set_global_summary(0, 0)
            return

        total_spent = self._expense_model.get_total_by_period(self._current_salary_id)
        total_budget = salary["amount"]

        self._view.set_global_summary(total_spent, total_budget)

    def _on_add_expense(self, amount_str: str, category_id: str,
                        description: str, date_str: str) -> None:
        """Gestisce l'aggiunta di una nuova spesa."""
        # Validazione importo
        is_valid, amount, error = validate_amount(amount_str)
        if not is_valid:
            QMessageBox.warning(self._view, "Errore", error)
            return

        if not self._current_salary_id:
            QMessageBox.warning(
                self._view,
                "Errore",
                "Nessuno stipendio registrato per questo periodo."
            )
            return

        # Validazione data nel periodo
        try:
            expense_date = date.fromisoformat(date_str)
            salary_day = self._settings_model.get_salary_day()
            period_start, period_end = get_current_period(salary_day)

            if not validate_date_in_period(expense_date, period_start, period_end):
                QMessageBox.warning(
                    self._view,
                    "Errore",
                    f"La data non rientra nel periodo corrente "
                    f"({period_start.strftime('%d/%m')} - {period_end.strftime('%d/%m')})"
                )
                return
        except ValueError:
            QMessageBox.warning(self._view, "Errore", "Data non valida.")
            return

        # Verifica sforamento budget
        salary = self._salary_model.get_salary_by_id(self._current_salary_id)
        if salary:
            category = next((c for c in self._current_categories if c["id"] == category_id), None)
            if category:
                budget = (salary["amount"] * category["percentage"]) / 100
                current_spent = self._expense_model.get_total_by_category(
                    self._current_salary_id, category_id
                )
                new_spent = current_spent + amount

                if new_spent > budget:
                    reply = QMessageBox.question(
                        self._view,
                        "Conferma sforamento",
                        f"Questa spesa farà sforare il budget di '{category['name']}' di "
                        f"{new_spent - budget:.2f} €. Vuoi continuare?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.No:
                        return

        # Aggiungi la spesa
        try:
            self._expense_model.add_expense(
                amount=amount,
                category_id=category_id,
                description=description,
                date_str=date_str,
                salary_period_id=self._current_salary_id
            )

            # Notifica cambiamento
            self._app_state.expenses_changed.emit()

            # Pulisci input
            self._view.clear_expense_inputs()

        except Exception as e:
            QMessageBox.critical(self._view, "Errore", f"Errore nel salvare la spesa: {str(e)}")

    def _on_delete_expense(self, expense_id: str) -> None:
        """Gestisce l'eliminazione di una spesa."""
        try:
            self._expense_model.delete_expense(expense_id)
            self._app_state.expenses_changed.emit()
        except Exception as e:
            QMessageBox.critical(self._view, "Errore", f"Errore nell'eliminare la spesa: {str(e)}")

    def _on_filter_changed(self, category_id: str) -> None:
        """Gestisce il cambio di filtro."""
        self._current_filter = category_id
        self._update_expenses_list()

    def _on_salary_changed(self, amount: float) -> None:
        """Reagisce ai cambiamenti di stipendio dall'AppState."""
        self.refresh()

    def _on_model_changed(self, model_id: str) -> None:
        """Reagisce ai cambiamenti di modello dall'AppState."""
        self.refresh()
