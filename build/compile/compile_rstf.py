"""Compile Ahnycca's fair submission into one PDF, in the order of the example compilation (MCS-I-RSTF7b.pdf):

    front                    title page and DepEd checklist of forms (build/compile/front_matter.py)
    I.   Research Plan      Ahnyccas papers/Resondi-Research-Plan-Heart-and-Lung-FINAL.pdf
    II.  ISEF Forms          the team's signed ISEF-Forms-2027 PDF: the user's newer copy of 14 Nov 2026 (consent
                             forms updated to cardiopulmonary); the older Drive copy is kept as -drive-older.pdf.
                             After Form 7 (continuation project): the previous year's paper, SmartSteth (2025),
                             which Form 7 lists as attached (build/compile/prior_project.py)
    III. ISEF Abstract       generated here: ISEF Abstract & Certification layout, abstract from the IMRaD
    IV.  Research Paper      title page, table of contents, Ahnyccas papers/Resondi-IMRaD-Heart-and-Lung-FINAL.pdf
    V.   Project Data Book   the scanned logbook (13 pages, CamScanner, supplied 15 Nov 2026)
    VI.  SRC Evaluation      the signed Review and Recommendation Form (Drive, 5 Nov 2026)

Each part opens with a divider page, as in the example, and the PDF has bookmarks.
The ISEF forms carry phone numbers and e-mail addresses: the downloaded sources live in
Downloads\\Resondi-private\\compile-sources\\, and the compiled PDF, which the user wants in Ahnyccas papers,
is listed in .gitignore so it never reaches GitHub. It does reach the link-shared Drive folder when Drive syncs.

    python build/compile/compile_rstf.py
"""
import os

import docx
import pymupdf as fitz

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PAPERS = os.path.join(ROOT, "Ahnyccas papers")
PRIV = os.path.normpath(os.path.join(ROOT, "..", "Resondi-private"))
SRC = os.path.join(PRIV, "compile-sources")
# The user asked (14 Nov) for the compiled document in Ahnyccas papers. It contains the ISEF forms' phone
# numbers and e-mail addresses, so it is kept out of git (.gitignore); the sources stay in Resondi-private.
OUTDIR = PAPERS
OUT = os.path.join(OUTDIR, "Resondi-Compiled-RSTF-FINAL.pdf")

PLAN = os.path.join(PAPERS, "Resondi-Research-Plan-Heart-and-Lung-FINAL.pdf")
IMRAD = os.path.join(PAPERS, "Resondi-IMRaD-Heart-and-Lung-FINAL.pdf")
IMRAD_DOCX = os.path.join(PAPERS, "Resondi-IMRaD-Heart-and-Lung-FINAL.docx")
ISEF = os.path.join(SRC, "ISEF-Forms-2027.pdf")
REVIEW = os.path.join(SRC, "Review-and-Recommendation-Form-RIM-I-signed.pdf")
AI_DISCLOSURE = os.path.join(ROOT, "papers-support", "Resondi-AI-Usage-Disclosure-2026-11-14.pdf")
LOGBOOK = os.path.join(SRC, "Logbook-scan-2026-11-15.pdf")  # the team's scanned logbook (user, 15 Nov)
PRIOR = os.path.join(SRC, "SmartSteth-FINAL-compile.pdf")  # Form 7 attachment, from build/compile/prior_project.py

W, H = 612, 792  # US Letter, like the example's divider pages

TITLE = ("Resondi: An IoT-Based AI-Assisted Auscultation Instrument for Cardiopulmonary Monitoring, "
         "Longitudinal Tracking, and Rehabilitation-Support System")  # as registered on the signed ISEF forms
FRONT = os.path.join(ROOT, "papers-support", "Resondi-Title-Page-and-Contents-FINAL.pdf")  # title page, checklist, contents
STUDENT = "Malimban, Ahnycca Krish N."
SCHOOL = "Puerto Princesa City National Science High School, Palawan, Philippines"


