"""What is still missing from the research plan and the IMRaD, by category, for Ahnyccas papers/.

The visible markers are read from the papers themselves, so the list always matches them:
  - IMRaD: every FILL(...) call in build/imrad/build_imrad.py, with its section heading
  - research plan: every paragraph of the FINAL research plan that carries a CONFIRM note
The other items (research questions or analyses the data cannot yet answer, and decisions for the
team) are stated in the papers' own limitations, and are listed here with what would close each.

Run:  python build/missing/build_missing.py   -> Ahnyccas papers/Resondi-Missing-Items-Research-Plan-and-IMRaD.docx
"""
import ast
import os
import re

import docx
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
IMRAD_SRC = os.path.join(ROOT, "build", "imrad", "build_imrad.py")
PAPERS = os.path.join(ROOT, "Ahnyccas papers")
PLAN = os.path.join(PAPERS, "Resondi-Research-Plan-Heart-and-Lung-FINAL.docx")
OUT = os.path.join(PAPERS, "Resondi-Missing-Items-Research-Plan-and-IMRaD.docx")

INK, GREY, ACCENT = RGBColor(0x1A, 0x1A, 0x1A), RGBColor(0x5A, 0x5A, 0x5A), RGBColor(0x8E, 0x2A, 0x52)
BLOCKS, BEFORE, LATER = "Blocks submission", "Before the fair", "Future work"

# IMRaD markers whose facts the paper's main claims rest on (same list as build/imrad/build_open_items.py)
BLOCKING = ("microphone", "four zones", "measurement unit", "how many qualified", "blinded",
            "sampling method", "ethics", "distinct from the 13")
# IMRaD markers that are advice about the 83-page full paper or an optional addition, not a missing fact
ADVICE = ("full paper's data analysis section specifies", "consider reporting cohen's kappa")


def imrad_markers():
    tree = ast.parse(open(IMRAD_SRC, encoding="utf-8").read())
    h1 = h2 = ""
    out = []
    for stmt in tree.body:
        for call in [n for n in ast.walk(stmt) if isinstance(n, ast.Call)]:
            name = getattr(call.func, "id", "")
            if name in ("H1", "H2") and call.args:
                try:
                    text = ast.literal_eval(call.args[0])
                except ValueError:
                    continue
                h1, h2 = (text, "") if name == "H1" else (h1, text)
            elif name == "FILL" and len(call.args) == 2:
                out.append((h2 or h1, ast.literal_eval(call.args[1])))
    return out


def plan_markers():
    d = docx.Document(PLAN)
    out = []
    for p in d.paragraphs:  # the builder prints these notes without the [[ ]] brackets
        if "CONFIRM" in p.text:
            out.append(p.text.strip())
    return out


# ------------------------------------------------------------------ document helpers
doc = Document()
st = doc.styles["Normal"]
st.font.name, st.font.size, st.font.color.rgb = "Calibri", Pt(10.5), INK
for s in doc.sections:
    s.top_margin = s.bottom_margin = Inches(0.75)
    s.left_margin = s.right_margin = Inches(0.75)


def para(text, size=10.5, bold=False, italic=False, color=INK, after=6, before=0):
    p = doc.add_paragraph()
    p.paragraph_format.space_after, p.paragraph_format.space_before = Pt(after), Pt(before)
    r = p.add_run(text)
    r.font.size, r.bold, r.italic, r.font.color.rgb = Pt(size), bold, italic, color
    return p


def shade(cell, fill):
    pr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:fill"), fill)
    pr.append(sh)


W = [0.35, 2.05, 2.9, 0.95, 0.85]


def table(rows):
    t = doc.add_table(rows=1, cols=5)
    t.style = "Table Grid"
    for c, h in enumerate(["#", "What is missing", "What closes it", "Who", "Priority"]):
        cell = t.rows[0].cells[c]
        cell.width = Inches(W[c]); shade(cell, "EBD3DE")
        r = cell.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(9.5)
    for i, row in enumerate(rows, 1):
        cells = t.add_row().cells
        for c, v in enumerate([str(i)] + list(row)):
            cells[c].width = Inches(W[c])
            r = cells[c].paragraphs[0].add_run(v)
            r.font.size = Pt(9)
            if c == 4:
                r.bold = v == BLOCKS
                if v == BLOCKS:
                    r.font.color.rgb = ACCENT
    para("", after=4)


