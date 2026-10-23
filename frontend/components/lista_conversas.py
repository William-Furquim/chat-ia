"""Barra lateral: usuário, botão "Nova conversa", lista de conversas e sair."""
import streamlit as st

import state
from services import api_client


def render() -> None:
    token = st.session_state.token
    with st.sidebar:
        st.markdown(f"### 💬 Chat IA\nOlá, **{st.session_state.username}**")
        if st.button("➕ Nova conversa", use_container_width=True, type="primary"):
            try:
                nova = api_client.criar_conversa(token)
                st.session_state.conversa_id = nova["id"]
                st.rerun()
            except api_client.ApiError as e:
                state.tratar_erro(e)

        st.divider()
        st.caption("Suas conversas")
        try:
            conversas = api_client.listar_conversas(token)
        except api_client.ApiError as e:
            state.tratar_erro(e)
            conversas = []

        if not conversas:
            st.info("Nenhuma conversa ainda. Clique em “Nova conversa”.")
        for c in conversas:
            ativa = c["id"] == st.session_state.conversa_id
            if st.button(c["titulo"], key=f"conv_{c['id']}", use_container_width=True,
                         type="secondary" if not ativa else "primary", icon="💬" if not ativa else "▶️"):
                st.session_state.conversa_id = c["id"]
                st.rerun()

        st.divider()
        if st.button("Sair", use_container_width=True):
            state.sair()
            st.rerun()
