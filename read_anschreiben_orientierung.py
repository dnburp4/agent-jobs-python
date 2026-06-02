    
# PDF einmal lesen für matching_score
import fitz

def read_anschreiben_orientierung(cv_path: str) -> str:

    doc = fitz.open(cv_path)
    text_lebenslauf = ""
    for page in doc:
        text_lebenslauf += page.get_text()
    
    return text_lebenslauf