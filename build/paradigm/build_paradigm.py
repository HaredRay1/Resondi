"""Research Paradigm section for Resondi, Chapter 2 — cardiopulmonary scope.

Built to the PPCNSHS template: an Input-Process-Output table captioned as a
figure, followed by an orienting paragraph and one paragraph per column.
Respiratory items trace to analyses already run in the research plan; the
cardiac items mirror them one for one so every heart variable has a matching
process and output.
"""
import os as _os
_BUILD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))).replace(chr(92), '/')
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

FONT = "Times New Roman"

INPUT = [
    "Specifications of the Resondi device and platform — hardware components, "
    "cost of materials, electrical requirements, graphical user interface, "
    "role-based access control, and data management processes",
    "Respiratory sound recordings — the ICBHI 2017 Respiratory Sound Database "
    "as the reference dataset, and recordings captured on Resondi hardware at "
    "six standardized lung auscultation locations",
    "Heart sound recordings — the CirCor DigiScope Phonocardiogram Dataset as "
    "the reference dataset, and recordings captured on Resondi hardware at the "
    "four cardiac valve auscultation points together with Erb’s point",
    "Recording quality indicators — signal-to-noise ratio, clarity ratings, and "
    "ambient noise levels measured in both lung and heart modes across three "
    "testing environments",
    "System response times across smart-stethoscope connection, sound "
    "recording, recording-quality assessment, signal preprocessing, and "
    "classification output",
    "Classification outputs — respiratory patterns of normal, wheeze, crackle, "
    "and combined wheeze-and-crackle, and cardiac patterns of normal and "
    "murmur — from both reference and Resondi recordings",
    "End-user acceptance and preference ratings from thirty participants "
    "across Puerto Princesa City and three patients at a private hospital",
]

PROCESS = [
    "Design and development of the Resondi smart stethoscope and "
    "cardiopulmonary monitoring platform — acoustic chest piece, microphone and "
    "preamplifier, ESP32 microcontroller, Bluetooth Low Energy, and a mobile "
    "application providing separate lung and heart auscultation modes",
    "Audio preprocessing — noise reduction, filtering, segmentation, and "
    "Mel-spectrogram representation, with band-pass parameters set to the "
    "frequency range of each mode",
    "Convolutional neural network training and classification of respiratory "
    "sound patterns and of heart sound patterns",
    "Descriptive analysis of device and system specifications through "
    "specification tables, system architecture and workflow diagrams, "
    "screenshots, and narrative description",
    "Statistical treatment — mean, standard deviation, and weighted mean; "
    "paired-samples t-test at the 0.05 level of significance; and McNemar’s "
    "exact test on the distribution of classification errors",
    "Interpretation of end-user ratings against the established five-point "
    "Likert acceptance scale",
]

OUTPUT = [
    "A developed and documented Resondi smart stethoscope and cardiopulmonary "
    "monitoring platform with guided auscultation at six standardized lung "
    "locations and at the cardiac valve points",
    "Determined recording quality and measured system response times in both "
    "lung and heart modes across the major system operations",
    "Established classification performance of the model for respiratory and "
    "for heart sound patterns, and the level of agreement between the "
    "reference and Resondi classification outputs",
    "Determined comparative recording quality between the conventional "
    "stethoscope and the Resondi device",
    "Assessed level of end-user acceptance and the most preferred "
    "instructional and navigation features of the system",
]

doc = Document()
st = doc.styles["Normal"]
st.font.name = FONT
st.font.size = Pt(12)
st.paragraph_format.space_after = Pt(0)

sec = doc.sections[0]
sec.left_margin = sec.right_margin = Inches(1)
sec.top_margin = Inches(0.9)
sec.bottom_margin = Inches(0.9)


def para(text, *, first=0.5, after=12, size=12):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Inches(first)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 2.0
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.font.name = FONT
    return p


# ── heading ──────────────────────────────────────────────────────────────
h = doc.add_paragraph()
h.paragraph_format.space_after = Pt(12)
hr = h.add_run("Research Paradigm")
hr.bold = True
hr.font.size = Pt(12)
hr.font.name = FONT

para("The research framework is based on the theories and models discussed in "
     "the theoretical framework and the review of related literature, from "
     "which the statements of the problem were crafted. The paradigm follows "
     "the Input–Process–Output model, in which the variables gathered by the "
     "study form the input, the developmental and statistical procedures "
     "applied to them form the process, and the findings that answer each "
     "statement of the problem form the output.")

# ── IPO table ────────────────────────────────────────────────────────────
tbl = doc.add_table(rows=2, cols=3)
tbl.style = "Table Grid"
tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

for i, head in enumerate(("INPUT", "PROCESS", "OUTPUT")):
    cell = tbl.rows[0].cells[i]
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(head)
    r.bold = True
    r.font.size = Pt(11)
    r.font.name = FONT