def imrad_abstract():
    d = docx.Document(IMRAD_DOCX)
    ps = [p.text.strip() for p in d.paragraphs]
    i = ps.index("ABSTRACT")
    return ps[i + 1]


def divider(doc, text):
    p = doc.new_page(width=W, height=H)
    r = fitz.Rect(40, H / 2 - 30, W - 40, H / 2 + 30)
    p.insert_textbox(r, text, fontname="tibo", fontsize=26, align=fitz.TEXT_ALIGN_CENTER)
    return p


def box(p, x, y, s=9, mark=False):
    r = fitz.Rect(x, y, x + s, y + s)
    p.draw_rect(r, color=(0, 0, 0), width=0.7)
    if mark:
        p.draw_line(r.tl + (1.6, 1.6), r.br - (1.6, 1.6), color=(0, 0, 0), width=1.1)
        p.draw_line(fitz.Point(r.x1 - 1.6, r.y0 + 1.6), fitz.Point(r.x0 + 1.6, r.y1 - 1.6), color=(0, 0, 0), width=1.1)


def fit_text(p, rect, text, font="helv", start=9.5, minimum=6.5, align=fitz.TEXT_ALIGN_JUSTIFY):
    size = start
    while size >= minimum:
        rc = p.insert_textbox(rect, text, fontname=font, fontsize=size, align=align, render_mode=3)  # dry run
        if rc >= 0:
            p.insert_textbox(rect, text, fontname=font, fontsize=size, align=align)
            return size
        size -= 0.25
    raise SystemExit("abstract does not fit the box")


CATEGORIES = ["Animal Sciences", "Behavioral & Social Sciences", "Biochemistry", "Biomedical & Health Sciences",
              "Biomedical Engineering", "Cellular & Molecular Biology", "Chemistry",
              "Computational Biology and Bioinformatics", "Earth & Environmental Sciences", "Embedded Systems",
              "Energy: Sustainable Materials and Design", "Engineering Technology: Statics and Dynamics",
              "Environmental Engineering", "Materials Science", "Mathematics", "Microbiology",
              "Physics and Astronomy", "Plant Sciences", "Robotics & Intelligent Machines", "Software Design",
              "Technology Enhances the Arts", "Translational Medical Science"]
# The fair division ticked on the team's review form (5 Nov 2026) is Robotics and Intelligent Machines.
CATEGORY = "Robotics & Intelligent Machines"


def tb(p, rect, text, **kw):
    """insert_textbox that refuses to fail silently (it draws nothing when the text does not fit)."""
    rc = p.insert_textbox(rect, text, **kw)
    if rc < 0:
        raise SystemExit(f"text does not fit {rect}: {text[:40]!r}")
    return rc


