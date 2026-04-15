"""Model spese — Gestione delle spese."""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Dict, Any, Optional


@dataclass
class Expense:
    """Voce di spesa."""

    id: str
    category_id: str
    description: str
    amount: float
    date: str  # ISO format: YYYY-MM-DD
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Converte la spesa in dizionario serializzabile."""
        return {
            "id": self.id,
            "category_id": self.category_id,
            "description": self.description,
            "amount": self.amount,
            "date": self.date,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Expense":
        """Crea una spesa da dizionario."""
        return cls(
            id=data["id"],
            category_id=data["category_id"],
            description=data["description"],
            amount=data["amount"],
            date=data["date"],
            note=data.get("note", ""),
        )


@dataclass
class ExpenseFilter:
    """Filtri per la ricerca delle spese."""

    category_id: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None


class ExpensesManager:
    """Gestisce le spese."""

    def __init__(self):
        self._expenses: List[Expense] = []

    def add_expense(self, expense: Expense) -> None:
        """Aggiunge una spesa."""
        self._expenses.append(expense)

    def update_expense(self, expense_id: str, updated_data: Dict[str, Any]) -> bool:
        """Aggiorna una spesa esistente."""
        for i, exp in enumerate(self._expenses):
            if exp.id == expense_id:
                for key, value in updated_data.items():
                    if hasattr(exp, key):
                        setattr(exp, key, value)
                return True
        return False

    def delete_expense(self, expense_id: str) -> bool:
        """Elimina una spesa."""
        initial_len = len(self._expenses)
        self._expenses = [exp for exp in self._expenses if exp.id != expense_id]
        return len(self._expenses) < initial_len

    def get_expenses(
        self, filter_params: Optional[ExpenseFilter] = None
    ) -> List[Expense]:
        """Recupera le spese, applicando eventuali filtri."""
        expenses = self._expenses
        if filter_params:
            if filter_params.category_id:
                expenses = [
                    e for e in expenses if e.category_id == filter_params.category_id
                ]
            if filter_params.start_date:
                expenses = [e for e in expenses if e.date >= filter_params.start_date]
            if filter_params.end_date:
                expenses = [e for e in expenses if e.date <= filter_params.end_date]
            if filter_params.min_amount is not None:
                expenses = [e for e in expenses if e.amount >= filter_params.min_amount]
            if filter_params.max_amount is not None:
                expenses = [e for e in expenses if e.amount <= filter_params.max_amount]
        return expenses

    def get_expenses_by_period(self, start_date: str, end_date: str) -> List[Expense]:
        """Recupera spese in un intervallo di date."""
        return self.get_expenses(
            ExpenseFilter(start_date=start_date, end_date=end_date)
        )

    def get_total_spent(self, filter_params: Optional[ExpenseFilter] = None) -> float:
        """Calcola il totale speso."""
        return sum(exp.amount for exp in self.get_expenses(filter_params))

    def get_spent_by_category(
        self, category_id: str, filter_params: Optional[ExpenseFilter] = None
    ) -> float:
        """Calcola le spese per categoria."""
        filter_params = filter_params or ExpenseFilter()
        filter_params.category_id = category_id
        return self.get_total_spent(filter_params)

    def to_dict(self) -> List[Dict[str, Any]]:
        """Converte tutte le spese in lista di dizionari."""
        return [exp.to_dict() for exp in self._expenses]

    def from_dict(self, data: List[Dict[str, Any]]) -> None:
        """Carica spese da lista di dizionari."""
        self._expenses = [Expense.from_dict(item) for item in data]
