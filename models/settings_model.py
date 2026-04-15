"""WageWise - Model per la gestione delle impostazioni applicative."""

from pathlib import Path
from models.storage import read_json, write_json

_DEFAULT_SETTINGS = {
    "salary_day": 27,
    "active_model_id": "model_builtin_50_30_20",
    "currency": "€",
    "theme": "dark",
}


class SettingsModel:
    """CRUD su settings.json."""

    def __init__(self, data_dir: Path) -> None:
        self._path = data_dir / "settings.json"
        self._data = read_json(self._path, dict(_DEFAULT_SETTINGS))

    def _save(self) -> None:
        write_json(self._path, self._data)

    # --- Getters ---
    def get_salary_day(self) -> int:
        return int(self._data.get("salary_day", _DEFAULT_SETTINGS["salary_day"]))

    def get_active_model_id(self) -> str:
        return str(self._data.get("active_model_id", _DEFAULT_SETTINGS["active_model_id"]))

    def get_currency(self) -> str:
        return str(self._data.get("currency", _DEFAULT_SETTINGS["currency"]))

    def get_theme(self) -> str:
        return str(self._data.get("theme", _DEFAULT_SETTINGS["theme"]))

    # --- Setters ---
    def set_salary_day(self, value: int) -> None:
        if not 1 <= value <= 31:
            raise ValueError("salary_day deve essere tra 1 e 31")
        self._data["salary_day"] = value
        self._save()

    def set_active_model_id(self, model_id: str) -> None:
        self._data["active_model_id"] = model_id
        self._save()

    def set_currency(self, currency: str) -> None:
        self._data["currency"] = currency
        self._save()

    def set_theme(self, theme: str) -> None:
        if theme not in ("dark", "light"):
            raise ValueError("Il tema deve essere 'dark' o 'light'")
        self._data["theme"] = theme
        self._save()