def heading(text, size=13, before=8):
    para(text, size=size, bold=True, color=ACCENT, after=4, before=before)


def cap(s):
    return s[0].upper() + s[1:]


# ------------------------------------------------------------------ content
IM = imrad_markers()
im_block = [(s, t) for s, t in IM if any(k in t.lower() for k in BLOCKING)]
im_advice = [(s, t) for s, t in IM if any(k in t.lower() for k in ADVICE)]
im_lookup = [(s, t) for s, t in IM if (s, t) not in im_block and (s, t) not in im_advice]
PL = plan_markers()

plan_refs = [(f"Reference list: {m.split('. CONFIRM')[0].split('CONFIRM')[0].strip(' .:')}",
              "The full reference (authors, year, title, journal, volume, pages, DOI). If the source cannot be "
              "found, drop the citation and reword the Rationale sentence that uses it.", "Team (Ahnycca)", BLOCKS)
             for m in PL]

plan_rq = [
    ("RQ 1, signal quality: no formal signal-to-noise ratio. The 45 dB and 32 dB figures were not measured against "
     "a common reference.", "Record Resondi and the conventional stethoscope at the same site with the same sound level "
     "meter and reference, and report the paired difference.", "Team with the device", LATER),
    ("RQ 7 / Hypothesis 2, reference vs device recordings: not testable. No Resondi recordings with "
     "clinician-assigned labels exist.", "Clinician-labelled Resondi device recordings (two blinded clinicians per "
     "breathing cycle), then score the fusion network on them.", "Team + clinicians", LATER),
    ("RQ 8 / Hypothesis 3, conventional vs Resondi quality: not tested inferentially. The paired raw measurements "
     "behind 45 dB and 32 dB were not kept.", "Paired recordings at the same sites; paired t-test or Wilcoxon "
     "signed-rank test, as Table 6 plans.", "Team with the device", LATER),
    ("RQ 9, acceptance: the UTAUT survey (n = 27) rated the old version, which ran the original model; the "
     "current version (rebuilt lung classifier, heart-sound models) has not been surveyed. Durability was not "
     "measured, and functionality was rated by one physician only (5 of 5, 29 Aug 2026), not by end users.",
     "Repeat the UTAUT survey on the current version, adding durability and functionality items and the four RQ 10 "
     "items, so one survey closes RQ 9 and RQ 10; then replace the n = 27 results in both papers.", "Team", BEFORE),
    ("RQ 10, instructional-support preferences: not answered. The survey had no items on diagram guidance, manual "
     "clarity, ease of learning, or app navigation.", "A short survey on those four aspects after a guided "
     "examination (frequency and percentage, as Table 6 plans).", "Team", BEFORE),
    ("RQ 11, longitudinal monitoring and rehabilitation: built but not evaluated. No patient has repeated "
     "recordings; the severity-error rule in Table 6 has not been applied.", "Repeated same-site recordings of the "
     "same patients over weeks, with rehabilitation completion and outcome recorded.", "Team + practitioner", LATER),
]

plan_analyses = [
    ("Cardiologist's blinded review of the 25 CirCor recordings has not been returned (the heart models were "
     "trained before it).", "The reviewer's answer sheet; then report agreement with the dataset's labels and "
     "revise the heart results if agreement is poor.", "Cardiologist", BEFORE),
    ("Heart models not tested on Resondi heart recordings; the device's low-frequency response is not measured.",
     "Swept-tone frequency response from 20 Hz, then heart recordings on the device labelled by a cardiologist.",
     "Team + cardiologist", LATER),
    ("Murmur sensitivity 66.7% on test patients, short of the pre-specified 80%.", "Set the threshold on more "
     "validation patients, or let the murmur model use the S1/S2 timing; retest on new patients.", "Model work", LATER),
    ("Murmur timing (systolic / diastolic) not attempted; the segmentation stage is not yet used by the murmur model.",
     "Next model round.", "Model work", LATER),
    ("Cardiac abnormality extent score and recording-level murmur metrics not computed (planned in Data Analysis).",
     "Compute from the existing test predictions.", "Model work", BEFORE),
    ("Hypotheses 1 and 2 tested for lung sounds only.", "Repeat the noise test on heart recordings; Hypothesis 2 "
     "needs labelled device heart recordings.", "Model work + team", LATER),
    ("Local Filipino lung dataset (run D in the plan) not collected.", "Resondi recordings of Filipino patients at "
     "the seven sites, labelled by two blinded clinicians, with ethics approval and consent.", "Team + clinicians",
     LATER),
]

