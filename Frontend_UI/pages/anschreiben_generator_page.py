from __future__ import annotations
import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
from Agent_Langgraph.db import get_profile
from Frontend_UI.progress_section import run_manual_pipeline
from Frontend_UI.results_section import render_results

st.title("Anschreiben Generator")
st.markdown("Lade deinen Lebenslauf hoch und füge die Stellenausschreibung direkt ein.")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    # --- Profil-Toggle wenn eingeloggt ---
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

    job_title = st.text_input(
        "Stellentitel",
        placeholder="z.B. Junior Consultant DevOps & Cloud Engineer",
    )
    company_name = st.text_input(
        "Unternehmen",
        placeholder="z.B. XAAS GmbH",
    )
    job_location = st.text_input(
        "Standort (optional)",
        placeholder="z.B. Hamburg",
    )

    job_description = st.text_area(
        "Stellenausschreibung (copy & paste)",
        placeholder="Füge hier den vollständigen Text der Stellenausschreibung ein...",
        height=300,
    )

    ref_file = st.file_uploader(
        "Referenz-Anschreiben für Stil (optional, PDF)",
        type="pdf",
    )

    if st.button("Anschreiben generieren", type="primary"):
        if not use_saved and not cv_file:
            st.error("Bitte Lebenslauf hochladen.")
        elif not job_title.strip():
            st.error("Bitte Stellentitel eingeben.")
        elif not company_name.strip():
            st.error("Bitte Unternehmen eingeben.")
        elif not job_description.strip():
            st.error("Bitte Stellenausschreibung einfügen.")
        else:
            result = run_manual_pipeline({
                "cv_file": cv_file,
                "job_title": job_title.strip(),
                "company_name": company_name.strip(),
                "job_location": job_location.strip(),
                "job_description": job_description.strip(),
                "ref_file": ref_file,
                "use_saved_profile": use_saved,
            })
            st.session_state["manual_result"] = result

with col2:
    if "manual_result" in st.session_state:
        render_results(st.session_state["manual_result"])
