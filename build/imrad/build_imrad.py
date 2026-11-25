"""Resondi — IMRaD paper, lung only.

Every figure reproduced here is one the team has already reported. Where a
methodological detail is not documented anywhere in the material available,
the text carries a marked placeholder rather than an invented value: a
fabricated sample rate would be worse than a visible gap.
"""
import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

INK   = RGBColor(0x1A, 0x1A, 0x1A)
ROSE  = RGBColor(0xC2, 0x18, 0x5B)
GREY  = RGBColor(0x59, 0x59, 0x59)
FONT  = "Times New Roman"

doc = Document()
st = doc.styles["Normal"]
st.font.name, st.font.size = FONT, Pt(12)
st.paragraph_format.space_after = Pt(0)
st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)

sec = doc.sections[0]
sec.left_margin = Inches(1.25); sec.right_margin = Inches(1.0)
sec.top_margin = sec.bottom_margin = Inches(1.0)

# Page numbers in the footer, so the table of contents in the compiled submission can point at real pages.
_fp = sec.footer.paragraphs[0]
_fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
_run = _fp.add_run()
for _tag, _attr in (("w:fldChar", "begin"), ("w:instrText", None), ("w:fldChar", "separate")):
    _el = OxmlElement(_tag)
    if _attr:
        _el.set(qn("w:fldCharType"), _attr)
    else:
        _el.set(qn("xml:space"), "preserve"); _el.text = "PAGE"
    _run._r.append(_el)
_t = OxmlElement("w:t"); _t.text = "1"; _run._r.append(_t)
_end = OxmlElement("w:fldChar"); _end.set(qn("w:fldCharType"), "end"); _run._r.append(_end)
_run.font.size, _run.font.name = Pt(11), FONT


def para(text="", *, after=10, before=0, first=0.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
         size=12, bold=False, italic=False, color=None, spacing=2.0):
    p = doc.add_paragraph()
    p.alignment = align
    pf = p.paragraph_format
    pf.space_after, pf.space_before = Pt(after), Pt(before)
    pf.first_line_indent = Inches(first)
    pf.line_spacing = spacing
    if text:
        r = p.add_run(text)
        r.bold, r.italic = bold, italic
        r.font.size, r.font.name = Pt(size), FONT
        if color: r.font.color.rgb = color
    return p


def H1(t):
    _h = para(t.upper(), after=10, before=18, first=0, align=WD_ALIGN_PARAGRAPH.CENTER,
         size=12, bold=True, spacing=2.0)
    _h.paragraph_format.keep_together = True               # a heading never splits between columns


def H2(t):
    para(t, after=8, before=12, first=0, size=12, bold=True, spacing=2.0).paragraph_format.keep_together = True


def H3(t):
    para(t, after=6, before=8, first=0, size=12, bold=True, italic=True,
         spacing=2.0).paragraph_format.keep_together = True


def FILL(p, text):
    r = p.add_run("  [[TO FILL: " + text + "]]")
    r.italic = True
    r.font.size, r.font.name = Pt(11), FONT
    r.font.color.rgb = ROSE


HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "..", "..", "figures") + os.sep


_N = {"fig": 0, "tab": 0}
COL_W = 3.0     # inches: one column of the two-column layout (6.25 in of text width, 0.25 in gap)
WIDE = []       # (first, last) elements of each figure or table set across the full width


TEXT_W = 6.25   # inches of text width


def _cell_margins(tbl, v=0):
    pr = tbl._tbl.tblPr
    m = OxmlElement("w:tblCellMar")
    for side in ("left", "right"):
        e = OxmlElement(f"w:{side}"); e.set(qn("w:w"), str(v)); e.set(qn("w:type"), "dxa"); m.append(e)
    pr.append(m)


def _widths(tbl, widths):
    """Set the column grid and the table width: Word lays a fixed table out from these, not from the cell widths."""
    for col, w in zip(tbl.columns, widths):
        col.width = Inches(w)
    tw = tbl._tbl.tblPr.find(qn("w:tblW"))
    if tw is None:
        tw = OxmlElement("w:tblW"); tbl._tbl.tblPr.append(tw)
    tw.set(qn("w:type"), "dxa"); tw.set(qn("w:w"), str(int(sum(widths) * 1440)))


def _no_split(row, header=False):
    pr = row._tr.get_or_add_trPr()
    pr.append(OxmlElement("w:cantSplit"))
    if header:
        pr.append(OxmlElement("w:tblHeader"))


def _cap_runs(p, label, caption):
    for text, bold, italic in ((label, True, False), (caption, False, True)):
        if text:
            r = p.add_run(text)
            r.bold, r.italic = bold, italic
            r.font.size, r.font.name = Pt(10.5), FONT


def FIG(num, caption, fname, width_in=6.0, note=None, span=False):
    """Numbered figure: caption above the picture, note beneath. Numbers are assigned in order (num is ignored).
    Caption, picture and note sit in one borderless table row that may not split: keep-with-next alone left captions
    on the page before their pictures in the two-column layout (found 25 Nov 2026)."""
    _N["fig"] += 1
    num = _N["fig"]
    from PIL import Image as _Img
    wide = span or width_in > COL_W                         # span: a small picture set across both columns
    width_in = min(width_in, TEXT_W - 0.05)
    t = doc.add_table(rows=1, cols=1)
    t.alignment, t.autofit = WD_TABLE_ALIGNMENT.CENTER, False
    _cell_margins(t)
    _no_split(t.rows[0])
    cell = t.cell(0, 0)
    cell.width = Inches(TEXT_W if wide else COL_W)
    _widths(t, [TEXT_W if wide else COL_W])
    c = cell.paragraphs[0]
    p = cell.add_paragraph()
    for q, before, after in ((c, 8, 4), (p, 0, 4)):
        q.alignment = WD_ALIGN_PARAGRAPH.CENTER
        q.paragraph_format.space_before, q.paragraph_format.space_after = Pt(before), Pt(after)
        q.paragraph_format.line_spacing = 1.0
    _cap_runs(c, f"Figure {num}. ", caption)
    path = FIGDIR + fname
    im = _Img.open(path)
    p.add_run().add_picture(path, width=Inches(width_in), height=Inches(width_in * im.height / im.width))
    if note:
        n = cell.add_paragraph()
        n.alignment = WD_ALIGN_PARAGRAPH.CENTER
        n.paragraph_format.space_after, n.paragraph_format.line_spacing = Pt(4), 1.0
        r = n.add_run(note); r.italic = True
        r.font.size, r.font.name, r.font.color.rgb = Pt(9.5), FONT, GREY
    last = para("", after=0, first=0, spacing=1.0)          # Word needs a paragraph between two tables
    if wide:
        WIDE.append((t._tbl, last._p))


def _rule(cell, side, size):
    pr = cell._tc.get_or_add_tcPr()
    b = pr.find(qn("w:tcBorders"))
    if b is None:
        b = OxmlElement("w:tcBorders")
        va = pr.find(qn("w:vAlign"))                        # schema order: tcW, ..., tcBorders, ..., vAlign
        if va is not None:
            va.addprevious(b)
        else:
            pr.append(b)
    e = OxmlElement(f"w:{side}")
    for k, v in (("val", "single"), ("sz", str(size)), ("space", "0"), ("color", "000000")):
        e.set(qn(f"w:{k}"), v)
    if side == "top":
        b.insert(0, e)
    else:
        b.append(e)


def TBL(num, caption, rows, widths, note=None, total=False):
    """Numbered table in the style of page 9 of the 83-page paper (user, 25 Nov 2026): "Table N." bold and the title
    in italics, both centred above; a heavy rule above and below the table and one under the bold, centred heads;
    no other lines; first column left, the rest centred. total=True makes the last row a bold total."""
    _N["tab"] += 1
    num = _N["tab"]
    # Caption, table and note sit in one borderless cell that may not split: Word ignores keep-with-next between
    # the sections of the two-column layout and left table heads alone at the foot of a page (25 Nov 2026).
    wide = sum(widths) > COL_W + 0.01
    outer = doc.add_table(rows=1, cols=1)
    outer.alignment, outer.autofit = WD_TABLE_ALIGNMENT.CENTER, False
    _cell_margins(outer)
    _widths(outer, [TEXT_W if wide else COL_W])
    _no_split(outer.rows[0])
    box = outer.cell(0, 0)
    box.width = Inches(TEXT_W if wide else COL_W)

    def line(q, before, after, align=WD_ALIGN_PARAGRAPH.CENTER):
        q.alignment = align
        q.paragraph_format.space_before, q.paragraph_format.space_after = Pt(before), Pt(after)
        q.paragraph_format.line_spacing = 1.0
        return q

    _cap_runs(line(box.paragraphs[0], 8, 0), f"Table {num}.", "")
    _cap_runs(line(box.add_paragraph(), 0, 5), "", caption)
    t = box.add_table(rows=len(rows), cols=len(rows[0]))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    _cell_margins(t, 40)
    _widths(t, widths)
    end = len(rows) - 1
    for i, row in enumerate(rows):
        _no_split(t.rows[i])
        for j, val in enumerate(row):
            cell = t.cell(i, j)
            cell.width = Inches(widths[j])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = line(cell.paragraphs[0], 3, 3,
                     WD_ALIGN_PARAGRAPH.LEFT if j == 0 and i > 0 else WD_ALIGN_PARAGRAPH.CENTER)
            r = p.add_run(str(val))
            r.bold = (i == 0) or (total and i == end)
            r.font.size, r.font.name = Pt(10.5), FONT
            if i == 0:
                _rule(cell, "top", 12)
                _rule(cell, "bottom", 8)
            if i == end:
                _rule(cell, "bottom", 12)
    # python-docx leaves the paragraph Word needs after a nested table; it holds the note
    n = line(box.paragraphs[-1], 4, 4, WD_ALIGN_PARAGRAPH.LEFT)
    if note:
        r = n.add_run(note); r.italic = True
        r.font.size, r.font.name, r.font.color.rgb = Pt(10), FONT, GREY
    last = para("", after=2, first=0, spacing=1.0)
    if wide:
        WIDE.append((outer._tbl, last._p))


# ═══════════════════════════════════════════════════ TITLE
para("Resondi: An IoT-Based AI-Assisted Auscultation Instrument for Cardiopulmonary "
     "Monitoring, Longitudinal Tracking, and Rehabilitation-Support System",
     after=8, first=0, align=WD_ALIGN_PARAGRAPH.CENTER, size=14, bold=True,
     spacing=1.4)
para("Ahnycca Krish N. Malimban",
     after=4, first=0, align=WD_ALIGN_PARAGRAPH.CENTER, spacing=1.2)
para("Science, Technology, Engineering and Mathematics — Senior High School\nPuerto Princesa City National Science High School, Palawan",
     after=8, first=0, align=WD_ALIGN_PARAGRAPH.CENTER, italic=True, spacing=1.2)
# Credits as on the team's title page (14 Nov 2026).
para("Research Advisers: John Lemuel J. Noche · Genelyn O. Bautista",
     after=2, first=0, align=WD_ALIGN_PARAGRAPH.CENTER, size=11, spacing=1.2)
para("Qualified Scientist: Bemsor T. Caabay, MSc",
     after=2, first=0, align=WD_ALIGN_PARAGRAPH.CENTER, size=11, spacing=1.2)
para("Consultants: Kenneth Wilson O. Lim, MD, FPCP, FPCCP · Sonia A. Ulanday, MD, FPPS, FPAPP · "
     "Riza Cornelle C. De La Bajan, MD, FPPS",
     after=16, first=0, align=WD_ALIGN_PARAGRAPH.CENTER, size=11, spacing=1.2)

# ═══════════════════════════════════════════════════ ABSTRACT
ABS = para("A conventional stethoscope keeps no record, so a heart or lung sound cannot be "
     "reviewed by a second clinician or compared with the same site at a later visit. "
     "This study developed Resondi, a low-cost smart stethoscope that records lung "
     "sounds at seven guided sites and heart sounds at five, files each recording by "
     "site, analyses it with neural networks, and routes every result to a "
     "practitioner for confirmation. In field testing in Puerto Princesa City, the "
     "device produced a signal about 13 dB stronger than a conventional stethoscope, "
     "93 percent of recordings were rated good or acceptable, and the original "
     "classifier agreed with reference labels on 6 of 15 recordings (40 percent; p = "
     "0.148 against 25 percent chance). That classifier had been trained on leaked "
     "data, so it was rebuilt with sound-based labels and a patient-wise split. In "
     "five-fold cross-validation on all 126 ICBHI 2017 patients, a three-branch "
     "feature-fusion network trained with paediatric SPRSound recordings reached 40.0 "
     "percent balanced accuracy against 34.0 percent for the original design "
     "(difference 5.9 points, p = 0.008). Two heart-sound models trained on the public"
     " CirCor dataset estimated heart rate within 3.0 beats per minute on 189 test "
     "patients and detected murmurs with 66.7 percent sensitivity, short of the 80 "
     "percent target, at 97.1 percent specificity. All the models now run in the "
     "Resondi application, but none has been tested against labelled recordings from "
     "the device. Resondi is a working acquisition platform; validating its models on "
     "clinician-labelled Filipino recordings is the next step.", first=0, spacing=1.6)
# 18 Nov 2026 (user: copy the AlagaVax format): "Abstract –" and "Keywords –" run in, bold italic.
_r = ABS.add_run("Abstract – "); _r.bold = _r.italic = True; _r.font.name = FONT
ABS.runs[0]._r.addprevious(_r._r)
KW = para("", first=0, spacing=1.6)
_r = KW.add_run("Keywords – "); _r.bold = _r.italic = True; _r.font.name = FONT
_r = KW.add_run("auscultation, lung sounds, heart sounds, smart stethoscope, convolutional neural network, "
                "feature fusion, primary care, Philippines"); _r.italic = True; _r.font.name = FONT

# ═══════════════════════════════════════════════════ INTRODUCTION
H1("I. Introduction")

para("Heart and lung disease are among the leading causes of mortality in the "
     "Philippines. Philippine Statistics Authority figures for 2024 place ischaemic heart "
     "disease first among all causes of death, with 134,074 deaths or 19.1 percent of the "
     "national total, and pneumonia fourth, with approximately 47,260 deaths or 6.7 "
     "percent. Conditions of this kind are, in principle, detectable at the point of first "
     "contact: the adventitious sounds that accompany consolidation, airway narrowing, and "
     "fluid accumulation, and the murmurs that accompany many heart conditions, are "
     "audible through a conventional stethoscope, and auscultation remains the first instrumented "
     "examination a patient receives in a barangay health station or rural health unit.", first=0)

para("The difficulty is not that these sounds are inaudible but that they are not "
     "retained. A conventional stethoscope produces no record. The acoustic evidence on "
     "which a clinical judgement rests exists only for the duration of the examination "
     "and only in the ear of the person holding the instrument. Nothing survives that a "
     "second clinician could review, that could be compared against the same anatomical "
     "site at a later visit, or that could be reconciled against a diagnosis made "
     "elsewhere. In facilities where no physician is present, the assessment of a midwife "
     "or barangay health worker is therefore both unverifiable and unrepeatable.")

para("The diagnostic consequence is measurable. In a pooled analysis across "
     "thirty-four studies, unaided auscultation achieved a sensitivity of approximately "
     "37 percent against a specificity of 89 percent (Arts et al., 2020). The asymmetry "
     "is characteristic: the examination rarely raises a false alarm but misses a large "
     "proportion of true disease. Part of this variance is attributable to inconsistent "
     "technique. Practitioners listen at different locations, for different durations, "
     "and describe what they hear in terms that are not standardised between observers.")

