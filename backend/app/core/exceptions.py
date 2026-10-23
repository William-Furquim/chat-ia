"""Exceções de domínio. Os handlers em main.py as convertem em códigos HTTP."""


class ErroDeDominio(Exception):
    def __init__(self, mensagem: str):
        self.mensagem = mensagem
        super().__init__(mensagem)


class CredenciaisInvalidas(ErroDeDominio):  # 401
    pass


class UsuarioJaExiste(ErroDeDominio):  # 409
    pass


class ConversaNaoEncontrada(ErroDeDominio):  # 404
    pass


class ModeloIndisponivel(ErroDeDominio):  # 503
    pass
