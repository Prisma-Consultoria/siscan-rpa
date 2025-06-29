from typing import List
from pydantic import BaseModel, Field
from enum import Enum


class InputType(Enum):
    """
    # Exemplo de uso
    tipo = LogicalInputType.CHECKBOX
    print(tipo.html_element)  # 'input'
    """

    TEXT = "text"
    DATE = "date"
    VALUE = "value"
    NUMBER = "number"
    CHECKBOX = "checkbox"
    TEXTAREA = "textarea"
    LIST = "list"
    SELECT = "select"
    RADIO = "radio"

    @property
    def html_element(self) -> str:
        if self in {
            InputType.TEXT,
            InputType.DATE,
            InputType.VALUE,
            InputType.NUMBER,
            InputType.CHECKBOX,
        }:
            return "input"
        elif self == InputType.TEXTAREA:
            return "textarea"
        elif self in {InputType.LIST, InputType.SELECT}:
            return "select"
        elif self == InputType.RADIO:
            return "radio"
        else:
            raise ValueError(f"Tipo de input não suportado: {self.value}")


class RequirementLevel(Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"

    # Ou, para uso de instância:
    def is_required(self) -> bool:
        """
        Verifica se a instância representa o nível 'required'.
        """
        return self is RequirementLevel.REQUIRED


class LoginInput(BaseModel):
    """Modelo de entrada para login/cadastro de usuário."""

    username: str = Field(..., description="Nome de usuário para cadastro")
    password: str = Field(..., description="Senha do usuário, deve ser criptografada")

    model_config = {
        "json_schema_extra": {"example": {"username": "alice", "password": "secret"}}
    }
