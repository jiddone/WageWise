"""Vista Storico — Pagina 3: Analisi Storica."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QScrollArea,
    QFrame, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from components.bar_chart import BarChart


class HistoryView(QWidget):
    """Pagina Storico per analisi nel tempo."""

    # Segnali emessi verso il controller
    salary_day_changed = pyqtSignal(int)  # nuovo salary_day
    months_changed = pyqtSignal(int)  # numero di mesi da visualizzare
    export_requested = pyqtSignal(int)  # richiesta esportazione PDF
    reset_data_requested = pyqtSignal()  # richiesta reset dati applicazione

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configura l'interfaccia utente."""
        # Layout principale con scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        self._main_layout = QVBoxLayout(container)
        self._main_layout.setContentsMargins(20, 20, 20, 20)
        self._main_layout.setSpacing(20)

        # Sezione: Configurazione salary_day
        self._setup_salary_day_section()

        # Sezione: Storico stipendi
        self._setup_salaries_history_section()

        # Sezione: Selettore periodo e categoria
        self._setup_period_selector_section()

        # Sezione: Grafico a barre
        self._setup_bar_chart_section()

        # Sezione: Esportazione PDF
        self._setup_export_section()

        # Sezione: Reset dati
        self._setup_reset_section()

        # Spazio finale
        self._main_layout.addStretch()

        scroll.setWidget(container)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

    def _setup_salary_day_section(self) -> None:
        """Configura la sezione per impostare il giorno dello stipendio."""
        group = QGroupBox("Configurazione Data Stipendio")
        layout = QHBoxLayout(group)
        layout.setSpacing(15)

        layout.addWidget(QLabel("Giorno del mese in cui ricevi lo stipendio:"))

        self._salary_day_spin = QSpinBox()
        self._salary_day_spin.setRange(1, 31)
        self._salary_day_spin.setValue(27)
        self._salary_day_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        layout.addWidget(self._salary_day_spin)

        self._save_salary_day_btn = QPushButton("Salva")
        self._save_salary_day_btn.clicked.connect(self._on_salary_day_changed)
        layout.addWidget(self._save_salary_day_btn)

        layout.addStretch()
        self._main_layout.addWidget(group)

    def _setup_salaries_history_section(self) -> None:
        """Configura la sezione storico stipendi."""
        group = QGroupBox("Storico Stipendi")
        layout = QVBoxLayout(group)

        self._salaries_table = QTableWidget()
        self._salaries_table.setColumnCount(4)
        self._salaries_table.setHorizontalHeaderLabels([
            "Periodo", "Data Accredito", "Importo €", "Modello"
        ])
        self._salaries_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self._salaries_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self._salaries_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._salaries_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self._salaries_table.setFrameShape(QFrame.Shape.NoFrame)
        self._salaries_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self._salaries_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._salaries_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._salaries_table.setAlternatingRowColors(True)
        # Nascondi barra di scorrimento verticale
        self._salaries_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._salaries_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(self._salaries_table)

        self._main_layout.addWidget(group)

    def _setup_period_selector_section(self) -> None:
        """Configura la sezione selettore periodo."""
        group = QGroupBox("Periodo di Analisi")
        layout = QHBoxLayout(group)
        layout.setSpacing(15)

        layout.addWidget(QLabel("Mostra: ultimi"))

        self._months_spin = QSpinBox()
        self._months_spin.setRange(1, 120)  # Minimo 1 mese, massimo 120 mesi (10 anni)
        self._months_spin.setValue(3)  # Default: 3 mesi
        self._months_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self._months_spin.setMinimumWidth(60)
        self._months_spin.valueChanged.connect(self._on_months_changed)
        layout.addWidget(self._months_spin)

        layout.addWidget(QLabel("mesi"))

        layout.addStretch()

        self._main_layout.addWidget(group)

    def _setup_bar_chart_section(self) -> None:
        """Configura la sezione grafico a barre."""
        group = QGroupBox("Budget vs Spesa")
        layout = QVBoxLayout(group)

        self._bar_chart = BarChart()
        self._bar_chart.setMinimumHeight(300)
        layout.addWidget(self._bar_chart)

        self._main_layout.addWidget(group)

    def _setup_export_section(self) -> None:
        """Configura la sezione esportazione PDF."""
        group = QGroupBox("Esporta Storico")
        layout = QHBoxLayout(group)
        layout.setSpacing(15)

        layout.addWidget(QLabel("Esporta PDF con gli ultimi"))

        self._export_months_spin = QSpinBox()
        self._export_months_spin.setRange(1, 120)
        self._export_months_spin.setValue(3)
        self._export_months_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self._export_months_spin.setMinimumWidth(60)
        layout.addWidget(self._export_months_spin)

        layout.addWidget(QLabel("mesi"))

        self._export_btn = QPushButton("Esporta PDF")
        self._export_btn.setObjectName("exportBtn")
        self._export_btn.clicked.connect(self._on_export_clicked)
        layout.addWidget(self._export_btn)

        layout.addStretch()

        self._main_layout.addWidget(group)

    def _setup_reset_section(self) -> None:
        """Configura la sezione reset dati applicazione."""
        group = QGroupBox("Reset Dati")
        layout = QHBoxLayout(group)
        layout.setSpacing(15)

        warning_label = QLabel(
            "Azzera stipendi, spese e modello attivo, riportando l'app al primo avvio."
        )
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label, 1)

        self._reset_data_btn = QPushButton("Resetta dati")
        self._reset_data_btn.setObjectName("dangerBtn")
        self._reset_data_btn.clicked.connect(self._on_reset_data_clicked)
        layout.addWidget(self._reset_data_btn)

        self._main_layout.addWidget(group)

    # === Metodi pubblici per il controller ===

    # === Metodi pubblici per il controller ===

    def set_salary_day(self, day: int) -> None:
        """Imposta il valore dello spinbox salary_day."""
        self._salary_day_spin.setValue(day)

    def set_salaries(self, salaries: list[dict]) -> None:
        """Popola la tabella degli stipendi.
        
        Args:
            salaries: Lista di dict con 'period', 'date', 'amount', 'model_name', 'note'
        """
        self._salaries_table.setRowCount(len(salaries))

        for row, sal in enumerate(salaries):
            self._salaries_table.setItem(row, 0, QTableWidgetItem(sal.get("period", "")))
            self._salaries_table.setItem(row, 1, QTableWidgetItem(sal.get("date", "")))

            amount = sal.get("amount", 0)
            amount_item = QTableWidgetItem(f"{amount:.2f} €")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._salaries_table.setItem(row, 2, amount_item)

            self._salaries_table.setItem(row, 3, QTableWidgetItem(sal.get("model_name", "")))
        
        # Adatta l'altezza della tabella al contenuto
        self._adjust_salaries_table_height()

    def _adjust_salaries_table_height(self) -> None:
        """Adatta l'altezza della tabella stipendi in base al numero di righe."""
        header_height = self._salaries_table.horizontalHeader().height()
        rows_height = sum(
            self._salaries_table.rowHeight(row)
            for row in range(self._salaries_table.rowCount())
        )
        total_height = header_height + rows_height + 2
        self._salaries_table.setFixedHeight(total_height)

    def set_months(self, months: int) -> None:
        """Imposta il valore dello spinbox mesi."""
        self._months_spin.setValue(months)

    def set_bar_chart_data(self, periods: list[str], budget_values: list[float],
                           spent_values: list[float]) -> None:
        """Imposta i dati del grafico a barre."""
        self._bar_chart.set_data(periods, budget_values, spent_values)

    # === Slot interni ===

    def _on_salary_day_changed(self) -> None:
        """Gestisce il cambio di salary_day."""
        day = self._salary_day_spin.value()
        self.salary_day_changed.emit(day)

    def _on_export_clicked(self) -> None:
        """Gestisce il click sul pulsante esporta."""
        months = self._export_months_spin.value()
        self.export_requested.emit(months)

    def _on_months_changed(self) -> None:
        """Gestisce il cambio del numero di mesi."""
        months = self._months_spin.value()
        self.months_changed.emit(months)

    def _on_reset_data_clicked(self) -> None:
        """Gestisce il click sul pulsante reset dati."""
        self.reset_data_requested.emit()
