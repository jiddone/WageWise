"""CategoryCard — Widget compatto per visualizzare i dati di una singola categoria."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

from components.budget_progress_bar import BudgetProgressBar


class CategoryCard(QFrame):
    """Card che mostra i dati di una singola categoria con barra di progresso."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configura il layout della card."""
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumWidth(280)
        self.setMaximumWidth(400)

        # Layout principale
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Riga 1: Pallino colore + Nome categoria
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        self._color_indicator = QLabel("●")
        self._color_indicator.setFont(QFont("Arial", 14))
        header_layout.addWidget(self._color_indicator)

        self._name_label = QLabel("Categoria")
        self._name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header_layout.addWidget(self._name_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Riga 2: Budget | Speso | Residuo
        stats_layout = QHBoxLayout()

        # Budget
        budget_layout = QVBoxLayout()
        budget_layout.setSpacing(2)
        budget_title = QLabel("Budget")
        budget_title.setProperty("class", "subtitle")
        self._budget_label = QLabel("0.00 €")
        self._budget_label.setFont(QFont("Arial", 11))
        budget_layout.addWidget(budget_title)
        budget_layout.addWidget(self._budget_label)
        stats_layout.addLayout(budget_layout)

        # Speso
        spent_layout = QVBoxLayout()
        spent_layout.setSpacing(2)
        spent_title = QLabel("Speso")
        spent_title.setProperty("class", "subtitle")
        self._spent_label = QLabel("0.00 €")
        self._spent_label.setFont(QFont("Arial", 11))
        spent_layout.addWidget(spent_title)
        spent_layout.addWidget(self._spent_label)
        stats_layout.addLayout(spent_layout)

        # Residuo
        remaining_layout = QVBoxLayout()
        remaining_layout.setSpacing(2)
        remaining_title = QLabel("Residuo")
        remaining_title.setProperty("class", "subtitle")
        self._remaining_label = QLabel("0.00 €")
        self._remaining_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        remaining_layout.addWidget(remaining_title)
        remaining_layout.addWidget(self._remaining_label)
        stats_layout.addLayout(remaining_layout)

        layout.addLayout(stats_layout)

        # Riga 3: Barra di progresso
        self._progress_bar = BudgetProgressBar()
        layout.addWidget(self._progress_bar)

        # Percentuale utilizzata
        self._percentage_label = QLabel("0% utilizzato")
        self._percentage_label.setProperty("class", "subtitle")
        self._percentage_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self._percentage_label)

    def set_data(self, name: str, color: str, budget: float, spent: float) -> None:
        """Aggiorna i dati della card.

        Args:
            name: Nome della categoria
            color: Colore in formato hex (#RRGGBB)
            budget: Budget assegnato in €
            spent: Totale speso in €
        """
        # Aggiorna nome e colore
        self._name_label.setText(name)
        self._color_indicator.setStyleSheet(f"color: {color};")

        # Calcola residuo
        remaining = budget - spent

        # Aggiorna labels
        self._budget_label.setText(f"{budget:.2f} €")
        self._spent_label.setText(f"{spent:.2f} €")
        self._remaining_label.setText(f"{remaining:.2f} €")

        # Colore residuo (rosso se negativo)
        if remaining < 0:
            self._remaining_label.setStyleSheet("color: #F44336;")
        else:
            self._remaining_label.setStyleSheet("color: #4CAF50;")

        # Aggiorna barra di progresso
        percentage = (spent / budget * 100) if budget > 0 else 0
        self._progress_bar.set_value(percentage)

        # Aggiorna label percentuale
        self._percentage_label.setText(f"{percentage:.1f}% utilizzato")

        # Cambia colore percentuale se sforato
        if percentage > 100:
            self._percentage_label.setStyleSheet("color: #F44336; font-size: 11px;")
        elif percentage > 84:
            self._percentage_label.setStyleSheet("color: #FFC107; font-size: 11px;")
        else:
            self._percentage_label.setStyleSheet("color: #888; font-size: 11px;")
