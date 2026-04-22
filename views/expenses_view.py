"""Vista Spese — Pagina 2: Registro Spese e Residui."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QDateEdit, QScrollArea,
    QFrame, QMessageBox, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont, QColor, QIcon, QDoubleValidator

from components.category_card import CategoryCard
from components.budget_progress_bar import BudgetProgressBar


class ExpensesView(QWidget):
    """Pagina Spese per tracciamento e residui."""

    # Segnali emessi verso il controller
    expense_add_requested = pyqtSignal(str, str, str, str)  # amount, category_id, description, date
    expense_delete_requested = pyqtSignal(str)  # expense_id
    filter_changed = pyqtSignal(str)  # category_id o "all"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._category_cards: dict[str, CategoryCard] = {}
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

        # Sezione: Inserimento spesa
        self._setup_expense_input_section()

        # Sezione: Lista spese
        self._setup_expense_list_section()

        # Sezione: Residui per categoria
        self._setup_residuals_section()

        # Sezione: Riepilogo globale
        self._setup_global_summary_section()

        # Spazio finale
        self._main_layout.addStretch()

        scroll.setWidget(container)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

    def _setup_expense_input_section(self) -> None:
        """Configura la sezione di inserimento spesa."""
        group = QGroupBox("Nuova Spesa")
        layout = QGridLayout(group)
        layout.setSpacing(10)

        # Importo
        layout.addWidget(QLabel("Importo:"), 0, 0)
        self._amount_input = QLineEdit()
        self._amount_input.setPlaceholderText("Es: 50.00")
        validator = QDoubleValidator(0.01, 999999.99, 2, self)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self._amount_input.setValidator(validator)
        layout.addWidget(self._amount_input, 0, 1)
        layout.addWidget(QLabel("€"), 0, 2)

        # Categoria
        layout.addWidget(QLabel("Categoria:"), 1, 0)
        self._category_combo = QComboBox()
        self._category_combo.setMinimumWidth(150)
        layout.addWidget(self._category_combo, 1, 1, 1, 2)

        # Descrizione
        layout.addWidget(QLabel("Descrizione:"), 2, 0)
        self._description_input = QLineEdit()
        self._description_input.setPlaceholderText("Es: Spesa al supermercato")
        layout.addWidget(self._description_input, 2, 1, 1, 2)

        # Data
        layout.addWidget(QLabel("Data:"), 3, 0)
        self._date_input = QDateEdit()
        self._date_input.setCalendarPopup(False)
        self._date_input.setButtonSymbols(QDateEdit.ButtonSymbols.NoButtons)
        self._date_input.setDate(QDate.currentDate())
        self._date_input.setDisplayFormat("dd/MM/yyyy")
        layout.addWidget(self._date_input, 3, 1, 1, 2)

        # Pulsante aggiungi
        self._add_expense_btn = QPushButton("Aggiungi Spesa")
        self._add_expense_btn.clicked.connect(self._on_add_expense_clicked)
        layout.addWidget(self._add_expense_btn, 4, 1, 1, 2)

        # Label periodo corrente
        self._period_label = QLabel("Periodo: —")
        self._period_label.setProperty("class", "subtitle")
        layout.addWidget(self._period_label, 5, 0, 1, 3)

        self._main_layout.addWidget(group)

    def _setup_expense_list_section(self) -> None:
        """Configura la sezione lista spese."""
        group = QGroupBox("Spese Registrate")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        # Filtro per categoria
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filtra per categoria:"))
        self._filter_combo = QComboBox()
        self._filter_combo.setMinimumWidth(150)
        self._filter_combo.addItem("Tutte", "all")
        self._filter_combo.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self._filter_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Tabella spese
        self._expenses_table = QTableWidget()
        self._expenses_table.setColumnCount(5)
        self._expenses_table.setHorizontalHeaderLabels([
            "Data", "Descrizione", "Categoria", "Importo", "Azioni"
        ])
        self._expenses_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self._expenses_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._expenses_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._expenses_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self._expenses_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self._expenses_table.setColumnWidth(4, 80)
        self._expenses_table.setFrameShape(QFrame.Shape.NoFrame)
        self._expenses_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self._expenses_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._expenses_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._expenses_table.setAlternatingRowColors(True)
        # Nascondi barra di scorrimento verticale
        self._expenses_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._expenses_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(self._expenses_table)

        self._main_layout.addWidget(group)

    def _setup_residuals_section(self) -> None:
        """Configura la sezione residui per categoria."""
        group = QGroupBox("Residui per Categoria")
        layout = QVBoxLayout(group)

        # Container per le card delle categorie
        self._categories_container = QWidget()
        self._categories_layout = QGridLayout(self._categories_container)
        self._categories_layout.setSpacing(15)
        layout.addWidget(self._categories_container)

        self._main_layout.addWidget(group)

    def _setup_global_summary_section(self) -> None:
        """Configura la sezione riepilogo globale."""
        group = QGroupBox("Riepilogo Globale")
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Info layout
        info_layout = QHBoxLayout()

        # Totale speso
        spent_layout = QVBoxLayout()
        spent_title = QLabel("Totale Speso")
        spent_title.setProperty("class", "subtitle")
        self._total_spent_label = QLabel("0.00 €")
        self._total_spent_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        spent_layout.addWidget(spent_title)
        spent_layout.addWidget(self._total_spent_label)
        info_layout.addLayout(spent_layout)

        # Residuo globale
        remaining_layout = QVBoxLayout()
        remaining_title = QLabel("Residuo Globale")
        remaining_title.setProperty("class", "subtitle")
        self._global_remaining_label = QLabel("0.00 €")
        self._global_remaining_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        remaining_layout.addWidget(remaining_title)
        remaining_layout.addWidget(self._global_remaining_label)
        info_layout.addLayout(remaining_layout)

        # Percentuale utilizzata
        pct_layout = QVBoxLayout()
        pct_title = QLabel("% Budget Utilizzata")
        pct_title.setProperty("class", "subtitle")
        self._global_percentage_label = QLabel("0%")
        self._global_percentage_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        pct_layout.addWidget(pct_title)
        pct_layout.addWidget(self._global_percentage_label)
        info_layout.addLayout(pct_layout)

        info_layout.addStretch()
        layout.addLayout(info_layout)

        # Barra progresso globale
        self._global_progress_bar = BudgetProgressBar()
        layout.addWidget(self._global_progress_bar)

        self._main_layout.addWidget(group)

    # === Metodi pubblici per il controller ===

    def set_period_label(self, text: str) -> None:
        """Imposta la label del periodo corrente."""
        self._period_label.setText(text)

    def set_categories(self, categories: list[dict]) -> None:
        """Imposta le categorie disponibili.
        
        Args:
            categories: Lista di dict con 'id', 'name', 'color'
        """
        # Aggiorna combo categorie
        self._category_combo.clear()
        for cat in categories:
            self._category_combo.addItem(cat["name"], cat["id"])

        # Aggiorna combo filtro
        current_filter = self._filter_combo.currentData()
        self._filter_combo.clear()
        self._filter_combo.addItem("Tutte", "all")
        for cat in categories:
            self._filter_combo.addItem(cat["name"], cat["id"])
        
        # Ripristina filtro precedente se possibile
        index = self._filter_combo.findData(current_filter)
        if index >= 0:
            self._filter_combo.setCurrentIndex(index)

    def set_category_cards(self, categories_data: list[dict]) -> None:
        """Crea/aggiorna le card delle categorie.
        
        Args:
            categories_data: Lista di dict con 'id', 'name', 'color', 'budget', 'spent'
        """
        # Pulisci layout esistente
        while self._categories_layout.count():
            item = self._categories_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._category_cards.clear()

        # Crea nuove card
        row, col = 0, 0
        for data in categories_data:
            card = CategoryCard()
            card.set_data(
                name=data["name"],
                color=data["color"],
                budget=data["budget"],
                spent=data["spent"]
            )
            self._categories_layout.addWidget(card, row, col)
            self._category_cards[data["id"]] = card
            
            col += 1
            if col >= 3:  # 3 card per riga
                col = 0
                row += 1

    def update_category_card(self, category_id: str, budget: float, spent: float) -> None:
        """Aggiorna una singola card categoria."""
        if category_id in self._category_cards:
            card = self._category_cards[category_id]
            # Ottieni i dati attuali per mantenere nome e colore
            # (in una implementazione reale, memorizzeresti questi dati)
            card.set_data(
                name=card._name_label.text(),
                color=card._color_indicator.styleSheet().replace("color: ", "").replace(";", ""),
                budget=budget,
                spent=spent
            )

    def set_expenses(self, expenses: list[dict]) -> None:
        """Popola la tabella delle spese.
        
        Args:
            expenses: Lista di dict con 'id', 'date', 'description', 'category_name', 'amount'
        """
        self._expenses_table.setRowCount(len(expenses))
        
        for row, expense in enumerate(expenses):
            # Data
            date_item = QTableWidgetItem(expense.get("date", ""))
            self._expenses_table.setItem(row, 0, date_item)
            
            # Descrizione
            desc_item = QTableWidgetItem(expense.get("description", ""))
            self._expenses_table.setItem(row, 1, desc_item)
            
            # Categoria
            cat_item = QTableWidgetItem(expense.get("category_name", ""))
            self._expenses_table.setItem(row, 2, cat_item)
            
            # Importo
            amount = expense.get("amount", 0)
            amount_item = QTableWidgetItem(f"{amount:.2f} €")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._expenses_table.setItem(row, 3, amount_item)
            
            # Pulsante elimina
            delete_btn = QPushButton("🗑")
            delete_btn.setProperty("class", "danger")
            delete_btn.style().unpolish(delete_btn)
            delete_btn.style().polish(delete_btn)
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.clicked.connect(lambda checked, eid=expense["id"]: self._on_delete_expense(eid))
            self._expenses_table.setCellWidget(row, 4, delete_btn)
        
        # Adatta l'altezza della tabella al contenuto
        self._adjust_table_height()

    def _adjust_table_height(self) -> None:
        """Adatta l'altezza della tabella in base al numero di righe."""
        # Calcola l'altezza totale: header + tutte le righe
        header_height = self._expenses_table.horizontalHeader().height()
        rows_height = sum(
            self._expenses_table.rowHeight(row) 
            for row in range(self._expenses_table.rowCount())
        )
        # Aggiungi un piccolo margine per evitare tagli
        total_height = header_height + rows_height + 2
        self._expenses_table.setFixedHeight(total_height)

    def set_global_summary(self, total_spent: float, total_budget: float) -> None:
        """Aggiorna il riepilogo globale.
        
        Args:
            total_spent: Totale speso nel periodo
            total_budget: Budget totale del periodo
        """
        remaining = total_budget - total_spent
        percentage = (total_spent / total_budget * 100) if total_budget > 0 else 0

        self._total_spent_label.setText(f"{total_spent:.2f} €")
        self._global_remaining_label.setText(f"{remaining:.2f} €")
        self._global_percentage_label.setText(f"{percentage:.1f}%")

        # Colore residuo
        if remaining < 0:
            self._global_remaining_label.setStyleSheet("color: #F44336;")
        else:
            self._global_remaining_label.setStyleSheet("color: #4CAF50;")

        # Aggiorna barra
        self._global_progress_bar.set_value(percentage)

    def clear_expense_inputs(self) -> None:
        """Pulisce i campi di input della spesa."""
        self._amount_input.clear()
        self._description_input.clear()
        self._date_input.setDate(QDate.currentDate())

    def get_expense_input(self) -> tuple[str, str, str, str]:
        """Restituisce i valori dei campi di input.
        
        Returns:
            Tuple di (amount, category_id, description, date)
        """
        amount = self._amount_input.text().replace(",", ".")
        category_id = self._category_combo.currentData()
        description = self._description_input.text()
        date = self._date_input.date().toString("yyyy-MM-dd")
        return amount, category_id, description, date

    def set_add_button_enabled(self, enabled: bool) -> None:
        """Abilita/disabilita il pulsante aggiungi."""
        self._add_expense_btn.setEnabled(enabled)

    # === Slot interni ===

    def _on_add_expense_clicked(self) -> None:
        """Gestisce il click sul pulsante aggiungi spesa."""
        amount, category_id, description, date = self.get_expense_input()
        self.expense_add_requested.emit(amount, category_id, description, date)

    def _on_delete_expense(self, expense_id: str) -> None:
        """Gestisce la richiesta di eliminazione spesa."""
        reply = QMessageBox.question(
            self,
            "Conferma eliminazione",
            "Sei sicuro di voler eliminare questa spesa?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.expense_delete_requested.emit(expense_id)

    def _on_filter_changed(self) -> None:
        """Gestisce il cambio di filtro."""
        category_id = self._filter_combo.currentData()
        self.filter_changed.emit(category_id)
