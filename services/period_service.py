"""Modello logica periodi — Gestione dei periodi stipendiali."""

from datetime import date, timedelta
from typing import List, Tuple, Optional


class Period:
    """Rappresenta un periodo stipendiale."""

    def __init__(self, start_date: date, end_date: date, salary_day: int = 15):
        self.start_date = start_date
        self.end_date = end_date
        self.salary_day = salary_day

    @classmethod
    def from_dict(cls, data: dict) -> "Period":
        """Crea un periodo da dizionario."""
        return cls(
            start_date=date.fromisoformat(data["start_date"]),
            end_date=date.fromisoformat(data["end_date"]),
            salary_day=data.get("salary_day", 15),
        )

    def to_dict(self) -> dict:
        """Converte il periodo in dizionario."""
        return {
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "salary_day": self.salary_day,
        }

    def contains_date(self, check_date: date) -> bool:
        """Verifica se una data è inclusa nel periodo."""
        return self.start_date <= check_date <= self.end_date

    def overlap(self, other: "Period") -> bool:
        """Verifica se questo periodo si sovrappone a un altro."""
        return not (
            self.end_date < other.start_date or self.start_date > other.end_date
        )


class PeriodCalculator:
    """Calcolatore della logica dei periodi."""

    @staticmethod
    def calculate_periods(
        salary_day: int, start_date: date, num_periods: int = 12
    ) -> List[Period]:
        """Calcola i periodi a partire da una data iniziale."""
        periods = []
        current_start = start_date

        for _ in range(num_periods):
            # Trova il giorno del mese specificato (salary_day)
            month = current_start.month
            year = current_start.year
            month_length = [
                31,
                29 if PeriodCalculator._is_leap(year) else 28,
                31,
                30,
                31,
                30,
                31,
                31,
                30,
                31,
                30,
                31,
            ][month - 1]
            day_to_use = min(salary_day, month_length)
            current_date = date(year, month, day_to_use)

            # Il periodo va dal giorno stipendio al giorno prima del prossimo stipendio
            next_start = PeriodCalculator._add_months(current_start, 1)
            end_date = date(
                next_start.year, next_start.month, next_start.day
            ) - timedelta(days=1)

            periods.append(Period(current_date, end_date, salary_day))
            current_start = next_start

        return periods

    @staticmethod
    def get_current_period(
        periods: List[Period], ref_date: Optional[date] = None
    ) -> Optional[Period]:
        """Recupera il periodo corrente per una data di riferimento."""
        ref_date = ref_date or date.today()
        for period in periods:
            if period.contains_date(ref_date):
                return period
        return None

    @staticmethod
    def _is_leap(year: int) -> bool:
        """Verifica se un anno è bisestile."""
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    @staticmethod
    def _add_months(source_date: date, months: int) -> date:
        """Aggiunge mesi a una data."""
        month = source_date.month - 1 + months
        year = source_date.year + month // 12
        month = month % 12 + 1
        day = min(
            source_date.day,
            [
                31,
                29 if PeriodCalculator._is_leap(year) else 28,
                31,
                30,
                31,
                30,
                31,
                31,
                30,
                31,
                30,
                31,
            ][month - 1],
        )
        return date(year, month, day)


class PeriodService:
    """Servizio per la logica dei periodi."""

    def __init__(self, salary_day: int = 15):
        self.salary_day = salary_day
        self._periods: List[Period] = []

    def initialize_periods(self, start_date: date, num_periods: int = 24) -> None:
        """Inizializza i periodi a partire da una data."""
        self._periods = PeriodCalculator.calculate_periods(
            self.salary_day, start_date, num_periods
        )

    def get_periods(self) -> List[Period]:
        """Restituisce tutti i periodi."""
        return self._periods

    def get_current_period(self, ref_date: Optional[date] = None) -> Optional[Period]:
        """Recupera il periodo corrente."""
        return PeriodCalculator.get_current_period(self._periods, ref_date)

    def get_period_by_dates(self, start_date: date, end_date: date) -> Optional[Period]:
        """Recupera un periodo specifico per date."""
        for period in self._periods:
            if period.start_date == start_date and period.end_date == end_date:
                return period
        return None

    def to_dict(self) -> List[dict]:
        """Converte i periodi in lista di dizionari."""
        return [period.to_dict() for period in self._periods]

    def from_dict(self, data: List[dict]) -> None:
        """Carica i periodi da lista di dizionari."""
        self._periods = [Period.from_dict(item) for item in data]
