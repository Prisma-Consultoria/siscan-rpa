from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.exc import IntegrityError

from ..env import get_db
from ..models import User
from ..utils.helpers import encrypt_password, decode_access_token
from ..utils.dependencies import jwt_required
from ..utils import messages as msg
from ..utils.schema import CadastrarInput

router = APIRouter(prefix="/user", tags=["user"])


@router.post("", status_code=201, summary="Criar Usuário", description="Registra um novo usuário")
def create_user(data: CadastrarInput):
    """Cadastrar novo usuário e armazenar a senha criptografada."""
    encrypted = encrypt_password(data.password)
    db = get_db()
    try:
        db.add(User(username=data.username, password=encrypted))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=msg.ERR_USERNAME_EXISTS)
    finally:
        db.close()
    return {"message": msg.USER_CREATED}


@router.get("/me", summary="Usuário Autenticado", description="Retorna informações do usuário autenticado", dependencies=[Depends(jwt_required)])
def read_me(authorization: str = Header(...)):
    token = authorization.split(" ", 1)[1]
    payload = decode_access_token(token)
    db = get_db()
    user = db.query(User).filter_by(uuid=payload.get("sub")).first()
    db.close()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return {
        "uuid": user.uuid,
        "username": user.username,
        "created_at": user.created_at.isoformat(),
    }
