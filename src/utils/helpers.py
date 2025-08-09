from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from playwright.async_api import async_playwright

from src.env import PRODUCTION, TAKE_SCREENSHOT, private_key, public_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="security/token")


def encrypt_password(password: str) -> bytes:
    """Encrypt a plain password using the loaded RSA public key."""
    return public_key.encrypt(
        password.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def decrypt_password(encrypted_password: bytes) -> str:
    """Decrypt a password previously encrypted with :func:`encrypt_password`."""
    return private_key.decrypt(
        encrypted_password,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    ).decode()


def verify_password(password: str, encrypted_password: bytes) -> bool:
    """Return ``True`` if the provided password matches the encrypted one."""
    try:
        return decrypt_password(encrypted_password) == password
    except Exception:
        return False


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Generate a JWT signed with the RSA private key."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, private_key, algorithm="RS256")


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode a JWT token using the RSA public key."""
    return jwt.decode(token, public_key, algorithms=["RS256"])


async def run_rpa(form_type: str, data: dict) -> dict:
    """Executa o fluxo de preenchimento conforme ``form_type``."""

    from pathlib import Path
    from src.env import (
        SISCAN_URL,
        SISCAN_USER,
        SISCAN_PASSWORD,
        HEADLESS,
    )
    from src.siscan.context import SiscanBrowserContext
    from src.siscan.classes.requisicao_exame_mamografia_rastreio import (
        RequisicaoExameMamografiaRastreio,
    )
    from src.siscan.classes.requisicao_exame_mamografia_diagnostica import (
        RequisicaoExameMamografiaDiagnostica,
    )

    screenshots: list[str] = []

    cls_map = {
        "requisicao-rastreamento": RequisicaoExameMamografiaRastreio,
        "requisicao-diagnostica": RequisicaoExameMamografiaDiagnostica,
    }

    rpa_cls = cls_map.get(form_type)

    if rpa_cls is None:
        # fluxos não implementados retornam sucesso imediato
        return {"success": True, "screenshots": []}

    context = SiscanBrowserContext(headless=HEADLESS)
    req = rpa_cls(base_url=SISCAN_URL, user=SISCAN_USER, password=SISCAN_PASSWORD)
    req._context = context

    try:
        await req.preencher(data)

        if TAKE_SCREENSHOT:
            Path("static/tmp").mkdir(parents=True, exist_ok=True)
            screenshot = await req.take_screenshot(
                f"{form_type}.png", subdir="static/tmp"
            )
            screenshots.append(str(screenshot))

        informations = req.context.information_messages
        success = True
        error = None
    except Exception as exc:  # pragma: no cover - network errors
        success = False
        informations = {}
        error = str(exc)
    finally:
        try:
            await context.close()
        except Exception:
            pass

    result = {"success": success, "screenshots": screenshots}
    if informations:
        result["information_messages"] = informations
    if error:
        result["error"] = error
    return result
