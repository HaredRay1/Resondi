"""Front matter for the compiled submission: title page, DepEd checklist of forms, table of contents.

Source: the team's draft "edit pa title page na orange ... may error sa table of contents" (14 Nov 2026), kept
privately as Downloads\\Resondi-private\\compile-sources\\front-matter-draft.pdf.
  - Title page: rebuilt in the same layout (A4, Times 12 pt, the orange RIM-I-RSTF7b tag) with the title corrected
    to the one registered on the signed ISEF forms ("AI-Assissted" -> "AI-Assisted", "IOT" -> "IoT",
    "Rehabilitation Support-System" -> "Rehabilitation-Support System").
  - Checklist of forms required: the team's page, unchanged.
  - Table of contents: generated from the FINAL IMRaD PDF's own headings and printed page numbers, replacing the
    draft's (wrong section names, mixed font sizes, "TABLE OF CONTENT").

    python build/compile/front_matter.py   -> Ahnyccas papers/Resondi-Title-Page-and-Contents-FINAL.pdf
"""
import os

import pymupdf as fitz

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PAPERS = os.path.join(ROOT, "Ahnyccas papers")
DRAFT = os.path.normpath(os.path.join(ROOT, "..", "Resondi-private", "compile-sources", "front-matter-draft.pdf"))
IMRAD = os.path.join(PAPERS, "Resondi-IMRaD-Heart-and-Lung-FINAL.pdf")
OUT = os.path.join(PAPERS, "Resondi-Title-Page-and-Contents-FINAL.pdf")

W, H = 595.3, 841.9  # A4, as the draft
ORANGE = (0.922, 0.482, 0.184)
TITLE = ("Resondi: An IoT-Based AI-Assisted Auscultation Instrument for Cardiopulmonary Monitoring, "
         "Longitudinal Tracking, and Rehabilitation-Support System")
CODE = "RIM-I-RSTF7b"

# (text, bold, gap before in points) — the draft's lines, in order, with its vertical rhythm.
BLOCKS = [
    (["A Science Investigatory Project Presented as an Entry to the", "Regional Science and Technology Fair",
      "Department of Education"], False, 40),
    (["Robotics and Intelligent Machines", "Individual Category", "Biomedical Engineering",
      "Sensor and Imaging - Devices"], True, 26),
    (["Proponent:"], False, 26),
    (["Ahnycca Krish N. Malimban"], True, 14),
    (["Researcher"], False, 2),
    (["John Lemuel J. Noche", "Genelyn O. Bautista"], True, 56),
    (["Research Advisers"], False, 2),
    (["Bemsor T. Caabay, MSc"], True, 56),
    (["Qualified Scientist"], False, 2),
    (["Kenneth Wilson O. Lim, MD, FPCP, FPCCP", "Sonia A. Ulanday, MD, FPPS, FPAPP",
      "Riza Cornelle C. De La Bajan, MD, FPPS"], True, 56),
    (["Consultants"], False, 2),
    (["Puerto Princesa City National Science High School", "Senior High School Department"], True, 28),
    (["Puerto Princesa City"], False, 2),
]
LINE = 15.6


def centred(p, y, text, bold):
    font = "tibo" if bold else "tiro"
    w = fitz.get_text_length(text, fontname=font, fontsize=12)
    p.insert_text(((W - w) / 2, y), text, fontname=font, fontsize=12)


def wrap(text, font, size, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if fitz.get_text_length(trial, fontname=font, fontsize=size) > width:
            lines.append(cur); cur = w
        else:
            cur = trial
    lines.append(cur)
    return lines


def title_page(doc):
    p = doc.new_page(width=W, height=H)
    tag = fitz.Rect(426.2, 9.65, W, 45.75)
    p.draw_rect(tag, color=None, fill=ORANGE, radius=0.25)
    tw = fitz.get_text_length(CODE, fontname="hebo", fontsize=20)
    p.insert_text((tag.x0 + (tag.width - tw) / 2, tag.y1 - 11), CODE, fontname="hebo", fontsize=20, color=(1, 1, 1))
    y = 74
    for line in wrap(TITLE, "tibo", 12, 420):
        centred(p, y, line, True); y += LINE
    for lines, bold, gap in BLOCKS:
        y += gap
        for line in lines:
            centred(p, y, line, bold); y += LINE
    assert y < H - 40, y


def imrad_headings():
    """(entry, level, printed page) for the IMRaD's main sections, read from the FINAL PDF."""
    d = fitz.open(IMRAD)
    wanted = [("ABSTRACT", 0), ("INTRODUCTION", 0), ("The Research Gap", 1), ("Objectives of the Study", 1),
              ("Scope and Delimitation", 1), ("METHODOLOGY", 0), ("RESULTS", 0), ("DISCUSSION", 0),
              ("Limitations", 1), ("Conclusion", 1), ("Recommendations", 1), ("REFERENCES", 0)]
    out, start = [], 0
    for name, lvl in wanted:
        for i in range(start, len(d)):
            lines = [s.strip() for s in d[i].get_text().splitlines()]
            if name in lines:
                printed = next((s for s in reversed(lines) if s.isdigit()), None)
                assert printed == str(i + 1), (name, i + 1, printed)  # the footer number matches the PDF page
                out.append((name.title() if lvl == 0 else name, lvl, i + 1))
                start = i
                break
        else:
            raise SystemExit(f"heading not found in the IMRaD: {name}")
    return out


def contents_page(doc):
    p = doc.new_page(width=W, height=H)
    head = "TABLE OF CONTENTS"
    hw = fitz.get_text_length(head, fontname="tibo", fontsize=12)
    p.insert_text(((W - hw) / 2, 92), head, fontname="tibo", fontsize=12)
    x0, x1 = 72, W - 72
    p.draw_line(fitz.Point(x0, 102), fitz.Point(x1, 102), width=0.6)
    y = 132
    for name, lvl, page in imrad_headings():
        text = name.upper() if lvl == 0 else name
        font = "tibo" if lvl == 0 else "tiro"
        x = x0 + (22 if lvl else 0)
        num = str(page)
        nw = fitz.get_text_length(num, fontname="tiro", fontsize=12)
        tw = fitz.get_text_length(text, fontname=font, fontsize=12)
        p.insert_text((x, y), text, fontname=font, fontsize=12)
        p.insert_text((x1 - nw, y), num, fontname="tiro", fontsize=12)
        dot_w = fitz.get_text_length(".", fontname="tiro", fontsize=12)
        n = int((x1 - nw - 6 - (x + tw + 6)) / dot_w)
        p.insert_text((x + tw + 4, y), "." * max(n, 0), fontname="tiro", fontsize=12)
        y += 26 if lvl == 0 else 22
    p.draw_line(fitz.Point(x0, y - 8), fitz.Point(x1, y - 8), width=0.6)
    return p


def main():
    draft = fitz.open(DRAFT)
    assert "CHECKLIST OF FORMS REQUIRED" in draft[1].get_text()
    out = fitz.open()
    title_page(out)
    out.insert_pdf(draft, from_page=1, to_page=1)   # the team's checklist, unchanged
    contents_page(out)
    out.set_toc([[1, "Title page", 1], [1, "Checklist of forms required", 2], [1, "Table of contents", 3]])
    out.save(OUT, garbage=3, deflate=True)
    print("wrote", OUT)
    for name, lvl, page in imrad_headings():
        print(f"  {'   ' * lvl}{name} .... {page}")


if __name__ == "__main__":
    main()