para("A second gap appears after assessment. Pulmonary rehabilitation, which has an "
     "established evidence base in chronic obstructive pulmonary disease, reaches only "
     "about 2.7 percent of patients worldwide. Where rehabilitation is delivered at all, "
     "progress is typically tracked through symptom questionnaires and functional tests "
     "rather than through any direct acoustic measure of the lung itself.")

para("Electronic stethoscopes that record and store audio are commercially available "
     "and address the first of these gaps. They have not reached Philippine primary care "
     "in any quantity, principally on cost: the 3M Littmann CORE Digital Stethoscope "
     "lists at approximately USD 379, equivalent to roughly ₱22,000 before shipping and "
     "import duties (3M, 2025), which exceeds the annual equipment allocation of many "
     "rural health units. Devices in this class also assume a trained clinician who "
     "already knows where to place the chest piece, and they organise recordings by "
     "timestamp rather than by anatomical site, which limits their usefulness for "
     "longitudinal comparison.")

para("This study developed and evaluated Resondi, a low-cost smart stethoscope that "
     "records lung sounds at seven standardised sites \u2014 six lung fields and a "
     "tracheal reference \u2014 and heart sounds at five cardiac sites under application "
     "guidance, stores each recording against its site of origin, applies a "
     "convolutional neural network to classify the recording, and presents the result to "
     "a practitioner for confirmation. The system is intended to support rather than "
     "replace clinical judgement, and to make a respiratory examination comparable "
     "between visits.")

# 18 Nov 2026: alignment statement, as in the AlagaVax paper.
para("The study contributes to United Nations Sustainable Development Goal 3, Good Health and "
     "Well-Being, by supporting the examination of heart and lung sounds at the primary level of care, "
     "and to Goal 9, Industry, Innovation and Infrastructure, through a locally built recording device "
     "and platform (United Nations, 2015).")

H2("Objectives of the Study")
para("The study set out to achieve the following:", first=0, after=6)
for n, (obj, sub) in enumerate([
    ("To develop a smart stethoscope capable of recording and organising lung sounds "
     "by anatomical site.",
     "The device must identify the site at which a recording was taken and file it "
     "accordingly, rather than storing an undifferentiated sequence of audio files."),
    ("To provide guided auscultation through a standardised anatomical sequence.",
     "The application directs the user to each of seven sites in a fixed order so that "
     "recordings are comparable between examinations and between operators."),
    ("To provide guided cardiac auscultation through a separate Heart Mode.",
     "The application directs the user to the aortic, pulmonic, tricuspid and mitral "
     "areas and Erb's point, in a fixed order from the base of the heart to the apex, and "
     "files each heart recording by site."),
    ("To assess the quality of recorded lung sounds.",
     "A recording degraded by ambient noise, weak contact, or motion artifact should be "
     "identified as such."),
    ("To implement AI-assisted classification of respiratory sound patterns.",
     "A convolutional neural network classifies each recording as normal, wheezing, "
     "crackles, or wheezing with crackles."),
    ("To develop AI-assisted analysis of heart sounds.",
     "Two models are trained on expert-annotated public recordings: one finds the "
     "first and second heart sounds and estimates heart rate, and one reports whether "
     "a murmur is present. Both run in the application; placing a murmur in the cardiac "
     "cycle is the next step."),
    ("To establish longitudinal monitoring of respiratory sound changes across visits.",
     "A recording is compared against an earlier recording taken at the same anatomical "
     "site on the same patient."),
    ("To provide rehabilitation support through guided breathing exercises.",
     "Exercises are released under practitioner supervision and completion is recorded."),
    ("To provide healthcare professionals with organised recordings and a review "
     "workflow.",
     "The practitioner confirms, modifies, or rejects each AI-assisted classification."),
], 1):
    p = para(f"{n}. {obj}", first=0, after=4, spacing=1.6)
    p.paragraph_format.left_indent = Inches(0.35)
    p2 = para(sub, first=0, after=8, size=11, italic=True, spacing=1.6)
    p2.paragraph_format.left_indent = Inches(0.6)

H2("Research Questions")
para("The study, as set out in the research plan, sought to answer the following questions. Questions 6, "
     "7 and 8 correspond to the plan's three hypotheses.", first=0, after=6)
for n, (q, subs) in enumerate([('What is the quality of cardiopulmonary sound recordings captured using Resondi in terms of', ['signal quality', 'clarity', 'noise level']), ('What are the specifications of the Resondi Smart Stethoscope in terms of', ['design', 'components', 'cost']), ('What are the specifications of the Resondi Cardiopulmonary Monitoring Platform in terms of', ['user interface', 'system architecture', 'role-based access', 'data management']), ('What are the specifications of the Resondi cardiopulmonary sound analysis system in terms of', ['audio preprocessing method', 'feature representations', 'CNN branch architecture', 'feature-fusion architecture']), ('What is the response time of the Resondi system in terms of', ['smart-stethoscope Wi-Fi connection', 'sound recording', 'recording-quality assessment', 'signal preprocessing', 'classification output']), ('Is there a significant difference in the classification performance of the CNN-fusion model between clean and noise-contaminated cardiopulmonary sound recordings?', []), ('Is there a significant difference between the classification performance obtained from reference-dataset recordings and that obtained from Resondi device recordings?', []), ('Is there a significant difference between the recording quality of a conventional stethoscope and Resondi?', []), ('What is the level of acceptance of end users toward Resondi in terms of', ['user-friendliness', 'usability', 'durability', 'functionality', 'perceived usefulness for community-based monitoring']), ('What are the preferences of end users regarding instructional support for Resondi in terms of', ['diagram-based auscultation-zone guidance', 'device manual clarity', 'overall ease of learning and self-use', 'app navigation flow']), ('How can Resondi support longitudinal cardiopulmonary monitoring and practitioner-supervised rehabilitation through repeated sound recordings, comparison of monitoring records, AI-assisted summaries, and practitioner-approved recommendations?', [])], 1):
    text = q + (": " + "; ".join(subs[:-1]) + (", and " if len(subs) > 2 else " and ") + subs[-1] + "?"
                if subs else "")
    p = para(f"{n}. {text}", first=0, after=4, spacing=1.6)
    p.paragraph_format.left_indent = Inches(0.35)

H2("Scope and Delimitation")
para("This study covers lung and heart sounds, at different stages. Lung sounds are "
     "recorded, classified and evaluated. Heart sounds are recorded at five sites and "
     "stored for practitioner review. Two heart-sound models, one that times the heart"
     " sounds and estimates heart rate and one that detects murmurs, were trained and "
     "tested on a public dataset and placed in the application, which shows each "
     "result with its limits; they have not been tested on Resondi heart recordings, and "
     "no heart recording is passed to the lung classifier. "
     "Lung classification is limited to four "
     "categories — normal, wheezing, crackles, and "
     "wheezing with crackles — and the system does not identify a disease, stage a "
     "condition, or produce a diagnosis. All classifications are presented to a "
     "practitioner for confirmation and none is returned to a patient unreviewed. "
     "Evaluation was conducted in Puerto Princesa City with a prototype device, and the "
     "findings describe that prototype rather than a production unit. The field "
     "evaluation used the original classifier, a single-input MFCC network. After that "
     "evaluation the classifier was rebuilt and a three-branch feature-fusion version was "
     "trained and tested on public lung-sound databases (ICBHI 2017 and SPRSound); the "
     "fusion version was then run on recordings already made with the Resondi device, but "
     "those recordings have no reference labels, so its accuracy on the device was not "
     "measured. A nine-site "
     "protocol remains planned and is discussed under planned extensions.", first=0)

# 18 Nov 2026: the literature becomes its own section, as in the AlagaVax paper.
H1("II. Review of Related Literature")
para("The literature establishes two things firmly. Convolutional neural networks "
     "classify lung sounds at a standard that compares favourably with human listeners: "
     "Kim et al. (2021), training on 1,918 recordings from actual patients, reported 86.5 "
     "percent accuracy in detecting abnormal lung sounds and 85.7 percent in "
     "distinguishing crackles, wheezes and rhonchi, outperforming medical students, "
     "interns and several residents tested on the same recordings. Acharya and Basu "
     "(2020) reported comparable results from a CNN-RNN model operating on "
     "mel-spectrograms. Separately, digital stethoscopes built on MEMS microphones and "
     "Bluetooth Low Energy have been shown to capture and transmit usable respiratory "
     "audio to a mobile application (Baraeinejad et al., 2023).", first=0)

para("What the literature does not establish is that either result survives contact with "
     "the conditions of primary care. Reported classification performance is obtained on "
     "curated benchmark corpora such as the ICBHI 2017 database (Rocha et al., 2019), "
     "whose recordings were collected by researchers using research-grade equipment under "
     "controlled conditions. Recordings taken on deployed devices by non-specialist "
     "operators differ from these in ways that bear directly on classification: ambient "
     "noise, inconsistent chest-piece placement, variation in operator technique, and "
     "differences between recording devices have all been identified as degrading "
     "AI-supported analysis (Komaryshyn & Kogut, 2026). The performance figures above are "
     "therefore properties of a "
     "model evaluated on clean audio, not predictions about what that model will do with "
     "audio captured in a barangay health station.", first=0)

para("Acquisition is the uncontrolled variable, and it is the one that existing systems "
     "leave to the operator. A device that records faithfully does not, by recording "
     "faithfully, ensure that the chest piece was in the right place, that the patient "
     "was breathing appropriately, or that the resulting audio is of sufficient quality to "
     "classify at all. Where acquisition is unguided and unassessed, a classifier of any "
     "accuracy inherits the variance of the recording, and the published accuracy figure "
     "ceases to describe the deployed system. This matters most precisely where "
     "auscultation matters most: Arts et al. (2020) found unaided auscultation pooled at "
     "37 percent sensitivity against 89 percent specificity across thirty-four studies, "
     "and attributed much of that weakness to variation in how clinicians listen and "
     "describe what they hear.", first=0)

para("Two further gaps follow from the same point. Digital recording makes longitudinal "
     "comparison possible in principle, but a change in lung sound between visits is "
     "interpretable only if both recordings were taken at the same anatomical location "
     "under the same conditions, and only if a professional reviews the comparison rather "
     "than accepting a model output as a finding. And although respiratory rehabilitation "
     "has an established evidence base, it reaches only about 2.7 percent of chronic "
     "obstructive pulmonary disease patients worldwide, and where delivered is tracked "
     "through symptom questionnaires and functional tests rather than through any direct "
     "acoustic measure of the lung.", first=0)

para("The gap this study addresses is therefore not the absence of an accurate classifier "
     "but the absence of a system that controls the conditions under which a classifier "
     "receives its input, and that keeps a professional in the decision path afterwards. "
     "Resondi was developed to standardise acquisition through guided placement at fixed "
     "anatomical locations, to assess recording quality before analysis rather than after, "
     "to classify under that constraint, to make successive recordings at the same "
     "location comparable, and to route every result to a practitioner for confirmation. "
     "The study reports what that system achieves and, equally, what it does not yet "
     "establish.", first=0)

# ═══════════════════════════════════════════════════ METHODOLOGY
H1("III. Materials and Methods")

H2("Research Design")
para("The study employed a developmental\u2013descriptive research design in two phases. "
         "In the first, an instrument was designed, constructed, and then characterised in "
         "the field across five dimensions: signal acquisition relative to a conventional "
         "acoustic stethoscope, recording clarity, system response time, performance across "
         "ambient noise conditions, and agreement between the original model's "
         "classification and reference labels. In the second, prompted by a flaw found in "
         "how the original model had been trained, the classifier was rebuilt and its "
         "candidate versions were compared on public lung-sound databases under a "
         "patient-wise evaluation. No experimental manipulation of human participants or "
         "control group was involved.", first=0)

H2("Device Development")
para("The device pairs a conventional acoustic chest piece and silicone tubing with a "
     "microphone and preamplifier, an ESP32 "
     "microcontroller, Bluetooth Low Energy communication, MicroSD storage, a 20 × 4 "
     "character LCD for device status, and a 10,000 mAh power bank. The assembly is housed "
     "in a 3D-printed polylactic acid casing. All results reported here were obtained with "
     "that build.", first=0)
para("The device has since been revised as enclosure version 2.0 (Figure 1), which was not used in "
     "this evaluation: the INMP441 digital microphone is read over I²S with no analogue "
     "preamplifier, and Bluetooth is replaced by a Wi-Fi access "
     "point through which a browser connects to the device directly. Whether the revised "
     "build changes recording quality has not yet been measured.", first=0)

# 16 Nov 2026 (user): the labelled figure of the old prototype was replaced with the version 2.0 3D model,
# labelled by build/dev2/label_render.py.
FIG(1, "The Resondi Smart Stethoscope, Version 2.0, with Components Identified",
    "Resondi-Device-3D-Labelled.png", 4.7,
    note="Rendered from the team's 3D model, which measures about 160 × 100 × 60 mm; the "
         "fabricated enclosure measures 173 × 80 × 70 mm, and colours are illustrative. The "
         "results in this paper were obtained with the earlier field build, which used an "
         "electret microphone on a MAX4466 board and Bluetooth Low Energy.")

p = para("The MAX4466 was selected for unit-to-unit consistency of frequency "
         "response. Because the system's central claim is that a recording taken at "
         "one visit can be compared against the same site at a later visit, variation "
         "in transducer response between devices would introduce drift into precisely "
         "the measurement the system exists to make.", first=0)

p = para("In the field build (Figure 2), the microcontroller samples the preamplified acoustic signal, writes the "
         "recording to MicroSD together with its metadata (anatomical site, timestamp, "
         "and duration) in WAV format, and advertises over Bluetooth Low Energy. Two "
         "storage paths "
         "operate in parallel: recordings transfer to the paired mobile application "
         "where a phone is present, and are retained on MicroSD for later transfer where "
         "it is not. Capture therefore does not depend on connectivity.", first=0)
para("Recordings were stored as 16-bit, 16 kHz mono WAV files of 15 seconds and divided "
     "into 1-second segments (16,000 samples) for classification; during training the "
     "segments overlapped by 50 percent (0.5-second hop), and at testing and in the "
     "application they did not overlap, with segment scores averaged over each breathing "
     "cycle or recording.", first=0)

FIG(2, "Hardware Architecture of the Field Build",
    "d1_hardware.png", 6.05)

H2("Auscultation Protocol")
para("Recordings are taken at seven standardised sites. A tracheal reference is captured "
     "first, over the suprasternal notch, followed by six lung fields in left\u2013right "
     "pairs: right and left upper (second intercostal space, midclavicular line), right "
     "and left middle (fourth to fifth intercostal space, mid-axillary line, sampling the "
     "right middle lobe and the lingula), and right and left lower (infrascapular, "
     "T8\u2013T10, beside the spine). The tracheal capture is a reference and is not "
     "classified as a lung field. Each site corresponds to one of the seven chest-location "
     "codes of the ICBHI 2017 database. The application presents an "
     "anatomical lung map, the user selects a location, positions the chest piece, "
     "confirms placement, and records. The resulting audio is saved with its anatomical "
     "location and recording metadata, and repeated recordings are permitted where "
     "necessary. Site attribution therefore does not depend on the operator remembering "
     "or entering it.", first=0)

