import binascii
import hashlib
import hmac
import secrets

from fastapi import Header, HTTPException

from app.db.database import get_user_by_session_token

PASSWORD_ITERATIONS = 200_000


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    salt_bytes = (
        secrets.token_bytes(16)
        if salt is None
        else binascii.unhexlify(salt.encode("utf-8"))
    )
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_bytes,
        PASSWORD_ITERATIONS,
    )
    return (
        binascii.hexlify(password_hash).decode("utf-8"),
        binascii.hexlify(salt_bytes).decode("utf-8"),
    )


def verify_password(password: str, password_hash: str, password_salt: str) -> bool:
    computed_hash, _ = hash_password(password, password_salt)
    return hmac.compare_digest(computed_hash, password_hash)


def create_session_token() -> str:
    return secrets.token_urlsafe(32)


def get_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        return None

    return token.strip()


def require_current_user(authorization: str | None = Header(default=None)) -> dict:
    token = get_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required.")

    user = get_user_by_session_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")

    return user
