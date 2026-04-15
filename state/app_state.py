"""AppState singleton - Stato globale condiviso dell'applicazione."""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal


class AppState(QObject):
    """Singleton che mantiene lo stato globale dell'applicazione.
    Emette segnali Qt quando lo stato cambia, permettendo ai controller
    di reagire senza accoppiamento diretto tra pagine."""

    # Segnali emessi al cambio di stato
    salary_changed = pyqtSignal(float)  # nuovo importo stipendio
    model_changed = pyqtSignal(str)  # id del nuovo modello attivo
    period_changed = pyqtSignal(object, object)  # (data_inizio, data_fine)
    settings_changed = pyqtSignal()  # qualsiasi setting modificato
    expenses_changed = pyqtSignal()  # spesa aggiunta/rimossa/modificata

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            super().__init__()
            self._initialized = True
            # Stato corrente
            self.current_salary: float = 0.0
            self.current_model_id: str = "default"
            self.current_period = (date.today(), date.today())
            self.salary_day: int = 15
            self.settings: Dict[str, Any] = {
                "currency": "EUR",
                "decimal_places": 2,
                "theme": "light",
            }
            self._expenses: Dict[str, list] = {}

    @classmethod
    def get_instance(cls) -> "AppState":
        """Restituisce l'istanza singleton di AppState."""
        return cls()

    # Proprietà per espense con notifica
    @property
    def expenses(self) -> Dict[str, list]:
        return self._expenses

    @expenses.setter
    def expenses(self, value: Dict[str, list]):
        self._expenses = value
        self.expenses_changed.emit()

    def update_salary(self, salary: float) -> None:
        """Aggiorna lo stipendio e emette il segnale."""
        self.current_salary = salary
        self.salary_changed.emit(salary)

    def update_model(self, model_id: str) -> None:
        """Aggiorna il modello attivo e emette il segnale."""
        self.current_model_id = model_id
        self.model_changed.emit(model_id)

    def update_period(self, start_date: date, end_date: date) -> None:
        """Aggiorna il periodo corrente e emette il segnale."""
        self.current_period = (start_date, end_date)
        self.period_changed.emit(start_date, end_date)

    def update_settings(self, key: str, value: Any) -> None:
        """Aggiorna un setting e emette il segnale."""
        self.settings[key] = value
        self.settings_changed.emit()
