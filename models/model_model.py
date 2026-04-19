"""Model per la gestione dei modelli di distribuzione (model.json)."""

import uuid
import copy
from models.storage import Storage, CorruptedFileError


DEFAULT_MODELS = {
    "models": [
        {
            "id": "model_builtin_50_30_20",
            "name": "50/30/20",
            "is_builtin": True,
            "categories": [
                {"id": "cat_001", "name": "Bisogni essenziali", "percentage": 50, "color": "#4CAF50"},
                {"id": "cat_002", "name": "Desideri", "percentage": 30, "color": "#2196F3"},
                {"id": "cat_003", "name": "Risparmio", "percentage": 20, "color": "#FF9800"},
            ],
        },
        {
            "id": "model_builtin_70_20_10",
            "name": "70/20/10",
            "is_builtin": True,
            "categories": [
                {"id": "cat_004", "name": "Spese vive", "percentage": 70, "color": "#4CAF50"},
                {"id": "cat_005", "name": "Risparmio", "percentage": 20, "color": "#FF9800"},
                {"id": "cat_006", "name": "Investimenti/Donazioni", "percentage": 10, "color": "#9C27B0"},
            ],
        },
        {
            "id": "model_builtin_6conti",
            "name": "Regola dei 6 conti (T. Harv Eker)",
            "is_builtin": True,
            "categories": [
                {"id": "cat_007", "name": "Necessità (NEC)", "percentage": 55, "color": "#4CAF50"},
                {"id": "cat_008", "name": "Risparmio lungo termine (LTSS)", "percentage": 10, "color": "#FF9800"},
                {"id": "cat_009", "name": "Formazione (EDU)", "percentage": 10, "color": "#2196F3"},
                {"id": "cat_010", "name": "Svago (PLAY)", "percentage": 10, "color": "#E91E63"},
                {"id": "cat_011", "name": "Investimenti (FFA)", "percentage": 10, "color": "#9C27B0"},
                {"id": "cat_012", "name": "Donazioni (GIVE)", "percentage": 5, "color": "#607D8B"},
            ],
        },
    ]
}


class ModelModel:
    """CRUD per il file model.json (modelli di distribuzione)."""

    FILENAME = "model.json"

    def __init__(self, storage: Storage):
        self._storage = storage
        self._data: dict = {}
        self._load()

    def _load(self) -> None:
        try:
            self._data = self._storage.read_json(
                self.FILENAME, default=copy.deepcopy(DEFAULT_MODELS)
            )
        except CorruptedFileError:
            self._data = copy.deepcopy(DEFAULT_MODELS)
            self._save()

        builtin_ids = {m["id"] for m in DEFAULT_MODELS["models"]}
        existing_ids = {m["id"] for m in self._data.get("models", [])}
        for builtin in DEFAULT_MODELS["models"]:
            if builtin["id"] not in existing_ids:
                self._data["models"].append(builtin)
                self._save()

    def _save(self) -> None:
        self._storage.write_json(self.FILENAME, self._data)

    def get_all_models(self) -> list[dict]:
        return list(self._data.get("models", []))

    def get_model_by_id(self, model_id: str) -> dict | None:
        for model in self._data.get("models", []):
            if model["id"] == model_id:
                return dict(model)
        return None

    def get_builtin_models(self) -> list[dict]:
        return [m for m in self._data.get("models", []) if m.get("is_builtin", False)]

    def get_custom_models(self) -> list[dict]:
        return [m for m in self._data.get("models", []) if not m.get("is_builtin", False)]

    def get_categories_for_model(self, model_id: str) -> list[dict]:
        model = self.get_model_by_id(model_id)
        if model is None:
            return []
        return list(model.get("categories", []))

    def get_model_names(self) -> list[tuple[str, str]]:
        return [(m["id"], m["name"]) for m in self._data.get("models", [])]

    def create_model(self, name: str, categories: list[dict]) -> dict:
        self._validate_categories(categories)

        model_id = f"model_{uuid.uuid4().hex[:8]}"
        cats = []
        for cat in categories:
            cats.append({
                "id": f"cat_{uuid.uuid4().hex[:8]}",
                "name": cat["name"].strip(),
                "percentage": cat["percentage"],
                "color": cat.get("color", "#6c63ff"),
            })

        new_model = {
            "id": model_id,
            "name": name.strip(),
            "is_builtin": False,
            "categories": cats,
        }

        self._data["models"].append(new_model)
        self._save()
        return dict(new_model)

    def create_custom_model(self, name: str, categories: list[dict]) -> str:
        """Crea un modello custom e restituisce il suo ID.

        Args:
            name: Nome del modello
            categories: Lista di dict con 'name', 'percentage', 'color'

        Returns:
            str: ID del modello creato
        """
        return self.create_model(name, categories)

    def update_model(self, model_id: str, name: str | None = None,
                     categories: list[dict] | None = None) -> dict:
        model = self._find_model(model_id)
        if model is None:
            raise KeyError(f"Modello '{model_id}' non trovato")
        if model.get("is_builtin", False):
            raise ValueError("I modelli builtin non possono essere modificati")

        if name is not None:
            model["name"] = name.strip()

        if categories is not None:
            self._validate_categories(categories)
            updated_cats = []
            for cat in categories:
                cat_id = cat.get("id", f"cat_{uuid.uuid4().hex[:8]}")
                updated_cats.append({
                    "id": cat_id,
                    "name": cat["name"].strip(),
                    "percentage": cat["percentage"],
                    "color": cat.get("color", "#6c63ff"),
                })
            model["categories"] = updated_cats

        self._save()
        return dict(model)

    def delete_model(self, model_id: str, active_model_id: str | None = None) -> None:
        model = self._find_model(model_id)
        if model is None:
            raise KeyError(f"Modello '{model_id}' non trovato")
        if model.get("is_builtin", False):
            raise ValueError("I modelli builtin non possono essere eliminati")
        if active_model_id and model_id == active_model_id:
            raise ValueError("Non puoi eliminare il modello attualmente in uso")

        self._data["models"] = [m for m in self._data["models"] if m["id"] != model_id]
        self._save()

    def _find_model(self, model_id: str) -> dict | None:
        for model in self._data.get("models", []):
            if model["id"] == model_id:
                return model
        return None

    def _validate_categories(self, categories: list[dict]) -> None:
        if not categories:
            raise ValueError("Un modello deve avere almeno una categoria")

        for cat in categories:
            if not cat.get("name", "").strip():
                raise ValueError("Ogni categoria deve avere un nome non vuoto")

        names = [c["name"].strip().lower() for c in categories]
        if len(names) != len(set(names)):
            raise ValueError("I nomi delle categorie devono essere univoci")

        total_pct = sum(c.get("percentage", 0) for c in categories)
        if total_pct != 100:
            raise ValueError(
                f"La somma delle percentuali deve essere 100, attualmente è {total_pct}"
            )

        for cat in categories:
            pct = cat.get("percentage", 0)
            if pct <= 0 or pct > 100:
                raise ValueError(
                    f"La percentuale di '{cat['name']}' deve essere tra 1 e 100"
                )
