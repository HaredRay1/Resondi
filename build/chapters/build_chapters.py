"""Build revised copies of Chapters 1-3 and the revision log.

Input:  chapters/original/AUSCULTA Chapt-N.docx (untouched downloads)
Output: chapters/Resondi-Chapter-N-Revised.docx, chapters/Resondi-Chapters-1-3-Revision-Log.docx
"""
import os
import re
import sys
import textwrap
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.oxml.ns import qn
from docx.enum.section import WD_ORIENT

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from engine import Chapter
import ch1, ch2, ch3

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "chapters", "original")
OUT = os.path.join(ROOT, "chapters")
PARADIGM = os.path.join(ROOT, "figures", "Resondi-Research-Paradigm.png")

COLS = [
    ("Input", ["1. Specifications of the Resondi device and platform",
               "2. Respiratory sound recordings: ICBHI 2017 reference dataset and Resondi recordings at seven standardized sites",
               "3. Recording quality indicators: signal strength, clarity ratings, ambient noise in three environments",
               "4. System response times across connection, recording, quality assessment, preprocessing, classification",
               "5. Classification outputs (normal, wheezing, crackles, both) and reference labels on 15 recordings",
               "6. End-user acceptance ratings from 27 respondents"]),
    ("Process", ["1. Design and development of the smart stethoscope and platform",
                 "2. Audio preprocessing: resampling, noise reduction, normalization, segmentation, MFCC extraction",
                 "3. CNN training and classification of respiratory sound patterns",
                 "4. Descriptive analysis of specifications",
                 "5. Statistics: mean, SD, weighted mean, Cronbach's alpha, 95% Wilson interval, exact binomial test against 25% chance at the 0.05 level",
                 "6. Interpretation against the five-point Likert acceptance scale"]),
    ("Output", ["1. A developed and documented Resondi smart stethoscope and platform with guided auscultation at seven sites",
                "2. Determined recording quality and system response times",
                "3. Established agreement between classifications and reference labels",
                "4. Signal strength relative to a conventional stethoscope",
                "5. Assessed level of end-user acceptance"]),
]


def draw_paradigm():
    fig, ax = plt.subplots(figsize=(10, 7.07))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.07)
    ax.axis("off")
    for i, (head, items) in enumerate(COLS):
        x = 0.1 + i * 3.4
        w = 2.9
        ax.text(x + w / 2, 6.72, head, ha="center", va="center", fontsize=17)
        ax.add_patch(FancyBboxPatch((x, 0.12), w, 6.25, boxstyle="round,pad=0.01,rounding_size=0.18",
                                    facecolor="white", edgecolor="black", linewidth=1.8))
        wrapped = "\n\n".join(textwrap.fill(t, 31) for t in items)
        ax.text(x + 0.14, 6.2, wrapped, ha="left", va="top", fontsize=9, linespacing=1.22)
        if i < 2:
            ax.add_patch(Polygon([[x + w + 0.08, 3.75], [x + w + 0.42, 3.3], [x + w + 0.08, 2.85]], closed=True, color="black"))
    fig.savefig(PARADIGM, dpi=200, bbox_inches="tight", pad_inches=0.05, facecolor="white")
    plt.close(fig)


def swap_paradigm(c):
    """Point the old Figure 4 picture at the redrawn diagram."""
    for p in c.paras():
        for blip in p._p.iter():
            if blip.tag.endswith("}blip"):
                rid = blip.get(qn("r:embed"))
                part = c.d.part.related_parts.get(rid)
                if part is not None and part.partname.endswith("image11.png"):
                    new, _ = c.d.part.get_or_add_image(PARADIGM)
                    blip.set(qn("r:embed"), new)
                    c.sec("Research Paradigm")
                    c.log.append((c.section, "Replaced", "Figure 4 input-process-output diagram (six sites, heart sounds, thirty participants, t-test, McNemar).",
                                  "Redrawn diagram, in the same layout, showing the study as carried out.", "The old figure repeated the same errors as the text."))
                    return
    raise AssertionError("paradigm image not found")


def clip(s, n=320):
    s = re.sub(r"\s+", " ", s or "").strip()
    return s if len(s) <= n else s[:n - 1].rsplit(" ", 1)[0] + " …"


