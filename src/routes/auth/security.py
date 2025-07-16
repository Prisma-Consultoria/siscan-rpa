from fastapi import APIRouter, HTTPException, status

from src.env import get_db
from src.models import User
from src.routes.auth.utils import verify_password, create_access_token
from src.siscan.schema.auth_schema import LoginInput

router = APIRouter(prefix="/security", tags=["security"])


@router.post(
    "/token",
    summary="Gerar token JWT",
    description="Gera um token de acesso para autenticação nos endpoints",
)
def login_for_access_token(data: LoginInput):
    db = get_db()
    user = db.query(User).filter_by(username=data.username).first()
    db.close()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect username or password",
        )
    token = create_access_token({"sub": user.uuid})
    return {"access_token": token, "token_type": "bearer"}
