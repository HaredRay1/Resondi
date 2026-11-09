"""Correction pass on the PSC XI pitch deck (handoff B5).

Usage: python fix_deck.py <source.pptx> <output.pptx>
Edits run text in place so the deck's own formatting is kept.
"""
import copy
import os
import re
import sys
import zipfile
from docx import Document
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

SRC, OUT = sys.argv[1], sys.argv[2]
prs = Presentation(SRC)
S = {i: s for i, s in enumerate(prs.slides, 1)}


def shape(slide, sid, shapes=None):
    for sh in (shapes if shapes is not None else slide.shapes):
        if sh.shape_type == 6:
            hit = shape(slide, sid, sh.shapes)
            if hit is not None:
                return hit
        elif sh.shape_id == sid:
            return sh
    if shapes is None:
        raise KeyError(f"slide shape {sid} not found")
    return None


def put(n, sid, *texts, para=0, expect=None):
    """Replace the run texts of one paragraph; extra runs are blanked."""
    p = shape(S[n], sid).text_frame.paragraphs[para]
    runs = p.runs
    if expect is not None:
        assert "".join(r.text for r in runs).startswith(expect), (n, sid, "".join(r.text for r in runs))
    assert len(texts) <= len(runs), (n, sid, len(runs))
    for r, t in zip(runs, texts):
        r.text = t
    for r in runs[len(texts):]:
        r.text = ""


# ---- 1. Remove the yellow WHAT CHANGED notes (top-right shapes) ----
removed = {}
for n, s in S.items():
    for sh in list(s.shapes):
        if sh.left >= Inches(9.0) and sh.top < Inches(1.6):
            removed.setdefault(n, []).append(sh.name)
            sh._element.getparent().remove(sh._element)

# ---- 2. Slide text corrections ----
# 3: updated PSA mortality figures (181,334 / 701,884 = 25.8%)
put(3, 6, "134,074", expect="133,373")
put(3, 11, "47,260", expect="46,718")
put(3, 16, "25.8%", expect="25.7%")
put(3, 17, "181,334 deaths combined", expect="180,091")

# 7: four sound patterns
put(7, 17, "The AI suggests a sound pattern: normal, wheeze, crackle, or both (lungs).", expect="Cloud AI")
put(7, 5, "Device and platform both work. The link between them is the ask.", expect="ESP32")
put(7, 22, "Today a recording crosses from device to platform on a memory card. ₱38,000 builds the link.", expect="Store-and-forward")
put(8, 9, "4 valve points + Erb’s point", expect="5 valve")
put(6, 10, "3,518 + schools", expect="~3,500")
put(16, 6, "Ahnycca Krish N. Malimban", expect="Ahnycca")
put(16, 11, "Hared Ray A. Cabrera", expect="Hared")
put(16, 16, "Jarred Paul G. Llacuna", expect="Jarred")
put(9, 6, "Record", " a fixed 15-second clip at a named site (a lung site takes two)", expect="Record")

# 8: seven sites
put(8, 6, "6 lung fields + trachea, always in the same order", expect="8 chest sites")

# 9: deployed model is MFCC + CNN; fusion is planned
put(9, 9, "Convert", " the sound into MFCCs, a picture of its frequency content", expect="Convert")
put(9, 12, "Classify", " with a CNN: lungs normal / wheeze / crackle / both; heart normal / murmur*", expect="Classify")
put(9, 21, "*Heart classification in development; spectrogram + chromagram fusion planned · Tariq et al., 2022 · Kim et al., 2025 · ICBHI 2017 (Rocha et al., 2019)", expect="*Heart")

# 10: signal strength, acceptance, built / next
put(10, 6, "+13 dB", expect="+24.6")
put(10, 7, "stronger signal than a conventional stethoscope (45 vs 32 dB, about 4.5× the amplitude)", expect="stronger")
put(10, 14, "3.95 / 5", expect="3 of 3")
put(10, 15, "average acceptance rating across 27 respondents (UTAUT survey: “Agree”)", expect="settings")
put(10, 18, "Device · platform · guided app · quality check · lung AI", expect="Lung + heart")
put(10, 24, "Device-to-platform link · visit comparison · review dashboard · access control", expect="Automatic")
put(10, 25, "Source: Malimban, 2026, Resondi research paper · Ambient noise: quiet room 24 dB, hospital ward 35 dB, community area 42 dB", expect="Source")