def abstract_page(doc, abstract):
    p = doc.new_page(width=W, height=H)
    tb(p, fitz.Rect(36, 22, W - 36, 44), "ISEF Sample Abstract & Certification", fontname="hebo",
       fontsize=12, align=fitz.TEXT_ALIGN_CENTER)
    left = fitz.Rect(36, 52, 452, 420)
    p.draw_rect(left, color=(0, 0, 0), width=0.8)
    y = left.y0 + 6
    tb(p, fitz.Rect(left.x0 + 6, y, left.x1 - 6, y + 40), TITLE, fontname="hebo", fontsize=10)
    y += 42
    p.insert_text((left.x0 + 6, y + 8), STUDENT, fontname="helv", fontsize=9.5)
    p.insert_text((left.x0 + 6, y + 22), SCHOOL, fontname="helv", fontsize=9.5)
    y += 30
    p.draw_line(fitz.Point(left.x0, y), fitz.Point(left.x1, y), color=(0, 0, 0), width=0.6)
    size = fit_text(p, fitz.Rect(left.x0 + 6, y + 5, left.x1 - 6, left.y1 - 4), abstract)

    # category column
    cx = 462
    p.insert_text((cx, 62), "Category", fontname="hebo", fontsize=10)
    for k, line in enumerate(["Pick one only -", "Mark an \"X\"", "in box at right"]):
        p.insert_text((cx, 74 + 9 * k), line, fontname="helv", fontsize=7.5)
    cy = 106
    for c in CATEGORIES:
        # wrap long names onto two lines at a word boundary
        words, lines, cur = c.split(), [], ""
        for w_ in words:
            if fitz.get_text_length(cur + " " + w_ if cur else w_, fontname="helv", fontsize=6.8) > 96:
                lines.append(cur); cur = w_
            else:
                cur = cur + " " + w_ if cur else w_
        lines.append(cur)
        for k, line in enumerate(lines):
            p.insert_text((cx, cy + 6.5 + 8 * k), line, fontname="helv", fontsize=6.8)
        box(p, W - 46, cy, 7.5, mark=(c == CATEGORY))
        cy += 8 * len(lines) + 5

    # certification questions
    qy = 432
    qs = [
        ("1.  As a part of this research project, the student directly handled, manipulated, or interacted with "
         "(check all that apply):", None),
        ("2.  This abstract describes only procedures performed by me/us, reflects my/our own independent research, "
         "and represents one year's work only.", "yn:"),
        ("3.  I/We worked or used equipment in a regulated research institution or industrial setting.", "yn:no"),
        ("4.  This project is a continuation of previous research.", "yn:yes"),
        ("5.  My display board includes non-published photographs/visual depictions of humans (other than myself).",
         "yn:"),
        ("6.  I/We hereby certify that the abstract and responses to the above statements are correct and properly "
         "reflect my/our own work.", "yn:"),
    ]
    for text, kind in qs:
        tb(p, fitz.Rect(36, qy, W - 130, qy + 30), text, fontname="helv", fontsize=9)
        qy += 28
        if kind is None:  # question 1: human participants, from the signed Human Participants Form (4)
            items = [("human participants", True), ("potentially hazardous biological agents", False),
                     ("vertebrate animals", False), ("microorganisms", False), ("rDNA", False), ("tissue", False)]
            xs = [54, 230, 54, 230, 340, 400]
            ys = [qy, qy, qy + 14, qy + 14, qy + 14, qy + 14]
            for (lab, m), x, yy in zip(items, xs, ys):
                box(p, x, yy, 9, m)
                p.insert_text((x + 14, yy + 8), lab, fontname="helv", fontsize=9)
            qy += 34
        else:
            ans = kind.split(":")[1]
            box(p, 54, qy, 9, ans == "yes"); p.insert_text((68, qy + 8), "yes", fontname="helv", fontsize=9)
            box(p, 110, qy, 9, ans == "no"); p.insert_text((124, qy + 8), "no", fontname="helv", fontsize=9)
            qy += 20
    off = fitz.Rect(W - 120, 650, W - 40, 710)
    p.draw_rect(off, color=(0, 0, 0), width=0.6)
    tb(p, off + (4, 14, -4, -4), "FOR ISEF\nOFFICIAL USE\nONLY", fontname="helv", fontsize=7,
       align=fitz.TEXT_ALIGN_CENTER)
    p.insert_text((36, H - 26), "International Rules: Guidelines for Science and Engineering Fairs 2026-2027, "
                  "societyforscience.org/ISEF", fontname="helv", fontsize=7)
    return size


def logbook_placeholder(doc):
    p = doc.new_page(width=W, height=H)
    p.insert_textbox(fitz.Rect(72, 300, W - 72, 330), "Project Data Book (Research Logbook)", fontname="tibo",
                     fontsize=16, align=fitz.TEXT_ALIGN_CENTER)
    p.insert_textbox(fitz.Rect(90, 340, W - 90, 420),
                     "The logbook is not in the shared folders. Scan its pages and insert them after this page; "
                     "the start and end dates must match the Student Checklist (1A): 17 July 2026 to 20 August "
                     "2026.", fontname="tiro", fontsize=11, align=fitz.TEXT_ALIGN_CENTER)


