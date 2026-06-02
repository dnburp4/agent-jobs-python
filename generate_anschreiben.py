from google import genai
from google.genai import types
import os
import pandas as pd
import datetime

from Agent_Langgraph.models import AnschreibenSchema

genai_client = genai.Client()


def generate_anschreiben(
    raw_cv: str,
    cv_keywords_formated: str,
    job_description: pd.DataFrame,
    anschreiben_orientierung_stil_beispiel: str = None,
) -> AnschreibenSchema:
    SYSTEM_PROMPT = f"""
    Du bist ein Experte für deutsche Bewerbungsschreiben. Deine Aufgabe ist es,
    professionelle, individuelle Anschreiben für den folgenden Bewerber zu erstellen.

    === ANWEISUNGEN ===
    Schreibe ein Anschreiben mit folgenden Eigenschaften:

    1. STRUKTUR (DIN 5008):
    - Absenderblock (Name, Adresse, Telefon, E-Mail) — aus dem Lebenslauf extrahieren
    - Empfängerblock (Unternehmen, ggf. Straße, Ort) — aus der Stellenbeschreibung
    - Ort und Datum (Konstanz, den [aktuelles Datum im Format "DD. Monat YYYY"]). Nutze immer das aktuelle Datum {datetime.datetime.now().strftime("%d. %B %Y")}.
    - Betreffzeile (z.B. "Bewerbung als Praktikant im Bereich XY") — nie (m/w/d) im Betreff
    - Anrede ("Sehr geehrte Frau [Name]," oder "Sehr geehrte Damen und Herren,")
    - 3–4 Absätze Brieftext
    - Grußformel + Name

    2. INHALT DER ABSÄTZE:
    Absatz 1 – Einstieg & Motivation:
    - Warum diese Stelle und dieses Unternehmen konkret?
    - Direkten Bezug zur Stellenausschreibung herstellen

    Absatz 2 – Studium & fachliche Kompetenzen:
    - Relevante Studieninhalte und Fähigkeiten zur Stelle

    Absatz 3 – Berufserfahrung & Soft Skills:
    - Relevante Praxiserfahrungen mit konkreten Aufgaben

    Absatz 4 – Schluss:
    - Verfügbarkeit und Einladung zum Gespräch

    3. STIL:
    - Professionell, direkt, authentisch – kein Floskel-Deutsch
    - Max. 1 DIN-A4-Seite (ca. 300–400 Wörter im Brieftext)

    4. STIL-REFERENZ (falls vorhanden, Sprache und Syntax übernehmen):
    {anschreiben_orientierung_stil_beispiel}

    === LEBENSLAUF (Volltext) ===
    {raw_cv}
    === LEBENSLAUF (Keywords) ===
    {cv_keywords_formated}
    === STELLE ===
    {job_description.to_string(index=False)}
    """

    response = genai_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=SYSTEM_PROMPT,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AnschreibenSchema,
        ),
    )

    return AnschreibenSchema.model_validate_json(response.text)