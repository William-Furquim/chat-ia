"""Caixa de envio: manda o texto à API; a resposta aparece ao recarregar o histórico."""
import streamlit as st

import state
from services import api_client


def render(conversa_id: int) -> None:
    texto = st.chat_input("Digite sua mensagem…")
    if not texto:
        return
    with st.chat_message("user"):
        st.markdown(texto)
    try:
        with st.chat_message("assistant"), st.spinner("Pensando…"):
            api_client.enviar_mensagem(st.session_state.token, conversa_id, texto)
    except api_client.ApiError as e:
        if e.status == 404:
            st.session_state.conversa_id = None
        state.tratar_erro(e)
        return
    st.rerun()