for i, items in enumerate((INPUT, PROCESS, OUTPUT)):
    cell = tbl.rows[1].cells[i]
    cell.text = ""
    for k, item in enumerate(items):
        p = cell.paragraphs[0] if k == 0 else cell.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(f"{k + 1}. {item}")
        r.font.size = Pt(9)
        r.font.name = FONT

for row in tbl.rows:
    for c in row.cells:
        c.width = Inches(2.17)

cap = doc.add_paragraph()
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.paragraph_format.space_before = Pt(10)
cap.paragraph_format.space_after = Pt(14)
cr = cap.add_run("Figure N. The Conceptual Framework and Paradigm of the Study")
cr.font.size = Pt(11)
cr.font.name = FONT

# ── explanation ──────────────────────────────────────────────────────────
para("Figure N represents the conceptual model of this study. The model was "
     "designed using the research questions and the objectives of the study. "
     "It has three parts — the input, the process, and the output — and each "
     "corresponds to the defined statements of the problem and to the models "
     "and theories adopted in the theoretical framework.")

para("For the input part, it includes the variables of the study. These are "
     "the specifications of the Resondi device and platform, covering the "
     "hardware components, cost of materials, electrical requirements, "
     "graphical user interface, role-based access control, and data "
     "management processes; the respiratory sound recordings, drawn both from "
     "the ICBHI 2017 Respiratory Sound Database as the reference dataset and "
     "from recordings captured on Resondi hardware at six standardized lung "
     "auscultation locations; the heart sound recordings, drawn both from the "
     "CirCor DigiScope Phonocardiogram Dataset as the reference dataset and "
     "from recordings captured on Resondi hardware at the four cardiac valve "
     "auscultation points together with Erb’s point; the recording quality "
     "indicators of signal-to-noise ratio, clarity ratings, and ambient noise "
     "levels measured in both modes across three testing environments; the "
     "system response times recorded across smart-stethoscope connection, "
     "sound recording, recording-quality assessment, signal preprocessing, "
     "and classification output; the classification outputs of the model into "
     "respiratory patterns of normal, wheeze, crackle, and combined "
     "wheeze-and-crackle, and into cardiac patterns of normal and murmur; and "
     "the end-user acceptance and preference ratings gathered from thirty "
     "participants across Puerto Princesa City and three patients at a "
     "private hospital.")

para("For the process part, it contains the developmental and analytical "
     "methods applied to those variables. These are the design and "
     "development of the smart stethoscope and the cardiopulmonary monitoring "
     "platform, integrating the acoustic chest piece, microphone and "
     "preamplifier, ESP32 microcontroller, Bluetooth Low Energy "
     "communication, and a mobile application that provides separate lung and "
     "heart auscultation modes; the audio preprocessing pipeline of noise "
     "reduction, filtering, segmentation, and Mel-spectrogram representation, "
     "in which the band-pass parameters are set to the frequency range proper "
     "to each mode, since heart sounds occupy a lower band than lung sounds; "
     "the training of the convolutional neural network and its classification "
     "of the respiratory and the heart sound patterns; the descriptive "
     "analysis of device and system specifications through specification "
     "tables, system architecture and workflow diagrams, screenshots, and "
     "narrative description; the statistical treatment of the gathered data "
     "using mean, standard deviation, and weighted mean, the paired-samples "
     "t-test at the 0.05 level of significance, and McNemar’s exact test on "
     "the distribution of classification errors; and the interpretation of "
     "the end-user ratings against the established five-point Likert "
     "acceptance scale.")

para("For the output part, it contains the outcomes of the processed "
     "variables. These are a developed and documented Resondi smart "
     "stethoscope and cardiopulmonary monitoring platform with guided "
     "auscultation at six standardized lung locations and at the cardiac "
     "valve points; the determined recording quality and the measured system "
     "response times in both modes across the major system operations; the "
     "established classification performance of the model for respiratory and "
     "for heart sound patterns, together with the level of agreement between "
     "the reference and Resondi classification outputs; the determined "
     "comparative recording quality between the conventional stethoscope and "
     "the Resondi device; and the assessed level of end-user acceptance "
     "together with the most preferred instructional and navigation features "
     "of the system.")

para("This model identifies the contribution of each variable as outlined "
     "above. The device specifications, the recording quality indicators, the "
     "respiratory and cardiac classification outputs, and the end-user "
     "evaluations were examined in this study in response to the statements "
     "of the problem, and the outputs that result from them establish the "
     "feasibility of the proposed system as a supportive tool for "
     "cardiopulmonary assessment and professional review.")

doc.save(_BUILD + "/paradigm/Resondi-Research-Paradigm.docx")
print("saved")
