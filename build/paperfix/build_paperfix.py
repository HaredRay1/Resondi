"""Paper revision pack: pasteable corrections for the user's 83-page research paper.

The paper is the user's own document (CLAUDE.md A4.1), so nothing here edits it.
Each item says where the text goes, what to do, why, and gives the revised text.
Run:  python build_paperfix.py   (writes deliverables/Resondi-Paper-Revision-Pack.docx)
"""
import os
import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

import figs
from facts import (SIGNAL, NOISE, CLARITY, RESPONSE, AGREE, CHANCE, UTAUT, UTAUT_OVERALL,
                   N_RESP, LO, HI, P_CHANCE, K_NEEDED, TOTAL_TIME, QA_SHARE, AMP_RATIO)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "deliverables", "Resondi-Paper-Revision-Pack.docx")

PRIMARY, INK, GREY = RGBColor(0x8E, 0x2A, 0x52), RGBColor(0x3A, 0x27, 0x30), RGBColor(0x8A, 0x74, 0x80)
PAPER_FONT = "Times New Roman"

DEV, CONV = SIGNAL
QR, HW, CA = NOISE["Quiet room"], NOISE["Hospital ward"], NOISE["Community area"]
K, N = AGREE
R = {k: v[0] for k, v in RESPONSE.items()}
SD = {k: v[1] for k, v in RESPONSE.items()}

doc = Document()
st = doc.styles["Normal"]
st.font.name = "Calibri"
st.font.size = Pt(10.5)
st.paragraph_format.space_after = Pt(0)
sec = doc.sections[0]
sec.left_margin = sec.right_margin = Inches(0.9)
sec.top_margin = sec.bottom_margin = Inches(0.8)


def P(text="", size=10.5, bold=False, italic=False, color=INK, after=6, before=0, font=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_after, pf.space_before, pf.line_spacing = Pt(after), Pt(before), 1.15
    if text:
        r = p.add_run(text)
        r.bold, r.italic = bold, italic
        r.font.size, r.font.color.rgb = Pt(size), color
        if font:
            r.font.name = font
    return p


def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), fill)
    tcPr.append(sh)


def borders(table, color="BFBFBF"):
    tblPr = table._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{side}")
        e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4"); e.set(qn("w:color"), color)
        b.append(e)
    tblPr.append(b)


def banner(label, text, fill="FBE9F0", color=PRIMARY):
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = t.rows[0].cells[0]
    shade(c, fill)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(label + "  "); r.bold = True; r.font.size = Pt(8.5); r.font.color.rgb = color
    r = p.add_run(text); r.font.size = Pt(9.5); r.font.color.rgb = INK
    P(after=2)


ITEMS = []


def item(title, where, action, why):
    ITEMS.append((title, where, action))
    P(f"{len(ITEMS)}. {title}", size=13, bold=True, color=PRIMARY, before=10, after=4)
    banner("WHERE", where)
    banner("DO THIS", action, fill="F2F2F2", color=INK)
    P("Why: " + why, size=9.5, italic=True, color=GREY, after=6)


def paste(*paras, heading=None):
    """Grey-ruled block of paper-ready text, in the paper's own typeface."""
    t = doc.add_table(rows=1, cols=1)
    borders(t)
    c = t.rows[0].cells[0]
    first = True
    if heading:
        p = c.paragraphs[0]
        r = p.add_run(heading); r.bold = True; r.font.name = PAPER_FONT; r.font.size = Pt(11)
        p.paragraph_format.space_after = Pt(4)
        first = False
    for text in paras:
        p = c.paragraphs[0] if first else c.add_paragraph()
        first = False
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(text); r.font.name = PAPER_FONT; r.font.size = Pt(11)
    P(after=6)


def mono_table(rows, widths, caption=None, note=None):
    """Monotone table (CLAUDE.md A4.4: all tables are black / grey / white)."""
    if caption:
        for line in caption:
            P(line, size=11, bold=(line == caption[0]), italic=(line != caption[0]), font=PAPER_FONT, after=0)
        P(after=2)
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    borders(t, "7F7F7F")
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j)
            c.width = Inches(widths[j])
            if i == 0:
                shade(c, "D9D9D9")
            p = c.paragraphs[0]
            r = p.add_run(str(val)); r.font.name = PAPER_FONT; r.font.size = Pt(10); r.bold = (i == 0)
    if note:
        P(note, size=9.5, italic=True, font=PAPER_FONT, before=2)
    P(after=6)


def image(path, caption):
    doc.add_picture(path, width=Inches(6.0))
    P(caption, size=10.5, italic=True, font=PAPER_FONT, after=8)


# ═════════════════════════════════════════════════════════════ FRONT MATTER
P("Resondi", size=24, bold=True, color=PRIMARY, after=0)
P("Revision Pack for the 83-Page Research Paper", size=15, bold=True, color=INK, after=2)
P("Paste-ready corrections to RIM-FULLPAPER-2026, prepared 30 October 2026", size=10.5,
  italic=True, color=GREY, after=10)

P("How to use this pack", size=12, bold=True, color=PRIMARY, after=3)
for line in (
    "Nothing in this pack has been written into your paper. Each numbered item gives the page "
    "and section, what to do (replace, insert or delete), one line on why, and the revised "
    "text in a ruled box. Copy the text in the box into your document.",
    "Page numbers are those printed in the footer of the PDF (Page N of 83). Items run in page "
    "order, so you can work through the paper once from front to back.",
    "Four figures in the paper are images that print superseded values, so their corrected "
    "captions would contradict the picture. Replacement images are included at the right "
    "items and saved as separate PNG files in figures/paperfix/.",
    "Items marked DECIDE need a choice from you before you paste. Everything else is a "
    "straight correction to match the verified figures in CLAUDE.md, Part A.",
):
    P("•  " + line, after=3)

