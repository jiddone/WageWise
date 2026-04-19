"""Validazioni input per l'applicazione WageWise."""

from datetime import date


def validate_amount(value: str) -> tuple[bool, float | None, str]:
    """Valida un importo inserito come stringa.

    Ritorna (is_valid, parsed_value, error_message)
    """
    if not value or not value.strip():
        return False, None, "L'importo è obbligatorio"

    try:
        # Gestisce sia punto che virgola come separatore decimale
        cleaned = value.strip().replace(',', '.')
        amount = float(cleaned)
    except ValueError:
        return False, None, "Inserisci un numero valido"

    if amount <= 0:
        return False, None, "L'importo deve essere maggiore di zero"

    # Arrotonda a 2 decimali
    return True, round(amount, 2), ""


def validate_percentage(value: int) -> tuple[bool, str]:
    """Valida una singola percentuale (0-100).

    Ritorna (is_valid, error_message)
    """
    if value < 0:
        return False, "La percentuale non può essere negativa"
    if value > 100:
        return False, "La percentuale non può superare 100"
    if value == 0:
        return False, "La percentuale deve essere maggiore di zero"
    return True, ""


def validate_model_categories(categories: list[dict]) -> tuple[bool, list[str]]:
    """Valida l'intero set di categorie di un modello.

    Controlla: nomi non vuoti, nomi univoci, somma percentuali = 100.
    Ritorna (is_valid, list_of_error_messages)
    """
    errors = []

    if not categories:
        errors.append("Un modello deve avere almeno una categoria")
        return False, errors

    # Controlla nomi vuoti
    for i, cat in enumerate(categories):
        name = cat.get("name", "").strip()
        if not name:
            errors.append(f"La categoria {i+1} deve avere un nome")

    # Controlla nomi duplicati
    names = [c.get("name", "").strip().lower() for c in categories if c.get("name", "").strip()]
    if len(names) != len(set(names)):
        errors.append("I nomi delle categorie devono essere univoci")

    # Controlla somma percentuali
    total_pct = sum(c.get("percentage", 0) for c in categories)
    if total_pct != 100:
        if total_pct < 100:
            errors.append(f"Mancano {100 - total_pct}% per arrivare a 100")
        else:
            errors.append(f"Eccesso di {total_pct - 100}% (deve essere esattamente 100)")

    # Controlla range percentuali
    for cat in categories:
        pct = cat.get("percentage", 0)
        if pct <= 0:
            errors.append(f"La percentuale di '{cat.get('name', 'categoria')}' deve essere maggiore di zero")
        elif pct > 100:
            errors.append(f"La percentuale di '{cat.get('name', 'categoria')}' non può superare 100")

    return len(errors) == 0, errors


def validate_date_in_period(check_date: date, period_start: date, period_end: date) -> bool:
    """Verifica che una data cada nel periodo specificato."""
    return period_start <= check_date <= period_end


def validate_json_structure(data: dict, schema: str) -> tuple[bool, list[str]]:
    """Valida la struttura di un dict letto da JSON rispetto a uno schema atteso.

    schema può essere: 'settings', 'models', 'salaries', 'expenses'.
    Ritorna (is_valid, list_of_issues)
    """
    issues = []

    if schema == 'settings':
        required = ['salary_day', 'active_model_id', 'currency', 'theme']
        for key in required:
            if key not in data:
                issues.append(f"Campo mancante: {key}")

    elif schema == 'models':
        if 'models' not in data:
            issues.append("Campo mancante: models")
        elif not isinstance(data['models'], list):
            issues.append("'models' deve essere una lista")

    elif schema == 'salaries':
        if 'salaries' not in data:
            issues.append("Campo mancante: salaries")
        elif not isinstance(data['salaries'], list):
            issues.append("'salaries' deve essere una lista")

    elif schema == 'expenses':
        if 'expenses' not in data:
            issues.append("Campo mancante: expenses")
        elif not isinstance(data['expenses'], list):
            issues.append("'expenses' deve essere una lista")

    return len(issues) == 0, issues
