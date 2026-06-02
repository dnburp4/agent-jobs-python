import json
import re
import pandas as pd
import groq
import os

def matching_score(jobs_filtered: pd.DataFrame, cv_candidate: str) -> str:
    # Hier muss die KI, dann die Matching Funktion übbernehmen.

    system_prompt = f"""Als Job-Matching-Experte, bewerte die Relevanz der folgenden Stellenanzeigen für einen Kandidaten basierend auf seinem Lebenslauf.
    Vergleiche die Stellenanzeigen mit den Informationen im Lebenslauf und gib eine Punktzahl von 0 bis 100 zurück, wobei 100 die höchste Relevanz bedeutet. 
    Berücksichtige dabei die Übereinstimmung von Fähigkeiten, Erfahrungen, Bildung und anderen relevanten Faktoren.
    Stelle sicher, dass die Bewertung objektiv und konsistent ist, basierend auf den bereitgestellten Informationen.

    Als Output von dem Score gebe JSON-Array zurück mit allen Splaten der originalen Dataframe 
    + eine zusätzliche Spalte "matching_score" mit der Punktzahl von 0 bis 100 für jede Stellenanzeige 
    + eine neue Spalte "begrundung", warum die Stelle relevant oder nicht relevant ist für den Kandidaten basierend auf dem Lebenslauf.
    Schreibe 2 Sätze als eine passende Begründung. 
    
    Antworte NUR als JSON-Array, kein Text davor oder danach.
    """

    # Beschreibungen kürzen damit der LLM-Context nicht überschritten wird
    df_slim = jobs_filtered.copy()
    df_slim["description"] = df_slim["description"].str[:500]

    user_input = f"""Hier das das Dataframe mit den wichgtisthen Anfragen, die deterministich schon erstellt wurden:
    {df_slim.to_json(orient='records')}

    Hier das der Lebenslauf des Kandidaten als Text:
    {cv_candidate}
    """

    client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

    matching_job = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_input,
            }
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.1,
    )

    raw = matching_job.choices[0].message.content
    cleaned = re.sub(r"```json|```", "", raw).strip()
    return json.loads(cleaned)
    