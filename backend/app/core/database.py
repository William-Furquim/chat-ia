"""Conexão SQLite e criação do esquema."""
import sqlite3
from collections.abc import Iterator

from app.core.config import get_settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    criado_em TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS conversas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    titulo TEXT NOT NULL,
    criado_em TEXT NOT NULL,
    atualizado_em TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS mensagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversa_id INTEGER NOT NULL REFERENCES conversas(id) ON DELETE CASCADE,
    papel TEXT NOT NULL CHECK (papel IN ('user', 'assistant')),
    conteudo TEXT NOT NULL,
    criado_em TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_conversas_usuario ON conversas(usuario_id);
CREATE INDEX IF NOT EXISTS idx_mensagens_conversa ON mensagens(conversa_id);
"""


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(get_settings().database_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = connect()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def get_db() -> Iterator[sqlite3.Connection]:
    """Dependência FastAPI: uma conexão por requisição."""
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()
