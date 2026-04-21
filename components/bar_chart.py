"""BarChart — Grafico a barre orizzontali riutilizzabile."""

from PyQt6.QtCharts import (
    QChart, QChartView, QHorizontalBarSeries, QBarSet,
    QBarCategoryAxis, QValueAxis
)
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont


class BarChart(QChartView):
    """Grafico a barre orizzontali per confrontare budget vs speso."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._chart = QChart()
        self._chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self._chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        self._chart.setBackgroundBrush(QColor("#2a2a3c"))
        self._chart.setTitleBrush(QColor("#ffffff"))
        self._chart.setTitleFont(QFont("Arial", 12, QFont.Weight.Bold))
        self._chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        self._chart.layout().setContentsMargins(10, 10, 10, 10)
        self.setChart(self._chart)
        
        self.setRenderHint(self.renderHints())
        self.setStyleSheet("border: none; background: transparent;")

    def set_data(self, periods: list[str], budget_values: list[float],
                 spent_values: list[float]) -> None:
        """Imposta i dati del grafico.
        
        Args:
            periods: Lista di etichette per i periodi (es. ["Gen 2025", "Feb 2025"])
            budget_values: Lista di valori budget per ogni periodo
            spent_values: Lista di valori spesi per ogni periodo
        """
        self._chart.removeAllSeries()
        
        # Rimuovi assi esistenti
        for axis in self._chart.axes():
            self._chart.removeAxis(axis)

        if not periods:
            self._chart.legend().setVisible(False)
            return

        # Crea la serie orizzontale
        series = QHorizontalBarSeries()
        series.setBarWidth(0.6)
        series.setLabelsVisible(True)
        series.setLabelsFormat("@value €")
        series.setLabelsPosition(QHorizontalBarSeries.LabelsPosition.LabelsInsideEnd)

        # Crea un QBarSet per il Budget (tutte le barre budget sono blu)
        budget_set = QBarSet("Budget")
        budget_set.setColor(QColor("#2196F3"))  # Blu
        budget_set.setBorderColor(QColor("#2196F3"))
        for budget in budget_values:
            budget_set.append(budget)
        series.append(budget_set)

        # Crea un solo QBarSet per la spesa con colore dinamico basato sulla % attuale
        # Il colore varia da verde (0% del budget) a rosso (100%+ del budget)
        # Calcola colore in base all'ultimo valore (periodo corrente)
        spent_color = QColor("#4CAF50")  # Default verde
        if budget_values and spent_values:
            last_budget = budget_values[-1]
            last_spent = spent_values[-1]
            if last_budget > 0:
                ratio = min(last_spent / last_budget, 1.0)
            else:
                ratio = 1.0 if last_spent > 0 else 0.0
            hue = int(120 * (1 - ratio))
            spent_color = QColor.fromHsv(hue, 200, 200)

        spent_set = QBarSet("Spesa")
        spent_set.setColor(spent_color)
        spent_set.setBorderColor(spent_color)
        for spent in spent_values:
            spent_set.append(spent)
        series.append(spent_set)

        self._chart.addSeries(series)

        # Asse Y (categorie/periodi) - verticale con etichette
        axis_y = QBarCategoryAxis()
        axis_y.append(periods)
        axis_y.setLabelsFont(QFont("Arial", 11))
        axis_y.setLabelsColor(QColor("#ffffff"))
        axis_y.setGridLineVisible(False)
        self._chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        # Asse X (valori) - orizzontale
        axis_x = QValueAxis()
        axis_x.setLabelFormat("%.0f €")
        axis_x.setLabelsFont(QFont("Arial", 10))
        axis_x.setLabelsColor(QColor("#a0a0b0"))
        axis_x.setGridLineColor(QColor("#3a3a5c"))
        
        # Calcola il range massimo
        max_value = max(max(budget_values) if budget_values else 0,
                       max(spent_values) if spent_values else 0)
        axis_x.setRange(0, max_value * 1.2)  # 20% di margine
        
        self._chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        # Leggenda
        self._chart.legend().setVisible(True)
        self._chart.legend().setFont(QFont("Arial", 10))
        self._chart.legend().setLabelColor(QColor("#a0a0b0"))
        self._chart.legend().setBackgroundVisible(False)

    def set_title(self, title: str) -> None:
        """Imposta il titolo del grafico."""
        self._chart.setTitle(title)

    def clear(self) -> None:
        """Rimuove tutte le serie dal grafico."""
        self._chart.removeAllSeries()