def main():
    for f in (PLAN, IMRAD, IMRAD_DOCX, ISEF, REVIEW, AI_DISCLOSURE, FRONT, PRIOR, LOGBOOK):
        if not os.path.exists(f):
            raise SystemExit(f"missing source: {f}")
    os.makedirs(OUTDIR, exist_ok=True)
    out = fitz.open()
    toc = []

    def add_section(label, title):
        divider(out, label)
        toc.append([1, title, out.page_count])

    def insert(path):
        src = fitz.open(path)
        out.insert_pdf(src)
        return src.page_count

    # Front matter, as in the example compilation: the title page and the DepEd checklist of forms.
    front = fitz.open(FRONT)
    out.insert_pdf(front, from_page=0, to_page=1)
    toc.append([1, "Title page", 1])
    toc.append([1, "Checklist of forms required", 2])

    add_section("I. RESEARCH PLAN", "I. Research Plan")
    insert(PLAN)
    add_section("II. ISEF FORMS", "II. ISEF Forms")
    # The signed forms, with the 29 Aug 2026 AI-disclosure attachment (pages after Form 2A) replaced by the
    # updated disclosure of 14 Nov 2026. The signed form pages themselves are not touched.
    isef = fitz.open(ISEF)
    texts = [" ".join(pg.get_text().split()) for pg in isef]
    a = next(i for i, t in enumerate(texts) if t.startswith("AI Usage Disclosure"))
    b = next(i for i, t in enumerate(texts) if "These were found and fixed during the session" in t)
    assert a < b and "Qualified Scientist" not in texts[b], (a, b)
    out.insert_pdf(isef, from_page=0, to_page=a - 1)
    out.insert_pdf(fitz.open(AI_DISCLOSURE))
    # Form 7 (Continuation/Research Progression Projects) is followed by the previous year's paper it lists as attached.
    f7 = [i for i, t in enumerate(texts) if "Projects Form (7)" in t and "Additional changes" in t]
    assert len(f7) == 1 and f7[0] > b, f7
    f7 = f7[0]
    out.insert_pdf(isef, from_page=b + 1, to_page=f7)
    toc.append([2, "Form 7 attachment: previous project, SmartSteth (2025)", out.page_count + 1])
    n_prior = insert(PRIOR)
    if f7 + 1 < isef.page_count:
        out.insert_pdf(isef, from_page=f7 + 1, to_page=isef.page_count - 1)
    print(f"  ISEF forms: replaced old AI disclosure pages {a + 1}-{b + 1} with the 14 Nov update; "
          f"SmartSteth ({n_prior} pages) after Form 7 (forms page {f7 + 1})")
    add_section("III. ISEF ABSTRACT", "III. ISEF Abstract")
    size = abstract_page(out, imrad_abstract())
    add_section("IV. RESEARCH PAPER", "IV. Research Paper (IMRaD)")
    out.insert_pdf(front, from_page=0, to_page=0)   # the paper's title page
    out.insert_pdf(front, from_page=2, to_page=2)   # its table of contents (IMRaD page numbers)
    insert(IMRAD)
    add_section("V. PROJECT DATA BOOK", "V. Project Data Book (Logbook)")
    insert(LOGBOOK)
    add_section("VI. SRC EVALUATION", "VI. SRC Evaluation")
    insert(REVIEW)

    out.set_toc(toc)
    out.set_metadata({"title": "Resondi: research plan, ISEF forms (with the Form 7 attachment), abstract, research "
                               "paper, logbook, SRC evaluation",
                      "author": "Ahnycca Krish N. Malimban"})
    out.save(OUT, garbage=3, deflate=True)
    print(f"wrote {OUT}: {out.page_count} pages; abstract font {size:.2f} pt")
    for lvl, t, pg in toc:
        print(f"  p.{pg:>3}  {'   ' * (lvl - 1)}{t}")


if __name__ == "__main__":
    main()
