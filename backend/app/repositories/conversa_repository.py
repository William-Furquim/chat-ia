"""Persistência de conversas e mensagens (SQL puro, sem regra de negócio)."""
import sqlite3

from app.repositories.usuario_repository import agora


def criar_conversa(db: sqlite3.Connection, usuario_id: int, titulo: str) -> sqlite3.Row:
    ts = agora()
    cur = db.execute(
        "INSERT INTO conversas (usuario_id, titulo, criado_em, atualizado_em) VALUES (?, ?, ?, ?)",
        (usuario_id, titulo, ts, ts),
    )
    db.commit()
    return buscar_conversa(db, cur.lastrowid, usuario_id)


def listar_conversas(db: sqlite3.Connection, usuario_id: int) -> list[sqlite3.Row]:
    return db.execute(
        "SELECT * FROM conversas WHERE usuario_id = ? ORDER BY atualizado_em DESC, id DESC",
        (usuario_id,),
    ).fetchall()


def buscar_conversa(db: sqlite3.Connection, conversa_id: int, usuario_id: int) -> sqlite3.Row | None:
    """Filtra por dono: conversa de outro usuário é tratada como inexistente."""
    return db.execute(
        "SELECT * FROM conversas WHERE id = ? AND usuario_id = ?", (conversa_id, usuario_id)
    ).fetchone()


def listar_mensagens(db: sqlite3.Connection, conversa_id: int) -> list[sqlite3.Row]:
    return db.execute(
        "SELECT * FROM mensagens WHERE conversa_id = ? ORDER BY id ASC", (conversa_id,)
    ).fetchall()


def inserir_mensagem(db: sqlite3.Connection, conversa_id: int, papel: str, conteudo: str) -> sqlite3.Row:
    cur = db.execute(
        "INSERT INTO mensagens (conversa_id, papel, conteudo, criado_em) VALUES (?, ?, ?, ?)",
        (conversa_id, papel, conteudo, agora()),
    )
    return db.execute("SELECT * FROM mensagens WHERE id = ?", (cur.lastrowid,)).fetchone()


def atualizar_conversa(db: sqlite3.Connection, conversa_id: int, titulo: str | None = None) -> None:
    if titulo is not None:
        db.execute(
            "UPDATE conversas SET titulo = ?, atualizado_em = ? WHERE id = ?",
            (titulo, agora(), conversa_id),
        )
    else:
        db.execute("UPDATE conversas SET atualizado_em = ? WHERE id = ?", (agora(), conversa_id))
