from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


class SchemaBundle:
    def __init__(self, schema_root: Path | str):
        self.schema_root = Path(schema_root)
        self._validators: dict[str, Draft202012Validator] = {}

    def validator(self, schema_name: str) -> Draft202012Validator:
        if schema_name not in self._validators:
            schema = json.loads((self.schema_root / schema_name).read_text())
            self._validators[schema_name] = Draft202012Validator(schema)
        return self._validators[schema_name]

    def validate(self, schema_name: str, payload: dict) -> None:
        validator = self.validator(schema_name)
        errors = sorted(validator.iter_errors(payload), key=lambda err: list(err.path))
        if errors:
            joined = "; ".join(
                f"{'/'.join(map(str, err.path)) or '<root>'}: {err.message}" for err in errors
            )
            raise ValueError(f"schema validation failed for {schema_name}: {joined}")
