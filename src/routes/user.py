from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.exc import IntegrityError

from src.env import get_db
from src.models import User
from src.routes.auth.dependencies import api_key_required
from src.routes.auth.utils import encrypt_password, oauth2_scheme, \
    decode_access_token
from src.siscan.schema.auth_schema import LoginInput
from src.siscan import messages as msg

router = APIRouter(prefix="/user", tags=["user"])


@router.post(
    "",
    status_code=201,
    summary="Criar Usuário",
    description="Registra um novo usuário",
    dependencies=[Depends(api_key_required)],
)
def create_user(data: LoginInput):
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


@router.get(
    "/me",
    summary="Usuário Autenticado",
    description="Retorna informações do usuário autenticado",
    dependencies=[Depends(oauth2_scheme)],
)
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
