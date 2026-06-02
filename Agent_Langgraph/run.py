from __future__ import annotations
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from Agent_Langgraph import build_graph, JobAgentState


def main() -> None:
    print("=== PyJobAgent — LangGraph ===\n")

    cv_path = r"C:\Users\nicol\Desktop\STUDIUM\Proyectos\agent-jobs-python\pdf_data\CV_BurbanoPuertas.pdf"
    print(f"CV-Pfad: {cv_path}\n")

    user_input = "Ich suche eine Stelle als Junior Entwickler. Ich wolle kein prkaitkum oder wekrkstudentstelle. Standort ist egal für mich."
    print(f"User Input: {user_input}\n")

    ref_input = r"C:\Users\nicol\Desktop\STUDIUM\Proyectos\agent-jobs-python\pdf_data\Bewerbung_Aesculap_BurbanoPuertas.pdf"
    print(f"Referenz-Anschreiben-Pfad: {ref_input}\n")

    anschreiben_path: str | None = ref_input if ref_input else None
    print(f"Anschreiben-Pfad: {anschreiben_path}\n")

    initial_state: JobAgentState = {
        "cv_path": cv_path,
        "user_input": user_input,
        "anschreiben_path": anschreiben_path,
        "cv_text": "",
        "candidate_profile": None,
        "ranked_jobs": [],
        "best_job": None,
        "anschreiben": "",
    }

    print("\n[Start] Graph läuft...\n")
    app = build_graph()
    result: JobAgentState = app.invoke(initial_state)

    print("\n" + "=" * 60)
    print("BESTE STELLE")
    print("=" * 60)
    if result.get("best_job") is not None:
        print(result["best_job"].to_string(index=False))

    print("\n" + "=" * 60)
    print("GENERIERTES ANSCHREIBEN")
    print("=" * 60)
    print(result.get("anschreiben", "[Kein Anschreiben generiert]"))
    print("\n[Fertig] Anschreiben wurde in anschreiben.txt gespeichert.")


if __name__ == "__main__":
    main()
