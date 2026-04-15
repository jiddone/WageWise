"""Sidebar — Componente navigazione laterale."""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from services.period_service import Period


class Sidebar(QWidget):
    """Sidebar con navigazione tra pagine e informazioni contestuali."""

    page_changed = pyqtSignal(str)

    def __init__(self, models_manager, period_service, parent=None):
        super().__init__(parent)
        self.models_manager = models_manager
        self.period_service = period_service
        self._setup_ui()
        self._populate_models()

    def _setup_ui(self):
        """Configura l'interfaccia della sidebar."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Titolo
        title = QLabel("WageWise")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        layout.addWidget(title)

        # Sottotitolo
        subtitle = QLabel("Gestione Bilancio")
        subtitle_font = QFont("Segoe UI", 10)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        layout.addWidget(subtitle)

        # Linea di separazione
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #bdc3c7;")
        layout.addWidget(separator)

        # Pulsanti di navigazione
        nav_pages = [
            ("🏠 Dashboard", "dashboard"),
            ("📊 Registro Spese", "expenses"),
            ("📈 Storico", "history"),
            ("⚙️ Impostazioni", "settings"),
        ]

        self.nav_buttons = {}
        for text, page_id in nav_pages:
            btn = self._create_nav_button(text, page_id)
            layout.addWidget(btn)
            self.nav_buttons[page_id] = btn

        # Linea di separazione inferiore
        layout.addStretch()
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background-color: #bdc3c7;")
        layout.addWidget(sep2)

        # Informazioni periodo corrente
        period_layout = QVBoxLayout()
        period_layout.setContentsMargins(0, 15, 0, 0)

        self.period_label = QLabel("Periodo corrente")
        self.period_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.period_label.setStyleSheet("color: #555;")
        period_layout.addWidget(self.period_label)

        self.dates_label = QLabel("-- / --")
        self.dates_label.setFont(QFont("Segoe UI", 8))
        self.dates_label.setStyleSheet("color: #888;")
        period_layout.addWidget(self.dates_label)

        layout.addLayout(period_layout)

        # Stato disponibile
        layout.addStretch()
        status_label = QLabel("Stato disponibile")
        status_label.setFont(QFont("Segoe UI", 7))
        status_label.setStyleSheet("color: #999;")
        layout.addWidget(status_label)

        self.setLayout(layout)

    def _create_nav_button(self, text: str, page_id: str) -> QPushButton:
        """Crea un pulsante di navigazione."""
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setAutoExclusive(False)  # permette deselezionare
        btn.setStyleSheet(self._get_button_style(False))
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.setMinimumHeight(40)
        font = QFont("Segoe UI", 9)
        btn.setFont(font)
        btn.clicked.connect(lambda checked, p=page_id: self._on_navigate(p))
        return btn

    def _get_button_style(self, selected: bool) -> str:
        """Restituisce lo stile CSS per i pulsanti."""
        if selected:
            return (
                "background-color: #3498db; "
                "color: white; "
                "border-radius: 6px; "
                "border: none;"
            )
        return (
            "background-color: transparent; "
            "color: #34495e; "
            "border-radius: 6px; "
            "border: 1px solid transparent; "
            "padding: 8px;"
        )

    def _populate_models(self):
        """Popola la sidebar con i modelli disponibili."""
        # Da implementare: visualizzazione modelli nella sidebar
        pass

    def _on_navigate(self, page_id: str):
        """Gestisce la richiesta di navigazione."""
        if page_id in self.nav_buttons:
            self.highlight_page(page_id)
            self.page_changed.emit(page_id)

    def update_period_info(self, period: Period):
        """Aggiorna le informazioni sul periodo corrente."""
        if period:
            self.period_label.setText(
                f"Periodo {period.start_date} - {period.end_date}"
            )
            self.dates_label.setText(
                f"{period.start_date.strftime('%d/%m/%Y')} - {period.end_date.strftime('%d/%m/%Y')}"
            )
        else:
            self.period_label.setText("Periodo non trovato")
            self.dates_label.setText("-- / --")

    def highlight_page(self, page_id: str):
        """Evidenzia la pagina corrente nella sidebar."""
        for pid, btn in self.nav_buttons.items():
            btn.setChecked(pid == page_id)
            btn.setStyleSheet(self._get_button_style(pid == page_id))
