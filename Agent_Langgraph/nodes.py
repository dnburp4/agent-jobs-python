from __future__ import annotations
import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import fitz
import pandas as pd

from lebenslauf_analayse import keys_words_create
from job_search import load_jobs, search_jobs
from matching_score import matching_score
from generate_anschreiben import generate_anschreiben
from read_anschreiben_orientierung import read_anschreiben_orientierung

from Agent_Langgraph.state import JobAgentState


def cv_analyse_node(state: JobAgentState) -> dict:
    """Node 1: CV als Text extrahieren + Kandidatenprofil mit LLM erstellen."""
    cv_path: str = state["cv_path"]
    user_input: str = state["user_input"]

    doc = fitz.open(cv_path)
    cv_text = ""
    for page in doc:
        cv_text += page.get_text()
    doc.close()

    candidate_profile = keys_words_create(user_input=user_input, filename=cv_path)

    return {
        "cv_text": cv_text,
        "candidate_profile": candidate_profile,
    }


def job_search_node(state: JobAgentState) -> dict:
    """Node 2: Jobs laden, filtern, mit KI ranken und beste Stelle auswählen."""
    cv_text: str = state["cv_text"]
    profile = state["candidate_profile"]

    jobs_df = load_jobs()
    filtered = search_jobs(
        df=jobs_df,
        keywords=profile.search_keywords,
        job_type=profile.job_type,
        top_n=5,
    )

    ranked = matching_score(jobs_filtered=filtered, cv_candidate=cv_text)

    df_ranked = pd.DataFrame(ranked)
    best_job = df_ranked.nlargest(1, "matching_score")[
        ["title", "company_name", "location", "matching_score", "begrundung", "description"]
    ]

    return {
        "ranked_jobs": ranked,
        "best_job": best_job,
    }


def anschreiben_node(state: JobAgentState) -> dict:
    """Node 3: Anschreiben mit Gemini generieren, optional mit Stil-Referenz."""
    cv_text: str = state["cv_text"]
    profile = state["candidate_profile"]
    best_job: pd.DataFrame = state["best_job"]
    ref_path: str | None = state.get("anschreiben_path")

    style_example: str | None = None
    if ref_path and os.path.isfile(ref_path):
        style_example = read_anschreiben_orientierung(ref_path)

    anschreiben_text = generate_anschreiben(
        raw_cv=cv_text,
        cv_keywords_formated=", ".join(profile.search_keywords),
        job_description=best_job,
        anschreiben_orientierung_stil_beispiel=style_example,
    )

    return {"anschreiben": anschreiben_text}
