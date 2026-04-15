"""Model modelli — Gestione dei modelli di budget."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .settings import CategoryConfig


@dataclass
class BudgetCategory:
    """Categoria del budget con importo calcolato."""

    id: str
    name: str
    percentage: float
    budget_amount: float = 0.0
    spent_amount: float = 0.0

    @property
    def remaining_amount(self) -> float:
        """Residuo disponibile per questa categoria."""
        return self.budget_amount - self.spent_amount

    @property
    def is_over_spent(self) -> bool:
        """Verifica se la categoria è in sovraccosto."""
        return self.spent_amount > self.budget_amount

    @property
    def progress_percentage(self) -> float:
        """Percentuale di utilizzo del budget."""
        if self.budget_amount == 0:
            return 0.0
        return min((self.spent_amount / self.budget_amount) * 100, 100.0)


@dataclass
class BudgetModel:
    """Modello di budget completo."""

    id: str
    name: str
    description: str
    salary_reference: float = 0.0
    categories: List[BudgetCategory] = field(default_factory=list)

    def calculate_budgets(self, salary: float) -> None:
        """Calcola gli importi budget per ogni categoria."""
        for category in self.categories:
            category.budget_amount = salary * (category.percentage / 100.0)

    def get_category(self, category_id: str) -> Optional[BudgetCategory]:
        """Recupera una categoria per ID."""
        for cat in self.categories:
            if cat.id == category_id:
                return cat
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Converte il modello in dizionario serializzabile."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "salary_reference": self.salary_reference,
            "categories": [
                {
                    "id": cat.id,
                    "name": cat.name,
                    "percentage": cat.percentage,
                    "budget_amount": cat.budget_amount,
                    "spent_amount": cat.spent_amount,
                }
                for cat in self.categories
            ],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BudgetModel":
        """Crea un modello da dizionario."""
        categories = [
            BudgetCategory(
                id=cat["id"],
                name=cat["name"],
                percentage=cat["percentage"],
                budget_amount=cat.get("budget_amount", 0.0),
                spent_amount=cat.get("spent_amount", 0.0),
            )
            for cat in data.get("categories", [])
        ]
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            salary_reference=data.get("salary_reference", 0.0),
            categories=categories,
        )


class ModelsManager:
    """Gestisce i modelli di budget."""

    def __init__(self):
        self._models: Dict[str, BudgetModel] = {}
        self._current_model_id: str = "default"

    def add_model(self, model: BudgetModel) -> None:
        """Aggiunge un modello."""
        self._models[model.id] = model

    def get_model(self, model_id: str) -> Optional[BudgetModel]:
        """Recupera un modello per ID."""
        return self._models.get(model_id)

    def get_current_model(self) -> Optional[BudgetModel]:
        """Recupera il modello attualmente attivo."""
        return self._models.get(self._current_model_id)

    def set_current_model(self, model_id: str) -> bool:
        """Imposta il modello attivo."""
        if model_id in self._models:
            self._current_model_id = model_id
            return True
        return False

    def list_models(self) -> List[BudgetModel]:
        """Restituisce tutti i modelli disponibili."""
        return list(self._models.values())
