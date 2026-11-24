"""Small JSON helpers used by the evaluator."""

import json
from pathlib import Path
from typing import Any


def load_json_file(file_path: str | Path) -> Any:
    """Load JSON data from a UTF-8 file."""
    path = Path(file_path)
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in '{path}' at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc


def save_json_file(data: Any, file_path: str | Path) -> None:
    """Write JSON data, creating parent directories when needed."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.write("\n")
