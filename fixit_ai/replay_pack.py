from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fixit_ai.common import ensure_parent, read_jsonl, write_json


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _iso_mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def _combine_jsonl(source_paths: list[Path], output_path: Path) -> int:
    records: list[str] = []
    for path in source_paths:
        records.extend(line for line in path.read_text().splitlines() if line.strip())
    ensure_parent(output_path)
    output_path.write_text("\n".join(records) + ("\n" if records else ""))
    return len(records)


def refresh_replay_pack(config: dict[str, Any], repo_root: Path | str, generated_at: str | None = None) -> dict:
    root = Path(repo_root)
    generated_at = generated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    manifest = {
        "generated_at": generated_at,
        "policy": dict(config.get("policy", {})),
        "datasets": [],
        "derived_artifacts": [],
    }

    for dataset in config.get("datasets", []):
        output_path = root / dataset["output"]
        source_entries = []
        source_paths: list[Path] = []
        for source in dataset.get("sources", []):
            path = root / source["path"]
            if not path.exists():
                raise FileNotFoundError(f"replay source missing: {path}")
            row_count = len(read_jsonl(path)) if path.suffix == ".jsonl" else 1
            source_entries.append(
                {
                    "path": source["path"],
                    "class": source["class"],
                    "row_count": row_count,
                    "sha256": _sha256(path),
                    "freshness": _iso_mtime(path),
                }
            )
            source_paths.append(path)
        output_row_count = _combine_jsonl(source_paths, output_path)
        manifest["datasets"].append(
            {
                "name": dataset["name"],
                "output": dataset["output"],
                "output_row_count": output_row_count,
                "output_sha256": _sha256(output_path),
                "sources": source_entries,
            }
        )

    for artifact in config.get("derived_artifacts", []):
        path = root / artifact["path"]
        exists = path.exists()
        manifest["derived_artifacts"].append(
            {
                "path": artifact["path"],
                "class": artifact["class"],
                "exists": exists,
                "sha256": _sha256(path) if exists else None,
                "freshness": _iso_mtime(path) if exists else None,
            }
        )

    write_json(root / config["manifest_output"], manifest)
    return manifest
