"""Model per la gestione dello storico stipendi (salaries.json)."""

import copy
import uuid
from datetime import date, timedelta

from core.period import get_period_for_date
from models.expense_model import DEFAULT_EXPENSES, ExpenseModel
from models.model_model import DEFAULT_MODELS, ModelModel
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

    def _model_exists(self, model_id: str) -> bool:
        try:
            data = self._storage.read_json(
                ModelModel.FILENAME,
                default=copy.deepcopy(DEFAULT_MODELS),
            )
        except CorruptedFileError as exc:
            raise ValueError(
                "Impossibile validare il modello dello stipendio: model.json è corrotto."
            ) from exc

        return any(model.get("id") == model_id for model in data.get("models", []))

    def _validate_model_id(self, model_id: str) -> None:
        if not model_id:
            raise ValueError("model_id non può essere vuoto")
        if not self._model_exists(model_id):
            raise ValueError(f"Modello stipendio non valido: '{model_id}'")

    def _validate_period_bounds(self, start_date_str: str,
                                period_end_str: str | None) -> None:
        if period_end_str is None:
            return
        try:
            period_start = date.fromisoformat(start_date_str)
            period_end = date.fromisoformat(period_end_str)
        except ValueError as exc:
            raise ValueError("Le date del periodo devono essere nel formato YYYY-MM-DD") from exc
        if period_end < period_start:
            raise ValueError("period_end non può essere precedente a period_start")

    def _salary_has_expenses(self, salary_id: str) -> bool:
        try:
            data = self._storage.read_json(
                ExpenseModel.FILENAME,
                default=dict(DEFAULT_EXPENSES),
            )
        except CorruptedFileError as exc:
            raise ValueError(
                "Impossibile eliminare lo stipendio: expenses.json è corrotto."
            ) from exc

        return any(
            expense.get("salary_period_id") == salary_id
            for expense in data.get("expenses", [])
        )

    def refresh(self) -> None:
        """Ricarica i dati dal disco."""
        self._load()

    def get_all_salaries(self) -> list[dict]:
        salaries = list(self._data.get("salaries", []))
        salaries.sort(key=lambda s: s.get("period_start", s.get("date", "")))
        return salaries

    def get_latest_salary(self) -> dict | None:
        salaries = self.get_all_salaries()
        if not salaries:
            return None
        return dict(salaries[-1])

    def get_period_bounds(self, salary: dict,
                          salary_day: int | None = None) -> tuple[date, date]:
        """Restituisce i confini congelati del periodo di uno stipendio."""
        period_start_str = salary.get("period_start")
        period_end_str = salary.get("period_end")
        if period_start_str and period_end_str:
            return (
                date.fromisoformat(period_start_str),
                date.fromisoformat(period_end_str),
            )

        sal_date = date.fromisoformat(salary["date"])
        if salary_day is None:
            salary_day = sal_date.day
        return get_period_for_date(sal_date, salary_day)

    def get_salary_covering_date(self, target_date: date,
                                 salary_day: int) -> dict | None:
        """Restituisce lo stipendio il cui periodo include la data indicata."""
        salaries = sorted(
            self._data.get("salaries", []),
            key=lambda salary: salary.get("period_start", salary.get("date", "")),
            reverse=True,
        )
        for salary in salaries:
            try:
                period_start, period_end = self.get_period_bounds(salary, salary_day)
            except (ValueError, KeyError):
                continue
            if period_start <= target_date <= period_end:
                return dict(salary)
        return None

    def get_effective_period_for_date(self, target_date: date,
                                      salary_day: int) -> tuple[date, date]:
        """Calcola il periodo corrente evitando sovrapposizioni con lo storico."""
        salary = self.get_salary_covering_date(target_date, salary_day)
        if salary:
            return self.get_period_bounds(salary, salary_day)

        period_start, period_end = get_period_for_date(target_date, salary_day)
        latest_salary = self.get_latest_salary()
        if latest_salary is None:
            return period_start, period_end

        latest_start, latest_end = self.get_period_bounds(latest_salary, salary_day)
        if latest_start <= target_date <= latest_end:
            return latest_start, latest_end
        if latest_end < target_date and period_start <= latest_end:
            period_start = latest_end + timedelta(days=1)
        return period_start, period_end

    def ensure_period_metadata(self, salary_day: int) -> bool:
        """Congela i periodi storici nei record esistenti quando mancanti."""
        salaries = sorted(self._data.get("salaries", []), key=lambda s: s.get("date", ""))
        parsed_starts: list[date | None] = []
        changed = False

        for salary in salaries:
            try:
                parsed_starts.append(date.fromisoformat(salary["date"]))
            except (ValueError, KeyError):
                parsed_starts.append(None)

        for index, salary in enumerate(salaries):
            period_start = parsed_starts[index]
            if period_start is None:
                continue

            try:
                stored_start = date.fromisoformat(salary.get("period_start", ""))
            except ValueError:
                stored_start = None
            if stored_start is None:
                salary["period_start"] = period_start.isoformat()
                changed = True

            try:
                stored_end = date.fromisoformat(salary.get("period_end", ""))
            except ValueError:
                stored_end = None
            if stored_end is not None:
                continue

            next_start = None
            for next_index in range(index + 1, len(parsed_starts)):
                if parsed_starts[next_index] is not None:
                    next_start = parsed_starts[next_index]
                    break

            if next_start is not None:
                period_end = next_start - timedelta(days=1)
            else:
                _, period_end = get_period_for_date(period_start, salary_day)

            salary["period_end"] = period_end.isoformat()
            changed = True

        if changed:
            self._save()
        return changed

    def is_model_in_use(self, model_id: str) -> bool:
        return any(
            salary.get("model_id") == model_id
            for salary in self._data.get("salaries", [])
        )

    def get_salary_by_id(self, salary_id: str) -> dict | None:
        for salary in self._data.get("salaries", []):
            if salary["id"] == salary_id:
                return dict(salary)
        return None

    def get_salary_for_period(self, period_start: date, period_end: date) -> dict | None:
        for salary in self._data.get("salaries", []):
            try:
                stored_start, stored_end = self.get_period_bounds(salary)
                if stored_start == period_start and stored_end == period_end:
                    return dict(salary)
            except (ValueError, KeyError):
                continue

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
                   note: str = "", period_end_str: str | None = None) -> dict:
        if amount <= 0:
            raise ValueError(f"L'importo deve essere positivo, ricevuto {amount}")

        try:
            date.fromisoformat(date_str)
        except ValueError:
            raise ValueError(f"Data non valida: '{date_str}'. Usa il formato YYYY-MM-DD")

        self._validate_model_id(model_id)
        self._validate_period_bounds(date_str, period_end_str)

        salary_id = f"sal_{uuid.uuid4().hex[:8]}"
        new_salary = {
            "id": salary_id,
            "amount": round(amount, 2),
            "date": date_str,
            "model_id": model_id,
            "note": note,
            "period_start": date_str,
            "period_end": period_end_str or date_str,
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
            salary["period_start"] = date_str
            period_end = salary.get("period_end")
            self._validate_period_bounds(date_str, period_end)

        if model_id is not None:
            self._validate_model_id(model_id)
            salary["model_id"] = model_id

        if note is not None:
            salary["note"] = note

        self._save()
        return dict(salary)

    def delete_salary(self, salary_id: str) -> None:
        if self._salary_has_expenses(salary_id):
            raise ValueError(
                "Impossibile eliminare lo stipendio: esistono spese collegate a questo periodo."
            )
        original_len = len(self._data["salaries"])
        self._data["salaries"] = [
            s for s in self._data["salaries"] if s["id"] != salary_id
        ]
        if len(self._data["salaries"]) == original_len:
            raise KeyError(f"Stipendio '{salary_id}' non trovato")
        self._save()

    def overwrite_salary_for_period(self, amount: float, date_str: str,
                                     model_id: str, note: str = "",
                                     period_end_str: str | None = None) -> dict:
        self._validate_model_id(model_id)
        self._validate_period_bounds(date_str, period_end_str)
        for salary in self._data["salaries"]:
            if salary["date"] == date_str:
                salary["amount"] = round(amount, 2)
                salary["model_id"] = model_id
                salary["note"] = note
                salary.setdefault("period_start", date_str)
                if period_end_str is not None:
                    salary["period_end"] = period_end_str
                self._save()
                return dict(salary)

        return self.add_salary(
            amount,
            date_str,
            model_id,
            note,
            period_end_str=period_end_str,
        )

    def _find_salary(self, salary_id: str) -> dict | None:
        for salary in self._data.get("salaries", []):
            if salary["id"] == salary_id:
                return salary
        return None
