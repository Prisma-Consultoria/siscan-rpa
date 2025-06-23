from __future__ import annotations

import json
import re
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Type

from jsonschema import validate, Draft7Validator
from jsonschema.exceptions import ValidationError, SchemaError
from pydantic import BaseModel

from src.utils import messages as msg

logger = logging.getLogger(__name__)


class SchemaValidationError(ValidationError):
    def __init__(
        self,
        required_missing: Optional[List[str]] = None,
        required_errors: Optional[List[ValidationError]] = None,
        pattern_errors: Optional[List[ValidationError]] = None,
        enum_errors: Optional[List[ValidationError]] = None,
        conditional_failure: Optional[List[Tuple[str, Optional[str], Optional[Union[str, list]]]]] = None,
        conditional_errors: Optional[List[ValidationError]] = None,
        outros_erros: Optional[List[ValidationError]] = None,
        message: Optional[str] = None,
        **kwargs,
    ):
        self.required_missing = required_missing or []
        self.required_errors = required_errors or []
        self.pattern_errors = pattern_errors or []
        self.enum_errors = enum_errors or []
        self.conditional_failure = conditional_failure or []
        self.conditional_errors = conditional_errors or []
        self.outros_erros = outros_erros or []

        if message is None:
            msgs = []
            if self.required_missing:
                msgs.append(
                    "Os seguintes campos obrigatórios estão ausentes: "
                    f"{', '.join(self.required_missing)}"
                )
            if self.pattern_errors:
                for err in self.pattern_errors:
                    msgs.append(
                        msg.E_PATTERN(err.path[-1], err.instance, err.validator_value)
                    )
            if self.enum_errors:
                for err in self.enum_errors:
                    msgs.append(
                        msg.E_ENUM(err.path[-1], err.instance, err.validator_value)
                    )
            if self.conditional_failure:
                for field_required, field_trigger, trigger_value in self.conditional_failure:
                    msgs.append(
                        msg.E_CONDITIONAL(field_required, field_trigger, trigger_value)
                    )
            if self.outros_erros:
                for err in self.outros_erros:
                    if err.validator == "maxItems":
                        value = err.schema["items"]["const"]
                        msgs.append(
                            msg.E_MAX_ITEMS(err.path[-1], value, err.instance)
                        )
                    else:
                        msgs.append(err.message)
            message = "; ".join(msgs)

        super().__init__(message, **kwargs)


class Validator:
    """Classe utilitária para validação de dados com base em JSON Schema.

    JSON Schema Draft-07
    """

    @classmethod
    def load_json(cls, schema_path: Union[str, Path]) -> Dict[str, Any]:
        """Carrega e retorna o JSON Schema do arquivo especificado.

        Parâmetros
        ----------
        schema_path : str | Path
            Caminho para o arquivo JSON Schema.

        Retorno
        -------
        dict
            Dicionário representando o JSON Schema.
        """
        schema_path = Path(schema_path)
        with open(schema_path, encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def _find_trigger_for_conditional_required(
        cls, error: ValidationError, schema: Dict[str, Any]
    ) -> List[Tuple[str, Optional[str], Optional[Union[str, list]]]]:
        """Dada a exceção de required condicional, retorna uma lista de tuplas:
            (nome_campo_tornado_obrigatório,
            nome_campo_disparador,
            valor_esperado).

        Se múltiplos campos tornaram-se obrigatórios pelo mesmo bloco 'if',
        retorna todos.
        """
        results: List[Tuple[str, Optional[str], Optional[Union[str, list]]]] = []
        schema_cursor = schema
        # Navega no schema original até o nível do erro
        for p in list(error.absolute_schema_path)[:-2]:  # Remove 'then', 'required'
            schema_cursor = schema_cursor[p]
        # Ex: {'if': {...}, 'then': {'required': [...]}}
        if_block = schema_cursor.get("if")
        required_fields = []
        if "required" in schema_cursor.get("then", {}):
            required_fields = schema_cursor["then"]["required"]
        elif error.validator_value:
            # fallback: alguns validadores passam o próprio required
            required_fields = error.validator_value
        if if_block and "properties" in if_block:
            properties = if_block["properties"]
            for field, condition in properties.items():
                trigger_field = field
                trigger_value = None
                if "const" in condition:
                    trigger_value = condition["const"]
                elif "enum" in condition:
                    trigger_value = condition["enum"]
                # Relaciona todos os required deste bloco com o mesmo
                # disparador
                for req_field in required_fields:
                    results.append((req_field, trigger_field, trigger_value))
        else:
            # fallback para tentar recuperar algo, embora improvável
            for req_field in required_fields:
                results.append((req_field, None, None))
        return results

    @classmethod
    def validate_data(cls, data: Dict[str, Any], model: Type[BaseModel]) -> BaseModel:
        schema = getattr(model, "__schema__", None)
        if schema is None:
            raise SchemaError("Modelo sem schema associado")

        try:
            validate(instance=data, schema=schema)
        except ValidationError:
            pass
        except SchemaError as se:
            raise se

        validator = Draft7Validator(schema)
        errors = list(validator.iter_errors(data))

        required_missing: List[str] = []
        required_errors: List[ValidationError] = []
        pattern_errors: List[ValidationError] = []
        enum_errors: List[ValidationError] = []
        conditional_failure: set = set()
        conditional_errors: List[ValidationError] = []
        outros_erros: List[ValidationError] = []

        for error in errors:
            if error.validator == "required" and "then" in error.schema_path:
                failures = cls._find_trigger_for_conditional_required(error, schema)
                for failure in failures:
                    conditional_failure.add(tuple(failure))
                conditional_errors.append(error)
            elif error.validator == "required":
                match = re.search(r"'([^']+)'", error.message)
                if match:
                    required_missing.append(match.group(1))
                required_errors.append(error)
            elif error.validator == "pattern":
                pattern_errors.append(error)
            elif error.validator == "enum":
                enum_errors.append(error)
            else:
                outros_erros.append(error)

        if (
            required_missing
            or pattern_errors
            or enum_errors
            or conditional_errors
            or outros_erros
        ):
            raise SchemaValidationError(
                required_missing=required_missing,
                required_errors=required_errors,
                pattern_errors=pattern_errors,
                enum_errors=enum_errors,
                conditional_failure=list(conditional_failure),
                conditional_errors=conditional_errors,
                outros_erros=outros_erros,
            )

        return model.model_validate(data)