# 11: chance = 25% over four classes, leakage disclosure, new budget lines
put(11, 6, "recordings from Resondi hardware matched clinician labels (40%), against 25% by chance across 4 sound classes", expect="recordings")
put(11, 7, "Small sample: n = 15 · 95% CI 19.8–64.3% · not yet above chance (p = 0.148)", expect="Small sample")
put(11, 10, "Our device sounds different from the reference audio, and our lab scores were inflated: one patient’s clips sat in both training and test sets.", expect="The model")
put(11, 13, "₱102K AI development: patient-separated retraining, a device-matched model, noise reduction · ₱120K clinical validation", expect="₱22K")
put(11, 16, "Retrain with patients kept apart, then validate on Resondi recordings, with every result still confirmed by a practitioner", expect="[≥")

# 12: price comparison against the Philippine benchmark
put(12, 8, "Unit cost ≈ ₱4,000, so a 50% margin from the first unit. About ¼ the Philippine price of an electronic stethoscope.", expect="Unit cost")

# 13: comparison table and source line
tbl = shape(S[13], 7).table
for r in tbl.rows:
    for c in r.cells:
        for p in c.text_frame.paragraphs:
            for run in p.runs:
                if run.text == "~₱22,000+":
                    run.text = "₱30,000 – 40,000"
                elif run.text == "Guided sites":
                    run.text = "Guided lung sites"
put(13, 9, "E-stethoscopes cost at least ₱30,000–40,000 in the Philippines (DOST-PCHRD). Eko CORE 300 (USD 199–249, Oct 2026) has no lung AI, and Eko’s AI is not sold here.", expect="Imported")

# 14: ₱500K seed recovered in commercial month 21 = month 35 from funding
put(14, 3, "Commercial in month 15, seed recovered by month 35", expect="Commercial")
put(14, 5, "Cumulative cash contribution (₱)", expect="Cumulative")
put(14, 14, "Month 21: passes ₱500K", expect="Month 17")
put(14, 39, "Each phase has an exit test before the next is funded. Cash contribution: ₱175,900 in commercial year 1, ₱426,900 in year 2, ₱885,700 in year 3.", expect="Each phase")
put(14, 40, "Contribution after platform and support cost, not revenue · finpack/model.py · concept note Figure 12", expect="Contribution")
# Bars redrawn to the old chart's scale (587,500 -> 1.806 in); values from finpack/model.py
scale = shape(S[14], 11).height / 587500
base = shape(S[14], 12).top
for bar_id, label_id, value, text in ((7, 6, 175900, "175,900"),
                                      (9, 8, 528700, "528,700"),
                                      (11, 10, 602800, "602,800")):
    bar, lab = shape(S[14], bar_id), shape(S[14], label_id)
    gap = bar.top - (lab.top + lab.height)
    bar.height = Emu(int(value * scale))
    bar.top = Emu(base - bar.height)
    lab.top = Emu(bar.top - gap - lab.height)
    put(14, label_id, text)

# 15: ₱500,000 ask
put(15, 3, "₱500,000 and three partners", expect="₱300,000")
put(15, 13, "Source: Resondi concept note, Tables 15–16", expect="Source")
# Concept note Table 15: ten categories (the old table had eight rows)
FUNDS = [
    ("Clinical validation", "₱120,000", "Ethics review, 300 paired field recordings"),
    ("AI development", "₱102,000", "Patient-separated retraining, quality check"),
    ("Contingency", "₱50,000", "Reserve for documented overruns only"),
    ("Cloud infrastructure", "₱48,000", "Runs the built platform: hosting, storage, backup"),
    ("Hardware refinement", "₱42,000", "Better microphones, PCB revision"),
    ("Production capital", "₱40,000", "First 10 saleable units"),
    ("Mobile application", "₱38,000", "Device-to-platform link, dashboard, visit comparison"),
    ("IP and registration", "₱25,000", "Trademark, utility model, SEC registration"),
    ("Compliance", "₱20,000", "FDA notification, data privacy, legal"),
    ("Deployment + marketing", "₱15,000", "Demos and outreach"),
]
assert sum(int(a[1:].replace(",", "")) for _, a, _ in FUNDS) == 500_000
gf = shape(S[15], 7)
tbl15 = gf.table
tr_proto = tbl15._tbl.tr_lst[-1]
while len(tbl15.rows) - 1 < len(FUNDS):
    tbl15._tbl.append(copy.deepcopy(tr_proto))
