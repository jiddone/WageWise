"""MainWindow — Finestra principale con navigazione."""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QLabel,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from ui.sidebar import Sidebar
from models.salary_model import ModelsManager
from services.period_service import PeriodService
from services.validator import Validator


class MainWindow(QMainWindow):
    """Finestra principale con navigazione tra pagine."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("WageWise — Gestione Bilancio")
        self.setMinimumSize(1000, 700)
        self.pages: dict[str, QWidget] = {}

        # Inizializza i manager
        self.models_manager = ModelsManager()
        self.period_service = PeriodService()
        self.validator = Validator()

        # Crea l'interfaccia
        self._setup_ui()
        self._setup_menu()
        self._setup_default_content()

    def _setup_ui(self):
        """Configura la struttura UI principale."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar(self.models_manager, self.period_service)
        self.sidebar.page_changed.connect(self._load_page)
        main_layout.addWidget(self.sidebar, 1)

        # Area contenuto (stacked widget per navigazione)
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, 3)

        # Footer
        footer = QWidget()
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(10, 5, 10, 5)
        footer_label = QLabel("WageWise v3.0 — OFFLINE")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(footer_label)
        main_layout.addWidget(footer, 1)

    def _setup_menu(self):
        """Configura il menu principale."""
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)

        # File
        file_menu = menu_bar.addMenu("File")
        exit_action = QAction("Esci", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Modelli
        models_menu = menu_bar.addMenu("Modelli")
        add_model_action = QAction("Aggiungi Modello", self)
        add_model_action.triggered.connect(self._add_new_model)
        models_menu.addAction(add_model_action)

        # Aiuto
        help_menu = menu_bar.addMenu("Aiuto")
        about_action = QAction("Informazioni", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_default_content(self):
        """Configura il contenuto iniziale."""
        # Inizializza periodi
        from datetime import date

        self.period_service.initialize_periods(date.today())
        self.sidebar.update_period_info(self.period_service.get_current_period(date.today()))

        # Carica la dashboard iniziale
        self._load_page("dashboard")

    def _load_page(self, page_name: str):
        """Carica una pagina specificata."""
        if page_name not in self.pages:
            self.pages[page_name] = self._create_placeholder_page(page_name)
            self.stacked_widget.addWidget(self.pages[page_name])

        self.stacked_widget.setCurrentWidget(self.pages[page_name])
        self.sidebar.highlight_page(page_name)

    def _create_placeholder_page(self, page_name: str) -> QWidget:
        """Crea una pagina placeholder finché la view reale non è disponibile."""
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel(f"Pagina: {page_name}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 24px; color: #666;")
        layout.addWidget(label)
        return page

    def _add_new_model(self):
        """Gestisce l'aggiunta di un nuovo modello."""
        # Logica per aggiungere modello (da implementare)
        print("Aggiungi nuovo modello richiesto")

    def _show_about(self):
        """Mostra informazioni sull'applicazione."""
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.about(
            self,
            "Informazioni",
            "WageWise v3.0\nGestione Bilancio con PyQt6\nModelli: 50/30/20, Zero-Based Budget",
        )
