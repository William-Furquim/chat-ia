"""ÚNICO ponto do front que fala com a API (via requests).

Nenhuma outra parte do front importa `requests` nem conhece URLs. Todos os erros viram `ApiError`
com uma mensagem amigável, para a interface nunca exibir traceback.
"""
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
TIMEOUT = float(os.getenv("API_TIMEOUT", "10"))
TIMEOUT_CHAT = float(os.getenv("API_TIMEOUT_CHAT", "40"))  # o modelo pode demorar mais


class ApiError(Exception):
    """Erro já traduzido para o usuário final."""

    def __init__(self, mensagem: str, status: int | None = None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status

    @property
    def sessao_expirada(self) -> bool:
        return self.status == 401


def _headers(token: str | None) -> dict:
    return {"Authorization": f"Bearer {token}"} if token else {}


def _detalhe(resp: requests.Response) -> str | None:
    try:
        d = resp.json().get("detail")
    except ValueError:
        return None
    if isinstance(d, list):  # erro 422 do Pydantic
        return "Dados inválidos: " + "; ".join(str(e.get("msg", "")) for e in d)
    return d if isinstance(d, str) else None


def _request(metodo: str, caminho: str, token: str | None = None, timeout: float = TIMEOUT, **kwargs):
    try:
        resp = requests.request(metodo, f"{API_URL}{caminho}", headers=_headers(token), timeout=timeout, **kwargs)
    except requests.ConnectionError:
        raise ApiError(f"Não foi possível conectar à API em {API_URL}. Verifique se o back-end está rodando.")
    except requests.Timeout:
        raise ApiError("A API demorou demais para responder. Tente novamente.")
    except requests.RequestException:
        raise ApiError("Falha de comunicação com a API.")

    if resp.ok:
        return resp.json()

    detalhe = _detalhe(resp)
    if resp.status_code == 401:
        raise ApiError(detalhe or "Sessão expirada. Faça login novamente.", 401)
    if resp.status_code == 404:
        raise ApiError(detalhe or "Conversa não encontrada.", 404)
    if resp.status_code == 409:
        raise ApiError(detalhe or "Registro já existe.", 409)
    if resp.status_code == 422:
        raise ApiError(detalhe or "Dados inválidos.", 422)
    if resp.status_code == 503:
        raise ApiError(detalhe or "O modelo de linguagem está indisponível. Tente novamente em instantes.", 503)
    raise ApiError("Erro inesperado na API. Tente novamente.", resp.status_code)


# --- endpoints -----------------------------------------------------------------------------------
def health() -> dict:
    return _request("GET", "/health", timeout=3)


def registrar(username: str, senha: str) -> dict:
    return _request("POST", "/auth/registrar", json={"username": username, "senha": senha})


def login(username: str, senha: str) -> dict:
    return _request("POST", "/auth/login", data={"username": username, "password": senha})


def listar_conversas(token: str) -> list[dict]:
    return _request("GET", "/conversas", token)


def criar_conversa(token: str, titulo: str | None = None) -> dict:
    return _request("POST", "/conversas", token, json={"titulo": titulo})


def abrir_conversa(token: str, conversa_id: int) -> dict:
    return _request("GET", f"/conversas/{conversa_id}", token)


def enviar_mensagem(token: str, conversa_id: int, conteudo: str) -> dict:
    return _request("POST", f"/conversas/{conversa_id}/mensagens", token, timeout=TIMEOUT_CHAT,
                    json={"conteudo": conteudo})
