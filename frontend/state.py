"""Estado mínimo da sessão: token, usuário e conversa ativa. O histórico NUNCA é guardado aqui."""
import streamlit as st

_PADRAO = {"token": None, "username": None, "conversa_id": None, "aviso": None}


def iniciar() -> None:
    for chave, valor in _PADRAO.items():
        st.session_state.setdefault(chave, valor)


def logado() -> bool:
    return bool(st.session_state.get("token"))


def entrar(token: str, username: str) -> None:
    st.session_state.update(token=token, username=username, conversa_id=None, aviso=None)


def sair(aviso: str | None = None) -> None:
    st.session_state.update(token=None, username=None, conversa_id=None, aviso=aviso)


def tratar_erro(erro) -> None:
    """401 derruba a sessão; qualquer outro erro é mostrado como mensagem amigável."""
    if erro.sessao_expirada:
        sair("Sua sessão expirou. Faça login novamente.")
        st.rerun()
    st.error(erro.mensagem)
