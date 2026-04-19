"""Vista Dashboard — Pagina 1: Configurazione Stipendio."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QSpinBox, QGridLayout, QScrollArea,
    QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor


class DashboardView(QWidget):
    """Pagina Dashboard per configurazione stipendio e modello."""

    # Segnali emessi verso il controller
    salary_save_requested = pyqtSignal(str)  # importo come stringa
    model_selected = pyqtSignal(str)  # id del modello
    custom_model_save_requested = pyqtSignal(str, list)  # nome, categorie

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        # Layout principale con scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        self._main_layout = QVBoxLayout(container)
        self._main_layout.setContentsMargins(20, 20, 20, 20)
        self._main_layout.setSpacing(20)

        # Titolo pagina
        title = QLabel("Dashboard")
        title_font = title.font()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        self._main_layout.addWidget(title)

        # Sezione: Input stipendio
        self._setup_salary_section()

        # Sezione: Scelta modello
        self._setup_model_section()

        # Sezione: Riepilogo (tabella e grafico placeholder)
        self._setup_summary_section()

        # Spazio finale
        self._main_layout.addStretch()

        scroll.setWidget(container)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

    def _setup_salary_section(self) -> None:
        group = QGroupBox("Stipendio del periodo")
        layout = QVBoxLayout(group)

        # Label periodo
        self._period_label = QLabel("Periodo: —")
        layout.addWidget(self._period_label)

        # Input importo
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Importo netto:"))
        self._salary_input = QLineEdit()
        self._salary_input.setPlaceholderText("Es: 1800.00")
        self._salary_input.setMaximumWidth(200)
        input_layout.addWidget(self._salary_input)
        input_layout.addWidget(QLabel("€"))
        input_layout.addStretch()
        layout.addLayout(input_layout)

        # Pulsante salva
        self._save_salary_btn = QPushButton("Salva stipendio")
        self._save_salary_btn.clicked.connect(self._on_save_salary)
        layout.addWidget(self._save_salary_btn)

        self._main_layout.addWidget(group)

    def _setup_model_section(self) -> None:
        group = QGroupBox("Modello di distribuzione")
        layout = QVBoxLayout(group)

        # ComboBox modelli
        combo_layout = QHBoxLayout()
        combo_layout.addWidget(QLabel("Modello:"))
        self._model_combo = QComboBox()
        self._model_combo.setMinimumWidth(250)
        self._model_combo.currentIndexChanged.connect(self._on_model_changed)
        combo_layout.addWidget(self._model_combo)
        combo_layout.addStretch()
        layout.addLayout(combo_layout)

        self._main_layout.addWidget(group)

    def _setup_summary_section(self) -> None:
        group = QGroupBox("Riepilogo distribuzione")
        layout = QVBoxLayout(group)

        # Tabella riepilogativa
        self._summary_table = QTableWidget()
        self._summary_table.setColumnCount(4)
        self._summary_table.setHorizontalHeaderLabels(
            ["Colore", "Categoria", "%", "Importo €"]
        )
        self._summary_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self._summary_table.setMaximumHeight(200)
        layout.addWidget(self._summary_table)

        # Placeholder per il grafico
        self._chart_placeholder = QLabel("[Grafico a torta — da implementare]")
        self._chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._chart_placeholder.setMinimumHeight(200)
        self._chart_placeholder.setStyleSheet("background-color: #2a2a3c; border-radius: 8px;")
        layout.addWidget(self._chart_placeholder)

        self._main_layout.addWidget(group)

    def _on_save_salary(self) -> None:
        """Emette il segnale per salvare lo stipendio."""
        amount = self._salary_input.text().strip()
        self.salary_save_requested.emit(amount)

    def _on_model_changed(self, index: int) -> None:
        """Emette il segnale quando cambia il modello selezionato."""
        model_id = self._model_combo.currentData()
        if model_id:
            self.model_selected.emit(model_id)

    # === Metodi pubblici per il controller ===

    def set_period_label(self, text: str) -> None:
        """Aggiorna la label del periodo corrente."""
        self._period_label.setText(text)

    def set_salary_input(self, amount: str) -> None:
        """Imposta il valore nel campo stipendio."""
        self._salary_input.setText(amount)

    def get_salary_input(self) -> str:
        """Restituisce il valore nel campo stipendio."""
        return self._salary_input.text().strip()

    def set_models(self, models: list[tuple[str, str]]) -> None:
        """Popola il ComboBox con i modelli disponibili.

        Args:
            models: lista di tuple (id, nome)
        """
        self._model_combo.clear()
        for model_id, name in models:
            self._model_combo.addItem(name, model_id)

    def set_selected_model(self, model_id: str) -> None:
        """Seleziona un modello specifico nel ComboBox."""
        for i in range(self._model_combo.count()):
            if self._model_combo.itemData(i) == model_id:
                self._model_combo.setCurrentIndex(i)
                break

    def get_selected_model_id(self) -> str | None:
        """Restituisce l'ID del modello selezionato."""
        return self._model_combo.currentData()

    def set_summary_data(self, categories: list[dict], salary: float) -> None:
        """Aggiorna la tabella riepilogativa.

        Args:
            categories: lista di dict con 'name', 'percentage', 'color'
            salary: importo dello stipendio
        """
        self._summary_table.setRowCount(len(categories) + 1)  # +1 per la riga totale

        for i, cat in enumerate(categories):
            # Colore
            color_item = QTableWidgetItem()
            color_item.setBackground(QColor(cat.get("color", "#6c63ff")))
            self._summary_table.setItem(i, 0, color_item)

            # Nome
            self._summary_table.setItem(i, 1, QTableWidgetItem(cat.get("name", "")))

            # Percentuale
            pct = cat.get("percentage", 0)
            self._summary_table.setItem(i, 2, QTableWidgetItem(f"{pct}%"))

            # Importo
            amount = (salary * pct) / 100
            self._summary_table.setItem(i, 3, QTableWidgetItem(f"{amount:.2f} €"))

        # Riga totale
        total_row = len(categories)
        self._summary_table.setItem(total_row, 0, QTableWidgetItem(""))
        self._summary_table.setItem(total_row, 1, QTableWidgetItem("Totale"))
        font = self._summary_table.font()
        font.setBold(True)
        self._summary_table.item(total_row, 1).setFont(font)
        self._summary_table.setItem(total_row, 2, QTableWidgetItem("100%"))
        self._summary_table.setItem(total_row, 3, QTableWidgetItem(f"{salary:.2f} €"))