P("What this pack corrects", size=12, bold=True, color=PRIMARY, before=8, after=3)
for line in (
    "Signal strength: 32.49 vs 7.89 dB becomes 45 vs 32 dB, a 13 dB gap, about 4.5 times "
    "the amplitude.",
    "Ambient noise: 25.67 to 32.49 dB becomes 24 dB (quiet room), 35 dB (hospital ward) and "
    "42 dB (community area).",
    "Figure 4.4 rewritten to match Table 5. All four timings in the current text contradict "
    "it, and the connection step is missing.",
    "McNemar's test and all three paired-samples t-tests removed. Classification agreement "
    "is reported with a Wilson interval and an exact binomial test against chance.",
    "The Data Analysis section reworded. It currently describes a device comparison, not a "
    "test of the classifier.",
    "Six lung locations become seven sites: the tracheal reference plus six lung fields.",
    "The reason the reference-dataset scores cannot be used as evidence is disclosed in "
    "plain language.",
    "End-user acceptance rewritten around the UTAUT instrument actually used: 27 "
    "respondents, not 30, with results reported. Section G deleted.",
    "Mel-spectrogram corrected to MFCC, which is what the deployed model uses.",
    "The Conclusions section, which is pasted two and a half times, replaced by a single "
    "copy.",
    "Product name: Ausculta becomes Resondi.",
):
    P("•  " + line, after=2)

banner("CHECK FIRST",
       "The corrected signal and noise values (45 / 32 dB and 24 / 35 / 42 dB) come from the "
       "verified figures in CLAUDE.md, not from anything printed in the paper. The paper's own "
       "figures and text print 32.49 / 7.89 dB and 27.88 / 32.49 / 25.67 dB. Before pasting, make "
       "sure your raw measurement sheets give the corrected values, because a panel may ask to "
       "see them.", fill="FFF2CC", color=RGBColor(0x7F, 0x60, 0x00))
doc.add_page_break()

# ═════════════════════════════════════════════════════════════ 1 NAME
item("Product name throughout",
     "Whole paper: 64 occurrences of 'Ausculta' and 1 of 'AUSCULTA'.",
     "Find and replace. In Google Docs, open Edit > Find and replace, tick 'Match case' and "
     "'Match using regular expressions', find \\bAusculta\\b and replace with Resondi. In "
     "Word, tick 'Match case' and 'Find whole words only', then find Ausculta. Do not do a plain "
     "replace without these options: it would also change 'Auscultation' to 'Resondition'.",
     "The product is now Resondi. The word boundary leaves auscultation, auscultatory and the "
     "recording filenames in Table 6 (AUSCULTA0001.WAV) untouched; those are real filenames "
     "and should stay as they are.")
paste("Resondi: A CNN-Assisted Auscultation Instrument for Lung Sound Monitoring, Longitudinal "
      "Tracking, and Rehabilitation Support-System",
      heading="Title line (page 1), after the replacement")

# ═════════════════════════════════════════════════════════════ 2 ABSTRACT
item("Abstract",
     "Page 1. The paragraph beginning 'Abstract—Respiratory illnesses remain…' and ending "
     "'…further validation recommended for actual healthcare settings.'",
     "Replace the whole paragraph. Leave the Keywords line as it is.",
     "The current abstract cites McNemar's test, six locations, a mel-spectrogram, and five "
     "acceptance dimensions that the questionnaire never measured. It also reports none of "
     "the device's measured results.")
paste(
    "Abstract—Respiratory illnesses remain a significant health concern, creating a need for "
    "accessible and systematic respiratory-sound monitoring, particularly in settings where "
    "assessment relies heavily on conventional auscultation. To address this challenge, the "
    "study developed Resondi, an artificial intelligence-assisted smart stethoscope and "
    "respiratory monitoring platform designed for standardized respiratory-sound recording, "
    "recording-quality assessment, sound-pattern classification, longitudinal monitoring, and "
    "professional review. The system integrates an acoustic stethoscope chest piece, microphone "
    "and preamplifier, ESP32 microcontroller, Bluetooth Low Energy communication, rechargeable "
    "power source, and a mobile-first application with guided auscultation at seven "
    "standardized sites: six lung fields and a tracheal reference. Respiratory recordings "
    "undergo noise reduction, filtering, and segmentation, and are represented as "
    "mel-frequency cepstral coefficients (MFCCs) before convolutional neural network "
    "classification into normal, wheeze, crackle, and combined wheeze-and-crackle patterns. "
    "The ICBHI 2017 Respiratory Sound Database was used as the reference dataset for model "
    f"development. The device produced a mean signal strength of {DEV} dB against {CONV} dB "
    f"for a conventional stethoscope, a {DEV - CONV} dB difference corresponding to roughly "
    f"{AMP_RATIO:.1f} times the amplitude, and {CLARITY[0]}% of recordings were rated good in "
    f"clarity. On {N} field recordings compared against reference labels, the classifier "
    f"agreed on {K} ({K / N:.0%}; 95% CI {LO:.1%}–{HI:.1%}), which did not differ "
    f"significantly from the {CHANCE:.0%} expected by chance across four categories (exact "
    f"binomial test, p = {P_CHANCE:.3f}). Scores obtained on the reference dataset were not "
    "independent of the training data and are not reported as evidence of performance. "
    f"End-user acceptance, assessed among {N_RESP} respondents with a questionnaire adapted "
    "from the Unified Theory of Acceptance and Use of Technology, averaged "
    f"{UTAUT_OVERALL:.2f} on a five-point scale (Agree). Overall, Resondi demonstrates the "
    "feasibility of integrating digital auscultation, AI-assisted sound analysis, and "
    "longitudinal monitoring into a single platform as a supportive tool for respiratory "
    "assessment and professional review. Classification accuracy has not yet been "
    "established, and retraining on a patient-separated dataset followed by clinical "
    "validation is required before use in healthcare settings.")

