from pathlib import Path
from pydantic import BaseModel
from typing import Tuple, Dict, List, Optional, Union, Type

from src.utils.validator import Validator


class SchemaMapExtractor:
    @classmethod
    def schema_to_maps(
        cls,
        schema: Union[str, Path, Type[BaseModel]],
        fields: Optional[List[str]] = None,
    ) -> Tuple[Dict[str, dict], Dict[str, dict]]:
        map_data_label = {}
        fields_map = {}

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

        for field, field_schema in properties.items():
            label = field_schema.get("title", field.replace("_", " ").capitalize())
            input_type = SchemaMapExtractor._infer_input_type(field_schema)
            requirement = SchemaMapExtractor._infer_requirement_level(
                field, required_fields
            )
            x_xpath = SchemaMapExtractor._infer_input_xpath(field_schema)
            map_data_label[field] = SchemaMapExtractor.make_field_dict(
                label, input_type, requirement, x_xpath
            )
            fm = SchemaMapExtractor._extract_fields_map(field_schema)
            if fm:
                fields_map[field] = fm
        return map_data_label, fields_map

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
    def _extract_fields_map(field_schema: dict) -> dict:
        if (
            field_schema.get("type") == "array"
            and "items" in field_schema
            and "enum" in field_schema["items"]
        ):
            return {v: v for v in field_schema["items"]["enum"] if v is not None}
        elif "enum" in field_schema:
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