para("Each site is recorded with the patient breathing through an "
     "open mouth more deeply than at rest, completing at least one full inspiration and "
     "expiration. The chest piece contacts bare skin, since clothing "
     "attenuates the signal and introduces friction artifact (Bohadana et al., 2014). "
     "Right and left locations are taken as a pair at each level before the sequence "
     "descends; the lateral sites are reached with the arm raised and the posterior sites "
     "with the patient seated and the arms brought forward.")

FIG(3, "The Seven Standardised Sites Recorded by the Evaluated Build",
    "d2_seven_sites.png", 4.9)

para("Heart Mode uses the same device and recording settings with a separate guided "
     "sequence of five sites (Figure 4), recorded from the base of the heart to the apex: the aortic "
     "area (second intercostal space, right sternal border), the pulmonic area (second "
     "intercostal space, left sternal border), Erb's point (third intercostal space, left "
     "sternal border), the tricuspid area (fourth intercostal space, left lower sternal "
     "border), and the mitral area at the apex (fifth intercostal space, midclavicular "
     "line). The first four are the standard valve auscultation points and match the "
     "locations of the CirCor DigiScope dataset (Oliveira et al., 2022); Erb's point is "
     "recorded and filed for the practitioner but has no counterpart in that dataset. Each "
     "site is recorded for 15 seconds with the diaphragm on bare skin and the patient at "
     "rest, and the recording is saved with its site, mode and time.", first=0)
FIG(3, "The Five Cardiac Sites Recorded in Heart Mode",
    "h1_heart_sites.png", 3.0,
    note="Numbered in recording order, from the base of the heart to the apex. Erb's point "
         "(3) is filed for the practitioner and is not part of the planned classifier input.")

H2("Signal Processing and Model Architecture")
para("Each raw WAV recording is resampled to 16 kHz to provide a consistent rate for "
     "processing, then passes through noise reduction to suppress background "
     "interference, amplitude normalisation to standardise level, and segmentation into "
     "fixed-length segments (Figure 5). Each segment is divided into short frames, transformed by "
     "Short-Time Fourier Transform, passed through a mel-scale filterbank, and reduced "
     "by a discrete cosine transform to mel-frequency cepstral coefficients (MFCCs), "
     "which form the input to the classifier. The parameters are given below.", first=0)

FIG(4, "Audio Preprocessing Applied to Every Recording",
    "d3_preprocess.png", 6.05)

p = para("The classifier is a convolutional neural network taking the MFCC sequence as "
         "its single input (Figure 6). Convolutional layers extract local patterns from the "
         "coefficients over time, pooling layers reduce feature dimensionality, the result "
         "is flattened, and a softmax output layer "
         "returns class probabilities over four categories: normal, wheezing, crackles, "
         "and wheezing with crackles. The model classifies respiratory sound patterns "
         "and does not identify diseases.", first=0)
para("The original model, which produced the field results reported below, was "
     "developed using the Edge Impulse "
     "platform and deployed as a WebAssembly build, which performs inference in the "
     "browser within the mobile-first application. This accounts for the classification "
     "latency reported below.", first=0)
para("Audio was sampled at 16 kHz and analysed in 1,000 ms windows advanced in "
     "500 ms steps, giving 50 percent overlap between consecutive windows; shorter "
     "segments were zero-padded. Each window was reduced to 13 mel-frequency "
     "cepstral coefficients computed over 0.02 s frames at a 0.02 s stride, using a "
     "32-filter mel filterbank, a 256-point FFT, a normalisation window of 101, a "
     "low-frequency cutoff of 0 Hz with no upper cutoff set, and a pre-emphasis "
     "coefficient of 0.98.", first=0)
para("The classifier is a one-dimensional convolutional network: the coefficient "
     "vector is reshaped to 13 channels, passed through a convolutional layer of 8 "
     "filters with kernel size 3 and ReLU activation, max-pooled with pool size and "
     "stride 2, and dropped out at 0.25; the same block repeats with 16 filters; the "
     "result is flattened into a four-unit softmax output layer. Training minimised "
     "categorical cross-entropy, the default loss of the Edge Impulse classification "
     "block, which was not changed, using the "
     "Adam optimiser at a learning rate of 0.005 with beta-1 of 0.9 and beta-2 of "
     "0.999, a batch size of 32, and 100 epochs. The impulse was trained on the full "
     "data subset. On the profiled target the feature block requires approximately "
     "154 ms and 15 KB of RAM, and inference approximately 3 ms, 12.5 KB of RAM and "
     "46.1 KB of flash.", first=0)
para("Twenty percent of the training data was held out for validation. No metadata "
     "key was supplied to govern that split, so the training and validation "
     "partitions were drawn at random over individual samples rather than grouped by "
     "parent recording or by subject. The impulse was profiled for an eight-bit "
     "quantised build, which is the build deployed to the device. No data "
     "augmentation was configured.", first=0)

FIG(5, "Classification Model Architecture",
    "d4_classifier.png", 6.05)

p = para("A rule-based interpretation layer operates above the classifier (Figure 7). Per-zone "
         "classifications are mapped by six explicit rules to a literature-supported "
         "possibility \u2014 for example, all zones healthy, a bilateral upper-zone wheeze "
         "component, or crackles in one or both lower zones \u2014 each accompanied by its "
         "supporting source. Patterns matching none of the defined rules default to a "
         "recommendation for further clinical evaluation. All outputs are framed as "
         "possibilities requiring clinical evaluation and none is presented as a "
         "diagnosis. The rules operate on four zones: the two anterior second-intercostal "
         "sites form the upper left and upper right zones, and the two posterior "
         "infrascapular sites the lower left and lower right zones. The two mid-axillary "
         "sites, over the right middle lobe and the lingula, and the trachea are classified "
         "and reported site by site but are not inputs to the zone rules, which as "
         "specified name only the four upper and lower zones.", first=0)

FIG(6, "Rule-Based Interpretation Layer Above the Classifier",
    "d5_rules.png", 6.05)

H2("Dataset")
p = para("The model was trained and evaluated against the ICBHI 2017 Respiratory Sound "
         "Database (Rocha et al., 2019), which contains 920 annotated recordings from "
         "126 subjects totalling 5.5 hours of audio and 6,898 annotated respiratory "
         "cycles, of which 3,256 contain adventitious sounds. Recordings were captured at "
         "seven chest locations using four recording devices \u2014 AKG C417L, Littmann "
         "Classic II SE, Littmann 3200, and Meditron. Although the database provides "
         "cycle-level crackle and wheeze annotations, the model evaluated here was "
         "trained on patient-level condition labels (asthma, bronchiolitis, pneumonia, "
         "and healthy) applied to every segment of a patient\u2019s audio and displayed "
         "as the four sound patterns. Because a condition is not audible in every "
         "segment, this labelling is itself a limitation, set out below. "
         "The database was collected by research teams in Portugal, at the "
         "University of Aveiro and Hospital Infante D. Pedro, and in Greece, at the "
         "Aristotle University of Thessaloniki and associated hospitals. It contains no "
         "Filipino or other Asian representation, a limitation treated explicitly in the "
         "discussion.", first=0)
para("The original model was not trained on a patient-wise partition. Its training, "
     "validation and test sets were drawn at random over individual samples, as "
     "described below. The rebuilt models, described under Classifier Rebuild, correct "
     "this.", first=0)

para("One property of this partitioning bears directly on how the corpus results below "
     "should be read. The 19,246 labelled samples are five seconds long and total "
     "approximately 96,000 seconds of audio, against roughly 19,800 seconds in the "
     "source database \u2014 a ratio of about 4.9, consistent with five-second segments cut "
     "at a one-second stride. Each second of source audio therefore appears in "
     "approximately five samples. Because the training, validation and test partitions "
     "were drawn at random over samples and not grouped by parent recording or subject, "
     "segments that share four of their five seconds of audio are distributed across all "
     "three partitions. Combined with patient-level labels, this allows a model to score "
     "well by recognising the patient rather than the sound. Neither the validation "
     "accuracy nor the held-out test accuracy is therefore independent of the training "
     "data, and neither is reported as evidence of performance. For the original model, "
     "the field agreement reported in the Results is the only estimate that is "
     "independent of its training data.", first=0)

H2("Classifier Rebuild")
para("Because the original model had learned to recognise patients rather than sounds, "
     "the classifier was rebuilt after the field evaluation. Three things were changed: "
     "the labels, the way the data were divided, and, in a second step, the model "
     "architecture and the training data.", first=0)
para("Labels were taken from the sound rather than the diagnosis. Each annotated "
     "breathing cycle in ICBHI 2017 carries its own crackle and wheeze flags, and these "
     "were mapped to the four output classes as shown in Table 1. Every one of the 6,898 "
     "cycles was used.", first=0)
TBL(1, "Mapping of ICBHI 2017 Cycle Annotations to the Four Output Classes",
    [["Crackles annotated", "Wheezes annotated", "Class"],
     ["No", "No", "Healthy"],
     ["Yes", "No", "Crackles"],
     ["No", "Yes", "Wheezing"],
     ["Yes", "Yes", "Wheezing with Crackles"]],
    [1.8, 1.8, 2.3],
    "Classes are ordered alphabetically in the model output (Crackles, Healthy, "
    "Wheezing, Wheezing with Crackles), the order Edge Impulse uses.")
para("Data were divided by patient before any audio was cut, so that no patient "
     "contributed to more than one partition: 65 patients (4,850 cycles) for training, "
     "30 (997 cycles) for validation, and 31 (1,051 cycles) for testing. The division was "
     "balanced by both class and recording device. A first division balanced by class "
     "alone placed 79 percent of the training audio on one of the database's four "
     "stethoscopes, and the resulting model scored at chance on recordings from the "
     "others; balancing the devices corrected most of that effect. Each cycle was cut into "
     "non-overlapping one-second windows at 16 kHz, and a cycle's prediction is the mean "
     "of its windows' class probabilities.", first=0)
para("Two architectures are reported. The first keeps the original design: 13 MFCCs per "
     "frame passed to a one-dimensional convolutional network, here with 32 and 64 "
     "filters. An eight-bit Edge Impulse build of this network replaced the original "
     "model in the Resondi application on 10 November 2026, and was itself replaced by "
     "the fusion network on 13 November 2026. The second is a three-branch "
     "feature-fusion network after Tariq et al. (2022), shown in Figure 8. The same window is represented "
     "three ways: as 13 MFCCs, as a log-power spectrogram from 0 to 4 kHz (129 bins, "
     "20 ms frames), and as a 12-bin chromagram from 50 to 4,000 Hz (64 ms frames). Each "
     "representation passes through its own convolutional branch; the three 64-unit "
     "outputs are concatenated and passed to a dense layer and a four-class softmax "
     "output, about 190,000 parameters in total.", first=0)
FIG(7, "The Three-Branch Feature-Fusion Classifier as Built",
    "p2_fusion.png", 6.05)
para("Because ICBHI 2017 contains only adult European patients, a second training "
     "corpus was added: SPRSound, the SJTU Paediatric Respiratory Sound Database "
     "(Zhang et al., 2022), recorded from children aged one month to 18 years at "
     "Shanghai Children's Medical Center and released under a CC BY 4.0 licence. Its "
     "event labels were mapped to the same four classes (normal to Healthy; fine or "
     "coarse crackle to Crackles; wheeze to Wheezing; wheeze with crackle to Wheezing "
     "with Crackles). Rhonchi and stridor events, which have no counterpart in the ICBHI "
     "labels, were excluded, as were recordings marked as poor quality. SPRSound was "
     "divided by patient, separately from ICBHI, with 230 children held out for testing. "
     "Because 82 percent of its windows are healthy, it was rebalanced: all crackle and "
     "wheeze windows were kept, healthy windows were capped at the number in ICBHI "
     "(20,590 of 49,417), and every combination of dataset and class carried equal "
     "weight in training. Audio from both corpora was band-limited to 0.1–3.9 kHz, "
     "levelled, and normalised separately for each corpus.", first=0)
para("Every version was trained with three random seeds, and versions were compared on "
     "the validation patients only. Fifteen versions were tried, including mel-filterbank "
     "input, data augmentation, a pair of yes-or-no detectors for crackles and wheezes, "
     "single-representation networks, a late-fusion average of three single networks, and "
     "the fusion network without its chromagram branch. Before any test patient was "
     "scored, the version to be reported was named in writing, and every test run was "
     "logged.", first=0)
para("Two evaluations followed. The first scored the pre-specified versions once on the "
     "31 ICBHI test patients and on the 230 SPRSound test children. The ICBHI test set was "
     "read three times in this way across successive rounds, each with its primary "
     "version fixed in advance. The second was a five-fold cross-validation across all 126 "
     "ICBHI patients, so that every patient was tested once by a model that had never "
     "seen them. Patients were dealt into five folds balanced by class and recording "
     "device; in fold k the test patients were fold k, early stopping used fold k + 1, "
     "and the remaining three folds were used for training, with SPRSound added for the "
     "fusion network. The app's MFCC design trained on ICBHI alone was compared with the "
     "fusion network trained on ICBHI and SPRSound, the latter averaged over its three "
     "seeds.", first=0)

para("To show how much a leaky division of the data inflates the score, the fusion "
     "network was also trained on two deliberately leaky divisions, with every other "
     "setting unchanged (one training seed). In the first, ICBHI breathing cycles were "
     "assigned at random to training (70 percent), validation (10 percent) and testing "
     "(20 percent), so that a test patient's other breaths were in the training data. In "
     "the second, the one-second windows were assigned at random, so that overlapping "
     "pieces of the same breath fell on both sides, similar in kind to the original model's division. "
     "The model from the first division was also scored on its own training cycles. "
     "These runs are a demonstration of the flaw, not estimates of accuracy, and no "
     "accuracy claim in this paper rests on them.", first=0)

H2("Heart Sound Component")
para("The cardiac models follow the same discipline as the lung classifier, an "
     "acoustic description and never a diagnosis. The planned output, in order of build, is "
     "that the first and second heart sounds (S1 and S2) are identified and timed, that a "
     "murmur is reported as present or absent, and that a present murmur is placed as "
     "systolic or diastolic, with a recording-quality gate in front. Third and fourth heart "
     "sounds (S3 and S4) are named but not promised, because no public dataset labels "
     "them in enough patients to train on. The first two steps, heart-sound timing with "
     "heart rate and murmur presence, were built, tested and placed in the application for "
     "this paper; murmur timing and the quality gate were not.", first=0)
para("The training corpus is the CirCor DigiScope Phonocardiogram Dataset (Oliveira et al., "
     "2022), recorded from children and adolescents in Brazil at the aortic, pulmonic, "
     "tricuspid and mitral areas and released under the Open Data Commons Attribution "
     "licence. Its publicly released portion, which was downloaded and checked for this "
     "study, holds 3,163 recordings from 942 patients. A cardiac physiologist labelled each "
     "patient's murmur as present (179 patients), absent (695) or unknown (68), and for a "
     "present murmur recorded its timing, shape, grade, pitch and quality, together with "
     "the boundaries of S1, systole, S2 and diastole. The unknown label marks recordings "
     "too poor to judge rather than a clinical state, so those patients are routed to the "
     "quality pathway rather than treated as a class.", first=0)
para("CirCor was divided by patient with a fixed seed into training (564 patients, "
     "1,898 recordings), validation (189 patients, 634 recordings) and test (189 "
     "patients, 631 recordings) sets, balanced by murmur label and by the dataset's "
     "two collection campaigns, so that no patient's recordings fell on more than one "
     "side. Each recording was band-pass filtered from 25 to 1,900 Hz, brought to a "
     "common level, and converted to a log-power spectrogram at 50 frames per second.", first=0)
