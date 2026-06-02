from __future__ import annotations
import streamlit as st
from Agent_Langgraph.db import get_profile


def render_inputs() -> dict | None:
    st.title("PyJobAgent")
    st.markdown(
        "Lade deinen Lebenslauf hoch, prompte deine Stellenwünsche und optional kannst du ein Referenz-Anschreiben für den Stil hochladen."
        "\n\n### Unser Agent kümmert sich um **den Rest**: "
        "\n\nEr *analysiert* deinen *Lebenslauf*, sucht passende *Stellen*, bewertet sie und generiert ein individuelles *Anschreiben* für die beste Stelle."
    )

    user_id = st.session_state.get("user_id")
    use_saved = False

    if user_id:
        if not st.session_state.get("profile_loaded"):
            st.session_state["saved_profile"] = get_profile(user_id)
            st.session_state["profile_loaded"] = True

        if st.session_state.get("saved_profile"):
            use_saved = st.toggle("Gespeichertes CV-Profil verwenden", value=True)
            if use_saved:
                st.info("Dein gespeichertes Profil wird verwendet — kein Upload nötig.")

    cv_file = None
    if not use_saved:
        cv_file = st.file_uploader("Lebenslauf (PDF)", type="pdf")

    user_input = st.text_area(
        "Was für eine Stelle suchst du?",
        placeholder="z.B. Werkstudent IT, Cloud oder KI, Standort egal",
        height=80,
    )

    ref_file = st.file_uploader(
        "Referenz-Anschreiben für Stil (optional, PDF)",
        type="pdf",
    )

    if st.button("Stellen suchen & Anschreiben generieren", type="primary"):
        if not use_saved and not cv_file:
            st.error("Bitte Lebenslauf hochladen.")
            return None
        if not user_input.strip():
            st.error("Bitte Stellenwunsch eingeben.")
            return None
        return {
            "cv_file": cv_file,
            "user_input": user_input.strip(),
            "ref_file": ref_file,
            "use_saved_profile": use_saved,
        }

    return None
