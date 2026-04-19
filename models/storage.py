"""Layer I/O generico per lettura e scrittura di file JSON."""

import json
from pathlib import Path
from typing import Any


class CorruptedFileError(Exception):
    """Sollevata quando un file JSON esiste ma è malformato o non decodificabile."""
    pass


class Storage:
    """Layer di persistenza JSON con gestione errori robusta."""

    def __init__(self, data_path: Path):
        self._data_path = data_path
        self._data_path.mkdir(parents=True, exist_ok=True)

    @property
    def data_path(self) -> Path:
        return self._data_path

    def read_json(self, filename: str, default: Any = None) -> Any:
        """Legge un file JSON. Se il file non esiste, lo crea con il default."""
        if default is None:
            default = {}

        filepath = self._data_path / filename

        if not filepath.exists():
            self.write_json(filename, default)
            return default

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError as e:
            raise CorruptedFileError(
                f"Il file '{filename}' è corrotto o malformato: {e}"
            ) from e
        except Exception as e:
            raise CorruptedFileError(
                f"Errore nella lettura del file '{filename}': {e}"
            ) from e

    def write_json(self, filename: str, data: Any) -> None:
        """Scrive dati su un file JSON con scrittura atomica."""
        filepath = self._data_path / filename
        temp_path = filepath.with_suffix('.tmp')

        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            temp_path.replace(filepath)
        except Exception:
            if temp_path.exists():
                temp_path.unlink()
            raise

    def file_exists(self, filename: str) -> bool:
        return (self._data_path / filename).exists()
