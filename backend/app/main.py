"""Ponto de entrada: cria a FastAPI, registra routers e traduz erros de domínio em HTTP."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.database import init_db
from app.core.exceptions import (
    ConversaNaoEncontrada,
    CredenciaisInvalidas,
    ErroDeDominio,
    ModeloIndisponivel,
    UsuarioJaExiste,
)
from app.routers import auth, conversas, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Chat IA Generativa — API",
    description="API de chat com múltiplas conversas por usuário, autenticação JWT e persistência em SQLite.\n\n"
                "Para testar aqui: faça `POST /auth/registrar`, depois clique em **Authorize** e informe usuário e senha.",
    version="1.0.0",
    lifespan=lifespan,
)

_STATUS_POR_ERRO = {
    CredenciaisInvalidas: 401,
    UsuarioJaExiste: 409,
    ConversaNaoEncontrada: 404,
    ModeloIndisponivel: 503,
}


@app.exception_handler(ErroDeDominio)
async def tratar_erro_de_dominio(_: Request, exc: ErroDeDominio):
    codigo = _STATUS_POR_ERRO.get(type(exc), 400)
    headers = {"WWW-Authenticate": "Bearer"} if codigo == 401 else None
    return JSONResponse(status_code=codigo, content={"detail": exc.mensagem}, headers=headers)


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(conversas.router)
