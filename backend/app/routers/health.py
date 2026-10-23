from fastapi import APIRouter, Depends

from app.llm.provider import LLMProvider, get_provider
from app.schemas.conversas import HealthSaida

router = APIRouter(tags=["Saúde"])


@router.get("/health", response_model=HealthSaida, summary="Verifica se a API está no ar")
def health(provider: LLMProvider = Depends(get_provider)):
    """Rota pública. Retorna o status da API e o modelo/provedor em uso."""
    return {"status": "ok", "provedor": provider.nome}
