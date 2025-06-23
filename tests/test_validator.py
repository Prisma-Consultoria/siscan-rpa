import json
from pathlib import Path

import pytest

from utils.schema import MamografiaRequest
from src.siscan.utils.validator import Validator, SchemaValidationError


def _load_data(json_path: Path) -> dict:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    # The fixture file does not include this field, but the schema requires it.
    data.setdefault("tipo_de_mamografia", "Rastreamento")
    return data


def test_validator_accepts_fake_data(fake_json_file):
    data = _load_data(Path(fake_json_file))
    model = Validator.validate_data(data, MamografiaRequest)
    assert isinstance(model, MamografiaRequest)


def test_validator_missing_required_field(fake_json_file):
    data = _load_data(Path(fake_json_file))
    data.pop("nome", None)
    with pytest.raises(SchemaValidationError):
        Validator.validate_data(data, MamografiaRequest)


def test_validator_invalid_cartao_sus(fake_json_file):
    data = _load_data(Path(fake_json_file))
    data["cartao_sus"] = "12345"  # Invalid length (should be 15)
    with pytest.raises(SchemaValidationError):
        Validator.validate_data(data, MamografiaRequest)
