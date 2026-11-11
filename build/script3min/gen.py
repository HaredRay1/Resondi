"""Build final/18-Resondi-Pitch-Script-3min.docx from the markdown script beside it (rose theme)."""
import os, re
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "final", "18-Resondi-Pitch-Script-3min.md")
OUT = os.path.join(ROOT, "final", "18-Resondi-Pitch-Script-3min.docx")
ROSE, PLUM, GREY = RGBColor(0xE9, 0x1E, 0x76), RGBColor(0x8E, 0x2A, 0x52), RGBColor(0x9E, 0x88, 0x92)

doc = Document()
for s in doc.sections:
    s.left_margin = s.right_margin = Cm(2.2)
    s.top_margin = s.bottom_margin = Cm(2)
st = doc.styles["Normal"]
st.font.name, st.font.size = "Poppins", Pt(11)
st.element.rPr.rFonts.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia", "Poppins")


def runs(p, text, size=None, color=None):
    """Add text with **bold** and *italic* markup."""
    for part in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", text):
        if not part:
            continue
        if part.startswith("**"):
            r = p.add_run(part[2:-2]); r.bold = True
        elif part.startswith("*"):
            r = p.add_run(part[1:-1]); r.italic = True
        else:
            r = p.add_run(part)
        if size: r.font.size = Pt(size)
        if color: r.font.color.rgb = color
    return p


lines = open(SRC, encoding="utf-8").read().splitlines()
i = 0
while i < len(lines):
    ln = lines[i].rstrip()
    if ln.startswith("# "):
        p = doc.add_paragraph(); r = p.add_run(ln[2:]); r.bold = True; r.font.size = Pt(22); r.font.color.rgb = PLUM
    elif ln.startswith("**[") :
        m = re.match(r"\*\*\[(.+?)\]\*\*\s*\*\((.+?)\)\*", ln)
        p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(12); p.paragraph_format.space_after = Pt(2)
        lab = m.group(1)
        lab = ("SLIDES " if re.match(r"[\d–, ]*[–,]", lab.split(" · ")[0]) else "SLIDE ") + lab.upper()
        r = p.add_run(lab); r.bold = True; r.font.size = Pt(10); r.font.color.rgb = ROSE
        r = p.add_run("   " + m.group(2)); r.font.size = Pt(10); r.font.color.rgb = GREY
        i += 1
        body = lines[i].strip()
        p = doc.add_paragraph(); p.paragraph_format.line_spacing = 1.5
        for k, seg in enumerate(body.split(" / ")):
            r = p.add_run(seg + (" /  " if k < len(body.split(" / ")) - 1 else "")); r.font.size = Pt(13)
    elif ln.strip() == "---":
        p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(6)
    elif re.match(r"^\d+\. ", ln):
        runs(doc.add_paragraph(style="List Number"), re.sub(r"^\d+\. ", "", ln))
    elif ln.startswith("- "):
        runs(doc.add_paragraph(style="List Bullet"), ln[2:])
    elif ln.strip():
        p = runs(doc.add_paragraph(), ln)
        if ln.startswith("*(") and ln.endswith(")*"):
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    i += 1

doc.save(OUT)
print("wrote", OUT)
