from pydantic import BaseModel, Field


class ConversaCriar(BaseModel):
    titulo: str | None = Field(default=None, max_length=80, examples=["Dúvidas de API"])


class MensagemEntrada(BaseModel):
    conteudo: str = Field(min_length=1, max_length=4000, examples=["Me explique o que é uma API REST"])


class MensagemSaida(BaseModel):
    id: int
    papel: str
    conteudo: str
    criado_em: str


class ConversaResumo(BaseModel):
    id: int
    titulo: str
    criado_em: str
    atualizado_em: str


class ConversaDetalhe(ConversaResumo):
    mensagens: list[MensagemSaida]


class RespostaChat(BaseModel):
    conversa_id: int
    mensagem_usuario: MensagemSaida
    resposta: MensagemSaida
    modelo: str
    criado_em: str


class HealthSaida(BaseModel):
    status: str
    provedor: str
