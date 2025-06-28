from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..env import get_db
from ..models import User
from ..utils.helpers import verify_password, create_access_token

router = APIRouter(prefix="/security", tags=["security"])


@router.post(
    "/token",
    summary="Gerar token JWT",
    description="Gera um token de acesso para autenticação nos endpoints",
)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    db = get_db()
    user = db.query(User).filter_by(username=form_data.username).first()
    db.close()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect username or password",
        )
    token = create_access_token({"sub": user.uuid})
    return {"access_token": token, "token_type": "bearer"}
