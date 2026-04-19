"""Model per la gestione del registro spese (expenses.json)."""

import uuid
from datetime import date
from models.storage import Storage, CorruptedFileError


DEFAULT_EXPENSES = {"expenses": []}


class ExpenseModel:
    """CRUD per il file expenses.json."""

    FILENAME = "expenses.json"

    def __init__(self, storage: Storage):
        self._storage = storage
        self._data: dict = {}
        self._load()

    def _load(self) -> None:
        try:
            self._data = self._storage.read_json(
                self.FILENAME, default=dict(DEFAULT_EXPENSES)
            )
        except CorruptedFileError:
            self._data = dict(DEFAULT_EXPENSES)
            self._save()

        if "expenses" not in self._data:
            self._data["expenses"] = []

    def _save(self) -> None:
        self._storage.write_json(self.FILENAME, self._data)

    def get_all_expenses(self) -> list[dict]:
        expenses = list(self._data.get("expenses", []))
        expenses.sort(key=lambda e: e.get("date", ""), reverse=True)
        return expenses

    def get_expense_by_id(self, expense_id: str) -> dict | None:
        for expense in self._data.get("expenses", []):
            if expense["id"] == expense_id:
                return dict(expense)
        return None

    def get_expenses_by_period(self, salary_period_id: str) -> list[dict]:
        expenses = [
            dict(e) for e in self._data.get("expenses", [])
            if e.get("salary_period_id") == salary_period_id
        ]
        expenses.sort(key=lambda e: e.get("date", ""), reverse=True)
        return expenses

    def get_expenses_by_category(self, salary_period_id: str,
                                  category_id: str) -> list[dict]:
        expenses = [
            dict(e) for e in self._data.get("expenses", [])
            if e.get("salary_period_id") == salary_period_id
            and e.get("category_id") == category_id
        ]
        expenses.sort(key=lambda e: e.get("date", ""), reverse=True)
        return expenses

    def get_total_by_category(self, salary_period_id: str,
                               category_id: str) -> float:
        total = 0.0
        for expense in self._data.get("expenses", []):
            if (expense.get("salary_period_id") == salary_period_id
                    and expense.get("category_id") == category_id):
                total += expense.get("amount", 0.0)
        return round(total, 2)

    def get_total_by_period(self, salary_period_id: str) -> float:
        total = 0.0
        for expense in self._data.get("expenses", []):
            if expense.get("salary_period_id") == salary_period_id:
                total += expense.get("amount", 0.0)
        return round(total, 2)

    def add_expense(self, amount: float, category_id: str,
                    description: str, date_str: str,
                    salary_period_id: str) -> dict:
        if amount <= 0:
            raise ValueError(f"L'importo deve essere positivo, ricevuto {amount}")

        try:
            date.fromisoformat(date_str)
        except ValueError:
            raise ValueError(f"Data non valida: '{date_str}'. Usa il formato YYYY-MM-DD")

        expense_id = f"exp_{uuid.uuid4().hex[:8]}"
        new_expense = {
            "id": expense_id,
            "amount": round(amount, 2),
            "category_id": category_id,
            "description": description.strip(),
            "date": date_str,
            "salary_period_id": salary_period_id,
        }

        self._data["expenses"].append(new_expense)
        self._save()
        return dict(new_expense)

    def delete_expense(self, expense_id: str) -> None:
        original_len = len(self._data["expenses"])
        self._data["expenses"] = [
            e for e in self._data["expenses"] if e["id"] != expense_id
        ]
        if len(self._data["expenses"]) == original_len:
            raise KeyError(f"Spesa '{expense_id}' non trovata")
        self._save()

    def get_category_totals(self, salary_period_id: str) -> dict[str, float]:
        totals: dict[str, float] = {}
        for expense in self._data.get("expenses", []):
            if expense.get("salary_period_id") == salary_period_id:
                cat_id = expense.get("category_id", "")
                totals[cat_id] = totals.get(cat_id, 0.0) + expense.get("amount", 0.0)
        return {k: round(v, 2) for k, v in totals.items()}
