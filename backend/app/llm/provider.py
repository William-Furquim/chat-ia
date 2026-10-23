"""Único ponto de acesso ao modelo de linguagem.

Trocar de modelo = mudar LLM_PROVIDER no .env. Rotas, serviços e front não mudam.
"""
from abc import ABC, abstractmethod

import requests

from app.core.config import get_settings
from app.core.exceptions import ModeloIndisponivel


class LLMProvider(ABC):
    nome: str

    @abstractmethod
    def responder(self, historico: list[dict]) -> str:
        """`historico`: lista de {"papel": "user"|"assistant", "conteudo": str}; a última é do usuário."""


class SimuladoProvider(LLMProvider):
    """Bot por regras: respostas prontas por palavra-chave, senão eco da pergunta."""

    nome = "simulado"

    _REGRAS = [
        (("api rest", "rest"), "Uma API REST expõe recursos por URLs e usa os verbos HTTP "
                               "(GET, POST, PUT, DELETE) para operar sobre eles, de forma stateless."),
        (("fastapi",), "FastAPI é um framework Python para APIs que usa type hints e Pydantic "
                       "para validar dados e gerar a documentação /docs automaticamente."),
        (("jwt", "token"), "JWT é um token assinado que carrega a identidade do usuário. "
                           "O cliente o envia no header Authorization: Bearer <token>."),
        (("streamlit",), "Streamlit transforma scripts Python em apps web; o estado da sessão "
                         "fica em st.session_state e a página é reexecutada a cada interação."),
        (("olá", "ola", "oi", "bom dia", "boa tarde", "boa noite"), "Olá! Sou o bot simulado deste "
                                                                   "checkpoint. Pergunte sobre API REST, FastAPI, JWT ou Streamlit."),
    ]

    def responder(self, historico: list[dict]) -> str:
        pergunta = historico[-1]["conteudo"].strip()
        baixa = pergunta.lower()
        for palavras, resposta in self._REGRAS:
            if any(p in baixa for p in palavras):
                return resposta
        return f"(bot simulado) Você disse: \"{pergunta}\". Esta é a mensagem nº {len(historico)} da conversa."


class GeminiProvider(LLMProvider):
    """API gratuita do Gemini via REST (chave em GEMINI_API_KEY)."""

    def __init__(self, api_key: str, modelo: str, timeout: int):
        self.api_key, self.modelo, self.timeout = api_key, modelo, timeout
        self.nome = f"gemini:{modelo}"

    def responder(self, historico: list[dict]) -> str:
        if not self.api_key:
            raise ModeloIndisponivel("GEMINI_API_KEY não configurada no back-end.")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.modelo}:generateContent"
        corpo = {
            "contents": [
                {"role": "user" if m["papel"] == "user" else "model", "parts": [{"text": m["conteudo"]}]}
                for m in historico
            ]
        }
        try:
            r = requests.post(url, json=corpo, headers={"x-goog-api-key": self.api_key}, timeout=self.timeout)
            r.raise_for_status()
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
            raise ModeloIndisponivel("O modelo de linguagem está indisponível no momento. Tente novamente.") from exc


def get_provider() -> LLMProvider:
    cfg = get_settings()
    if cfg.llm_provider == "gemini":
        return GeminiProvider(cfg.gemini_api_key, cfg.gemini_model, cfg.llm_timeout)
    return SimuladoProvider()
