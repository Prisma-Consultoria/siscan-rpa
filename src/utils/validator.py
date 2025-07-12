from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Union, Type

from pydantic import BaseModel, ValidationError


class SchemaValidationError(Exception):
    """Collects validation errors returned by Pydantic."""

    def __init__(self, errors: List[dict]):
        self.errors = errors
        message = "; ".join(
            f"{'.'.join(str(p) for p in err.get('loc', []))}: {err.get('msg')}"
            for err in errors
        )
        super().__init__(message)


class Validator:
    """Utility class for loading JSON files and validating data."""

    @classmethod
    def load_json(cls, schema_path: Union[str, Path]) -> Dict[str, Any]:
        path = Path(schema_path)
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def validate_data(cls, data: Dict[str, Any], model: Type[BaseModel]) -> BaseModel:
        try:
            return model.model_validate(data)
        except ValidationError as exc:  # pragma: no cover - raised during tests
            raise SchemaValidationError(exc.errors()) from exc