plan_decisions = [
    ("Peso figures remain: bill of materials ₱2,775, unit cost ₱4,000 (they answer RQ 2, cost) and the Littmann "
     "price ₱22,000 in the Rationale.", "Keep them as device specifications, or remove them if the fair's rules "
     "exclude any money figure (RQ 2's cost item would then go too).", "Team", BEFORE),
]

# Short labels for the IMRaD markers, keyed by a phrase in the marker text (first match wins).
LABELS = [
    ("name the microphone part", "Which microphone the evaluated build used (INMP441 or MAX4466)"),
    ("low-frequency limit", "The microphone's low-frequency limit, from its datasheet"),
    ("four zones", "How the six lung fields map onto the four zones the rules use"),
    ("measurement unit", "Signal test: unit, reference level, comparator stethoscope, how it was captured"),
    ("how many qualified", "Clarity ratings: number of raters and whether they agreed"),
    ("blinded", "Whether the three pulmonologists were blinded to the model output"),
    ("sampling method", "How the 27 acceptance respondents were recruited"),
    ("ethics", "Ethics: any committee, school or hospital approval, with its date"),
    ("distinct from the 13", "Whether the 3 hospital patients are among the 13 survey patients"),
    ("confirm this is the term", "The research-design term your school uses"),
    ("bit depth", "Bit depth and segment length used at segmentation"),
    ("loss function", "The original model's loss function"),
    ("name the institutions", "Names and dates of the institutions in early engagement"),
    ("full paper's data analysis", "Full paper (not the IMRaD): replace the paired t-test on class labels"),
    ("consider reporting cohen", "Optional: Cohen's kappa with a confidence interval"),
]


def label(t):
    low = t.lower()
    return next((lab for key, lab in LABELS if key in low), cap(t[:80]))


im_block_rows = [(label(t), f"In {s}: {cap(t)}. Answer from the team's records or the adviser; never estimate.",
                  "Team / adviser", BLOCKS) for s, t in im_block]
im_lookup_rows = [(label(t), f"In {s}: {cap(t)}.", "Team", BLOCKS) for s, t in im_lookup]
im_advice_rows = [(label(t), f"In {s}: {cap(t)}. Act on it or decide not to, then delete the marker; the IMRaD "
                   "text itself is already correct.", "Team", BLOCKS) for s, t in im_advice]

im_evidence = [
    ("Classifier accuracy on Resondi device recordings is unmeasured (26 device recordings ran, none labelled).",
     "Clinician-labelled device recordings, then balanced accuracy, per-class recall, kappa.", "Team + clinicians",
     LATER),
    ("The 15 field recordings' reference labels are not linked to the recordings, so kappa and a confusion matrix "
     "cannot be computed.", "Recover the 15 paired classifications from the field records.", "Team", BEFORE),
    ("Heart: cardiologist review pending; device frequency response unmeasured; heart models untested on device; "
     "murmur sensitivity 66.7% against the 80% target.", "As in the research plan's list above.",
     "Cardiologist + team", LATER),
    ("Objectives 7 to 9 (longitudinal monitoring, rehabilitation support, practitioner review) are built but not "
     "evaluated.", "Repeated recordings, rehabilitation outcomes, and the number and time of practitioner reviews.",
     "Team + practitioner", LATER),
    ("Acceptance (n = 27, overall 3.95) was rated on the old version; the current version has not been surveyed.",
     "As in the research plan's list above: one repeated UTAUT survey on the current version.", "Team", BEFORE),
    ("Automated quality check takes 145 s per recording, too slow to run before every classification.",
     "Faster quality check, then re-time it.", "Development", LATER),
    ("The practitioner cannot change the AI's classification label directly (objective 9 says confirm, modify, or "
     "reject); disagreement goes in a comment.", "Add an override control in the app, or reword objective 9.",
     "Development / team", BEFORE),
]

