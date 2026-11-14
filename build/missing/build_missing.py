"""A plain-language to-do list for the research plan and the IMRaD, for Ahnyccas papers/ (user, 14 Nov 2026:
"simplify the missing stuff ... so I can understand and know what to do and provide").

It stays in step with the papers: every visible [[TO FILL]] marker in build/imrad/build_imrad.py, every CONFIRM note
in the FINAL research plan, and every "[Add ... full citation]" left in the FINAL IMRaD is read from the source and
shown as a plain question. A marker with no plain wording yet is still listed (with its raw text) and warned about.

Run:  python build/missing/build_missing.py   -> Ahnyccas papers/Resondi-Missing-Items-Research-Plan-and-IMRaD.docx
"""
import ast
import os
import re

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
IMRAD_SRC = os.path.join(ROOT, "build", "imrad", "build_imrad.py")
PAPERS = os.path.join(ROOT, "Ahnyccas papers")
PLAN = os.path.join(PAPERS, "Resondi-Research-Plan-Heart-and-Lung-FINAL.docx")
IMRAD_FINAL = os.path.join(PAPERS, "Resondi-IMRaD-Heart-and-Lung-FINAL.docx")
OUT = os.path.join(PAPERS, "Resondi-Missing-Items-Research-Plan-and-IMRaD.docx")
ACCENT, GREY = RGBColor(0x8E, 0x2A, 0x52), RGBColor(0x5A, 0x5A, 0x5A)


def imrad_markers():
    """(section heading, marker text) for every FILL(...) in the IMRaD builder."""
    tree = ast.parse(open(IMRAD_SRC, encoding="utf-8").read())
    head, out = "", []
    for stmt in tree.body:
        for call in [n for n in ast.walk(stmt) if isinstance(n, ast.Call)]:
            name = getattr(call.func, "id", "")
            if name in ("H1", "H2", "H3") and call.args:
                try:
                    head = ast.literal_eval(call.args[0])
                except ValueError:
                    pass
            elif name == "FILL" and len(call.args) == 2:
                out.append((head, ast.literal_eval(call.args[1])))
    return out


# Plain wording for each IMRaD marker, found by a phrase in the marker: (short title, what to give, where to find it)
PLAIN = [
    ("name the microphone part", "Which microphone was used",
     "Which microphone was inside the device you tested in the field: the INMP441 or the MAX4466? Only one was used.",
     "Look at the device itself or the parts list / receipt."),
    ("low-frequency limit", "The microphone's lowest frequency",
     "The lowest sound frequency that microphone can pick up (for example \"60 Hz\"), and whether the field-test device "
     "used the same microphone.", "The microphone's datasheet (search \"INMP441 datasheet\" or \"MAX4466 datasheet\")."),
    ("bit depth", "Recording settings",
     "The bit depth of the recordings (for example 16-bit) and how long each piece was when the recordings were cut up "
     "for the model (for example 5 seconds).", "Edge Impulse project settings, or the device code."),
    ("loss function", "The original model's loss function",
     "The name of the loss function the original Edge Impulse model used. It is almost certainly \"categorical "
     "cross-entropy\"; just confirm it.", "Edge Impulse: open the model in expert mode and scroll past the optimizer line."),
    ("four zones", "How the lung sites group into four zones",
     "The app's rules use four zones (upper left, upper right, lower left, lower right), but you record six lung sites "
     "plus the trachea. Say which zone each site belongs to, especially the two side (mid-axillary) sites.",
     "Your design notes, or the rules in the app."),
    ("measurement unit", "Details of the 45 dB vs 32 dB test",
     "What unit and reference you measured in, the brand and model of the regular stethoscope, and how you measured the "
     "sound coming out of the regular stethoscope.", "Your field-test notes or logbook."),
    ("how many qualified", "Who rated the recording quality",
     "How many health professionals rated the recordings as good, acceptable or poor, and whether you checked that they "
     "agreed with each other.", "Your field-test records."),
    ("sampling method", "How the 27 survey respondents were chosen",
     "How you chose the 27 people who answered the acceptance survey (for example, everyone available at the clinic "
     "that day) and who was allowed to take part.", "Your survey records, or ask your adviser."),
    ("distinct from the 13", "Hospital patients vs survey patients",
     "Are the 3 patients you recorded at the private hospital the same people as any of the 13 patients who answered "
     "the survey? Just yes or no.", "Your records."),
    ("confirm this is the term", "Name of your research design",
     "What your school calls this kind of study: \"developmental-descriptive\" (what the paper says now), \"research and "
     "development (R&D)\", or \"design and development research\". It must not be called experimental.",
     "Ask your adviser."),
    ("full paper's data analysis", "A note about the 83-page full paper",
     "This note says the 83-page full paper uses a t-test where it should not. Nothing is missing in the IMRaD itself. "
     "Say \"remove the note\"; I can also give you corrected wording for the full paper.", "Nothing to look up."),
    ("consider reporting cohen", "Optional: Cohen's kappa",
     "This note suggests adding Cohen's kappa (agreement that allows for lucky guesses). It needs the 15 field-test "
     "results matched to their correct labels (Part B, item 15). If you do not have them, say \"remove the note\".",
     "Nothing to look up unless you have item B15."),
]

