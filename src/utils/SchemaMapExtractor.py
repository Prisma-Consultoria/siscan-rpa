from pathlib import Path

from typing import Tuple, Dict, List, Optional, Union, Type

from pydantic import BaseModel
from src.utils.validator import Validator


class SchemaMapExtractor:
    @staticmethod
    def schema_to_maps(
        schema: Union[str, Path, Type[BaseModel]],
        fields: Optional[List[str]] = None,
    ) -> Tuple[Dict[str, tuple], Dict[str, dict]]:
        """
        Dado um JSON Schema, retorna duas tuplas:
          - MAP_DATA_LABEL: dicionário no formato esperado, restrito aos
            campos informados (se fornecidos)
          - FIELDS_MAP: dicionário para campos do tipo enum, array[enum], etc.
        """
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
            map_data_label[field] = (label, input_type, requirement)
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
    def _infer_requirement_level(field: str, required_fields: List[str]) -> str:
        if field in required_fields:
            return "required"
        return "optional"

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
