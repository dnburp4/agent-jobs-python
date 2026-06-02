from __future__ import annotations
from typing import Optional, Any
from typing_extensions import TypedDict


class JobAgentState(TypedDict):
    # Inputs vom User
    cv_path: str
    user_input: str
    anschreiben_path: Optional[str]

    # Nach cv_analyse_node
    cv_text: str
    candidate_profile: Any          # CandidateProfile Pydantic-Instanz

    # Nach job_search_node
    ranked_jobs: list[dict]
    best_job: Any                   # pd.DataFrame (1 Zeile)

    # Nach anschreiben_node
    anschreiben: Any  # AnschreibenSchema
