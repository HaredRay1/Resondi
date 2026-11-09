"""Revision pack: everything the user pastes into their own copy of the concept note.

Section text and tables are lifted from the rebuilt concept note itself, so the
pack cannot drift from the master document.
"""
import re, copy
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph
from docx.table import Table

import os
_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
SRC = os.path.normpath(os.path.join(_ROOT, "deliverables", "Resondi-Concept-Note-FINAL.docx"))
OUT = os.path.normpath(os.path.join(_ROOT, "deliverables", "Resondi-Financial-Revision-Pack.docx"))
FIG = {11: os.path.join(_ROOT, "figures", "Figure-11-Allocation-500k.png"),
       12: os.path.join(_ROOT, "figures", "Figure-12-Cumulative-Recovery.png"),
       8:  os.path.join(_ROOT, "figures", "Figure-08-Business-Model-Canvas.png")}

DEEP, PRIMARY = RGBColor(0x5E,0x16,0x36), RGBColor(0x8E,0x2A,0x52)
INK, GREY, TEAL = RGBColor(0x3A,0x27,0x30), RGBColor(0x8A,0x74,0x80), RGBColor(0x0E,0x8F,0x86)
RED = RGBColor(0xC0,0x00,0x00)
HEAD, BAND = "F6DCE7", "FBEFF4"

src = Document(SRC)
body = list(src.element.body.iterchildren())

def ptext(el):
    return "".join(t.text or "" for t in el.iter(qn("w:t")))

def find(start_text, after=0):
    for i, el in enumerate(body):
        if i >= after and el.tag == qn("w:p") and ptext(el).strip().startswith(start_text):
            return i
    raise SystemExit("not found: " + start_text)

# ── output document ──────────────────────────────────────────────────────
doc = Document()
st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(11)
st.paragraph_format.space_after = Pt(0)
sec = doc.sections[0]
sec.left_margin = sec.right_margin = Inches(0.9)
sec.top_margin = sec.bottom_margin = Inches(0.8)

def P(text="", size=11, bold=False, italic=False, color=INK, after=6, before=0,
      align=None, indent=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format; pf.space_after = Pt(after); pf.space_before = Pt(before)
    pf.line_spacing = 1.15
    if indent is not None: pf.left_indent = Inches(indent)
    if align: p.alignment = align
    if text:
        r = p.add_run(text); r.bold = bold; r.italic = italic
        r.font.size = Pt(size); r.font.color.rgb = color
    return p

def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), fill); tcPr.append(sh)

def rule(color="E6CCD8"):
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(6)
    pPr = p._p.get_or_add_pPr(); b = OxmlElement("w:pBdr")
    bt = OxmlElement("w:bottom"); bt.set(qn("w:val"), "single"); bt.set(qn("w:sz"), "6")
    bt.set(qn("w:space"), "1"); bt.set(qn("w:color"), color); b.append(bt); pPr.append(b)

def where(txt):
    """Rose placement banner that sits above every block to paste."""
    t = doc.add_table(rows=1, cols=1); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = t.rows[0].cells[0]; shade(c, "FBE9F0")
    p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(2)
    r = p.add_run("WHERE IT GOES  "); r.bold = True; r.font.size = Pt(8.5); r.font.color.rgb = PRIMARY
    r = p.add_run(txt); r.font.size = Pt(9.5); r.font.color.rgb = INK
    P(after=4)

def copy_para(el):
    """Rebuild a source paragraph run by run, keeping bold, italic and red markers."""
    sp = Paragraph(el, src)
    if not ptext(el).strip():
        return
    p = doc.add_paragraph()
    pf = p.paragraph_format; pf.space_after = Pt(7); pf.line_spacing = 1.15
    if sp.alignment is not None: p.alignment = sp.alignment
    txt = ptext(el).strip()
    if re.fullmatch(r"(Figure|Table) \d+", txt) or sp.paragraph_format.keep_with_next:
        pf.keep_with_next = True
    for r in sp.runs:
        nr = p.add_run(r.text)
        nr.bold, nr.italic = r.bold, r.italic
        nr.font.size = Pt(11)
        col = r.font.color.rgb if r.font.color and r.font.color.type else None
        nr.font.color.rgb = RED if str(col) == "C00000" else INK