def log_doc(chapters, confirms):
    d = Document()
    st = d.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(10)
    s = d.sections[0]
    s.orientation = WD_ORIENT.LANDSCAPE
    s.page_width, s.page_height = s.page_height, s.page_width
    s.left_margin = s.right_margin = Inches(0.6)
    s.top_margin = s.bottom_margin = Inches(0.6)
    ROSE = RGBColor(0x8E, 0x2A, 0x52)

    def P(t, size=10, bold=False, italic=False, color=None, after=5):
        p = d.add_paragraph()
        p.paragraph_format.space_after = Pt(after)
        r = p.add_run(t)
        r.font.size, r.bold, r.italic = Pt(size), bold, italic
        if color:
            r.font.color.rgb = color
        return p

    def table(rows, widths, head=True):
        t = d.add_table(rows=len(rows), cols=len(widths))
        t.style = "Table Grid"
        t.autofit = False
        for j, w in enumerate(widths):
            t.columns[j].width = Inches(w)
        for i, row in enumerate(rows):
            for j, v in enumerate(row):
                c = t.cell(i, j)
                c.width = Inches(widths[j])
                pp = c.paragraphs[0]
                pp.paragraph_format.space_after = Pt(1)
                r = pp.add_run(str(v))
                r.font.size = Pt(8.5)
                r.bold = head and i == 0
        if head:
            tr = t.rows[0]._tr.get_or_add_trPr()
            h = tr.makeelement(qn("w:tblHeader"), {})
            tr.append(h)
        P("", after=4)

    P("Resondi · Chapters 1–3 Revision Log", 16, True, color=ROSE, after=2)
    P("Every change made to the revised copies, 6 November 2026", 10, italic=True, after=8)
    P("The originals in Google Drive were not changed. Untouched copies are in chapters/original/. Your layout, headers and "
      "school format were kept. Yellow highlights in the revised chapters are facts only you can supply.", after=8)

    P("Summary", 12.5, True, color=ROSE, after=3)
    rows = [("Chapter", "Revised", "Added", "Removed", "Replaced")]
    for c in chapters:
        n = Counter(x[1] for x in c.log)
        rows.append((c.label, n["Revised"], n["Added"], n["Removed"], n["Replaced"]))
    table(rows, [2.4, 1, 1, 1, 1])

    P("The most serious problems found", 12.5, True, color=ROSE, after=3)
    for t in ("Text from other people's papers was still in the chapters. Chapter 2's Theoretical Framework was about cybersecurity at Makati City Hall, and its only defined term was Chronic Kidney Disease. Chapter 3's Data Analysis was about propagating the plant Ardisia squamulosa, and its trustworthiness section referred to students who experienced body shaming. All removed and rewritten for this study.",
              "The chapters described a different study from the one that was done: fusion, heart sound classification, noise testing, six sites, thirty participants, a t-test and McNemar. They now describe what was done, in the past tense, matching the IMRaD.",
              "Chapter 3 said the data would be split by subject. They were not, so the data leakage is now disclosed, as it is in the concept note.",
              "Chapter 2 mentioned a Raspberry Pi. The device uses an ESP32."):
        P("•  " + t, after=3)
    P("", after=4)

    P("Decisions for you and your adviser", 12.5, True, color=ROSE, after=3)
    for t in ("Research questions and hypotheses (Chapter 1). I changed them to what Chapter 4 can actually answer, and kept a sentence saying three hypotheses were proposed and not tested. Changing questions after the results are in is a sensitive step, so show your adviser. The alternative is to keep the original questions and report those parts as not carried out.",
              "Tense. I moved Chapters 1 and 3 to the past tense because the study is finished. If your school wants Chapters 1–3 kept in proposal form, tell me and I will convert them back.",
              "Lung-only scope. These chapters said “cardiopulmonary”, while the full paper's title and IMRaD are lung-only. I followed the full paper. Theme 6 on heart sounds stays as literature for the planned Heart Mode.",
              "Which device. Chapter 3 describes the build that was tested (Bluetooth, preamplifier, power bank) with a short note on version 2.0, as the IMRaD does. The concept note describes version 2.0, because it is pitching the current product."):
        P("•  " + t, after=3)
    P("", after=4)

    P("Facts only you can supply (highlighted yellow in the chapters)", 12.5, True, color=ROSE, after=3)
    for ch, t in confirms:
        P(f"•  {ch}: {t}", after=2)
    P("", after=4)

    P("Also worth doing (not changed)", 12.5, True, color=ROSE, after=3)
    for t in ("Reference list. These chapters have none of their own. Your full paper's list needs Venkatesh et al. (2003), Hsu et al. (2021) and Oliveira et al. (2022). Remove Amit (2016), Cybermeter (2021), NIST (2014), Lincoln and Guba (1985), Birt et al. (2016) and Zulfiqar et al. (2021) unless they are cited elsewhere.",
              "Theme 5 cites “a 2022 study” in The Journal of Emergency Medicine with no author. I could not confirm the authors, so it stays as written. Please add them from the article.",
              "Themes 2 and 3 repeat much of the same material. A panel may read that as padding. I left both because they are your review; merging them would shorten Chapter 2 considerably.",
              "The signed certificates and validation forms still carry the Ausculta title. See the Rename Checklist (final/14).",
              "I could not check the citations against the original articles. Sources were kept as you cited them."):
        P("•  " + t, after=3)

    for c in chapters:
        d.add_page_break()
        P(c.label + ": every change", 13, True, color=ROSE, after=4)
        rows = [("#", "Section", "Action", "Was", "Now", "Why")]
        for i, (sec, act, was, now, why) in enumerate(c.log, 1):
            rows.append((i, sec, act, clip(was), clip(now), why))
        table(rows, [0.3, 1.05, 0.6, 2.85, 2.85, 2.1])
    path = os.path.join(OUT, "Resondi-Chapters-1-3-Revision-Log.docx")
    d.save(path)
    return path


def main():
    draw_paradigm()
    confirms = []
    chapters = []
    for n, mod, label in ((1, ch1, "Chapter 1"), (2, ch2, "Chapter 2"), (3, ch3, "Chapter 3")):
        c = Chapter(os.path.join(SRC, f"AUSCULTA Chapt-{n}.docx"), label)
        mod.apply(c)
        if n == 2:
            swap_paradigm(c)
        out = os.path.join(OUT, f"Resondi-Chapter-{n}-Revised.docx")
        hits = c.save(out)
        chapters.append(c)
        for x in c.log:
            for m in re.findall(r"\[CONFIRM ([^\]]*)\]", x[3]):
                confirms.append((label, m))
        print(label, Counter(x[1] for x in c.log), "name hits", hits)
    print(log_doc(chapters, confirms))


if __name__ == "__main__":
    main()
