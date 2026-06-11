from __future__ import annotations
import pandas as pd
import streamlit as st
from Agent_Langgraph.db import save_bewerbung
from Agent_Langgraph.download_pdf import generate_pdf
from Agent_Langgraph.models import Absender, AnschreibenSchema, Empfaenger
from Agent_Langgraph.state import JobAgentState


def render_results(state: JobAgentState) -> None:
    """Zeigt beste Stelle, Ranking-Tabelle und das generierte Anschreiben."""
    st.divider()

    # --- Beste Stelle ---
    job_url: str = ""
    best_job: pd.DataFrame | None = state.get("best_job")
    if best_job is not None and not best_job.empty:
        row = best_job.iloc[0]
        job_url = row.get("url", "") or ""
        st.subheader("Beste Stelle")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{row['title']}** @ {row['company_name']}")
            if job_url:
                st.markdown(f"[Stelle auf Arbeitnow ansehen]({job_url})")
            st.markdown(f"📍 {row['location']}")
            st.markdown(f"{row['description']}")
            st.markdown(f"_{row.get('begrundung', '')}_")
        with col2:
            st.metric("Match", f"{int(row['matching_score'])}/100")

    # --- Alle Ergebnisse ---
    ranked_jobs: list[dict] = state.get("ranked_jobs", [])
    if ranked_jobs:
        st.subheader("Alle bewerteten Stellen")
        df_all = pd.DataFrame(ranked_jobs).sort_values("matching_score", ascending=False)
        show_cols = ["title", "company_name", "location", "matching_score"]
        if "url" in df_all.columns:
            st.dataframe(
                df_all[show_cols + ["url"]],
                use_container_width=True,
                hide_index=True,
                column_config={"url": st.column_config.LinkColumn("Bewerben")},
            )
        else:
            st.dataframe(df_all[show_cols], use_container_width=True, hide_index=True)

    # --- Anschreiben ---
    anschreiben: AnschreibenSchema | None = state.get("anschreiben")
    if anschreiben is None:
        return

    st.subheader("Generiertes Anschreiben")

    # Absender
    edited_name = st.text_input("Name (Absender)", value=anschreiben.absender.name)
    edited_strasse = st.text_input("Straße (Absender)", value=anschreiben.absender.strasse)
    edited_ort = st.text_input("Ort (Absender)", value=anschreiben.absender.ort)
    edited_telefon = st.text_input("Telefon", value=anschreiben.absender.telefon)
    edited_email = st.text_input("E-Mail", value=anschreiben.absender.email)

    st.divider()

    # Empfänger
    edited_ansprechsartner = st.text_input("Ansprechpartner (Empfänger)", value=anschreiben.empfaenger.ansprechsartner or "")
    edited_unternehmen = st.text_input("Unternehmen (Empfänger)", value=anschreiben.empfaenger.unternehmen)
    edited_emp_strasse = st.text_input("Straße (Empfänger)", value=anschreiben.empfaenger.strasse or "")
    edited_emp_ort = st.text_input("Ort (Empfänger)", value=anschreiben.empfaenger.ort)

    st.divider()

    # Kopfzeilen
    edited_datum = st.text_input("Datum", value=anschreiben.datum)
    edited_betreff = st.text_input("Betreff", value=anschreiben.betreff)
    edited_anrede = st.text_input("Anrede", value=anschreiben.anrede)

    st.divider()

    # Absätze — dynamisch, egal wie viele das LLM zurückgibt
    edited_absaetze: list[str] = []
    for i, absatz in enumerate(anschreiben.absaetze):
        edited = st.text_area(f"Absatz {i + 1}", value=absatz, height=175)
        edited_absaetze.append(edited)

    st.divider()

    edited_abschluss = st.text_input("Abschluss", value=anschreiben.abschluss)
    edited_unterschrift = st.text_input("Unterschrift", value=anschreiben.unterschrift)

    # Bearbeitetes Anschreiben zusammenbauen
    edited_anschreiben = AnschreibenSchema(
        absender=Absender(
            name=edited_name,
            strasse=edited_strasse,
            ort=edited_ort,
            telefon=edited_telefon,
            email=edited_email,
        ),
        empfaenger=Empfaenger(
            ansprechsartner=edited_ansprechsartner or None,
            unternehmen=edited_unternehmen,
            strasse=edited_emp_strasse or None,
            ort=edited_emp_ort,
        ),
        datum=edited_datum,
        betreff=edited_betreff,
        anrede=edited_anrede,
        absaetze=edited_absaetze,
        abschluss=edited_abschluss,
        unterschrift=edited_unterschrift,
    )

    pdf_bytes = generate_pdf(edited_anschreiben)
    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        if st.download_button(
            label="Als PDF herunterladen",
            data=pdf_bytes,
            file_name="anschreiben.pdf",
            mime="application/pdf",
            use_container_width=True,
        ):
            user_id = st.session_state.get("user_id")
            if user_id:
                save_bewerbung(
                    user_id=user_id,
                    job_title=edited_anschreiben.betreff,
                    company=edited_anschreiben.empfaenger.unternehmen,
                    anschreiben=edited_anschreiben.model_dump(),
                )
                st.session_state.pop("bewerbungen_cache", None)
    with btn_col2:
        if job_url:
            st.link_button("Jetzt bewerben", job_url, use_container_width=True)
