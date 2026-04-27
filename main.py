"""WageWise — Entry point dell'applicazione desktop."""

import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from views.main_window import MainWindow
from core.app_state import AppState
from core.runtime_paths import get_data_path, get_stylesheet_path, get_window_icon_path


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("WageWise")

    # Carica il foglio di stile
    qss_path = get_stylesheet_path()
    if qss_path.exists():
        with open(qss_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())

    # Imposta icona applicazione
    icon_path = get_window_icon_path()
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Inizializza il percorso dati
    data_path = get_data_path()

    # Inizializza l'AppState singleton
    app_state = AppState.instance()
    app_state.set_data_path(data_path)

    # Crea e mostra la finestra principale
    window = MainWindow(data_path=data_path)
    window.show()

    # Aggiorna lo stato della navigazione DOPO che tutto è inizializzato
    window.update_navigation_state()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