def copy_table(el):
    st_ = Table(el, src)
    rows = [[c.text for c in r.cells] for r in st_.rows]
    ncol = len(rows[0])
    t = doc.add_table(rows=len(rows), cols=ncol); t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        is_head = i == 0
        is_group = (not is_head and not row[0].startswith(" ") and row[0].isupper()) \
                   or row[0].strip().upper() == "TOTAL"
        for j, txt in enumerate(row):
            c = t.rows[i].cells[j]; c.text = ""
            p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(1)
            r = p.add_run(txt.strip() if j else txt.replace("   ", "", 1) if txt.startswith("   ") else txt)
            r.font.size = Pt(9.5); r.font.color.rgb = INK
            r.bold = is_head or is_group
            if txt.startswith("   ") and j == 0:
                p.paragraph_format.left_indent = Inches(0.18)
            if is_head: shade(c, HEAD)
            elif is_group: shade(c, BAND)
    W = {"Line item": (3.9, 1.3, 1.3), "Category": (3.7, 1.4, 1.4)}.get(rows[0][0])
    if W:
        t.autofit = False
        for col, w in zip(t.columns, W): col.width = Inches(w)
        for row in t.rows:
            for c, w in zip(row.cells, W): c.width = Inches(w)
    P(after=6)

def copy_range(a, b, figs=()):
    """Copy body[a:b]; images are swapped for the rose figure files in order."""
    figs = list(figs)
    for el in body[a:b]:
        if el.tag == qn("w:tbl"):
            copy_table(el)
        elif el.tag == qn("w:p"):
            if el.findall(".//" + qn("w:drawing")):
                n = figs.pop(0)
                p = P(after=10, align=WD_ALIGN_PARAGRAPH.CENTER)
                p.add_run().add_picture(FIG[n], width=Inches(6.7 if n == 8 else 6.0))
            else:
                copy_para(el)

# ── title ────────────────────────────────────────────────────────────────
P("RESONDI", 24, True, color=DEEP, after=0)
P("Concept note — financial revision pack", 13, italic=True, color=PRIMARY, after=4)
P("Paste-ready replacements for the financial requirement, its tables and figures, the "
  "business model canvas, and every other passage the ₱500,000 change touches. Each block "
  "carries a rose banner telling you exactly where it goes. Red text marks data only you can "
  "supply.", 10, color=GREY, after=10)

# placement map
P("Placement map", 14, True, color=DEEP, before=4, after=6)
MAP = [
 ("Figure 8", "Business Model section, under “Business Model Canvas”", "Replace image; own landscape page"),
 ("Table 4, row 4", "Business Model section, “Unit economics”", "Replace one cell"),
 ("3 paragraphs", "Business Model section, after the Year 1 / Year 2 projection paragraph", "Replace"),
 ("Opening paragraph", "FINANCIAL REQUIREMENT, first paragraph", "Replace"),
 ("Figure 11", "FINANCIAL REQUIREMENT, after the opening paragraph", "Replace (donut → bar chart)"),
 ("Table 9", "FINANCIAL REQUIREMENT, after Figure 11", "Replace"),
 ("Table 10", "FINANCIAL REQUIREMENT, “Detailed breakdown”", "Replace"),
 ("3 paragraphs", "FINANCIAL REQUIREMENT, “What the requirement does not include”", "Replace the one paragraph with three"),
 ("Figure 12", "FINANCIAL REQUIREMENT, “Return on the requirement”, after its first paragraph", "NEW — insert"),
 ("3 paragraphs", "FINANCIAL REQUIREMENT, “Return on the requirement”", "Replace"),
 ("6 sentences", "Evidence, development priority, value proposition, business model, Table 8, continuity", "Swap the figures shown"),
]
t = doc.add_table(rows=len(MAP) + 1, cols=3); t.style = "Table Grid"
for j, h in enumerate(("What", "Where in the concept note", "Action")):
    c = t.rows[0].cells[j]; c.text = ""; shade(c, HEAD)
    r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(9.5); r.font.color.rgb = INK
for i, row in enumerate(MAP, 1):
    for j, txt in enumerate(row):
        c = t.rows[i].cells[j]; c.text = ""
        r = c.paragraphs[0].add_run(txt); r.font.size = Pt(9.5); r.font.color.rgb = INK
        r.bold = j == 0
        if j == 2 and txt.startswith("NEW"): r.font.color.rgb = TEAL; r.bold = True
