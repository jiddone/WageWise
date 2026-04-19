"""Controller Dashboard — Logica Pagina 1."""

from datetime import date
from pathlib import Path

from PyQt6.QtCore import QObject

from views.dashboard_view import DashboardView
from core.app_state import AppState
from core.period import get_current_period, format_period_label
from core.validators import validate_amount, validate_model_categories
from models.storage import Storage
from models.settings_model import SettingsModel
from models.model_model import ModelModel
from models.salary_model import SalaryModel


class DashboardController(QObject):
    """Controller per la pagina Dashboard.

    Gestisce:
    - Caricamento e salvataggio dello stipendio
    - Selezione del modello di distribuzione
    - Aggiornamento della tabella riepilogativa
    """

    def __init__(self, view: DashboardView, data_path: Path, parent=None):
        super().__init__(parent)
        self._view = view
        self._data_path = data_path

        # Inizializza modelli
        self._storage = Storage(data_path)
        self._settings_model = SettingsModel(self._storage)
        self._model_model = ModelModel(self._storage)
        self._salary_model = SalaryModel(self._storage)

        # Ottieni riferimento all'AppState
        self._app_state = AppState.instance()

        # Configura la view
        self._setup_view()

        # Carica i dati iniziali
        self.refresh()

    def _setup_view(self) -> None:
        """Collega i segnali della view ai metodi del controller."""
        self._view.salary_save_requested.connect(self._on_save_salary)
        self._view.model_selected.connect(self._on_model_selected)
        self._view.custom_model_save_requested.connect(self._on_save_custom_model)
        self._view.custom_model_cancel_requested.connect(self._on_cancel_custom_model)

        # Connetti all'AppState per aggiornamenti
        self._app_state.salary_changed.connect(self._on_salary_changed)
        self._app_state.model_changed.connect(self._on_model_changed)

    def refresh(self) -> None:
        """Aggiorna la view con i dati correnti."""
        # Calcola il periodo corrente
        salary_day = self._settings_model.get_salary_day()
        period_start, period_end = get_current_period(salary_day)
        self._app_state.current_period = (period_start, period_end)

        # Aggiorna label periodo
        period_text = f"Periodo: {format_period_label(period_start, period_end)}"
        self._view.set_period_label(period_text)

        # Carica lo stipendio del periodo corrente
        salary = self._salary_model.get_salary_for_period(period_start, period_end)
        if salary:
            self._view.set_salary_input(str(salary["amount"]))
            self._app_state.current_salary = salary["amount"]
        else:
            self._view.set_salary_input("")
            self._app_state.current_salary = 0.0

        # Carica i modelli
        models = self._model_model.get_model_names()
        self._view.set_models(models)

        # Seleziona il modello attivo
        active_model_id = self._settings_model.get_active_model_id()
        self._view.set_selected_model(active_model_id)
        self._app_state.current_model_id = active_model_id

        # Aggiorna la tabella riepilogativa
        self._update_summary()

    def _update_summary(self) -> None:
        """Aggiorna la tabella riepilogativa con il modello e stipendio correnti."""
        model_id = self._view.get_selected_model_id()
        if not model_id:
            return

        categories = self._model_model.get_categories_for_model(model_id)
        salary_text = self._view.get_salary_input()

        try:
            salary = float(salary_text.replace(',', '.')) if salary_text else 0.0
        except ValueError:
            salary = 0.0

        self._view.set_summary_data(categories, salary)

    def _on_save_salary(self, amount_str: str) -> None:
        """Gestisce il salvataggio dello stipendio."""
        is_valid, amount, error = validate_amount(amount_str)
        if not is_valid:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self._view, "Errore", error)
            return

        # Ottieni il periodo corrente
        salary_day = self._settings_model.get_salary_day()
        period_start, period_end = get_current_period(salary_day)

        # Ottieni il modello attivo
        model_id = self._settings_model.get_active_model_id()

        # Salva lo stipendio (sovrascrivi se esiste già per questo periodo)
        date_str = period_start.isoformat()
        salary = self._salary_model.overwrite_salary_for_period(
            amount, date_str, model_id
        )

        # Aggiorna l'AppState
        self._app_state.current_salary = amount

        # Aggiorna la tabella riepilogativa
        self._update_summary()

    def _on_model_selected(self, model_id: str) -> None:
        """Gestisce la selezione di un nuovo modello."""
        # Salva il modello come attivo
        self._settings_model.set_active_model_id(model_id)

        # Aggiorna l'AppState
        self._app_state.current_model_id = model_id

        # Aggiorna la tabella riepilogativa
        self._update_summary()

    def _on_salary_changed(self, amount: float) -> None:
        """Reagisce ai cambiamenti di stipendio dall'AppState."""
        self._update_summary()

    def _on_model_changed(self, model_id: str) -> None:
        """Reagisce ai cambiamenti di modello dall'AppState."""
        self._update_summary()

    def _on_save_custom_model(self, name: str, categories: list) -> None:
        """Gestisce il salvataggio di un modello custom.

        Args:
            name: Nome del modello
            categories: Lista di dict con 'name', 'percentage', 'color'
        """
        # Valida le categorie
        is_valid, errors = validate_model_categories(categories)
        if not is_valid:
            self._view.show_error("\n".join(errors))
            return

        # Crea il modello
        try:
            model_id = self._model_model.create_custom_model(name, categories)

            # Aggiorna la lista modelli nella view
            models = self._model_model.get_model_names()
            self._view.set_models(models)

            # Seleziona il nuovo modello
            self._view.set_selected_model(model_id)
            self._settings_model.set_active_model_id(model_id)
            self._app_state.current_model_id = model_id

            # Nascondi l'editor
            self._view.show_custom_model_editor(False)

            # Aggiorna la tabella riepilogativa
            self._update_summary()

            self._view.show_info(f"Modello '{name}' salvato con successo!")

        except Exception as e:
            self._view.show_error(f"Errore nel salvare il modello: {str(e)}")

    def _on_cancel_custom_model(self) -> None:
        """Gestisce l'annullamento della creazione modello custom."""
        # La view già nasconde l'editor, qui possiamo fare pulizia aggiuntiva se necessario
        pass
