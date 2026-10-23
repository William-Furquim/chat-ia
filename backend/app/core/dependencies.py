"""Dependências de autenticação/autorização reutilizadas pelas rotas protegidas."""
import sqlite3

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.database import get_db
from app.core.security import decodificar_token
from app.repositories import usuario_repository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def usuario_atual(
    token: str | None = Depends(oauth2_scheme),
    db: sqlite3.Connection = Depends(get_db),
) -> dict:
    """Exige header `Authorization: Bearer <token>` válido. Caso contrário, 401."""
    erro = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token ausente ou inválido. Faça login novamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise erro
    payload = decodificar_token(token)
    if not payload:
        raise erro
    usuario = usuario_repository.buscar_por_id(db, int(payload["sub"]))
    if not usuario:
        raise erro
    return dict(usuario)
