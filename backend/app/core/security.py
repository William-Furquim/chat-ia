"""Hash de senha (PBKDF2) e emissão/validação de tokens JWT."""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import get_settings

_ITERACOES = 240_000


def hash_senha(senha: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt.encode(), _ITERACOES)
    return f"pbkdf2_sha256${_ITERACOES}${salt}${digest.hex()}"


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        _, iteracoes, salt, esperado = senha_hash.split("$")
        digest = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt.encode(), int(iteracoes))
    except ValueError:
        return False
    return hmac.compare_digest(digest.hex(), esperado)


def criar_token(usuario_id: int, username: str) -> str:
    cfg = get_settings()
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": str(usuario_id),
        "username": username,
        "iat": agora,
        "exp": agora + timedelta(minutes=cfg.jwt_expire_minutes),
    }
    return jwt.encode(payload, cfg.jwt_secret, algorithm=cfg.jwt_algorithm)


def decodificar_token(token: str) -> dict | None:
    """Retorna o payload ou None se o token for inválido/expirado."""
    cfg = get_settings()
    try:
        return jwt.decode(token, cfg.jwt_secret, algorithms=[cfg.jwt_algorithm])
    except jwt.PyJWTError:
        return None
