"""Build the Resondi pitch script .docx.

Default source is script5/pitch_4m30.txt, the 4:30 pitch for the 3-5 minute PSC
limit, which also feeds the deck's speaker notes (deck_fix/fix_deck.py).
Usage:  python build_script.py [source.txt] [output.docx]
"""
import re
import sys
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

_HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else _HERE.parent / "script5" / "pitch_4m30.txt"
OUT = (Path(sys.argv[2]) if len(sys.argv) > 2
       else _HERE.parent.parent / "deliverables" / "Resondi-Pitch-Script.docx")

FONT = "Calibri"
INK = RGBColor(0x1A, 0x1A, 0x1A)
GREY = RGBColor(0x60, 0x60, 0x60)
ROSE = RGBColor(0x8E, 0x2A, 0x52)
SPEAK = {"A": "Ahnycca", "H": "Hared", "J": "Jarred", "ALL": "ALL"}

doc = Document()
s = doc.styles["Normal"]
s.font.name = FONT
s.font.size = Pt(11)
s.font.color.rgb = INK
s.paragraph_format.space_after = Pt(4)
s.paragraph_format.line_spacing = 1.15
for sec in doc.sections:
    sec.top_margin = sec.bottom_margin = Inches(0.75)
    sec.left_margin = sec.right_margin = Inches(0.9)


def shade_para(p, fill):
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), fill)
    pPr.append(shd)


lines = SRC.read_text(encoding="utf-8").split("\n")

# ── preamble: everything before the first [m:ss-m:ss] marker ────────────
i = 0
while i < len(lines) and not re.match(r"^\[\d+:\d{2}", lines[i]):
    i += 1
head, body = lines[:i], lines[i:]

title = head[0].strip() if head else "RESONDI PITCH SCRIPT"
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(2)
r = p.add_run(title)
r.font.size = Pt(17)
r.bold = True
r.font.color.rgb = ROSE

for ln in head[1:]:
    ln = ln.strip()
    if not ln:
        continue
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(ln)
    r.font.size = Pt(9.5)
    r.italic = True
    r.font.color.rgb = GREY

doc.add_paragraph().paragraph_format.space_after = Pt(6)

# ── body ────────────────────────────────────────────────────────────────
for ln in body:
    raw = ln.rstrip()
    if not raw.strip():
        continue

    # section header  [0:00-0:25] HOOK
    m = re.match(r"^\[(\d+:\d{2}[^\]]*)\]\s*(.*)$", raw)
    if m and m.group(2) and m.group(2).isupper():
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(13)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(f"{m.group(1)}   {m.group(2)}")
        r.font.size = Pt(12)
        r.bold = True
        r.font.color.rgb = ROSE
        continue

    # slide cue
    if raw.startswith("SLIDE"):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.15)
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(2)
        shade_para(p, "F2F2F2")
        r = p.add_run(raw)
        r.font.size = Pt(9.5)
        r.bold = True
        r.font.color.rgb = GREY
        continue

    # stage direction
    if raw.lstrip().startswith("["):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.15)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(raw.strip())
        r.font.size = Pt(9.5)
        r.italic = True
        r.font.color.rgb = GREY
        continue

    # speaker line
    sm = re.match(r"^(ALL|[AHJ]):\s*(.*)$", raw.strip())
    if sm:
        who, said = sm.group(1), sm.group(2)
        cut = "<<CUT IF LONG>>" in said
        said = said.replace("<<CUT IF LONG>>", "").rstrip()
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.55)
        p.paragraph_format.first_line_indent = Inches(-0.55)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(f"{who}: ")
        r.bold = True
        r.font.size = Pt(11)
        r.font.color.rgb = ROSE if who == "ALL" else INK
        for part in re.split(r"(\[[^\]]*\])", said):
            if not part:
                continue
            r = p.add_run(part)
            r.font.size = Pt(11)
            if part.startswith("["):
                r.italic = True
                r.font.color.rgb = GREY
        if cut:
            r = p.add_run("   ✂ CUT IF LONG")
            r.font.size = Pt(8.5)
            r.bold = True
            r.font.color.rgb = GREY
        continue

    p = doc.add_paragraph()
    p.add_run(raw.strip()).font.size = Pt(11)

doc.save(OUT)

spoken = [l for l in lines if re.match(r"^(ALL|[AHJ]):", l.strip())]
words = sum(len(re.sub(r"\[.*?\]", "", l.split(":", 1)[1]).split()) for l in spoken)
print(f"saved {OUT}")
print(f"  {len(spoken)} spoken lines, {words:,} words, "
      f"{int(words / 150)}m{int(words / 150 % 1 * 60):02d}s at 150 wpm")
