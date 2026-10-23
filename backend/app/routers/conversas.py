import sqlite3

from fastapi import APIRouter, Depends, status

from app.core.database import get_db
from app.core.dependencies import usuario_atual
from app.llm.provider import LLMProvider, get_provider
from app.schemas.conversas import (
    ConversaCriar,
    ConversaDetalhe,
    ConversaResumo,
    MensagemEntrada,
    RespostaChat,
)
from app.services import conversa_service

# Todas as rotas deste router exigem token (autenticação) e só enxergam dados do dono (autorização).
router = APIRouter(prefix="/conversas", tags=["Conversas"], dependencies=[Depends(usuario_atual)])

_RESPOSTAS_COMUNS = {401: {"description": "Token ausente ou inválido"}}


@router.get("", response_model=list[ConversaResumo], summary="Lista as conversas do usuário logado",
            responses=_RESPOSTAS_COMUNS)
def listar(db: sqlite3.Connection = Depends(get_db), usuario: dict = Depends(usuario_atual)):
    """Mais recentes primeiro. Nunca inclui conversas de outros usuários."""
    return conversa_service.listar_conversas(db, usuario["id"])


@router.post("", response_model=ConversaResumo, status_code=status.HTTP_201_CREATED,
             summary="Cria uma nova conversa", responses=_RESPOSTAS_COMUNS)
def criar(dados: ConversaCriar, db: sqlite3.Connection = Depends(get_db),
          usuario: dict = Depends(usuario_atual)):
    """Cria uma conversa vazia. Sem título, vira "Nova conversa" e é renomeada na primeira mensagem."""
    return conversa_service.criar_conversa(db, usuario["id"], dados.titulo)


@router.get("/{conversa_id}", response_model=ConversaDetalhe, summary="Abre uma conversa com o histórico",
            responses={**_RESPOSTAS_COMUNS, 404: {"description": "Conversa inexistente (ou de outro usuário)"}})
def abrir(conversa_id: int, db: sqlite3.Connection = Depends(get_db),
          usuario: dict = Depends(usuario_atual)):
    """Devolve a conversa e todas as mensagens, em ordem cronológica."""
    return conversa_service.abrir_conversa(db, conversa_id, usuario["id"])


@router.post("/{conversa_id}/mensagens", response_model=RespostaChat, status_code=status.HTTP_201_CREATED,
             summary="Envia uma mensagem e recebe a resposta do bot",
             responses={**_RESPOSTAS_COMUNS, 404: {"description": "Conversa inexistente"},
                        422: {"description": "Mensagem vazia ou inválida"},
                        503: {"description": "Modelo de linguagem indisponível"}})
def enviar(conversa_id: int, dados: MensagemEntrada, db: sqlite3.Connection = Depends(get_db),
           usuario: dict = Depends(usuario_atual), provider: LLMProvider = Depends(get_provider)):
    """Grava a mensagem do usuário, consulta o modelo e grava a resposta. Ambas ficam no banco."""
    return conversa_service.enviar_mensagem(db, conversa_id, usuario["id"], dados.conteudo, provider)
