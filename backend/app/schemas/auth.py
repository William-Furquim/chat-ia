from pydantic import BaseModel, Field


class RegistrarEntrada(BaseModel):
    username: str = Field(min_length=3, max_length=30, pattern=r"^[A-Za-z0-9_.-]+$", examples=["william"])
    senha: str = Field(min_length=6, max_length=100, examples=["segredo123"])


class UsuarioSaida(BaseModel):
    id: int
    username: str


class TokenSaida(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
