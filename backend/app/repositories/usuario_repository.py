"""Persistência de usuários (SQL puro, sem regra de negócio)."""
import sqlite3
from datetime import datetime, timezone


def agora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def buscar_por_username(db: sqlite3.Connection, username: str) -> sqlite3.Row | None:
    return db.execute("SELECT * FROM usuarios WHERE username = ?", (username,)).fetchone()


def buscar_por_id(db: sqlite3.Connection, usuario_id: int) -> sqlite3.Row | None:
    return db.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()


def criar(db: sqlite3.Connection, username: str, senha_hash: str) -> int:
    cur = db.execute(
        "INSERT INTO usuarios (username, senha_hash, criado_em) VALUES (?, ?, ?)",
        (username, senha_hash, agora()),
    )
    db.commit()
    return cur.lastrowid
