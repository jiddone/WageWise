"""WageWise - Layer I/O generico per lettura/scrittura file JSON."""

import json
from pathlib import Path
from typing import Any


class CorruptedFileError(Exception):
    """Sollevata quando un file JSON è malformato e non può essere parseato."""
    pass


def read_json(path: Path, default: Any = None) -> Any:
    """Legge un file JSON. Se il file non esiste, lo crea con il default e lo restituisce.
    Se il file esiste ma è malformato, solleva CorruptedFileError.

    Args:
        path: Percorso del file JSON.
        default: Contenuto di default se il file non esiste. Se None, usa {}.

    Returns:
        Il contenuto parseato del file JSON.
    """
    if default is None:
        default = {}

    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        write_json(path, default)
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise CorruptedFileError(f"File JSON corrotto: {path} — {e}") from e


def write_json(path: Path, data: Any) -> None:
    """Scrive dati su un file JSON con formattazione leggibile.

    Args:
        path: Percorso del file JSON.
        data: Dati da serializzare.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
