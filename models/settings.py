"""Model settings — Configurazioni globali del budget."""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class CategoryConfig:
    """Configurazione di una singola categoria del budget."""

    id: str
    name: str
    percentage: float


@dataclass
class BudgetModel:
    """Modello di distribuzione del budget."""

    id: str
    name: str
    description: str
    categories: List[CategoryConfig] = field(default_factory=list)

    def total_percentage(self) -> float:
        """Calcola la somma delle percentuali delle categorie."""
        return sum(cat.percentage for cat in self.categories)

    def is_valid(self) -> bool:
        """Verifica che il modello sia valido (percentuali totali = 100)."""
        return abs(self.total_percentage() - 100.0) < 0.01


@dataclass
class SalaryModelConfig:
    """Configurazioni per i modelli di stipendio."""

    default_model_id: str = "default"
    allowed_models: List[str] = field(default_factory=lambda: ["default", "zero_based"])


# Configurazione globale
GLOBAL_SETTINGS = SalaryModelConfig()