# ═════════════════════════════════════════════════════════════ 3 MATERIALS
item("Materials paragraph",
     "Page 3, under 'III. MATERIALS AND METHODS', heading 'Materials'. The paragraph "
     "beginning 'Various materials and instruments…' and ending '…impact on the community.'",
     "Replace the whole paragraph.",
     "It repeats the mel-spectrogram claim, 30 participants, and the durability and "
     "community-impact dimensions. None of these is in the questionnaire actually "
     "administered.")
paste(
    "Various materials and instruments supported the different phases of the development and "
    "validation process. The ICBHI 2017 Respiratory Sound Database served as the reference "
    "dataset for training and testing the classification model. Digital modeling software and "
    "a 3D printer were used to design and fabricate the device casing, while an ESP32 "
    "microcontroller, microphone, preamplifier, rechargeable battery, and other electronic "
    "components were used to build the smart stethoscope prototype. BLE communication modules "
    "and optional MicroSD storage supported wireless data transmission and local recording "
    "backup during system integration. The Base44 platform was used to develop the Resondi "
    "mobile application, including its user interface, role-based workflows, and research "
    "dashboard, while signal-processing tools supported noise reduction, filtering, "
    "segmentation, and the extraction of mel-frequency cepstral coefficients (MFCCs) for the "
    "CNN-based classification model. Statistical tools were used to compute classification "
    "metrics on the reference dataset and agreement with reference labels during device "
    "testing. Clinical validation involved review by three pulmonologists, one of whom was "
    "also a pediatrician, and device testing among three patients at a private hospital under "
    "an attending physician's supervision. Documentation tools, including consent forms and "
    "data recording sheets, were used to ensure proper monitoring and record-keeping "
    "throughout the clinical validation process. Lastly, a five-point Likert-scale "
    "questionnaire adapted from the Unified Theory of Acceptance and Use of Technology "
    f"(Venkatesh et al., 2003) was used for end-user acceptance testing among {N_RESP} "
    "respondents across Puerto Princesa City, assessing performance expectancy, effort "
    "expectancy, social influence, and facilitating conditions.")

# ═════════════════════════════════════════════════════════════ 4 TABLE 1.1 TEXT
item("Description of the reference dataset (labels used)",
     "Page 4, the paragraph under Table 1.1 beginning 'Table 1.1 describes the reference "
     "dataset.' Only its last sentence changes: 'The present study uses the cycle-level "
     "crackle and wheeze annotations rather than the patient-level condition labels, "
     "consistent with…'",
     "Replace that last sentence (from 'The present study uses…' to the end of the "
     "paragraph) with the text below.",
     "The sentence is not accurate for the model evaluated. It was trained on patient-level "
     "condition labels, which is one of the three reasons its reference-dataset scores are "
     "inflated (item 7).")
paste(
    "Although the database provides cycle-level crackle and wheeze annotations, the model "
    "evaluated in this study was trained on patient-level condition labels (asthma, "
    "bronchiolitis, pneumonia, and healthy), applied to every segment of a patient's audio and "
    "displayed in the application as the four sound patterns. Because a patient's condition is "
    "not audible in every segment, this labelling is treated as a limitation under Manual "
    "(Reference Dataset) Testing. The retraining described there uses the cycle-level "
    "annotations, so that each segment is labelled from its own crackle and wheeze flags.")

# ═════════════════════════════════════════════════════════════ 5 SITES
item("Guided auscultation sites: six becomes seven",
     "Page 5, heading 'Guided Auscultation and Recording Workflow Development'. The "
     "paragraph beginning 'The existing lung map guided recordings…'",
     "Replace the whole paragraph.",
     "The protocol records seven sites: a tracheal reference followed by the six lung fields "
     "the paper already names. Each site matches one of the seven ICBHI chest-location codes "
     "that Table 1.1 already lists. A nine-site protocol is planned, not built, so it is not "
     "mentioned here.")
paste(
    "The lung map guided recordings at seven standardized sites. A tracheal reference was "
    "captured first, over the suprasternal notch, followed by six lung fields taken in "
    "left–right pairs: right upper and left upper (second intercostal space, midclavicular "
    "line), right middle and left middle (fourth to fifth intercostal space, mid-axillary "
    "line), and right lower and left lower (infrascapular, T8–T10, beside the spine). Each "
    "site corresponds to one of the seven chest-location codes of the ICBHI 2017 database. The "
    "tracheal capture serves as a reference and is not classified as a lung field. The user "
    "selected a site, positioned the stethoscope, confirmed placement, recorded, and saved the "
    "audio with its anatomical location and recording metadata; the application did not "
    "advance to the next site until the current one had been recorded. Repeated recordings "
    "were allowed when necessary.")

# ═════════════════════════════════════════════════════════════ 6 PREPROCESSING
item("Audio preprocessing and CNN model development",
     "Page 5, heading 'Audio Preprocessing and CNN Model Development'. The paragraph "
     "beginning 'Reference recordings and eligible device recordings…'",
     "Replace the whole paragraph.",
     "The deployed model takes MFCCs, not a mel-spectrogram image. The three-branch fusion "
     "model is planned and must not be described as built.")
paste(
    "Reference recordings and eligible device recordings underwent preprocessing, including "
    "resampling to 16 kHz, noise reduction, amplitude normalization, and segmentation into "
    "fixed-length windows. Each window was represented as mel-frequency cepstral coefficients "
    "(MFCCs), and a dedicated CNN model was developed to classify respiratory sound patterns "
    "as normal, wheeze, crackle, or wheeze plus crackle. Additional categories such as "
    "other/abnormal, uncertain, and insufficient quality were used at the platform level. The "
    "model was not used to independently diagnose specific diseases. A three-branch "
    "architecture fusing spectrogram, MFCC, and chromagram features is planned but was not "
    "part of the evaluated build.")

