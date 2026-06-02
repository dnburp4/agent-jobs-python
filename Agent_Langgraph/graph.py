from __future__ import annotations
import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from langgraph.graph import StateGraph, START, END

from Agent_Langgraph.state import JobAgentState
from Agent_Langgraph.nodes import cv_analyse_node, job_search_node, anschreiben_node


def build_graph():
    """
    Baut und kompiliert den sequenziellen Job-Application-Graphen.

    START → cv_analyse_node → job_search_node → anschreiben_node → END
    """
    graph = StateGraph(JobAgentState)

    graph.add_node("cv_analyse", cv_analyse_node)
    graph.add_node("job_search", job_search_node)
    graph.add_node("anschreiben", anschreiben_node)

    graph.add_edge(START, "cv_analyse")
    graph.add_edge("cv_analyse", "job_search")
    graph.add_edge("job_search", "anschreiben")
    graph.add_edge("anschreiben", END)

    return graph.compile()
