"""BudgetProgressBar — Barra di progresso con colorazione dinamica."""

from PyQt6.QtWidgets import QProgressBar
from PyQt6.QtCore import Qt


class BudgetProgressBar(QProgressBar):
    """Barra di progresso con colorazione dinamica basata sulla percentuale.
    
    - Verde (0%–59%): budget ampiamente disponibile
    - Giallo (60%–84%): attenzione, budget in esaurimento
    - Rosso (85%–100%+): budget quasi esaurito o sforato
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.set_value(0)

    def _setup_ui(self) -> None:
        """Configura l'aspetto della barra."""
        self.setMinimumHeight(12)
        self.setMaximumHeight(12)
        self.setTextVisible(False)
        self.setRange(0, 100)

    def set_value(self, percentage: float) -> None:
        """Imposta il valore della barra e aggiorna il colore.
        
        Args:
            percentage: Percentuale di utilizzo (può essere > 100)
        """
        display_value = min(max(percentage, 0), 100)
        self.setValue(int(display_value))

        if percentage <= 59:
            status = "ok"
        elif percentage <= 84:
            status = "warning"
        else:
            status = "danger"

        self.setProperty("status", status)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
