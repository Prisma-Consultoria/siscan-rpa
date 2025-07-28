import jwt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from typing import Any, Dict, Optional

from src.env import private_key, public_key

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