for row in t.rows:
    row.cells[0].width, row.cells[1].width, row.cells[2].width = Inches(1.4), Inches(3.6), Inches(1.7)
P(after=4)
P("Numbering does not change: Figure 12 is new but falls after Figure 11, which was "
  "previously the last figure, and no table is added or removed.", 9.5, italic=True, color=GREY, after=6)

# ── PART 1: business model section ───────────────────────────────────────
P("1  Business model section", 15, True, color=DEEP, after=8).paragraph_format.page_break_before = True

where("Business Model section, under the heading “Business Model Canvas”, on a page of its own "
      "turned to LANDSCAPE, image at full width (about 10 in with 0.5 in margins). In Google Docs: "
      "select the caption and image, then File → Page setup → Apply to: Selected content → Landscape. "
      "At portrait width the canvas text drops below a readable size.")
i8 = next(i for i, el in enumerate(body) if el.tag == qn("w:p") and ptext(el).strip() == "Figure 8")
copy_range(i8, i8 + 3, figs=[8])

where("Table 4 (Unit Economics and Pricing Derivation), fourth row “Platform operating "
      "cost”. Replace only the middle Derivation cell; the Amount stays ₱350 per month.")
P("Metered cloud, storage and backup per active facility at pilot scale, carried at",
  11, after=4, indent=0.2)
P("Why: the old cell derived ₱350 by dividing the seed’s cloud budget by five facilities, "
  "which double-counts money already spent and is only right at a scale the business never "
  "operates at.", 9.5, italic=True, color=GREY, after=10, indent=0.2)

where("Business Model section, “How value is captured”. These three paragraphs replace "
      "the paragraph that begins “The annual figures are run-rate totals” and the one that "
      "begins “Two conservatisms are built into these figures”. Paste them directly after "
      "the paragraph that ends “…which is ₱450,600 of that total.”")
a = find("The annual figures are run-rate totals")
b = find("Why the model is sustainable")
copy_range(a, b)

# ── PART 2: financial requirement ────────────────────────────────────────
P("2  Financial requirement — the whole section", 15, True, color=DEEP, after=4).paragraph_format.page_break_before = True
P("Everything from the FINANCIAL REQUIREMENT heading down to (not including) REFERENCES. "
  "Simplest route: delete the old section in your document and paste this whole part in "
  "one go.", 10, color=GREY, after=10)
a = find("FINANCIAL REQUIREMENT")
b = find("REFERENCES")
where("Starts at the FINANCIAL REQUIREMENT heading. Figure 11 replaces the old donut chart; "
      "Tables 9 and 10 replace the old ₱300,000 tables; Figure 12 is new and sits inside "
      "“Return on the requirement”.")
copy_range(a, b, figs=[11, 12])

# ── PART 3: scattered sentences ──────────────────────────────────────────
P("3  Sentences elsewhere that carry the old figures", 15, True, color=DEEP, after=4).paragraph_format.page_break_before = True
P("Each of these sits outside the financial section but quotes a number the ₱500,000 "
  "change moves. Find the old wording, replace it with the new.", 10, color=GREY, after=10)
SWAPS = [
 ("Evidence from initial testing, last sentence of the classification paragraph",
  "clinical validation carries ₱51,000 of the requested funding",
  "clinical validation carries ₱120,000 of the requested funding, the largest single category,"),
 ("Current state and development priority",
  "supported by ₱64,000 of AI development",
  "supported by ₱102,000 of AI development"),
 ("Value proposition, “What Resondi does not yet do”",
  "₱64,000 of AI development and ₱42,000 of hardware refinement",
  "₱102,000 of AI development and ₱42,000 of hardware refinement"),
 ("Business model, paragraph beginning “The lower blocks tie directly…”",
  "The ₱300,000 seed divides into eight categories",
  "The ₱500,000 seed divides into ten categories"),
 ("Table 10, CEO row",
  "investor reporting against the ₱300,000 recovery schedule",
  "investor reporting against the ₱500,000 recovery schedule"),
 ("Continuity and governance",
  "the ₱300,000 is received by a company registered with the Securities and Exchange Commission",
  "the ₱500,000 is received by a company registered with the Securities and Exchange Commission"),
]
t = doc.add_table(rows=len(SWAPS) + 1, cols=3); t.style = "Table Grid"
for j, h in enumerate(("Where", "Old wording", "New wording")):
    c = t.rows[0].cells[j]; c.text = ""; shade(c, HEAD)
    r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(9.5); r.font.color.rgb = INK