# ═════════════════════════════════════════════════════════════ 7 LEAKAGE
item("Manual (reference dataset) testing: disclosure",
     "Page 5, heading 'Manual (Reference Dataset) Testing'. The two-sentence paragraph "
     "beginning 'Reference recordings were processed using the trained model…'",
     "Replace the whole paragraph.",
     "The reference-dataset scores (71.1% test, 83.4% and 83.7% validation) are inflated. The "
     "paper does not quote them, but it says they were obtained, so it must also say why they "
     "are not reported. The 40% field agreement is the only estimate independent of the "
     "training data.")
paste(
    "Reference recordings were processed using the trained model, and accuracy, precision, "
    "sensitivity, specificity, F1-score, and a confusion matrix were obtained. These scores "
    "are not reported as evidence of performance, for three reasons identified after "
    "training. First, the recordings were cut into five-second segments at a one-second "
    "stride, so consecutive segments shared four of their five seconds of audio, and the "
    "segments were then divided into training, validation, and test sets at random rather "
    "than by patient. Near-identical audio from the same patient therefore appeared on both "
    "sides of every split. Second, no grouping key was supplied to keep a patient's segments "
    "together in either split. Third, each segment carried its patient's overall condition "
    "label rather than a label for the sounds it actually contained, so the model could "
    "succeed by recognizing the patient rather than the sound pattern. The reference-dataset "
    "scores are therefore optimistic and not independent of the training data.",
    "The dataset is being rebuilt by assigning whole patients to the training or test set "
    "before any segmentation, cutting one non-overlapping segment per annotated respiratory "
    "cycle, and labelling each segment from its own crackle and wheeze annotations. Accuracy "
    "is expected to fall when the model is retrained on this dataset, and the confusion matrix "
    "and per-class recall will be reported alongside it, since the most common class (healthy "
    "cycles) makes up about 53% of the corpus. The field agreement reported under Results is "
    "the only estimate in this study that is independent of the training data.")

# ═════════════════════════════════════════════════════════════ 8 ACCEPTANCE METHOD
item("End-user acceptance testing (method)",
     "Page 7, heading 'End User Acceptance Testing'. The paragraph beginning 'A 5-point "
     "Likert scale survey assessed user-friendliness…'",
     "Replace the whole paragraph.",
     "The questionnaire administered was a UTAUT instrument. It has no durability or "
     "community-impact item, and it has 27 responses, not 30.")
paste(
    "End-user acceptance was assessed using a questionnaire adapted from the Unified Theory of "
    f"Acceptance and Use of Technology (UTAUT; Venkatesh et al., 2003), administered to {N_RESP} "
    "respondents across Puerto Princesa City: 13 patients, 13 general respondents, and one "
    "health practitioner. Twelve items were rated on a five-point Likert scale and grouped "
    "into performance expectancy, effort expectancy, social influence, and facilitating "
    "conditions, the last assessing the degree to which conformity with recognized "
    "medical-device standards influenced confidence in the device. Four further items used a "
    "yes/no response format, one with a 'maybe' option, and are reported as frequencies. "
    "Acceptance testing also involved three patients at a private hospital, conducted under "
    "the guidance and supervision of an attending physician who reviewed and consented to the "
    "procedure. The system's purpose and limitations were explained to participants before "
    "the survey was administered.")

# ═════════════════════════════════════════════════════════════ 9 DATA ANALYSIS
item("Data Analysis, subsections B to G",
     "Pages 7–8, under 'Data Analysis'. Subsection A stays as it is. Subsections B, C, D, E "
     "and F are each replaced. Subsection G is deleted. Table 1.4 (the Likert interpretation "
     "scale) stays.",
     "Replace the body text of B, C, D, E and F with the text below, keeping each lettered "
     "heading where shown. Delete G, both its heading 'G. End-User Preference Evaluation' "
     "and its paragraph.",
     "C, D and E each specify a paired-samples t-test. A t-test compares means of continuous "
     "data; it cannot be applied to class labels (D), ordinal quality grades (E), or one pair "
     "of recordings (C). D also describes a comparison of 'two sources of recordings', which "
     "reads as a device comparison when it is a test of the classifier. G describes a "
     "preference survey whose results appear nowhere in the paper, and the questionnaire "
     "export contains no preference items.")
paste(
    "Respiratory-sound recording quality was evaluated using signal strength, clarity ratings, "
    "and ambient noise measurements. The response times of the smart-stethoscope connection, "
    "sound recording, recording-quality assessment, signal preprocessing, and classification "
    "output were measured in seconds. Mean and standard deviation were computed to summarize "
    "the results.",
    heading="B. Assessment of Recording Quality and System Performance")
paste(
    "Classification performance on the reference dataset was computed using accuracy, "
    "precision, recall (sensitivity), and F1-score; for the reasons given under Manual "
    "(Reference Dataset) Testing, these values are not reported as evidence of performance. "
    "The effect of ambient noise on classification was examined descriptively by classifying "
    "a clean recording and a noise-contaminated recording and comparing the outputs (Table 6). "
    "A single pair of recordings does not support a significance test, and none was applied.",
    heading="C. Evaluation of Artificial Intelligence Classification Performance")
paste(
    f"The classifications produced by the model for {N} recordings acquired with the Resondi "
    "device were compared against reference labels assigned to the same recordings. This is a "
    "test of the classifier's accuracy on device recordings, not a comparison between two "
    "recording devices. Agreement was reported as the proportion of matching classifications "
    "with a 95% Wilson score confidence interval, and tested against the "
    f"{CHANCE:.0%} agreement expected by chance across four categories using an exact "
    "one-sided binomial test at a 0.05 level of significance.",
    heading="D. Classification Agreement")
