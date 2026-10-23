"""Entrada do front-end: configura a página e roteia entre login e chat."""
import streamlit as st

import state
from pages import chat, login

st.set_page_config(page_title="Chat IA", page_icon="💬", layout="wide")
state.iniciar()

# Roteamento: sem token só existe a página de login; com token, só a de chat.
if state.logado():
    paginas = [st.Page(chat.render, title="Chat", icon="💬", url_path="chat", default=True)]
else:
    paginas = [st.Page(login.render, title="Login", icon="🔐", url_path="login", default=True)]

st.navigation(paginas, position="hidden").run()
