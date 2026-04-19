"""Componente PieChart — Grafico a torta riutilizzabile con QtCharts."""

from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice


class PieChart(QChartView):
    """Grafico a torta riutilizzabile per la distribuzione del budget.

    Metodi principali:
    - set_data(categories: list[dict]) → aggiorna le slice
      Ogni dict: {"name": str, "value": float, "color": str}
    - clear() → rimuove tutte le slice
    """

    def __init__(self, parent=None):
        # Crea il chart
        self._chart = QChart()
        self._chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self._chart.setTitle("Distribuzione Budget")
        self._chart.setTheme(QChart.ChartTheme.ChartThemeDark)

        super().__init__(self._chart, parent)

        self._series = QPieSeries()
        self._series.setHoleSize(0.35)  # Stile donut
        self._series.setPieSize(0.8)

        self._chart.addSeries(self._series)

        # Configura il tooltip
        self._series.hovered.connect(self._on_slice_hovered)

        # Dati correnti
        self._data: list[dict] = []

    def set_data(self, categories: list[dict]) -> None:
        """Aggiorna il grafico con nuovi dati.

        Args:
            categories: Lista di dict con 'name', 'value' (importo), 'color'
        """
        self._data = categories
        self._series.clear()

        total = sum(cat.get("value", 0) for cat in categories)
        if total == 0:
            return

        for cat in categories:
            name = cat.get("name", "Senza nome")
            value = cat.get("value", 0)
            color = cat.get("color", "#6c63ff")

            if value > 0:
                slice_item = self._series.append(name, value)
                slice_item.setBrush(QColor(color))
                slice_item.setLabelVisible(True)
                slice_item.setLabelPosition(QPieSlice.LabelPosition.LabelOutside)

                # Calcola la percentuale
                percentage = (value / total) * 100
                slice_item.setLabel(f"{name}\n{percentage:.1f}%")

    def clear(self) -> None:
        """Rimuove tutte le slice dal grafico."""
        self._series.clear()
        self._data = []

    def _on_slice_hovered(self, slice_item: QPieSlice, state: bool) -> None:
        """Gestisce l'hover su una slice."""
        if state:
            # Esplodi la slice leggermente
            slice_item.setExploded(True)
            slice_item.setExplodeDistanceFactor(0.05)
        else:
            slice_item.setExploded(False)
