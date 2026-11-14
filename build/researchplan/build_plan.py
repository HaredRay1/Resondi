"""Revise the Resondi research plan (copy of the user's Drive file) to match what was actually built.

Run: python build/researchplan/build_plan.py   (after figures.py)
In : research-plan/original/Resondi-Research-Plan-Revised.docx   (untouched Drive download)
Out: research-plan/Resondi-Research-Plan-Revised-Heart-and-Lung-2026-11-13.docx
     research-plan/Resondi-Research-Plan-Revision-Log-Heart-and-Lung-2026-11-13.docx
Text in [[double brackets]] is written with a yellow highlight: facts only the team can confirm.
Results and Discussion read their numbers from model-rebuild/results/stats/ (stats-results.json from
analysis_stats.py; fusion-comparison.json from fusion_eval.py), so run those scripts first.
"""
import copy
import os
import re

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt
from docx.text.paragraph import Paragraph

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
RP = os.path.join(ROOT, "research-plan")
SRC = os.path.join(RP, "original", "Resondi-Research-Plan-Revised.docx")
OUT = os.path.join(RP, "Resondi-Research-Plan-Revised-Heart-and-Lung-2026-11-13.docx")
LOGF = os.path.join(RP, "Resondi-Research-Plan-Revision-Log-Heart-and-Lung-2026-11-13.docx")
FIG = os.path.join(ROOT, "figures")
RFIG = os.path.join(RP, "figures")

D = docx.Document(SRC)
P = list(D.paragraphs)          # indices below refer to the ORIGINAL document
LOG = []
MARK = re.compile(r"\[\[(.*?)\]\]", re.S)


def log(section, was, now, why):
    LOG.append((section, was, now, why))


def write_runs(p, text, rPr=None, size=None, bold=None, italic=None):
    for k, part in enumerate(MARK.split(text)):
        if not part:
            continue
        r = p.add_run(part)
        if rPr is not None:
            r._r.insert(0, copy.deepcopy(rPr))
        if k % 2 == 1:
            r.font.highlight_color = WD_COLOR_INDEX.YELLOW
        if size:
            r.font.size = Pt(size)
        if bold is not None:
            r.bold = bold
        if italic is not None:
            r.italic = italic
    return p


def first_rPr(p):
    for r in p.runs:
        if r._r.rPr is not None and r.text.strip():
            return r._r.rPr
    return None


def set_text(p, text):
    rPr = first_rPr(p)
    rPr = copy.deepcopy(rPr) if rPr is not None else None
    for el in list(p._p):
        if el.tag in (qn("w:r"), qn("w:hyperlink")):
            p._p.remove(el)
    write_runs(p, text, rPr)


def replace(p, old, new):
    """Replace inside one paragraph; keep run formatting when the text sits in one run."""
    if old not in p.text:
        raise SystemExit(f"PATTERN MISSING in paragraph: {old!r}\n  in: {p.text[:120]!r}")
    for r in p.runs:
        if old in r.text:
            r.text = r.text.replace(old, new)
            return
    set_text(p, p.text.replace(old, new))


def new_para(after_el, text, template, align=None, bold=None, italic=None, size=None, keep_next=False, keep_num=False):
    el = copy.deepcopy(template._p)
    for ch in list(el):
        if ch.tag != qn("w:pPr"):
            el.remove(ch)
    pPr = el.find(qn("w:pPr"))
    if pPr is not None:
        for t in ("w:sectPr",) if keep_num else ("w:sectPr", "w:numPr"):
            s = pPr.find(qn(t))
            if s is not None:
                pPr.remove(s)
    after_el.addnext(el)
    p = Paragraph(el, template._parent)
    write_runs(p, text, first_rPr(template), size=size, bold=bold, italic=italic)
    if align is not None:
        p.alignment = align
    if keep_next:
        p.paragraph_format.keep_with_next = True
    return p


def caption(after_el, label, title, template):
    """APA 7: bold label line, italic title line, both above the table or figure."""
    a = new_para(after_el, label, template, align=WD_ALIGN_PARAGRAPH.LEFT, bold=True, keep_next=True)
    a.paragraph_format.space_before = Pt(10)
    a.paragraph_format.space_after = Pt(0)
    a.paragraph_format.first_line_indent = Inches(0)
    b = new_para(a._p, title, template, align=WD_ALIGN_PARAGRAPH.LEFT, italic=True, keep_next=True)
    b.paragraph_format.space_after = Pt(4)
    b.paragraph_format.first_line_indent = Inches(0)
    return b


def note(after_el, text, template):
    p = new_para(after_el, "", template, align=WD_ALIGN_PARAGRAPH.LEFT, size=9.5)
    r = p.add_run("Note. ")
    r.italic = True
    r.font.size = Pt(9.5)
    write_runs(p, text, size=9.5)
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.space_after = Pt(10)
    return p


def table(after_el, rows, widths=None, bold_last=False):
    t = D.add_table(rows=len(rows), cols=len(rows[0]))
    after_el.addnext(t._tbl)
    tblPr = t._tbl.tblPr
    tblPr.append(parse_xml(
        f'<w:tblBorders {nsdecls("w")}><w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/></w:tblBorders>'))
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j)
            para = c.paragraphs[0]
            write_runs(para, str(val), size=9.5, bold=True if (i == 0 or (bold_last and i == len(rows) - 1)) else None)
            for r in para.runs:
                r.font.name = "Times New Roman"
            pf = para.paragraph_format
            pf.space_before, pf.space_after, pf.first_line_indent = Pt(1), Pt(1), Inches(0)
            pf.line_spacing = 1.0
            if i == 0:
                c._tc.get_or_add_tcPr().append(parse_xml(
                    f'<w:tcBorders {nsdecls("w")}><w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/></w:tcBorders>'))
            if bold_last and i == len(rows) - 1:
                c._tc.get_or_add_tcPr().append(parse_xml(
                    f'<w:tcBorders {nsdecls("w")}><w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/></w:tcBorders>'))
            if widths:
                c.width = Inches(widths[j])
    return t


def figure(after_el, path, width, template):
    p = new_para(after_el, "", template, align=WD_ALIGN_PARAGRAPH.CENTER, keep_next=True)
    p.paragraph_format.first_line_indent = Inches(0)
    p.add_run().add_picture(path, width=Inches(width))
    return p


BODY = P[97]       # body paragraph template (procedures)
DBODY = P[163]     # body paragraph template (data analysis)

# ======================================================================= RATIONALE
old9 = "(Philippine Statistics Authority [PSA], 2026)"
set_text(P[9], P[9].text
         .replace("led all causes at 19.1 percent, and pneumonia ranked fourth at 6.7 percent " + old9,
                  "led all causes at 19.1 percent (134,074 deaths), and pneumonia ranked fourth at 6.7 percent "
                  "(47,260 deaths); together the two accounted for 181,334 deaths, or 25.8 percent of the total "
                  "(Philippine Statistics Authority [PSA], 2025b)"))
log("Rationale ¶1", "…19.1 percent, … 6.7 percent (PSA, 2026)",
    "Adds the death counts (134,074; 47,260; together 181,334 = 25.8%) and cites PSA 2025b",
    "The citation year did not match the bibliography (both PSA entries are 2025). Counts make the percentages checkable.")

set_text(P[12],
         "This study will develop and evaluate Resondi, a low-cost, Internet of Things (IoT)-based, AI-assisted smart "
         "stethoscope and cardiopulmonary monitoring platform. Separate Lung and Heart modes will guide the user through "
         "standardized anatomical sites (seven lung sites and five cardiac sites), store each recording by site on a microSD "
         "card, and classify lung sounds into four acoustic patterns (Healthy, Crackles, Wheezing, and Wheezing with "
         "Crackles) with a convolutional neural network. The device's bill of materials is ₱2,775, about one-eighth of the "
         "listed price of the Littmann CORE. Every AI-assisted result will be presented to a licensed practitioner, who may "
         "confirm, modify, or return it for a repeat recording. Heart sounds will be captured and filed for review, and "
         "the heart-sound timing, heart-rate and murmur models already in the application will be tested on the device. Resondi is intended as a decision-support instrument rather than a "
         "diagnostic one, making an examination retrievable and comparable between visits.")
log("Rationale ¶4", "This study developed and evaluated Resondi, a low-cost, IOT-based …",
    "Future tense; seven lung and five cardiac sites; the four output classes; BOM ₱2,775 against ₱22,000",
    "A research plan is written in the future tense. Site count and classes now match the device and the model; the cost figure supports the low-cost claim with a number.")

# ======================================================================= RESEARCH QUESTIONS
for i in (16, 17, 18):
    replace(P[i], "Ausculta", "Resondi")
log("Research questions 2–4", "the Ausculta Smart Stethoscope / Platform / analysis system", "Resondi …",
    "The project was renamed Resondi; the old name remained in three questions.")
replace(P[19], "Smart-stethoscope connection", "Smart-stethoscope Wi-Fi connection")
log("Research question 5", "Smart-stethoscope connection", "Smart-stethoscope Wi-Fi connection",
    "The device connects over its own Wi-Fi access point, not Bluetooth.")

# ======================================================================= GOALS
replace(P[45], "establish BLE and MicroSD communication", "establish Wi-Fi access-point and microSD communication")
replace(P[45], "implement a multi-branch CNN feature-fusion model based on the selected reference architecture",
        "implement a multi-branch CNN feature-fusion model based on the selected reference architecture (Tariq et al., "
        "2022) and compare it with a single-branch MFCC baseline, using per-cycle sound labels and patient-wise data "
        "partitioning")
log("Goals", "establish BLE and MicroSD communication; implement a multi-branch CNN feature-fusion model…",
    "Wi-Fi access point and microSD; fusion compared with an MFCC baseline under patient-wise partitioning; reference article named",
    "The device has no Bluetooth. A fusion model is only meaningful against a baseline, and the honest split is part of the method.")

# ======================================================================= MATERIALS
replace(P[55], "TinkerCAD for the 3D model", "TinkerCAD for the casing model and Blender for 3D renders")
replace(P[55], "Python with Edge-Impulse for respiratory-sound preprocessing and AI model development",
        "Python (NumPy, SciPy, librosa, and PyTorch) and Edge Impulse for respiratory-sound preprocessing, AI model "
        "development, and WebAssembly deployment")
replace(P[55], "BLE/API integration will provide the communication layer",
        "The device's own Wi-Fi access point and local web interface, together with microSD file transfer, will provide "
        "the communication layer")
log("Materials ¶1", "TinkerCAD …; Python with Edge-Impulse …; BLE/API integration will provide the communication layer",
    "Adds Blender and the Python libraries actually used; Wi-Fi access point and microSD as the communication layer",
    "Matches the tools used and the device's real connectivity.")

set_text(P[56],
         "For the physical device, the materials will include an acoustic stethoscope chest piece; an INMP441 digital MEMS "
         "microphone connected over the I²S interface, which delivers 16-bit samples directly so that no separate "
         "preamplifier is needed; an ESP32 microcontroller (240 MHz, with built-in 2.4 GHz Wi-Fi); a 32 GB microSD card "
         "for storage; a 10,000 mAh rechargeable lithium-ion battery with charging and protection circuitry; a 20 × 4 I²C "
         "liquid-crystal display; two push buttons; status LEDs; silicone; connecting wires; and resistors. The casing "
         "will be 3D printed in PLA filament by fused deposition modelling. The specification is summarized in Table 1, "
         "the hardware architecture in Figure 1, and the device design in Figure 2.")
log("Materials ¶2", "MEMS microphone, microphone preamplifier module, … BLE-capable communication, … LED display … silicon",
    "INMP441 on I²S (no preamplifier), ESP32 with Wi-Fi, 32 GB microSD, 10,000 mAh battery, 20 × 4 LCD, two buttons, silicone",
    "The VER 2.0 device has a digital I²S microphone, no preamplifier, no Bluetooth and an LCD. 'Silicon' corrected to 'silicone'.")

c = caption(P[56]._p, "Table 1", "Specification of the Resondi Smart Stethoscope (VER 2.0)", BODY)
t1 = table(c._p, [
    ["Component", "Specification"],
    ["Microcontroller", "ESP32, 240 MHz, built-in 2.4 GHz Wi-Fi"],
    ["Microphone", "INMP441 digital MEMS microphone, I²S interface (no analogue preamplifier)"],
    ["Recording format", "16 kHz, 16-bit, mono WAV; 15 s per recording (about 480 kB)"],
    ["Storage", "32 GB microSD card"],
    ["Display and controls", "20 × 4 I²C LCD; two push buttons; status LEDs"],
    ["Connectivity", "Own Wi-Fi access point (RESONDI_WIFI); local web interface at http://192.168.4.1; works without internet"],
    ["Power", "10,000 mAh rechargeable lithium-ion battery with charging and protection circuit"],
    ["Enclosure", "PLA, fused deposition modelling; 173 × 80 × 70 mm"],
    ["Cost", "Bill of materials ₱2,775; fully loaded unit cost ₱4,000"],
], widths=[1.6, 4.6])
n = note(t1._tbl, "Values are from the VER 2.0 specification sheet and bill of materials.", BODY)
c = caption(n._p, "Figure 1", "Hardware Architecture of the Resondi Smart Stethoscope", BODY)
f = figure(c._p, os.path.join(FIG, "Resondi-Hardware-Block-VER2.png"), 6.0, BODY)
n = note(f._p, "Recordings cross from the device to the platform on the microSD card; the automatic gateway between "
         "them is not yet built.", BODY)
c = caption(n._p, "Figure 2", "Concept Render of the Resondi Smart Stethoscope", BODY)
f = figure(c._p, os.path.join(FIG, "Resondi-Device-3D.png"), 5.2, BODY)
note(f._p, "Rendered from the team's 3D model, which measures about 160 × 100 × 60 mm; the fabricated enclosure "
     "measures 173 × 80 × 70 mm.", BODY)
log("Materials (new)", "—", "Table 1 (device specification), Figure 1 (hardware block diagram), Figure 2 (device render)",
    "Gives the specification research question a concrete reference and replaces prose-only description.")

# ======================================================================= PROCEDURES (flow list)
replace(P[75], "BLE and MicroSD", "Wi-Fi and MicroSD")
log("Procedures flow", "Smart-Stethoscope BLE and MicroSD Integration", "Smart-Stethoscope Wi-Fi and MicroSD Integration",
    "No Bluetooth on the device.")

