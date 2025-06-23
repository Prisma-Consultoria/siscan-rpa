import json
from pathlib import Path
from typing import Any, Optional, List, Literal, Annotated
from pydantic import BaseModel, Field, create_model


def _parse_field(fs: dict, required: bool):
    t = fs.get("type")
    optional = False
    if isinstance(t, list):
        optional = "null" in t
        t = [x for x in t if x != "null"]
        t = t[0] if t else None
    default = ... if required and not optional else None

    if t == "string":
        typ = str
        if "enum" in fs:
            typ = Literal[tuple(v for v in fs["enum"] if v is not None)]
        kwargs = {}
        if "pattern" in fs:
            kwargs["pattern"] = fs["pattern"]
        return (Optional[typ] if optional else typ, Field(default, **kwargs))
    if t == "array":
        items = fs.get("items", {})
        item_type = str
        if "enum" in items:
            item_type = Literal[tuple(v for v in items["enum"] if v is not None)]
        kwargs = {}
        if "minItems" in fs:
            kwargs["min_length"] = fs["minItems"]
        if "maxItems" in fs:
            kwargs["max_length"] = fs["maxItems"]
        typ = List[item_type]
        return (Optional[typ] if optional else typ, Field(default, **kwargs))

    return (Optional[Any] if optional else Any, Field(default))


def create_model_from_json_schema(name: str, schema_path: Path) -> type[BaseModel]:
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    props = schema.get("properties", {})
    required = schema.get("required", [])
    fields = {}
    for fname, fs in props.items():
        ftype, field = _parse_field(fs, fname in required)
        fields[fname] = (ftype, field)

    model = create_model(name, **fields)
    model.__schema__ = schema
    model.__schema_path__ = str(schema_path)
    return model


# Cria modelo para requisicao mamografia
SCHEMA_DIR = Path(__file__).resolve().parents[1] / "src" / "siscan" / "schemas"
MAMO_SCHEMA_PATH = SCHEMA_DIR / "requisicao_exame_mamografia_rastreamento.schema.json"
MamografiaRequest = create_model_from_json_schema("MamografiaRequest", MAMO_SCHEMA_PATH)