im_decisions = [
    ("Reference style: the DepEd review form asks for Works Cited in MLA format; the IMRaD uses APA 7 (the research "
     "plan's form asks for APA). The panel ticked the earlier paper complete.", "Ask the adviser which style the "
     "regional fair enforces; converting the 40-odd references and in-text citations to MLA can be done in one pass.",
     "Team / adviser", BEFORE),
    ("Littmann price ₱22,000 in the Introduction.", "Keep as a cost comparison, or remove if the fair excludes money "
     "figures.", "Team", BEFORE),
    ("Heart result screen not yet viewed with a patient account (the paper says the app shows it).", "Record a heart "
     "site from a patient account and press Analyse heart sound.", "Team", BEFORE),
    ("In-app Filipino text for the heart results not checked by a Filipino speaker.", "Read it in the app and "
     "correct any wording.", "Team", BEFORE),
]

# Fair forms and documents outside the two papers, found in the team's Drive folders on 14 Nov 2026.
forms = [
    ("AI Usage Disclosure: the updated version (14 Nov 2026, Resondi-AI-Usage-Disclosure-2026-11-14) was written by AI "
     "from the project records and replaces the 29 Aug attachment in the compiled document. Its statements about who "
     "did what have not yet been checked by the team.", "Read it, correct anything wrong about the team's own work, "
     "and replace the 29 Aug attachment in the team's own ISEF form set too.", "Team", BEFORE),
    ("Student Checklist (1A), item 10, Source of Data: only 'self-collected' is ticked. The rebuilt models use the "
     "public ICBHI 2017, SPRSound and CirCor datasets.", "Also tick 'publicly available' and name the three datasets.",
     "Team", BEFORE),
    ("Project title: the papers, title page and abstract now use the title registered on the signed ISEF forms, but "
     "some documents still say Ausculta (Qualified Scientist Form 2B, the physicians' certificates, the validation "
     "form).", "Add a line explaining the rename where the fair asks; do not edit the signed certificates.", "Team",
     BEFORE),
    ("Possible conflict of interest: Genelyn O. Bautista is listed as a research adviser on the title page (and now "
     "the IMRaD cover), but she also signed the Human Participants Form (4) as the review board's medical "
     "professional. ISEF rules say board members may not be the adult sponsor, direct supervisor or qualified "
     "scientist; Form 2A names only John Lemuel J. Noche as adviser.", "Ask the SRC whether her adviser role "
     "conflicts with her board role; if it does, remove her from one of them (the papers and title page follow the "
     "title page's list).", "Team / adviser", BEFORE),
    ("Checklist of forms required: the Form 2C row (Regulated Research Institution / Industrial Setting) is blank, "
     "but a Form 2C (completed by the hardware consultant) is in the ISEF forms.", "Tick it, or mark it NA if the "
     "SRC says it does not apply.", "Team", BEFORE),
    ("Letters of 4 Nov 2026 to five cardiologists (three hospitals) and the draft CirCor heart-sound certificate are "
     "still unsigned. The draft certificate calls the heart samples 'respiratory sound characteristics'.", "Get the "
     "signatures, and correct the certificate wording to heart sounds before it is signed.", "Team", BEFORE),
    ("Review form (5 Nov 2026): logbook item 6, 'accurate and detailed description of procedures', was left unticked "
     "(neither complete nor incomplete).", "Make sure the logbook describes each procedure, with dates.", "Team",
     BEFORE),
    ("Compiled document, section V: the logbook (Project Data Book) is not in the shared folders, so a placeholder "
     "page stands in for it.", "Scan the logbook and put the pages after that page (or send the scans and the "
     "compilation is rebuilt with them).", "Team", BLOCKS),
    ("Compiled document, section III: the ISEF Abstract & Certification page was generated from the IMRaD's 250-word "
     "abstract. Questions 1, 3 and 4 are ticked from the signed forms; questions 2, 5 and 6 (own work, display-board "
     "photos, certification) are left blank.", "Ahnycca ticks questions 2, 5 and 6 herself and checks the page "
     "against the official ISEF form.", "Ahnycca", BLOCKS),
    ("Compiled document, section II: Form 7 lists the previous year's abstract and research plan as attached. The "
     "SmartSteth paper (2025), which carries its abstract, is now attached after Form 7; the 2025 research plan "
     "itself is not in the folders.", "If the fair wants the 2025 research plan as well, supply it and it is added "
     "after the paper.", "Team", BEFORE),
    ("Compiled document: the example compilation also opens with a cover page, a plagiarism report and the DepEd "
     "checklist of required forms. They were left out, following the order given (research plan first).",
     "Add them in front if the fair asks for them.", "Team", BEFORE),
]