paste(
    "Signal strength of recordings acquired with the Resondi device and with a conventional "
    "acoustic stethoscope was measured under the same conditions and compared descriptively. "
    "Recordings acquired with Resondi were rated by qualified healthcare professionals as "
    "good, acceptable, or poor against predetermined recording-quality criteria, and the "
    "ratings were summarized as percentages.",
    heading="E. Comparative Analysis of Recording Quality")
paste(
    "Weighted mean and standard deviation were computed for each UTAUT construct and for the "
    "twelve Likert items overall, and interpreted using the scale in Table 1.4. Internal "
    "consistency was estimated with Cronbach's alpha for each construct of two or more items. "
    "Yes/no items were reported as frequencies and percentages.",
    heading="F. End-User Acceptance Evaluation")

# ═════════════════════════════════════════════════════════════ 10 TABLE 3
item("Table 3 and its paragraph",
     "Page 9, 'Table 3. Recording Quality Parameters and Findings of the Ausculta Device' "
     "and the paragraph after it, beginning 'As shown in Table 3…'",
     "Replace the three rows of the table, then replace the paragraph.",
     "The signal strength (32.49 dB) and noise range (25.67–32.49 dB) are superseded. The "
     "current text also never states what the device was compared against.")
mono_table(
    [["Parameter", "Resondi Finding", "Interpretation"],
     ["Signal Strength", f"{DEV} dB (conventional stethoscope: {CONV} dB)",
      f"Stronger measurable signal: a {DEV - CONV} dB difference, about {AMP_RATIO:.1f} times "
      "the amplitude"],
     ["Clarity of Recordings", f"{CLARITY[0]}% Good",
      f"{CLARITY[1]}% acceptable and {CLARITY[2]}% poor; most recordings suitable for analysis"],
     ["Ambient Noise", f"{QR}–{CA} dB",
      "Recording remained possible in a quiet room, a hospital ward, and a community area"]],
    [1.5, 2.0, 3.1],
    caption=["Table 3.", "Recording Quality Parameters and Findings of the Resondi Device"])
paste(
    f"As shown in Table 3, Resondi produced a mean signal strength of {DEV} dB against {CONV} "
    f"dB for a conventional stethoscope, {CLARITY[0]}% of its recordings were rated good in "
    f"clarity, and it continued to record at ambient noise levels of {QR} to {CA} dB. Because "
    f"the decibel scale is logarithmic, the {DEV - CONV} dB difference corresponds to roughly "
    f"{AMP_RATIO:.1f} times the sound-pressure amplitude; it is not a ratio of the two decibel "
    "values. These findings indicate that the device can capture usable respiratory sounds "
    "across the tested settings, consistent with studies showing that electronic stethoscopes "
    "enhance sound acquisition (Wu et al., 2022; McLane et al., 2021). The margin between "
    f"signal and ambient noise narrows from about {DEV - QR} dB in a quiet room to about "
    f"{DEV - CA} dB in a community area, which is where recording quality is most at risk.")

# ═════════════════════════════════════════════════════════════ 11 TABLE 4 (DECIDE)
item("DECIDE: Table 4, cost of materials",
     "Pages 9–10, 'Table 4. Cost of Materials' (total Php 2,094.47) and the paragraph "
     "after Figure 3.",
     "Choose one option. (a) Recommended: keep Table 4 as it is, because it is the cost of "
     "the prototype that was actually built and tested, and add the sentence below at the end "
     "of the paragraph after Figure 3. (b) Replace Table 4 with the new bill of materials "
     "(₱2,775.00). Only choose (b) if Table 2, Figure 2.3 and the device description are "
     "updated to the same hardware.",
     "The new bill of materials prices the version 2.0 build, which differs from the one "
     "tested: a Li-ion battery with an LM2577 boost converter instead of the power bank, no "
     "separate MAX9814 preamplifier, Wi-Fi instead of Bluetooth, and a 32 GB card. Putting "
     "its total into Table 4 alone would make the paper contradict itself.")
paste(
    "A revised bill of materials for the version 2.0 build, which replaces the power bank "
    "with a rechargeable Li-ion battery and boost converter and reads the microphone "
    "digitally without a separate preamplifier, is estimated at ₱2,775.00 per prototype unit. That estimate excludes a battery protection "
    "circuit and charging module, which the final design will require.",
    heading="Sentence to add for option (a)")
banner("ALSO NOTE",
       "Use the ₱2,775.00 bill of materials (PLA casing, 20 × 4 LCD, 32 GB card). The VER 2.0 "
       "file on this PC still reads PETG and ₱2,875.00, so check which one you cite.",
       fill="F2F2F2", color=INK)

# ═════════════════════════════════════════════════════════════ 12 FIG 4.2 / 4.3
item("Figures 4.2 and 4.3: feature representation",
     "Page 11, the paragraphs under 'Figure 4.2. Feature Representation…' and under "
     "'Figure 4.3. Classification Model Architecture…' (the latter continues onto page 12).",
     "Replace both paragraphs. The diagram images also end at 'mel-spectrogram'. Add an "
     "'MFCC' step after it in Figure 4.2, and relabel the input of Figure 4.3 'MFCC input'.",
     "The deployed model computes MFCCs from the mel-scale spectrum; it does not take the "
     "mel-spectrogram image itself.")
