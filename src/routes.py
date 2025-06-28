from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.exc import IntegrityError
from .env import get_db
from .models import User
from .utils.helpers import (
    run_rpa,
    encrypt_password,
)
from .utils.dependencies import jwt_required
from src.utils import messages as msg
from src.utils.schema import CadastrarInput, PreencherSolicitacaoInput

router = APIRouter()


@router.post(
    "/cadastrar-usuario",
    status_code=201,
    summary="Cadastrar Usuário",
    description="Registra um novo usuário no banco de dados",
)
def cadastrar_usuario(data: CadastrarInput):
    """Cadastrar novo usuário e armazenar a senha criptografada."""
    username = data.username
    encrypted = encrypt_password(data.password)
    db = get_db()
    try:
        db.add(User(username=username, password=encrypted))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=msg.ERR_USERNAME_EXISTS)
    finally:
        db.close()

    return {"message": msg.USER_CREATED}


@router.post(
    "/preencher-solicitacao-mamografia",
    summary="Preencher Solicitação de Mamografia",
    description="Executa o RPA para preencher a solicitação de mamografia no SIScan",
    dependencies=[Depends(jwt_required)],
)
async def preencher_solicitacao(data: PreencherSolicitacaoInput):
    """Preencher automaticamente a solicitação de mamografia no SIScan."""
    result = await run_rpa("solicitacao", data.__dict__)
    return result


@router.post(
    "/preencher-laudo-mamografia",
    summary="Preencher Laudo de Mamografia",
    description="Executa o RPA para preencher o laudo de mamografia no SIScan",
)
async def preencher_laudo(data: dict):
    """Preencher automaticamente o laudo de mamografia no SIScan."""
    result = await run_rpa("laudo", data)
    return result
