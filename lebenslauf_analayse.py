import fitz
import json
import os
import re
from pydantic import BaseModel
from groq import Groq


class CandidateProfile(BaseModel):
    name: str
    skills: list[str]
    experience_years: int
    education: str
    languages: list[str]
    job_type: str
    search_keywords: list[str]


def keys_words_create(user_input: str, filename: str = "") -> CandidateProfile:
    
    # 1. PDF einlesen - AUSSERHALB des loops zusammenbauen
    path = filename.strip()
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()  # nur das ist im loop
    
    # 2. Prompt - NACH dem loop, wenn text vollständig ist
    system_prompt = """
    Analysiere diesen Lebenslauf. Extrahiere die Daten UND
    generiere 6 Such-Keywords, mit denen man passende
    Stellenanzeigen in Deutschland finden würde, die zu dem User Input passen.
    
    Analysiere immer, was der User als Wunsch Stelle angegeben hat und 
    generiere die Keywords basierend auf diesen Informationen.

    Die Keywords sollen konkrete Jobtitel/Technologien sein und die gewünschte 
    Stelle des User Inputs angeben wie zum Beispiel Praktikum, Werkstudent, 
    Senior, Junior oder Trainee.
    
    Außerdem muss du immer den Bereich des Bewerbers in einem Keyword erkennen.
    Wähle immer einen der folgenden Bereiche als einzlenes Keyword aus, basierend auf dem Lebenslauf und User Input:
    IT, Marketing, Business, Medizin, Social Media, executive, Relations, 
    Communication, Engineering, Consulting, Supply, HR, Customer Service, 
    Development, Finance, Controlling

    ACHTUNG - Die search_keywords müssen nur einzelne Wörter sein (keine Kombinationen wie "Data Science").
    Die search_keywords sollen NUR Skills/Technologien/Fachbereiche sein - KEIN Job-Typ wie Werkstudent oder Praktikum.
    Den Job-Typ (Werkstudent, Praktikum, Senior, etc.) trägst du separat in das Feld "job_type" ein.

    Antworte NUR als JSON, kein Text davor oder danach:
    {
      "name": "...",
      "skills": [...],
      "experience_years": 0,
      "education": "...",
      "languages": [...],
      "job_type": "Werkstudent",
      "search_keywords": ["IT", "Java", "SQL", "Development", "Finance", "Controlling"]
    }

    Lebenslauf:
    """ + text  # CV-Text hier anhängen

    # 3. Groq Client - korrekte Syntax
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # 4. API Call
    chat_completion = client.chat.completions.create(
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
        temperature=0.1,  # niedrig für konsistentes JSON
    )

    # 5. Response holen
    raw_response = chat_completion.choices[0].message.content
    print("Raw Response:\n", raw_response)

    # 6. JSON parsen und Pydantic validieren
    # manchmal gibt das LLM ```json ... ``` zurück, das müssen wir entfernen
    cleaned = re.sub(r"```json|```", "", raw_response).strip()
    
    profile = CandidateProfile.model_validate_json(cleaned)
    return profile


if __name__ == "__main__":
    cv_path = r"C:\Users\nicol\Desktop\STUDIUM\Proyectos\agent-jobs-python\pdf_data\CV_BurbanoPuertas.pdf"
    user_input = input("Was für eine Stelle suchst du? ")
    
    candidate_profile = keys_words_create(user_input, cv_path)
    
    print("\n✅ Profil erfolgreich erstellt:")
    print(candidate_profile.search_keywords)


