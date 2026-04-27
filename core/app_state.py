"""AppState — Singleton che mantiene lo stato globale dell'applicazione.

Emette segnali Qt quando lo stato cambia, permettendo ai controller
di reagire senza accoppiamento diretto tra pagine.
"""

from __future__ import annotations
from datetime import date
from pathlib import Path
from typing import Optional, Tuple

from PyQt6.QtCore import QObject, pyqtSignal

from models.storage import Storage
from models.settings_model import SettingsModel
from models.model_model import ModelModel
from models.salary_model import SalaryModel
from models.expense_model import ExpenseModel


class AppState(QObject):
    """Singleton che mantiene lo stato globale dell'applicazione."""

    # Segnali emessi al cambio di stato
    salary_changed = pyqtSignal(float)          # nuovo importo stipendio
    model_changed = pyqtSignal(str)             # id del nuovo modello attivo
    period_changed = pyqtSignal(object, object) # (data_inizio, data_fine)
    settings_changed = pyqtSignal()             # qualsiasi setting modificato
    expenses_changed = pyqtSignal()             # spesa aggiunta/rimossa/modificata

    _instance: Optional[AppState] = None

    def __new__(cls) -> AppState:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @classmethod
    def instance(cls) -> AppState:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._initialized = True

        # Stato corrente
        self._current_salary: float = 0.0
        self._current_model_id: str = ""
        self._current_period: Optional[Tuple[date, date]] = None
        self._salary_day: int = 27

        # Modelli (inizializzati in set_data_path)
        self._storage: Optional[Storage] = None
        self._settings_model: Optional[SettingsModel] = None
        self._model_model: Optional[ModelModel] = None
        self._salary_model: Optional[SalaryModel] = None
        self._expense_model: Optional[ExpenseModel] = None

    def set_data_path(self, data_path: Path) -> None:
        """Inizializza i modelli con il percorso dati specificato."""
        self._storage = Storage(data_path)
        self._settings_model = SettingsModel(self._storage)
        self._model_model = ModelModel(self._storage)
        self._salary_model = SalaryModel(self._storage)
        self._expense_model = ExpenseModel(self._storage)

        # Carica lo stato iniziale
        self._salary_day = self._settings_model.get_salary_day()
        active_model_id = self._settings_model.get_active_model_id()
        if self._model_model.has_model(active_model_id):
            self._current_model_id = active_model_id
        else:
            self._current_model_id = ""

    # === Proprietà ===

    @property
    def current_salary(self) -> float:
        return self._current_salary

    @current_salary.setter
    def current_salary(self, value: float) -> None:
        if self._current_salary != value:
            self._current_salary = value
            self.salary_changed.emit(value)

    @property
    def current_model_id(self) -> str:
        return self._current_model_id

    @current_model_id.setter
    def current_model_id(self, value: str) -> None:
        if self._current_model_id != value:
            self._current_model_id = value
            self.model_changed.emit(value)

    @property
    def current_period(self) -> tuple[date, date] | None:
        return self._current_period

    @current_period.setter
    def current_period(self, value: tuple[date, date]) -> None:
        self._current_period = value
        self.period_changed.emit(value[0], value[1])

    @property
    def salary_day(self) -> int:
        return self._salary_day

    @salary_day.setter
    def salary_day(self, value: int) -> None:
        self._salary_day = value
        self.settings_changed.emit()

    # === Accesso ai modelli ===

    @property
    def storage(self) -> Storage | None:
        return self._storage

    @property
    def settings_model(self) -> SettingsModel | None:
        return self._settings_model

    @property
    def model_model(self) -> ModelModel | None:
        return self._model_model

    @property
    def salary_model(self) -> SalaryModel | None:
        return self._salary_model

    @property
    def expense_model(self) -> ExpenseModel | None:
        return self._expense_model

    # === Metodi di convenienza ===

    def notify_expenses_changed(self) -> None:
        """Notifica che le spese sono cambiate."""
        self.expenses_changed.emit()

    def refresh_from_settings(self) -> None:
        """Ricarica lo stato dai settings su disco."""
        if self._settings_model:
            self._settings_model.refresh()
            if self._model_model:
                self._model_model.refresh()
            self._salary_day = self._settings_model.get_salary_day()
            active_model_id = self._settings_model.get_active_model_id()
            if self._model_model and self._model_model.has_model(active_model_id):
                resolved_model_id = active_model_id
            else:
                resolved_model_id = ""
            self.current_model_id = resolved_model_id
            self.settings_changed.emit()