for i, row in enumerate(SWAPS, 1):
    for j, txt in enumerate(row):
        c = t.rows[i].cells[j]; c.text = ""
        r = c.paragraphs[0].add_run(txt); r.font.size = Pt(9.5)
        r.font.color.rgb = GREY if j == 1 else INK
        r.font.strike = j == 1; r.bold = j == 2
for row in t.rows:
    row.cells[0].width, row.cells[1].width, row.cells[2].width = Inches(1.9), Inches(2.4), Inches(2.4)

# ── PART 4: canvas text ──
P("4  Business model canvas — block text", 15, True, color=DEEP, after=4).paragraph_format.page_break_before = True
P("4a is exactly what Figure 8 shows: short enough to stay readable on one landscape page. "
  "4b is the full wording from before, which still belongs in the narrative sections and is "
  "useful if your own canvas has more room. Title: “Business Model Canvas — Resondi”. "
  "Subtitle: “All monetary figures derive from the ₱500,000 financial requirement.”",
  10, color=GREY, after=10)
ORDER = ["Key Partners", "Key Activities", "Key Resources", "Value Propositions",
         "Customer Relationships", "Channels", "Customer Segments",
         "Cost Structure", "Revenue Streams"]
def blocks(B, title):
    h = P(title, 12.5, True, color=DEEP, before=8, after=4)
    if title.startswith("4b"): h.paragraph_format.page_break_before = True
    for name in ORDER:
        p = P(after=3, before=7)
        r = p.add_run(name.upper()); r.bold = True; r.font.size = Pt(11); r.font.color.rgb = PRIMARY
        for item in B[name]:
            q = P(after=3, indent=0.25)
            q.paragraph_format.first_line_indent = Inches(-0.17)
            r = q.add_run("•  " + item); r.font.size = Pt(10.5); r.font.color.rgb = INK
dk = open(os.path.join(_ROOT, "build", "deckfigs", "build.py"), encoding="utf-8").read()
ns1 = {}; exec(dk[dk.index("CANVAS = {"):dk.index("def fig8():")], ns1)
blocks(ns1["CANVAS"], "4a  Condensed — as drawn in Figure 8")
srcpy = open(os.path.join(_ROOT, "build", "fig", "fig6_canvas.py"), encoding="utf-8").read()
ns = {}; exec(srcpy[srcpy.index("BLOCKS = {"):srcpy.index("# ── layout")], ns)
KEEP_BREAK = True
blocks(ns["BLOCKS"], "4b  Full wording")

# ── PART 5: statistics revisions from the previous round ────────────────
P("5  Statistics revisions (from the previous round)", 15, True, color=DEEP, after=4).paragraph_format.page_break_before = True
P("Already in the master concept note, repeated here so a manual paste is complete. These "
  "carry the updated PSA mortality figures, the confidence interval, the marginal-homogeneity clause, "
  "and the signal-strength wording.", 10, color=GREY, after=10)
where("BACKGROUND OF THE PROBLEM, first paragraph. Replace the whole paragraph.")
a = find("Respiratory and cardiovascular conditions require repeated")
copy_range(a, a + 1)
where("MARKET ANALYSIS, \u201cDemand\u201d, first paragraph. Replace the whole paragraph.")
a = find("Respiratory and cardiovascular disease together account")
copy_range(a, a + 1)
where("\u201cEvidence from initial testing\u201d. These two paragraphs replace the section\u2019s "
      "two existing paragraphs. Red text marks the two numbers only you have.")
a = find("The prototype has been built and measured")
b = find("Current state and development priority")
copy_range(a, b)
where("REFERENCES. Replace the Philippine Statistics Authority entry.")
a = find("Philippine Statistics Authority. (2026")
copy_range(a, a + 1)

doc.save(OUT)
print("pack written:", OUT)
