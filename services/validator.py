"""Validatori — Validazione dati di input."""

import re
from typing import Tuple, Optional


class ValidationResult:
    """Risultato della validazione."""

    def __init__(self, is_valid: bool, error: Optional[str] = None):
        self.is_valid = is_valid
        self.error = error

    def __bool__(self):
        return self.is_valid


class Validator:
    """Validatori generici per l'applicazione."""

    @staticmethod
    def validate_salary(salary: float) -> ValidationResult:
        """Validazione importo stipendio."""
        if not isinstance(salary, (int, float)):
            return ValidationResult(False, "Lo stipendio deve essere un numero")
        if salary <= 0:
            return ValidationResult(False, "Lo stipendio deve essere maggiore di zero")
        if salary > 1_000_000:
            return ValidationResult(
                False, "Lo stipendio sembra anomalo, controlla il valore"
            )
        return ValidationResult(True)

    @staticmethod
    def validate_percentage(percentage: float) -> ValidationResult:
        """Validazione percentuale."""
        if not isinstance(percentage, (int, float)):
            return ValidationResult(False, "La percentuale deve essere un numero")
        if percentage < 0 or percentage > 100:
            return ValidationResult(False, "La percentuale deve essere tra 0 e 100")
        return ValidationResult(True)

    @staticmethod
    def validate_category(category: dict) -> ValidationResult:
        """Validazione di una categoria del budget."""
        required_fields = ["id", "name", "percentage"]
        for field in required_fields:
            if field not in category:
                return ValidationResult(False, f"Manca il campo obbligatorio: {field}")

        result = Validator.validate_percentage(category["percentage"])
        if not result:
            return result

        if not category["name"] or not category["name"].strip():
            return ValidationResult(
                False, "Il nome della categoria non può essere vuoto"
            )

        return ValidationResult(True)

    @staticmethod
    def validate_expense(expense: dict) -> ValidationResult:
        """Validazione di una spesa."""
        required_fields = ["id", "category_id", "description", "amount", "date"]
        for field in required_fields:
            if field not in expense:
                return ValidationResult(False, f"Manca il campo obbligatorio: {field}")

        # Validazione importo
        result = Validator.validate_salary(expense["amount"])
        if not result:
            return ValidationResult(
                False, "L'importo della spesa deve essere un numero positivo"
            )

        # Validazione data (formato YYYY-MM-DD)
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(date_pattern, expense["date"]):
            return ValidationResult(False, "La data deve essere nel formato YYYY-MM-DD")

        # Validazione descrizione
        if not expense["description"] or not expense["description"].strip():
            return ValidationResult(False, "La descrizione non può essere vuota")

        return ValidationResult(True)

    @staticmethod
    def validate_period_data(start_date: str, end_date: str) -> ValidationResult:
        """Validazione date periodo."""
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        for date_str, name in [(start_date, "data inizio"), (end_date, "data fine")]:
            if not re.match(date_pattern, date_str):
                return ValidationResult(
                    False, f"La {name} deve essere nel formato YYYY-MM-DD"
                )
        return ValidationResult(True)
