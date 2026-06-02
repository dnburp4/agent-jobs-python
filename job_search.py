import sys
import time
import fitz
import requests
import pandas as pd
from bs4 import BeautifulSoup
import lebenslauf_analayse
import matching_score
from generate_anschreiben import generate_anschreiben
from read_anschreiben_orientierung import read_anschreiben_orientierung

sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "https://www.arbeitnow.com/api/job-board-api"


def _clean_html(html: str) -> str:
    return BeautifulSoup(html, "html.parser").get_text(separator=" ", strip=True)


def _fetch_page(page: int) -> list:
    try:
        res = requests.get(BASE_URL, params={"page": page}, timeout=10)
        res.raise_for_status()
        return res.json().get("data", [])
    except Exception as e:
        print(f"  Fehler auf Seite {page}: {e}")
        return []


def _parse_job(job: dict) -> dict:
    return {
        "slug": job.get("slug"),
        "company_name": job.get("company_name"),
        "title": job.get("title"),
        "description": _clean_html(job.get("description", "")),
        "location": job.get("location"),
        "remote": job.get("remote"),
        "url": job.get("url"),
        "tags": ", ".join(job.get("tags", [])),
        "job_types": ", ".join(job.get("job_types", [])),
    }


def load_jobs() -> pd.DataFrame:
    all_jobs = []
    page = 1

    print("Lade Jobs von Arbeitnow API...")
    while True:
        data = _fetch_page(page)
        if not data:
            break
        all_jobs.extend(data)
        print(f"  Seite {page}: {len(data)} Stellen geladen")
        page += 1
        time.sleep(0.3)

    if not all_jobs:
        print("Keine Jobs geladen.")
        return pd.DataFrame()

    df = pd.DataFrame([_parse_job(j) for j in all_jobs])
    print(f"\nGesamt: {len(df)} Stellen geladen.\n")
    return df


def search_jobs(df: pd.DataFrame, keywords: list[str], job_type: str, top_n: int = 3) -> pd.DataFrame:
    if df.empty:
        print("DataFrame ist leer.")
        return df

    print(f"Pflichtfilter Job-Typ: '{job_type}'")
    print(f"Skill-Keywords: {keywords}\n")

    df = df.copy()

    # Pflichtfilter: job_type muss im Titel oder job_types-Feld stehen
    title_tags = (df["title"].fillna("") + " " + df["job_types"].fillna("")).str.lower()
    df = df[title_tags.str.contains(job_type.lower(), na=False)]

    if df.empty:
        print(f"Keine Stellen mit Job-Typ '{job_type}' gefunden.")
        return df

    print(f"{len(df)} Stellen mit Job-Typ '{job_type}' gefunden. Filtere nach Skills...\n")

    searchable = (
        df["title"].fillna("") + " "
        + df["description"].fillna("") + " "
        + df["tags"].fillna("")
    ).str.lower()

    def count_hits(text: str) -> int:
        return sum(1 for kw in keywords if kw.lower() in text)

    df["_hits"] = searchable.apply(count_hits)
    matched = df[df["_hits"] > 0].sort_values("_hits", ascending=False).head(top_n)

    if matched.empty:
        print("Keine passenden Stellen gefunden.")
    else:
        print(f"{len(matched)} passende Stellen gefunden (top {top_n}):\n")
        for _, row in matched.iterrows():
            print(f"  [{row['_hits']} Treffer] {row['title']} @ {row['company_name']} — {row['location']}")
            print(f"  {row['url']}\n")

    return matched.drop(columns=["_hits"])


if __name__ == "__main__":
    cv_path = r"C:\Users\nicol\Desktop\STUDIUM\Proyectos\agent-jobs-python\pdf_data\CV_BurbanoPuertas.pdf"
    anschreiben_path = r"C:\Users\nicol\Desktop\STUDIUM\Proyectos\agent-jobs-python\pdf_data\Bewerbung_Aesculap_BurbanoPuertas.pdf"

    profile = lebenslauf_analayse.keys_words_create("Finde für mich eine Stelle als Werkstudent in meinem Bereich IT .Standort ist egal für mich", cv_path)
    print(f"Job-Typ: {profile.job_type}")
    print(f"Keywords: {profile.search_keywords}")

    # PDF einmal lesen für matching_score
    doc = fitz.open(cv_path)
    text_lebenslauf = ""
    for page in doc:
        text_lebenslauf += page.get_text()

    df = load_jobs()
    results = search_jobs(df, keywords=profile.search_keywords, job_type=profile.job_type, top_n=5)

    if not results.empty:
        print("\nErgebnis DataFrame:")
        print(results[["title", "company_name", "location", "url"]].to_string(index=False))
    print("*" * 50)

    print("Erstellung von Matching Score...")
    print("=" * 50)
    matching_scores = matching_score.matching_score(results, text_lebenslauf)
    print("\nMatching Scores:")


    for score in matching_scores:
        print(f"  [{score['matching_score']}] {score['title']} @ {score['company_name']}")
        print(f"  {score['begrundung']}\n")

    df_result_matching_scores = pd.DataFrame(matching_scores)
    print("\nDataFrame mit Matching Scores:")
    print(df_result_matching_scores[["title", "company_name", "location", "matching_score", "begrundung"]])

    print("*" * 50)

    df_max_score = df_result_matching_scores.nlargest(1, "matching_score")[["title", "company_name", "location", "matching_score", "begrundung", "description"]]

    print("\nBeste Stelle basierend auf Matching Score:")
    print(df_max_score.to_string(index=False))
    
    bereits_vorhandenes_anschreiben_fuer_orientierung = read_anschreiben_orientierung(anschreiben_path)

    generate_anschreiben(
        raw_cv=text_lebenslauf,
        cv_keywords_formated=", ".join(profile.search_keywords),
        job_description=df_max_score,
        anschreiben_orientierung_stil_beispiel=bereits_vorhandenes_anschreiben_fuer_orientierung,
    )



