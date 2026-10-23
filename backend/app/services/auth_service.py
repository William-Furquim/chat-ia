"""Regras de negócio de autenticação."""
import sqlite3

from app.core.exceptions import CredenciaisInvalidas, UsuarioJaExiste
from app.core.security import criar_token, hash_senha, verificar_senha
from app.repositories import usuario_repository


def registrar(db: sqlite3.Connection, username: str, senha: str) -> dict:
    if usuario_repository.buscar_por_username(db, username):
        raise UsuarioJaExiste("Este nome de usuário já está em uso.")
    usuario_id = usuario_repository.criar(db, username, hash_senha(senha))
    return {"id": usuario_id, "username": username}


def login(db: sqlite3.Connection, username: str, senha: str) -> dict:
    usuario = usuario_repository.buscar_por_username(db, username)
    if not usuario or not verificar_senha(senha, usuario["senha_hash"]):
        raise CredenciaisInvalidas("Usuário ou senha incorretos.")
    return {
        "access_token": criar_token(usuario["id"], usuario["username"]),
        "token_type": "bearer",
        "username": usuario["username"],
    }