# ======================================================================= REFERENCE DATASETS
set_text(P[97],
         "The ICBHI 2017 Respiratory Sound Database (Rocha et al., 2019) will be used as the primary public reference "
         "dataset for lung-sound training, validation, and testing. It contains 920 recordings from 126 patients, made "
         "with four different stethoscopes and microphones, in which experts annotated the onset and offset of 6,898 "
         "respiratory cycles together with the presence of crackles and wheezes. Each respiratory cycle will be labelled "
         "from these annotations into one of four sound classes (Table 2). Patient-level diagnoses will not be used as "
         "training labels, because a diagnosis does not describe the sound of every breath, and a model trained on them "
         "learns to recognize patients rather than sounds. The SJTU Paediatric Respiratory Sound Database, SPRSound "
         "(Zhang et al., 2022; CC BY 4.0), which annotates individual breathing events in Chinese children, will be "
         "evaluated as additional training data, mapped to the same four classes; its rhonchi and stridor events have no "
         "ICBHI counterpart and will be excluded. For the cardiac component, the CirCor DigiScope Phonocardiogram Dataset "
         "(Oliveira et al., 2022), available through PhysioNet under the Open Data Commons Attribution licence, will be "
         "used. Its public release contains 3,163 recordings from 942 patients, each patient labelled murmur Present, "
         "Absent, or Unknown (Table 3). A blinded set of 25 CirCor recordings, five from each murmur category, will be "
         "reviewed independently by a cardiologist to confirm the reference labels. Reference labels will be stored "
         "separately from AI predictions. The selected CNN-fusion methodology is adapted from the reference article "
         "(Tariq et al., 2022), which classified ICBHI recordings by diagnosis from spectrogram, MFCC, and chromagram "
         "images using a fusion of three CNN architectures; this study fuses the three representations in separate CNN "
         "branches.")
log("Reference datasets", "ICBHI … will be used …; a heart-sound reference dataset … such as the CirCor DigiScope …",
    "Dataset sizes; per-cycle sound labels instead of diagnoses; SPRSound as additional training data; CirCor public release (3,163 recordings, 942 patients); blinded 25-recording cardiologist review; reference article named",
    "The plan gave no sizes. Diagnosis labels were the cause of the original model's inflated scores. CirCor's public release is smaller than the full dataset often quoted (5,282 recordings, 1,568 patients).")

c = caption(P[97]._p, "Table 2", "Respiratory-Cycle Labels Derived From the ICBHI 2017 Annotations", BODY)
t2 = table(c._p, [
    ["Crackles annotated", "Wheezes annotated", "Class", "Cycles", "Share"],
    ["No", "No", "Healthy", "3,642", "52.8%"],
    ["Yes", "No", "Crackles", "1,864", "27.0%"],
    ["No", "Yes", "Wheezing", "886", "12.8%"],
    ["Yes", "Yes", "Wheezing with Crackles", "506", "7.3%"],
    ["", "", "Total", "6,898", "100.0%"],
], widths=[1.3, 1.3, 1.9, 0.9, 0.8], bold_last=True)
n = note(t2._tbl, "The model outputs the classes in alphabetical order (Crackles, Healthy, Wheezing, Wheezing with "
         "Crackles), as Edge Impulse does. Because Healthy is 52.8 percent of cycles, a model that always predicts it "
         "would reach 52.8 percent accuracy while detecting nothing; chance across four balanced classes is 25 percent.", BODY)
c = caption(n._p, "Table 3", "CirCor DigiScope Public Release Used for the Cardiac Component", BODY)
t3 = table(c._p, [
    ["Characteristic", "Value"],
    ["Patients", "942"],
    ["Recordings", "3,163"],
    ["Murmur label (patients)", "Absent 695 (73.8%) · Present 179 (19.0%) · Unknown 68 (7.2%)"],
    ["Recordings by location", "Mitral 861 · Aortic 800 · Pulmonary 766 · Tricuspid 732 · other 4"],
    ["Blinded cardiologist review set", "25 recordings: 5 each of no murmur, holosystolic, early-systolic, mid-systolic, and diastolic"],
], widths=[2.2, 4.0])
note(t3._tbl, "Counts are from the version 1.0.3 public training set. Erb's point, recorded by Resondi as a fifth cardiac "
     "site, has no counterpart in the dataset.", BODY)
log("Reference datasets (new)", "—", "Table 2 (label derivation and class counts), Table 3 (CirCor summary)",
    "States the class imbalance and the baselines that every accuracy figure must be read against.")

# ======================================================================= DEVICE BUILD
replace(P[105], "microcontroller, microphone, preamplifier, communication/storage components, battery, and other electronic parts",
        "microcontroller, digital MEMS microphone, microSD storage module, LCD, push buttons, battery, and other electronic parts")
log("Components and requirements", "…microphone, preamplifier, communication/storage components…",
    "…digital MEMS microphone, microSD storage module, LCD, push buttons…", "No preamplifier in the VER 2.0 device.")
set_text(P[108], P[108].text.rstrip() + " The enclosure will be printed in PLA by fused deposition modelling and will "
         "measure 173 × 80 × 70 mm.")
log("Fabrication", "(no dimensions)", "Adds PLA, FDM and 173 × 80 × 70 mm", "Matches the specification sheet.")
set_text(P[111],
         "The INMP441 digital MEMS microphone will be connected to the ESP32 through the I²S interface, which delivers "
         "16-bit samples directly and removes the need for an analogue preamplifier. A 20 × 4 I²C liquid-crystal display "
         "will show device status and recording prompts, and two push buttons will start and confirm recordings. The "
         "rechargeable battery will use an appropriate charging and protection circuit.")
log("System integration", "The microphone and preamplifier will be connected… Where included, the OLED display…",
    "INMP441 over I²S, no preamplifier; 20 × 4 LCD and two push buttons", "The OLED was replaced by a 20 × 4 LCD in VER 2.0.")
set_text(P[114],
         "The ESP32 smart stethoscope will raise its own 2.4 GHz Wi-Fi access point (RESONDI_WIFI) and serve a local web "
         "interface at http://192.168.4.1, so that a phone or laptop can start, label, and review recordings without "
         "installing an application or needing internet access. Recordings will be saved as 16 kHz, 16-bit, mono WAV files "
         "of 15 seconds (about 480 kB each). Automatic transfer from the device to the cloud platform (the gateway) is not "
         "part of the current build; until it is implemented, the platform will identify file transfer as manual rather "
         "than represent it as automatic.")
log("Device integration", "The ESP32 smart stethoscope will communicate with the application through BLE…",
    "Own Wi-Fi access point and local web interface; recording format; the gateway stated as not yet built",
    "The device has no Bluetooth. Stating the missing gateway keeps the plan honest about the current architecture.")
set_text(P[115],
         "In addition, the device stores every recording on its microSD card for offline use. The user can remove the "
         "card, transfer the audio files to a phone or computer, and select which recordings to upload to the platform. "
         "Uploaded recordings will be classified by the platform's AI model into the four sound patterns, and a severity "
         "score of abnormal-sound activity will be computed (see Data Analysis); the platform will not assess the "
         "severity of any lung condition.")
log("MicroSD integration", "…processed by the app's AI algorithm … to assess the severity of lung conditions.",
    "…classified into the four sound patterns; severity score of abnormal-sound activity only",
    "The model describes sounds; assessing the severity of a condition would be a diagnostic claim the plan elsewhere rules out.")
replace(P[118], "through a BLE/API integration layer", "through a Wi-Fi and file-upload integration layer")
replace(P[118], "BLE firmware", "device firmware")
set_text(P[118], P[118].text.rstrip() + " The trained classification model will be exported from Edge Impulse as a "
         "WebAssembly library and run in the browser, so no recording has to leave the platform for inference.")
log("Platform development", "BLE/API integration layer; BLE firmware", "Wi-Fi and file-upload integration layer; model runs in the browser as WebAssembly",
    "Matches the device and the deployed classifier.")

# ======================================================================= GUIDED AUSCULTATION
set_text(P[123],
         "In Lung Mode, the platform will guide recordings from seven standard sites (Figure 3): the trachea; the right and "
         "left upper anterior chest at the midclavicular line; the right and left lateral chest at the mid-axillary line; "
         "and the right and left lower posterior chest at the level of T8 to T10. In Heart Mode, it will guide recordings "
         "from five cardiac sites: the aortic, pulmonic, tricuspid, and mitral points and Erb's point. The user selects a "
         "site, places the stethoscope, confirms, records, and saves the audio with its metadata. Repeat recordings are "
         "allowed when needed. To support accurate placement, the platform will provide an instructional diagram "
         "highlighting each site, and a device manual will give step-by-step instructions on stethoscope positioning, "
         "the recording workflow, and practices for reproducibility.")
log("Guided auscultation", "right upper, left upper, right middle, left middle, right lower, and left lower (six sites)",
    "Seven lung sites (trachea + six) and five cardiac sites, with Figure 3",
    "The protocol and the device use seven lung sites; the left lung has no middle lobe. Heart Mode sites were missing.")
c = caption(P[123]._p, "Figure 3", "Lung Mode Auscultation Sites and Recording Order", BODY)
f = figure(c._p, os.path.join(FIG, "d2_seven_sites.png"), 5.6, BODY)
note(f._p, "Tc = trachea. Sites 1 and 2: upper anterior, midclavicular line; sites 3 and 4: lateral, mid-axillary line; "
     "sites 5 and 6: lower posterior, T8 to T10.", BODY)

# ======================================================================= PREPROCESSING AND MODEL
set_text(P[129],
         "Reference recordings and eligible device recordings will be resampled to 16 kHz mono, scaled to the 16-bit "
         "integer range, and cut into 1-second windows (16,000 samples) inside each annotated respiratory cycle, with a "
         "0.5-second stride for training and non-overlapping windows for evaluation. The 1-second window matches the "
         "input of the deployed model. Each window will be converted into three feature representations (Table 4): "
         "Mel-frequency cepstral coefficients (MFCC), a log-power spectrogram, and a chromagram, the three representations "
         "used in the reference study (Tariq et al., 2022). The reference study fused three separately trained CNN "
         "architectures (FDC-1, FDC-2, and FDC-3) into one network (FDC-FS) and applied it to one representation at a time. "
         "This study adapts that idea to fuse the representations themselves: each representation will feed its own CNN "
         "branch, and the branch outputs will be concatenated and passed to a dense layer with a softmax output over four "
         "classes: Crackles, Healthy, "
         "Wheezing, and Wheezing with Crackles (Figure 4). Window scores within a cycle will be averaged to give one "
         "classification per cycle. A single-branch MFCC network, the design of the deployed model, will serve as the "
         "baseline, and the average of the three single-branch models' probabilities (late fusion) will be compared as "
         "well, so that any gain can be attributed to fusion itself. Additional categories such as other/abnormal, "
         "uncertain, and insufficient quality may be used at the platform level. The model will not be used to "
         "independently diagnose specific diseases.")
log("Preprocessing and CNN development", "…conversion into Mel-spectrogram representations… A dedicated CNN model will be developed…",
    "1-s windows at 16 kHz; MFCC, spectrogram and chromagram branches (Tariq et al., 2022); MFCC baseline and late fusion as comparisons; Table 4 and Figure 4",
    "The plan described a single Mel-spectrogram CNN, which conflicts with its own fusion research question and with the model being trained.")
c = caption(P[129]._p, "Table 4", "Feature Representations and Network Configuration", BODY)
t4 = table(c._p, [
    ["Item", "Setting"],
    ["Input", "1-s window, 16,000 samples at 16 kHz, 16-bit scale"],
    ["Windowing", "0.5-s stride for training; non-overlapping 1-s windows for evaluation; cut inside annotated cycles"],
    ["MFCC branch", "13 coefficients; 20-ms frames and stride; 32 mel filters; 256-point FFT; pre-emphasis 0.98; "
                    "cepstral mean and variance normalization over 101 frames"],
    ["Spectrogram branch", "Log-power spectrogram, 0–4 kHz, 129 frequency bins, 20-ms frames"],
    ["Chromagram branch", "12 pitch-class bins, 50–4,000 Hz, 64-ms frames"],
    ["Baseline network", "1-D CNN: convolution (32 filters, kernel 3), max pooling, dropout 0.25; convolution (64 filters, "
                         "kernel 3), max pooling, dropout 0.25; dense softmax over 4 classes"],
    ["Fusion network", "One CNN branch per representation; 64 features per branch concatenated (3 × 64); dense layer; "
                       "softmax over 4 classes (about 190,000 parameters)"],
    ["Training", "Adam optimizer, learning rate 0.001; class weighting; early stopping on the validation subset; "
                 "three random seeds (11, 22, 33) per configuration"],
    ["Output", "Crackles, Healthy, Wheezing, Wheezing with Crackles; window scores averaged per respiratory cycle"],
    ["Deployment", "Edge Impulse int8 WebAssembly library loaded by the platform; a fusion model would need an ONNX or "
                   "custom-block route, because Edge Impulse has no chromagram block"],
], widths=[1.6, 4.6])
n = note(t4._tbl, "Settings are those of the training scripts in the project repository (model-rebuild).", BODY)
c = caption(n._p, "Figure 4", "Planned Three-Branch Feature-Fusion Classifier", BODY)
f = figure(c._p, os.path.join(RFIG, "fig4_fusion.png"), 6.2, BODY)
note(f._p, "Adapted from Tariq et al. (2022), who fused three CNN architectures on one representation at a time; here "
     "the three representations are fused. The MFCC branch alone is the baseline against which fusion is judged.", BODY)

# ======================================================================= TESTING
set_text(P[132], P[132].text.rstrip() + " Because the classes are imbalanced, balanced accuracy (the mean of the four "
         "per-class recalls) will be the primary measure, reported against the 25 percent chance level for four classes "
         "and the 52.8 percent majority-class baseline. The test subset will be scored once, for the final selected "
         "model only.")
log("Manual (reference dataset) testing", "Accuracy, precision, sensitivity, specificity, F1-score, and confusion matrix…",
    "Adds balanced accuracy as the primary measure, the 25% and 52.8% baselines, and a single test run",
    "Plain accuracy on ICBHI rewards always predicting Healthy; scoring the test set once prevents choosing a lucky result.")
set_text(P[135], P[135].text.rstrip() + " Because the reference corpus was recorded with four different stethoscopes "
         "and microphones, while Resondi uses a digital MEMS microphone, device results will always be reported "
         "separately from reference results and never pooled with them.")
log("Device unit testing", "(no statement on microphone differences)", "Device results reported separately from reference results",
    "A change of microphone alone can change model performance; pooling would hide it.")

# ======================================================================= DATA ANALYSIS: partitioning
set_text(P[164],
         "All partitioning of data into training, validation, and testing subsets will be performed patient-wise, so that "
         "no patient contributes data to more than one subset. This is necessary because the reference database contains "
         "multiple recordings per patient and multiple cycles per recording; a random split at cycle or recording level "
         "would place the same patient on both sides of the partition and inflate every reported metric. The official "
         "ICBHI 2017 partition will not be used, because it is not balanced by recording device, and a model trained "
         "mostly on one microphone fails on the others. Patients will instead be assigned to training, validation, and "
         "testing subsets in proportions of about 70, 15, and 15 percent of cycles, stratified jointly by sound label and "
         "recording device (seed 20261109), giving 65, 30, and 31 patients respectively (Table 5 and Figure 5). The "
         "validation subset will be used for all model and setting choices; the testing subset will be used once, for the "
         "final model.")
