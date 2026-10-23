"""Configurações da API, lidas de variáveis de ambiente / arquivo .env."""
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    database_path: str
    jwt_secret: str
    jwt_algorithm: str
    jwt_expire_minutes: int
    llm_provider: str  # "simulado" | "gemini"
    gemini_api_key: str
    gemini_model: str
    llm_timeout: int


def get_settings() -> Settings:
    """Lê as configurações a cada chamada (facilita os testes)."""
    return Settings(
        database_path=os.getenv("DATABASE_PATH", str(BACKEND_DIR / "chat.db")),
        jwt_secret=os.getenv("JWT_SECRET", "dev-secret-troque-em-producao-0123456789"),
        jwt_algorithm="HS256",
        jwt_expire_minutes=int(os.getenv("JWT_EXPIRE_MINUTES", "120")),
        llm_provider=os.getenv("LLM_PROVIDER", "simulado").lower(),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        llm_timeout=int(os.getenv("LLM_TIMEOUT", "20")),
    )
