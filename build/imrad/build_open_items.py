"""IMRaD open items: one worksheet listing every TO FILL marker in build_imrad.py.

Generated from the builder's source, so it always matches the paper. Replaces the
older IMRaD Fill-In and IMRaD Outstanding worksheets.
Run:  python build_open_items.py
"""
import ast
import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "build_imrad.py")
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "deliverables",
                                    "Resondi-IMRaD-Open-Items.docx"))

INK, GREY, ACCENT = RGBColor(0x1A, 0x1A, 0x1A), RGBColor(0x5A, 0x5A, 0x5A), RGBColor(0x8E, 0x2A, 0x52)

# Which items block the paper (CLAUDE.md B6.4 names these as load-bearing),
# keyed by a phrase that appears in the marker text.
BLOCKING = {
    "microphone": "Device: which microphone the evaluated build used",
    "four zones": "Rule layer: how the six fields map onto four zones",
    "measurement unit": "Signal: unit, reference level and comparator",
    "how many qualified": "Clarity: number of raters and their agreement",
    "blinded": "Reference labels: were the pulmonologists blinded",
    "sampling method": "Acceptance: how the 27 respondents were recruited",
    "ethics": "Ethics: committee approval or physician supervision",
    "distinct from the 13": "Acceptance: overlap of hospital patients and survey patients",
}


def items():
    """Walk the builder in source order, pairing each FILL with its section heading."""
    tree = ast.parse(open(SRC, encoding="utf-8").read())
    h1 = h2 = ""
    out = []
    for stmt in tree.body:  # top-level statements, in source order
        for call in [n for n in ast.walk(stmt) if isinstance(n, ast.Call)]:
            name = getattr(call.func, "id", "")
            if name in ("H1", "H2") and call.args:
                try:
                    text = ast.literal_eval(call.args[0])
                except ValueError:
                    continue
                if name == "H1":
                    h1, h2 = text, ""
                else:
                    h2 = text
            elif name == "FILL" and len(call.args) == 2:
                out.append((h1, h2, ast.literal_eval(call.args[1])))
    return out


def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:fill"), fill)
    tcPr.append(sh)


doc = Document()
st = doc.styles["Normal"]
st.font.name, st.font.size, st.font.color.rgb = "Calibri", Pt(10.5), INK
for s in doc.sections:
    s.top_margin = s.bottom_margin = Inches(0.8)
    s.left_margin = s.right_margin = Inches(0.8)


def para(text, size=10.5, bold=False, italic=False, color=INK, after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    r = p.add_run(text)
    r.font.size, r.bold, r.italic, r.font.color.rgb = Pt(size), bold, italic, color
    return p


ITEMS = items()
blocking = [i for i, (_, _, t) in enumerate(ITEMS)
            if any(k in t.lower() for k in BLOCKING)]

para("RESONDI", size=9, bold=True, color=ACCENT, after=0)
para("IMRaD paper: open items", size=20, bold=True, after=2)
para(f"Every TO FILL marker in the lung-only IMRaD, {len(ITEMS)} in all, in the order they "
     "appear. Generated from build/imrad/build_imrad.py on each run, so this list always "
     "matches the paper.", size=10.5, italic=True, color=GREY, after=10)
para("How to use it", size=12, bold=True, color=ACCENT, after=3)
for line in (
    "Each row names the section, what the paper needs, and whether it blocks the paper. "
    "Answer it from your records or your adviser, never by estimating.",
    "Give the answers to whoever maintains build_imrad.py. Each one replaces its FILL(...) "
    "call with real text, and this worksheet shrinks by one row on the next rebuild.",
    f"{len(blocking)} items are marked BLOCKING: the paper's main claims rest on them. "
    "Settle those first.",
):
    para("•  " + line, after=3)
para("", after=4)

t = doc.add_table(rows=1, cols=4)
t.style = "Table Grid"
for c, (h, w) in enumerate(zip(["#", "Section", "What the paper needs", "Priority"],
                               [0.35, 1.6, 4.3, 0.85])):
    cell = t.rows[0].cells[c]
    cell.width = Inches(w)
    shade(cell, "D9D9D9")
    r = cell.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(9.5)
for i, (h1, h2, text) in enumerate(ITEMS):
    row = t.add_row().cells
    vals = [str(i + 1), h2 or h1, text[0].upper() + text[1:], "BLOCKING" if i in blocking else "Lookup"]
    for c, (v, w) in enumerate(zip(vals, [0.35, 1.6, 4.3, 0.85])):
        row[c].width = Inches(w)
        r = row[c].paragraphs[0].add_run(v)
        r.font.size = Pt(9.5)
        r.bold = (c == 3 and v == "BLOCKING")

para("", after=4)
para("Not on this list because they are already settled in the paper: seven sites, MFCC input, "
     "ambient noise of 24 / 35 / 42 dB, the patient-level labels and random split behind the "
     "inflated corpus scores, and the UTAUT acceptance results.", size=9.5, italic=True, color=GREY)

doc.save(OUT)
print(f"written: {OUT}  ({len(ITEMS)} items, {len(blocking)} blocking)")
