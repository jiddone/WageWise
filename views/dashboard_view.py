"""Vista Dashboard — Pagina 1: Configurazione Stipendio."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QSpinBox, QGridLayout, QScrollArea,
    QFrame, QColorDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QDoubleValidator


class DashboardView(QWidget):
    """Pagina Dashboard per configurazione stipendio e modello."""

    # Segnali emessi verso il controller
    salary_save_requested = pyqtSignal(str)  # importo come stringa
    model_selected = pyqtSignal(str)  # id del modello
    custom_model_save_requested = pyqtSignal(str, list)  # nome, categorie
    custom_model_cancel_requested = pyqtSignal()

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

        # Pulsanti per modello custom
        btn_layout = QHBoxLayout()
        self._create_model_btn = QPushButton("Crea modello personalizzato")
        self._create_model_btn.clicked.connect(self._on_create_model_clicked)
        btn_layout.addWidget(self._create_model_btn)

        self._edit_model_btn = QPushButton("Modifica")
        self._edit_model_btn.setEnabled(False)
        btn_layout.addWidget(self._edit_model_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Sezione editor modello custom (nascosta di default)
        self._setup_custom_model_editor(layout)

        self._main_layout.addWidget(group)

    def _setup_custom_model_editor(self, parent_layout: QVBoxLayout) -> None:
        """Configura l'editor per il modello personalizzato."""
        self._custom_editor_widget = QWidget()
        self._custom_editor_widget.setVisible(False)
        self._custom_editor_widget.setStyleSheet("background-color: #2a2a3a; border-radius: 8px;")
        editor_layout = QVBoxLayout(self._custom_editor_widget)
        editor_layout.setContentsMargins(20, 20, 20, 20)
        editor_layout.setSpacing(15)

        # Nome modello
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Nome modello:"))
        self._custom_model_name_input = QLineEdit()
        self._custom_model_name_input.setPlaceholderText("Es: Il mio modello 50/30/20")
        name_layout.addWidget(self._custom_model_name_input)
        editor_layout.addLayout(name_layout)

        # Lista categorie
        editor_layout.addWidget(QLabel("Categorie:"))
        self._categories_container = QWidget()
        self._categories_layout = QVBoxLayout(self._categories_container)
        self._categories_layout.setSpacing(8)
        editor_layout.addWidget(self._categories_container)

        # Pulsante aggiungi categoria
        self._add_category_btn = QPushButton("+ Aggiungi categoria")
        self._add_category_btn.clicked.connect(self._on_add_category)
        editor_layout.addWidget(self._add_category_btn)

        # Label percentuale rimanente
        self._remaining_pct_label = QLabel("Rimanente: 100%")
        self._remaining_pct_label.setStyleSheet("font-weight: bold; padding: 5px;")
        editor_layout.addWidget(self._remaining_pct_label)

        # Pulsanti azione
        btn_layout = QHBoxLayout()
        self._save_custom_model_btn = QPushButton("Salva modello")
        self._save_custom_model_btn.setEnabled(False)
        self._save_custom_model_btn.clicked.connect(self._on_save_custom_model)
        btn_layout.addWidget(self._save_custom_model_btn)

        self._cancel_custom_model_btn = QPushButton("Annulla")
        self._cancel_custom_model_btn.clicked.connect(self._on_cancel_custom_model)
        btn_layout.addWidget(self._cancel_custom_model_btn)
        btn_layout.addStretch()
        editor_layout.addLayout(btn_layout)

        parent_layout.addWidget(self._custom_editor_widget)

    def _on_create_model_clicked(self) -> None:
        """Mostra l'editor per creare un nuovo modello."""
        self._custom_editor_widget.setVisible(True)
        self._create_model_btn.setEnabled(False)
        # Aggiungi una riga vuota di default
        if self._categories_layout.count() == 0:
            self._on_add_category()

    def _on_add_category(self) -> None:
        """Aggiunge una riga per una nuova categoria."""
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(10, 8, 10, 8)
        row_layout.setSpacing(15)

        # Nome categoria
        name_input = QLineEdit()
        name_input.setPlaceholderText("Nome categoria")
        name_input.setMinimumWidth(150)
        name_input.setMaximumWidth(250)
        row_layout.addWidget(name_input)

        # Percentuale
        pct_spin = QSpinBox()
        pct_spin.setRange(0, 100)
        pct_spin.setValue(0)
        pct_spin.setSuffix("%")
        pct_spin.setMinimumWidth(90)
        pct_spin.setMaximumWidth(110)
        pct_spin.setMinimumHeight(32)
        pct_spin.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
        pct_spin.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                padding-right: 20px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                height: 14px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #4a4a5a;
            }
        """)
        pct_spin.valueChanged.connect(self._update_remaining_percentage)
        row_layout.addWidget(pct_spin)

        # Selettore colore con label
        color_layout = QHBoxLayout()
        color_layout.setSpacing(5)
        color_btn = QPushButton()
        color_btn.setMaximumWidth(40)
        color_btn.setMinimumHeight(28)
        default_color = "#4CAF50"
        color_btn.setStyleSheet(f"background-color: {default_color}; border: none; border-radius: 4px;")
        color_btn.setToolTip("Clicca per cambiare colore")
        color_btn.clicked.connect(lambda: self._choose_color(color_btn))
        color_layout.addWidget(color_btn)
        
        color_label = QLabel("Colore")
        color_label.setStyleSheet("color: #888; font-size: 11px;")
        color_layout.addWidget(color_label)
        color_layout.addStretch()
        row_layout.addLayout(color_layout)

        # Label importo calcolato
        amount_label = QLabel("— €")
        amount_label.setStyleSheet("color: #aaa; min-width: 80px; font-weight: bold;")
        row_layout.addWidget(amount_label)

        # Pulsante rimuovi
        remove_btn = QPushButton("✕")
        remove_btn.setMaximumWidth(35)
        remove_btn.setMinimumHeight(28)
        remove_btn.setToolTip("Rimuovi categoria")
        remove_btn.setStyleSheet("background-color: #ff4444; color: white; border: none; border-radius: 4px;")
        remove_btn.clicked.connect(lambda: self._remove_category_row(row_widget))
        row_layout.addWidget(remove_btn)

        row_layout.addStretch()

        # Salva riferimenti
        row_widget.name_input = name_input
        row_widget.pct_spin = pct_spin
        row_widget.color_btn = color_btn
        row_widget.amount_label = amount_label

        self._categories_layout.addWidget(row_widget)
        self._update_remaining_percentage()

    def _choose_color(self, button: QPushButton) -> None:
        """Apre il dialog di selezione colore."""
        color = QColorDialog.getColor()
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()}; border: none; min-height: 20px;")

    def _remove_category_row(self, row_widget: QWidget) -> None:
        """Rimuove una riga categoria."""
        row_widget.deleteLater()
        self._update_remaining_percentage()

    def _update_remaining_percentage(self) -> None:
        """Aggiorna la label della percentuale rimanente."""
        total = 0
        for i in range(self._categories_layout.count()):
            item = self._categories_layout.itemAt(i)
            if item and item.widget():
                row = item.widget()
                total += row.pct_spin.value()

        remaining = 100 - total
        if remaining > 0:
            self._remaining_pct_label.setText(f"Rimanente: {remaining}%")
            self._remaining_pct_label.setStyleSheet("font-weight: bold; padding: 5px; color: #FFC107;")
            self._save_custom_model_btn.setEnabled(False)
        elif remaining == 0:
            self._remaining_pct_label.setText("✓ Somma: 100%")
            self._remaining_pct_label.setStyleSheet("font-weight: bold; padding: 5px; color: #4CAF50;")
            self._save_custom_model_btn.setEnabled(True)
        else:
            self._remaining_pct_label.setText(f"Eccesso: {abs(remaining)}%")
            self._remaining_pct_label.setStyleSheet("font-weight: bold; padding: 5px; color: #F44336;")
            self._save_custom_model_btn.setEnabled(False)

    def _on_save_custom_model(self) -> None:
        """Emette il segnale per salvare il modello custom."""
        name = self._custom_model_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Attenzione", "Inserisci un nome per il modello.")
            return

        categories = []
        for i in range(self._categories_layout.count()):
            item = self._categories_layout.itemAt(i)
            if item and item.widget():
                row = item.widget()
                cat_name = row.name_input.text().strip()
                if not cat_name:
                    QMessageBox.warning(self, "Attenzione", "Tutte le categorie devono avere un nome.")
                    return
                
                # Estrai colore dallo stylesheet
                style = row.color_btn.styleSheet()
                color = "#4CAF50"
                if "background-color:" in style:
                    color = style.split("background-color:")[1].split(";")[0].strip()

                categories.append({
                    "name": cat_name,
                    "percentage": row.pct_spin.value(),
                    "color": color
                })

        self.custom_model_save_requested.emit(name, categories)

    def _on_cancel_custom_model(self) -> None:
        """Nasconde l'editor e resetta i campi."""
        self._custom_editor_widget.setVisible(False)
        self._create_model_btn.setEnabled(True)
        self._custom_model_name_input.clear()
        
        # Rimuovi tutte le righe categorie
        while self._categories_layout.count() > 0:
            item = self._categories_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self._update_remaining_percentage()
        self.custom_model_cancel_requested.emit()

    def update_custom_model_amounts(self, salary: float) -> None:
        """Aggiorna gli importi calcolati per ogni categoria nell'editor."""
        for i in range(self._categories_layout.count()):
            item = self._categories_layout.itemAt(i)
            if item and item.widget():
                row = item.widget()
                pct = row.pct_spin.value()
                amount = (salary * pct) / 100
                row.amount_label.setText(f"{amount:.2f} €")

    def show_custom_model_editor(self, show: bool = True) -> None:
        """Mostra/nasconde l'editor del modello custom."""
        self._custom_editor_widget.setVisible(show)
        self._create_model_btn.setEnabled(not show)

    def is_custom_model_editor_visible(self) -> bool:
        """Restituisce True se l'editor custom è visibile."""
        return self._custom_editor_widget.isVisible()

    def show_error(self, message: str) -> None:
        """Mostra un messaggio di errore."""
        QMessageBox.critical(self, "Errore", message)

    def show_info(self, message: str) -> None:
        """Mostra un messaggio informativo."""
        QMessageBox.information(self, "Info", message)

    def show_confirmation(self, message: str) -> bool:
        """Mostra un dialog di conferma. Restituisce True se confermato."""
        reply = QMessageBox.question(
            self, "Conferma", message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes

    def _setup_summary_section(self) -> None:
        """Configura la sezione riepilogativa con tabella e grafico."""
        group = QGroupBox("Riepilogo distribuzione")
        layout = QVBoxLayout(group)

        # Layout verticale: tabella sopra, grafico sotto
        content_layout = QVBoxLayout()

        # Tabella riepilogativa (ora occupa tutta la larghezza)
        self._summary_table = QTableWidget()
        self._summary_table.setColumnCount(4)
        self._summary_table.setHorizontalHeaderLabels(["Colore", "Categoria", "%", "Importo €"])
        self._summary_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self._summary_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._summary_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self._summary_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self._summary_table.setColumnWidth(0, 60)   # Colore
        self._summary_table.setColumnWidth(2, 80)   # Percentuale
        self._summary_table.setColumnWidth(3, 120)  # Importo
        # Nascondi scrollbar verticali e orizzontali
        self._summary_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._summary_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Rimuovi bordi extra
        self._summary_table.setFrameShape(QFrame.Shape.NoFrame)
        content_layout.addWidget(self._summary_table)

        # Grafico a torta sotto la tabella
        from components.pie_chart import PieChart
        self._pie_chart = PieChart()
        self._pie_chart.setMinimumSize(400, 300)
        content_layout.addWidget(self._pie_chart, 1)

        layout.addLayout(content_layout)
        self._main_layout.addWidget(group)

    # === Metodi pubblici per il Controller ===

    def set_period_label(self, text: str) -> None:
        """Aggiorna la label del periodo corrente."""
        self._period_label.setText(text)

    def set_salary_input(self, value: str) -> None:
        """Imposta il valore del campo stipendio."""
        self._salary_input.setText(value)

    def get_salary_input(self) -> str:
        """Restituisce il valore inserito nel campo stipendio."""
        return self._salary_input.text().strip()

    def set_models(self, models: list[tuple[str, str]]) -> None:
        """Popola il ComboBox con i modelli disponibili.

        Args:
            models: Lista di tuple (id, nome)
        """
        self._model_combo.clear()
        for model_id, name in models:
            self._model_combo.addItem(name, model_id)

    def set_selected_model(self, model_id: str) -> None:
        """Seleziona il modello specificato nel ComboBox."""
        for i in range(self._model_combo.count()):
            if self._model_combo.itemData(i) == model_id:
                self._model_combo.setCurrentIndex(i)
                break

    def get_selected_model_id(self) -> str:
        """Restituisce l'ID del modello selezionato."""
        return self._model_combo.currentData()

    def set_summary_data(self, categories: list[dict], salary: float) -> None:
        """Aggiorna la tabella e il grafico con i dati del modello.

        Args:
            categories: Lista di dict con 'name', 'percentage', 'color'
            salary: Importo dello stipendio per calcolare gli importi
        """
        # Aggiorna tabella
        row_count = len(categories) + 1  # +1 per riga totale
        self._summary_table.setRowCount(row_count)

        # Calcola altezza dinamica: header (30px) + righe (35px ciascuna) + padding (10px)
        header_height = 30
        row_height = 35
        padding = 20
        table_height = header_height + (row_count * row_height) + padding
        self._summary_table.setMinimumHeight(table_height)
        self._summary_table.setMaximumHeight(table_height)

        total_pct = 0
        total_amount = 0.0

        for i, cat in enumerate(categories):
            name = cat.get("name", "")
            pct = cat.get("percentage", 0)
            color = cat.get("color", "#6c63ff")
            amount = (salary * pct) / 100 if salary > 0 else 0

            total_pct += pct
            total_amount += amount

            # Colore (pallino)
            color_item = QTableWidgetItem()
            color_item.setBackground(QColor(color))
            self._summary_table.setItem(i, 0, color_item)

            # Nome
            self._summary_table.setItem(i, 1, QTableWidgetItem(name))

            # Percentuale
            self._summary_table.setItem(i, 2, QTableWidgetItem(f"{pct}%"))

            # Importo
            self._summary_table.setItem(i, 3, QTableWidgetItem(f"{amount:.2f}"))

        # Riga totale
        total_row = len(categories)
        total_name = QTableWidgetItem("Totale")
        total_name.setFont(self.font())
        total_name_font = total_name.font()
        total_name_font.setBold(True)
        total_name.setFont(total_name_font)
        self._summary_table.setItem(total_row, 1, total_name)

        total_pct_item = QTableWidgetItem(f"{total_pct}%")
        total_pct_item.setFont(total_name_font)
        self._summary_table.setItem(total_row, 2, total_pct_item)

        total_amount_item = QTableWidgetItem(f"{total_amount:.2f}")
        total_amount_item.setFont(total_name_font)
        self._summary_table.setItem(total_row, 3, total_amount_item)

        # Aggiorna grafico
        chart_data = []
        for cat in categories:
            pct = cat.get("percentage", 0)
            amount = (salary * pct) / 100 if salary > 0 else 0
            chart_data.append({
                "name": cat.get("name", ""),
                "value": amount,
                "color": cat.get("color", "#6c63ff")
            })
        self._pie_chart.set_data(chart_data)

        # Aggiorna importi nell'editor custom se visibile
        if self.is_custom_model_editor_visible():
            self.update_custom_model_amounts(salary)

    def _on_model_changed(self, index: int) -> None:
        """Gestisce il cambio di selezione del modello."""
        model_id = self._model_combo.itemData(index)
        if model_id:
            self.model_selected.emit(model_id)

    def _on_save_salary(self) -> None:
        """Gestisce il click sul pulsante salva stipendio."""
        amount = self._salary_input.text().strip()
        self.salary_save_requested.emit(amount)
