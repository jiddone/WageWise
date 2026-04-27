"""Componente Sidebar — Widget navigazione laterale."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QPixmap

from core.runtime_paths import get_sidebar_logo_path


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

        # Logo / Nome app con icona
        icon_layout = QHBoxLayout()
        icon_layout.setContentsMargins(0, 0, 0, 0)

        # Usa l'icona grande (192x192 PNG)
        icon_path = get_sidebar_logo_path()
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path))
            scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label = QLabel()
            icon_label.setPixmap(scaled_pixmap)
            icon_layout.addStretch()
            icon_layout.addWidget(icon_label)
            icon_layout.addStretch()
        else:
            # Fallback emoji se l'icona non esiste
            icon_label = QLabel("💰")
            icon_label.setFont(QFont("", 24))
            icon_layout.addStretch()
            icon_layout.addWidget(icon_label)
            icon_layout.addStretch()

        layout.addLayout(icon_layout)

        # Spazio
        layout.addSpacing(30)

        # Pulsanti di navigazione
        self._btn_dashboard = QPushButton("Dashboard")
        self._btn_expenses = QPushButton("Spese")
        self._btn_history = QPushButton("Storico")

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
        # Se il pulsante è disabilitato, ignora il click
        if index > 0 and not self._buttons[index].isEnabled():
            return
        self.set_current_index(index)
        self.page_changed.emit(index)

    def set_current_index(self, index: int) -> None:
        """Imposta il pulsante attivo in base all'indice."""
        if 0 <= index < len(self._buttons):
            self._current_index = index
            for i, btn in enumerate(self._buttons):
                btn.setChecked(i == index)

    def set_navigation_enabled(self, enabled: bool) -> None:
        """Abilita o disabilita la navigazione alle pagine Spese e Storico.

        Quando enabled=False, i pulsanti 'Spese' e 'Storico' diventano
        non cliccabili (utile se nessun modello è attivo).
        """
        self._btn_expenses.setEnabled(enabled)
        self._btn_history.setEnabled(enabled)
