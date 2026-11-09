"""Resondi - Statistics in jamovi: agreement, signal, clarity, response time, ICBHI (rebuilt 30 Oct 2026).

Target values are CLAUDE.md A5 and B7, each rechecked against the data on 30 Oct.
"""
import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FONT = "Calibri"
INK = RGBColor(0x1A, 0x1A, 0x1A)
GREY = RGBColor(0x5A, 0x5A, 0x5A)
ACCENT = RGBColor(0x8E, 0x2A, 0x52)
HDR_FILL = "D9D9D9"

doc = Document()
st = doc.styles["Normal"]
st.font.name = FONT
st.font.size = Pt(10.5)
st.font.color.rgb = INK
st.paragraph_format.space_after = Pt(6)
st.paragraph_format.line_spacing = 1.12

for s in doc.sections:
    s.top_margin = s.bottom_margin = Inches(0.8)
    s.left_margin = s.right_margin = Inches(0.9)


def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def para(text="", size=10.5, bold=False, italic=False, color=INK,
         before=0, after=6, align=None, mono=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    if align:
        p.alignment = align
    r = p.add_run(text)
    r.font.name = "Consolas" if mono else FONT
    r.font.size = Pt(size)
    r.bold = bold
    r.italic = italic
    r.font.color.rgb = color
    return p


def rich(parts, size=10.5, before=0, after=6, indent=0.0):
    """parts: list of (text, bold, mono) tuples."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    if indent:
        p.paragraph_format.left_indent = Inches(indent)
    for text, bold, mono in parts:
        r = p.add_run(text)
        r.font.name = "Consolas" if mono else FONT
        r.font.size = Pt(size - (0.5 if mono else 0))
        r.bold = bold
        r.font.color.rgb = INK
    return p


def h1(text):
    para(text, size=15, bold=True, color=ACCENT, before=16, after=4)


def h2(text):
    para(text, size=11.5, bold=True, before=11, after=3)


def bullet(text, level=0):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Inches(0.26 + 0.24 * level)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(text)
    r.font.name = FONT
    r.font.size = Pt(10.5)
    r.font.color.rgb = INK


def code(text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.26)
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(7)
    r = p.add_run(text)
    r.font.name = "Consolas"
    r.font.size = Pt(9.5)
    r.font.color.rgb = RGBColor(0x5E, 0x16, 0x36)
    return p


def table(rows, widths, header=True):
    t = doc.add_table(rows=0, cols=len(rows[0]))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for ci, text in enumerate(row):
            cells[ci].width = Inches(widths[ci])
            p = cells[ci].paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(str(text))
            r.font.name = FONT
            r.font.size = Pt(9.5)
            r.bold = header and ri == 0
            r.font.color.rgb = INK
            if header and ri == 0:
                shade(cells[ci], HDR_FILL)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def note(text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.22)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run(text)
    r.font.name = FONT
    r.font.size = Pt(10)
    r.italic = True


# position map from analyse_acceptance.py, as spreadsheet letters
COLS = [  # letter, short name, construct / use
    ("D", "role", "Respondent role (patient, general respondent, practitioner)"),
    ("E", "prior_exp", "Yes/No: prior experience with medical devices or health apps"),
    ("F", "pe1", "Performance expectancy, item 1"),
    ("G", "pe2", "Performance expectancy, item 2"),
    ("H", "pe3", "Performance expectancy, item 3"),
    ("I", "ra1", "Regulatory assurance, item 1"),
    ("J", "ee1", "Effort expectancy, item 1"),
    ("K", "ee2", "Effort expectancy, item 2"),
    ("L", "ee3", "Effort expectancy, item 3"),
    ("M", "ra2", "Regulatory assurance, item 2"),
    ("N", "peers", "Yes/No: peers or colleagues encourage use"),
    ("O", "si1", "Social influence (single item)"),
    ("P", "ra3", "Regulatory assurance, item 3"),
    ("Q", "training", "Yes/Maybe/No: access to training and technical support"),
    ("R", "resources", "Yes/No: institution provides resources"),
    ("S", "ra4", "Regulatory assurance, item 4"),
    ("T", "ra5", "Regulatory assurance, item 5"),
]
LIKERT = "F, G, H, I, J, K, L, M, O, P, S and T"



# ═══════════════════════════════════════════════════════════════════════
para("RESONDI", size=9, bold=True, color=ACCENT, after=0)
para("Statistics in jamovi", size=20, bold=True, after=2)
para("Agreement, signal strength, clarity, response time and the ICBHI comparison, "
     "with the result you should get at every step", size=11, italic=True, color=GREY, after=4)
para("Team Wheezards · Puerto Princesa City National Science High School · "
     "revised 30 October 2026", size=9, color=GREY, after=14)

note("This replaces the earlier guide, which treated the 32.49 dB measurement as unresolved, "
     "used the five-dimension acceptance survey, and analysed the full ICBHI comparison "
     "including Healthy recordings. The acceptance survey now has its own guide (file 10).")

h1("What each analysis answers")
table([
    ["Section", "Question", "Result in the documents"],
    ["1–3", "Does the model agree with the reference labels better than chance?",
     "6 of 15 (40%); Wilson 95% CI 19.8–64.3%; p = 0.148 against 25%"],
    ["4", "How much stronger is the device's signal?", "45 vs 32 dB: +13 dB, about 4.5× the amplitude"],
    ["5", "How clear are the recordings?", "68% good, 25% acceptable, 7% poor"],
    ["6", "How long does each stage take?", "Table 5: quality check 144.68 s is the bottleneck"],
    ["7", "Do the abnormal ICBHI categories differ in how abnormal they are?",
     "Kruskal–Wallis without Healthy: H = 32.53, df = 2, p < .001"],
    ["—", "Acceptance (UTAUT, n = 27)", "See file 10, the acceptance guide"],
], [0.7, 3.2, 2.9])

# ── 0 ───────────────────────────────────────────────────────────────────
h1("0  Install the one module you need")
para("Cohen's kappa is not in base jamovi. Install the meddecide module once:")
bullet("Click the + Modules button (top right) > jamovi library.")
bullet("Search for meddecide and click Install.")
note("Everything else in this guide uses base jamovi.")

# ── 1 ───────────────────────────────────────────────────────────────────
h1("1  Build the agreement dataset")
para("One row per field recording, 15 rows in all. Three columns:")
table([
    ["Column", "Type", "What it holds"],
    ["reference", "Nominal", "The label the reviewing clinicians gave: Normal, Wheezing, Crackles, or Wheezing with crackles"],
    ["model", "Nominal", "The label Resondi returned for the same recording, spelled exactly the same way"],
    ["agree", "Nominal (0/1)", "1 if reference and model match, otherwise 0"],
], [1.1, 1.2, 4.5])
note("Spell the four labels identically in both columns, or jamovi treats 'Crackle' and "
     "'Crackles' as different classes and the confusion matrix comes out wrong.")

# ── 2 ───────────────────────────────────────────────────────────────────
h1("2  Confusion matrix and Cohen's kappa")
h2("2a  The confusion matrix (base jamovi)")
code("Analyses  →  Frequencies  →  Independent Samples  χ² test of association")
bullet("Move reference into Rows and model into Columns.")
bullet("Ignore the χ² test itself; with 15 recordings and 16 cells it is not valid. You only need the table.")
para("The diagonal holds the 6 agreements. Read the off-diagonal cells: they show which "
     "patterns the model confuses, which matters more for retraining than the 40% does.")
h2("2b  Cohen's kappa (needs meddecide)")
code("Analyses  →  meddecide  →  Agreement  →  Interrater Reliability")
bullet("Move reference and model into the variables box.")
bullet("Leave Kappa type on Cohen.")
para("Kappa corrects the 40% for the agreement expected by chance. Report it with its "
     "confidence interval, and expect the interval to be wide: fifteen recordings cannot "
     "pin it down.")
note("Kappa is not yet in any Resondi document. If you report it, add it to the IMRaD's "
     "Interpretation of the Classification Result, where a TO FILL marker asks for it.")

# ── 3 ───────────────────────────────────────────────────────────────────
h1("3  Does the model beat guessing? (exact binomial test)")
code("Analyses  →  Frequencies  →  2 Outcomes  Binomial test")
bullet("Move agree into the Variables box.")
bullet("Set Test value to 0.25, the chance level for four classes.")
bullet("Under Hypothesis, choose '> Test value'. The question is whether the model does "
       "better than chance, so the test is one-sided.")
bullet("Tick Confidence intervals.")
para("Expect a proportion of 0.40 for the '1' level and p = 0.148: not significant. Eight "
     "of fifteen agreements would have been needed for p < 0.05.")
note("jamovi's interval is the exact (Clopper–Pearson) one, about 16.3% to 67.7%. The Resondi "
     "documents quote the Wilson interval, 19.8% to 64.3%, which is narrower and better behaved "
     "at small n. Both are correct. Quote the Wilson interval so every document agrees, and "
     "if a judge asks, say which interval it is.")

# ── 4 ───────────────────────────────────────────────────────────────────
h1("4  Signal strength: device vs conventional stethoscope")
para("The documents report 45 dB for Resondi against 32 dB for a conventional stethoscope. "
     "Those figures come from your measurement sheets, not from the 83-page paper, which "
     "prints different values. Check your sheets give 45 and 32 before running anything.")
para("If you have one row per recording session with both readings (columns db_resondi and "
     "db_conventional):")
code("Analyses  →  T-Tests  →  Paired Samples T-Test")
bullet("Put db_resondi and db_conventional together as one pair.")
bullet("Tick Student's and Wilcoxon rank; tick Mean difference and Confidence interval.")
para("Report the mean difference in dB with its confidence interval, for example 'a mean "
     "difference of 13 dB'. Use the Wilcoxon result if the differences look skewed.")
note("Never divide decibels. 45 ÷ 32 means nothing, because the scale is logarithmic. "
     "A 13 dB difference is about 4.5 times the sound-pressure amplitude (10^(13/20)).")

# ── 5 ───────────────────────────────────────────────────────────────────
h1("5  Recording clarity")
h2("5a  The percentages")
code("Analyses  →  Exploration  →  Descriptives")
bullet("Put clarity (Good / Acceptable / Poor) in Variables and tick Frequency tables.")
para("Expect 68% good, 25% acceptable and 7% poor. The counts behind those percentages "
     "appear nowhere in the paper. Report the count with the percentages; a percentage "
     "without its denominator is the first thing a reviewer questions.")
h2("5b  Did your raters agree? (only if more than one rated)")
para("If two or more health professionals rated the same recordings, put one column per "
     "rater and use the Interrater Reliability analysis from Section 2b. Clarity is ordered, "
     "so choose weighted kappa. If only one person rated, say so in the paper.")

# ── 6 ───────────────────────────────────────────────────────────────────
h1("6  Response time")
code("Analyses  →  Exploration  →  Descriptives")
bullet("Put the five stage columns in Variables: connection, recording, quality, "
       "preprocessing, classification. Tick Mean and Std. deviation.")
table([
    ["Stage", "Mean (s)", "SD (s)"],
    ["Smart-stethoscope connection", "4.55", "0.83"],
    ["Sound recording", "15.00", "0.00"],
    ["Recording-quality assessment", "144.68", "28.94"],
    ["Signal preprocessing", "20.91", "4.18"],
    ["Classification output", "3.97", "0.87"],
], [3.0, 1.2, 1.2])
note("Table 5 of the paper is authoritative. Figure 4.4 of the paper contradicts it; the "
     "paper revision pack (file 07, item 13) replaces that figure.")

# ── 7 ───────────────────────────────────────────────────────────────────
h1("7  ICBHI: how abnormal is each abnormal category?")
para("This uses data/dataset920.csv, one row per ICBHI recording, with sound_category and "
     "abnormal_sound_percent.")
note("Leave Healthy out. A recording is called Healthy because it has no abnormal cycles, so "
     "its abnormal_sound_percent is 0 by definition. Including it makes three of the six "
     "comparisons true by construction, and the very large χ² it produces means nothing.")
bullet("In the Data tab, add a filter: sound_category != 'Healthy'. That leaves 633 recordings.")
code("Analyses  →  ANOVA  →  One-Way ANOVA (Non-parametric)  Kruskal–Wallis")
bullet("Dependent variable: abnormal_sound_percent. Grouping variable: sound_category.")
bullet("Tick DSCF pairwise comparisons.")
table([
    ["Category", "Recordings", "Mean abnormal cycles"],
    ["Wheezing with crackles", "92", "84.7%"],
    ["Crackles", "366", "70.6%"],
    ["Wheezing", "175", "64.7%"],
], [2.6, 1.3, 2.0])
para("Expect H = 32.53, df = 2, p < .001, with all three pairwise comparisons significant. "
     "Report it with one line saying why Healthy was excluded.")

# ── 8 ───────────────────────────────────────────────────────────────────
h1("8  What to write")
h2("Statistical treatment")
para("Descriptive statistics summarised recording clarity, response time, ambient noise and "
     "signal strength. Classification agreement was reported as the proportion of matching "
     "classifications with a 95% Wilson score interval, and tested against the 25% expected "
     "by chance across four categories with an exact one-sided binomial test at α = 0.05. "
     "Differences in abnormal-cycle percentage across the three abnormal ICBHI categories were "
     "tested with the Kruskal–Wallis test, excluding Healthy recordings, which are zero by "
     "definition. Analyses were performed in jamovi (version ___).", size=10.5)
h2("Do not use")
bullet("McNemar's test for the 15 recordings, or any p = 1.000 result. It answers a different "
       "question (whether two methods err in the same direction) and has no power at n = 15.")
bullet("A paired t-test on class labels or on Good/Acceptable/Poor grades. t-tests need "
       "continuous data. They are fine for dB values and seconds.")
bullet("Any reference-dataset accuracy (71.1%, 83.4%, 83.7%). Those scores are inflated by "
       "the train/test overlap described in the model statistics summary (file 09).")

# ── 9 ───────────────────────────────────────────────────────────────────
h1("9  How many recordings the next study needs")
para("Fifteen recordings cannot show a classifier beats chance unless it is very good. For "
     "80% power with a one-sided exact binomial test against 25% at α = 0.05:")
table([
    ["If the model's true agreement is", "Recordings needed", "Agreements needed to pass"],
    ["40%", "62", "22"],
    ["50%", "26", "11"],
    ["60%", "14", "7"],
], [2.6, 1.7, 2.4])
para("To pin agreement down to within ±10 percentage points (Wilson interval at 50%), you "
     "need about 93 recordings. The clinical validation line in the budget targets 300 paired "
     "recordings, which covers both.")
note("Run this after the patient-separated retraining. Testing the current model on more "
     "recordings measures a model you already know is going to be replaced.")

out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                                    "deliverables", "Resondi-jamovi-Statistics-Guide.docx"))
doc.save(out)
print("written:", out)
