"""Componente BarChart — Grafico a barre orizzontali riutilizzabile con QtCharts."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

from PyQt6.QtCharts import QChart, QChartView, QHorizontalBarSeries, QBarSet, QBarCategoryAxis, QValueAxis


class BarChart(QChartView):
    """Grafico a barre orizzontali per confrontare budget vs speso.

    Metodi principali:
    - set_data(periods, budget_values, spent_values) → aggiorna le barre
      Ogni dict: {"name": str, "value": float, "color": str}
    - clear() → rimuove tutte le barre
    """

    def __init__(self, parent=None):
        # Crea il chart
        self._chart = QChart()
        self._chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self._chart.setTitle("Budget vs Spesa")
        self._chart.setTheme(QChart.ChartTheme.ChartThemeDark)

        super().__init__(self._chart, parent)

        # Background deve essere DOPO setChart per sovrascrivere il tema
        self._chart.setBackgroundBrush(QColor("#1e2330"))  # bg-surface

        self._series = QHorizontalBarSeries()
        self._series.setBarWidth(0.6)
        self._series.setLabelsVisible(True)
        self._series.setLabelsFormat("@value €")
        self._series.setLabelsPosition(QHorizontalBarSeries.LabelsPosition.LabelsInsideEnd)

        self._chart.addSeries(self._series)

        # Dati correnti per ricalcolo colori
        self._budget_values: list[float] = []
        self._spent_values: list[float] = []

    def set_data(self, periods: list[str], budget_values: list[float],
                 spent_values: list[float]) -> None:
        """Aggiorna il grafico con nuovi dati.

        Args:
            periods: Lista di etichette per i periodi (es. ["Gen 2025", "Feb 2025"])
            budget_values: Lista di valori budget per ogni periodo
            spent_values: Lista di valori spesi per ogni periodo
        """
        self._budget_values = budget_values
        self._spent_values = spent_values

        self._series.clear()

        if not periods:
            self._chart.legend().setVisible(False)
            return

        # Crea un QBarSet per il Budget
        budget_set = QBarSet("Budget")
        budget_set.setColor(QColor("#2196F3"))
        budget_set.setBorderColor(QColor("#2196F3"))
        for budget in budget_values:
            budget_set.append(budget)
        self._series.append(budget_set)

        # Crea un QBarSet per la spesa con colore dinamico
        spent_color = QColor("#4CAF50")
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
        self._series.append(spent_set)

        # Rimuovi assi esistenti
        for axis in self._chart.axes():
            self._chart.removeAxis(axis)

        # Asse Y (categorie/periodi)
        axis_y = QBarCategoryAxis()
        axis_y.append(periods)
        axis_y.setLabelsFont(QFont("Arial", 11))
        axis_y.setLabelsColor(QColor("#ffffff"))
        axis_y.setGridLineVisible(False)
        self._chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        self._series.attachAxis(axis_y)

        # Asse X (valori)
        axis_x = QValueAxis()
        axis_x.setLabelFormat("%.0f")
        axis_x.setLabelsFont(QFont("Arial", 10))
        axis_x.setLabelsColor(QColor("#a0a0b0"))
        axis_x.setGridLineColor(QColor("#3a3a5c"))

        max_value = max(max(budget_values) if budget_values else 0,
                       max(spent_values) if spent_values else 0)
        if max_value <= 0:
            max_value = 100  # Default minimo per evitare assi invisibili
        axis_x.setRange(0, max_value * 1.2)
        
        # Aggiungi label "€" manualmente vicino all'asse
        self._chart.setTitle("Budget vs Spesa (€)")

        self._chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        self._series.attachAxis(axis_x)

        # Leggenda
        self._chart.legend().setVisible(True)
        self._chart.legend().setFont(QFont("Arial", 10))
        self._chart.legend().setLabelColor(QColor("#a0a0b0"))
        self._chart.legend().setBackgroundVisible(False)

    def clear(self) -> None:
        """Rimuove tutte le barre dal grafico."""
        self._series.clear()
        self._budget_values = []
        self._spent_values = []