log("Unit of analysis and partitioning", "Where the official ICBHI 2017 training and testing partition is available, it will be adopted directly…",
    "Own patient-wise split stratified by label and device (65/30/31 patients); validation for choices, test used once; Table 5 and Figure 5",
    "The partition actually used differs from the official one, for a stated reason; the plan must describe the partition that produces the reported numbers.")
c = caption(P[164]._p, "Table 5", "Patient-Wise Partition of the ICBHI 2017 Database", DBODY)
t5 = table(c._p, [
    ["Subset", "Patients", "Recordings", "Healthy", "Crackles", "Wheezing", "Wheezing with Crackles", "Cycles"],
    ["Training", "65", "598", "2,536", "1,332", "628", "354", "4,850 (70.3%)"],
    ["Validation", "30", "158", "551", "264", "138", "44", "997 (14.5%)"],
    ["Testing", "31", "164", "555", "268", "120", "108", "1,051 (15.2%)"],
    ["Total", "126", "920", "3,642", "1,864", "886", "506", "6,898"],
], widths=[0.85, 0.65, 0.8, 0.7, 0.75, 0.75, 0.95, 1.05], bold_last=True)
n = note(t5._tbl, "Recordings by device (training / validation / testing): AKG C417L 420 / 107 / 119; Littmann Classic II "
         "SE 58 / 14 / 15; Littmann 3200 42 / 12 / 6; Meditron 78 / 25 / 24.", DBODY)
c = caption(n._p, "Figure 5", "Class Composition of Each Subset", DBODY)
f = figure(c._p, os.path.join(RFIG, "fig5_partition.png"), 6.2, DBODY)
note(f._p, "Bars show the share of respiratory cycles in each class, with cycle counts.", DBODY)

# ======================================================================= DATA ANALYSIS: severity model wording
replace(P[171], "The CNN feature-fusion classification model analyses each respiratory cycle and outputs confidence scores "
        "between 0 and 1 for four classes",
        "The CNN feature-fusion classification model analyses each 1-second window, and its window scores are averaged "
        "within each respiratory cycle to give confidence scores between 0 and 1 for four classes")
log("Severity algorithm", "…analyses each respiratory cycle and outputs confidence scores…",
    "…analyses each 1-second window; scores averaged within each cycle…", "The model operates on 1-s windows, not whole cycles.")

set_text(P[204], P[204].text.rstrip() + " Balanced accuracy and the macro-averaged F1-score will be the primary summary "
         "measures. In the testing subset, 52.8 percent of cycles are Healthy, so accuracy must exceed that figure, and "
         "balanced accuracy must exceed 25 percent, before a model can be said to detect anything.")
log("Classification metrics", "Accuracy will be reported alongside the majority-class baseline…",
    "Balanced accuracy and macro-F1 as primary; the 52.8% and 25% thresholds stated", "Makes the baseline concrete for this partition.")

# ======================================================================= DATA ANALYSIS: analysis map
c = caption(P[221]._p, "Table 6", "Research Questions, Data, and Planned Analyses", DBODY)
table(c._p, [
    ["Research question", "Data", "Analysis"],
    ["1. Recording quality", "Signal strength (dB), clarity ratings, ambient noise (dB) in a quiet room, a ward, and a community setting",
     "Mean, SD; proportion of Good, Acceptable, Poor, and Invalid recordings"],
    ["2–4. Specifications", "Device, platform, and analysis-system documentation", "Descriptive: tables and diagrams"],
    ["5. Response time", "Timed trials of connection, recording, quality check, preprocessing, and classification (s)", "Mean, SD, range"],
    ["6. Clean vs noise-contaminated", "Correct or incorrect classification of the same cycles with and without added noise",
     "McNemar's test (exact when b + c < 25); odds ratio"],
    ["7. Reference vs device", "The same reference audio played back and re-recorded through Resondi",
     "McNemar's test; TOST equivalence on the accuracy difference"],
    ["8. Conventional vs Resondi quality", "Paired recordings at the same site", "Paired t-test or Wilcoxon signed-rank (Shapiro–Wilk); Cohen's d"],
    ["9. Acceptance", "Five-point Likert ratings", "Weighted mean, SD; Cronbach's alpha"],
    ["10. Instructional preferences", "Survey choices", "Frequency and percentage"],
    ["11. Longitudinal support", "Repeated same-site recordings", "Descriptive trends; change counted only beyond the severity RMSE"],
    ["Model performance", "Cycle-level predictions for the 31 test patients",
     "Balanced accuracy, macro-F1, per-class sensitivity and specificity, Cohen's kappa, confusion matrix, ICBHI score; "
     "95% patient-level bootstrap CI (1,000 resamples)"],
], widths=[1.6, 2.4, 2.3])
log("Tests of difference (new)", "—", "Table 6: each research question mapped to its data and test",
    "Lets a reader check that every question has a matching analysis.")

# ======================================================================= CARDIAC, HARDWARE, SOFTWARE
set_text(P[245], P[245].text.rstrip() + " Erb's point, which Resondi records as a fifth cardiac site, has no counterpart "
         "in the dataset, so its recordings will be reported separately.")
log("Heart-sound reference labels", "(four locations only)", "Erb's point reported separately", "The device records five cardiac sites.")
replace(P[263], "MEMS microphone, and preamplifier", "INMP441 digital MEMS microphone, and the ESP32's I²S input")
log("Hardware frequency response", "…MEMS microphone, and preamplifier", "…INMP441 digital MEMS microphone, and the ESP32's I²S input",
    "There is no preamplifier in the acquisition chain.")
set_text(P[270],
         "Signal processing, feature extraction, and model training will be performed in Python 3 using NumPy, SciPy, "
         "librosa, and PyTorch, and in Edge Impulse, whose trained models will be exported as WebAssembly libraries and "
         "checked in Node.js against the Python results before deployment. Inferential statistics will be computed in "
         "jamovi and cross-checked in Python using statsmodels and pingouin. Random seeds will be fixed and recorded for "
         "every partitioning, augmentation, and resampling operation (partition seed 20261109; training seeds 11, 22, and "
         "33), and every evaluation of the test subset will be logged, so that the analysis is reproducible and no "
         "favourable run can be selected after the fact. The analysis scripts, together with the fitted coefficients of "
         "the severity algorithm, will be deposited in the project repository.")
log("Software and reproducibility", "NumPy, SciPy, librosa, scikit-learn, and TensorFlow…",
    "PyTorch and Edge Impulse (WebAssembly, checked in Node.js); the actual seeds; every test run logged", "Matches the software actually used.")

# ======================================================================= OLD NAME
n_old = 0
for p in P[:274]:
    if re.search(r"\bAusculta\b", p.text):
        for r in p.runs:
            if re.search(r"\bAusculta\b", r.text):
                r.text = re.sub(r"\bAusculta\b", "Resondi", r.text)
                n_old += 1
        if re.search(r"\bAusculta\b", p.text):
            set_text(p, re.sub(r"\bAusculta\b", "Resondi", p.text))
            n_old += 1
log("Data Analysis (several)", "Ausculta severity algorithm / application / device", f"Resondi ({n_old} more occurrences)",
    "Project renamed.")

# ======================================================================= RESULTS AND DISCUSSION
import json
STATS = os.path.join(ROOT, "model-rebuild", "results", "stats")
S = json.load(open(os.path.join(STATS, "stats-results.json"), encoding="utf-8"))
T, CI = S["test"], S["test_ci"]


def pc(x, d=1):
    return f"{x * 100:.{d}f}"


def ci(k, d=1, scale=100):
    lo, hi = CI[k]
    return f"{lo * scale:.{d}f}–{hi * scale:.{d}f}" if scale == 100 else f"{lo:.3f} to {hi:.3f}"


def pfmt(p):
    return "< .001" if p < 0.001 else f"= {p:.3f}".replace("0.", ".")


HEAD1, HEAD2 = P[160], P[162]
cur = P[272]._p
h = new_para(cur, "RESULTS AND DISCUSSION", HEAD1, keep_num=True)
h.paragraph_format.page_break_before = True
cur = h._p


def h2(text):
    global cur
    cur = new_para(cur, text, HEAD2, keep_next=True)._p


def para(text):
    global cur
    cur = new_para(cur, text, DBODY)._p


def tab(label, title, rows, widths, note_text=None, bold_last=False):
    global cur
    c_ = caption(cur, label, title, DBODY)
    t_ = table(c_._p, rows, widths=widths, bold_last=bold_last)
    cur = note(t_._tbl, note_text, DBODY)._p if note_text else t_._tbl


def fig(label, title, path, width, note_text):
    global cur
    c_ = caption(cur, label, title, DBODY)
    f_ = figure(c_._p, path, width, DBODY)
    cur = note(f_._p, note_text, DBODY)._p


para("This section reports the evaluation completed to date. Results of the earlier field evaluation, which used "
     "the original and since-withdrawn classification model, are summarized first. The rebuilt lung-sound classifier is "
     "then reported on the 31 held-out test patients, followed by the tests of the hypotheses that the available data "
     "allow and the severity-score analysis. The feature-fusion models are then compared with the individual "
     "single-representation models, a second round adds a paediatric corpus and is confirmed by cross-validation, and "
     "the models are then set beside the original model and the reference study. The heart-sound models, tested on "
     "public recordings, are reported last.")

h2("System Evaluation From the Field Study")
para("Table 7 summarizes the system-level results of the earlier field evaluation. Resondi recorded a stronger signal "
     "than a conventional stethoscope (45 dB against 32 dB, a 13 dB margin, or about 4.5 times the amplitude). These are "
     "indicative margins rather than a formal signal-to-noise ratio, because the two figures were not captured against a "
     "common reference, so no inferential test was applied and Hypothesis 3 remains untested. Most recordings were rated "
     "good (68 percent) or acceptable (25 percent). The recording-quality check was the slowest stage at 144.68 seconds, "
     "longer than the 15-second recording it assesses, so at 14 captures a full lung and heart examination would take "
     "about 34 minutes of screening time. End users rated the system favourably (n = 27; overall weighted mean 3.95 of 5, "
     "\"agree\"). In the field test, the original model's output agreed with the reference label for 6 of 15 recordings "
     "(40 percent; Wilson 95% CI 19.8–64.3%), which does not differ significantly from the 25 percent expected by chance "
     "(exact binomial p = .148).")
tab("Table 7", "Results of the Earlier Field Evaluation", [
    ["Measure", "Result"],
    ["Signal strength", "Resondi 45 dB; conventional stethoscope 32 dB (13 dB margin, ≈ 4.5× amplitude)"],
    ["Ambient noise", "Quiet room 24 dB; ward 35 dB; community setting 42 dB"],
    ["Recording quality", "Good 68%; acceptable 25%; poor 7%"],
    ["Response time (s)", "Connection 4.55; recording 15.00; quality check 144.68; preprocessing 20.91; classification 3.97"],
    ["Field agreement (original model)", "6 of 15 = 40% (Wilson 95% CI 19.8–64.3%); exact binomial vs 25%: p = .148"],
    ["End-user acceptance", "n = 27; overall weighted mean 3.95 of 5"],
], [2.0, 4.3], "Values are from the full research paper (response times from its Table 5). The number of recordings "
   "behind the quality proportions was not recorded, and the field test did not record whether the reference labeller "
   "was blinded to the AI output.")

h2("Model Development on the Validation Subset")
vs = sorted([r for r in S["validation_summary"] if r["seeds"] >= 2], key=lambda r: -r["bal_mean"])
NAMES = {"late3": "Late fusion of three views", "single_mfcc": "MFCC (fusion study)", "single_spec": "Spectrogram",
         "mfcc_twodet": "MFCC, two yes/no detectors", "baseline": "MFCC (deployed design)", "mfcc_spec": "MFCC + augmentation",
         "mfe_twodet": "Mel energies, two detectors", "single_chroma": "Chromagram", "mfe_floor72": "Mel energies, −72 dB floor",
         "mfe_aug": "Mel energies + augmentation", "mfe": "Mel energies (MFE)", "mfe_mixup": "Mel energies + mixup",
         "mfe_floor72_aug": "Mel energies, −72 dB + augmentation", "mfe2k": "Mel energies, 50–2,000 Hz",
         "fdc3": "Three-branch fusion", "fdc2_nochroma": "Fusion without chromagram"}
best = vs[0]
para(f"{len(vs)} model configurations were trained with three random seeds each (two for one configuration) and "
     f"compared on the 30 validation "
     f"patients only (Table 8 and Figure 6). The single-branch MFCC network reached {vs[[r['recipe'] for r in vs].index('single_mfcc')]['bal_mean']*100:.1f} "
     f"percent balanced accuracy. Mel filterbank energies alone performed worse (31.4–37.9 percent), and restricting them "
     f"to 50–2,000 Hz lowered performance further. Splitting the four-way decision into two yes/no detectors, for crackles "
     f"and for wheezes, raised the mel-energy model by about 5 points but did not improve the MFCC model. The best "
     f"configuration was late fusion of the MFCC, spectrogram, and chromagram models, which averaged "
     f"{best['bal_mean']*100:.1f} ± {best['bal_sd']*100:.1f} percent, the only change that exceeded the MFCC baseline by more "
     f"than the spread between seeds. Because three seeds per configuration are too few for a valid inferential "
     f"comparison, and because repeated testing on the validation subset would inflate false positives, these figures were "
     f"used only to choose models and are reported descriptively.")
tab("Table 8", "Validation Balanced Accuracy of the Model Configurations", [["Configuration", "Seeds", "Balanced accuracy, mean ± SD (%)", "Macro-F1"]] +
    [[NAMES.get(r["recipe"], r["recipe"]), str(r["seeds"]), f"{r['bal_mean']*100:.1f} ± {r['bal_sd']*100:.1f}", f"{r['f1_mean']:.3f}"] for r in vs],
    [2.6, 0.6, 2.0, 0.9], "Cycle-level scores on the 30 validation patients; chance is 25 percent. Validation scores are "
    "optimistic: they were used to choose the configuration, seed, and training epoch.")
fig("Figure 6", "Validation Balanced Accuracy by Configuration", os.path.join(STATS, "fig_validation_models.png"), 5.6,
    "Bars show the mean over three seeds; whiskers show one standard deviation. Rose bars are fusion models.")

