import os
from datetime import datetime

from dotenv import load_dotenv
from google import genai
from langchain.tools import Tool, StructuredTool
import fitz

load_dotenv()

STELLE_PATH = r"C:\Users\nicol\Desktop\STUDIUM\Proyectos\agent-jobs-python\stelle.txt"
DEFAULT_CV_PATH = r"C:\Users\nicol\Desktop\STUDIUM\Proyectos\agent-jobs-python\pdf_data\CV_BurbanoPuertas.pdf"

genai_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def _extract_lebenslauf(filename: str = "") -> str:
    path = filename.strip() if filename else DEFAULT_CV_PATH
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

lebenslauf_tool = Tool(
    name="lebenslauf",
    func=_extract_lebenslauf,
    description="Extracts text from a Lebenslauf PDF file. Input: absolute path to the PDF.",
)


def search_jobs(user_cv_information: str = "") -> str:
    #Hier ist die Stelle hardgecodede als TXT. 
    # Hier sollten wir die Funktionalität implementieren, um die Stelle basierend auf den Informationen aus dem CV zu suchen
    # Stelle sollte aus dem API kommen

    with open(STELLE_PATH, "r", encoding="utf-8") as f:
        stellenangebot = f.read()
    return stellenangebot

search_jobs_tool = Tool(
    name="search_jobs",
    func=search_jobs,
    description="Searches for job opportunities based on user's CV information. Returns the job description text.",
)


def generate_anschreiben(
    user_cv_information: str,
    job_description: str,
    filename: str = "anschreiben.txt",
) -> str:
    SYSTEM_PROMPT = f"""
    Du bist ein Experte für deutsche Bewerbungsschreiben. Deine Aufgabe ist es,
    professionelle, individuelle Anschreiben für den folgenden Bewerber zu erstellen.

    === ANWEISUNGEN ===
    Schreibe ein Anschreiben mit folgenden Eigenschaften:

    1. STRUKTUR (DIN 5008):
    - Absenderblock (Name, Adresse, Telefon, E-Mail)
    - Empfängerblock (Unternehmen, Ansprechperson, Adresse)
    - Ort und Datum (Konstanz, den [aktuelles Datum])
    - Betreffzeile (z.B. "Bewerbung als Praktikant im Bereich XY")
    - Anrede ("Sehr geehrte Frau [Name]," oder "Sehr geehrte Damen und Herren,")
    - 3–4 Absätze Brieftext
    - Grußformel + Name

    2. INHALT DER ABSÄTZE:
    Absatz 1 – Einstieg & Motivation:
    - Warum diese Stelle und dieses Unternehmen konkret?
    - Direkten Bezug zur Stellenausschreibung herstellen
    - Kein generisches "Mit großem Interesse..."

    Absatz 2 – Studium & fachliche Kompetenzen:
    - Relevante Studieninhalte und starke Noten gezielt einbauen
    - Konkrete Fähigkeiten nennen, die zur ausgeschriebenen Stelle passen

    Absatz 3 – Berufserfahrung & Soft Skills:
    - Relevante Praxiserfahrungen mit konkreten Aufgaben verknüpfen
    - Teamfähigkeit, Eigeninitiative, Mehrsprachigkeit einbinden (wo sinnvoll)

    Absatz 4 – Schluss:
    - Verfügbarkeit für das Praxissemester / den Stellenantritt nennen
    - Einladung zum Gespräch selbstbewusst formulieren

    3. STIL:
    - Professionell, direkt, authentisch – kein Floskel-Deutsch
    - Aktive Formulierungen statt Passiv
    - Individuell auf die Stelle zugeschnitten, nicht generisch
    - Max. 1 DIN-A4-Seite (ca. 300–400 Wörter im Brieftext)
    - Keine Aufzählungspunkte im Fließtext

    4. AUSGABE:
    Gib NUR den vollständigen Anschreiben-Text aus, druckfertig formatiert.
    Keine Erklärungen oder Kommentare davor oder danach.

    === BEWERBERINFORMATIONEN LEBENSLAUF ===
    {user_cv_information}
    === STELLE ===
    {job_description}
    """

    response = genai_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=SYSTEM_PROMPT,
    )

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"--- Anschreiben Output ---\nTimestamp: {timestamp}\n\n{response.text}\n\n"

    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)
    return response.text

generate_anschreiben_tool = StructuredTool.from_function(
    func=generate_anschreiben,
    name="generate_anschreiben",
    description=(
        "Generates a German Anschreiben (cover letter) tailored to the candidate's CV "
        "and the job description. Args: user_cv_information (CV text), "
        "job_description (job posting text). Returns the Anschreiben text."
    ),
)