para("Two models were trained. The first, for heart-sound timing, is a small "
     "convolutional network followed by a bidirectional recurrent layer that labels "
     "every 20 ms frame as S1, systole, S2 or diastole, learned from the dataset's "
     "annotated boundaries. Its frame labels are then decoded so that the four states "
     "can only follow each other in the order of the cardiac cycle, with the one "
     "decoding setting chosen on the validation patients. Heart rate is 60 divided by "
     "the median interval between successive S1 onsets, as the application would "
     "compute it. It was scored on test recordings against the heart rate from the "
     "reference boundaries, with an untrained autocorrelation estimate as a baseline, "
     "and an S1 or S2 onset counted as found when it lay within 100 ms of a reference "
     "onset. The second model, for murmurs, is a one-dimensional convolutional network"
     " that scores six-second windows; a recording's score is the mean over its "
     "windows and a patient's is the highest over their sites, so a murmur counts as "
     "present when it is detected at any site. Three training seeds were averaged, and"
     " patients labelled unknown were left out of training and reported separately.", first=0)
para("Because a missed murmur costs more than an unnecessary referral, sensitivity was"
     " the primary criterion. Before any test patient was scored, the decision "
     "threshold was fixed on the validation patients as the highest one reaching 80 "
     "percent sensitivity there; sensitivity, specificity, positive predictive value, "
     "F1-score, Cohen's kappa, the area under the ROC curve (AUROC) and the confusion "
     "matrix were then reported at the patient level, with patient-level bootstrap "
     "confidence intervals. One change was made to the plan before testing and is "
     "recorded in the training script: the timing model was planned with three seeds "
     "and up to 40 epochs, but one epoch took about five minutes on the available "
     "computer, so it was trained with one seed for up to 15 epochs.", first=0)
para("Both models were then placed in the Resondi application in the same way as the "
     "lung fusion network: exported to ONNX and run in the browser with ONNX Runtime "
     "Web, with the feature calculation rewritten in JavaScript. Because the device "
     "records at 16 kHz and CirCor at 4 kHz, the application first low-pass filters "
     "each recording and keeps every fourth sample, then computes exactly the training"
     " features. This path was checked in three ways: in Python, by passing all 631 "
     "test recordings, upsampled to 16 kHz, through it; in Node.js, by comparing the "
     "JavaScript code with the Python reference on 25 test recordings; and in a "
     "browser on the application's preview build, on 8. A heart recording in the "
     "application is analysed on request, and the result, an estimated heart rate and "
     "a murmur flag at the threshold fixed above, is saved with the recording, shown "
     "with its limits, and passed to the reviewing cardiac practitioner with the case.", first=0)
para("The dataset's labels are also being checked against an independent "
     "listener. Twenty-five CirCor recordings were drawn at random with a fixed seed, five "
     "from each of five groups: no murmur, holosystolic, early-systolic, mid-systolic, and "
     "diastolic murmur. They were renamed S01 to S25 in mixed order and given to a reviewing "
     "cardiologist with an answer sheet asking, for each recording, whether it is usable, "
     "whether a murmur is heard, its timing, its grade, and the reviewer's confidence. The "
     "dataset's own labels are held separately and are not shown to the reviewer, so the "
     "comparison tests the labels the models learned from. The review was planned to "
     "finish before training, but the models were trained before it was returned; if it "
     "finds the dataset's labels unreliable, the heart results below must be revised.", first=0)
p = para("Fundamental heart sounds lie lower in frequency than lung sounds, with most S1 and "
         "S2 energy below about 150 Hz. The field build used an electret microphone on a "
         "MAX4466 amplifier board, whose low-frequency response is set by the capsule and its "
         "acoustic coupling and is not specified by the manufacturer for this application. "
         "The digital microphone in the version 2.0 build is "
         "specified by its manufacturer from about 60 Hz upward, so the low end of the heart "
         "sound band may be attenuated. Before any cardiac result on the device is reported, the frequency "
         "response of the whole acquisition chain will be measured with swept tones from "
         "20 Hz to 2,000 Hz, and any low-frequency loss will be reported as a hardware "
         "limitation rather than attributed to the classifier.", first=0)

H2("Evaluation Procedures")
para("Before analysis, each recording was assessed where technically possible for "
     "background noise, signal amplitude, signal-to-noise ratio, duration, clipping, "
     "motion artifact, missing or invalid samples, and insufficient signal, and "
     "classified as Good, Acceptable, Poor, or Invalid. Poor or invalid recordings were "
     "recommended for repetition rather than forced into a classification. Reference "
     "recordings were additionally reviewed by three physicians, a pulmonologist, a "
     "pediatric pulmonologist and a pediatrician, so that classifications could be checked "
     "against expert clinical judgement across adult and pediatric presentations. Reference labels were "
     "stored separately from model predictions.", first=0)

para("Six procedures were carried out with the completed prototype.", first=0, after=6)

p = para("Signal acquisition. Mean signal strength produced by the device was compared "
         "against that of a conventional acoustic stethoscope recorded under the same "
         "conditions. Both figures are reported in decibels. The study records did not "
         "keep the reference level, the make and model of the conventional stethoscope, "
         "or how its acoustic output was captured, so the two figures were not measured "
         "against a common reference; they are reported as indicative margins, not as a "
         "signal-to-noise ratio.", first=0, after=6, spacing=1.6)

para("Recording clarity. Recordings acquired with a conventional stethoscope and with "
     "Resondi were evaluated by three qualified healthcare professionals against predetermined "
     "recording-quality criteria, and rated good, acceptable, or poor.", first=0,
     after=2, spacing=1.6)

para("Ambient noise conditions. Recordings were obtained in three settings — a "
     "community area, a quiet room, and a hospital ward — with ambient noise measured in "
     "each.", first=0, after=6, spacing=1.6)

para("System response time. The duration of each processing stage was measured: device "
     "connection, recording, preprocessing, classification, and quality assessment.",
     first=0, after=6, spacing=1.6)

p = para("Classification agreement. Fifteen recordings classified by the model were "
         "compared against reference labels for the same recordings. Agreement was "
         "summarised as the proportion of matching classifications with a 95 percent "
         "Wilson score interval, and tested against the 25 percent agreement expected by "
         "chance across four categories using an exact binomial test at a 0.05 level of "
         "significance. No test of marginal homogeneity was applied, because such a test "
         "addresses the direction of disagreement rather than the extent of agreement and "
         "is without power at this sample size. Reference labels were stored separately "
         "from model predictions.", first=0, after=6, spacing=1.6)
para("The physicians' review was a confirmation of labels, not independent labelling. "
     "Each reviewed the respiratory sound samples together with the labels the "
     "researchers presented, judged them against the ICBHI 2017 categories, and "
     "certified on 21 August 2026 that the samples and their labels were consistent "
     "with recognised respiratory sound characteristics. The reviewers therefore saw "
     "the labels; their certificates do not record whether they also saw the model's "
     "output.", first=0, after=6, spacing=1.6)

para("Rebuilt classifier on device recordings. After the fusion network was placed in "
     "the Resondi application, the published application was run, read-only, on every "
     "lung recording stored in it that had audio (45 recordings). Of these, 33 entries "
     "were recordings made with the Resondi device (16 kHz, about 15 seconds), 26 of "
     "them unique, since some files had been uploaded more than once. For each recording "
     "the score of each class and the class with the highest score were recorded, using "
     "the application's own analysis function, and no result was saved to any patient "
     "record. None of these recordings has a reference label, so the procedure measures "
     "whether the network runs on device audio and how clearly it separates the classes, "
     "not whether its classifications are correct.", first=0, after=6, spacing=1.6)

p = para("End-user acceptance. Acceptance was assessed with 27 respondents across Puerto "
         "Princesa City, recruited by convenience sampling, using a questionnaire adapted "
         "from the Unified Theory of Acceptance and Use of Technology (Venkatesh, Morris, "
         "Davis, & Davis, 2003), together with three patients at a private hospital under "
         "the supervision of an attending physician who reviewed and consented to the "
         "procedure. Because respondents were not randomly selected, the results describe "
         "this group and are not generalised to the wider population. Items were rated on a "
         "five-point Likert scale and grouped into four constructs \u2014 performance "
         "expectancy, effort expectancy, social influence and facilitating conditions "
         "\u2014 together with a fifth group assessing the degree to which conformity with "
         "recognised medical-device standards (ISO 13485, ISO 14971, ISO/IEC 62304, ISO/IEC "
         "27001 and ISO 14155) influenced confidence in the device, reported here as "
         "facilitating conditions. Weighted mean, standard deviation and Cronbach\u2019s alpha "
         "were computed for each construct and interpreted against the five-point "
         "acceptance scale. Three items used a dichotomous response format and are reported "
         "as frequencies rather than means. Three behavioural-intention items and all "
         "open-ended items returned no responses and are not reported. The respondents "
         "rated the earlier version of the system, which ran the original classification "
         "model; the current version, with the rebuilt lung-sound classifier and the "
         "heart-sound models, has not yet been rated. Respondents were eligible if they "
         "were prospective users of the system, such as health workers and other "
         "authorised end users, or patients examined with it, and the system\u2019s "
         "purpose and limitations were explained to each before the survey was "
         "administered. No further eligibility rule, such as an age limit, was recorded.",
         first=0, after=6, spacing=1.6)

H2("Data Analysis")
p = para("Descriptive statistics were used to summarise recording clarity, response "
         "time, ambient noise, and signal strength. Classification agreement was "
         "reported as the proportion of recordings on which the model and the reference "
         "labels matched, with a 95 percent Wilson score interval and an exact one-sided "
         "binomial test against the 25 percent expected by chance.",
         first=0)
para("The rebuilt classifiers were judged primarily by balanced accuracy, the mean of "
     "the four per-class recalls, because healthy cycles make up about half of ICBHI and "
     "plain accuracy rewards a model that always answers Healthy; with four classes, "
     "chance is 25 percent. Plain accuracy, macro-averaged F1, per-class recall and "
     "Cohen's kappa are reported alongside it. Confidence intervals are 95 percent "
     "patient-level bootstrap intervals, resampling whole patients 1,000 times, because "
     "the cycles of one patient are not independent of one another. The cross-validated "
     "difference between the two architectures was tested with a paired patient "
     "bootstrap of 5,000 resamples, applying the same resampled patients to both models, "
     "with a one-sided p-value for the hypothesis that the fusion network is no better. "
     "Paired predictions on the same cycles were compared with McNemar's test, and the "
     "fold-level and patient-level differences with a paired t-test and a Wilcoxon "
     "signed-rank test as supporting analyses. On the unlabelled device recordings, the "
     "score of the top class was summarised by its range and median, against 25 percent "
     "for four equally likely classes.", first=0)
para("Model training and the bootstrap analyses were run in Python 3 with NumPy, SciPy "
     "and PyTorch. Every other statistic in this paper, and the statistical figures, were "
     "produced or reproduced with jamovi 2.7 (The jamovi project, 2025) through its R "
     "package jmv, from comma-separated files that accompany the paper.", first=0)

H2("Ethical Considerations")
para("The study was conducted under the supervision of the research adviser, John "
     "Lemuel J. Noche, of the Puerto Princesa City National Science High School research "
     "programme. "
     "Participation was voluntary throughout. Written consent forms and data recording "
     "sheets were used for monitoring and record-keeping, and the purpose and stated "
     "limitations of the system were explained to participants before any recording was "
     "made or any survey administered.", first=0)

para("Recordings of the three hospital patients were obtained under the guidance and "
     "direct supervision of an attending physician, who reviewed the procedure and "
     "consented to it. Recordings were stored without direct patient identifiers, and "
     "research exports exclude personally identifiable information. Lung sound "
     "recordings constitute sensitive personal information under Republic Act No. 10173, "
     "the Data Privacy Act of 2012, and were handled accordingly.", first=0)

para("The study was reviewed before any data were collected. The school's "
     "Institutional Review Board, a three-member panel of a registered nurse, an "
     "educator and the school administrator, approved it after full committee review "
     "on 16 July 2026 as minimal risk, with written informed consent required from "
     "participants aged 18 or over and no minors enrolled, and the school's Scientific"
     " Review Committee approved the research plan on 17 July 2026. Data were "
     "collected from 20 July to 28 August 2026, the start and end of experimentation in the "
     "research logbook. This was review at school level under "
     "the science fair rules, not review by a hospital or university research ethics "
     "committee; the clinical validation planned for the next phase will seek that "
     "review before it begins.", first=0)


# ═══════════════════════════════════════════════════ RESULTS
H1("IV. Results and Discussion")

para("The results are reported by research question, in the order the questions were "
     "set. Research Questions 1, 5 and 9 are answered from the field evaluation, which"
     " used the original classifier; Research Questions 2 to 4 from the device, the "
     "platform and the rebuilt analysis system, including the tests of the rebuilt "
     "lung-sound and heart-sound models; and Research Questions 6 to 8 by the three "
     "hypotheses. The section ends with the result for each of the study's nine "
     "objectives.", first=0)

H2("Research Question 1: Quality of the Recordings")
H3("Signal Acquisition")
para("Mean signal strength measured approximately 45 dB for Resondi against "
     "approximately 32 dB for a conventional acoustic stethoscope recorded under "
     "the same conditions. Because the decibel scale is logarithmic, the 13 dB "
     "difference corresponds to roughly 4.5 times the sound-pressure amplitude; it "
     "is not a ratio of the decibel values themselves. Signal strength alone does "
     "not establish better clinical performance; recording quality and "
     "classification accuracy bear on that separately.", first=0)

H3("Recording Clarity")
FIG(7, "Distribution of Recording Clarity Ratings",
    "r1_clarity.png", 4.3)

H3("Ambient Noise Conditions")
FIG(8, "Ambient Noise Levels Across Three Recording Environments",
    "r2_noise.png", 4.3)

para("These results answer Research Question 1 descriptively. In signal quality, "
     "Resondi recorded about 13 dB more than a conventional stethoscope; in clarity, "
     "93 percent of recordings were rated good or acceptable (Figure 9); and in noise level, "
     "recordings were made at ambient levels of 24, 35 and 42 dB, the last in a "
     "community setting (Figure 10).", first=0)

H2("Research Question 2: Specifications of the Smart Stethoscope")
para("In its current version 2.0 design, the Resondi smart stethoscope is a handheld unit that joins an "
     "acoustic chest piece to a digital microphone in a 3D-printed polylactic acid "
     "enclosure of 173 by 80 by 70 mm, with a 20 by 4 character display and two "
     "buttons, used to record at seven standardised lung sites and five cardiac sites."
     " Its components are an ESP32 microcontroller with built-in Wi-Fi, a digital MEMS"
     " microphone, a 32 GB microSD card and a 10,000 mAh battery; it records "
     "15-second, 16 kHz mono WAV files and serves its own Wi-Fi network and web page, "
     "so it works without internet. Its cost is a bill of materials of ₱2,775 and a "
     "fully loaded unit cost of ₱4,000. The field build tested in this study differed in "
     "two parts: it used an electret microphone on a MAX4466 amplifier board and "
     "communicated over Bluetooth Low Energy.", first=0)

# 25 Nov 2026 (user: show the budget as page 9 of the 83-page paper does, and break the device down into its parts).
import sys as _sys0
_sys0.path.insert(0, os.path.join(HERE, "..", "fig"))
import bom_v2  # noqa: E402
_pc = {k: f"{v / bom_v2.TOTAL * 100:.1f}" for k, v in bom_v2.CATS.items()}
para("Figure 11 takes the device apart into the parts of its bill of materials.", first=0)
FIG(11, "Exploded View of the Version 2.0 Device and Its Parts", "Resondi-Exploded-View.png", 6.1,
    note="Outer parts are rendered from the team's 3D model, whose proportions differ from the 173 by 80 by 70 mm "
         "enclosure. The internal parts are drawn from the bill of materials; their position inside the enclosure "
         "is illustrative.")