paste(
    "Figure 4.2 illustrates the feature representation used in the Resondi respiratory-sound "
    "analysis system. Preprocessed audio is divided into short overlapping frames and "
    "converted to a time–frequency representation using the Short-Time Fourier Transform "
    "(STFT). The spectrum of each frame is passed through a mel-scale filterbank, the "
    "logarithm is taken, and a discrete cosine transform reduces it to a small set of "
    "mel-frequency cepstral coefficients (MFCCs). The coefficients from successive frames form "
    "the fixed-size feature representation provided as the CNN input.",
    heading="Under Figure 4.2")
paste(
    "Figure 4.3 illustrates the classification model architecture used in the Resondi "
    "respiratory-sound analysis system. The process begins with the MFCC input, which "
    "represents the preprocessed respiratory sound as a sequence of cepstral coefficients over "
    "time. The input is passed through the convolutional layers, which extract relevant local "
    "patterns from the coefficients, followed by pooling layers that reduce the feature "
    "dimensions. The extracted features are then processed by the fully connected layers, "
    "where higher-level representations are learned. The softmax layer converts the model's "
    "output into class probabilities, which are then used to determine the predicted "
    "respiratory-sound classification. The system classifies respiratory sounds into four "
    "categories: Normal, Wheezing, Crackles, and Wheezing with Crackles. Overall, the figure "
    "demonstrates the sequence from feature input → feature extraction → dimensionality "
    "reduction → classification → predicted respiratory-sound category.",
    heading="Under Figure 4.3")

FIGS = figs.build_all()

# ═════════════════════════════════════════════════════════════ 13 FIG 4.4
qa = "Recording-quality assessment"
item("Figure 4.4: response time (match Table 5)",
     "Page 12, the bar chart 'Response Time Comparison of System Operations' and the "
     "paragraph beginning 'Figure 4.4 presents the response time comparison…'",
     "Replace the image with the one below, then replace the paragraph.",
     "Table 5 is authoritative. The current figure and text give 1.24, 15.32, 3.18, 2.67 and "
     "1.05 seconds, and every one of them contradicts Table 5. The text also omits the "
     "connection step and names recording as the slowest operation, when quality assessment "
     "takes almost ten times as long.")
image(FIGS["4.4"], "Figure 4.4 Response Time of System Operations")
paste(
    "Figure 4.4 presents the mean response time of each system operation, with standard "
    f"deviations, as recorded in Table 5. Recording-quality assessment required the longest "
    f"time at {R[qa]:.2f} seconds (SD {SD[qa]:.2f}), followed by signal preprocessing at "
    f"{R['Signal preprocessing']:.2f} seconds (SD {SD['Signal preprocessing']:.2f}), sound "
    f"recording at {R['Sound recording']:.2f} seconds (SD {SD['Sound recording']:.2f}), "
    f"smart-stethoscope connection at {R['Smart-stethoscope connection']:.2f} seconds "
    f"(SD {SD['Smart-stethoscope connection']:.2f}), and classification output at "
    f"{R['Classification output']:.2f} seconds (SD {SD['Classification output']:.2f}). "
    f"Recording-quality assessment accounts for about {QA_SHARE:.0%} of the "
    f"{TOTAL_TIME:.0f} seconds from connection to result and is the main constraint on "
    "usability. The fixed recording duration accounts for the zero standard deviation of "
    "sound recording.")

# ═════════════════════════════════════════════════════════════ 14 FIG 4.6
item("Figure 4.6: classification agreement (remove McNemar)",
     "Page 12, the graphic 'Classification Agreement Summary' (it shows 'McNemar's "
     "p = 1.000' and carries a stray 'Figure 4.4' label inside the image), and the paragraph "
     "beginning 'Figure 4.6 presents the classification agreement…'",
     "Replace the image with the one below, then replace the paragraph.",
     "McNemar's test asks whether two methods err in the same direction, not whether a "
     "classifier is accurate, and at n = 15 it cannot detect anything. Its p = 1.000 was read "
     "as the two methods being 'statistically equivalent', which the test cannot show. The "
     "right comparison is agreement against chance.")
image(FIGS["4.6"], "Figure 4.6 Classification Agreement Against Reference Labels")
paste(
    "Figure 4.6 presents the agreement between the classifications produced by the Resondi "
    f"model and the reference labels for the same recordings. Of the {N} recordings "
    f"evaluated, {K} produced matching classifications, an agreement of {K / N:.0%} with a 95% "
    f"Wilson score interval of {LO:.1%} to {HI:.1%}. The interval contains both the "
    f"{CHANCE:.0%} agreement expected by chance across four categories and the level of a "
    "usefully performing classifier, and an exact binomial test against chance returned "
    f"p = {P_CHANCE:.3f}; {K_NEEDED} of the {N} recordings would have needed to agree to "
    "reach significance at the 0.05 level. The result therefore does not establish that the "
    f"model classifies device recordings better than chance, and {N} recordings are too few "
    "to support a conclusion about accuracy in either direction. This figure measures the "
    "classifier's accuracy on device recordings; it is not a comparison between recording "
    "devices.")

# ═════════════════════════════════════════════════════════════ 15 FIG 4.7
item("Figure 4.7: signal strength",
     "Pages 12–13, the bar chart 'Signal Strength Comparison' and the paragraph beginning "
     "'Figure 4.7 presents the comparison of signal strength…', which continues onto page "
     "13 and ends '…must also be considered.'",
     "Replace the image with the one below, then replace the whole paragraph.",
     "32.49 vs 7.89 dB is superseded by 45 vs 32 dB. Decibel values cannot be divided to "
     "give 'times stronger'; a 13 dB difference is about 4.5 times the amplitude.")
