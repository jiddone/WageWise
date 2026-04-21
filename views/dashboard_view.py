"""Vista Dashboard — Pagina 1: Configurazione Stipendio."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QSpinBox, QGridLayout, QScrollArea,
    QFrame, QMessageBox, QListView, QStyledItemDelegate, QStyleOptionViewItem,
    QStyle
)
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QSize
from PyQt6.QtGui import QColor, QDoubleValidator, QPalette, QFont, QTextOption


class ModelComboDelegate(QStyledItemDelegate):
    """Delegate personalizzato per disegnare pulsanti elimina accanto ai modelli custom."""
    
    delete_clicked = pyqtSignal(str)  # emette l'id del modello da eliminare
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._custom_model_ids = set()
        self._delete_button_rects = {}  # Mappa index -> rect del bottone
        self._active_model_id = ""     # ID del modello attivo (per evidenziarlo)
        
    def set_custom_models(self, custom_ids: set[str]):
        """Imposta quali modelli sono custom (e quindi hanno il pulsante elimina)."""
        self._custom_model_ids = custom_ids

    def set_active_model(self, model_id: str) -> None:
        """Imposta quale modello è quello attivo (per evidenziarlo nella lista)."""
        self._active_model_id = model_id
        
    def initStyleOption(self, option, index):
        """Override per garantire sempre un font con pointSize valido (evita warning QSS)."""
        super().initStyleOption(option, index)
        if option.font.pointSize() <= 0:
            option.font = QFont("Arial", 10)

    def paint(self, painter, option, index):
        """Disegna la riga con il nome del modello e il pulsante elimina se custom."""
        from PyQt6.QtGui import QTextOption
        
        # Ottieni dati
        model_id = index.data(Qt.ItemDataRole.UserRole)
        text = index.data(Qt.ItemDataRole.DisplayRole)

        # Evidenzia il modello attivo con un prefisso stella
        if model_id == self._active_model_id:
            text = f"★ {text}"
        
        # Disegna lo sfondo in base allo stato (selezione / hover / normale)
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, QColor("#6c63ff"))
        elif option.state & QStyle.StateFlag.State_MouseOver:
            painter.fillRect(option.rect, QColor("#3a3a5c"))
        else:
            painter.fillRect(option.rect, QColor("#2a2a3c"))
            
        # Calcola rettangoli
        rect = option.rect
        button_width = 24
        button_height = 20
        padding = 5
        
        # Se è un modello custom, riserva spazio per il pulsante
        if model_id in self._custom_model_ids:
            text_rect = QRect(rect.left() + padding, rect.top(), 
                            rect.width() - button_width - padding * 3, rect.height())
            button_rect = QRect(rect.right() - button_width - padding,
                              rect.top() + (rect.height() - button_height) // 2,
                              button_width, button_height)
            self._delete_button_rects[index.row()] = button_rect
            
            # Disegna il pulsante elimina (rosso con X)
            painter.save()
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#ff4444"))
            painter.drawRoundedRect(button_rect, 3, 3)
            
            # Disegna la X
            painter.setPen(QColor("white"))
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            painter.drawText(button_rect, Qt.AlignmentFlag.AlignCenter, "✕")
            painter.restore()
        else:
            text_rect = QRect(rect.left() + padding, rect.top(), 
                            rect.width() - padding * 2, rect.height())
            if index.row() in self._delete_button_rects:
                del self._delete_button_rects[index.row()]
        
        # Disegna il testo con font esplicito (evita warning pointSize=-1 da QSS)
        safe_font = QFont("Arial", 10)
        painter.setFont(safe_font)
        painter.setPen(QColor("#ffffff"))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text)
        
    def sizeHint(self, option, index):
        """Restituisce la dimensione preferita per la riga."""
        # Non chiamiamo super() perché internamente userebbe il font del widget
        # che con QSS ha pixelSize impostato e pointSize=-1, causando warning.
        return QSize(option.rect.width() if option.rect.width() > 0 else 200, 28)
        
    def editorEvent(self, event, model, option, index):
        """Gestisce il click sul pulsante elimina."""
        if event.type() == event.Type.MouseButtonRelease:
            model_id = index.data(Qt.ItemDataRole.UserRole)
            if model_id in self._custom_model_ids:
                # Verifica se il click è nel rettangolo del bottone
                if index.row() in self._delete_button_rects:
                    button_rect = self._delete_button_rects[index.row()]
                    if button_rect.contains(int(event.position().x()), int(event.position().y())):
                        self.delete_clicked.emit(model_id)
                        return True
        return super().editorEvent(event, model, option, index)


class DashboardView(QWidget):
    """Pagina Dashboard per configurazione stipendio e modello."""

    # Segnali emessi verso il controller
    salary_save_requested = pyqtSignal(str)  # importo come stringa
    model_selected = pyqtSignal(str)  # id del modello
    custom_model_save_requested = pyqtSignal(str, list, str)  # nome, categorie, model_id (vuoto per nuovo)
    custom_model_cancel_requested = pyqtSignal()
    delete_model_requested = pyqtSignal(str)  # id del modello da eliminare
    edit_model_requested = pyqtSignal(str)  # id del modello da modificare
    set_active_model_requested = pyqtSignal(str)  # id del modello da impostare come attivo

    def __init__(self, parent=None):
        super().__init__(parent)
        self._editing_model_id = ""  # ID del modello in modifica (vuoto per nuovo)
        self._active_model_id = ""   # ID del modello attualmente attivo
        self._custom_model_ids: set = set()
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

        # ComboBox modelli con pulsanti elimina per modelli custom
        combo_layout = QHBoxLayout()
        combo_layout.addWidget(QLabel("Modello:"))
        self._model_combo = QComboBox()
        self._model_combo.setMinimumWidth(150)
        self._model_combo.currentIndexChanged.connect(self._on_model_changed)
        
        # Usa un delegate personalizzato per disegnare i pulsanti elimina
        self._model_delegate = ModelComboDelegate(self._model_combo)
        self._model_combo.setItemDelegate(self._model_delegate)
        
        # Connetti il segnale delete del delegate
        self._model_delegate.delete_clicked.connect(self._on_delete_model_clicked)
        
        # Intercetta gli eventi mouse sul combobox per gestire il click sul bottone elimina
        self._model_combo.view().viewport().installEventFilter(self)
        
        combo_layout.addWidget(self._model_combo)
        
        # Pulsante "Seleziona come attivo"
        self._set_active_model_btn = QPushButton("Seleziona come attivo")
        self._set_active_model_btn.setToolTip("Imposta questo modello come attivo per le spese")
        self._set_active_model_btn.clicked.connect(self._on_set_active_model_clicked)
        combo_layout.addWidget(self._set_active_model_btn)
        
        combo_layout.addStretch()
        layout.addLayout(combo_layout)

        # Pulsanti per modello custom
        btn_layout = QHBoxLayout()
        self._create_model_btn = QPushButton("Crea modello personalizzato")
        self._create_model_btn.clicked.connect(self._on_create_model_clicked)
        btn_layout.addWidget(self._create_model_btn)

        self._edit_model_btn = QPushButton("Modifica")
        self._edit_model_btn.setEnabled(False)
        self._edit_model_btn.clicked.connect(self._on_edit_model_clicked)
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
        self._custom_editor_widget.setProperty("class", "panel")
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
        self._remaining_pct_label.setProperty("class", "remaining-pct")
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
        self._editing_model_id = ""
        self._custom_editor_widget.setVisible(True)
        self._create_model_btn.setEnabled(False)
        # Aggiungi una riga vuota di default
        if self._categories_layout.count() == 0:
            self._on_add_category()

    def _on_edit_model_clicked(self) -> None:
        """Emette il segnale per modificare il modello custom selezionato."""
        model_id = self._model_combo.currentData()
        if model_id:
            self.edit_model_requested.emit(model_id)

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

        # Percentuale - solo spinbox senza bottoni
        pct_spin = QSpinBox()
        pct_spin.setRange(0, 100)
        pct_spin.setValue(0)
        pct_spin.setSuffix("%")
        pct_spin.setFixedWidth(70)
        pct_spin.setMinimumHeight(32)
        pct_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
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
        color_label.setProperty("class", "subtitle")
        color_layout.addWidget(color_label)
        color_layout.addStretch()
        row_layout.addLayout(color_layout)

        # Pulsante rimuovi
        remove_btn = QPushButton("✕")
        remove_btn.setFixedSize(40, 36)
        remove_btn.setToolTip("Rimuovi categoria")
        remove_btn.setProperty("class", "danger")
        remove_btn.style().unpolish(remove_btn)
        remove_btn.style().polish(remove_btn)
        remove_btn.clicked.connect(lambda: self._remove_category_row(row_widget))
        row_layout.addWidget(remove_btn)

        row_layout.addStretch()

        # Salva riferimenti
        row_widget.name_input = name_input
        row_widget.pct_spin = pct_spin
        row_widget.color_btn = color_btn

        self._categories_layout.addWidget(row_widget)
        self._update_remaining_percentage()

    def _choose_color(self, button: QPushButton) -> None:
        """Apre il dialog di selezione colore nativo di Qt."""
        from PyQt6.QtWidgets import QColorDialog
        from PyQt6.QtGui import QColor
        
        # Estrai colore corrente
        style = button.styleSheet()
        current_color = "#4CAF50"
        if "background-color:" in style:
            current_color = style.split("background-color:")[1].split(";")[0].strip()
        
        color = QColorDialog.getColor(QColor(current_color), self, "Seleziona colore")
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()}; border: none; min-height: 20px;")

    def _remove_category_row(self, row_widget: QWidget) -> None:
        """Rimuove una riga categoria."""
        row_widget.deleteLater()
        self._update_remaining_percentage()

    def _update_remaining_percentage(self) -> None:
        """Aggiorna la label della percentuale rimanente con colore gradiente."""
        total = 0
        spinboxes = []
        for i in range(self._categories_layout.count()):
            item = self._categories_layout.itemAt(i)
            if item and item.widget():
                row = item.widget()
                total += row.pct_spin.value()
                spinboxes.append(row.pct_spin)

        remaining = 100 - total
        
        # Calcola il colore gradiente: verde (100%) -> rosso (0%)
        # remaining va da 0 a 100
        ratio = max(0, remaining) / 100.0
        r = int(244 - (244 - 76) * ratio)   # 244 -> 76
        g = int(67 + (175 - 67) * ratio)    # 67 -> 175
        b = int(54 + (80 - 54) * ratio)     # 54 -> 80
        color = f"#{r:02x}{g:02x}{b:02x}"

        if remaining > 0:
            self._remaining_pct_label.setText(f"Rimanente: {remaining}%")
            self._remaining_pct_label.setStyleSheet(f"font-weight: bold; padding: 5px; color: {color};")
            self._save_custom_model_btn.setEnabled(False)
        elif remaining == 0:
            self._remaining_pct_label.setText("Rimanente: 0%")
            self._remaining_pct_label.setStyleSheet("font-weight: bold; padding: 5px; color: #F44336;")
            self._save_custom_model_btn.setEnabled(True)
        else:
            self._remaining_pct_label.setText(f"Eccesso: {abs(remaining)}%")
            self._remaining_pct_label.setStyleSheet("font-weight: bold; padding: 5px; color: #F44336;")
            self._save_custom_model_btn.setEnabled(False)

        # Limita le percentuali se si arriva a 100%
        for spin in spinboxes:
            current_max = spin.maximum()
            if remaining <= 0:
                # Se siamo a 100% o oltre, il max è il valore corrente
                spin.setMaximum(spin.value())
            else:
                # Altrimenti il max è 100
                spin.setMaximum(100)

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

        self.custom_model_save_requested.emit(name, categories, self._editing_model_id)

    def _on_cancel_custom_model(self) -> None:
        """Nasconde l'editor e resetta i campi."""
        self._editing_model_id = ""
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
        pass  # le righe editor non mostrano importi calcolati

    def show_custom_model_editor(self, show: bool = True) -> None:
        """Mostra/nasconde l'editor del modello custom."""
        self._custom_editor_widget.setVisible(show)
        self._create_model_btn.setEnabled(not show)

    def populate_model_editor(self, model: dict) -> None:
        """Popola l'editor con i dati di un modello esistente per la modifica."""
        # Imposta il nome
        self._custom_model_name_input.setText(model.get("name", ""))

        # Rimuovi tutte le righe esistenti
        while self._categories_layout.count() > 0:
            item = self._categories_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Aggiungi una riga per ogni categoria, con i valori pre-compilati
        for cat in model.get("categories", []):
            self._on_add_category()
            count = self._categories_layout.count()
            if count > 0:
                row = self._categories_layout.itemAt(count - 1).widget()
                row.name_input.setText(cat.get("name", ""))
                row.pct_spin.blockSignals(True)
                row.pct_spin.setValue(cat.get("percentage", 0))
                row.pct_spin.blockSignals(False)
                color = cat.get("color", "#4CAF50")
                row.color_btn.setStyleSheet(
                    f"background-color: {color}; border: none; border-radius: 4px;"
                )

        # Aggiorna la label percentuale rimanente
        self._update_remaining_percentage()

        # Memorizza l'ID del modello in modifica e mostra l'editor
        self._editing_model_id = model.get("id", "")
        self._custom_editor_widget.setVisible(True)
        self._create_model_btn.setEnabled(False)

    def close_custom_model_editor(self) -> None:
        """Chiude e resetta completamente l'editor del modello custom."""
        self._editing_model_id = ""
        self._custom_editor_widget.setVisible(False)
        self._create_model_btn.setEnabled(True)
        self._custom_model_name_input.clear()
        while self._categories_layout.count() > 0:
            item = self._categories_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._update_remaining_percentage()

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
        # Disabilita editing celle e selezione
        self._summary_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._summary_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self._summary_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
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

    def set_models(self, models: list[tuple[str, str]], custom_model_ids: set[str] = None) -> None:
        """Popola il ComboBox con i modelli disponibili.

        Args:
            models: Lista di tuple (id, nome)
            custom_model_ids: Set di ID dei modelli custom (per mostrare il pulsante elimina)
        """
        self._model_combo.clear()
        self._custom_model_ids = custom_model_ids or set()
        
        # Pulisci i rettangoli dei bottoni precedenti
        self._model_delegate._delete_button_rects.clear()
        
        # Aggiorna il delegate con i modelli custom
        self._model_delegate.set_custom_models(self._custom_model_ids)
        
        for model_id, name in models:
            self._model_combo.addItem(name, model_id)
        
        # Forza il repaint del combobox
        self._model_combo.update()

    def set_selected_model(self, model_id: str) -> None:
        """Seleziona il modello specificato nel ComboBox."""
        for i in range(self._model_combo.count()):
            if self._model_combo.itemData(i) == model_id:
                self._model_combo.setCurrentIndex(i)
                break

    def set_active_model_id(self, model_id: str) -> None:
        """Aggiorna il modello attivo: evidenzialo nel ComboBox e aggiorna il pulsante."""
        self._active_model_id = model_id
        self._model_delegate.set_active_model(model_id)
        self._model_combo.update()
        # Forza il repaint della lista se è aperta
        self._model_combo.view().update()
        self._update_set_active_button_state()

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
        
        # Colore vuoto per la riga totale
        empty_color_item = QTableWidgetItem()
        empty_color_item.setFlags(Qt.ItemFlag.NoItemFlags)
        self._summary_table.setItem(total_row, 0, empty_color_item)
        
        total_name = QTableWidgetItem("Totale")
        total_name_font = QFont()
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
            self._last_selected_model = model_id
            self.model_selected.emit(model_id)
            
            # Abilita il pulsante Modifica solo per modelli custom
            is_custom = model_id in self._custom_model_ids
            self._edit_model_btn.setEnabled(is_custom)
            
            # Aggiorna lo stato del pulsante "Seleziona come attivo"
            self._update_set_active_button_state()

    def _on_set_active_model_clicked(self) -> None:
        """Gestisce il click sul pulsante 'Seleziona come attivo'."""
        model_id = self._model_combo.currentData()
        if model_id:
            self.set_active_model_requested.emit(model_id)
    
    def _update_set_active_button_state(self) -> None:
        """Aggiorna lo stato del pulsante 'Seleziona come attivo' in base al modello selezionato."""
        model_id = self._model_combo.currentData()
        is_already_active = (model_id == self._active_model_id) if model_id else True
        self._set_active_model_btn.setEnabled(
            model_id is not None and model_id != "" and not is_already_active
        )
        if is_already_active:
            self._set_active_model_btn.setToolTip("Questo modello è già quello attivo")
        else:
            self._set_active_model_btn.setToolTip("Imposta questo modello come attivo per le spese")

    def _on_save_salary(self) -> None:
        """Gestisce il click sul pulsante salva stipendio."""
        amount = self._salary_input.text().strip()
        self.salary_save_requested.emit(amount)

    def _on_delete_model_clicked(self, model_id: str) -> None:
        """Gestisce il click sul pulsante elimina di un modello custom."""
        # Trova il nome del modello
        model_name = ""
        for i in range(self._model_combo.count()):
            if self._model_combo.itemData(i) == model_id:
                model_name = self._model_combo.itemText(i)
                break
        
        # Chiedi conferma
        reply = QMessageBox.question(
            self,
            "Conferma eliminazione",
            f'Vuoi eliminare il modello "{model_name}"?\n\nQuesta azione non può essere annullata.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_model_requested.emit(model_id)

    def eventFilter(self, obj, event):
        """Intercetta gli eventi mouse sul viewport del combobox per gestire il click sul bottone elimina."""
        if obj == self._model_combo.view().viewport():
            if event.type() == event.Type.MouseButtonPress or event.type() == event.Type.MouseButtonRelease:
                # Ottieni l'indice sotto il cursore
                view = self._model_combo.view()
                index = view.indexAt(event.position().toPoint())
                if index.isValid():
                    model_id = index.data(Qt.ItemDataRole.UserRole)
                    if model_id in self._custom_model_ids:
                        # Verifica se il click è nel rettangolo del bottone
                        if index.row() in self._model_delegate._delete_button_rects:
                            button_rect = self._model_delegate._delete_button_rects[index.row()]
                            # Converti le coordinate
                            viewport_pos = event.position().toPoint()
                            if button_rect.contains(viewport_pos):
                                if event.type() == event.Type.MouseButtonRelease:
                                    # Emetti il segnale per eliminare
                                    self._on_delete_model_clicked(model_id)
                                return True  # Blocca l'evento
        return super().eventFilter(obj, event)