# ------------------------------------------------------------------ document
doc = Document()
for s in doc.sections:
    s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Inches(1)
COUNT = {"A": 0, "B": 0, "C": 0, "warn": []}


def para(text="", bold=False, italic=False, color=None, after=6, before=0, left=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after, p.paragraph_format.space_before = Pt(after), Pt(before)
    if left is not None:
        p.paragraph_format.left_indent = Inches(left)
    if text:
        r = p.add_run(text)
        r.bold, r.italic = bold, italic
        if color is not None:
            r.font.color.rgb = color
    return p


def heading(text, before=12):
    para(text, bold=True, color=ACCENT, after=4, before=before)


def item(part, title, what, where=None, goes=None):
    """'N. Title: what to do', then indented 'Where to find it' and 'It goes in' lines."""
    COUNT[part] += 1
    p = para(after=2 if (where or goes) else 6)
    r = p.add_run(f"{COUNT[part]}. {title}: ")
    r.bold = True
    p.add_run(what)
    lines = [("Where to find it: ", where), ("It goes in: ", goes)]
    lines = [(k, v) for k, v in lines if v]
    for i, (k, v) in enumerate(lines):
        q = para(after=6 if i == len(lines) - 1 else 2, left=0.6)
        rk = q.add_run(k)
        rk.italic = True
        q.add_run(v).font.color.rgb = GREY


para("RESONDI · AHNYCCA'S PAPERS", bold=True, color=ACCENT, after=0)
para("What you still need to do for the research plan and the IMRaD", bold=True, after=4)
para("Do Part A first: those are gaps that are visible in the papers right now. Part B makes the papers stronger before "
     "the fair. Part C is future work that the papers already describe as not done yet, so it does not stop you "
     "submitting.", after=4)
para("How to send answers: reply in the chat with the part, the number and your answer, for example \"A3: 16-bit, 5 "
     "seconds\". The papers are then updated and this list gets shorter. Never guess an answer: if you do not know, say "
     "so and the sentence can be reworded instead.", after=8)

# ---------------------------------------------------------------- Part A
heading("Part A. Must do before you submit")
para("These questions are marked [[TO FILL]] inside the IMRaD. Only your team knows the answers.", italic=True,
     color=GREY, after=6)
markers = imrad_markers()
for section, text in markers:
    hit = next((x for x in PLAIN if x[0] in text.lower()), None)
    if hit is None:
        COUNT["warn"].append(text[:60])
        item("A", "Missing fact", text[0].upper() + text[1:] + ".", None, f"IMRaD, {section}")
    else:
        item("A", hit[1], hit[2], hit[3], f"IMRaD, {section}")

for m in [p.text.strip() for p in docx.Document(PLAN).paragraphs if "CONFIRM" in p.text]:
    ref = m.split("CONFIRM")[0].strip(" .:[")
    item("A", "Finish a reference in the research plan",
         f"{ref}: give the full reference (all authors, year, title, journal, volume, pages, DOI), or say \"drop it\". "
         "Or say \"find it\" and I will look it up.", "Search the title online, or your concept note.",
         "Research plan, References")
for p in docx.Document(IMRAD_FINAL).paragraphs:
    if re.search(r"\[Add (the )?full citation", p.text):
        item("A", "Finish a reference in the IMRaD", f"{re.split(r'\[Add', p.text)[0].strip()}: give the full "
             "reference, or say \"find it\".", None, "IMRaD, References")

item("A", "Scan your logbook", "Scan the pages of your research logbook (Project Data Book). Its dates must match the "
     "Student Checklist (Form 1A): 17 July to 20 August 2026. Send the scans and they go into the compiled document.",
     None, "Compiled document, Part V")
item("A", "Tick three boxes on the ISEF abstract page", "On the abstract page, questions 2, 5 and 6 (your own work, "
     "photos of people on your display board, and your certification) must be answered by you. Questions 1, 3 and 4 "
     "are already ticked from your signed forms.", None, "Compiled document, Part III")

# ---------------------------------------------------------------- Part B
heading("Part B. Should do before the fair")
para("The papers are honest without these, because they already say what is missing, but each one makes them "
     "stronger.", italic=True, color=GREY, after=6)
para("Decisions (ask your adviser or the SRC)", bold=True, after=4)
item("B", "Reference style", "The fair's review form asks for a \"Works Cited\" list in MLA style, but both papers use "
     "APA. Ask your adviser which one the fair checks. If it is MLA, say so and both papers are converted.")
item("B", "Genelyn O. Bautista's two roles", "She is listed as a research adviser, but she also signed the Human "
     "Participants Form (4) as the review board's nurse. ISEF rules do not let a board member also supervise the "
     "project. Ask the SRC whether this is a problem; if it is, she is removed from one of the two roles.")
para("Forms to fix", bold=True, after=4, before=4)
item("B", "Student Checklist (Form 1A), item 10", "Under \"Source of data\", also tick \"publicly available\" and "
     "write the three public datasets: ICBHI 2017, SPRSound and CirCor.")
item("B", "Checklist of forms required", "The Form 2C row is blank, but your set has a Form 2C (from the hardware "
     "consultant). Tick it, or write NA if the SRC says it does not apply.")
item("B", "The old name Ausculta", "Form 2B, the doctors' certificates and the validation form still say Ausculta. Do "
     "not edit signed papers. If the fair asks, add a short note that the project was renamed Resondi.")
item("B", "Unsigned letters", "The 4 November letters to the five cardiologists and the heart-sound certificate are "
     "not signed yet. Before it is signed, change \"respiratory sound characteristics\" on the certificate to heart "
     "sounds.")
item("B", "Logbook procedures", "The review form left logbook item 6 (\"accurate and detailed description of "
     "procedures\") unticked. Make sure every procedure is written in the logbook with its date.")
item("B", "Read the AI Usage Disclosure", "The new disclosure (14 November) was written by AI from the project "
     "records. Read it, correct anything it gets wrong about your own work, and put it in your own ISEF form set too.")
item("B", "Form 7 attachment", "Your SmartSteth (2025) paper is attached after Form 7. Form 7 also mentions last year's "
     "research plan; if the fair wants it and you have it, send it and it is added after the paper.")
item("B", "Cover page and plagiarism report", "The example compilation also had these. Add them only if the fair asks.")
para("Checks (a few minutes each)", bold=True, after=4, before=4)
item("B", "Facility counts", "The IMRaD cites the Department of Health registry for 26,504 barangay health stations, "
     "2,682 rural health units and 836 city or municipal health centres. The registry site could not be opened "
     "automatically, so check the three numbers yourself and tell me the date you looked.",
     "nhfr.doh.gov.ph (National Health Facility Registry)")
item("B", "Heart result screen", "Log in with a patient account, record a heart site, press \"Analyse heart sound\", "
     "and check the result screen shows. The paper says the app shows it.")
item("B", "Filipino wording", "Have a Filipino speaker read the Filipino text on the heart result screen and correct "
     "anything awkward.")
para("Information to collect", bold=True, after=4, before=4)
item("B", "Repeat the acceptance survey", "The 27 survey answers were about the old version. Run the survey again on "
     "the new version, and add questions on durability, functionality, and the four instructional-support topics "
     "(diagram guide, device manual, ease of learning, app navigation). This answers Research Questions 9 and 10. "
     "Send the responses export.")
item("B", "The 15 field-test results", "Find, for each of the 15 field-test recordings, the AI's answer next to the "
     "correct label. With these, kappa and a confusion matrix can be added.", "Your field-test records.")
item("B", "The cardiologist's answer sheet", "Get the cardiologist's answers for the 25 heart recordings, so the "
     "heart results can be checked against them.")

para("Things I can do for you: just say \"go\" (nothing to look up)", bold=True, after=4, before=4)
for line in ("Compute the heart abnormality score and the murmur result for each recording, from the existing test.",
             "Add a control in the app so a practitioner can change the AI's label (objective 9 says confirm, modify "
             "or reject), or reword objective 9 to match the app.",
             "Look up any reference you cannot find."):
    para("•  " + line, after=3)

# ---------------------------------------------------------------- Part C
heading("Part C. Later (future work)")
para("Both papers already say these are not done yet, so they do not stop you submitting. They need new recordings or "
     "a new model round.", italic=True, color=GREY, after=6)
for title, what in [
    ("Labelled device recordings", "Record patients with Resondi and have two clinicians label each breath, to measure "
     "how accurate the AI is on the device itself (Research Question 7)."),
    ("Side-by-side recordings", "Record with Resondi and a regular stethoscope at the same spots, measured with one "
     "sound meter (Research Questions 1 and 8)."),
    ("Repeated recordings", "Record the same patients over several weeks, with their rehabilitation progress "
     "(Research Question 11)."),
    ("Heart recordings on the device", "Test how low a sound the device can record, then record heart sounds on the "
     "device and have a cardiologist label them."),
    ("A better murmur detector", "It finds 66.7 percent of murmurs now, against a target of 80 percent; also add murmur "
     "timing and a noise test for heart sounds."),
    ("A Filipino lung-sound dataset", "Resondi recordings of Filipino patients at the seven sites, labelled by two "
     "clinicians, with ethics approval and consent."),
    ("A faster quality check", "It takes 145 seconds per recording now, too slow to run before every analysis."),
]:
    item("C", title, what)

# ---------------------------------------------------------------- done
heading("Already done")
for line in (
    "Ethics approval, the physicians' review, the institutions you visited, the cover credits and the 250-word "
    "abstract: filled in from your Drive folders.",
    "The four unfinished IMRaD references now have full citations: Kim et al. (2021), Baraeinejad et al. (2023), and "
    "the Department of Health's facility plan (2020) and facility registry (2025).",
    "Cost figures (₱2,775 parts, ₱4,000 per unit): kept, as you decided; the ₱22,000 Littmann price comparison stays "
    "too.",
    "The reference cited as Shkarupylo et al. (2024) is really Komaryshyn & Kogut (2026); corrected in both papers, with its full citation.",
    "The acceptance results are marked as coming from the old version.",
    "The SmartSteth paper is attached after Form 7 in the compiled document.",
    "Both papers are formatted: Times New Roman 11, justified, consistent indents, references flush left with a "
    "hanging indent.",
):
    para("•  " + line, after=3)
para("Made by build/missing/build_missing.py from the FINAL papers, so it always matches what is in them.", italic=True,
     color=GREY, before=8)

import os as _os, sys as _sys  # house style: Times New Roman 11, justified, consistent indents (14 Nov)
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "style"))
import house_style  # noqa: E402
print("  house style:", house_style.apply(doc))
doc.save(OUT)
print(f"wrote {OUT}: Part A {COUNT['A']} items, Part B {COUNT['B']}, Part C {COUNT['C']}; IMRaD markers {len(markers)}")
for w in COUNT["warn"]:
    print("  WARNING: no plain wording for marker:", w)
