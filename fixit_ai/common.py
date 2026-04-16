from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Iterable, List, Any

import yaml


def ensure_parent(path: Path | str) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def read_jsonl(path: Path | str) -> List[dict]:
    target = Path(path)
    if not target.exists():
        return []
    return [json.loads(line) for line in target.read_text().splitlines() if line.strip()]


def write_jsonl(path: Path | str, records: Iterable[dict]) -> None:
    target = ensure_parent(path)
    lines = [json.dumps(record, ensure_ascii=False) for record in records]
    target.write_text("\n".join(lines) + ("\n" if lines else ""))


def read_yaml(path: Path | str) -> Any:
    return yaml.safe_load(Path(path).read_text())


def write_json(path: Path | str, payload: Any) -> None:
    target = ensure_parent(path)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n")


def write_text(path: Path | str, content: str) -> None:
    target = ensure_parent(path)
    target.write_text(content)


def write_pickle(path: Path | str, payload: Any) -> None:
    target = ensure_parent(path)
    with target.open("wb") as handle:
        pickle.dump(payload, handle)


def read_pickle(path: Path | str) -> Any:
    with Path(path).open("rb") as handle:
        return pickle.load(handle)