h2("Classification Performance on the Test Subset")
cm = T["confusion"]
sup = [sum(r) for r in cm]
para(f"The configuration chosen on 11 November (the single-branch MFCC network, seed {S['model']['seed']}, epoch "
     f"{S['model']['epoch']}; validation balanced accuracy 47.2 percent) was evaluated once on the {S['test_patients']} test "
     f"patients ({T['n']:,} respiratory cycles). Its balanced accuracy was {pc(T['balanced_accuracy'])} percent (95% "
     f"patient-level bootstrap CI {ci('balanced_accuracy')}), plain accuracy {pc(T['accuracy'])} percent against a "
     f"majority-class baseline of {pc(T['majority_baseline'])} percent, macro-F1 {T['macro_f1']:.3f}, and Cohen's kappa "
     f"{T['kappa']:.3f} (95% CI {ci('kappa', scale=1)}), which is slight agreement (Table 9). The ICBHI score was "
     f"{pc(T['icbhi_score'])} percent (sensitivity {pc(T['icbhi_se'])}, specificity {pc(T['icbhi_sp'])}). The model detected "
     f"crackles well (recall {pc(T['recall'][0])} percent) but missed most wheezes ({pc(T['recall'][2])} percent) and "
     f"labelled most healthy cycles as abnormal (Healthy recall {pc(T['recall'][1])} percent; Table 10 and Figure 7). The "
     f"12-point drop from validation to test shows how much choosing among many runs on 30 patients flattered the "
     f"chosen model.")
tab("Table 9", "Test-Set Classification Performance (31 Patients, 1,051 Cycles)", [
    ["Measure", "Value", "95% CI"],
    ["Balanced accuracy", f"{pc(T['balanced_accuracy'])}%", ci("balanced_accuracy") + "%"],
    ["Accuracy", f"{pc(T['accuracy'])}%", ci("accuracy") + "%"],
    ["Macro-F1", f"{T['macro_f1']:.3f}", ci("macro_f1", scale=1)],
    ["Cohen's kappa", f"{T['kappa']:.3f}", ci("kappa", scale=1)],
    ["ICBHI score", f"{pc(T['icbhi_score'])}% (Se {pc(T['icbhi_se'])}%, Sp {pc(T['icbhi_sp'])}%)", ci("icbhi_score") + "%"],
    ["Majority-class baseline", f"{pc(T['majority_baseline'])}%", "—"],
    ["Chance (four balanced classes)", "25.0%", "—"],
], [2.2, 2.4, 1.6], f"Confidence intervals from {S['bootstrap_valid_draws']:,} patient-level bootstrap resamples. The model "
   "was chosen on validation before the test patients were read, and the test subset was scored once.")
tab("Table 10", "Per-Class Test Performance", [["Class", "Cycles", "Recall (sensitivity)", "Specificity", "Precision", "F1"]] +
    [[LBL, f"{sup[i]:,}", f"{pc(T['recall'][i])}%", f"{pc(T['specificity'][i])}%", f"{pc(T['precision'][i])}%", f"{T['f1'][i]:.3f}"]
     for i, LBL in enumerate(["Crackles", "Healthy", "Wheezing", "Wheezing with Crackles"])],
    [1.9, 0.7, 1.2, 0.9, 0.9, 0.7])
fig("Figure 7", "Test-Set Confusion Matrix", os.path.join(STATS, "fig_confusion_test.png"), 4.2,
    "Cell counts with row percentages; the diagonal is the recall of each class.")

h2("Hypothesis 1: Clean Versus Noise-Contaminated Recordings")
n20, n10, n5 = S["noise_20dB"], S["noise_10dB"], S["noise_5dB"]
para(f"To test Hypothesis 1, Gaussian noise was added to every test window at signal-to-noise ratios of 20, 10, and 5 dB "
     f"and the same cycles were classified again. Performance fell to chance at every level (Table 11 and Figure 8): at "
     f"20 dB, balanced accuracy dropped from {pc(T['balanced_accuracy'])} to {pc(n20['metrics']['balanced_accuracy'])} percent. "
     f"McNemar's exact test showed that more cycles changed from correct to incorrect than the reverse at each level "
     f"(20 dB: b = {n20['mcnemar']['b']}, c = {n20['mcnemar']['c']}, odds ratio {n20['mcnemar']['odds_ratio']:.2f}, "
     f"Holm-adjusted p {pfmt(n20['mcnemar']['p_holm'])}). The null hypothesis of no difference was therefore rejected: the "
     f"classifier is not robust to added noise, even at a level milder than the ward and community conditions measured in "
     f"the field.")
tab("Table 11", "Effect of Added Noise on the Same Test Cycles", [["Condition", "Accuracy", "Balanced accuracy", "b", "c", "Odds ratio", "p (Holm)"],
    ["Clean", f"{pc(T['accuracy'])}%", f"{pc(T['balanced_accuracy'])}%", "—", "—", "—", "—"]] +
    [[f"{s} dB SNR", f"{pc(S[f'noise_{s}dB']['metrics']['accuracy'])}%", f"{pc(S[f'noise_{s}dB']['metrics']['balanced_accuracy'])}%",
      str(S[f"noise_{s}dB"]["mcnemar"]["b"]), str(S[f"noise_{s}dB"]["mcnemar"]["c"]), f"{S[f'noise_{s}dB']['mcnemar']['odds_ratio']:.2f}",
      pfmt(S[f"noise_{s}dB"]["mcnemar"]["p_holm"])] for s in (20, 10, 5)],
    [1.2, 0.9, 1.2, 0.5, 0.5, 0.9, 0.9], "b = cycles correct when clean and wrong when noisy; c = the reverse. "
    "McNemar's exact binomial test, Holm-corrected across the three noise levels.")
fig("Figure 8", "Test-Set Performance Under Added Noise", os.path.join(STATS, "fig_noise_test.png"), 4.6,
    "The dashed line marks chance (25 percent).")

h2("Hypotheses 2 and 3: Device and Conventional-Stethoscope Comparisons")
para("Hypothesis 2 could not be tested: no Resondi device recordings with independent, clinician-assigned cycle labels "
     "exist yet, and the 15 field-test recordings are not linked to their reference labels in the study records. "
     "Descriptively, when the deployed model was run on the 33 stored Resondi device recordings, its highest class score "
     "was only 27–34 percent (median 30 percent), close to the 25 percent of a uniform guess, compared with 41–48 percent "
     "on reference-style recordings. Normalizing the loudness of every device recording changed none of the 33 labels, "
     "which points to the microphone, not the recording level, as the cause. Hypothesis 3 was likewise not tested "
     "inferentially, because the paired raw measurements behind the 45 dB and 32 dB figures were not retained.")

h2("Respiratory-Sound Severity Score")
cal_, sv = S["calibration"], S["severity_test"]
co = cal_["coef"]
para(f"The severity algorithm was calibrated on the {cal_['n_recordings']} validation recordings by ordinary least squares "
     f"(Table 12). All three abnormal-class confidence scores were significant predictors, but the fit was weak "
     f"(R² = {cal_['r2_fit']:.3f}), and the wheezing and crackles terms were strongly collinear (VIF {cal_['vif'][0]:.1f} and "
     f"{cal_['vif'][1]:.1f}), so the individual coefficients are unstable. On the {sv['n_recordings']} test recordings, "
     f"whose reference severity averaged {sv['ref_mean']:.1f} ± {sv['ref_sd']:.1f} percent, the uncalibrated estimator "
     f"overestimated severity by {sv['direct']['bias']:.1f} points on average (RMSE {sv['direct']['rmse']:.1f}, MAE "
     f"{sv['direct']['mae']:.1f}, R² {sv['direct']['r2']:.2f}). Calibration removed most of the bias but explained almost "
     f"none of the variation (RMSE {sv['calibrated_ols']['rmse']:.1f}, MAE {sv['calibrated_ols']['mae']:.1f}, R² "
     f"{sv['calibrated_ols']['r2']:.3f}; {cal_['clipped_test']} predictions clipped), and the beta-regression sensitivity "
     f"analysis gave the same picture (RMSE {sv['beta_regression']['rmse']:.1f}, R² {sv['beta_regression']['r2']:.3f}; Figure 9). "
     f"Because RMSE equalled roughly 43 points on a 0–100 scale, a change in severity between visits would have to exceed "
     f"about 43 points before the longitudinal analysis could count it as real.")
tab("Table 12", "Severity Calibration and Accuracy", [
    ["", "Estimate", "SE", "p", "VIF"],
    ["Intercept", f"{co['intercept']:.1f}", f"{cal_['se'][0]:.1f}", pfmt(cal_['p'][0]), "—"],
    ["p(Wheezing)", f"{co['p(W)']:.1f}", f"{cal_['se'][1]:.1f}", pfmt(cal_['p'][1]), f"{cal_['vif'][0]:.1f}"],
    ["p(Crackles)", f"{co['p(C)']:.1f}", f"{cal_['se'][2]:.1f}", pfmt(cal_['p'][2]), f"{cal_['vif'][1]:.1f}"],
    ["p(Wheezing with Crackles)", f"{co['p(WC)']:.1f}", f"{cal_['se'][3]:.1f}", pfmt(cal_['p'][3]), f"{cal_['vif'][2]:.1f}"],
    ["Test recordings (n = 164)", "RMSE", "MAE", "R²", "Bias"],
    ["Direct estimator", f"{sv['direct']['rmse']:.1f}", f"{sv['direct']['mae']:.1f}", f"{sv['direct']['r2']:.3f}", f"{sv['direct']['bias']:+.1f}"],
    ["Calibrated (OLS)", f"{sv['calibrated_ols']['rmse']:.1f}", f"{sv['calibrated_ols']['mae']:.1f}", f"{sv['calibrated_ols']['r2']:.3f}", f"{sv['calibrated_ols']['bias']:+.1f}"],
    ["Beta regression (sensitivity)", f"{sv['beta_regression']['rmse']:.1f}", f"{sv['beta_regression']['mae']:.1f}", f"{sv['beta_regression']['r2']:.3f}", f"{sv['beta_regression']['bias']:+.1f}"],
], [2.3, 1.0, 1.0, 1.0, 0.9], f"Calibration fitted on {cal_['n_recordings']} validation recordings (R² = {cal_['r2_fit']:.3f}, "
   f"df = {cal_['df']}); errors are in percentage points on the 0–100 severity scale.")
fig("Figure 9", "Predicted Against Reference Severity (Test Recordings)", os.path.join(STATS, "fig_severity_test.png"), 4.0,
    "The dashed line marks perfect agreement.")
kw = S["kruskal"]
g = kw["groups"]
sig = [d for d in kw["dscf"] if d["p"] < 0.05]
para(f"A Kruskal–Wallis test found that predicted severity differed across the reference recording categories, "
     f"H({kw['df']}) = {kw['H']:.2f}, p {pfmt(kw['p'])}, but the effect was small (ε² = {kw['epsilon_sq']:.3f}; Table 13). "
     f"Dwass–Steel–Critchlow–Fligner comparisons located the difference only between Crackles and Wheezing with Crackles "
     f"recordings (p {pfmt(sig[0]['p']) if sig else '> .05'}); healthy recordings received a median predicted severity of "
     f"{g['Healthy']['median']:.1f} percent, close to that of abnormal recordings, which reflects the model's tendency to "
     f"label healthy breaths as abnormal.")
tab("Table 13", "Predicted Severity by Reference Recording Category (Test Recordings)",
    [["Category", "n", "Median (%)", "IQR (%)"]] +
    [[k_, str(v_["n"]), f"{v_['median']:.1f}", f"{v_['iqr'][0]:.1f}–{v_['iqr'][1]:.1f}"] for k_, v_ in g.items()] +
    [["Pairwise (DSCF)", "W", "p", ""]] + [[d["pair"], f"{d['W']:.2f}", pfmt(d["p"]).replace("= ", ""), ""] for d in kw["dscf"]],
    [2.8, 0.8, 1.2, 1.4], f"Kruskal–Wallis H({kw['df']}) = {kw['H']:.2f}, p {pfmt(kw['p'])}, ε² = {kw['epsilon_sq']:.3f}. "
    "Recording category: Healthy if no cycle is adventitious, otherwise the most frequent adventitious class, ties to "
    "Wheezing with Crackles.")

h2("Feature-Fusion Model Compared With the Individual Models")
FZ = json.load(open(os.path.join(STATS, "fusion-comparison.json"), encoding="utf-8"))
FI = FZ["sets"]["icbhi"]
FM, FC, FMC = FI["metrics"], FI["ci"], FI["mcnemar_vs_primary"]
FORD = ["single_mfcc", "single_spec", "single_chroma", "fdc2_nochroma", "fdc3", "late3"]
FN = {"single_mfcc": "MFCC alone", "single_spec": "Spectrogram alone", "single_chroma": "Chromagram alone",
      "fdc2_nochroma": "Two-branch fusion (MFCC + spectrogram)", "fdc3": "Three-branch feature fusion",
      "late3": "Late fusion of the three models"}
VAL = {r["recipe"]: r for r in S["validation_summary"]}
import csv as _csv, statistics as _st
_seen = {}
for _r in _csv.DictReader(open(os.path.join(STATS, "..", "fusion-validation.csv"), encoding="utf-8")):
    if _r["data"] == "icbhi" and _r["val_set"] == "icbhi":
        _seen.setdefault((_r["recipe"], _r["seed"]), float(_r["cycle_balanced_acc"]))
for _rc in {k[0] for k in _seen}:
    _v = [v for (rc, _), v in _seen.items() if rc == _rc]
    VAL[_rc] = {"bal_mean": _st.mean(_v), "bal_sd": _st.stdev(_v) if len(_v) > 1 else 0.0, "seeds": len(_v)}
lt, sm = FM["late3"], FM["single_mfcc"]
best_single = max(["single_mfcc", "single_spec", "single_chroma"], key=lambda r: FM[r]["balanced_accuracy"])
para("The fusion design is adapted from the reference study (Tariq et al., 2022). That study converted 3-second clips "
     "of ICBHI recordings into spectrogram, MFCC, and chromagram images, trained three convolutional networks "
     "(FDC-1, FDC-2, and FDC-3) separately, and fused them into a single network (FDC-FS) that it applied to one "
     "representation at a time. Because the reference study found that each representation worked well on its own, "
     "this study fused the representations themselves: each one feeds its own convolutional branch, and the branch "
     "outputs are either concatenated and trained jointly (three-branch feature fusion) or produced by separately "
     "trained models and averaged (late fusion, which, like FDC-FS, combines networks that were trained independently). "
     "Three questions were asked: whether each representation carries useful information on its own, whether combining "
     "them helps, and whether joint training is better than averaging separately trained models. Six configurations "
     "were therefore trained on the same 65 patients: the three single-representation models, the three-branch feature "
     "fusion network, a two-branch ablation without the chromagram, and late fusion of the three single "
     "models. Late fusion had the highest mean validation balanced accuracy "
     f"({VAL['late3']['bal_mean']*100:.1f} ± {VAL['late3']['bal_sd']*100:.1f} percent) and was declared the primary model "
     "before any test patient was read. Each configuration was then scored once on the 31 test patients at the seed it "
     "had scored best with on validation, so that the individual models could be compared with fusion; none of these "
     "test scores was used to choose a model.")
