"""Model per la gestione dello storico stipendi (salaries.json)."""

import uuid
from datetime import date
from models.storage import Storage, CorruptedFileError


DEFAULT_SALARIES = {"salaries": []}


class SalaryModel:
    """CRUD per il file salaries.json."""

    FILENAME = "salaries.json"

    def __init__(self, storage: Storage):
        self._storage = storage
        self._data: dict = {}
        self._load()

    def _load(self) -> None:
        try:
            self._data = self._storage.read_json(
                self.FILENAME, default=dict(DEFAULT_SALARIES)
            )
        except CorruptedFileError:
            self._data = dict(DEFAULT_SALARIES)
            self._save()

        if "salaries" not in self._data:
            self._data["salaries"] = []

    def _save(self) -> None:
        self._storage.write_json(self.FILENAME, self._data)

    def get_all_salaries(self) -> list[dict]:
        salaries = list(self._data.get("salaries", []))
        salaries.sort(key=lambda s: s.get("date", ""))
        return salaries

    def get_salary_by_id(self, salary_id: str) -> dict | None:
        for salary in self._data.get("salaries", []):
            if salary["id"] == salary_id:
                return dict(salary)
        return None

    def get_salary_for_period(self, period_start: date, period_end: date) -> dict | None:
        for salary in self._data.get("salaries", []):
            try:
                sal_date = date.fromisoformat(salary["date"])
                if period_start <= sal_date <= period_end:
                    return dict(salary)
            except (ValueError, KeyError):
                continue
        return None

    def get_salary_by_date(self, target_date: date) -> dict | None:
        for salary in self._data.get("salaries", []):
            try:
                sal_date = date.fromisoformat(salary["date"])
                if sal_date == target_date:
                    return dict(salary)
            except (ValueError, KeyError):
                continue
        return None

    def add_salary(self, amount: float, date_str: str, model_id: str,
                   note: str = "") -> dict:
        if amount <= 0:
            raise ValueError(f"L'importo deve essere positivo, ricevuto {amount}")

        try:
            date.fromisoformat(date_str)
        except ValueError:
            raise ValueError(f"Data non valida: '{date_str}'. Usa il formato YYYY-MM-DD")

        salary_id = f"sal_{uuid.uuid4().hex[:8]}"
        new_salary = {
            "id": salary_id,
            "amount": round(amount, 2),
            "date": date_str,
            "model_id": model_id,
            "note": note,
        }

        self._data["salaries"].append(new_salary)
        self._save()
        return dict(new_salary)

    def update_salary(self, salary_id: str, amount: float | None = None,
                      date_str: str | None = None, model_id: str | None = None,
                      note: str | None = None) -> dict:
        salary = self._find_salary(salary_id)
        if salary is None:
            raise KeyError(f"Stipendio '{salary_id}' non trovato")

        if amount is not None:
            if amount <= 0:
                raise ValueError(f"L'importo deve essere positivo, ricevuto {amount}")
            salary["amount"] = round(amount, 2)

        if date_str is not None:
            try:
                date.fromisoformat(date_str)
            except ValueError:
                raise ValueError(f"Data non valida: '{date_str}'")
            salary["date"] = date_str

        if model_id is not None:
            salary["model_id"] = model_id

        if note is not None:
            salary["note"] = note

        self._save()
        return dict(salary)

    def delete_salary(self, salary_id: str) -> None:
        original_len = len(self._data["salaries"])
        self._data["salaries"] = [
            s for s in self._data["salaries"] if s["id"] != salary_id
        ]
        if len(self._data["salaries"]) == original_len:
            raise KeyError(f"Stipendio '{salary_id}' non trovato")
        self._save()

    def overwrite_salary_for_period(self, amount: float, date_str: str,
                                     model_id: str, note: str = "") -> dict:
        for salary in self._data["salaries"]:
            if salary["date"] == date_str:
                salary["amount"] = round(amount, 2)
                salary["model_id"] = model_id
                salary["note"] = note
                self._save()
                return dict(salary)

        return self.add_salary(amount, date_str, model_id, note)

    def _find_salary(self, salary_id: str) -> dict | None:
        for salary in self._data.get("salaries", []):
            if salary["id"] == salary_id:
                return salary
        return None
