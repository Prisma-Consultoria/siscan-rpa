from pydantic import BaseModel, Field


class LoginInput(BaseModel):
    """Modelo de entrada para login/cadastro de usuário."""

    username: str = Field(..., description="Nome de usuário para cadastro")
    password: str = Field(..., description="Senha do usuário, deve ser "
                                           "criptografada")

    model_config = {
        "json_schema_extra": {"example": {"username": "alice", "password": "secret"}}
    }