H3("Cost of Materials")
para("Table 2 and Figure 12 present the cost of materials of one version 2.0 unit, a total of ₱2,775.00. The parts "
     f"that capture the sound, the stethoscope set and the microphone, take the largest share at {_pc['Acoustic sensing']} "
     f"percent, followed by the power supply at {_pc['Power supply']} percent and the display and controls at "
     f"{_pc['Display and controls']} percent; the microcontroller that runs the device is {_pc['Microcontroller']} percent. "
     "Prices are preliminary Philippine-market estimates and vary with supplier and shipping. The total leaves out a "
     "battery protection circuit and a charging module, which the final design needs: the fully loaded unit cost of "
     "₱4,000 adds ₱625 for battery protection, charging and a production allowance and ₱600 for assembly, "
     "calibration and packaging.", first=0)
FIG(12, "Cost Breakdown of the Version 2.0 Device", "Resondi-Cost-Breakdown.png", 3.0,
    note="Percentages are rounded to one decimal place.")
TBL(2, "Cost of Materials of One Version 2.0 Device", bom_v2.table_rows(), [1.20, 0.68, 0.52, 0.60], total=True)

H3("Heart Mode")
para("Heart Mode was implemented on the device and in the application. It guides the "
     "operator through the five cardiac sites in order, records 15 seconds at each in the "
     "same 16 kHz WAV format as lung recordings, and files each recording by site for "
     "practitioner review; the heart-sound models described above can then be run on it. "
     "No quantitative evaluation of "
     "heart recordings made with the device was carried out in this study: signal strength, "
     "recording clarity and classification agreement were measured on lung recordings only. "
     "The heart-sound models were evaluated on public recordings instead, as reported "
     "below; the cardiologist's review of the CirCor labels had not been returned when this "
     "paper was written.", first=0)

H2("Research Question 3: Specifications of the Monitoring Platform")
para("The platform's user interface is a web application in English and Filipino with "
     "separate Lung and Heart modes, each guiding the user through its sites on a body"
     " diagram and filing every recording by site, with a recording history, a same-"
     "site comparison and trend charts. Its architecture has three tiers: the device, "
     "which records to its microSD card; the transfer, in which a phone joins the "
     "device's Wi-Fi, downloads the recordings and uploads them through the "
     "application's transfer page, since the automatic gateway is not yet built; and "
     "the platform, which stores each recording against the patient's record, runs the"
     " lung-sound and heart-sound models in the browser and presents every result to a"
     " practitioner. Role-based access separates patients, practitioners and "
     "administrators: a practitioner is verified by an administrator, may review only "
     "recordings in the specialisation they hold, respiratory, cardiac or both, and "
     "can read only the cases a patient has sent to them, which row-level security on "
     "each record enforces. For data management, each recording is stored as a private"
     " audio file with its site, mode, examination and date; each analysis is saved "
     "separately with the name of the model that produced it; deleting a recording "
     "deletes its analyses, plans, reviews and submissions; and an approved recording "
     "can be exported as a PDF report.", first=0)

# 18 Nov 2026 (user: "in theirs, they have the app ui in the results and discussion"): the application's
# screens, captured from the live app at phone size; names, ages and file names masked (build/app_ui/).
para("Figure 13 shows the screens a patient uses. The welcome screen states, before sign-in, that the analysis is"
     " a screening aid produced by a model that has not completed clinical validation. The dashboard offers the "
     "two modes, Lung Auscultation and Heart Auscultation, each with its own placement guide. A full examination "
     "is chosen as the standard seven lung sites or the full cardiopulmonary set of twelve sites, and the guides "
     "number each site on a body diagram, from the trachea through the six lung fields and from the aortic area "
     "to the mitral area, with the landmark and what to listen for at each.", first=0)
FIG(11, "Patient Screens of the Resondi Application", "ui1_patient.png", 6.3,
    note="Captured from the live application at phone size; the patient's name is masked.")
para("Figure 14 shows how recordings enter the platform and are kept. The transfer page walks the user through "
     "joining the device's RESONDI_WIFI network, downloading the recordings from the device page at "
     "192.168.4.1 and uploading them once the phone is back online. The history lists every recording by site and "
     "shows whether it has been sent to a practitioner; each recording opens to its audio and its sound analysis; "
     "and the trend view plots a recording score from 0 to 100 over time, which the screen itself describes as a "
     "tracking summary of the model's classification, not a medical assessment of lung function.", first=0)
FIG(12, "Recording Transfer, History, Result and Trend Screens", "ui2_records.png", 6.3,
    note="Captured from the live application at phone size; the recording's file name is masked.")
para("Figure 15 shows the practitioner and administrator side. A verified practitioner sees the recordings "
     "waiting for review and the patients assigned to them; a patient's record shows the profile and every "
     "recording with its analysis, labelled as a model score rather than an accuracy and, for recordings scored by"
     " the withdrawn first model, marked as such. The practitioner approves, disapproves or requests further "
     "review of each recommended breathing exercise before the patient can start it. The administrator manages "
     "accounts, verifies practitioners' credentials and reviews an activity log, and is stated on screen not to "
     "act as a medical practitioner.", first=0)
FIG(13, "Practitioner and Administrator Screens", "ui3_practitioner.png", 6.3,
    note="Captured from the live application at phone size; account and patient names and the patient's age are "
         "masked.")

H2("Research Question 4: Specifications and Performance of the Sound Analysis System")
para("The analysis system preprocesses audio to 16 kHz mono and cuts it into 1-second "
     "windows, each band-limited to 100 to 3,900 Hz and levelled before its features "
     "are computed. Its feature representations are MFCC, a log-power spectrogram and "
     "a chromagram; each feeds its own CNN branch, and the fusion architecture "
     "concatenates the three branch outputs into a dense layer with a softmax over the"
     " four sound classes. Heart sounds are analysed by two separate models, a "
     "segmentation model that times S1 and S2 and gives the heart rate, and a murmur "
     "model. The subsections below report how the original classifier and the rebuilt "
     "models performed.", first=0)

H3("Classification Agreement")
para("Of fifteen recordings compared against reference labels, six produced matching "
     "classifications, an agreement of 40 percent with a 95 percent Wilson score interval "
     "of 19.8 to 64.3 percent (Figure 16). That interval contains both the 25 percent agreement "
     "expected by chance across four categories and a usefully performing classifier, and "
     "the present sample cannot distinguish between them. An exact binomial test against "
     "chance returned p = 0.148; eight of fifteen agreements would have been required to "
     "reach conventional significance. Fifteen recordings is too small a sample to support "
     "a conclusion about accuracy, and none is drawn here. These fifteen recordings were "
     "classified by the original model. The rebuilt models reported below were "
     "not scored against these reference labels.", first=0)

FIG(10, "Classification Agreement Against Reference Labels, with the 95% "
        "Wilson Interval", "r4_agreement.png", 4.6)

H3("Rebuilt Classifier: Pre-Specified Test")
para("Table 3 gives the rebuilt models' scores on the 31 ICBHI test patients, none of "
     "whom contributed to training. Every model scored above the 25 percent expected by "
     "chance, but on ICBHI data alone no change of architecture moved balanced accuracy "
     "clearly beyond the mid-thirties, and every confidence interval overlapped. The "
     "fusion network trained on ICBHI and SPRSound, named as the primary model before the "
     "test was read, reached 39.4 percent, the best pre-specified result, and 57.2 percent "
     "on the 230 SPRSound test children. Models trained on ICBHI alone scored between 23 "
     "and 32 percent on those children.", first=0)
TBL(2, "Balanced Accuracy of the Rebuilt Models on the 31 ICBHI Test Patients",
    [["Model", "Training data", "Balanced accuracy (95% CI)", "Plain accuracy", "Macro F1"],
     ["MFCC network, Edge Impulse 8-bit build (in the app 10–13 Nov)", "ICBHI", "33.5%", "44.0%", "—"],
     ["MFCC network, best of ten versions", "ICBHI", "35.0% (24.6–40.3)", "38.5%", "0.31"],
     ["Late fusion of three single networks", "ICBHI", "32.9% (23.9–40.9)", "—", "0.31"],
     ["Three-branch fusion network", "ICBHI", "36.7% (26.0–43.0)", "—", "0.36"],
     ["Three-branch fusion network", "ICBHI + SPRSound", "39.4% (28.4–44.6)", "47.2%", "0.38"]],
    [2.15, 1.05, 1.45, 0.75, 0.6],
    "Chance is 25 percent. Intervals are patient-level bootstrap intervals. Each row was "
    "named as its round's primary model before the test patients were scored, except the "
    "Edge Impulse build, which was checked against the same patients after export.")

H3("Rebuilt Classifier: Cross-Validation Across All 126 Patients")
para("Because 31 test patients give wide intervals, the two architectures were also "
     "compared by five-fold cross-validation, in which each of the 126 ICBHI patients and "
     "6,898 cycles was classified once by a model that had not seen that patient. Table 4 "
     "gives the result. The fusion network trained with SPRSound reached 40.0 percent "
     "balanced accuracy against 34.0 percent for the app's MFCC design. The paired "
     "difference was 5.9 percentage points (95 percent CI 1.0 to 10.3; one-sided "
     "p = 0.008), and the fusion network scored higher on 14 of the 15 seed-and-fold "
     "comparisons, the fifteenth being a tie. It improved recall on every class (Table 4). "
     "On the 230 SPRSound test children, the fold models averaged 56 percent.", first=0)
TBL(3, "Five-Fold Cross-Validation Across All 126 ICBHI Patients (6,898 Cycles)",
    [["Measure", "MFCC network, ICBHI only", "Fusion network, ICBHI + SPRSound"],
     ["Balanced accuracy (95% CI)", "34.0% (30.4–38.2)", "40.0% (35.9–43.5)"],
     ["Fold mean ± SD", "34.1 ± 2.7", "39.9 ± 2.8"],
     ["Plain accuracy", "36.6%", "43.0%"],
     ["Macro F1", "0.31", "0.37"],
     ["Recall: Crackles", "50%", "56%"],
     ["Recall: Healthy", "33%", "40%"],
     ["Recall: Wheezing", "31%", "38%"],
     ["Recall: Wheezing with Crackles", "22%", "26%"],
     ["SPRSound test children", "—", "56%"]],
    [2.2, 1.85, 2.05],
    "The fusion network is the average of three training seeds. Intervals are "
    "patient-level bootstrap intervals.")
para("The supporting analyses agreed. Across the five folds the fusion network's "
     "balanced accuracy was higher in every fold, by a mean of 5.8 points (paired "
     "t(4) = 4.75, p = 0.009; Figure 17). Of the 126 patients, 69 had more of their cycles "
     "classified correctly by the fusion network, 39 fewer, and 18 the same (Wilcoxon "
     "signed-rank p = 0.009; Figure 18). Cycle by cycle, the fusion network alone was "
     "right on 1,277 cycles and the MFCC network alone on 831 (McNemar p < 0.001), though "
     "this last test treats cycles as independent and overstates the certainty; the "
     "patient-level analyses are the ones to rely on. Figure 19 shows where each model's "
     "errors fall.", first=0)
FIG(13, "Balanced Accuracy of the Two Architectures in Each of the Five Folds",
    "j1_cv_folds.png", 3.0,
    note="Produced in jamovi (jmv, paired-samples t-test, descriptives plot). Points are "
         "fold means with 95% confidence intervals.")
FIG(14, "Share of Each Patient's Cycles Classified Correctly, by Architecture",
    "j2_cv_patients.png", 3.0,
    note="Produced in jamovi (jmv, paired-samples comparison of 126 patients).")
FIG(15, "True Class Against Predicted Class in Cross-Validation",
    "j3_cv_confusion.png", 3.0,
    note="Produced in jamovi (jmv, contingency tables, row percentages). Each bar group is "
         "one true class; bars show how its cycles were classified. The two panels have "
         "different vertical scales.")


H3("Rebuilt Classifier: Effect of a Leaky Division")
para("Table 5 shows what the same fusion network scores when the division of the data "
     "leaks. Trained and tested on patients it had never heard, it reached 39.0 percent "
     "balanced accuracy. When the cycles were divided at random, so that 119 of 119 test "
     "patients also had breaths in training, the score rose to 58.2 percent. When the "
     "one-second windows were divided at random, it reached 52.5 percent, a smaller rise "
     "because only the training portion of the database had been cut into overlapping "
     "windows. Scored on its own training cycles, it reached 78.5 percent. The model and "
     "its training were identical in every row; only the division changed. The higher "
     "figures measure how well the network recognises audio it has already heard, not how "
     "well it classifies a new patient, and are not reported as its accuracy.", first=0)
TBL(4, "The Same Fusion Network Scored on an Honest and on Leaky Divisions of ICBHI 2017",
    [["Division of the data", "Test patients heard in training", "Balanced accuracy", "Plain accuracy"],
     ["By patient (five-fold cross-validation): the reported figure", "None", "39.0%", "41.1%"],
     ["Breathing cycles at random", "119 of 119", "58.2%", "56.6%"],
     ["One-second windows at random", "Pieces of the same breath (3,822 of 4,008 test cycles)", "52.5%", "50.2%"],
     ["Scored on its own training cycles", "All", "78.5%", "68.9%"]],
    [2.25, 1.75, 1.05, 1.05],
    "One training seed (11), so the first row is 39.0 percent rather than the 40.0 percent of "
    "the three-seed ensemble. Chance is 25 percent. The leaky rows are a demonstration of "
    "the flaw and must not be quoted as the model's accuracy.")

H3("Heart-Sound Models on CirCor Test Patients")
para("Table 6 gives the heart-sound results on the 189 CirCor test patients, none of "
     "whom contributed to training, to the decoding setting or to the murmur "
     "threshold. The timing model found 96.8 percent of reference S1 sounds and 97.3 "
     "percent of S2 sounds within 100 ms, with a mean onset error of 15 and 12 ms, and"
     " 95.7 and 96.5 percent of its detections were real. Its heart rate was within 5 "
     "beats per minute of the reference on 85 percent of 631 recordings and within 10 "
     "on 96 percent: a mean absolute error of 3.0 beats per minute (95 percent CI "
     "2.5–3.6), against 35.4 for the untrained baseline, which often locked onto half "
     "or double the true rate. The error had almost no bias (+0.1 beats per minute), "
     "but its 95 percent limits of agreement were −13.7 to +14.0, because a few "
     "recordings were read badly wrong; Figure 20 shows that these were mostly fast "
     "rates read too low and slow rates read too high. Reference rates ranged from 49 "
     "to 171 beats per minute, median 103, as expected in children.", first=0)
para("The murmur detector did not reach its pre-specified target. On the validation "
     "patients the chosen threshold gave 80.6 percent sensitivity; on the test "
     "patients it found 24 of the 36 with a murmur, 66.7 percent (95 percent CI "
     "50.0–81.8), and wrongly flagged 4 of the 139 without one, a specificity of 97.1 "
     "percent. Its AUROC of 0.96 shows that it ranks patients well, but the threshold "
     "carried over from the validation patients was too strict for the test patients, "
     "and it was not adjusted after the test was read. Of the 14 test patients whose "
     "murmur status the dataset marks unknown, it flagged 2. The 12 missed murmurs are"
     " the result to weigh: a screening flag that misses one murmur in three cannot be"
     " used to rule a murmur out.", first=0)
