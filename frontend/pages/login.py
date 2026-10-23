"""Página de login e cadastro."""
import streamlit as st

import state
from services import api_client


def render() -> None:
    st.title("💬 Chat com IA")
    st.caption("Entre ou crie uma conta para acessar suas conversas.")

    if st.session_state.aviso:
        st.warning(st.session_state.aviso)

    try:
        info = api_client.health()
        st.success(f"API no ar • modelo: {info['provedor']}", icon="✅")
    except api_client.ApiError as e:
        st.error(e.mensagem)

    aba_entrar, aba_criar = st.tabs(["Entrar", "Criar conta"])

    with aba_entrar:
        with st.form("form_login"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", type="primary"):
                try:
                    r = api_client.login(usuario, senha)
                    state.entrar(r["access_token"], r["username"])
                    st.rerun()
                except api_client.ApiError as e:
                    st.error(e.mensagem)

    with aba_criar:
        with st.form("form_registro"):
            usuario = st.text_input("Novo usuário (3 a 30 caracteres)")
            senha = st.text_input("Nova senha (mín. 6 caracteres)", type="password")
            if st.form_submit_button("Criar conta"):
                try:
                    api_client.registrar(usuario, senha)
                    r = api_client.login(usuario, senha)
                    state.entrar(r["access_token"], r["username"])
                    st.rerun()
                except api_client.ApiError as e:
                    st.error(e.mensagem)
