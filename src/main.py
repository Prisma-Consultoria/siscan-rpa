import logging
from fastapi import FastAPI

from .env import Base, engine
from .routes.preencher_formulario_siscan import (
    router as formulario_router,
)
from .routes.security import router as security_router
from .routes.user import router as user_router

logging.basicConfig(
    level=logging.DEBUG,  # Troque para logging.INFO caso deseje menos verbosidade
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="API RPA SISCAN",
    description="API para interação com o sistema SISCAN RPA",
    version="0.1.0",
)

# Cria tabelas a partir dos models
Base.metadata.create_all(bind=engine)

app.include_router(user_router)
app.include_router(formulario_router)
app.include_router(security_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5001)