para("Placed in the application, the models gave the same results through the device's"
     " 16 kHz audio path as through the original one. On the 631 test recordings, the "
     "heart-rate error was 3.03 beats per minute against 3.01, and the murmur flag was"
     " the same on 99.7 percent of recordings, so the extra resampling costs nothing "
     "measurable. The JavaScript code gave the same heart rate and murmur flag as the "
     "Python reference on 25 of 25 recordings, and in the browser on 8 of 8, where an "
     "analysis took under a second once the models, about 2 MB, had downloaded. These "
     "checks show that the application computes what was tested; they say nothing "
     "about how the models perform on the Resondi microphone.", first=0)
TBL(5, "Heart-Sound Models on 189 CirCor Test Patients",
    [["Model", "Measure", "Result (95% CI)"],
     ["Heart-sound timing", "S1 found within 100 ms; detections that are real", "96.8%; 95.7%"],
     ["Heart-sound timing", "S2 found within 100 ms; detections that are real", "97.3%; 96.5%"],
     ["Heart-sound timing", "Mean onset error, S1; S2", "15 ms; 12 ms"],
     ["Heart rate (631 recordings)", "Mean absolute error", "3.0 BPM (2.5–3.6); untrained baseline 35.4 (29.9–40.8)"],
     ["Heart rate (631 recordings)", "Within 5 BPM; within 10 BPM", "85%; 96%"],
     ["Murmur (175 patients)", "Sensitivity (pre-specified target 80%)", "66.7% (50.0–81.8): 24 of 36"],
     ["Murmur (175 patients)", "Specificity", "97.1% (93.9–99.3): 135 of 139"],
     ["Murmur (175 patients)", "Positive predictive value", "85.7% (71.0–96.7)"],
     ["Murmur (175 patients)", "F1-score; Cohen's kappa", "0.75 (0.61–0.86); 0.70 (0.54–0.82)"],
     ["Murmur (175 patients)", "AUROC", "0.96 (0.92–0.99)"]],
    [1.7, 2.35, 2.05],
    "CirCor recordings: children and adolescents in Brazil, recorded with an electronic "
    "stethoscope. Murmur measures are per patient, a patient counting as positive when any "
    "site is; the 14 patients labelled unknown are excluded and reported in the text. "
    "Neither model has been tested on Resondi device recordings.")
FIG(17, "Estimated Against Reference Heart Rate on 631 CirCor Test Recordings",
    "r6_heart_rate.png", 2.2, span=True,
    note="Each point is one recording. The dashed line is perfect agreement and the shaded "
         "band is within 5 beats per minute. Teal points are more than 10 beats per minute "
         "off. Reference rates come from the dataset's annotated S1 boundaries.")

H3("Summary of the Model Results")
para("Table 7 brings together the results of the models now running in the application: "
     "the lung fusion network and the two heart-sound models. Every figure comes from "
     "public datasets on patients the models never heard in training; none comes from "
     "Resondi device recordings.", first=0)
TBL(6, "Accuracy of the Lung Fusion Network and the Heart-Sound Models",
    [["Model", "Test", "Measure", "Result (95% CI)"],
     ["Lung fusion network (MFCC, spectrogram, chromagram; ICBHI + SPRSound)",
      "Five-fold cross-validation, 126 ICBHI adults", "Balanced accuracy; accuracy; macro F1",
      "40.0% (35.9–43.5); 43.0%; 0.37"],
     ["Lung fusion network", "Held-out SPRSound children, 230 patients", "Balanced accuracy",
      "56.3%"],
     ["Lung fusion network", "Single pre-specified test, 31 ICBHI adults",
      "Balanced accuracy; accuracy; macro F1", "39.4% (28.4–44.6); 47.2%; 0.38"],
     ["Lung fusion network", "Single pre-specified test, 230 SPRSound children",
      "Balanced accuracy", "57.2% (46.7–63.4)"],
     ["MFCC network, ICBHI only (comparison)", "Five-fold cross-validation, 126 ICBHI adults",
      "Balanced accuracy", "34.0% (30.4–38.2)"],
     ["Fusion against MFCC", "Same 126 adults, paired", "Difference in balanced accuracy",
      "+5.9 points (+1.0 to +10.3), p = .008"],
     ["Heart-sound timing", "189 CirCor test patients", "S1 found; S2 found (within 100 ms)",
      "96.8%; 97.3%"],
     ["Heart rate", "631 CirCor test recordings", "Mean absolute error; within 5 BPM",
      "3.0 BPM (2.5–3.6); 85%"],
     ["Murmur detection", "175 CirCor test patients", "Sensitivity (target 80%)",
      "66.7% (50.0–81.8)"],
     ["Murmur detection", "175 CirCor test patients", "Specificity; AUROC",
      "97.1% (93.9–99.3); 0.96"]],
    [1.75, 1.6, 1.5, 1.25],
    "Chance for the four lung classes is 25 percent balanced accuracy. The lung rows "
    "come from Tables 3 and 4 and the text around them, and the heart rows from Table 6. The murmur detector missed its "
    "pre-specified 80 percent sensitivity. None of these models has been tested on "
    "labelled Resondi device recordings.")

# ═══════════════════════════════════════════════════ DISCUSSION
H2("Research Question 5: Response Time")
para("Figure 21 gives the mean time of each stage in the field system: device "
     "connection 4.55 seconds, sound recording 15.00 seconds, recording-quality "
     "assessment 144.68 seconds, signal preprocessing 20.91 seconds and "
     "classification output 3.97 seconds.", first=0)

FIG(9, "Mean Duration of Each Processing Stage",
    "r3_response.png", 5.9)

para("The quality check is the stage that limits use: it takes longer than the "
     "15-second recording it assesses, so at 14 captures a full lung and heart "
     "examination would take about 34 minutes of screening time. The rebuilt "
     "classifier is faster than the original: the fusion network took a median of 2.0 "
     "seconds per recording in the application, including fetching the audio, and the "
     "heart-sound models took under 1 second once loaded.", first=0)

H2("Research Question 6: Clean Versus Noise-Contaminated Recordings (Hypothesis 1)")
para("To test Hypothesis 1, Gaussian noise was added to every test window at signal-"
     "to-noise ratios of 20, 10 and 5 dB, and the same 1,051 cycles of the 31 ICBHI "
     "test patients were classified again by the single-branch MFCC network chosen on "
     "11 November, before the fusion network was adopted. Balanced accuracy fell from "
     "35.0 percent on clean audio to 26.6, 25.4 and 25.3 percent, that is, to chance. "
     "At each level McNemar's exact test found far more cycles turned from correct to "
     "incorrect than the reverse (20 dB: 183 against 75; 10 dB: 205 against 69; 5 dB: "
     "209 against 72; Holm-adjusted p < .001 at every level). The null hypothesis was "
     "therefore rejected: classification performance differs significantly between "
     "clean and noise-contaminated recordings, and noise even milder than the ward and"
     " community conditions measured in the field reduces the classifier to chance. "
     "The fusion network now in the application has not yet been tested under added "
     "noise.", first=0)

H2("Research Question 7: Reference-Dataset Versus Device Recordings (Hypothesis 2)")
para("Hypothesis 2 could not be tested: no Resondi device recordings with independent,"
     " clinician-assigned labels exist yet, and the 15 field-test recordings are not "
     "linked to their reference labels in the study records. What can be reported is "
     "how the networks behave on device recordings without labels.", first=0)

para("The fusion network ran without error on all 45 stored lung recordings, at a "
     "median of 2.0 seconds per recording including fetching the audio. On the 26 unique "
     "recordings made with the Resondi device, it chose Healthy for 16, Wheezing with "
     "Crackles for 6, Wheezing for 3 and Crackles for 1. The score of the chosen class "
     "ranged from 31 to 66 percent, with a median of 41 percent (Figure 22). On the same "
     "device files, the Edge Impulse build that the fusion network replaced had given top "
     "scores of only 27 to 34 percent (median 30 percent), close to the 25 percent of four "
     "equally likely classes. The fusion network therefore separates the classes more "
     "clearly on device audio. Whether its choices are correct cannot be read from these "
     "recordings, because none of them has a reference label.", first=0)
FIG(16, "Top-Class Score of the Deployed Fusion Network on 26 Resondi Device "
        "Recordings", "r5_device.png", 6.0,
    note="Each point is one recording, placed in the row of the class the network chose. "
         "The shaded band is the range of top-class scores the previous Edge Impulse build "
         "gave on the same device files. No recording has a reference label, so the chart "
         "shows how decisive the network is, not how accurate.")

H2("Research Question 8: Recording Quality of a Conventional Stethoscope Versus Resondi (Hypothesis 3)")
para("Hypothesis 3 was not tested inferentially, because the paired raw measurements "
     "behind the 45 dB and 32 dB figures were not retained. Descriptively, Resondi "
     "recorded a signal about 13 dB stronger than the conventional stethoscope, about "
     "4.5 times the amplitude, and 93 percent of its recordings were rated good or "
     "acceptable. These are indicative margins rather than a test of difference, so "
     "the null hypothesis can be neither rejected nor retained on the present data.", first=0)

H2("Research Question 9: End-User Acceptance")
para("Twenty-seven respondents completed the acceptance questionnaire on the earlier "
     "version of the system, which ran the original classification model: 13 patients, "
     "13 general respondents and one health practitioner. Across the twelve five-point "
     "Likert items, overall acceptance was 3.95, interpreted as Agree.", first=0)

para("Performance expectancy and effort expectancy each returned a weighted mean of "
     "4.09 (SD = 0.59 and 0.60 respectively), both interpreted as Agree. Facilitating "
     "conditions returned 3.84 (SD = 0.61) and social influence 3.63 (SD = 1.21), "
     "likewise interpreted as Agree.")

para("One physician also rated the prototype on the study's instrument validation form"
     " on 29 August 2026, giving the highest rating, 5 of 5, for general relevance, "
     "functionality, performance and usability, accessibility, and reliability, and "
     "rated it 4 of 5 for clinical relevance, clinical appropriateness and information"
     " clarity, and 3 of 5 for patient safety and clinical usefulness. This is one "
     "expert's judgement, not an end-user result.")

para("Internal consistency varied across constructs. Effort expectancy reached "
     "acceptable reliability (\u03b1 = 0.76). Facilitating conditions (\u03b1 = 0.59) and "
     "performance expectancy (\u03b1 = 0.51) fell below the conventional 0.70 "
     "threshold. With three to five items per construct and 27 respondents these "
     "values are reported as provisional, and the constructs are presented "
     "descriptively rather than as validated scales. Social influence is represented "
     "by a single item, for which no alpha is computed.")

p = para("Dichotomous items are reported as frequencies. Twenty-one of 27 respondents "
         "(78 percent) indicated that peers or colleagues encourage use of the device, "
         "and 20 of 27 (74 percent) reported that their institution provides resources "
         "to use it effectively. Access to training and technical support was the least "
         "certain response: 12 respondents (44 percent) answered \u2018maybe\u2019, 8 "
         "(30 percent) \u2018yes\u2019 and 7 (26 percent) \u2018no\u2019. Eleven "
         "respondents (41 percent) reported prior experience with medical devices or "
         "health applications.")
para("The study's full report states that the three patients recorded at the private "
     "hospital also took part in the acceptance survey; the records do not show whether "
     "all three are among the 27 responses analysed here.")

para("Mapped to the five aspects named in Research Question 9, effort expectancy is "
     "the closest measure of user-friendliness and usability (4.09) and performance "
     "expectancy of perceived usefulness for community-based monitoring (4.09). "
     "Functionality was rated only by the physician validator (5 of 5), and durability"
     " was not measured, so the answer to Research Question 9 is partial. These ratings are of the earlier version; acceptance of the current "
     "version, with the rebuilt classifier and the heart-sound models, has not yet been "
     "surveyed.", first=0)

H2("Research Question 10: Preferences for Instructional Support")
para("Research Question 10 is not yet answered. The questionnaire contained no items "
     "on diagram-based zone guidance, manual clarity, ease of learning or app "
     "navigation, and its open-ended items returned no responses. The nearest evidence"
     " is that access to training and technical support was the least certain item: 12"
     " of 27 respondents (44 percent) answered maybe, 8 (30 percent) yes and 7 (26 "
     "percent) no. A short survey on the four named aspects, given after a guided "
     "examination, is needed to answer it.", first=0)

H2("Research Question 11: Longitudinal Monitoring and Rehabilitation Support")
para("The functions behind the last three objectives were built and run in the "
     "application, but none was evaluated with users. For longitudinal comparison, a "
     "recording's page shows the two most recent recordings from the same anatomical "
     "site side by side, with each one's classification and the number of days between"
     " them, and a four-week chart sets the number of exercises a patient completed "
     "each week against the share of that week's lung recordings classified as normal."
     " For rehabilitation support, each lung result generates a suggested breathing-"
     "exercise plan matched to its sound class, and each heart recording a cardiac "
     "activity plan; no exercise can be started until a practitioner with the matching"
     " specialization has approved it, a guided session player then leads the patient "
     "through it, and each completed session is recorded. For practitioner review, a "
     "verified practitioner sees only the recordings a patient has sent to them, "
     "listens to each, reads its AI-assisted result, and approves, disapproves, or "
     "returns each recommended exercise with a comment. The application has no "
     "separate control for overriding the classification label itself, so a "
     "practitioner who disagrees with it records that in the comment.", first=0)
para("None of these functions has been measured. No patient was recorded repeatedly "
     "over time, so no change between visits has been observed; no rehabilitation "
     "outcome was recorded; and the number of results reviewed and the time a review "
     "takes were not measured. They are reported as built, not as shown to work.", first=0)

H2("Results by Objective")
para("Against the nine objectives set out in the introduction, the results stand as "
     "follows.", first=0)
for n, txt in enumerate([
    "Smart stethoscope that records and organizes lung sounds by site: achieved. The "
    "device records at each standardized site and files every recording by site, and "
    "it produced a signal about 13 dB stronger than a conventional stethoscope.",
    "Guided auscultation through a standardized sequence: achieved. The application "
    "guides the user through the seven lung sites in a fixed order (Figure 3).",
    "Guided cardiac auscultation in Heart Mode: achieved. Heart Mode guides recording"
    " at the four valve areas and Erb's point; heart recordings made with the device "
    "have not been evaluated quantitatively.",
    "Assessment of recording quality: achieved in part. Ninety-three percent of "
    "recordings were rated good or acceptable, but the automated quality check, at "
    "145 seconds a recording, is too slow to run before every classification.",
    "AI-assisted classification of respiratory sound patterns: achieved in part. The "
    "classifier runs in the application; its rebuilt form scores 40.0 percent "
    "balanced accuracy on unseen ICBHI patients against 25 percent by chance, and its"
    " accuracy on Resondi device recordings has not been measured.",
    "AI-assisted analysis of heart sounds: achieved in part. On CirCor test patients "
    "the heart-rate error was 3.0 beats per minute and murmur sensitivity 66.7 "
    "percent, short of the 80 percent target; both models run in the application but "
    "have not been tested on device recordings.",
    "Longitudinal monitoring across visits: built, not evaluated. Same-site "
    "comparison and the four-week trend run in the application, but no patient has "
    "repeated recordings in the study data.",
    "Rehabilitation support: built, not evaluated. Exercise plans are released only "
    "after practitioner approval and completion is recorded; no rehabilitation "
    "outcome was measured.",
    "Practitioner review workflow: built, not evaluated. Practitioners review only "
    "the cases sent to them and decide on each recommendation; review volume and time"
    " were not measured.",
], 1):
    p = para(f"{n}. {txt}", first=0, after=4, spacing=1.6)
    p.paragraph_format.left_indent = Inches(0.35)