# What the Drive folders resolved on 14 Nov 2026 (recorded so the team knows where each answer came from).
resolved = [
    ("IMRaD: ethics approval", "School Institutional Review Board, full committee, 16 Jul 2026, minimal risk; Scientific "
     "Review Committee 17 Jul 2026; data collected 17 Jul to 20 Aug 2026 (ISEF Forms 4, 1B, 1A). Also added to the "
     "research plan's Risk and Safety."),
    ("IMRaD: whether the reviewing physicians were blinded", "They confirmed the labels they were shown, against the "
     "ICBHI 2017 categories, on 21 Aug 2026; not blinded to the labels; exposure to the model output not recorded "
     "(the four certificates)."),
    ("IMRaD: who the three physicians are", "A pulmonologist, a pediatric pulmonologist and a pediatrician (the "
     "certificates and Form 2A); the paper had said three pulmonologists."),
    ("IMRaD: institutions engaged", "Interviews with written permission, 18 to 22 Aug 2026: ACE Medical Center Palawan, "
     "Palawan Medical Plaza, Posas Medical Clinic, Palawan Coop Hospital (TB-DOTS), Provincial Health Office (the "
     "permission letters). The paper's claim of pilot and classroom discussions was replaced with this."),
    ("IMRaD: cover page credits (review form, Part 3)", "Research adviser and consultants added from Form 2A."),
    ("IMRaD: abstract length (review form, Part 4, max 250 words)", "Rewritten to 250 words from 420."),
    ("Title page and table of contents", "Title page rebuilt with the typos fixed (AI-Assisted, IoT, "
     "Rehabilitation-Support System); the IMRaD now has printed page numbers, and the table of contents is generated "
     "from its real headings (the draft listed sections that do not exist); both papers now carry the registered "
     "title; the IMRaD cover credits match the title page."),
    ("ISEF AI Usage Disclosure","Updated 14 Nov: covers the November work (model rebuild, heart models, app, paper "
     "revisions), withdraws the leaked 71% figure, corrects \"AI did not train the model\" and \"paper not written by "
     "AI\"; swapped into the compiled document in place of the 29 Aug pages."),
    ("Research plan RQ 9 and IMRaD acceptance: functionality", "One physician's instrument validation, 29 Aug 2026, "
     "added (Survey Validation form)."),
    ("Form 7 attachment (continuation project)", "The previous year's paper, SmartSteth (2025), supplied by the user "
     "on 14 Nov, placed after Form 7 in the compiled document. In the compiled copy only, a stray footer photo that "
     "covered the text and hid the interview transcripts was removed, and the page numbers made continuous."),
]

n_plan = len(plan_refs) + len(plan_rq) + len(plan_analyses) + len(plan_decisions)
n_im = len(im_block_rows) + len(im_lookup_rows) + len(im_advice_rows) + len(im_evidence) + len(im_decisions)
n_block_plan = sum(r[3] == BLOCKS for r in plan_refs + plan_rq + plan_analyses + plan_decisions)
n_block_im = sum(r[3] == BLOCKS for r in im_block_rows + im_lookup_rows + im_advice_rows + im_evidence + im_decisions)

# ------------------------------------------------------------------ write
para("RESONDI · AHNYCCA'S PAPERS", size=9, bold=True, color=ACCENT, after=0)
para("What is still missing: research plan and IMRaD", size=19, bold=True, after=2)
para("Generated 14 November 2026 by build/missing/build_missing.py from the FINAL papers. The visible markers are "
     "read from the papers, so this list matches them.", size=10, italic=True, color=GREY, after=8)

