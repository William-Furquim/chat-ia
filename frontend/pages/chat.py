"""Página principal do chat: sidebar + histórico + caixa de envio."""
import streamlit as st

import state
from components import caixa_envio, lista_conversas, mensagens
from services import api_client


def render() -> None:
    lista_conversas.render()

    conversa_id = st.session_state.conversa_id
    if conversa_id is None:
        st.title("💬 Chat com IA")
        st.info("Escolha uma conversa na barra lateral ou clique em “Nova conversa”.")
        return

    try:
        conversa = api_client.abrir_conversa(st.session_state.token, conversa_id)  # histórico vem da API
    except api_client.ApiError as e:
        if e.status == 404:
            st.session_state.conversa_id = None
        state.tratar_erro(e)
        return

    st.subheader(conversa["titulo"])
    mensagens.render(conversa["mensagens"])
    caixa_envio.render(conversa_id)