para(f"On the test subset, late fusion reached a balanced accuracy of {pc(lt['balanced_accuracy'])} percent (95% "
     f"patient-level bootstrap CI {FC['late3'][0]*100:.1f}–{FC['late3'][1]*100:.1f}), macro-F1 {lt['macro_f1']:.3f}, and "
     f"Cohen's kappa {lt['kappa']:.3f} (Table 14 and Figure 10). The MFCC model alone, the representation used by the "
     f"deployed classifier, reached {pc(sm['balanced_accuracy'])} percent, the spectrogram model "
     f"{pc(FM['single_spec']['balanced_accuracy'])} percent, and the chromagram model "
     f"{pc(FM['single_chroma']['balanced_accuracy'])} percent. The jointly trained three-branch feature-fusion network reached "
     f"{pc(FM['fdc3']['balanced_accuracy'])} percent and its two-branch ablation {pc(FM['fdc2_nochroma']['balanced_accuracy'])} "
     f"percent. The difference between late fusion and the MFCC model was "
     f"{(lt['balanced_accuracy'] - sm['balanced_accuracy'])*100:+.1f} points (95% CI "
     f"{-FC['single_mfcc_minus_primary'][1]*100:+.1f} to {-FC['single_mfcc_minus_primary'][0]*100:+.1f}); McNemar's exact "
     f"test on the same 1,051 cycles gave b = {FMC['single_mfcc']['b']}, c = {FMC['single_mfcc']['c']}, Holm-adjusted p "
     f"{pfmt(FMC['single_mfcc']['p_holm'])}. Late fusion therefore classified more cycles correctly than the MFCC model, "
     "mostly healthy ones, yet scored lower on balanced accuracy, because it recognised fewer cycles of the smaller "
     "abnormal classes; balanced accuracy, not the cycle count, is the primary measure.")
tab("Table 14", "Test-Set Performance of the Individual and Fusion Models (31 Patients, 1,051 Cycles)",
    [["Model", "Validation BA (%)", "Test BA, 95% CI (%)", "Macro-F1", "Kappa", "ICBHI score (%)", "vs late fusion: b / c, p (Holm)"]] +
    [[FN[r], f"{VAL[r]['bal_mean']*100:.1f}" if r in VAL else "—",
      f"{pc(FM[r]['balanced_accuracy'])} ({FC[r][0]*100:.1f}–{FC[r][1]*100:.1f})", f"{FM[r]['macro_f1']:.3f}",
      f"{FM[r]['kappa']:.3f}", pc(FM[r]['icbhi_score']),
      (f"{FMC[r]['b']} / {FMC[r]['c']}, {pfmt(FMC[r]['p_holm']).replace('= ', '')}" if r in FMC else "primary")] for r in FORD],
    [1.9, 0.75, 1.15, 0.6, 0.55, 0.7, 1.15],
    "BA = balanced accuracy (mean per-class recall); chance is 25 percent. Validation BA is the mean of three seeds; "
    "each test score uses the seed chosen on validation. b = cycles that late fusion classified correctly and the other "
    "model did not; c = the reverse. McNemar's exact test, Holm-corrected across the five comparisons. Every test run is "
    "logged in model-rebuild/results/final-test-log.csv.")
fig("Figure 10", "Test Balanced Accuracy of the Deployed, Individual, and Fusion Models",
    os.path.join(STATS, "fig_fusion_test.png"), 6.2,
    "Whiskers are 95 percent patient-level bootstrap confidence intervals; the dashed line marks chance. Grey bars are "
    "single-representation models, pale bars jointly trained fusion, and the rose bar the primary late-fusion model.")
_cls = ["Crackles", "Healthy", "Wheezing", "Wheezing with Crackles"]
_top = {i: max(FORD, key=lambda r: FM[r]["recall"][i]) for i in range(4)}
para("The representations failed in different places, which is the condition under which fusion can help (Table 15 and "
     f"Figure 11). The MFCC model found most crackles (recall {pc(sm['recall'][0])} percent) but labelled most healthy "
     f"cycles as abnormal (Healthy recall {pc(sm['recall'][1])} percent). The spectrogram model recognised more healthy "
     f"cycles ({pc(FM['single_spec']['recall'][1])} percent) but few wheezes ({pc(FM['single_spec']['recall'][2])} percent). "
     f"The chromagram model, which keeps only pitch-class information, had the highest recall for wheezes "
     f"({pc(FM['single_chroma']['recall'][2])} percent) and for the combined class ({pc(FM['single_chroma']['recall'][3])} "
     f"percent), consistent with wheezes being tonal. The jointly trained three-branch network recognised the most healthy "
     f"cycles ({pc(FM['fdc3']['recall'][1])} percent). Late fusion recognised {pc(lt['recall'][1])} percent of healthy "
     f"cycles and {pc(lt['recall'][2])} percent of wheezes, while crackle recall fell to {pc(lt['recall'][0])} percent and "
     f"the combined class to {pc(lt['recall'][3])} percent: averaging traded the single models' sensitivity to abnormal "
     f"sounds for fewer false alarms on healthy breaths, and the combined class was largely lost. No configuration detected "
     f"the combined Wheezing with Crackles class reliably; the best recall for it was "
     f"{max(FM[r]['recall'][3] for r in FORD)*100:.1f} percent ({FN[_top[3]]}).")
tab("Table 15", "Per-Class Test Recall of the Individual and Fusion Models",
    [["Model", "Crackles", "Healthy", "Wheezing", "Wheezing with Crackles", "Specificity for Healthy"]] +
    [[FN[r]] + [f"{x*100:.1f}%" for x in FM[r]["recall"]] + [f"{FM[r]['icbhi_sp']*100:.1f}%"] for r in FORD],
    [2.2, 0.8, 0.8, 0.8, 1.2, 1.0],
    "Recall is the share of each class's test cycles classified correctly. The class sizes are Crackles 268, Healthy "
    "555, Wheezing 120, and Wheezing with Crackles 108 cycles.")
fig("Figure 11", "Per-Class Test Recall by Model", os.path.join(STATS, "fig_fusion_recall.png"), 6.2,
    "Bars show recall for each class. The representations make different errors; no configuration detects the combined class reliably.")
if "sprs" in FZ["sets"]:
    FS = FZ["sets"]["sprs"]
    para(f"As an external check, the same models were applied to the held-out SPRSound test set ({FS['patients']} "
         f"children, {FS['cycles']:,} annotated events; Table 16). These recordings come from a different stethoscope, a "
         f"different age group, and a different hospital, and none of these children were used in training. Late fusion "
         f"reached {pc(FS['metrics']['late3']['balanced_accuracy'])} percent balanced accuracy and the MFCC model "
         f"{pc(FS['metrics']['single_mfcc']['balanced_accuracy'])} percent, so the ranking of the configurations should "
         f"be read as specific to the ICBHI recording conditions until it is confirmed on other data.")
    tab("Table 16", "External Check on the SPRSound Test Set (Children, Models Trained on ICBHI Only)",
        [["Model", "Balanced accuracy, 95% CI (%)", "Macro-F1", "Crackles", "Healthy", "Wheezing", "W + C"]] +
        [[FN[r], f"{pc(FS['metrics'][r]['balanced_accuracy'])} ({FS['ci'][r][0]*100:.1f}–{FS['ci'][r][1]*100:.1f})",
          f"{FS['metrics'][r]['macro_f1']:.3f}"] + [f"{x*100:.0f}%" for x in FS["metrics"][r]["recall"]] for r in FORD],
        [2.2, 1.6, 0.7, 0.7, 0.7, 0.7, 0.6],
        "SPRSound (Zhang et al., 2022): paediatric recordings at 8 kHz, resampled to 16 kHz; event labels mapped to the "
        "four classes, with rhonchi and stridor excluded. W + C = Wheezing with Crackles.")

CV = json.load(open(os.path.join(ROOT, "model-rebuild", "results", "cv-results.json"), encoding="utf-8"))["results"]
cvm, cvf = CV["mfcc_icbhi seed 11"], CV["fdc3_sprs ensemble 11+22+33"]
h2("Adding the Paediatric Corpus, and Cross-Validation")
para("Because every model trained on ICBHI alone failed on the SPRSound children and none separated clearly from the "
     "others on the ICBHI test patients, a second round added SPRSound to the training data. SPRSound is 82 percent "
     "healthy and recorded from children, and added as it was, it taught the model that a child's breath is healthy: the "
     "MFCC model then found almost none of ICBHI's healthy cycles. It was therefore rebalanced. All crackle and wheeze "
     "windows were kept, healthy windows were capped at the number in ICBHI (20,590 of 49,417), every combination of "
     "dataset and class carried equal weight, and the audio from both corpora was band-limited to 0.1–3.9 kHz, "
     "levelled, and normalised separately for each corpus. The same six configurations were trained with three seeds "
     "each and compared on the ICBHI validation patients only. The three-branch feature-fusion network led "
     "(48.7 ± 1.0 percent), and its seed-33 run was named as the primary model in writing before the test patients "
     "were scored.")
para("On the 31 ICBHI test patients the primary model reached 39.4 percent balanced accuracy (95 percent CI 28.4–44.6; "
     "macro-F1 0.38), the best pre-specified test result of the study, and 57.2 percent (46.7–63.4) on the 230 SPRSound "
     "test children (Table 17). Healthy recall rose to 52 percent, against about 30 percent for the MFCC models, so far "
     "fewer healthy breaths were flagged as abnormal. Wheezing remained weak at 24 percent.")
tab("Table 17", "Test Results of the Second Round, Trained on ICBHI and SPRSound",
    [["Model", "ICBHI test, 31 adults", "SPRSound test, 230 children", "Role"],
     ["Three-branch feature fusion, seed 33", "39.4% (28.4–44.6)", "57.2% (46.7–63.4)", "Primary"],
     ["MFCC alone, seed 22", "36.7%", "51.3%", "Comparison"],
     ["Two-branch fusion without chromagram, seed 11", "36.5%", "53.4%", "Comparison"],
     ["Late fusion of three models, seed 22", "35.7%", "52.8%", "Comparison"],
     ["Spectrogram alone, seed 33", "34.6%", "51.0%", "Comparison"],
     ["Chromagram alone, seed 33", "38.9%", "45.9%", "Comparison"]],
    [2.6, 1.3, 1.5, 0.9],
    "Balanced accuracy; chance is 25 percent. Intervals are patient-level bootstrap intervals and are given for the "
    "primary model. This was the third reading of the ICBHI test patients; in each reading the primary model was "
    "fixed in advance.")
para("Thirty-one test patients give wide intervals, and the test patients had now been read three times. The two "
     "designs that matter most were therefore compared by five-fold cross-validation across all 126 ICBHI patients: the "
     "MFCC network trained on ICBHI alone, which is the design of the first deployed model, and the fusion network "
     "trained on ICBHI and SPRSound, averaged over its three seeds. Patients were dealt into five folds balanced by "
     "class and recording device; in fold k, fold k was the test set, fold k + 1 was used only for early stopping, and "
     "the other three folds were used for training. Every patient was therefore classified once by a model that had "
     "never seen them.")
para(f"The fusion network reached {cvf['pooled_balanced']*100:.1f} percent balanced accuracy (95 percent CI "
     f"{cvf['ci95'][0]*100:.1f}–{cvf['ci95'][1]*100:.1f}) against {cvm['pooled_balanced']*100:.1f} percent "
     f"({cvm['ci95'][0]*100:.1f}–{cvm['ci95'][1]*100:.1f}) for the MFCC network (Table 18). In a paired patient "
     "bootstrap of 5,000 resamples the difference was 5.9 points (95 percent CI 1.0 to 10.3; one-sided p = 0.008), and the "
     "fusion network scored higher on 14 of the 15 seed-and-fold comparisons, the other being a tie. The supporting "
     "analyses, run in jamovi, agreed: the fusion network was higher in every fold (paired t(4) = 4.75, p = .009; "
     "Figure 12); 69 of the 126 patients had more of their cycles classified correctly by it, 39 fewer and 18 the same "
     "(Wilcoxon signed-rank p = .009; Figure 13); and recall rose for every class (Figure 14). On the SPRSound test "
     f"children the fold models averaged {cvf['sprs_test_mean']*100:.0f} percent. The single test reading (39.4 percent) "
     "and the cross-validation (40.0 percent) agree closely, so about 40 percent is the study's best estimate.")
_rc = lambda r: [f"{r['recall'][k]*100:.0f}%" for k in ("Crackles", "Healthy", "Wheezing", "Wheezing with Crackles")]
tab("Table 18", "Five-Fold Cross-Validation Across All 126 ICBHI Patients (6,898 Cycles)",
    [["Measure", "MFCC network, ICBHI only", "Fusion network, ICBHI + SPRSound"],
     ["Balanced accuracy (95% CI)", f"{cvm['pooled_balanced']*100:.1f}% ({cvm['ci95'][0]*100:.1f}–{cvm['ci95'][1]*100:.1f})",
      f"{cvf['pooled_balanced']*100:.1f}% ({cvf['ci95'][0]*100:.1f}–{cvf['ci95'][1]*100:.1f})"],
     ["Fold mean ± SD", f"{cvm['fold_mean']*100:.1f} ± {cvm['fold_sd']*100:.1f}",
      f"{cvf['fold_mean']*100:.1f} ± {cvf['fold_sd']*100:.1f}"],
     ["Plain accuracy", f"{cvm['accuracy']*100:.1f}%", f"{cvf['accuracy']*100:.1f}%"],
     ["Macro-F1", f"{cvm['macro_f1']:.2f}", f"{cvf['macro_f1']:.2f}"],
     ["Recall: Crackles / Healthy / Wheezing / W + C", " / ".join(_rc(cvm)), " / ".join(_rc(cvf))],
     ["SPRSound test children (mean of folds)", "—", f"{cvf['sprs_test_mean']*100:.0f}%"]],
    [2.4, 1.9, 2.0],
    "The fusion network is the average of three training seeds. Intervals are patient-level bootstrap intervals. "
    "W + C = Wheezing with Crackles.")
fig("Figure 12", "Balanced Accuracy of the Two Designs in Each of the Five Folds", os.path.join(FIG, "j1_cv_folds.png"), 4.6,
    "Produced in jamovi (jmv 2.8, paired-samples t-test, descriptives plot). Points are fold means with 95% confidence "
    "intervals.")