image(FIGS["4.7"], "Figure 4.7 Signal Strength Comparison")
paste(
    "Figure 4.7 presents the mean signal strength recorded by the Resondi device and by a "
    f"conventional stethoscope under the same conditions. Resondi recorded {DEV} dB and the "
    f"conventional stethoscope {CONV} dB. Because decibels are logarithmic, the "
    f"{DEV - CONV} dB difference corresponds to roughly {AMP_RATIO:.1f} times the amplitude "
    "rather than a ratio of the two values. The device therefore captured a stronger "
    "respiratory sound signal under the tested conditions. Signal strength alone does not "
    "establish better clinical performance, as recording quality and classification accuracy "
    "must also be considered.")

# ═════════════════════════════════════════════════════════════ 16 FIG 4.8
item("Figure 4.8: ambient noise",
     "Page 13, the bar chart 'Noise Resilience by Environment' and the paragraph beginning "
     "'Figure 4.8 presents the measured noise levels…'",
     "Replace the image with the one below, then replace the paragraph.",
     "The superseded values put the hospital ward highest and the community area lowest. The "
     "verified values reverse that order and show how little margin is left in a community "
     "setting.")
image(FIGS["4.8"], "Figure 4.8 Ambient Noise by Recording Environment")
paste(
    "Figure 4.8 presents the ambient noise level measured in each of the three recording "
    f"environments. Noise was lowest in the quiet room at {QR} dB, followed by the hospital "
    f"ward at {HW} dB and the community area at {CA} dB. Against the device's {DEV} dB mean "
    f"signal strength, this leaves a margin of about {DEV - QR} dB in the quiet room, "
    f"{DEV - HW} dB in the hospital ward, and only {DEV - CA} dB in the community area. The "
    "device recorded respiratory sounds in all three settings, but the narrowing margin "
    "indicates that recordings made in community settings are the most vulnerable to noise, "
    "and that noise reduction and quality checking matter most there.")

# ═════════════════════════════════════════════════════════════ 17 TABLE 5 TEXT
item("Table 5 paragraph",
     "Page 14, the paragraph under Table 5 beginning 'Table 5 presents the response time of "
     "the Ausculta system across five system operations.'",
     "Replace the paragraph. Table 5 itself is correct and stays.",
     "The current text names only four of the five operations (it runs 'sound recording' "
     "and 'quality assessment' together) and never states a result.")
paste(
    "Table 5 presents the response time of the Resondi system across five operations: "
    "smart-stethoscope connection, sound recording, recording-quality assessment, signal "
    f"preprocessing, and classification output. Recording-quality assessment took the "
    f"longest, at a mean of {R[qa]:.2f} seconds, and classification output the shortest, at "
    f"{R['Classification output']:.2f} seconds. The same values are shown graphically in "
    "Figure 4.4.")

# ═════════════════════════════════════════════════════════════ 18 TABLE 6 TEXT
item("Table 6 paragraph",
     "Page 14, the paragraph under Table 6 beginning 'Table 6 showed the comparison of the AI "
     "model's classification performance…'",
     "Replace the paragraph. Table 6 itself stays.",
     "With one clean and one noisy recording, the result is a single observation. The "
     "current wording reads as a general finding about noise robustness.")
paste(
    "Table 6 compares the AI model's output for one clean recording and one "
    "noise-contaminated recording. The model classified both as Normal. Both recordings had "
    "the same duration and sampling rate, and the noise-contaminated recording showed a "
    "higher RMS amplitude. With a single pair of recordings this is a descriptive observation "
    "only: it shows that the added noise did not change the output in this instance, and it "
    "does not establish that the model is robust to noise in general.")

# ═════════════════════════════════════════════════════════════ 19 ACCEPTANCE RESULTS
item("End-user acceptance results (new)",
     "Page 14, directly after the Table 6 paragraph and before 'V. CONCLUSIONS'.",
     "Insert the heading, Table 7, and the three paragraphs below.",
     "The paper describes an acceptance evaluation in its abstract and methods but reports "
     "no results anywhere. These are the results of the questionnaire actually "
     "administered.")
rows = [["Construct", "Items", "Mean", "SD", "Verbal Interpretation", "α"]]
for name, items_, mean, sd, alpha in UTAUT:
    rows.append([name, items_, f"{mean:.2f}", f"{sd:.2f}", "Agree", "—" if alpha is None else f"{alpha:.2f}"])
rows.append(["Overall (12 Likert items)", 12, f"{UTAUT_OVERALL:.2f}", "—", "Agree", "—"])
P("End-User Acceptance", size=11, bold=True, font=PAPER_FONT, after=4)
mono_table(rows, [2.1, 0.6, 0.7, 0.6, 1.5, 0.6],
           caption=["Table 7.", f"End-User Acceptance by UTAUT Construct (n = {N_RESP})"],
           note="Note. α = Cronbach's alpha; not computed for a single-item construct. "
                "Interpretation follows Table 1.4.")
paste(
    f"Table 7 presents end-user acceptance among {N_RESP} respondents: 13 patients, 13 general "
    "respondents, and one health practitioner. Across the twelve Likert items, overall "
    f"acceptance was {UTAUT_OVERALL:.2f}, interpreted as Agree. Performance expectancy and "
    "effort expectancy each averaged 4.09, facilitating conditions 3.84, and social influence "
    "3.63, all interpreted as Agree. Internal consistency was acceptable for effort expectancy "
    "(α = 0.76) but fell below the conventional 0.70 threshold for facilitating conditions "
    "(α = 0.59) and performance expectancy (α = 0.51). With three to five items per construct "
    f"and {N_RESP} respondents, the constructs are reported descriptively rather than as "
    "validated scales.",
    f"Twenty-one of {N_RESP} respondents (78%) indicated that peers or colleagues encourage "
    "use of the device, and 20 (74%) that their institution provides resources to use it. "
    "Access to training and technical support was the least certain: 12 (44%) answered "
    "maybe, 8 (30%) yes, and 7 (26%) no. Eleven respondents (41%) reported prior experience "
    "with medical devices or health applications.",
    "These results carry four limitations. Only one health practitioner responded, so items "
    "on institutional resources and professional practice were largely answered by "
    "respondents to whom they do not apply. Five of the twelve Likert items ask about "
    "conformity with ISO standards that the device has not yet achieved. Three "
    "behavioral-intention items and all open-ended items returned no responses. The response "
    "options also contained inconsistent spellings of 'Strongly Agree', which were treated as "
    "the same response.")

