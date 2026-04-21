"""LineChart — Grafico a linee riutilizzabile."""

from PyQt6.QtCharts import (
    QChart, QChartView, QLineSeries, QValueAxis, QCategoryAxis
)
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPen


class LineChart(QChartView):
    """Grafico a linee per visualizzare trend nel tempo."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._chart = QChart()
        self._chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self._chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        self._chart.setBackgroundBrush(QColor("#2a2a3c"))
        self._chart.setTitleBrush(QColor("#ffffff"))
        self._chart.setTitleFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.setChart(self._chart)
        
        # Rimuovi il bordo grigio
        self.setStyleSheet("border: none; background: transparent;")
        
        # Serie memorizzate
        self._series: dict[str, QLineSeries] = {}
        self._categories: list[str] = []

    def set_categories(self, categories: list[str]) -> None:
        """Imposta le categorie per l'asse X.
        
        Args:
            categories: Lista di etichette per l'asse X
        """
        self._categories = categories

    def add_series(self, name: str, data: list[tuple[str, float]], color: str) -> None:
        """Aggiunge una serie al grafico.
        
        Args:
            name: Nome della serie (legenda)
            data: Lista di tuple (categoria, valore)
            color: Colore della linea in formato hex
        """
        # Rimuovi serie esistente con lo stesso nome
        if name in self._series:
            self._chart.removeSeries(self._series[name])
            del self._series[name]

        # Crea nuova serie
        series = QLineSeries()
        series.setName(name)
        
        # Configura penna
        pen = QPen(QColor(color))
        pen.setWidth(3)
        series.setPen(pen)

        # Aggiungi punti
        for i, (category, value) in enumerate(data):
            series.append(i, value)

        self._series[name] = series
        self._chart.addSeries(series)

        # Aggiorna assi
        self._update_axes()

    def remove_series(self, name: str) -> None:
        """Rimuove una serie dal grafico."""
        if name in self._series:
            self._chart.removeSeries(self._series[name])
            del self._series[name]
            self._update_axes()

    def clear(self) -> None:
        """Rimuove tutte le serie dal grafico."""
        for series in self._series.values():
            self._chart.removeSeries(series)
        self._series.clear()

    def _update_axes(self) -> None:
        """Aggiorna gli assi del grafico."""
        # Rimuovi assi esistenti
        for axis in self._chart.axes():
            self._chart.removeAxis(axis)

        if not self._series:
            return

        # Asse X (categorie)
        axis_x = QCategoryAxis()
        axis_x.setLabelsPosition(QCategoryAxis.AxisLabelsPosition.AxisLabelsPositionOnValue)
        axis_x.setLabelsFont(QFont("Arial", 10))
        axis_x.setLabelsColor(QColor("#a0a0b0"))
        axis_x.setGridLineColor(QColor("#3a3a5c"))
        
        for i, category in enumerate(self._categories):
            axis_x.append(category, i)
        
        # Range asse X
        if self._categories:
            axis_x.setRange(0, len(self._categories) - 1)
        
        self._chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)

        # Asse Y (valori)
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%.0f €")
        axis_y.setLabelsFont(QFont("Arial", 10))
        axis_y.setLabelsColor(QColor("#a0a0b0"))
        axis_y.setGridLineColor(QColor("#3a3a5c"))

        # Calcola range
        all_values = []
        for series in self._series.values():
            for i in range(series.count()):
                all_values.append(series.at(i).y())
        
        if all_values:
            min_val = min(all_values)
            max_val = max(all_values)
            margin = (max_val - min_val) * 0.1 if max_val != min_val else max_val * 0.1
            axis_y.setRange(max(0, min_val - margin), max_val + margin)
        
        self._chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

        # Attacca le serie agli assi
        for series in self._series.values():
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)

        # Legenda
        if len(self._series) > 0:
            self._chart.legend().setVisible(True)
            self._chart.legend().setFont(QFont("Arial", 10))
            self._chart.legend().setLabelColor(QColor("#a0a0b0"))
        else:
            self._chart.legend().setVisible(False)
