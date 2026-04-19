"""Color picker personalizzato con controlli esterni."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QLineEdit, QGridLayout, QWidget, QColorDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class CustomColorDialog(QDialog):
    """Dialog di selezione colore con controlli ±1 esterni."""
    
    def __init__(self, initial_color: str = "#4CAF50", parent=None):
        super().__init__(parent)
        self._color = QColor(initial_color)
        self._setup_ui()
        self._update_preview()
        
    def _setup_ui(self) -> None:
        self.setWindowTitle("Seleziona colore")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Preview colore
        preview_layout = QHBoxLayout()
        preview_layout.addWidget(QLabel("Colore selezionato:"))
        self._preview = QLabel()
        self._preview.setFixedSize(60, 40)
        self._preview.setStyleSheet(f"background-color: {self._color.name()}; border: 2px solid #555; border-radius: 4px;")
        preview_layout.addWidget(self._preview)
        preview_layout.addStretch()
        layout.addLayout(preview_layout)
        
        # Bottone per aprire QColorDialog nativo
        native_btn = QPushButton("Scegli dal selettore nativo...")
        native_btn.clicked.connect(self._open_native_dialog)
        layout.addWidget(native_btn)
        
        # Sezione RGB con controlli ±1
        rgb_group = QWidget()
        rgb_group.setStyleSheet("background-color: #2a2a3c; border-radius: 8px; padding: 10px;")
        rgb_layout = QGridLayout(rgb_group)
        rgb_layout.setSpacing(10)
        
        # Header
        rgb_layout.addWidget(QLabel("Componente"), 0, 0)
        rgb_layout.addWidget(QLabel("Valore"), 0, 1, Qt.AlignmentFlag.AlignCenter)
        
        # Red
        rgb_layout.addWidget(QLabel("Rosso:"), 1, 0)
        self._red_spin = self._create_spinbox()
        self._red_spin.setValue(self._color.red())
        self._red_spin.valueChanged.connect(self._on_color_changed)
        rgb_layout.addWidget(self._red_spin, 1, 1)
        
        # Green
        rgb_layout.addWidget(QLabel("Verde:"), 2, 0)
        self._green_spin = self._create_spinbox()
        self._green_spin.setValue(self._color.green())
        self._green_spin.valueChanged.connect(self._on_color_changed)
        rgb_layout.addWidget(self._green_spin, 2, 1)
        
        # Blue
        rgb_layout.addWidget(QLabel("Blu:"), 3, 0)
        self._blue_spin = self._create_spinbox()
        self._blue_spin.setValue(self._color.blue())
        self._blue_spin.valueChanged.connect(self._on_color_changed)
        rgb_layout.addWidget(self._blue_spin, 3, 1)
        
        layout.addWidget(rgb_group)
        
        # HTML hex
        hex_layout = QHBoxLayout()
        hex_layout.addWidget(QLabel("HTML:"))
        self._hex_input = QLineEdit()
        self._hex_input.setText(self._color.name())
        self._hex_input.setMaximumWidth(100)
        self._hex_input.textChanged.connect(self._on_hex_changed)
        hex_layout.addWidget(self._hex_input)
        hex_layout.addStretch()
        layout.addLayout(hex_layout)
        
        # Bottoni OK/Cancel
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Annulla")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
    def _create_spinbox(self) -> QSpinBox:
        """Crea uno spinbox per valori 0-255 senza frecce."""
        spin = QSpinBox()
        spin.setRange(0, 255)
        spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        spin.setFixedWidth(60)
        spin.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                background-color: #1e1e2e;
                border: 1px solid #3a3a4a;
                border-radius: 4px;
                color: white;
            }
            QSpinBox:focus {
                border: 1px solid #6c63ff;
            }
        """)
        return spin
        
    def _on_color_changed(self) -> None:
        """Aggiorna il colore quando cambiano i valori RGB."""
        self._color = QColor(
            self._red_spin.value(),
            self._green_spin.value(),
            self._blue_spin.value()
        )
        self._update_preview()
        self._hex_input.setText(self._color.name())
        
    def _on_hex_changed(self, text: str) -> None:
        """Aggiorna il colore quando cambia l'hex."""
        if len(text) == 7 and text.startswith("#"):
            color = QColor(text)
            if color.isValid():
                self._color = color
                self._red_spin.setValue(color.red())
                self._green_spin.setValue(color.green())
                self._blue_spin.setValue(color.blue())
                self._update_preview()
                
    def _update_preview(self) -> None:
        """Aggiorna il preview del colore."""
        self._preview.setStyleSheet(
            f"background-color: {self._color.name()}; border: 2px solid #555; border-radius: 4px;"
        )
        
    def _open_native_dialog(self) -> None:
        """Apre il dialog nativo di Qt."""
        color = QColorDialog.getColor(self._color, self, "Seleziona colore")
        if color.isValid():
            self._color = color
            self._red_spin.setValue(color.red())
            self._green_spin.setValue(color.green())
            self._blue_spin.setValue(color.blue())
            self._hex_input.setText(color.name())
            self._update_preview()
            
    def get_color(self) -> str:
        """Restituisce il colore selezionato in formato hex."""
        return self._color.name()
