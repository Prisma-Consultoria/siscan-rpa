import sys
from pathlib import Path
from pydantic import BaseModel
from typing import Tuple, Dict, List, Optional, Union, Type

from src.utils.import_utils import get_class_from_module
from src.utils.validator import Validator


class SchemaMapExtractor:
    @classmethod
    def schema_to_maps(
        cls,
        schema: Union[str, Path, Type[BaseModel]],
        fields: Optional[List[str]] = None,
    ) -> Tuple[Dict[str, dict], Dict[str, dict]]:
        fields_metadata = {}
        field_value_map = {}

        if schema is None:
            return fields_metadata, field_value_map

        if isinstance(schema, (str, Path)):
            schema_dict = Validator.load_json(schema)
        elif isinstance(schema, type) and issubclass(schema, BaseModel):
            schema_dict = getattr(schema, "__schema__", schema.model_json_schema())
        else:
            raise TypeError("schema must be a path or BaseModel class")

        properties = schema_dict.get("properties", {})
        required_fields = schema_dict.get("required", [])

        # Se lista de campos for informada, filtra as propriedades
        if fields is not None:
            properties = {k: v for k, v in properties.items() if k in fields}

        schema_defs = schema_dict.get("$defs", {})
        for field, field_schema in properties.items():
            label = field_schema.get("title", field.replace("_", " ").capitalize())
            input_type = SchemaMapExtractor._infer_input_type(field_schema)
            requirement = SchemaMapExtractor._infer_requirement_level(
                field, required_fields
            )
            x_xpath = SchemaMapExtractor._infer_input_xpath(field_schema)
            fields_metadata[field] = SchemaMapExtractor.make_field_dict(
                label, input_type, requirement, x_xpath
            )
            fm = SchemaMapExtractor._extract_fields_map(field_schema,
                                                        schema_defs)
            if fm:
                field_value_map[field] = fm
        return fields_metadata, field_value_map

    @staticmethod
    def _infer_input_type(field_schema: dict) -> str:
        x_widget = field_schema.get("x-widget")
        if x_widget:
            return x_widget
        if "enum" in field_schema and isinstance(field_schema["enum"], list):
            if field_schema.get("type") == "array":
                return "checkbox"
            if len(field_schema["enum"]) > 0:
                return "radio"
        elif field_schema.get("pattern") == "^\\d{2}/\\d{2}/\\d{4}$":
            return "date"
        elif field_schema.get("pattern") == "^\\d{4}$":
            return "text"
        return "text"

    @staticmethod
    def _infer_input_xpath(field_schema: dict) -> str:
        return field_schema.get("x-xpath", "")

    @staticmethod
    def _infer_requirement_level(
            field: str, required_fields: List[str]) -> bool:
        if field in required_fields:
            return True
        return False

    @staticmethod
    def _extract_fields_map(field_schema: dict,
                            schema_defs: dict = None) -> dict:
        """
        Retorna o mapeamento dos valores possíveis para campos do tipo enum,
        incluindo quando definidos por $ref no schema.
        """
        # Verifica se o campo referencia um enum via $ref
        if "$ref" in field_schema and schema_defs is not None:
            ref_path = field_schema["$ref"]
            if ref_path.startswith("#/$defs/"):
                enum_name = ref_path.replace("#/$defs/", "")
                # Tenta obter a classe do enum a partir do módulo
                enum_cls = get_class_from_module(
                    "src.siscan.schema.types", enum_name)
                if enum_cls and hasattr(enum_cls, "get_external_map"):
                    return enum_cls.get_external_map()

                # fallback: enum tradicional
                enum_def = schema_defs.get(enum_name, {})
                if "enum" in enum_def:
                    return {v: v for v in enum_def["enum"] if v is not None}

        # Arrays de enums definidos via items
        if (
                field_schema.get("type") == "array"
                and "items" in field_schema
                and "enum" in field_schema["items"]
        ):
            return {v: v for v in field_schema["items"]["enum"] if
                    v is not None}
        # Enum direto no campo
        if "enum" in field_schema:
            return {v: v for v in field_schema["enum"] if v is not None}
        return None

    @classmethod
    def make_field_dict(
            cls,
            label: str,
            input_type: str,
            requirement: bool,
            xpath: str | None = "") -> dict:
        return {
            "label": label,
            "input_type": input_type,
            "required": requirement,
            "xpath": xpath
        }