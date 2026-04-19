"""Logica di calcolo dei periodi stipendiali.

Il cuore dell'applicazione è il concetto di periodo stipendiale:
l'intervallo tra un accredito dello stipendio e il giorno prima dell'accredito successivo.
"""

import calendar
from datetime import date, timedelta


def clamp_day_to_month(day: int, year: int, month: int) -> int:
    """Restituisce il giorno effettivo, limitato all'ultimo giorno del mese.

    Esempio: clamp_day_to_month(31, 2025, 2) → 28
    """
    last_day = calendar.monthrange(year, month)[1]
    return min(day, last_day)


def get_current_period(salary_day: int) -> tuple[date, date]:
    """Calcola il periodo stipendiale corrente basandosi sulla data odierna.

    Restituisce (data_inizio, data_fine) dove:
    - data_inizio = ultimo salary_day passato (o oggi se oggi è il salary_day)
    - data_fine = giorno prima del prossimo salary_day

    Gestisce automaticamente i mesi con meno giorni del salary_day.
    """
    today = date.today()
    return get_period_for_date(today, salary_day)


def get_period_for_date(target_date: date, salary_day: int) -> tuple[date, date]:
    """Dato un giorno qualsiasi, restituisce il periodo stipendiale in cui cade.

    Utile per determinare a quale periodo appartiene una spesa o per
    navigare nello storico.
    """
    year = target_date.year
    month = target_date.month

    # Calcola il giorno effettivo di accredito per questo mese
    actual_salary_day = clamp_day_to_month(salary_day, year, month)
    current_period_start = date(year, month, actual_salary_day)

    if target_date >= current_period_start:
        # Siamo nel periodo che inizia oggi
        period_start = current_period_start
    else:
        # Siamo nel periodo precedente
        # Calcola il mese precedente
        if month == 1:
            prev_year = year - 1
            prev_month = 12
        else:
            prev_year = year
            prev_month = month - 1
        prev_salary_day = clamp_day_to_month(salary_day, prev_year, prev_month)
        period_start = date(prev_year, prev_month, prev_salary_day)

    # Calcola la fine del periodo (giorno prima del prossimo salary_day)
    if period_start.month == 12:
        next_year = period_start.year + 1
        next_month = 1
    else:
        next_year = period_start.year
        next_month = period_start.month + 1

    next_salary_day = clamp_day_to_month(salary_day, next_year, next_month)
    period_end = date(next_year, next_month, next_salary_day) - timedelta(days=1)

    return (period_start, period_end)


def get_all_periods(salaries: list[dict], salary_day: int) -> list[dict]:
    """Costruisce la lista ordinata di tutti i periodi storici.

    Per ogni stipendio registrato, calcola le date di inizio e fine periodo.
    Restituisce una lista di dict con: salary_id, start_date, end_date, amount.
    Ordinata cronologicamente dal più vecchio al più recente.
    """
    periods = []
    for salary in salaries:
        try:
            sal_date = date.fromisoformat(salary["date"])
            period_start, period_end = get_period_for_date(sal_date, salary_day)
            periods.append({
                "salary_id": salary["id"],
                "start_date": period_start,
                "end_date": period_end,
                "amount": salary["amount"],
                "date": sal_date,
            })
        except (ValueError, KeyError):
            continue

    periods.sort(key=lambda p: p["date"])
    return periods


def format_period_label(start_date: date, end_date: date) -> str:
    """Formatta un periodo come stringa leggibile.

    Esempio: "27/01/2025 — 26/02/2025"
    """
    return f"{start_date.strftime('%d/%m/%Y')} — {end_date.strftime('%d/%m/%Y')}"
