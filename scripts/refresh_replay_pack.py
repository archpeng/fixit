#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fixit_ai.common import read_yaml
from fixit_ai.replay_pack import refresh_replay_pack


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(REPO_ROOT / "configs/replay-pack.yaml"))
    parser.add_argument("--generated-at", default=None)
    args = parser.parse_args()

    manifest = refresh_replay_pack(read_yaml(args.config), REPO_ROOT, generated_at=args.generated_at)
    print(
        f"replay pack refreshed datasets={len(manifest['datasets'])} derived={len(manifest['derived_artifacts'])} -> {read_yaml(args.config)['manifest_output']}"
    )


if __name__ == "__main__":
    main()
