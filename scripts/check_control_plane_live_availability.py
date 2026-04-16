#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fixit_ai.common import read_yaml, write_json


def _health_check(url: str) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            return response.status == 200, response.read().decode("utf-8", errors="replace")
    except Exception as exc:  # pragma: no cover - network branch
        return False, str(exc)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--health-url", default="http://127.0.0.1:3401/health")
    parser.add_argument("--snapshot", default=str(REPO_ROOT / "data/live/control_plane_service_context.jsonl"))
    parser.add_argument("--services", default=str(REPO_ROOT / "configs/services.yaml"))
    parser.add_argument("--output", default=str(REPO_ROOT / "data/eval/control-plane-live-readback.json"))
    args = parser.parse_args()

    services = read_yaml(args.services)
    service = services["pilot_family"]["service"]
    health_ok, health_body = _health_check(args.health_url)
    snapshot_path = Path(args.snapshot)
    snapshot_available = snapshot_path.exists()
    service_entry_found = False
    if snapshot_available:
        for line in snapshot_path.read_text().splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("service") == service:
                service_entry_found = True
                break

    payload = {
        "health_url": args.health_url,
        "health_ok": health_ok,
        "health_body": health_body,
        "snapshot_path": str(snapshot_path.relative_to(REPO_ROOT)) if snapshot_path.is_absolute() else str(snapshot_path),
        "snapshot_available": snapshot_available,
        "service": service,
        "service_entry_found": service_entry_found,
        "fallback_expected": not service_entry_found,
    }
    write_json(args.output, payload)
    print(f"control-plane live readback -> {args.output}")


if __name__ == "__main__":
    main()