# Keep the table inside its original frame: split the body height evenly over ten rows
body_h = gf.height - tbl15.rows[0].height
row_h = Emu(body_h // len(FUNDS))
for i, (cat, amt, unl) in enumerate(FUNDS, 1):
    row = tbl15.rows[i]
    row.height = row_h
    for cell, text in zip(row.cells, (cat, amt, unl)):
        cell.margin_top = cell.margin_bottom = Emu(36000)
        runs = cell.text_frame.paragraphs[0].runs
        runs[0].text = text
        runs[0].font.size = Pt(11)
        for r in runs[1:]:
            r.text = ""

# 16: founder roles as now stated
put(16, 7, "CEO · data and model operations", expect="Managing")
put(16, 12, "CTO · platform and security", expect="Platform")
put(16, 17, "COO · production and operations", expect="Hardware")

# Footers that now run long: widen to the page-number column
for n, sid in ((7, 22), (9, 21), (10, 25), (13, 9)):
    shape(S[n], sid).width = Inches(10.6) - shape(S[n], sid).left + Inches(0.89)

# 16: Jarred's longer role wraps; align his card's text with Hared's
for mine, ref in ((16, 11), (17, 12), (18, 13)):
    shape(S[16], mine).top = shape(S[16], ref).top
    shape(S[16], mine).height = shape(S[16], ref).height

# 17: seven sites, school abbreviation
# source lines: the concept note's sections are named, not numbered, and its tables were renumbered 2 Nov
put(5, 24, "Targets paraphrased from UN SDG Goal 3 (3.4, 3.8, 3.c) · concept note, Proposed Startup Solution", expect="Targets")
put(6, 24, "Source: DOH facility registry, 2025 · Resondi concept note, Market Analysis (Figure 9)", expect="Source")
put(12, 25, "Source: Resondi concept note, Tables 5–6 and business model canvas", expect="Source")

# 2: the problem in the pitch script's own words (build/script5/pitch_4m30.txt)
put(2, 3, "In a barangay health station, a midwife listens to a patient’s chest.", expect="Tuesday")
put(2, 4, "When the exam ends, the sound is gone. Nobody can review what she heard.", expect="A nurse")
put(2, 5, "Walang resibo. ", "There is nothing to review.", expect="By then")
put(2, 6, "Respiratory disease here is not only a hospital problem. It is a monitoring problem.", expect="All that")
put(2, 7, "How chest exams are documented in primary care today", expect="Illustrative")

# 17: closes on the script's last lines
put(17, 2, "LISTEN · ANALYZE · REHABILITATE", expect="BACK TO")
put(17, 5, "Today", expect="Tuesday")
put(17, 6, "Every sound is recorded at the same seven sites, tagged and saved.", expect="The nurse")
put(17, 9, "Next visit", expect="Friday")
put(17, 10, "The doctor plays it beside the last one and sees whether the patient is recovering.", expect="The doctor")
put(17, 11, "Because every breath carries information. ", "It listens to recovery.", expect="Every breath")
put(17, 13, "Resondi · Hear smarter. Breathe better. · Team Wheezards, PPCNSHS", expect="Ausculta")

# ---- 3. Old raster logo -> text wordmark until the Resondi logo exists ----
def wordmark(n, sid, size, align):
    pic = shape(S[n], sid)
    box = S[n].shapes.add_textbox(pic.left, pic.top, pic.width, pic.height)
    box.name = "Resondi wordmark"
    tf = box.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = "Resondi"
    r.font.name = "Poppins"
    r.font.bold = True
    r.font.size = Pt(size)
    r.font.color.rgb = RGBColor(0xE9, 0x1E, 0x76)
    pic._element.getparent().remove(pic._element)

wordmark(1, 2, 96, PP_ALIGN.CENTER)
wordmark(17, 12, 48, PP_ALIGN.LEFT)

# ---- 4. Speaker notes: drop REVISION NOTE, keep the script, fix numbers ----
# The notes are the 6 Nov pitch script (final/03), spoken lines only, one section
# per slide, so the script document and the deck cannot drift apart.
SCRIPT_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "final",
                          "03-Resondi-Pitch-Script.docx")