H2("Discussion")

para("The results separate cleanly into two groups. Signal acquisition, recording "
     "clarity, and operation across ambient conditions support the conclusion that the "
     "device captures usable respiratory audio in the settings it is intended for. "
     "Classification agreement does not support any conclusion at all, and the reasons "
     "are worth stating precisely rather than softening.", first=0)

H2("Acquisition and Clarity")
para("The device produced a measurably stronger signal than a conventional acoustic "
     "stethoscope under matched conditions, and 93 percent of recordings were rated good "
     "or acceptable. Recordings remained usable at the highest ambient noise level "
     "tested, 42 dB in a community area, although against a 45 dB signal that setting "
     "leaves only about 3 dB of margin. Taken together these findings "
     "indicate that acquisition is not the limiting component of the system. The "
     "7 percent of recordings rated poor is a more informative figure than the 68 percent "
     "rated good, because at its present speed the automated quality check is impractical "
     "to run before every classification, so poor recordings can still reach the "
     "classifier.", first=0)

H2("Interpretation of the Classification Result")
para("Agreement of 40 percent on fifteen recordings should not be read as a performance "
     "estimate, in either direction. The 95 percent Wilson confidence interval on six of "
     "fifteen extends from approximately 19.8 percent to 64.3 percent — an interval 44 "
     "percentage points wide, which contains both chance performance and a potentially "
     "useful classifier. A sample of this size cannot distinguish between them.", first=0)

para("Chance performance is itself class-dependent. With four classes, the expected "
     "agreement by chance alone is 25 percent, and the observed 40 percent corresponds "
     "to a Cohen's kappa of approximately +0.20, conventionally described as slight to "
     "fair. This is a weak result rather than a null one, but it rests on fifteen "
     "observations and no inference should be drawn from it.")

p = para("No test of marginal homogeneity is reported for the agreement comparison, and the "
         "reason is worth stating because such a test is a natural thing to reach for. "
         "McNemar\u2019s test evaluates whether a model errs more often in one direction than "
         "the other \u2014 the symmetry of disagreement \u2014 and not whether two sets of labels "
         "agree. A non-significant result would indicate an absence of detectable "
         "asymmetry, which is compatible with a classifier of any quality including one "
         "performing at chance, and absence of evidence is not evidence of equivalence. At "
         "fifteen paired observations the test would in any case be without power. "
         "Agreement is therefore reported as the proportion of matching classifications "
         "with its Wilson interval and tested against chance with an exact binomial test. "
         "The test does have a proper use in this programme: comparing successive model "
         "versions on the same fixed test partition, where the paired predictions make it "
         "the correct instrument. That use is set out in the evaluation plan below.",
         first=0)

H2("Response Time as a Usability Constraint")
para("Quality assessment at 145 seconds dominates total elapsed time, exceeding the "
     "combined 44 seconds of connection, recording, preprocessing, and classification by "
     "more than a factor of three. Across a full seven-site examination this stage alone "
     "would contribute roughly seventeen minutes, which is not compatible with the consultation "
     "times available in a rural health unit. Reducing this duration is a higher "
     "development priority than any improvement in classification accuracy, because a "
     "system that is not used produces no classifications to improve.", first=0)

H2("What the Classifier Rebuild Shows")
para("The rebuild changes how the classification result should be read, though not the "
     "field figure itself. The 40 percent field agreement belongs to the original model, "
     "whose training was flawed; it is neither confirmed nor contradicted by the rebuilt "
     "models, which have not been scored against labelled device recordings. What the rebuild provides "
     "is the first estimate of the classifier's performance that is free of patient "
     "leakage: about 34 to 35 percent balanced accuracy for the original MFCC design on "
     "unseen patients, and about 40 percent for the fusion network trained with the "
     "paediatric corpus, against 25 percent by chance.", first=0)
para("Two findings from the rebuild bear on what comes next. First, architecture alone "
     "did not help: on ICBHI data alone, the fusion network was not clearly better than "
     "the single MFCC network on the test patients, and a late-fusion average of three "
     "networks did no better. The gain appeared only when training data were added. "
     "Second, data that differ from the training data defeat the model. A division that "
     "left one stethoscope dominant in training produced a model that scored at chance on "
     "the others, and models trained on adults alone scored near chance on children. Both "
     "point the same way: the classifier will perform on Resondi recordings of Filipino "
     "patients only once it has been trained on them.", first=0)
para("The motivation for fusing representations is that the two abnormal classes have "
     "opposite acoustic signatures. A crackle is a brief, broadband, discontinuous event, "
     "well represented in a spectrogram; a wheeze is a continuous musical sound defined by "
     "pitch, which a chromagram represents directly. The rebuilt MFCC network was indeed "
     "weakest on wheezes on the test patients (11 percent recall), and the fusion network "
     "trained with SPRSound raised wheeze recall to 24 percent on those patients and to "
     "38 percent in cross-validation. Wheezing remains the weakest single class.", first=0)
para("These figures should not be compared with the 95 to 99 percent reported by some "
     "studies on ICBHI, including Tariq et al. (2022). Those studies usually classify the "
     "patient's diagnosis rather than the sound of each breath, and divide recordings "
     "at random, so that a patient's audio appears in both training and testing, which is "
     "the same flaw found in this study's original model.", first=0)
para("Table 5 measures the size of that effect on this study's own network. The same model "
     "that scores 39.0 percent on unseen patients scores 58.2 percent once their other "
     "breaths are in training, and 78.5 percent on the breaths it was trained on, within "
     "the 71 to 84 percent the original model reported. The original model's division was "
     "leakier than either demonstration: five-second samples overlapping by four seconds, "
     "each labelled with the patient's diagnosis.", first=0)
para("The fusion network has since been put into the Resondi application. Because Edge "
     "Impulse provides no chromagram processing, it runs in the browser as an exported "
     "ONNX model, the three seeds combined in one file, with the band-limiting, levelling "
     "and feature extraction rewritten in JavaScript. The rewritten features gave the same "
     "top class as the Python originals on 600 of 600 validation windows. Run on 26 "
     "recordings already made with the Resondi device, the deployed fusion network gave "
     "top-class scores of 31 to 66 percent (median 41; Figure 22), against 27 to 34 "
     "percent for the "
     "Edge Impulse build it replaced. That shows it is more decisive on device audio, not "
     "that it is more often right: none of those recordings has a reference label.",
     first=0)

H2("The Heart Sound Component")
para("The heart component has moved past the acquisition side, unevenly. On the CirCor"
     " test patients, finding the heart sounds and reading heart rate from them worked"
     " well: S1 and S2 were found about 97 percent of the time, and heart rate was "
     "usually within 5 beats per minute. Murmur detection was weaker than planned. The"
     " model ranks patients well, yet at the threshold fixed in advance it missed 12 "
     "of 36 murmurs, so the 80 percent sensitivity reached on the validation patients "
     "did not hold on new ones. Reporting the miss rather than moving the threshold "
     "after the fact is the same discipline applied to the lung results. Setting the "
     "threshold on more validation patients, or letting the murmur model use the "
     "timing model's S1 and S2 positions to look inside systole and diastole "
     "separately, are the likely ways to close the gap.", first=0)
para("None of this has yet been shown on the Resondi device, and the lung results "
     "carry a direct warning: a classifier trained on one set of stethoscopes, or one "
     "age group, did not transfer to another. That warning applies with more force to "
     "the heart. CirCor was recorded from Brazilian children with a commercial "
     "electronic stethoscope; Resondi's patients include Filipino adults, whose "
     "resting heart rates are lower than the median of 103 in the test set, and its "
     "microphone may attenuate the lowest heart-sound frequencies. The models were "
     "also trained before the cardiologist's review of the CirCor labels was returned,"
     " the reverse of the order this study planned. The remaining work is therefore to"
     " complete that review, measure the device's low-frequency response, and test "
     "both models on heart recordings made with the Resondi device and labelled by a "
     "cardiologist. The models were placed in the application before that test, which "
     "this study had planned to come first. Each heart result in the application is "
     "therefore labelled as a screening aid, tested on public recordings of children "
     "and not on the device, with a note that a missing murmur flag does not rule a "
     "murmur out, and each goes to a cardiac practitioner for review.", first=0)

H2("Planned Extensions")
para("Two extensions are planned and were not implemented in the work reported here.",
     first=0)
para("The acquisition protocol extends from seven sites to nine. The two additional "
     "sites are an interscapular pair at T3–T4, beside the spine, which sample the "
     "posterior upper lobes; the tracheal reference and the six fields already recorded "
     "are retained. Figure 23 shows the nine sites on the body and Table 8 gives their "
     "landmarks.", first=0)

FIG(15, "Planned Nine-Site Acquisition Protocol",
    "p1_nine_sites.png", 4.6)

TBL(4, "Planned Nine-Site Acquisition Protocol",
    [["Site", "Surface landmark", "Region sampled"],
     ["Tc", "Suprasternal notch, over the trachea", "Central airway"],
     ["1", "2nd ICS, right midclavicular line", "Right upper lobe"],
     ["2", "2nd ICS, left midclavicular line", "Left upper lobe"],
     ["3", "4th–5th ICS, right mid-axillary line", "Right middle lobe"],
     ["4", "4th–5th ICS, left mid-axillary line", "Lingula"],
     ["5", "Interscapular T3–T4, right of the spine", "Right upper lobe"],
     ["6", "Interscapular T3–T4, left of the spine", "Left upper lobe"],
     ["7", "Infrascapular T8–T10, right", "Right lower lobe"],
     ["8", "Infrascapular T8–T10, left", "Left lower lobe"]],
    [0.75, 3.0, 2.0],
    "Sites 5 and 6 (interscapular) were not implemented at the time of evaluation; the "
    "other seven are the protocol evaluated here, renumbered. The tracheal reference is "
    "recorded first and provides a within-patient comparison for central airway sound, against "
    "which peripheral field recordings may be interpreted.")

para("The rationale for sampling more positions is empirical rather than procedural. In "
     "a study of 2,402 multi-channel lung recordings, classification accuracy rose from "
     "approximately 0.79 at a single auscultation position to approximately 0.92 across "
     "four (Kim et al., 2025). The present seven-site protocol already samples six lung "
     "fields; the extension adds the posterior upper fields, so that every lobe is "
     "sampled from both the front and the back of the chest.", first=0)

para("The second, and the one that matters most, is a local dataset: recordings of "
     "Filipino patients made on the Resondi device at the seven standardised sites, with "
     "each breathing cycle labelled independently by two clinicians who have not seen the "
     "model's output, collected with ethics approval and consent. The planned study "
     "separates the effect of each change, as Table 9 shows. Its first three rows have "
     "now been run on public data; the fourth cannot be run on any public dataset.",
     first=0)

TBL(5, "Separating the Effects of Architecture and Data",
    [["Run", "Classifier", "Training data", "Status", "Result (cross-validated or test)"],
     ["A", "MFCC network", "ICBHI 2017", "Done", "34.0% (CV); 35.0% (test)"],
     ["B", "Three-branch fusion", "ICBHI 2017", "Done", "36.7% (test); not clearly better than A"],
     ["C", "Three-branch fusion", "ICBHI + SPRSound", "Done", "40.0% (CV); 39.4% (test)"],
     ["D", "Three-branch fusion", "ICBHI + SPRSound + local Resondi recordings", "Planned",
      "—"]],
    [0.45, 1.25, 1.65, 0.7, 1.95],
    "The plan originally named HF_Lung_V1, a Taiwanese corpus, for run C. Its public "
    "download link no longer works, so SPRSound was used instead. All runs are scored on "
    "the same ICBHI patients, so that every comparison is made on the same people.")

H2("Intended Users and Deployment Context")
para("The system is designed for a specific tier of the Philippine health system, and the "
     "evaluation above is interpretable only against that setting. Care of the conditions "
     "Resondi addresses is delivered overwhelmingly at the primary level, and that level "
     "is where diagnostic equipment is scarcest: primary care accounts for roughly four "
     "percent of total health spending against about half for hospital care, and only "
     "half of Filipinos can reach a primary care facility within thirty minutes of travel "
     "(Department of Health, 2020).", first=0)

para("Department of Health facility registry figures record approximately 26,504 "
     "barangay health stations, 2,682 rural health units, and 836 municipal and city "
     "health centres nationwide (Department of Health, 2025) \u2014 roughly 30,000 public facilities at which "
     "auscultation forms part of routine assessment. Of these, the facilities Resondi "
     "can presently serve are narrower: about 3,518 rural health units and "
     "municipal or city health centres that have a resident clinician able to perform the practitioner review the platform depends "
     "on. Nursing and medical schools form a second group, for which the system functions "
     "as a teaching instrument rather than a clinical one. Table 10 gives the role of each group.", first=0)

TBL(3, "Intended Users and Their Role in the System",
    [["Group", "Role", "What the system provides"],
     ["Rural health units and municipal health centres",
      "Primary deployment site", "Guided acquisition, recording quality control, "
      "longitudinal comparison at a fixed site"],
     ["Midwives, nurses and barangay health workers",
      "Operators", "Placement guidance that reduces the skill required to obtain a "
      "comparable recording"],
     ["Rural health physicians and reviewing practitioners",
      "Review layer", "A queue of classified recordings to confirm, modify or reject; "
      "the diagnosis remains theirs"],
     ["Nursing and medical schools",
      "Teaching use", "Labelled recordings of real respiratory sounds for instruction "
      "and practice"],
     ["Patients in geographically isolated barangays",
      "Indirect beneficiaries", "A reviewable record where none previously existed, and "
      "supervised rehabilitation tracking"]],
    [1.75, 1.3, 2.85],
    "Patients are reached through institutional deployment under practitioner "
    "supervision rather than directly; the system is not designed for unsupervised "
    "home use.")

para("Two features of this setting bear directly on the design decisions reported in "
     "the methodology. The operator is frequently not a physician, which is why "
     "acquisition is guided rather than left to the user\u2019s judgement of where to "
     "listen. And connectivity is unreliable, which is why capture writes to local "
     "storage and synchronises later rather than requiring a live connection. Neither "
     "choice would be necessary in a tertiary hospital, and neither is incidental to the "
     "results reported here.", first=0)

para("Engagement with health facilities in Palawan so far consists of interviews. "
     "Between 18 and 22 August 2026, with written permission from each, the researcher"
     " interviewed practitioners at ACE Medical Center Palawan, Palawan Medical Plaza,"
     " Posas Medical Clinic, Palawan Coop Hospital (its tuberculosis DOTS programme) "
     "and the Provincial Health Office about the care of patients with lung disease. "
     "These were information-gathering interviews, not agreements to pilot or deploy "
     "the system, and no memorandum of agreement is in place.", first=0)

H2("Limitations")
para("Seven limitations bear directly on the interpretation of these findings.", first=0,
     after=6)
