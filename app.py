"""AppState singleton — Stato globale condiviso e QApplication."""

import sys
from PyQt6.QtWidgets import QApplication
from state.app_state import AppState


def create_app() -> QApplication:
    """Crea e restituisce l'istanza QApplication."""
    if QApplication.instance() is None:
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    return app


def get_app_state() -> AppState:
    """Restituisce l'istanza singleton di AppState."""
    return AppState.get_instance()