fig("Figure 13", "Share of Each Patient's Cycles Classified Correctly, by Design", os.path.join(FIG, "j2_cv_patients.png"), 4.6,
    "Produced in jamovi (jmv 2.8, paired samples, 126 patients).")
fig("Figure 14", "True Class Against Predicted Class in Cross-Validation", os.path.join(FIG, "j3_cv_confusion.png"), 5.4,
    "Produced in jamovi (jmv 2.8, contingency tables, row percentages). The two panels have different vertical scales.")
para("On 13 November 2026 this fusion network replaced the Edge Impulse model in the Resondi application. Because Edge "
     "Impulse provides no chromagram processing, it runs in the browser as an exported ONNX model, the three seeds "
     "combined in one file, with the band-limiting, levelling and feature extraction rewritten in JavaScript; the "
     "rewritten features gave the same top class as the Python originals on 600 of 600 validation windows. On 26 "
     "recordings already made with the Resondi device it gave top-class scores of 31 to 66 percent (median 41), against "
     "27 to 34 percent for the model it replaced. That shows it is more decisive on device audio, not that it is more "
     "often right: none of those recordings has a reference label, so its accuracy on the device remains untested.")

h2("Comparison With the Original Model and the Reference Study")
para("Table 19 places the models of this study beside the original Resondi model and the reference study. The original "
     "model was reported at 71.1 percent test accuracy and 83.4 to 83.7 percent validation accuracy, but those figures "
     "came from five-second clips cut at a one-second stride from the same patients and split at random, so near-identical "
     "audio appeared in both training and testing, and every clip carried the patient's diagnosis rather than a label of "
     "the sound it contained. They measure recognition of familiar patients, not of breath sounds, and cannot be compared "
     "with any figure in this section. The only unleaked estimate for the original model is the field agreement of 6 of "
     "15 recordings (40 percent), which did not differ from chance.")
para("The reference study reported a weighted accuracy of 99.1 percent for FDC-FS on spectrogram images of the ICBHI "
     "recordings (99.0 percent for MFCC and 98.4 percent for chromagram images), and 97, 91, and 95 percent before data "
     "augmentation. Four differences in protocol mean these figures cannot be set against the present ones. First, its "
     "task was the patient's diagnosis in six categories (bronchiectasis, chronic obstructive pulmonary disease, healthy, "
     "lower and upper respiratory tract infection, and pneumonia), not the sound of each breath; chronic obstructive "
     "pulmonary disease made up 785 of its 919 recordings (85 percent), and the weighted accuracy it reported is dominated "
     "by that class. Second, the recordings were augmented tenfold before being divided into training (64 percent), "
     "validation (16 percent), and test (20 percent) sets, and the study does not report keeping each patient's "
     "recordings, or the augmented copies of one recording, on one side of the split. Third, it classified 3-second clips "
     "rather than breathing cycles. Fourth, its fused network has about 1.48 million trainable parameters, against roughly "
     "190,000 for the fusion network here, which was trained on 65 patients. When the idea was adapted to the present task "
     "and evaluated on whole held-out patients, the best pre-specified configuration reached 39.4 percent balanced "
     "accuracy on the test patients and 40.0 percent in cross-validation across all 126. The gap shows how strongly the evaluation protocol and the task, rather than the "
     "architecture, determine the number that is reported. The finding the two studies share is that spectrogram, MFCC, "
     "and chromagram representations each carry usable information about lung sounds.")
tab("Table 19", "Original Model, Deployed Models, and Fusion Models Compared", [
    ["Model", "Labels", "Evaluation", "Result", "Comparable?"],
    ["Original Resondi model (withdrawn)", "Patient diagnosis on every clip", "Random split of overlapping 5-s clips",
     "71.1% test; 83.4–83.7% validation accuracy", "No: leaked"],
    ["Original model, field test", "Reference label per recording", "15 device recordings",
     "6 of 15 = 40% agreement (95% CI 19.8–64.3%)", "Partly: device audio, n = 15"],
    ["First deployed model (Edge Impulse v1, int8; in the app 10\u201313 Nov)", "Per-cycle sound labels", "31 held-out patients",
     "33.5% balanced; 44.0% accuracy", "Yes"],
    ["Deployed design retrained (11 Nov)", "Per-cycle sound labels", "31 held-out patients",
     "35.0% balanced (95% CI 24.6–40.3%)", "Yes"],
    ["MFCC alone (fusion study)", "Per-cycle sound labels", "31 held-out patients",
     f"{pc(sm['balanced_accuracy'])}% balanced", "Yes"],
    ["Three-branch feature fusion", "Per-cycle sound labels", "31 held-out patients",
     f"{pc(FM['fdc3']['balanced_accuracy'])}% balanced", "Yes"],
    ["Late fusion (primary)", "Per-cycle sound labels", "31 held-out patients",
     f"{pc(lt['balanced_accuracy'])}% balanced (95% CI {FC['late3'][0]*100:.1f}–{FC['late3'][1]*100:.1f}%)", "Yes"],
    ["Three-branch fusion + SPRSound (primary, second round)", "Per-cycle sound labels", "31 held-out patients",
     "39.4% balanced (95% CI 28.4–44.6%)", "Yes"],
    ["Three-branch fusion + SPRSound, 3-seed ensemble (in the app since 13 Nov)", "Per-cycle sound labels",
     "5-fold cross-validation, all 126 patients", "40.0% balanced (95% CI 35.9–43.5%)", "Yes"],
    ["MFCC design, same cross-validation", "Per-cycle sound labels", "5-fold cross-validation, all 126 patients",
     "34.0% balanced (95% CI 30.4–38.2%)", "Yes"],
    ["Reference study, FDC-FS (Tariq et al., 2022), original data", "Diagnosis, 6 classes (COPD 85%)",
     "64/16/20 split of 3-s clips; patient separation not reported", "97% (spectrogram), 91% (MFCC), 95% (chromagram), weighted",
     "No: different task and protocol"],
    ["Reference study, FDC-FS, tenfold augmented data", "Diagnosis, 6 classes (COPD 85%)",
     "Augmented before splitting", "99.1% (spectrogram), 99.0% (MFCC), 98.4% (chromagram), weighted",
     "No: different task and protocol"],
], [1.9, 1.3, 1.4, 1.6, 1.0], "Balanced accuracy averages the four per-class recalls; plain accuracy is inflated by the "
   "Healthy majority (52.8 percent of test cycles). The reference study's figures are weighted accuracies over six "
   "diagnosis classes as published (Tariq et al., 2022, Tables 8 and 9).")

h2("Heart Sound Component: Models Tested on CirCor")
para("Heart Mode is implemented on the device and in the application: it guides the operator through the aortic, "
     "pulmonic, tricuspid and mitral areas and Erb's point, in order from the base of the heart to the apex (Figure 15), "
     "records 15 seconds at each site in the same 16 kHz WAV format as lung recordings, and files each recording by site "
     "for practitioner review. No heart recording is passed to the lung classifier; heart recordings are analysed by "
     "the separate heart-sound models described below, which now run in the application.")
fig("Figure 15", "The Five Cardiac Sites Recorded in Heart Mode", os.path.join(FIG, "h1_heart_sites.png"), 3.8,
    "Numbered in recording order. Erb's point (3) is filed for the practitioner and has no counterpart in the CirCor "
    "dataset, so it is not part of the classifier input.")
para("Two heart-sound models were trained and tested on the CirCor DigiScope public release (Table 3: 3,163 recordings "
     "from 942 patients). The patients were divided with a fixed seed into training (564 patients, 1,898 recordings), "
     "validation (189 patients, 634 recordings) and test (189 patients, 631 recordings) subsets, stratified by murmur "
     "label and collection campaign, so that no patient appeared in more than one subset. Each recording was band-pass "
     "filtered from 25 to 1,900 Hz, levelled, and converted to a log-power spectrogram at 50 frames per second. The "
     "segmentation model, a small convolutional network followed by a bidirectional recurrent layer, labels every 20 ms "
     "frame as S1, systole, S2 or diastole, learned from the expert boundaries, and its output is decoded so that the "
     "four states follow the order of the cardiac cycle. Heart rate is 60 divided by the median interval between "
     "successive S1 onsets. The murmur model, a one-dimensional convolutional network averaged over three training "
     "seeds, scores six-second windows; a patient counts as positive when any of their sites does. Patients labelled "
     "Unknown were left out of training and are reported separately. As the analysis plan specifies, the murmur "
     "threshold was fixed on the validation patients, before any test patient was scored, as the highest one reaching "
     "the pre-specified minimum sensitivity of 80 percent.")
para("Table 20 gives the results on the 189 test patients. The segmentation model found 96.8 percent of reference S1 "
     "sounds and 97.3 percent of S2 sounds within 100 ms, with mean onset errors of 15 and 12 ms. Heart rate was within "
     "5 beats per minute of the reference on 85 percent of 631 recordings and within 10 on 96 percent, a mean absolute "
     "error of 3.0 beats per minute (95 percent CI 2.5–3.6) against 35.4 for an untrained autocorrelation baseline "
     "(Figure 16). The error had almost no bias (+0.1 beats per minute), but its 95 percent limits of agreement were "
     "−13.7 to +14.0, because a few recordings, mostly at very fast or very slow rates, were read badly wrong.")
para("The murmur model did not reach its pre-specified sensitivity on the test patients. The threshold that gave 80.6 "
     "percent sensitivity on validation found 24 of the 36 test patients with a murmur, 66.7 percent (95 percent CI "
     "50.0–81.8), and wrongly flagged 4 of the 139 without one, a specificity of 97.1 percent. Its AUROC of 0.96 shows "
     "that it ranks patients well, so the shortfall lies in a threshold set on 189 validation patients that did not "
     "carry over; the threshold was not changed after the test was read. Of the 14 test patients labelled Unknown, it "
     "flagged 2. A screening flag that misses one murmur in three cannot be used to rule a murmur out.")
para("Both models were then placed in the Resondi application, exported to ONNX and run in the browser with ONNX "
     "Runtime Web, with the feature calculation rewritten in JavaScript. The application first low-pass filters each "
     "16 kHz device recording and keeps every fourth sample, to match CirCor's 4 kHz, and then computes exactly the "
     "training features. Through that path the 631 test recordings, upsampled to 16 kHz, gave a heart-rate error of "
     "3.03 beats per minute against 3.01, and the same murmur flag on 99.7 percent of recordings. The JavaScript code "
     "matched the Python reference on 25 of 25 recordings in Node.js and on 8 of 8 in a browser on the application's "
     "preview build, where an analysis took under a second once the models, about 2 MB, had downloaded. A heart "
     "recording is analysed on request; the estimated heart rate and the murmur flag are saved with it, shown with "
     "their limits (a screening aid, tested on public recordings of children and not on the device, and a missing "
     "flag does not rule a murmur out), and passed to the reviewing cardiac practitioner with the case. These checks "
     "show that the application computes what was tested, not how the models perform on the Resondi microphone.")
tab("Table 20", "Heart-Sound Models on 189 CirCor Test Patients", [
    ["Model", "Measure", "Result (95% CI)"],
    ["Segmentation", "S1 found within 100 ms; detections that are real", "96.8%; 95.7%"],
    ["Segmentation", "S2 found within 100 ms; detections that are real", "97.3%; 96.5%"],
    ["Segmentation", "Mean onset error, S1; S2", "15 ms; 12 ms"],
    ["Heart rate (631 recordings)", "Mean absolute error", "3.0 BPM (2.5–3.6); untrained baseline 35.4 (29.9–40.8)"],
    ["Heart rate (631 recordings)", "Within 5 BPM; within 10 BPM", "85%; 96%"],
    ["Murmur (175 patients)", "Sensitivity (pre-specified minimum 80%)", "66.7% (50.0–81.8): 24 of 36"],
    ["Murmur (175 patients)", "Specificity", "97.1% (93.9–99.3): 135 of 139"],
    ["Murmur (175 patients)", "Precision (positive predictive value)", "85.7% (71.0–96.7)"],
    ["Murmur (175 patients)", "F1-score; Cohen's kappa", "0.75 (0.61–0.86); 0.70 (0.54–0.82)"],
    ["Murmur (175 patients)", "AUROC", "0.96 (0.92–0.99)"],
], [1.7, 2.4, 2.2], "CirCor recordings: children and adolescents in Brazil, recorded with an electronic stethoscope. "
   "Murmur measures are per patient; the 14 patients labelled Unknown are excluded and reported in the text. Neither "
   "model has been tested on Resondi device recordings. Scripts: model-rebuild/scripts/heart_seg.py and heart_murmur.py.")
fig("Figure 16", "Estimated Against Reference Heart Rate on 631 CirCor Test Recordings",
    os.path.join(FIG, "r6_heart_rate.png"), 3.9,
    "Each point is one recording. The dashed line is perfect agreement and the shaded band is within 5 beats per minute; "
    "teal points are more than 10 beats per minute off. Reference rates come from the dataset's annotated S1 boundaries.")
para("Several parts of the cardiac plan are not yet done, and they are stated here so that the results are not read as "
     "more than they are. The models were trained before the cardiologist's blinded review of 25 CirCor recordings was "
     "returned, although the plan put the review first; if the review finds the dataset's labels unreliable, these "
     "results must be revised. The murmur model does not yet use the segmentation stage, murmur timing (systolic or "
     "diastolic) has not been attempted, the cardiac abnormality extent score and the recording-level metrics have not "
     "been computed, and the frequency response of the Resondi acquisition chain has not been measured. One change was "
     "made before testing and is recorded in the training script: the segmentation model was planned with three seeds "
     "and up to 40 epochs but, at about five minutes an epoch, was trained with one seed for up to 15. Hypotheses 1 and "
     "2 have so far been tested for lung sounds only.")
para("The order of the remaining cardiac work follows from the lung results. A lung classifier trained on one set of "
     "stethoscopes or one age group did not transfer to another, and CirCor was recorded from Brazilian children, whose "
     "heart rates (median 103 beats per minute in the test set) are higher than those of the Filipino adults Resondi "
     "will also examine, with a commercial electronic stethoscope. The cardiologist's review will be completed, the "
     "acquisition chain's low-frequency response measured, since most S1 and S2 energy lies below about 150 Hz, and the "
     "murmur model's sensitivity raised to its target on new patients, and the models will then be tested on heart "
     "recordings made with the Resondi device and labelled by a cardiologist. The models were placed in the "
     "application before that test, which the plan had put first, so every heart result there is marked as a "
     "screening aid until the device test is done.")

