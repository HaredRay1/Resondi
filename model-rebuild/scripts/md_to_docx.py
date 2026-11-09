"""Turn a docs/*.md file into a .docx (headings, paragraphs, lists, tables, code blocks, **bold**).

    python scripts/md_to_docx.py docs/LOCAL-DATASET-INTEGRATION.md
"""
import re
import sys

from docx import Document
from docx.shared import Pt, RGBColor

ROSE = RGBColor(0x8E, 0x2A, 0x52)


def runs(p, text, size=10.5, font=None):
    for part in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", text):
        if not part:
            continue
        bold, code = part.startswith("**"), part.startswith("`")
        r = p.add_run(part.strip("*`") if (bold or code) else part)
        r.bold = bold
        r.font.size = Pt(size)
        if code or font:
            r.font.name = "Consolas"


def main(src):
    lines = open(src, encoding="utf-8").read().splitlines()
    d = Document()
    d.styles["Normal"].font.name = "Calibri"
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            j = i + 1
            while not lines[j].startswith("```"):
                j += 1
            p = d.add_paragraph()
            runs(p, "\n".join(lines[i + 1:j]), 9, font="code")
            i = j + 1
            continue
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip("|").split("|")]
                if not all(set(c) <= set("-: ") for c in cells):
                    rows.append(cells)
                i += 1
            t = d.add_table(rows=len(rows), cols=len(rows[0]))
            t.style = "Table Grid"
            for a, row in enumerate(rows):
                for b, c in enumerate(row):
                    p = t.cell(a, b).paragraphs[0]
                    runs(p, f"**{c}**" if a == 0 and c else c, 9.5)
            d.add_paragraph()
            continue
        m = re.match(r"^(#{1,3}) (.*)", ln)
        if m:
            p = d.add_paragraph()
            r = p.add_run(m.group(2))
            r.bold, r.font.size, r.font.color.rgb = True, Pt({1: 17, 2: 13.5, 3: 11.5}[len(m.group(1))]), ROSE
        elif re.match(r"^\s*([-*]|\d+\.) ", ln):
            num = re.match(r"^\s*\d+\.", ln)
            p = d.add_paragraph(style="List Number" if num else "List Bullet")
            runs(p, re.sub(r"^\s*([-*]|\d+\.) ", "", ln))
        elif ln.strip() and ln.strip() != "---":
            runs(d.add_paragraph(), ln)
        i += 1
    out = src[:-3] + ".docx"
    d.save(out)
    print("saved", out)


if __name__ == "__main__":
    main(sys.argv[1])
