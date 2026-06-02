from fpdf import FPDF
from Agent_Langgraph.models import AnschreibenSchema

_UNICODE_MAP = str.maketrans({
    '–': '-',    # en dash
    '—': '-',    # em dash
    '‘': "'",    # linkes einfaches Anführungszeichen
    '’': "'",    # rechtes einfaches Anführungszeichen
    '“': '"',    # linkes doppeltes Anführungszeichen
    '”': '"',    # rechtes doppeltes Anführungszeichen
    '…': '...',  # Auslassungspunkte
    ' ': ' ',    # geschütztes Leerzeichen
})


def _safe(text: str | None) -> str:
    if not text:
        return ""
    return text.translate(_UNICODE_MAP)


_LEFT = 25
_RIGHT = 20
_TOP = 20
_USABLE_W = 210 - _LEFT - _RIGHT  # 165 mm
_LH = 5.5   # standard line height


def generate_pdf(data: AnschreibenSchema) -> bytes:
    pdf = FPDF("P", "mm", "A4")
    pdf.set_margins(left=_LEFT, top=_TOP, right=_RIGHT)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # --- Absender (klein, oben links) ---
    pdf.set_font("Helvetica", size=10)
    for line in [
        data.absender.name,
        data.absender.strasse,
        data.absender.ort,
        f"Tel: {data.absender.telefon}",
        data.absender.email,
    ]:
        pdf.cell(_USABLE_W, _LH, _safe(line), align="R")
        pdf.ln(_LH)

    pdf.ln(8)

    # --- Empfänger (links) ---
    pdf.set_font("Helvetica", size=10)
    emp_lines = [data.empfaenger.unternehmen]
    if data.empfaenger.ansprechsartner:
        emp_lines.append(data.empfaenger.ansprechsartner)
    if data.empfaenger.strasse:
        emp_lines.append(data.empfaenger.strasse)
    emp_lines.append(data.empfaenger.ort)
    for line in emp_lines:
        pdf.cell(_USABLE_W, _LH, _safe(line))
        pdf.ln(_LH)

    pdf.ln(5)

    # --- Datum (rechtsbündig) ---
    pdf.cell(_USABLE_W, _LH, _safe(data.datum), align="R")
    pdf.ln(10)

    # --- Betreff (fett) ---
    pdf.set_font("Helvetica", style="B", size=10)
    pdf.multi_cell(_USABLE_W, _LH, _safe(data.betreff))
    pdf.ln(8)

    # --- Anrede ---
    pdf.set_font("Helvetica", size=10)
    pdf.cell(_USABLE_W, _LH, _safe(data.anrede))
    pdf.ln(_LH + 3)

    # --- Absätze mit Abstand dazwischen ---
    for absatz in data.absaetze:
        pdf.multi_cell(_USABLE_W, _LH, _safe(absatz))
        pdf.ln(4)

    # --- Abschluss & Unterschrift ---
    pdf.ln(3)
    pdf.cell(_USABLE_W, _LH, _safe(data.abschluss))
    pdf.ln(14)
    pdf.cell(_USABLE_W, _LH, _safe(data.unterschrift))

    return bytes(pdf.output())
