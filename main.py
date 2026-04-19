"""WageWise — Entry point dell'applicazione desktop."""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from views.main_window import MainWindow
from core.app_state import AppState


def get_base_path() -> Path:
    """Restituisce il percorso base dell'app, funziona sia in sviluppo che da PyInstaller."""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


def get_data_path() -> Path:
    """Restituisce il percorso della cartella dati, specifico per il sistema operativo."""
    import os
    if sys.platform == 'win32':
        base = Path(os.environ.get('LOCALAPPDATA', Path.home()))
    elif sys.platform == 'darwin':
        base = Path.home() / 'Library' / 'Application Support'
    else:
        base = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share'))
    data_dir = base / 'WageWise' / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("WageWise")

    # Carica il foglio di stile
    base_path = get_base_path()
    qss_path = base_path / 'assets' / 'style.qss'
    if qss_path.exists():
        with open(qss_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())

    # Imposta icona applicazione
    icon_path = base_path / 'assets' / 'icon.ico'
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

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
