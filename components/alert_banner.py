"""AlertBanner — Banner orizzontale per avvisi e notifiche."""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont


class AlertBanner(QWidget):
    """Banner orizzontale full-width per avvisi e notifiche.
    
    Tre livelli:
    - info (blu): informazioni generali
    - warning (giallo): avvisi di attenzione
    - error (rosso): errori o sforamenti
    """

    closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._auto_close_timer = None
        self._setup_ui()
        self.hide()

    def _setup_ui(self) -> None:
        """Configura il layout del banner."""
        # Layout orizzontale
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(15, 10, 15, 10)
        self._layout.setSpacing(10)

        # Icona
        self._icon_label = QLabel()
        self._icon_label.setFont(QFont("Arial", 14))
        self._layout.addWidget(self._icon_label)

        # Testo messaggio
        self._message_label = QLabel()
        self._message_label.setWordWrap(True)
        self._message_label.setFont(QFont("Arial", 11))
        self._layout.addWidget(self._message_label, 1)

        # Pulsante chiudi
        self._close_btn = QPushButton("✕")
        self._close_btn.setFixedSize(24, 24)
        self._close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close_btn.clicked.connect(self.hide_banner)
        self._layout.addWidget(self._close_btn)

    def show_message(self, text: str, level: str = "info", auto_dismiss_ms: int = 0) -> None:
        """Mostra un messaggio nel banner.
        
        Args:
            text: Testo del messaggio
            level: Livello del messaggio ("info", "warning", "error")
            auto_dismiss_ms: Tempo in ms dopo cui chiudere automaticamente (0 = mai)
        """
        self._message_label.setText(text)

        # Configura stile in base al livello
        if level == "error":
            bg_color = "#F44336"
            icon = "⚠"
        elif level == "warning":
            bg_color = "#FFC107"
            text_color = "#1a1a2e"
            icon = "⚡"
        else:  # info
            bg_color = "#2196F3"
            icon = "ℹ"

        text_color = "#ffffff" if level != "warning" else "#1a1a2e"

        self._icon_label.setText(icon)
        self._icon_label.setStyleSheet(f"color: {text_color};")
        self._message_label.setStyleSheet(f"color: {text_color};")
        self._close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {text_color};
                border: none;
                font-weight: bold;
                border-radius: 12px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.2);
            }}
        """)

        self.setStyleSheet(f"""
            AlertBanner {{
                background-color: {bg_color};
                border-radius: 8px;
            }}
        """)

        # Mostra il banner
        self.show()

        # Configura auto-dismiss se richiesto
        if auto_dismiss_ms > 0:
            if self._auto_close_timer is None:
                self._auto_close_timer = QTimer(self)
                self._auto_close_timer.setSingleShot(True)
                self._auto_close_timer.timeout.connect(self.hide_banner)
            self._auto_close_timer.start(auto_dismiss_ms)

    def hide_banner(self) -> None:
        """Nasconde il banner."""
        self.hide()
        self.closed.emit()

        # Ferma il timer se attivo
        if self._auto_close_timer and self._auto_close_timer.isActive():
            self._auto_close_timer.stop()
