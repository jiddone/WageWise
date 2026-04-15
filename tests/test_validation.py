"""Test per la validazione."""

import pytest
from services.validator import Validator, ValidationResult


def test_validate_salary_valid():
    """Test validazione stipendio valido."""
    result = Validator.validate_salary(3000.0)
    assert result.is_valid
    assert result.error is None


def test_validate_salary_zero():
    """Test validazione stipendio zero."""
    result = Validator.validate_salary(0)
    assert not result.is_valid
    assert "maggiore di zero" in result.error.lower()


def test_validate_salary_negative():
    """Test validazione stipendio negativo."""
    result = Validator.validate_salary(-100)
    assert not result.is_valid


def test_validate_salary_non_numeric():
    """Test validazione stipendio non numerico."""
    result = Validator.validate_salary("abc")
    assert not result.is_valid


def test_validate_percentage_valid():
    """Test validazione percentuale valida."""
    result = Validator.validate_percentage(50.0)
    assert result.is_valid


def test_validate_percentage_zero():
    """Test validazione percentuale zero."""
    result = Validator.validate_percentage(0)
    assert result.is_valid


def test_validate_percentage_hundred():
    """Test validazione percentuale 100."""
    result = Validator.validate_percentage(100)
    assert result.is_valid


def test_validate_percentage_negative():
    """Test validazione percentuale negativa."""
    result = Validator.validate_percentage(-10)
    assert not result.is_valid


def test_validate_percentage_over_hundred():
    """Test validazione percentuale > 100."""
    result = Validator.validate_percentage(150)
    assert not result.is_valid


def test_validate_category_valid():
    """Test validazione categoria valida."""
    category = {"id": "c1", "name": "Test", "percentage": 50.0}
    result = Validator.validate_category(category)
    assert result.is_valid


def test_validate_category_missing_fields():
    """Test validazione categoria campi mancanti."""
    category = {"id": "c1"}
    result = Validator.validate_category(category)
    assert not result.is_valid


def test_validate_category_invalid_percentage():
    """Test validazione categoria percentuale invalida."""
    category = {"id": "c1", "name": "Test", "percentage": 150.0}
    result = Validator.validate_category(category)
    assert not result.is_valid


def test_validate_category_empty_name():
    """Test validazione categoria nome vuoto."""
    category = {"id": "c1", "name": "", "percentage": 50.0}
    result = Validator.validate_category(category)
    assert not result.is_valid


def test_validate_expense_valid():
    """Test validazione spesa valida."""
    expense = {
        "id": "1",
        "category_id": "c1",
        "description": "Spesa test",
        "amount": 100.0,
        "date": "2026-04-15",
    }
    result = Validator.validate_expense(expense)
    assert result.is_valid


def test_validate_expense_invalid_amount():
    """Test validazione spesa importo non valido."""
    expense = {
        "id": "1",
        "category_id": "c1",
        "description": "Spesa test",
        "amount": -100.0,
        "date": "2026-04-15",
    }
    result = Validator.validate_expense(expense)
    assert not result.is_valid


def test_validate_expense_invalid_date():
    """Test validazione spesa data non valida."""
    expense = {
        "id": "1",
        "category_id": "c1",
        "description": "Spesa test",
        "amount": 100.0,
        "date": "15-04-2026",
    }
    result = Validator.validate_expense(expense)
    assert not result.is_valid


def test_validate_expense_empty_description():
    """Test validazione spesa descrizione vuota."""
    expense = {
        "id": "1",
        "category_id": "c1",
        "description": "",
        "amount": 100.0,
        "date": "2026-04-15",
    }
    result = Validator.validate_expense(expense)
    assert not result.is_valid


def test_validate_period_valid():
    """Test validazione periodo valido."""
    result = Validator.validate_period_data("2026-04-01", "2026-04-30")
    assert result.is_valid


def test_validate_period_invalid_format():
    """Test validazione periodo formato non valido."""
    result = Validator.validate_period_data("01-04-2026", "30-04-2026")
    assert not result.is_valid


def test_validate_period_empty():
    """Test validazione periodo date vuote."""
    result = Validator.validate_period_data("", "")
    assert not result.is_valid
