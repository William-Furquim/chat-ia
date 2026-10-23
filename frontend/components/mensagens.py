"""Renderiza o histórico de mensagens de uma conversa."""
import streamlit as st


def render(mensagens: list[dict]) -> None:
    if not mensagens:
        st.caption("Conversa vazia. Escreva a primeira mensagem abaixo.")
    for m in mensagens:
        with st.chat_message(m["papel"]):
            st.markdown(m["conteudo"])
