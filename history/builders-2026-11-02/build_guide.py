"""Resondi - Acceptance Survey Analysis in jamovi (UTAUT, n = 27), step-by-step guide.

Column letters follow the position map in newdata/analyse_acceptance.py; target values
are CLAUDE.md A7.
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
para("Acceptance Survey Analysis in jamovi", size=20, bold=True, after=2)
para("Reproducing the UTAUT acceptance results (n = 27): construct means, "
     "Cronbach's alpha and the yes/no frequencies", size=11, italic=True, color=GREY,
     after=4)
para("Team Wheezards · Puerto Princesa City National Science High School · "
     "revised 30 October 2026", size=9, color=GREY, after=14)

note("This replaces the earlier guide, which assumed five dimensions (user-friendliness, "
     "usability, durability, functionality, community impact) and 30 respondents. The "
     "questionnaire actually administered is a UTAUT instrument, and the export holds 27 "
     "responses. Nothing in the old guide's Step 8 applies any more.")

# ── what this produces ──────────────────────────────────────────────────
h1("What this produces")
para("The analysis has already been run once, with newdata/analyse_acceptance.py. This "
     "guide lets you reproduce the same numbers yourself in jamovi, so that you can explain "
     "every one of them to an adviser or a judge, and rerun them if the response sheet "
     "changes.")
table([
    ["Output", "Form", "Where it is already used"],
    ["Four construct means with SD", "Mean and SD to 2 decimals, plus the verbal "
     "interpretation", "IMRaD Results; paper pack Table 7; concept note; Q&A"],
    ["Overall acceptance", "One mean across the 12 Likert items", "Everywhere: 3.95, Agree"],
    ["Cronbach's alpha", "α to 2 decimals, for constructs of two or more items",
     "IMRaD Results; paper pack Table 7"],
    ["Four yes/no frequencies", "Counts and percentages, never means",
     "IMRaD Results; paper pack item 19"],
], [1.9, 2.4, 2.5])

h2("The numbers you should get")
para("If your jamovi output matches these, you have reproduced the published analysis. "
     "If it does not, the troubleshooting table at the end explains the usual reasons.")
table([
    ["Construct", "Items", "n", "Mean", "SD", "Verbal", "α"],
    ["Performance expectancy", "3", "27", "4.09", "0.59", "Agree", "0.51"],
    ["Effort expectancy", "3", "27", "4.09", "0.60", "Agree", "0.76"],
    ["Regulatory assurance", "5", "27", "3.84", "0.61", "Agree", "0.59"],
    ["Social influence", "1", "27", "3.63", "1.21", "Agree", "—"],
    ["Overall (12 Likert items)", "12", "27", "3.95", "—", "Agree", "—"],
], [2.0, 0.6, 0.5, 0.7, 0.6, 1.0, 0.6])
table([
    ["Yes/no item", "Result"],
    ["Peers or colleagues encourage use", "Yes 21 of 27 (78%)"],
    ["Institution provides resources", "Yes 20 of 27 (74%)"],
    ["Access to training and technical support", "Maybe 12 (44%) · Yes 8 (30%) · No 7 (26%)"],
    ["Prior experience with medical devices or health apps", "Yes 11 of 27 (41%)"],
], [3.3, 3.5])

# ── privacy ─────────────────────────────────────────────────────────────
h1("Before you start: protect the respondents")
para("The Google Forms export contains respondents' names and e-mail addresses. They are "
     "not needed for any part of this analysis and must not appear in any file you share, "
     "screenshot, or upload.")
bullet("Work only on a copy: in Google Sheets, File > Make a copy.")
bullet("In the copy, delete the Timestamp, name and e-mail columns before doing anything "
       "else. In the export these should be the first three columns, A to C, with the role "
       "question in D; read the headers to confirm.")
bullet("Never paste the original export into jamovi, a chat window, or a slide.")
note("analyse_acceptance.py follows the same rule: it never reads the name, e-mail or "
     "timestamp columns.")

# ── step 1 ──────────────────────────────────────────────────────────────
h1("Step 1: Name the columns")
para("Do this in the copy, before deleting columns A to C, so the letters below still "
     "match. Replace each question's long header text with the short name in the table. "
     "jamovi uses the header as the variable name, and short names make the formulas in "
     "Step 4 readable.")
table([["Column", "Rename to", "What it holds"]] + [list(c) for c in COLS],
      [0.7, 1.1, 5.0])
note("Check the order before you rename. Read each header and confirm it belongs to the "
     "construct shown: the three performance-expectancy items ask whether the device would "
     "be useful, the effort-expectancy items ask whether it would be easy to use, the five "
     "regulatory-assurance items mention ISO standards, and the social-influence item asks "
     "whether people important to the respondent think they should use it. If your export's "
     "order differs, follow the header text, not the letter.")
para("Then delete columns A to C, and delete every column to the right of T. Those are the "
     "three behavioural-intention items and the open-ended questions; all of them returned "
     "no responses, so there is nothing to analyse.")

# ── step 2 ──────────────────────────────────────────────────────────────
h1("Step 2: Turn the Likert answers into numbers")
para(f"The Likert columns are {LIKERT}. The four yes/no columns (E, N, Q, R) and the role "
     "column (D) stay as text.")
para("Select the twelve Likert columns, then open Edit > Find and replace. Set Search to "
     "'Specific range' (it fills in your selection), tick 'Match entire cell contents', and "
     "run these six replacements one at a time:")
table([
    ["Find", "Replace with"],
    ["Strongly Disagree", "1"],
    ["Disagree", "2"],
    ["Neutral", "3"],
    ["Agree", "4"],
    ["Strongly Agree", "5"],
    ["Stongly Agree", "5"],
], [3.0, 1.5])
note("'Stongly Agree' is a typo in the form's own option list and appears 9 times. It "
     "means Strongly Agree, so it scores 5. 'Match entire cell contents' is what stops "
     "'Agree' from also matching inside 'Strongly Agree'.")
para("Now scan the twelve columns for any cell that is still text. The export contains two "
     "further spellings of the same options (for example a trailing space or different "
     "capitalisation). Replace each by hand with its number. When every cell in the twelve "
     "columns is a digit from 1 to 5, the data is clean.")
para("Download the copy: File > Download > Comma-separated values (.csv). Name it "
     "acceptance_utaut.csv.")

# ── step 3 ──────────────────────────────────────────────────────────────
h1("Step 3: Open the data in jamovi")
bullet("Open jamovi. Click the ☰ menu (top left) > Open > Browse, and choose "
       "acceptance_utaut.csv.")
bullet("Check the row count at the bottom of the Data tab. It should be 27. If it is "
       "higher, people have responded since 30 October 2026, and every figure in this guide "
       "will change; see 'If your numbers differ' at the end.")
bullet("Click the Data tab, then Setup. For each of the twelve Likert variables, set the "
       "measure type to Continuous. Set role, prior_exp, peers, training and resources to "
       "Nominal.")

# ── step 4 ──────────────────────────────────────────────────────────────
h1("Step 4: Compute the construct scores")
para("Each respondent gets one score per construct: the mean of that construct's items. "
     "In the Data tab, click Compute, name the new variable, and type its formula:")
table([
    ["New variable", "Formula"],
    ["PE", "MEAN(pe1, pe2, pe3)"],
    ["EE", "MEAN(ee1, ee2, ee3)"],
    ["RA", "MEAN(ra1, ra2, ra3, ra4, ra5)"],
    ["SI", "si1"],
    ["OVERALL", "MEAN(pe1, pe2, pe3, ee1, ee2, ee3, ra1, ra2, ra3, ra4, ra5, si1)"],
], [1.3, 5.5])
note("Social influence has a single item, so its 'score' is that item. Overall is the mean "
     "of all twelve items for each respondent; with no missing answers it equals the mean "
     "of every Likert response in the survey.")

# ── step 5 ──────────────────────────────────────────────────────────────
h1("Step 5: Descriptives, the construct means")
bullet("Analyses > Exploration > Descriptives.")
bullet("Move PE, EE, RA, SI and OVERALL into Variables.")
bullet("Under Statistics, tick N, Mean, Std. deviation, Minimum and Maximum.")
para("Compare the Mean and Std. deviation rows with 'The numbers you should get'. The SD "
     "reported for each construct is the spread of respondents' construct scores, which is "
     "what Step 4 produced. The overall row has no published SD; report the mean only.")

# ── step 6 ──────────────────────────────────────────────────────────────
h1("Step 6: Cronbach's alpha, one construct at a time")
bullet("Analyses > Factor > Reliability Analysis.")
bullet("Move pe1, pe2 and pe3 into Items. Under Scale Statistics tick Cronbach's α; under "
       "Item Statistics tick 'Cronbach's α (if item is dropped)'. Expect 0.51.")
bullet("Clear the Items box and repeat with ee1–ee3 (expect 0.76), then ra1–ra5 (expect 0.59).")
bullet("Do not run it for social influence. Alpha needs at least two items.")
note("Alpha below 0.70 does not make a result wrong, but it means the items in that "
     "construct do not move together closely enough to treat it as one validated scale. "
     "With three to five items and 27 respondents, report the constructs descriptively and "
     "call their alphas provisional, which is what the IMRaD and the paper pack already do.")

# ── step 7 ──────────────────────────────────────────────────────────────
h1("Step 7: The yes/no items, as frequencies")
bullet("Analyses > Exploration > Descriptives.")
bullet("Move prior_exp, peers, training and resources into Variables, and tick 'Frequency "
       "tables'.")
para("Report each as counts and percentages, as in the second target table. Never average "
     "these: a mean of yes and no is not a measurement. The training item has three "
     "answers (yes, maybe, no), so report all three.")

# ── step 8 ──────────────────────────────────────────────────────────────
h1("Step 8 (optional): By respondent role")
para("To see whether patients and general respondents answered differently, drag role into "
     "'Split by' in the Step 5 Descriptives. Report the patient and general-respondent "
     "groups (13 each) side by side, descriptively only; with 13 per group, a significance "
     "test would not be meaningful. Do not report the practitioner group: it is one person, "
     "and a single answer is not a group mean.")

# ── step 9 ──────────────────────────────────────────────────────────────
h1("Step 9: Interpret against the scale")
table([
    ["Mean range", "Verbal interpretation"],
    ["4.21–5.00", "Strongly Agree"],
    ["3.41–4.20", "Agree"],
    ["2.61–3.40", "Neutral"],
    ["1.81–2.60", "Disagree"],
    ["1.00–1.80", "Strongly Disagree"],
], [1.6, 2.4])
note("This is Table 1.4 of the 83-page paper, unchanged. All four constructs and the "
     "overall mean fall in the Agree band.")

# ── what to say and not say ─────────────────────────────────────────────
h1("What the results support, and what they do not")
bullet("Support: respondents in Puerto Princesa City rated Resondi favourably, at 3.95 of "
       "5, and found it both useful and easy to use (4.09 each).")
bullet("Do not claim practitioner acceptance. Only one practitioner responded; items about "
       "institutional resources and professional practice were mostly answered by people "
       "they do not apply to.")
bullet("Do not cite the regulatory-assurance items as evidence of ISO conformity. Five of the "
       "twelve items ask about standards the device has not yet achieved; they measure how "
       "much conformity would reassure respondents, nothing more.")
bullet("Do not report behavioural intention. Those three items returned no responses.")
bullet("Do not describe the constructs as validated scales while their alphas sit below 0.70.")

# ── if numbers differ ───────────────────────────────────────────────────
h1("If your numbers differ")
para("If the live sheet now holds more than 27 responses, rerun everything above, and then "
     "update every document that quotes these figures. They are built from source, so the "
     "values must be changed in the builders (or given to whoever maintains them), not typed "
     "into the .docx files:")
table([
    ["Document", "Where the figures appear"],
    ["Concept note (01)", "'Proposed Startup Solution': the paragraph reporting the "
     "prototype's measured results"],
    ["Pitch deck (02)", "Slide 10, third stat card, and its speaker notes"],
    ["Pitch script (03)", "Section 7:05–7:35, 'Validation and who benefits'"],
    ["Judge Q&A (04)", "Research method and statistics: 'How were your twenty-seven "
     "acceptance respondents selected?'"],
    ["IMRaD (06)", "Evaluation Procedures and the End-User Acceptance results"],
    ["Paper revision pack (07)", "Items 2, 3, 8, 19 (Table 7) and 20"],
], [2.0, 4.8])

# ── troubleshooting ─────────────────────────────────────────────────────
h1("Troubleshooting")
table([
    ["Symptom", "Cause and fix"],
    ["Descriptives shows no Mean row",
     "The variables are still Nominal. Return to Step 3 and set the twelve items to "
     "Continuous."],
    ["A Likert column will not turn Continuous, or shows blanks",
     "A text answer survived Step 2. Sort that column in Google Sheets, find the cell that "
     "is not a digit, replace it, and re-download."],
    ["N is 28 or more", "New responses have arrived since 30 October 2026. See 'If your "
     "numbers differ'."],
    ["N is 26 or less", "A row was deleted by accident, or a respondent left an item blank. "
     "Check the Data tab for empty cells."],
    ["A computed column is all blank",
     "A variable name in the formula is misspelled. Names are case-sensitive and must match "
     "the headers exactly."],
    ["A construct mean is close but not exact (for example 4.07 instead of 4.09)",
     "One of the spelling variants was scored wrongly, or a column was assigned to the wrong "
     "construct. Recheck Step 2, then the header text against Step 1."],
    ["Alpha is negative",
     "An item is in the wrong construct, or a column was mis-renamed. The published "
     "analysis reverse-codes nothing; if a header reads as negatively worded, flag it to "
     "your adviser rather than recoding it silently."],
], [2.3, 4.5])

para()
para("Save the jamovi file (.omv) with acceptance_utaut.csv, and keep both with the name and "
     "e-mail columns removed. If anyone asks how a number was produced, the file answers in "
     "one click. As a cross-check, newdata/analyse_acceptance.py run on the same export "
     "(saved as survey_raw.csv in its folder) prints the same table.",
     size=10, italic=True, color=GREY)

out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                                    "deliverables", "Resondi-Acceptance-Survey-jamovi-Guide.docx"))
doc.save(out)
print("written:", out)
