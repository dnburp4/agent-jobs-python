from __future__ import annotations
import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st

# Secrets aus Streamlit (lokal: .streamlit/secrets.toml, Cloud: Web-UI) nach os.environ bridgen
try:
    for _key, _val in st.secrets.items():
        if isinstance(_val, str):
            os.environ.setdefault(_key, _val)
except Exception:
    pass  # Lokal ohne secrets.toml: os.environ bereits durch .env oder Shell gesetzt

from Agent_Langgraph.db import sign_in, sign_up, sign_out

st.set_page_config(page_title="PyJobAgent", page_icon="💼", layout="wide")

# --- Sidebar Auth ---
with st.sidebar:
    if st.session_state.get("user_id"):
        st.success(f"Eingeloggt als\n{st.session_state['user_email']}")
        if st.button("Abmelden"):
            sign_out()
            st.session_state.pop("user_id", None)
            st.session_state.pop("user_email", None)
            st.session_state.pop("profile_loaded", None)
            st.rerun()
    else:
        with st.expander("Anmelden / Registrieren (optional)"):
            tab_login, tab_register = st.tabs(["Anmelden", "Registrieren"])

            with tab_login:
                email = st.text_input("E-Mail", key="login_email")
                password = st.text_input("Passwort", type="password", key="login_pw")
                if st.button("Anmelden", key="btn_login"):
                    try:
                        res = sign_in(email, password)
                        st.session_state["user_id"] = res.user.id
                        st.session_state["user_email"] = res.user.email
                        st.rerun()
                    except Exception as e:
                        st.error(f"Fehler: {e}")

            with tab_register:
                email_r = st.text_input("E-Mail", key="reg_email")
                password_r = st.text_input("Passwort", type="password", key="reg_pw")
                if st.button("Registrieren", key="btn_register"):
                    try:
                        res = sign_up(email_r, password_r)
                        st.success("Konto erstellt! Bitte E-Mail bestätigen, dann anmelden.")
                    except Exception as e:
                        st.error(f"Fehler: {e}")

pg = st.navigation([
    st.Page("pages/agent_page.py", title="Agent Anschreiben"),
    st.Page("pages/anschreiben_generator_page.py", title="Anschreiben Generator"),
])
pg.run()
