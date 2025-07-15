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