"""Regras de negócio de conversas e mensagens."""
import sqlite3

from app.core.exceptions import ConversaNaoEncontrada
from app.llm.provider import LLMProvider
from app.repositories import conversa_repository as repo

TITULO_PADRAO = "Nova conversa"


def criar_conversa(db: sqlite3.Connection, usuario_id: int, titulo: str | None) -> dict:
    conversa = repo.criar_conversa(db, usuario_id, (titulo or "").strip() or TITULO_PADRAO)
    return dict(conversa)


def listar_conversas(db: sqlite3.Connection, usuario_id: int) -> list[dict]:
    return [dict(c) for c in repo.listar_conversas(db, usuario_id)]


def _obter_conversa(db: sqlite3.Connection, conversa_id: int, usuario_id: int) -> sqlite3.Row:
    conversa = repo.buscar_conversa(db, conversa_id, usuario_id)
    if not conversa:
        raise ConversaNaoEncontrada("Conversa não encontrada.")
    return conversa


def abrir_conversa(db: sqlite3.Connection, conversa_id: int, usuario_id: int) -> dict:
    conversa = _obter_conversa(db, conversa_id, usuario_id)
    mensagens = [dict(m) for m in repo.listar_mensagens(db, conversa_id)]
    return {**dict(conversa), "mensagens": mensagens}


def enviar_mensagem(
    db: sqlite3.Connection, conversa_id: int, usuario_id: int, conteudo: str, provider: LLMProvider
) -> dict:
    conversa = _obter_conversa(db, conversa_id, usuario_id)
    historico = [{"papel": m["papel"], "conteudo": m["conteudo"]} for m in repo.listar_mensagens(db, conversa_id)]
    historico.append({"papel": "user", "conteudo": conteudo})

    # Chama o modelo ANTES de gravar: se falhar (503), nada fica pela metade no banco.
    texto = provider.responder(historico)

    msg_user = repo.inserir_mensagem(db, conversa_id, "user", conteudo)
    msg_bot = repo.inserir_mensagem(db, conversa_id, "assistant", texto)
    if conversa["titulo"] == TITULO_PADRAO:
        repo.atualizar_conversa(db, conversa_id, titulo=conteudo[:40].strip())
    else:
        repo.atualizar_conversa(db, conversa_id)
    db.commit()
    return {
        "conversa_id": conversa_id,
        "mensagem_usuario": dict(msg_user),
        "resposta": dict(msg_bot),
        "modelo": provider.nome,
        "criado_em": msg_bot["criado_em"],
    }