h2("Discussion")
para("Rebuilding the classifier with per-cycle sound labels and a patient-wise, device-balanced split produced the first "
     "unleaked estimate of its performance: a balanced accuracy of 35.0 percent on 31 unseen patients. This is above the "
     "25 percent chance level, but the 95 percent confidence interval (24.6–40.3 percent) reaches down to chance, and "
     "Cohen's kappa of 0.15 indicates only slight agreement. The figures of 71 to 84 percent reported for the original "
     "model came from overlapping windows of the same patients appearing in both training and testing, together with "
     "diagnosis labels applied to every window, and cannot be compared with these results. The present figures are lower "
     "but measure what the plan set out to measure. A second round, which added a paediatric corpus to training, raised "
     "the best estimate to about 40 percent, confirmed across all 126 patients.")
para("Three findings shape the next stage. First, validation scores were consistently optimistic: the chosen model fell "
     "from 47.2 percent on validation to 35.0 percent on test, which justifies scoring the test subset once and reporting "
     "every test run. Second, the model's errors are systematic rather than random: it detects crackles but misses most "
     "wheezes and flags about 70 percent of healthy cycles as abnormal. As a screening aid this is the safer direction of "
     "error, but it would overload a practitioner's review queue, and it also explains why the severity score separates "
     "the recording categories so weakly. Third, the classifier is fragile: noise at 20 dB below the signal reduced it to "
     "chance, and on recordings from the Resondi microphone the first deployed model's output was close to uniform. Both point to the same "
     "limitation, which is that a model trained on four hospital stethoscopes does not transfer to a different acquisition "
     "chain or a noisier environment.")
_gain = (lt["balanced_accuracy"] - sm["balanced_accuracy"]) * 100
_sig = FMC["single_mfcc"]["p_holm"] < 0.05 and FC["single_mfcc_minus_primary"][1] < 0
_ci_cross = FC["single_mfcc_minus_primary"][0] < 0 < FC["single_mfcc_minus_primary"][1]
if _gain > 0 and _sig:
    _verdict = (f"Fusion helped: late fusion exceeded the MFCC model by {_gain:.1f} points, and the paired McNemar test "
                f"confirmed that the gain was not a chance difference on these cycles.")
elif _gain > 0:
    _verdict = (f"Fusion helped only modestly: late fusion exceeded the MFCC model by {_gain:.1f} points, but "
                + ("the bootstrap interval for the difference includes zero" if _ci_cross else
                   "the paired McNemar test was not significant after correction")
                + ", so with 31 test patients the gain cannot be distinguished from chance.")
else:
    _verdict = (f"Fusion did not help on the test patients: late fusion scored {abs(_gain):.1f} points "
                f"{'below' if _gain < 0 else 'level with'} the MFCC model, despite leading on validation.")
_dep = 35.0
para("The fusion study tested the central design idea of the reference study under honest conditions. " + _verdict +
     f" It also scored below the deployed design retrained on the same split ({_dep:.1f} percent), so fusion trained on ICBHI alone was not adopted. "
     "Two observations explain why fusion was worth testing and why it did not pay off. First, the representations made "
     "different errors: the MFCC model over-called crackles, the spectrogram and fusion models recognised healthy breaths "
     "better, and the chromagram picked up the tonal quality of wheezes. Averaging their outputs, however, pulled the "
     "decisions toward the Healthy and Crackles classes and lost most of the combined class, so the errors cancelled "
     "less than hoped. Second, late fusion of separately trained models did "
     f"{'better' if lt['balanced_accuracy'] >= FM['fdc3']['balanced_accuracy'] else 'worse'} than the jointly trained "
     f"three-branch network ({pc(FM['fdc3']['balanced_accuracy'])} percent; McNemar b = {FMC['fdc3']['b']}, "
     f"c = {FMC['fdc3']['c']}, Holm-adjusted p {pfmt(FMC['fdc3']['p_holm'])}), even though late fusion had led on "
     "validation. With 65 training patients and 31 test patients, a ranking set on validation did not hold on test, which "
     "is itself a reason to choose the model before reading the test subset and to report every configuration.")
para(f"The chromagram model alone had the highest test balanced accuracy ({pc(FM['single_chroma']['balanced_accuracy'])} "
     f"percent, 95% CI {FC['single_chroma'][0]*100:.1f}–{FC['single_chroma'][1]*100:.1f}), although it was the weakest "
     f"model on validation ({VAL['single_chroma']['bal_mean']*100:.1f} percent). Because it was not the pre-specified model "
     "and its lead appeared only on test, it is reported as a hypothesis for the local dataset to check, not as a result: "
     "pitch-based features deserve a place in the next round, where they will be chosen on validation alone. Three of the "
     "six retrained runs also did not reproduce their logged validation scores exactly (the MFCC model by +0.7 points, the "
     "spectrogram model by -2.3, and late fusion, which uses it, by -1.5), because neural-network training is not fully "
     "deterministic even with a fixed seed; the test scores above come from the retrained models, and the next round will "
     "enable the library's deterministic mode. "
     "The reference study's 99.1 percent, set beside the "
     f"{min(FM[r]['balanced_accuracy'] for r in FORD)*100:.0f} to {max(FM[r]['balanced_accuracy'] for r in FORD)*100:.0f} "
     "percent range obtained here, shows that the task and the evaluation protocol matter far more than the architecture: "
     "a diagnosis-level task dominated by one class, evaluated without reported patient separation, can yield very high "
     "accuracy that need not carry over to unseen patients.")
para("That verdict held only for ICBHI alone. When the rebalanced paediatric corpus was added, the three-branch fusion "
     "network became the best model on validation, on the single test reading (39.4 percent) and in cross-validation "
     "(40.0 against 34.0 percent; difference 5.9 points, 95 percent CI 1.0 to 10.3, p = 0.008). Fusion therefore helps "
     "once the network has more varied data to learn from, and the fusion network was adopted and placed in the "
     "application on 13 November 2026. The order in which the gains appeared is the lesson: architecture alone moved "
     "little, data moved more, and the data that matter most, Resondi recordings of Filipino patients, are still to be "
     "collected.")
para("These results define the next stage of the work rather than undermining it. Changing the feature "
     "representation and training recipe on ICBHI alone produced no clear gain; the one significant gain, about six points, "
     "came from adding a second corpus to training, while a change of "
     "device or noise level erased the model's skill entirely. The decisive step is therefore a local dataset: Resondi "
     "device recordings of Filipino patients at the seven standard sites, with each breathing cycle labelled independently "
     "by two clinicians blinded to the AI output, with noise augmentation during training and a recording-quality gate "
     "before classification. Until that dataset exists, every AI output must remain a decision-support suggestion "
     "confirmed by a licensed practitioner, and the severity percentage should not be shown as a clinical measure.")
para("The study has several limitations. Thirty-one test patients give wide confidence intervals. The reference corpus "
     "is dominated by adult patients with chronic obstructive pulmonary disease, whereas Resondi targets community and "
     "paediatric use. The noise experiment used synthetic Gaussian noise rather than recorded ward or community noise, "
     "and the earlier field results came from the withdrawn model with no record of reference-label blinding. The ICBHI "
     "test patients were read three times, once per round, each time with the primary model fixed in advance, which the "
     "cross-validation across all 126 patients guards against. Above all, neither the fusion network now in the "
     "application nor any other rebuilt model has been tested on Resondi device recordings with reference labels. The "
     "heart models run in the application but have been tested on CirCor only: not on Resondi heart recordings, not after the cardiologist's review "
     "of their training labels, which is still pending, and, for murmurs, short of the pre-specified sensitivity.")
log("Heart sound component (13 Nov, regional science fair version)", "Results reported the lung component only",
    "New section 'Heart Sound Component: Status' with Figure 15 (the five cardiac sites): Heart Mode implemented; CirCor "
    "public release checked (942 patients, 3,163 recordings, murmur 179/695/68); blinded cardiologist review set prepared, "
    "review pending; murmur classifier not yet trained. Limitations add the unevaluated heart component. The sentence "
    "about 'the work the funding is meant to buy' reworded, as this version is for the regional science and technology "
    "fair and carries no financial requirement.",
    "Requested by the user on 13 Nov: include the heart feature and exclude the financial requirement.")
log("Heart-sound models (14 Nov)", "Heart section reported the acquisition stage only; murmur classifier not yet trained",
    "Section renamed 'Heart Sound Component: Models Tested on CirCor'. New Table 20 and Figure 16: on 189 CirCor test "
    "patients, S1/S2 found within 100 ms 96.8%/97.3%, heart rate mean absolute error 3.0 BPM (95% CI 2.5-3.6); murmur "
    "sensitivity 66.7% (50.0-81.8), short of the pre-specified 80%, specificity 97.1%, AUROC 0.96. Disclosed: trained "
    "before the cardiologist's review; segmentation not yet used by the murmur model; murmur timing, extent score and "
    "recording-level metrics not done; one-seed change. Rationale and limitations updated.",
    "Requested by the user on 14 Nov. Numbers from model-rebuild/results/heart-segmentation.md and heart-murmur.md.")
log("Heart-sound models in the application (14 Nov)", "Models tested on CirCor; application did not classify heart sounds",
    "Results: the models now run in the application (ONNX in the browser, 16 kHz audio decimated to 4 kHz); app-path check "
    "on 631 test recordings (heart-rate error 3.03 vs 3.01 BPM, murmur flag the same on 99.7%); JavaScript matched Python "
    "25/25 in Node.js and 8/8 in a browser. States that the models went into the application before the device test the "
    "plan put first, and that every heart result there is marked as a screening aid. Rationale and limitations updated.",
    "Requested by the user on 14 Nov. Numbers from model-rebuild/results/heart-app-path-check.md and heart-js-parity.json; "
    "app change in app-changes/heart-models-v1.md.")
log("Second training round, cross-validation, deployment (13 Nov)", "Fusion reported as not adopted (ICBHI-only round)",
    "New section 'Adding the Paediatric Corpus, and Cross-Validation': Table 17 (ICBHI + SPRSound test, 39.4% / 57.2%), "
    "Table 18 (5-fold CV, 40.0% vs 34.0%, +5.9 points, p = 0.008), Figures 12-14 made with jamovi (jmv), and the 13 Nov "
    "deployment of the fusion network in the app. Comparison table renumbered 17 -> 19 with three new rows. Discussion: "
    "verdict revised (fusion helps once SPRSound is added), limitations add the three test readings and the untested device.",
    "Requested by the user on 13 Nov. Numbers from model-rebuild/results/final-test-icbhi-sprs.md and cv-results.json; "
    "jamovi output in build/imrad/jamovi-output.txt.")
log("Results and Discussion (new)", "—",
    "Section G with Tables 7–13 and Figures 6–9: field-study results, validation comparison, single test run with bootstrap CIs, "
    "McNemar noise test (H1), H2/H3 status, severity calibration (OLS, VIF, beta regression, RMSE/MAE/R²), Kruskal–Wallis with "
    "DSCF, fusion comparison (Tables 14–17, Figures 10–11: individual models vs late and FDC-FS fusion on the 31 test "
    "patients with bootstrap CIs and Holm-corrected McNemar tests, SPRSound external check, original model and reference "
    "study), discussion and limitations",
    "Requested by the user on 11 Nov. Statistics computed by model-rebuild/scripts/analysis_stats.py and "
    "scripts/fusion_eval.py; jamovi steps in model-rebuild/results/stats/JAMOVI-STEPS.md. Late fusion was fixed as the "
    "primary model on validation before the test patients were read.")