heading("Priority", size=12, before=2)
for line in (
    f"{BLOCKS}: a [[...]] marker is visible in the paper. Fill or remove every one before the paper is submitted.",
    f"{BEFORE}: should be done for the regional fair, but the paper is honest without it; it already states the gap.",
    f"{LATER}: needs new data or a new model round. The paper reports it as a limitation or planned work, so it does "
    "not stop submission.",
):
    para("•  " + line, after=2)

heading("Summary", size=12)
t = doc.add_table(rows=4, cols=3); t.style = "Table Grid"
for r, vals in enumerate([["Paper", "Items", BLOCKS],
                          ["Research plan", str(n_plan), str(n_block_plan)],
                          ["IMRaD", str(n_im), str(n_block_im)],
                          ["Fair forms and the compiled document", str(len(forms)),
                           str(sum(r[3] == BLOCKS for r in forms))]]):
    for c, v in enumerate(vals):
        cell = t.rows[r].cells[c]
        if r == 0:
            shade(cell, "EBD3DE")
        run = cell.paragraphs[0].add_run(v); run.font.size = Pt(9.5); run.bold = r == 0
para("", after=2)

heading("Part 1. Research plan (Resondi-Research-Plan-Heart-and-Lung-FINAL)", size=14, before=10)
heading("1.1  Visible notes in the paper", size=11.5)
table(plan_refs)
heading("1.2  Research questions the data cannot yet fully answer (stated in Table 21)", size=11.5)
table(plan_rq)
heading("1.3  Planned analyses not yet done", size=11.5)
table(plan_analyses)
heading("1.4  Decisions for the team", size=11.5)
table(plan_decisions)

heading("Part 2. IMRaD (Resondi-IMRaD-Heart-and-Lung-FINAL)", size=14, before=10)
heading(f"2.1  Visible [[TO FILL]] facts the main claims rest on ({len(im_block_rows)})", size=11.5)
table(im_block_rows)
heading(f"2.2  Visible [[TO FILL]] facts to look up ({len(im_lookup_rows)})", size=11.5)
table(im_lookup_rows)
heading(f"2.3  Visible [[TO FILL]] notes that are advice, not missing facts ({len(im_advice_rows)})", size=11.5)
table(im_advice_rows)
heading("2.4  Evidence not yet collected (stated in the paper's limitations)", size=11.5)
table(im_evidence)
heading("2.5  Decisions and checks for the team", size=11.5)
table(im_decisions)

heading("Part 3. Fair forms and the compiled document (Resondi-Compiled-RSTF-FINAL)", size=14, before=10)
para("Found in the team's Drive folders (research papers and supporting documents) on 14 November 2026. These are not "
     "part of the IMRaD or research plan, but the fair reviews them with the papers.", size=10, italic=True,
     color=GREY, after=4)
table(forms)

heading("Resolved on 14 November 2026 from the team's Drive folders", size=14, before=10)
t2 = doc.add_table(rows=1, cols=2); t2.style = "Table Grid"
for c, (h, w) in enumerate(zip(["Item", "Answer and source"], [2.2, 4.8])):
    cell = t2.rows[0].cells[c]; cell.width = Inches(w); shade(cell, "EBD3DE")
    r = cell.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(9.5)
for item, ans in resolved:
    cells = t2.add_row().cells
    for c, (v, w) in enumerate(zip([item, ans], [2.2, 4.8])):
        cells[c].width = Inches(w)
        r = cells[c].paragraphs[0].add_run(v); r.font.size = Pt(9)
para("", after=4)

para("Send the answers to the visible markers and they can be written into the papers, rebuilt, and recopied here "
     "under the FINAL names; this list then shrinks on its next run. The full fill-in worksheet for the IMRaD, with the "
     "same markers, is in imrad/ (Resondi-IMRaD-Heart-and-Lung-Open-Items-2026-11-13).",
     size=9.5, italic=True, color=GREY, before=6)

doc.save(OUT)
print(f"wrote {OUT}: plan {n_plan} items ({n_block_plan} blocking), IMRaD {n_im} items ({n_block_im} blocking); "
      f"IMRaD markers {len(IM)} = {len(im_block)} + {len(im_lookup)} + {len(im_advice)}; plan markers {len(PL)}")
