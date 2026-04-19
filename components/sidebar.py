"""Componente Sidebar — Widget navigazione laterale."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont


class Sidebar(QWidget):
    """Sidebar con logo e pulsanti di navigazione."""

    page_changed = pyqtSignal(int)  # Indice della pagina selezionata (0, 1, 2)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_index = 0
        self._buttons: list[QPushButton] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setFixedWidth(200)
        self.setObjectName("sidebar")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)

        # Logo / Nome app
        logo = QLabel("💰 WageWise")
        logo_font = QFont()
        logo_font.setPointSize(16)
        logo_font.setBold(True)
        logo.setFont(logo_font)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        # Spazio
        layout.addSpacing(30)

        # Pulsanti di navigazione
        self._btn_dashboard = QPushButton("📊 Dashboard")
        self._btn_expenses = QPushButton("💸 Spese")
        self._btn_history = QPushButton("📈 Storico")

        self._buttons = [
            self._btn_dashboard,
            self._btn_expenses,
            self._btn_history,
        ]

        for i, btn in enumerate(self._buttons):
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(45)
            btn.clicked.connect(lambda checked, idx=i: self._on_button_clicked(idx))
            layout.addWidget(btn)

        # Seleziona il primo di default
        self._buttons[0].setChecked(True)

        # Spazio espandibile in fondo
        layout.addStretch()

    def _on_button_clicked(self, index: int) -> None:
        """Gestisce il click su un pulsante di navigazione."""
        self.set_current_index(index)
        self.page_changed.emit(index)

    def set_current_index(self, index: int) -> None:
        """Imposta il pulsante attivo in base all'indice."""
        if 0 <= index < len(self._buttons):
            self._current_index = index
            for i, btn in enumerate(self._buttons):
                btn.setChecked(i == index)
