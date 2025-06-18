from typing import Union, Dict, Any, Tuple, Optional, List

import json
import re
from pathlib import Path
import logging
from jsonschema import validate, ValidationError, SchemaError, Draft7Validator
from jsonschema.exceptions import ValidationError, SchemaError

logger = logging.getLogger(__name__)


class SchemaValidationError(ValidationError):
    def __init__(
        self,
        required_missing=None,
        required_errors=None,
        pattern_errors=None,
        enum_errors=None,
        conditional_failure=None,
        conditional_errors=None,
        outros_erros=None,
        message=None,
        **kwargs
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
                        f"Campo '{err.path[-1]}' com valor '{err.instance}' "
                        f"não corresponde ao padrão '{err.validator_value}'"
                    )
            if self.enum_errors:
                for err in self.enum_errors:
                    msgs.append(
                        f"Campo '{err.path[-1]}' com valor '{err.instance}' "
                        f"não está entre os valores permitidos: "
                        f"{err.validator_value}"
                    )
            if self.conditional_failure:
                for field_required, field_trigger, trigger_value \
                        in self.conditional_failure:
                    msgs.append(
                        f"O campo '{field_required}' tornou-se obrigatório "
                        f"porque o campo '{field_trigger}' foi informado com "
                        f"o valor '{trigger_value}'."
                    )
            if self.outros_erros:
                for err in self.outros_erros:
                    if err.validator == "maxItems":
                        value = err.schema["items"]["const"]
                        msgs.append(
                            f"Quando o valor do campo '{err.path[-1]}' for "
                            f"'{value}', apenas ele deve constar na lista. "
                            f"Foir informado '{err.instance}'."
                        )
                    else:
                        msgs.append(err.message)
            message = "; ".join(msgs)

        super().__init__(message, **kwargs)


class SchemaValidator:
    """
    Classe utilitária para validação de dados com base em JSON Schema.
    JSON Schema Draft-07
    """

    @classmethod
    def load_schema(cls, schema_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Carrega e retorna o JSON Schema do arquivo especificado.

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
        """
        Dada a exceção de required condicional, retorna uma lista de tuplas:
            (nome_campo_tornado_obrigatório,
            nome_campo_disparador,
            valor_esperado).

        Se múltiplos campos tornaram-se obrigatórios pelo mesmo bloco 'if',
        retorna todos.
        """
        results: List[
            Tuple[str, Optional[str], Optional[Union[str, list]]]] = []
        # Navega no schema original até o nível do erro
        schema_cursor = schema
        for p in list(error.absolute_schema_path)[
                 :-2]:  # Remove 'then', 'required'
            schema_cursor = schema_cursor[p]

        # Ex: {'if': {...}, 'then': {'required': [...]}}
        if_block = schema_cursor.get("if")
        required_fields = []
        if "required" in schema_cursor.get("then", {}):
            required_fields = schema_cursor["then"]["required"]
        elif error.validator_value:
            # fallback: alguns validadores passam o próprio required
            required_fields = error.validator_value

        # Recupera campo e valor do(s) disparador(es)
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
    def validate_data(cls, data: Dict[str, Any],
                      schema_path: Union[str, Path]) -> bool:
        schema = cls.load_schema(schema_path)

        try:
            validate(instance=data, schema=schema)
        except ValidationError:
            pass
        except SchemaError as se:
            raise se

        validator = Draft7Validator(schema)
        errors = list(validator.iter_errors(data))

        required_missing = []
        required_errors = []
        pattern_errors = []
        enum_errors = []
        conditional_failure = set()
        conditional_errors = []
        outros_erros = []

        for error in errors:
            if error.validator == "required" and "then" in error.schema_path:
                failures = cls._find_trigger_for_conditional_required(error,
                                                                      schema)
                for failure in failures:
                    conditional_failure.add(failure)
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

        if (required_missing
                or pattern_errors
                or enum_errors
                or conditional_errors
                or outros_erros):
            raise SchemaValidationError(
                required_missing=required_missing,
                required_errors=required_errors,
                pattern_errors=pattern_errors,
                enum_errors=enum_errors,
                conditional_failure=list(conditional_failure),
                conditional_errors=conditional_errors,
                outros_erros=outros_erros,
            )

        return True
