"""Model per la gestione delle impostazioni applicative (settings.json)."""

from models.storage import Storage, CorruptedFileError


DEFAULT_SETTINGS = {
    "salary_day": 27,
    "active_model_id": "model_builtin_50_30_20",
    "currency": "€",
    "theme": "dark"
}


class SettingsModel:
    """CRUD per il file settings.json."""

    FILENAME = "settings.json"

    def __init__(self, storage: Storage):
        self._storage = storage
        self._data: dict = {}
        self._load()

    def _load(self) -> None:
        try:
            self._data = self._storage.read_json(
                self.FILENAME, default=dict(DEFAULT_SETTINGS)
            )
        except CorruptedFileError:
            self._data = dict(DEFAULT_SETTINGS)
            self._save()

        for key, value in DEFAULT_SETTINGS.items():
            if key not in self._data:
                self._data[key] = value

    def _save(self) -> None:
        self._storage.write_json(self.FILENAME, self._data)

    def get_salary_day(self) -> int:
        return self._data.get("salary_day", DEFAULT_SETTINGS["salary_day"])

    def get_active_model_id(self) -> str:
        return self._data.get("active_model_id", DEFAULT_SETTINGS["active_model_id"])

    def get_currency(self) -> str:
        return self._data.get("currency", DEFAULT_SETTINGS["currency"])

    def get_theme(self) -> str:
        return self._data.get("theme", DEFAULT_SETTINGS["theme"])

    def get_all(self) -> dict:
        return dict(self._data)

    def set_salary_day(self, day: int) -> None:
        if not 1 <= day <= 31:
            raise ValueError(f"salary_day deve essere tra 1 e 31, ricevuto {day}")
        self._data["salary_day"] = day
        self._save()

    def set_active_model_id(self, model_id: str) -> None:
        if not model_id:
            raise ValueError("active_model_id non può essere vuoto")
        self._data["active_model_id"] = model_id
        self._save()

    def set_currency(self, currency: str) -> None:
        self._data["currency"] = currency
        self._save()

    def set_theme(self, theme: str) -> None:
        if theme not in ("dark", "light"):
            raise ValueError(f"Theme deve essere 'dark' o 'light', ricevuto '{theme}'")
        self._data["theme"] = theme
        self._save()

    def set_all(self, settings: dict) -> None:
        self._data.update(settings)
        self._save()