# ═════════════════════════════════════════════════════════════ 20 CONCLUSIONS
item("Conclusions",
     "Pages 14–15, everything under 'V. CONCLUSIONS' up to the heading 'VI. "
     "ACKNOWLEDGMENT'.",
     "Delete all of it and paste the four paragraphs below.",
     "The section is pasted two and a half times in a row (it restarts at 'Ausculta "
     "demonstrates a structured and integrated approach…' twice). It also repeats six "
     "locations and the mel-spectrogram, and it does not state a single result.")
paste(
    "Resondi demonstrates a structured and integrated approach to respiratory-sound "
    "monitoring through the combination of standardized auscultation, digital recording, "
    "wireless communication, and AI-assisted sound analysis. The system records at seven "
    "standardized sites, six lung fields and a tracheal reference, and checks recording "
    "quality to promote consistent and comparable respiratory-sound acquisition.",
    "The integration of the microphone, preamplifier, ESP32 microcontroller, and Bluetooth "
    "Low Energy provides the technical framework for capturing and transmitting respiratory "
    f"sounds. The device produced a signal {DEV - CONV} dB stronger than a conventional "
    f"stethoscope, {CLARITY[0]}% of its recordings were rated good in clarity, and it recorded "
    f"in settings with ambient noise between {QR} and {CA} dB. Its processing pipeline "
    "applies noise reduction, filtering, segmentation, MFCC feature extraction, and CNN-based "
    "classification of normal, wheeze, crackle, and combined wheeze-and-crackle patterns.",
    "Classification accuracy has not been established. Agreement with reference labels on "
    f"{N} device recordings was {K / N:.0%}, which did not differ significantly from chance, "
    "and scores obtained on the reference dataset were not independent of the training data. "
    f"Recording-quality assessment, at a mean of about {R[qa] / 60:.1f} minutes, is the main "
    f"constraint on response time. End-user acceptance was favorable, at {UTAUT_OVERALL:.2f} "
    f"of 5 among {N_RESP} respondents, though the respondents were largely not health "
    "practitioners.",
    "Overall, the findings support the feasibility of the proposed Resondi architecture as a "
    "framework for standardized respiratory-sound recording, longitudinal monitoring, and "
    "professional review. Retraining on a patient-separated dataset, faster quality "
    "assessment, and prospective clinical validation are necessary before the system's "
    "effectiveness and reliability in healthcare settings can be determined. Resondi is "
    "consequently positioned as a supportive respiratory-monitoring system that assists "
    "professional assessment, rather than as a replacement for professional clinical "
    "evaluation.")

# ═════════════════════════════════════════════════════════════ 21 REFERENCE
item("Reference to add",
     "Page 15 onward, 'VII. REFERENCES', in alphabetical position (after the V entries, or "
     "at the end if there are none).",
     "Insert the entry below.",
     "Items 3 and 8 now cite UTAUT. The reference list does not include it yet.")
paste("Venkatesh, V., Morris, M. G., Davis, G. B., & Davis, F. D. (2003). User acceptance of "
      "information technology: Toward a unified view. MIS Quarterly, 27(3), 425–478. "
      "https://doi.org/10.2307/30036540")

# ═════════════════════════════════════════════════════════════ CHECKLIST
item("Device concept render (new figure)",
     "Section describing the device, after the sentence added for Table 4 (item 11).",
     "Insert the image below with its caption. Number it to fit your figure order.",
     "It shows the version 2.0 design at a glance. The caption says it is a concept render, "
     "because the model's proportions differ from the real 173 × 80 × 70 mm enclosure and no "
     "result in the paper came from this build.")
image(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "figures", "Resondi-Device-3D.png"),
      "Concept render of the Resondi version 2.0 enclosure")
paste("Concept render of the Resondi version 2.0 enclosure, from the team's Blender model. "
      "Proportions and colours are illustrative. No result in this study was obtained on this build.",
      heading="Caption")

doc.add_page_break()
P("Checklist", size=13, bold=True, color=PRIMARY, after=4)
rows = [["#", "Item", "Where", "Done"]]
for i, (title, where, _) in enumerate(ITEMS, 1):
    m = re.match(r"(Pages? [\d–]+|Whole paper)", where)
    rows.append([i, title, m.group(1) if m else where, ""])
mono_table(rows, [0.35, 2.6, 3.1, 0.55])

P("Not covered by this pack", size=12, bold=True, color=PRIMARY, before=6, after=3)
for line in (
    "The clarity denominator. 68 / 25 / 7% is of an unstated number of recordings, and it "
    "cannot be derived from the percentages. Add the count if your rating sheets have it.",
    "Who rated clarity, how many raters, and whether they were blinded. These are open "
    "questions (IMRaD TO FILL #8 and #9). The pack does not invent answers.",
    "Ethics approval. The paper describes physician supervision, which is not the same as "
    "ethics-committee approval (IMRaD TO FILL #12).",
    "The Introduction's description of patients practising independently at home. The "
    "concept note has since dropped home self-recording; decide whether the paper should "
    "follow.",
    "Retrained model results. Once the patient-separated dataset has been trained, item 7 "
    "and the Conclusions will need the new accuracy, confusion matrix and per-class recall.",
):
    P("•  " + line, after=3)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
doc.save(OUT)
print("wrote", os.path.normpath(OUT), "|", len(ITEMS), "items")
