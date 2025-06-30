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


async def run_rpa(form_type, data):
    """Executa o fluxo do RPA utilizando Playwright assíncrono."""
    screenshots = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # TODO: implementar login no SISCAN usando CPF/senha de users db

        # TODO: navegar até o formulário e preencher campos com 'data'
        # Exemplo: page.handle_fill("input[name=campo1]",
        """
        req = RequisicaoExameMamografiaRastreio(
            base_url=SISCAN_URL, user=SISCAN_USER, password=SISCAN_PASSWORD
        )

        req._context = SiscanBrowserContext(headless=headless)

        await req.authenticate()
        await req.preencher(json_data)
        """
        # informations = req.context.information_messages
        if not PRODUCTION and TAKE_SCREENSHOT:
            for i in range(1, 4):
                path = f"static/tmp/{form_type}_step{i}.png"
                await page.screenshot(path=path)
                screenshots.append(path)

        if PRODUCTION:
            await page.click("button[type=submit]")

        await browser.close()

    return {"success": True, "screenshots": screenshots}