for lim in [
    "Sample size. Fifteen paired recordings are insufficient to establish classification "
    "performance. The confidence interval reported above is the direct consequence.",
    "The rebuilt models' accuracy on the device is unmeasured. Every accuracy figure for "
    "the rebuilt classifier comes from public databases recorded on other stethoscopes. "
    "The fusion network has been run on 26 recordings from the Resondi device, whose "
    "digital microphone sounds different, but none of them has a reference label, and "
    "the evidence above shows that a change of recording device alone can "
    "reduce a model to chance.",
    "Training data representation. ICBHI 2017 was collected from adults in Portugal and "
    "Greece, and SPRSound from children in China. Neither contains Filipino patients, and "
    "transfer to Philippine patients has not been established.",
    "Original evaluation partition. The original model's database was not partitioned "
    "patient-wise: overlapping segments of the same patient’s audio, each carrying "
    "the patient’s condition label, fell on both sides of every split. Its scores on "
    "that database are inflated and are not reported as evidence of performance.",
    "Repeated use of the test patients. The 31 ICBHI test patients were scored three "
    "times, once per round, each time with the primary model fixed in advance. All three "
    "results are reported, and the cross-validation across all 126 patients guards "
    "against a lucky split.",
    "The heart models are untested on the device, although they run in the application. "
    "The heart-sound timing, heart-rate and "
    "murmur results come from CirCor, children recorded in Brazil on another stethoscope. "
    "The models have not been run on Resondi heart recordings, the device's response at the "
    "lowest heart-sound frequencies has not been measured, and the models were trained "
    "before the cardiologist's check of the dataset's labels was returned. The murmur "
    "detector also missed its pre-specified sensitivity on the test patients.",
    "Speed of automated quality control. The system assesses whether ambient noise, weak "
    "signal, or motion artifact has rendered a recording unusable, but at a mean of 145 "
    "seconds per recording the check is too slow to run routinely before "
    "classification. In practice quality control therefore still rests largely with the "
    "reviewing practitioner.",
]:
    p = para(lim, first=0, after=6, spacing=1.6)
    p.paragraph_format.left_indent = Inches(0.35)

H1("V. Conclusion")
para("Resondi acquires, organises, and processes lung sound recordings at seven "
     "standardised sites and heart sound recordings at five, operates across the range of ambient conditions "
     "found in Philippine primary care, and produces a signal measurably stronger than "
     "that of a conventional acoustic stethoscope. These capabilities are demonstrated.",
     first=0)
para("The classification component is not yet demonstrated on the device. The original "
     "model's 40 percent agreement on fifteen recordings establishes neither that it works "
     "nor that it does not, and that model was later found to have been trained on leaked "
     "data. Rebuilt without that flaw, the classifier scores about 34 percent balanced "
     "accuracy on unseen patients, and about 40 percent once paediatric recordings are "
     "added and the three-branch fusion network is used, a statistically significant "
     "gain. The fusion network now runs in the application and separates the classes "
     "more clearly on device recordings than its predecessor, but its accuracy on those "
     "recordings has not been measured. The study is therefore best understood as establishing a working "
     "acquisition platform, together with an honestly measured classifier baseline, on "
     "which validation with local recordings can now proceed. The heart component is one "
     "step behind: its models time the heart sounds, read heart rate and detect murmurs on "
     "public recordings, the last short of its sensitivity target, and they now run in "
     "the application, but none has yet been tested on the device.")
para("The system does not replace clinical judgement and is not designed to. Every "
     "classification is presented to a practitioner who confirms, modifies, or rejects "
     "it, and no result is returned to a patient unreviewed. On the evidence reported "
     "here, that arrangement is not a precaution but a requirement.")

# 18 Nov 2026: acknowledgement, as in the AlagaVax paper; names as on the title page credits.
H1("Acknowledgement")
para("The researcher thanks the research advisers, John Lemuel J. Noche and Genelyn O. Bautista; the "
     "qualified scientist, Bemsor T. Caabay, MSc; the consultants, Kenneth Wilson O. Lim, MD, Sonia A. "
     "Ulanday, MD, and Riza Cornelle C. De La Bajan, MD, for their clinical guidance; fellow Team Wheezards "
     "members Hared Ray A. Cabrera and Jarred Paul G. Llacuna; the health workers, patients and other "
     "respondents who took part in the field evaluation and the acceptance survey; and Puerto Princesa City "
     "National Science High School.")

H1("Recommendations")
for rec in [
    "Score the fusion network against reference labels on recordings from the Resondi "
    "device, beginning with the "
    "fifteen field recordings if their reference labels can be recovered, and report "
    "balanced accuracy, per-class recall and Cohen's kappa with confidence intervals.",
    "Collect and clinically label a Philippine lung sound dataset on the Resondi device, "
    "with two independent, blinded clinicians per breathing cycle, ethics approval and "
    "consent, and quantify the gain from training on it.",
    "Confirm on labelled device recordings that the fusion network now running in the "
    "application performs as it did on the public test patients.",
    "Implement the nine-site protocol and evaluate it against the seven-site protocol on "
    "the same patients.",
    "Reduce the execution time of the automated recording quality assessment, now 145 "
    "seconds, to a duration that allows it to run before every classification within "
    "clinical workflow.",
    "Replace the 3D-printed polylactic acid enclosure, which softens at temperatures "
    "reachable inside a vehicle in tropical conditions, with a material suitable for "
    "field deployment, and repeat the signal-strength and recording-clarity measurements "
    "on the version 2.0 build before reporting any result as a property of the current "
    "device.",
    "Complete the cardiologist's blinded review of the 25 CirCor recordings and report "
    "agreement with the dataset's labels; if agreement is poor, retrain and revise the "
    "heart results.",
    "Raise the murmur detector's sensitivity to its 80 percent target on new patients, "
    "for example by setting the threshold on more validation patients or by using the "
    "heart-sound timing to examine systole and diastole separately, and add murmur timing.",
    "Measure the device's frequency response from 20 Hz, then test the heart-sound timing, "
    "heart-rate and murmur models on Resondi heart recordings labelled by a cardiologist, "
    "and keep every heart result in the application marked as a screening aid until that "
    "test is done.",
    "Conduct a prospective evaluation in a rural health unit measuring recordings "
    "captured per week, proportion of abnormal classifications reviewed, and time to "
    "review.",
]:
    p = para("• " + rec, first=0, after=6, spacing=1.6)
    p.paragraph_format.left_indent = Inches(0.35)

# ═══════════════════════════════════════════════════ REFERENCES
H1("References")
REFS = [
 "United Nations. (2015). Transforming our world: The 2030 Agenda for Sustainable Development "
 "(A/RES/70/1). https://sdgs.un.org/2030agenda",
 "3M. (2025). Littmann CORE digital stethoscope (Model 8480) [Product listing]. "
 "https://mdmaxx.com/products/3m-8480-littmann-core-digital-stethoscope",
 "Arts, L., Lim, E. H. T., van de Ven, P. M., Heunks, L., & Tuinman, P. R. (2020). The "
 "diagnostic accuracy of lung auscultation in adult patients with acute pulmonary "
 "pathologies: A meta-analysis. Scientific Reports, 10, 7347.",
 "Bohadana, A., Izbicki, G., & Kraman, S. S. (2014). Fundamentals of lung auscultation. "
 "New England Journal of Medicine, 370(8), 744–751.",
 "Department of Health. (2020). Philippine health facility development plan 2020\u20132040.",
 "Department of Health. (2025). National Health Facility Registry [Database]. "
 "https://nhfr.doh.gov.ph",
 "Philippine Statistics Authority. (2025). Registered deaths in the Philippines, 2024.",
 "Rocha, B. M., Filos, D., Mendes, L., Serbes, G., Ulukaya, S., Kahya, Y. P., Jakovljevic, "
 "N., Turukalo, T. L., Vogiatzis, I. M., Perantoni, E., Kaimakamis, E., Natsiavas, P., "
 "Oliveira, A., Jácome, C., Marques, A., Maglaveras, N., Paiva, R. P., Chouvarda, I., & "
 "de Carvalho, P. (2019). An open access database for the evaluation of respiratory sound "
 "classification algorithms. Physiological Measurement, 40(3), 035001.",
 "Hsu, F.-S., Huang, S.-R., Huang, C.-W., Huang, C.-J., Cheng, Y.-R., Chen, C.-C., "
 "Hsiao, J., Chen, C.-W., Chen, L.-C., Lai, Y.-C., Hsu, B.-F., Lin, N.-J., Tsai, W.-L., "
 "Wu, Y.-L., Tseng, T.-L., Tseng, C.-T., Chen, Y.-T., & Lai, F. (2021). Benchmarking of "
 "eight recurrent neural network variants for breath phase and adventitious sound "
 "detection on a self-developed open-access lung sound database \u2014 HF_Lung_V1. "
 "arXiv:2102.03049.",
 "Kim, Y., Kim, K. B., Leem, A. Y., Kim, K., & Lee, S. H. (2025). Enhanced respiratory "
 "sound classification using deep learning and multi-channel auscultation. Journal of "
 "Clinical Medicine, 14(15), 5437. https://doi.org/10.3390/jcm14155437",
 "Zhang, Q., et al. (2022). SPRSound: Open-source SJTU paediatric "
 "respiratory sound database. IEEE Transactions on Biomedical Circuits and Systems, 16(5), "
 "867–881. https://doi.org/10.1109/TBCAS.2022.3204910",
 "Oliveira, J., Renna, F., Costa, P. D., Nogueira, M., Oliveira, C., Ferreira, C., Jorge, "
 "A., Mattos, S., Hatem, T., Tavares, T., Elola, A., Rad, A. B., Sameni, R., Clifford, G. "
 "D., & Coimbra, M. T. (2022). The CirCor DigiScope dataset: From murmur detection to "
 "murmur classification. IEEE Journal of Biomedical and Health Informatics, 26(6), "
 "2524\u20132535. https://doi.org/10.1109/JBHI.2021.3137048",
 "Venkatesh, V., Morris, M. G., Davis, G. B., & Davis, F. D. (2003). User acceptance of "
 "information technology: Toward a unified view. MIS Quarterly, 27(3), 425–478.",
 "The jamovi project. (2025). jamovi (Version 2.7) [Computer software]. "
 "https://www.jamovi.org",
 "R Core Team. (2025). R: A language and environment for statistical computing (Version "
 "4.6) [Computer software]. R Foundation for Statistical Computing. "
 "https://www.R-project.org",
 "Tariq, Z., Shah, S. K., & Lee, Y. (2022). Feature-based fusion using CNN for lung and "
 "heart sound classification. Sensors, 22(4), 1521.",
 "Acharya, J., & Basu, A. (2020). Deep neural network for respiratory sound "
 "classification in wearable devices enabled by patient specific model tuning. IEEE "
 "Transactions on Biomedical Circuits and Systems, 14(3), 535\u2013544.",
 "Baraeinejad, B., Shams, M., Saberi Hamedani, M., Nasiri-Valikboni, A., Forouzesh, M., "
 "Fakhraeelotfabadi, S., Karimian, R., Babaei, S., Rashidi, D., Germchi, D., Torabi, Y., "
 "Gorji, P., & Vashaee, D. (2023). Clinical IoT in practice: A novel design and "
 "implementation of a multi-functional digital stethoscope for remote health monitoring "
 "[Preprint]. TechRxiv. https://doi.org/10.36227/techrxiv.24459988.v1",
 "Kim, Y., Hyon, Y., Jung, S. S., Lee, S., Yoo, G., Chung, C., & Ha, T. (2021). "
 "Respiratory sound classification for crackles, wheezes, and rhonchi in the clinical "
 "field using deep learning. Scientific Reports, 11(1), 17186. "
 "https://doi.org/10.1038/s41598-021-96724-7",
 "Komaryshyn, T., & Kogut, I. (2026). Intelligent digital stethoscope for neural network "
 "analysis of auscultatory signals: A review of sensors, architectures and algorithms. "
 "Computational Problems of Electrical Engineering, 16(1), 7\u201310. "
 "https://doi.org/10.23939/jcpee2026.01.007",
]
for r in sorted(REFS):
    p = para(r, first=0, after=8, align=WD_ALIGN_PARAGRAPH.LEFT, size=11, spacing=1.6)
    p.paragraph_format.left_indent = Inches(0.5)
    p.paragraph_format.first_line_indent = Inches(-0.5)

OUT = os.path.normpath(os.path.join(HERE, "..", "..", "imrad", "Resondi-IMRaD-Heart-and-Lung-2026-11-13.docx"))
import os as _os, sys as _sys  # house style: Times New Roman 11, justified, consistent indents (14 Nov)
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "style"))
import house_style  # noqa: E402
# 18 Nov 2026 (user): the AlagaVax paper's layout, single-spaced in two columns, replaces the double spacing of
# 14 Nov for the IMRaD (the research plan stays double-spaced).
print("  house style:", house_style.apply(doc, line_spacing=1.0))
import two_column  # noqa: E402
print("  two columns:", two_column.apply(doc, KW._p, WIDE))
# Review of 16 Nov 2026 (user: "review it further"): internal contradictions and small errors.
import review_fixes  # noqa: E402
print("  review fixes:", review_fixes.apply(doc, [
    ("so at 14 captures a full lung and heart examination would take about 34 minutes of screening time.",
     "so across the seven lung sites the quality check alone would add about 17 minutes to an examination, "
     "and more with Heart Mode.", 1),
    ("Chance performance is itself class-dependent. With four classes, the expected agreement by chance alone is "
     "25 percent, and the observed 40 percent corresponds to a Cohen's kappa of approximately +0.20, conventionally "
     "described as slight to fair.",
     "With four equally likely classes, the expected agreement by chance alone is 25 percent. Cohen's kappa could "
     "not be computed, because the fifteen recordings are not linked to their reference labels in the study "
     "records.", 1),
    ("That use is set out in the evaluation plan below.",
     "That is how it is used in this study, in the noise test of Research Question 6.", 1),
    ("Wheezing remains the weakest single class.",
     "Wheezing with Crackles remains the weakest class (26 percent recall in cross-validation; Table 4).", 1),
    ("Each cycle was cut into non-overlapping one-second windows at 16 kHz,",
     "Each cycle was cut into one-second windows at 16 kHz, overlapping by half in training and not overlapping "
     "in testing,", 1),
    ("and the trachea are classified and reported site by site", "and the trachea are reported site by site", 1),
    ("and Research Questions 6 to 8 by the three hypotheses.",
     "Research Questions 6 to 8 by the three hypotheses; and Research Questions 10 and 11 from the survey and "
     "the application.", 1),
    ("Each row was named as its round's primary model before the test patients were scored,",
     "Each row was named in advance, before the test patients were scored,", 1),
    ("With three to five items per construct and 27 respondents",
     "With three to five items in each of the other constructs and 27 respondents", 1),
    ("HF_Lung_V1, a Taiwanese corpus", "HF_Lung_V1 (Hsu et al., 2021), a Taiwanese corpus", 1),
    ("through its R package jmv,", "through its R package jmv, running in R 4.6 (R Core Team, 2025),", 1),
    ("so that every lobe is sampled from both the front and the back of the chest",
     "so that each upper lobe is sampled from both the front and the back of the chest", 1),
    ("revised as enclosure version 2.0", "revised as version 2.0", 1),
    ("organizes", "organises", 1),
    ("standardized", "standardised", 2),
    ("specialization", "specialisation", 1),
]))
doc.save(OUT)

import re
txt = "\n".join(p.text for p in doc.paragraphs)
print(f"saved {OUT}")
print(f"  words        : {len(txt.split()):,}")
print(f"  TO FILL marks: {txt.count('[[TO FILL')}")
print(f"  tables       : {len(doc.tables)}")
for bad in ("\u20b1", "budget", "funded", "funding"):
    if bad.lower() in txt.lower():
        print(f"  NOTE financial wording present: {bad}")
