import sqlite3

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.database import get_db
from app.core.dependencies import usuario_atual
from app.schemas.auth import RegistrarEntrada, TokenSaida, UsuarioSaida
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/registrar", response_model=UsuarioSaida, status_code=status.HTTP_201_CREATED,
             summary="Cria uma conta de usuário")
def registrar(dados: RegistrarEntrada, db: sqlite3.Connection = Depends(get_db)):
    """Cadastra usuário e senha (a senha é guardada apenas como hash PBKDF2). 409 se o usuário já existir."""
    return auth_service.registrar(db, dados.username, dados.senha)


@router.post("/login", response_model=TokenSaida, summary="Autentica e devolve um token JWT")
def login(form: OAuth2PasswordRequestForm = Depends(), db: sqlite3.Connection = Depends(get_db)):
    """Recebe `username` e `password` (form-data, padrão OAuth2) e devolve o token Bearer. 401 se inválidos."""
    return auth_service.login(db, form.username, form.password)


@router.get("/me", response_model=UsuarioSaida, summary="Dados do usuário logado")
def me(usuario: dict = Depends(usuario_atual)):
    """Rota protegida: útil para o front validar se o token guardado ainda vale."""
    return usuario