def pitch_by_slide(path):
    out, n = {}, None
    for p in Document(path).paragraphs:
        text = p.text.strip()
        m = re.match(r"^SLIDE (\d+)\b", text)
        if m:
            n = int(m.group(1))
            out[n] = [text]
        elif n and text and not (p.runs and p.runs[0].italic):  # italics are stage directions
            out[n].append(text.replace("[CUT]", "(optional)"))
    return {k: "\n".join(v) for k, v in out.items()}


NOTES = pitch_by_slide(SCRIPT_SRC)
assert sorted(NOTES) == list(range(1, 18)), sorted(NOTES)
NOTES[13] += ("\n\nIF ASKED ABOUT THE EKO CORE 300: it launched on 22 October 2026 at "
              "USD 199–249, so price alone is no longer our edge. It detects one cardiac "
              "finding, has no lung AI and no guided lung placement, and Eko’s AI "
              "subscription is not offered in the Philippines. No vendor we reviewed "
              "documents same-site comparison across visits.")
for n, s in S.items():
    s.notes_slide.notes_text_frame.text = NOTES[n]

# ---- 4b. Backup slides 18-20: tiers, bundles (concept note Tables 7-8), device render ----
# Not in the 4:30 pitch; shown only if a judge asks about pricing.
FIGS_NOV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "figs_nov")
BACKUP = [
    ("Resondi-Subscription-Tiers-Slide.png",
     "BACKUP · PRICING (concept note Table 7). Proposed prices, not yet validated with buyers. "
     "Essential at ₱1,500 is what the projections use; Clinical and Network only add above it, "
     "and both need the features the ₱38,000 mobile-application line builds."),
    ("Resondi-Bundles-And-Offers.png",
     "BACKUP · BUNDLES (concept note Table 8). No discount comes out of the ₱600 per facility per "
     "month that pays cloud operation and the replacement reserve. Starter's discount comes from "
     "device margin only. Limited trial about ₱750, feature trial ₱200; offers do not stack."),
    ("../../figures/Resondi-Device-3D.png",
     "BACKUP · THE DEVICE. Concept render from our Blender model; proportions and colours are "
     "illustrative. The real enclosure is 173 × 80 × 70 mm (concept note Table 1)."),
]
blank = min(prs.slide_layouts, key=lambda l: len(l.placeholders))
for png, note in BACKUP:
    sl = prs.slides.add_slide(blank)
    for ph in list(sl.placeholders):
        ph._element.getparent().remove(ph._element)
    sl.background.fill.solid()
    sl.background.fill.fore_color.rgb = RGBColor(0xFF, 0xF5, 0xF9)
    path = os.path.join(FIGS_NOV, png)
    pic = sl.shapes.add_picture(path, 0, 0, width=prs.slide_width)
    if pic.height > prs.slide_height:  # taller than 16:9: trim empty floor, top and bottom
        spare = 1 - prs.slide_height / pic.height
        pic.crop_top, pic.crop_bottom = spare * 0.6, spare * 0.4
        pic.height = prs.slide_height
    pic.top = (prs.slide_height - pic.height) // 2
    if "Device-3D" in png:
        cap = sl.shapes.add_textbox(Inches(0.5), Inches(6.85), Inches(12.3), Inches(0.4))
        run = cap.text_frame.paragraphs[0].add_run()
        run.text = "Concept render from the team’s Blender model. Proportions and colours are illustrative."
        run.font.name, run.font.size = "Poppins", Pt(12)
        run.font.color.rgb = RGBColor(0x8E, 0x2A, 0x52)
    pic.name = os.path.basename(png)[:-4]
    sl.notes_slide.notes_text_frame.text = note

prs.core_properties.title = "Resondi · Pitch Deck · Philippine Startup Challenge XI"
prs.save(OUT)

# ---- 5. Product rename everywhere else (alt text, remaining runs, notes) ----
PAT = re.compile(r"\b(AUSCULTA|Ausculta|ausculta|AUSCORA|Auscora|auscora)\b")
def sub(m):
    w = m.group(1)
    return "RESONDI" if w.isupper() else ("Resondi" if w[0].isupper() else "resondi")

tmp = OUT + ".tmp"
with zipfile.ZipFile(OUT) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    hits = 0
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename.endswith((".xml", ".rels")):
            text = data.decode("utf-8")
            text, k = PAT.subn(sub, text)
            hits += k
            data = text.encode("utf-8")
        zout.writestr(item, data)
os.replace(tmp, OUT)

print("removed note shapes:", {k: len(v) for k, v in removed.items()})
print("renamed occurrences:", hits)
