from __future__ import annotations
import os
import sys
import tempfile
import streamlit as st

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from Agent_Langgraph import build_graph, JobAgentState
from Agent_Langgraph.db import get_profile, save_profile

_NODE_LABELS = {
    "cv_analyse": "CV wird analysiert...",
    "job_search": "Stellen werden geladen & bewertet...",
    "anschreiben": "Anschreiben wird generiert...",
}


def run_pipeline(inputs: dict) -> JobAgentState:
    """Führt den LangGraph aus und zeigt den Fortschritt per Node."""
    use_saved = inputs.get("use_saved_profile", False)
    user_id = st.session_state.get("user_id")

    ref_bytes = inputs["ref_file"].getbuffer() if inputs["ref_file"] else None
    ref_path = None
    if ref_bytes:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_ref:
            tmp_ref.write(ref_bytes)
            ref_path = tmp_ref.name

    # Wenn gespeichertes Profil: kein tempfile für CV nötig
    cv_path = ""
    if not use_saved:
        cv_bytes = inputs["cv_file"].getbuffer()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_cv:
            tmp_cv.write(cv_bytes)
            cv_path = tmp_cv.name

    initial_state: JobAgentState = {
        "cv_path": cv_path,
        "user_input": inputs["user_input"],
        "anschreiben_path": ref_path,
        "cv_text": "",
        "candidate_profile": None,
        "ranked_jobs": [],
        "best_job": None,
        "anschreiben": "",
    }

    # Gespeichertes Profil in State laden → cv_analyse_node wird übersprungen
    if use_saved and user_id:
        saved = st.session_state.get("saved_profile") or get_profile(user_id)
        if saved:
            from lebenslauf_analayse import CandidateProfile
            initial_state["cv_text"] = saved["cv_text"]
            initial_state["candidate_profile"] = CandidateProfile.model_validate(
                saved["candidate_profile"]
            )

    final_state = initial_state.copy()

    try:
        app = build_graph()
        with st.status("Pipeline läuft...", expanded=True) as status:
            for node_output in app.stream(initial_state):
                node_name = list(node_output.keys())[0]
                label = _NODE_LABELS.get(node_name, node_name)
                st.write(f"✅ {label}")
                final_state.update(node_output[node_name])
            status.update(label="Fertig!", state="complete")
    finally:
        if cv_path:
            os.unlink(cv_path)
        if ref_path:
            os.unlink(ref_path)

    # Profil in DB speichern wenn eingeloggt und neues CV hochgeladen
    if user_id and not use_saved and final_state.get("candidate_profile"):
        save_profile(
            user_id=user_id,
            cv_text=final_state["cv_text"],
            candidate_profile=final_state["candidate_profile"].model_dump(),
        )
        st.session_state["saved_profile"] = get_profile(user_id)

    return final_state


def run_manual_pipeline(inputs: dict) -> JobAgentState:
    """Pipeline ohne Jobsuche: CV analysieren + manuell eingefügte Stelle verwenden."""
    import fitz
    import pandas as pd
    from lebenslauf_analayse import keys_words_create, CandidateProfile
    from generate_anschreiben import generate_anschreiben
    from read_anschreiben_orientierung import read_anschreiben_orientierung

    use_saved = inputs.get("use_saved_profile", False)
    user_id = st.session_state.get("user_id")

    ref_bytes = inputs["ref_file"].getbuffer() if inputs["ref_file"] else None
    ref_path = None
    if ref_bytes:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_ref:
            tmp_ref.write(ref_bytes)
            ref_path = tmp_ref.name

    cv_path = ""
    if not use_saved:
        cv_bytes = inputs["cv_file"].getbuffer()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_cv:
            tmp_cv.write(cv_bytes)
            cv_path = tmp_cv.name

    try:
        with st.status("Pipeline läuft...", expanded=True) as status:
            if use_saved and user_id:
                saved = st.session_state.get("saved_profile") or get_profile(user_id)
                cv_text = saved["cv_text"]
                candidate_profile = CandidateProfile.model_validate(saved["candidate_profile"])
                st.write("✅ Gespeichertes Profil geladen.")
            else:
                st.write("⏳ CV wird analysiert...")
                doc = fitz.open(cv_path)
                cv_text = "".join(page.get_text() for page in doc)
                doc.close()
                candidate_profile = keys_words_create(
                    user_input=f"{inputs['job_title']} bei {inputs['company_name']}",
                    filename=cv_path,
                )
                st.write("✅ CV wurde analysiert.")

            st.write("⏳ Anschreiben wird generiert...")
            best_job = pd.DataFrame([{
                "title": inputs["job_title"],
                "company_name": inputs["company_name"],
                "location": inputs.get("job_location", ""),
                "matching_score": 100,
                "begrundung": "Manuell eingegeben",
                "description": inputs["job_description"],
            }])

            style_example = None
            if ref_path and os.path.isfile(ref_path):
                style_example = read_anschreiben_orientierung(ref_path)

            anschreiben = generate_anschreiben(
                raw_cv=cv_text,
                cv_keywords_formated=", ".join(candidate_profile.search_keywords),
                job_description=best_job,
                anschreiben_orientierung_stil_beispiel=style_example,
            )
            st.write("✅ Anschreiben wurde generiert.")
            status.update(label="Fertig!", state="complete")
    finally:
        if cv_path:
            os.unlink(cv_path)
        if ref_path:
            os.unlink(ref_path)

    # Profil in DB speichern wenn eingeloggt und neues CV hochgeladen
    user_id = st.session_state.get("user_id")
    if user_id and not use_saved:
        save_profile(
            user_id=user_id,
            cv_text=cv_text,
            candidate_profile=candidate_profile.model_dump(),
        )
        st.session_state["saved_profile"] = get_profile(user_id)

    return {
        "cv_path": "",
        "user_input": inputs["job_title"],
        "anschreiben_path": None,
        "cv_text": cv_text,
        "candidate_profile": candidate_profile,
        "ranked_jobs": [],
        "best_job": None,
        "anschreiben": anschreiben,
    }
