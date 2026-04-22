"""MainWindow — Finestra principale con sidebar e QStackedWidget."""

from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget,
    QMessageBox
)
from PyQt6.QtCore import Qt

from components.sidebar import Sidebar
from views.dashboard_view import DashboardView
from views.expenses_view import ExpensesView
from views.history_view import HistoryView
from controllers.dashboard_ctrl import DashboardController
from controllers.expenses_ctrl import ExpensesController
from controllers.history_ctrl import HistoryController


class MainWindow(QMainWindow):
    """Finestra principale dell'applicazione.

    Layout:
    ┌──────────┬────────────────────────────────┐
    │          │                                │
    │ Sidebar  │     QStackedWidget             │
    │          │     (Dashboard | Spese | Storico) │
    │          │                                │
    └──────────┴────────────────────────────────┘
    """

    def __init__(self, data_path: Path, parent=None):
        super().__init__(parent)
        self._data_path = data_path
        self._setup_ui()
        self._setup_controllers()

    def _setup_ui(self) -> None:
        self.setWindowTitle("WageWise")
        self.setMinimumSize(1024, 768)
        self.resize(1280, 800)

        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principale
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self._sidebar = Sidebar()
        self._sidebar.page_changed.connect(self._on_page_changed)
        main_layout.addWidget(self._sidebar)

        # StackedWidget per le pagine
        self._stack = QStackedWidget()
        main_layout.addWidget(self._stack, 1)

        # Crea le 3 pagine
        self._dashboard_view = DashboardView()
        self._expenses_view = ExpensesView()
        self._history_view = HistoryView()

        # Aggiungi allo stack
        self._stack.addWidget(self._dashboard_view)
        self._stack.addWidget(self._expenses_view)
        self._stack.addWidget(self._history_view)

    def _setup_controllers(self) -> None:
        """Inizializza i controller per ogni pagina."""
        # Controller Dashboard
        self._dashboard_ctrl = DashboardController(
            self._dashboard_view,
            self._data_path
        )

        # Controller Spese (Epica 3)
        self._expenses_ctrl = ExpensesController(
            self._expenses_view,
            self._data_path
        )

        # Controller Storico (Epica 4)
        self._history_ctrl = HistoryController(
            self._history_view,
            self._data_path
        )

    def _on_page_changed(self, index: int) -> None:
        """Gestisce il cambio di pagina dalla sidebar."""
        self._stack.setCurrentIndex(index)

        # Chiama refresh sul controller della pagina attiva
        if index == 0 and hasattr(self, '_dashboard_ctrl'):
            self._dashboard_ctrl.refresh()
        elif index == 1 and hasattr(self, '_expenses_ctrl'):
            self._expenses_ctrl.refresh()
        elif index == 2 and hasattr(self, '_history_ctrl'):
            self._history_ctrl.refresh()