# ======================================================================= BIBLIOGRAPHY
BIB = [
    "[[3M. (2025). 3M Littmann CORE Digital Stethoscope [Product listing]. CONFIRM: add the source of the ₱22,000 price cited in the Rationale.]]",
    "Arts, L., Lim, E. H. T., van de Ven, P. M., Heunks, L., & Tuinman, P. R. (2020). The diagnostic accuracy of lung auscultation in adult patients with acute pulmonary pathologies: A meta-analysis. Scientific Reports, 10, 7347. https://doi.org/10.1038/s41598-020-64405-6",
    "Bohadana, A., Izbicki, G., & Kraman, S. S. (2014). Fundamentals of lung auscultation. New England Journal of Medicine, 370(8), 744–751. https://doi.org/10.1056/NEJMra1302901",
    "Choi, S. I., Jeong, Y., Jung, W. J., Kim, B.-K., Lee, S. Y., Lee, J., Kim, J.-Y., Cho, W.-Y., Chang, [[CONFIRM initials]], An, H., Park, S., & Lee, E. J. (2026). Usefulness of lung sound data collection using Skeeper SM-300® device: A pilot study. PLOS ONE, 21(5), e0348588. https://doi.org/10.1371/journal.pone.0348588",
    "[[DeepRespNet: A deep neural network for classification of respiratory sounds. (2024). Biomedical Signal Processing and Control, 93, 106191. https://doi.org/10.1016/j.bspc.2024.106191 — CONFIRM: add the authors.]]",
    "Global Burden of Disease Collaborative Network. (2025). Global Burden of Disease Study 2023 (GBD 2023) results. Institute for Health Metrics and Evaluation. https://vizhub.healthdata.org/gbd-results/",
    "Global Initiative for Asthma. (2023). Global strategy for asthma management and prevention (2023 update). https://ginasthma.org/gina-reports",
    "Gonzales, A., Custodio, R., Lapitan, M. C., & Ladia, M. A. (2023). End users' perspectives on the quality and design of mHealth technologies during the COVID-19 pandemic in the Philippines: Qualitative study. JMIR Formative Research, 7, e41838. https://doi.org/10.2196/41838",
    "Hajesmaeel-Gohari, S., Khordastan, F., Fatehi, F., Samzadeh, H., & Bahaadinbeigy, K. (2022). The most used questionnaires for evaluating satisfaction, usability, acceptance, and quality outcomes of mobile health. BMC Medical Informatics and Decision Making, 22, 22. https://doi.org/10.1186/s12911-022-01764-2",
    "Holden, R. J., & Karsh, B.-T. (2010). The technology acceptance model: Its past and its future in health care. Journal of Biomedical Informatics, 43(1), 159–172. https://doi.org/10.1016/j.jbi.2009.07.002",
    "Huang, D.-M., Huang, J., Qiao, K., Zhong, N.-S., Lu, H.-Z., & Wang, W.-J. (2023). Deep learning-based lung sound analysis for intelligent stethoscope. Military Medical Research, 10, 44. https://doi.org/10.1186/s40779-023-00479-3",
    "Kim, J.-W., Bae, S., Cho, W.-Y., Lee, B., & Jung, H.-Y. (2024). Stethoscope-guided supervised contrastive learning for cross-domain adaptation on respiratory sound classification. Proceedings of the IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP), 1431–1435. https://doi.org/10.1109/ICASSP48485.2024.10447734",
    "Kim, J.-W., Toikkanen, M., Jalali, A., Kim, M., Han, H.-J., Kim, H., Shin, W., Jung, H.-Y., & Kim, K. (2025). Adaptive metadata-guided supervised contrastive learning for domain adaptation on respiratory sound classification. IEEE Journal of Biomedical and Health Informatics, 29(8), 5381–5393. https://doi.org/10.1109/JBHI.2025.3545159",
    "Kim, T. K. (2015). T test as a parametric statistic. Korean Journal of Anesthesiology, 68(6), 540–546. https://doi.org/10.4097/kjae.2015.68.6.540",
    "Lahham, A., & Holland, A. E. (2021). The need for expanding pulmonary rehabilitation services. Life, 11(11), 1236. https://doi.org/10.3390/life11111236",
    "Leng, S., Tan, R. S., Chai, K. T. C., Wang, C., Ghista, D., & Zhong, L. (2015). The electronic stethoscope. BioMedical Engineering OnLine, 14, 66. https://doi.org/10.1186/s12938-015-0056-y",
    "Oliveira, J., Renna, F., Costa, P. D., Nogueira, M., Oliveira, C., Ferreira, C., Jorge, A., Mattos, S., Hatem, T., Tavares, T., Elola, A., Rad, A. B., Sameni, R., Clifford, G. D., & Coimbra, M. T. (2022). The CirCor DigiScope dataset: From murmur detection to murmur classification. IEEE Journal of Biomedical and Health Informatics, 26(6), 2524–2535. https://doi.org/10.1109/JBHI.2021.3137048",
    "[[Park et al. (2025). CONFIRM: add the full reference for the source cited in the Rationale on autonomous AI interpretation.]]",
    "Philips, A. L., Sodhi, I., Warrier, J., & Sinha, V. (2016). Development of digital stethoscope for telemedicine. https://www.researchgate.net/publication/289489645",
    "Philippine Statistics Authority. (2025a). 2024 causes of death in the Philippines (provisional as of 31 July 2025). https://psa.gov.ph/content/2024-causes-death-philippines-provisional-31-july-2025",
    "Philippine Statistics Authority. (2025b, October 28). 2024 causes of death in the Philippines (provisional as of 31 August 2025). https://psa.gov.ph/system/files/vsd/1_Press%20Release%20_2024%20Cause%20of%20Death%20Statistics_as%20of31%20August%202025_ONS-%20signed.update.pdf",
    "Pramono, R. X. A., Bowyer, S., & Rodriguez-Villegas, E. (2017). Automatic adventitious respiratory sound analysis: A systematic review. PLOS ONE, 12(5), e0177926. https://doi.org/10.1371/journal.pone.0177926",
    "Rocha, B. M., Filos, D., Mendes, L., Vogiatzis, I., Perantoni, E., Kaimakamis, E., Natsiavas, P., Oliveira, A., Jácome, C., Marques, A., Paiva, R. P., Chouvarda, I., Carvalho, P., & Maglaveras, N. (2018). A respiratory sound database for the development of automated classification. In Precision Medicine Powered by pHealth and Connected Health (pp. 51–55). Springer. https://doi.org/10.1007/978-981-10-7419-6_6",
    "Rocha, B. M., Filos, D., Mendes, L., Serbes, G., Ulukaya, S., Kahya, Y. P., Jakovljevic, N., Turukalo, T. L., Vogiatzis, I. M., Perantoni, E., Kaimakamis, E., Natsiavas, P., Oliveira, A., Jácome, C., Marques, A., Maglaveras, N., Paiva, R. P., Chouvarda, I., & de Carvalho, P. (2019). An open access database for the evaluation of respiratory sound classification algorithms. Physiological Measurement, 40(3), 035001. https://doi.org/10.1088/1361-6579/ab03ea",
    "[[Shkarupylo et al. (2024). CONFIRM: add the full reference for the source cited in the Rationale on noise and contact artifacts.]]",
    "Subido-Cariño, M. T., Donadel, M., Asi, L. D., Ariola-Ramos, M. S., Arguelles, V. L., Co, S. N., Mahon, G., Fernandez, S. P. C., Punzalan, K. A., Sornillo, J. B., Smith, R., Westercamp, M., & Hechanova-Cruz, R. A. (2025). SARS-CoV-2 seroprevalence, illness recall, and work absenteeism among healthcare workers: A facility-based cross-sectional study in the Philippines, 2021. Clinical Infectious Diseases, 81(2), 255. https://doi.org/10.1093/cid/ciaf342",
    "Tanaka, T., Yanagita, Y., Morishita, T., Nagata, F., Granados Santiago, M., López-López, L., & Valenza, M. C. (2025). Effectiveness of physical and therapy interventions for non-ICU hospitalized pneumonia patients: A systematic review of randomized controlled trials. Healthcare, 13(12), 1444. https://doi.org/10.3390/healthcare13121444",
    "Tariq, Z., Shah, S. K., & Lee, Y. (2022). Feature-based fusion using CNN for lung and heart sound classification. Sensors, 22(4), 1521. https://doi.org/10.3390/s22041521",
    "Tzeng, J.-T., Li, J.-L., Chen, H.-Y., Huang, C.-H., Chen, C.-H., Fan, C.-Y., Huang, E. P.-C., & Lee, C.-C. (2025). Improving the robustness and clinical applicability of automatic respiratory sound classification using deep learning–based audio enhancement: Algorithm development and validation. JMIR AI, 4, e67239. https://doi.org/10.2196/67239",
    "Wang, Z., & Sun, Z. (2024). Performance evaluation of lung sounds classification using deep learning under variable parameters. EURASIP Journal on Advances in Signal Processing, 2024, 51. https://doi.org/10.1186/s13634-024-01148-w",
    "Wei, T.-J., Hsiung, P.-Y., Liu, J.-H., Lin, T.-C., Kuo, F.-T., & Wu, C.-Y. (2022). Use of electronic auscultation in full personal protective equipment to detect ventilation status in selective lung ventilation: A randomized controlled trial. Frontiers in Medicine, 9, 851395. https://doi.org/10.3389/fmed.2022.851395",
    "Weiskopf, N. G., & Weng, C. (2013). Methods and dimensions of electronic health record data quality assessment: Enabling reuse for clinical research. Journal of the American Medical Informatics Association, 20(1), 144–151. https://doi.org/10.1136/amiajnl-2011-000681",
    "World Health Organization. (2023). Package of interventions for rehabilitation: Module 4. Cardiopulmonary conditions. https://apps.who.int/iris/handle/10665/370395",
    "Xia, T., Han, J., & Mascolo, C. (2022). Exploring machine learning for audio-based respiratory condition screening: A concise review of databases, methods, and open issues. Experimental Biology and Medicine. https://doi.org/10.1177/15353702221115428",
    "Ye, P., Li, Q., Jian, W., Liu, S., Tan, L., Chen, W., Zhang, D., & Zheng, J. (2022). Regularity and mechanism of fake crackle noise in an electronic stethoscope. Frontiers in Physiology, 13, 1079468. https://doi.org/10.3389/fphys.2022.1079468",
    "Yenew, C., et al. (2022). Occupational exposure to infectious diseases among health workers: Effects, managements and recommendations. Journal of Infectious Diseases and Epidemiology, 9, 295.",
    "Yin, Z., Yan, J., Fang, S., Wang, D., & Han, D. (2022). User acceptance of wearable intelligent medical devices through a modified unified theory of acceptance and use of technology. Annals of Translational Medicine, 10(11), 629. https://doi.org/10.21037/atm-21-5510",
    "Zhang, Q., Zhang, J., Yuan, J., Huang, H., Zhang, Y., Zhang, B., Lv, G., Lin, S., Wang, N., Liu, X., Tang, M., Wang, Y., Ma, H., Liu, L., Yuan, S., Zhou, H., Zhao, J., Li, Y., Yin, Y., … Lian, Y. (2022). SPRSound: Open-source SJTU paediatric respiratory sound database. IEEE Transactions on Biomedical Circuits and Systems, 16(5), 867–881. https://doi.org/10.1109/TBCAS.2022.3204910 [[CONFIRM the author list against the article.]]",
]
bib_tpl = P[275]
anchor = P[274]._p
old_bib = [p for p in P[275:] if not p.text.startswith(("PUERTO PRINCESA CITY NATIONAL", "SCIENCE, TECHNOLOGY, ENGINEERING"))]
for entry in BIB:
    para = new_para(anchor, entry, bib_tpl, align=WD_ALIGN_PARAGRAPH.LEFT)
    pf = para.paragraph_format
    pf.left_indent, pf.first_line_indent, pf.space_after = Inches(0.5), Inches(-0.5), Pt(6)
    anchor = para._p
log("Bibliography", "Unsorted; Wang & Sun (2024) listed three times (once as 'Song'); Huang (2023) twice (once as 'Xu'); Rocha (2019) twice; entries split across lines; 'Holden & Ben-Tzion'; '(… in Bing)' tags",
    "Alphabetical APA 7 list, duplicates removed, entries joined; Holden & Karsh (2010); added Arts 2020, Bohadana 2014, Lahham & Holland 2021, Oliveira 2022, Tariq 2022, Zhang 2022 (SPRSound); placeholders for 3M 2025, Park 2025, Shkarupylo 2024",
    "Every in-text citation now has an entry. Three sources cited in the Rationale were never listed and must be supplied by the team (highlighted).")

# ======================================================================= LAYOUT: real page header, no typed headers
hdr_pairs = []
for i, p in enumerate(P):
    if p.text.strip().startswith("PUERTO PRINCESA CITY NATIONAL SCIENCE HIGH SCHOOL"):
        hdr_pairs.append(i)
x0, x1 = copy.deepcopy(P[0]._p), copy.deepcopy(P[1]._p)
footer_xml = [copy.deepcopy(el) for el in D.sections[0].footer._element if el.tag == qn("w:p")]  # holds the PAGE field


def drop(p_el):
    pPr = p_el.find(qn("w:pPr"))
    if pPr is not None and pPr.find(qn("w:sectPr")) is not None:
        for ch in list(p_el):
            if ch.tag != qn("w:pPr"):
                p_el.remove(ch)
    else:
        p_el.getparent().remove(p_el)


for i in hdr_pairs:
    drop(P[i]._p)
    if P[i + 1].text.strip().startswith("SCIENCE, TECHNOLOGY, ENGINEERING"):
        drop(P[i + 1]._p)
for p in old_bib:
    if p._p.getparent() is not None:
        drop(p._p)

# Merge the per-page sections into one, and start the major parts on new pages instead
for p_el in list(D.element.body.iter(qn("w:p"))):
    pPr = p_el.find(qn("w:pPr"))
    if pPr is not None:
        s = pPr.find(qn("w:sectPr"))
        if s is not None:
            pPr.remove(s)
for i in (14, 30, 52, 63, 96, 150, 160, 274):
    P[i].paragraph_format.page_break_before = True
# drop empty paragraphs left directly after removed headers at the top of a page
sec = D.sections[0]
sec.different_first_page_header_footer = False
hdr = sec.header
hdr.is_linked_to_previous = False
for blip in x0.iter(qn("a:blip")):
    part = D.part.related_parts[blip.get(qn("r:embed"))]
    blip.set(qn("r:embed"), hdr.part.relate_to(part, RT.IMAGE))
for el in (x0, x1):
    pPr = el.find(qn("w:pPr"))
    if pPr is not None and pPr.find(qn("w:sectPr")) is not None:
        pPr.remove(pPr.find(qn("w:sectPr")))
for el in list(hdr._element):
    if el.tag == qn("w:p"):
        hdr._element.remove(el)
hdr._element.append(x0)
hdr._element.append(x1)
ftr = sec.footer
ftr.is_linked_to_previous = False
for el in list(ftr._element):
    if el.tag == qn("w:p"):
        ftr._element.remove(el)
for el in footer_xml:
    ftr._element.append(el)
pg = sec._sectPr.find(qn("w:pgNumType"))
if pg is not None:
    sec._sectPr.remove(pg)
sec.header_distance = Inches(0.3)
sec.top_margin = Inches(1.0)
log("Layout", "School header typed into the body at the top of each page (one section per page)",
    "Header moved into the real page header; single section; major parts start on a new page",
    "With tables and figures added, typed headers would have landed mid-page.")

D.core_properties.title = "Resondi Research Plan (revised 11 November 2026)"
D.save(OUT)
print("wrote", OUT)

# ======================================================================= REVISION LOG
L = docx.Document()
st = L.styles["Normal"]
st.font.name, st.font.size = "Times New Roman", Pt(10)
for s in L.sections:
    s.left_margin = s.right_margin = Inches(0.7)
    s.top_margin = s.bottom_margin = Inches(0.7)
L.add_heading("Resondi Research Plan: Revision Log (11 November 2026)", level=1)
L.add_paragraph("Source: Resondi-Research-Plan-Revised.docx (Google Drive, last modified 11 Nov 2026). Revised copy: "
                "Resondi-Research-Plan-Revised-Heart-and-Lung-2026-11-13.docx. The original was not edited. Results and Discussion are "
                "not part of this revision: the fusion model is still training. Yellow highlights in the revised plan "
                "mark facts only the team can confirm.")
tb = L.add_table(rows=1, cols=5)
tb.style = "Table Grid"
for j, h in enumerate(["#", "Section", "Original", "Revised", "Reason"]):
    tb.rows[0].cells[j].text = h
    tb.rows[0].cells[j].paragraphs[0].runs[0].bold = True
for k, (sct, was, now, why) in enumerate(LOG, 1):
    cells = tb.add_row().cells
    for j, v in enumerate([str(k), sct, was, now, why]):
        cells[j].text = v
for row in tb.rows:
    for j, w in enumerate([0.3, 1.2, 1.9, 2.1, 1.9]):
        row.cells[j].width = Inches(w)
L.add_heading("For the team to confirm (highlighted in the plan)", level=2)
for t in ["Full references for 3M (2025), Park et al. (2025) and Shkarupylo et al. (2024), cited in the Rationale.",
          "Authors of the DeepRespNet (2024) article; the missing initials of 'Chang' in Choi et al. (2026); the SPRSound author list.",
          "Which PSA release (2025a or 2025b) gives the 701,884 total; the plan now cites 2025b.",
          "Research question 9 lists user-friendliness, usability, durability, functionality and perceived usefulness, but the survey "
          "actually run (n = 27) used UTAUT constructs, including facilitating conditions. Align the question with the instrument used.",
          "The fusion design in Table 4 and Figure 4 follows the training script now running (three branches, concatenation, dense). "
          "If the final model differs, update both."]:
    L.add_paragraph(t, style="List Bullet")
L.save(LOGF)
print("wrote", LOGF, len(LOG), "edits")
