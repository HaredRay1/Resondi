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
from docx.enum.table import WD_TABLE_ALIGNMENT
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
    para(t.upper(), after=10, before=18, first=0, align=WD_ALIGN_PARAGRAPH.CENTER,
         size=12, bold=True, spacing=2.0)


def H2(t):
    para(t, after=8, before=12, first=0, size=12, bold=True, spacing=2.0)


def FILL(p, text):
    r = p.add_run("  [[TO FILL: " + text + "]]")
    r.italic = True
    r.font.size, r.font.name = Pt(11), FONT
    r.font.color.rgb = ROSE


HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "..", "..", "figures") + os.sep


_N = {"fig": 0, "tab": 0}


def FIG(num, caption, fname, width_in=6.0, note=None):
    """Centred figure with a numbered caption beneath it. Numbers are assigned in order;
    the num argument is ignored except for the lettered companion figure "1b"."""
    if num != "1b":
        _N["fig"] += 1
        num = _N["fig"]
    from docx.shared import Inches as _In
    from PIL import Image as _Img
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(14); p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.0
    path = FIGDIR + fname
    im = _Img.open(path)
    p.add_run().add_picture(path, width=_In(width_in),
                            height=_In(width_in * im.height / im.width))
    c = doc.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.paragraph_format.space_after = Pt(4); c.paragraph_format.line_spacing = 1.0
    r = c.add_run(f"Figure {num}. "); r.bold = True
    r.font.size, r.font.name = Pt(10.5), FONT
    r = c.add_run(caption); r.italic = True
    r.font.size, r.font.name = Pt(10.5), FONT
    if note:
        para(note, after=10, before=2, first=0, align=WD_ALIGN_PARAGRAPH.CENTER,
             size=9.5, italic=True, color=GREY, spacing=1.0)
    else:
        para("", after=8, first=0, spacing=1.0)


def TBL(num, caption, rows, widths, note=None):
    _N["tab"] += 1
    num = _N["tab"]
    para(f"Table {num}", after=0, before=14, first=0,
         align=WD_ALIGN_PARAGRAPH.LEFT, bold=True, spacing=1.0)
    para(caption, after=6, first=0, align=WD_ALIGN_PARAGRAPH.LEFT,
         italic=True, spacing=1.0)
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = t.cell(i, j)
            cell.width = Inches(widths[j])
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run(str(val))
            r.bold = (i == 0)
            r.font.size, r.font.name = Pt(10.5), FONT
    for row in t.rows:
        for j, w in enumerate(widths):
            row.cells[j].width = Inches(w)
    if note:
        para(note, after=8, before=4, first=0, align=WD_ALIGN_PARAGRAPH.LEFT,
             size=10, italic=True, color=GREY, spacing=1.0)
    else:
        para("", after=4, first=0, spacing=1.0)



# ═══════════════════════════════════════════════════ TITLE
para("Resondi: A CNN-Assisted Smart Stethoscope for Lung and Heart Sound "
     "Monitoring, Longitudinal Tracking, and Rehabilitation Support",
     after=8, first=0, align=WD_ALIGN_PARAGRAPH.CENTER, size=14, bold=True,
     spacing=1.4)
para("Ahnycca Krish N. Malimban",
     after=4, first=0, align=WD_ALIGN_PARAGRAPH.CENTER, spacing=1.2)
para("Science, Technology, Engineering and Mathematics — Senior High School\nPuerto Princesa City National Science High School, Palawan",
     after=16, first=0, align=WD_ALIGN_PARAGRAPH.CENTER, italic=True, spacing=1.2)

# ═══════════════════════════════════════════════════ ABSTRACT
H1("Abstract")
para("Auscultation is the first examination most Filipino patients with heart or lung "
     "disease receive, but a conventional stethoscope keeps no record, so a lung sound "
     "cannot be reviewed by a second clinician or compared with the same site at a later "
     "visit. This study developed Resondi, a low-cost smart stethoscope that records lung "
     "sounds at seven guided sites, files each recording by site, classifies it into four "
     "sound patterns with a convolutional neural network, and routes every result to a "
     "practitioner for confirmation. A Heart Mode guides recording at five cardiac sites, "
     "the four valve points and Erb's point, and stores each heart recording for "
     "practitioner review. In field testing in Puerto Princesa City, the device "
     "produced a signal about 13 dB stronger than a conventional stethoscope (45 dB against "
     "32 dB), 93 percent of recordings were rated good or acceptable, and the original "
     "classifier agreed with reference labels on 6 of 15 recordings (40 percent; 95 percent "
     "CI 19.8–64.3; p = 0.148 against 25 percent chance). That classifier was later found "
     "to have been trained on leaked data, and was rebuilt with sound-based labels and a "
     "patient-wise split. In five-fold cross-validation across all 126 ICBHI 2017 patients, "
     "a three-branch feature-fusion network trained with the SPRSound paediatric corpus "
     "reached 40.0 percent balanced accuracy against 34.0 percent for the original design, a "
     "significant gain of 5.9 points (95 percent CI 1.0–10.3; p = 0.008). The fusion "
     "network now runs in the Resondi application; on 26 recordings made with the device it "
     "gave clearer top-class scores than the build it replaced (median 41 percent, against "
     "27 to 34 percent), but those recordings carry no reference labels, so its accuracy "
     "on the device has not been measured. Resondi is "
     "established as a working acquisition platform; validating its classifier on "
     "clinician-labelled Filipino recordings is the next step. Heart sounds are recorded "
     "but not yet classified: a heart-murmur classifier has been specified on the CirCor "
     "DigiScope dataset, and a blinded review of 25 of its recordings by a cardiologist has "
     "been prepared to check its labels before training.", first=0, spacing=1.6)
para("Keywords: auscultation, lung sounds, heart sounds, smart stethoscope, convolutional neural "
     "network, feature fusion, primary care, Philippines", first=0, italic=True, spacing=1.6)

# ═══════════════════════════════════════════════════ INTRODUCTION
H1("Introduction")

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

H2("The Research Gap")
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
     "AI-supported analysis. The performance figures above are therefore properties of a "
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
    ("To prepare AI-assisted detection of heart murmurs.",
     "A heart-sound classifier is specified to report whether a murmur is present and "
     "when in the cardiac cycle it occurs, trained on expert-annotated public recordings "
     "whose labels are first checked by a cardiologist."),
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

H2("Scope and Delimitation")
para("This study covers lung and heart sounds, at different stages. Lung sounds are "
     "recorded, classified and evaluated. Heart sounds are recorded at five sites and "
     "stored for practitioner review; a heart-murmur classifier is specified and its "
     "training data prepared, but it has not been trained or evaluated, and no heart "
     "recording is passed to the lung classifier. Lung classification is limited to four "
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

# ═══════════════════════════════════════════════════ METHODOLOGY
H1("Methodology")

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
p = para("", first=0, after=4, spacing=1.0)
FILL(p, "confirm this is the term your institution uses. Developmental-descriptive "
        "is accurate for what was done and is standard in Philippine senior high "
        "school research; some programmes say research and development (R&D) or "
        "design and development research (DDR) instead. Do not let it be called "
        "experimental \u2014 there is no manipulated variable and no control group")

H2("Device Development")
para("The device pairs a conventional acoustic chest piece and silicone tubing with a "
     "microphone and preamplifier, an ESP32 "
     "microcontroller, Bluetooth Low Energy communication, MicroSD storage, a 20 × 4 "
     "character LCD for device status, and a 10,000 mAh power bank. The assembly is housed "
     "in a 3D-printed polylactic acid casing. All results reported here were obtained with "
     "that build.", first=0)
para("The device has since been revised as enclosure version 2.0, which was not used in "
     "this evaluation: the INMP441 digital microphone is read over I²S with no analogue "
     "preamplifier, and Bluetooth is replaced by a Wi-Fi access "
     "point through which a browser connects to the device directly. Whether the revised "
     "build changes recording quality has not yet been measured.", first=0)

FIG(1, "The Resondi Smart Stethoscope, with Components Identified",
    "d6_device.png", 6.05,
    note="The enclosure houses the microphone and preamplifier, the ESP32 "
         "with Bluetooth Low Energy, MicroSD storage, and the lithium-ion "
         "cell with its charging and protection circuitry.")

FIG("1b", "Concept Render of the Version 2.0 Enclosure", "Resondi-Device-3D.png", 5.2,
    note="Rendered from the team's Blender model. Proportions and colours are illustrative, "
         "and no result in this paper was obtained on this build.")

p = para("The microphone was selected for unit-to-unit consistency of frequency "
         "response. Because the system's central claim is that a recording taken at "
         "one visit can be compared against the same site at a later visit, variation "
         "in transducer response between devices would introduce drift into precisely "
         "the measurement the system exists to make.", first=0)
FILL(p, "name the microphone part. Earlier project documentation cites both an "
        "INMP441 (a MEMS microphone) and a MAX4466 (an electret amplifier board); "
        "these are different components and only one is in the build. The "
        "consistency argument above holds either way, but the part must be named "
        "for the device to be reproducible")

p = para("The microcontroller samples the preamplified acoustic signal, writes the "
         "recording to MicroSD together with its metadata — anatomical site, timestamp, "
         "and duration \u2014 in WAV format, and advertises over Bluetooth Low Energy. Two "
         "storage paths "
         "operate in parallel: recordings transfer to the paired mobile application "
         "where a phone is present, and are retained on MicroSD for later transfer where "
         "it is not. Capture therefore does not depend on connectivity.", first=0)
FILL(p, "bit depth and the segment length used at segmentation. The paper gives the "
        "16 kHz rate and WAV format but not these two")

FIG(2, "Hardware Architecture of the Device",
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
    "d2_seven_sites.png", 6.0)

para("Heart Mode uses the same device and recording settings with a separate guided "
     "sequence of five sites, recorded from the base of the heart to the apex: the aortic "
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
    "h1_heart_sites.png", 5.2,
    note="Numbered in recording order, from the base of the heart to the apex. Erb's point "
         "(3) is filed for the practitioner and is not part of the planned classifier input.")

H2("Signal Processing and Model Architecture")
para("Each raw WAV recording is resampled to 16 kHz to provide a consistent rate for "
     "processing, then passes through noise reduction to suppress background "
     "interference, amplitude normalisation to standardise level, and segmentation into "
     "fixed-length segments. Each segment is divided into short frames, transformed by "
     "Short-Time Fourier Transform, passed through a mel-scale filterbank, and reduced "
     "by a discrete cosine transform to mel-frequency cepstral coefficients (MFCCs), "
     "which form the input to the classifier. The parameters are given below.", first=0)

FIG(4, "Audio Preprocessing Applied to Every Recording",
    "d3_preprocess.png", 6.05)

p = para("The classifier is a convolutional neural network taking the MFCC sequence as "
         "its single input. Convolutional layers extract local patterns from the "
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
     "result is flattened into a four-unit softmax output layer. Training used the "
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
p = para("", first=0, after=4, spacing=1.0)
FILL(p, "state the loss function. The architecture terminates in a softmax over four "
        "classes, so categorical cross-entropy is near certain, but confirm it by "
        "scrolling the expert-mode editor past the optimiser definition")

FIG(5, "Classification Model Architecture",
    "d4_classifier.png", 6.05)

para("A rule-based interpretation layer operates above the classifier. Per-zone "
         "classifications are mapped by six explicit rules to a literature-supported "
         "possibility \u2014 for example, all zones healthy, a bilateral upper-zone wheeze "
         "component, or crackles in one or both lower zones \u2014 each accompanied by its "
         "supporting source. Patterns matching none of the defined rules default to a "
         "recommendation for further clinical evaluation. All outputs are framed as "
         "possibilities requiring clinical evaluation and none is presented as a "
         "diagnosis.", first=0)
FILL(p, "the interpretation rules operate on four zones (upper left, upper right, lower "
        "left, lower right) while recording yields six classified lung fields plus the "
        "tracheal reference. State how the six fields map onto the four zones the rules "
        "evaluate, in particular where the two mid-axillary sites are assigned")

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
     "feature-fusion network after Tariq et al. (2022). The same window is represented "
     "three ways: as 13 MFCCs, as a log-power spectrogram from 0 to 4 kHz (129 bins, "
     "20 ms frames), and as a 12-bin chromagram from 50 to 4,000 Hz (64 ms frames). Each "
     "representation passes through its own convolutional branch; the three 64-unit "
     "outputs are concatenated and passed to a dense layer and a four-class softmax "
     "output, about 190,000 parameters in total.", first=0)
FIG(7, "The Three-Branch Feature-Fusion Classifier as Built",
    "p2_fusion.png", 6.05,
    note="The diagram was drawn when this design was planned. The built version uses a "
         "log-power spectrogram in the first branch.")
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

H2("Heart Sound Component")
para("Heart recordings are not classified in the system reported here. The cardiac "
     "classifier is specified to follow the same discipline as the lung classifier, an "
     "acoustic description and never a diagnosis. The planned output, in order of build, is "
     "that the first and second heart sounds (S1 and S2) are identified and timed, that a "
     "murmur is reported as present or absent, and that a present murmur is placed as "
     "systolic or diastolic, with a recording-quality gate in front. Third and fourth heart "
     "sounds (S3 and S4) are named but not promised, because no public dataset labels "
     "them in enough patients to train on.", first=0)
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
para("The planned evaluation divides CirCor by patient, as for the lung data, and reports "
     "sensitivity, specificity, F1-score, Cohen's kappa and the confusion matrix at the "
     "patient level, a murmur counting as present when it is detected at any site. Because "
     "a missed murmur costs more than an unnecessary referral, sensitivity is the primary "
     "criterion: the decision threshold will be set on the validation patients to reach a "
     "pre-specified sensitivity, and the specificity that results will be reported as the "
     "cost of that choice. S1 and S2 timing will be scored separately against the reference "
     "boundaries, as the mean absolute error in milliseconds.", first=0)
para("Before training, the dataset's labels are being checked against an independent "
     "listener. Twenty-five CirCor recordings were drawn at random with a fixed seed, five "
     "from each of five groups: no murmur, holosystolic, early-systolic, mid-systolic, and "
     "diastolic murmur. They were renamed S01 to S25 in mixed order and given to a reviewing "
     "cardiologist with an answer sheet asking, for each recording, whether it is usable, "
     "whether a murmur is heard, its timing, its grade, and the reviewer's confidence. The "
     "dataset's own labels are held separately and are not shown to the reviewer, so the "
     "comparison tests the labels the classifier will learn from.", first=0)
p = para("Fundamental heart sounds lie lower in frequency than lung sounds, with most S1 and "
         "S2 energy below about 150 Hz. The digital microphone in the version 2.0 build is "
         "specified by its manufacturer from about 60 Hz upward, so the low end of the heart "
         "sound band may be attenuated. Before any cardiac result is reported, the frequency "
         "response of the whole acquisition chain will be measured with swept tones from "
         "20 Hz to 2,000 Hz, and any low-frequency loss will be reported as a hardware "
         "limitation rather than attributed to the classifier.", first=0)
FILL(p, "confirm the microphone's specified low-frequency limit from its datasheet, and "
        "whether the field build used the same microphone")

H2("Evaluation Procedures")
para("Before analysis, each recording was assessed where technically possible for "
     "background noise, signal amplitude, signal-to-noise ratio, duration, clipping, "
     "motion artifact, missing or invalid samples, and insufficient signal, and "
     "classified as Good, Acceptable, Poor, or Invalid. Poor or invalid recordings were "
     "recommended for repetition rather than forced into a classification. Reference "
     "recordings were additionally reviewed by three pulmonologists, one of whom is also "
     "a practising pediatrician, so that classifications could be checked against expert "
     "clinical judgement across adult and pediatric presentations. Reference labels were "
     "stored separately from model predictions.", first=0)

para("Six procedures were carried out with the completed prototype.", first=0, after=6)

p = para("Signal acquisition. Mean signal strength produced by the device was compared "
         "against that of a conventional acoustic stethoscope recorded under the same "
         "conditions.", first=0, after=6, spacing=1.6)
FILL(p, "the measurement unit, the reference level if the figures are in decibels, the "
        "make and model of the comparator stethoscope, and how the acoustic output of "
        "an acoustic stethoscope was captured for measurement")

para("Recording clarity. Recordings acquired with a conventional stethoscope and with "
     "Resondi were evaluated by qualified healthcare professionals against predetermined "
     "recording-quality criteria, and rated good, acceptable, or poor.", first=0,
     after=2, spacing=1.6)
p = para("", first=0, after=6, spacing=1.6)
FILL(p, "how many qualified healthcare professionals rated the recordings, and "
        "whether inter-rater agreement was assessed. The criteria are documented; the "
        "raters are not")

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
FILL(p, "state whether the three reviewing pulmonologists were blinded to the model "
        "output when assigning reference labels. If the labels were assigned before the "
        "model was trained, say so \u2014 chronology establishes blinding and is the "
        "strongest form of it. Note also that the full paper\u2019s Data Analysis section "
        "describes this as a comparison between \u2018the two sources of respiratory-sound "
        "recordings\u2019, which reads as a device comparison rather than a test of "
        "classifier accuracy. Correct that wording in the full paper so the two agree")

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
         "Princesa City using a questionnaire adapted from the Unified Theory of Acceptance "
         "and Use of Technology (Venkatesh, Morris, Davis, & Davis, 2003), together with "
         "three patients at a private hospital under the supervision of an attending "
         "physician who reviewed and consented to the procedure. Items were rated on a "
         "five-point Likert scale and grouped into four constructs \u2014 performance "
         "expectancy, effort expectancy, social influence and facilitating conditions "
         "\u2014 together with a fifth group assessing the degree to which conformity with "
         "recognised medical-device standards (ISO 13485, ISO 14971, ISO/IEC 62304, ISO/IEC "
         "27001 and ISO 14155) influenced confidence in the device, reported here as "
         "facilitating conditions. Weighted mean, standard deviation and Cronbach\u2019s alpha "
         "were computed for each construct and interpreted against the five-point "
         "acceptance scale. Three items used a dichotomous response format and are reported "
         "as frequencies rather than means. Three behavioural-intention items and all "
         "open-ended items returned no responses and are not reported.",
         first=0, after=6, spacing=1.6)
FILL(p, "sampling method and inclusion criteria for the 27 respondents. The instrument is "
        "documented; how respondents were recruited is not")

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
p = para("", first=0, after=4, spacing=1.0)
FILL(p, "the full paper's Data Analysis section specifies a paired-samples t-test for "
        "three comparisons on class labels and quality grades. A t-test operates on means "
        "of continuous data and is not valid on those, so correct the full paper to match "
        "what is stated here")

H2("Ethical Considerations")
para("The study was conducted under the supervision of the research adviser of the "
     "Puerto Princesa City National Science High School research programme. "
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

p = para("Formal review by an institutional ethics committee was not obtained for the "
         "work reported here. The safeguards described above \u2014 adviser supervision, "
         "written informed consent, physician supervision of all patient recordings, and "
         "de-identified storage \u2014 were the measures in place. Ethics committee review is "
         "part of the clinical validation planned for the next phase, and prospective "
         "evaluation in a health facility will not proceed without it.",
         first=0)
FILL(p, "this paragraph states plainly that no ethics committee review was obtained, "
        "which is the defensible position if that is accurate. If any body did approve "
        "the study \u2014 a school research committee, the partner hospital, or the "
        "Provincial Health Office \u2014 name it and the approval date here instead, and "
        "delete the first sentence. Do not describe physician supervision as ethics "
        "approval; a research panel will distinguish them")


# ═══════════════════════════════════════════════════ RESULTS
H1("Results")

para("Findings are reported in the order the evaluation procedures were carried out. "
     "The classification result is the weakest of the five and is stated without "
     "qualification.", first=0)

H2("Signal Acquisition")
para("Mean signal strength measured approximately 45 dB for Resondi against "
     "approximately 32 dB for a conventional acoustic stethoscope recorded under "
     "the same conditions. Because the decibel scale is logarithmic, the 13 dB "
     "difference corresponds to roughly 4.5 times the sound-pressure amplitude; it "
     "is not a ratio of the decibel values themselves. Signal strength alone does "
     "not establish better clinical performance; recording quality and "
     "classification accuracy bear on that separately.", first=0)

H2("Recording Clarity")
FIG(7, "Distribution of Recording Clarity Ratings",
    "r1_clarity.png", 5.7)

H2("Ambient Noise Conditions")
FIG(8, "Ambient Noise Levels Across Three Recording Environments",
    "r2_noise.png", 5.7)

H2("System Response Time")
FIG(9, "Mean Duration of Each Processing Stage",
    "r3_response.png", 5.9)

H2("Classification Agreement")
para("Of fifteen recordings compared against reference labels, six produced matching "
     "classifications, an agreement of 40 percent with a 95 percent Wilson score interval "
     "of 19.8 to 64.3 percent. That interval contains both the 25 percent agreement "
     "expected by chance across four categories and a usefully performing classifier, and "
     "the present sample cannot distinguish between them. An exact binomial test against "
     "chance returned p = 0.148; eight of fifteen agreements would have been required to "
     "reach conventional significance. Fifteen recordings is too small a sample to support "
     "a conclusion about accuracy, and none is drawn here. These fifteen recordings were "
     "classified by the original model. The rebuilt models reported below were "
     "not scored against these reference labels.", first=0)

FIG(10, "Classification Agreement Against Reference Labels, with the 95% "
        "Wilson Interval", "r4_agreement.png", 5.7)

H2("End-User Acceptance")
para("Twenty-seven respondents completed the acceptance questionnaire: 13 patients, "
     "13 general respondents and one health practitioner. Across the twelve five-point "
     "Likert items, overall acceptance was 3.95, interpreted as Agree.", first=0)

para("Performance expectancy and effort expectancy each returned a weighted mean of "
     "4.09 (SD = 0.59 and 0.60 respectively), both interpreted as Agree. Facilitating "
     "conditions returned 3.84 (SD = 0.61) and social influence 3.63 (SD = 1.21), "
     "likewise interpreted as Agree.")

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
FILL(p, "confirm whether the three patients recorded at the private hospital are "
        "distinct from the 13 respondents who identified themselves as patients in the "
        "acceptance questionnaire. The two groups are currently described separately")

H2("Heart Mode")
para("Heart Mode was implemented on the device and in the application. It guides the "
     "operator through the five cardiac sites in order, records 15 seconds at each in the "
     "same 16 kHz WAV format as lung recordings, and files each recording by site for "
     "practitioner review, with no classification applied. No quantitative evaluation of "
     "heart recordings was carried out in this study: signal strength, recording clarity "
     "and classification agreement were measured on lung recordings only. The CirCor "
     "training data were obtained and checked, and the blinded review set for the "
     "cardiologist was prepared; the review had not been returned when this paper was "
     "written.", first=0)

H2("Rebuilt Classifier: Pre-Specified Test")
para("Table 2 gives the rebuilt models' scores on the 31 ICBHI test patients, none of "
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

H2("Rebuilt Classifier: Cross-Validation Across All 126 Patients")
para("Because 31 test patients give wide intervals, the two architectures were also "
     "compared by five-fold cross-validation, in which each of the 126 ICBHI patients and "
     "6,898 cycles was classified once by a model that had not seen that patient. Table 3 "
     "gives the result. The fusion network trained with SPRSound reached 40.0 percent "
     "balanced accuracy against 34.0 percent for the app's MFCC design. The paired "
     "difference was 5.9 percentage points (95 percent CI 1.0 to 10.3; one-sided "
     "p = 0.008), and the fusion network scored higher on 14 of the 15 seed-and-fold "
     "comparisons, the fifteenth being a tie. It improved recall on every class (Table 3). "
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
     "t(4) = 4.75, p = 0.009; Figure 13). Of the 126 patients, 69 had more of their cycles "
     "classified correctly by the fusion network, 39 fewer, and 18 the same (Wilcoxon "
     "signed-rank p = 0.009; Figure 14). Cycle by cycle, the fusion network alone was "
     "right on 1,277 cycles and the MFCC network alone on 831 (McNemar p < 0.001), though "
     "this last test treats cycles as independent and overstates the certainty; the "
     "patient-level analyses are the ones to rely on. Figure 15 shows where each model's "
     "errors fall.", first=0)
FIG(13, "Balanced Accuracy of the Two Architectures in Each of the Five Folds",
    "j1_cv_folds.png", 5.6,
    note="Produced in jamovi (jmv, paired-samples t-test, descriptives plot). Points are "
         "fold means with 95% confidence intervals.")
FIG(14, "Share of Each Patient's Cycles Classified Correctly, by Architecture",
    "j2_cv_patients.png", 5.6,
    note="Produced in jamovi (jmv, paired-samples comparison of 126 patients).")
FIG(15, "True Class Against Predicted Class in Cross-Validation",
    "j3_cv_confusion.png", 6.05,
    note="Produced in jamovi (jmv, contingency tables, row percentages). Each bar group is "
         "one true class; bars show how its cycles were classified. The two panels have "
         "different vertical scales.")


H2("Rebuilt Classifier on Resondi Device Recordings")
para("The fusion network ran without error on all 45 stored lung recordings, at a "
     "median of 2.0 seconds per recording including fetching the audio. On the 26 unique "
     "recordings made with the Resondi device, it chose Healthy for 16, Wheezing with "
     "Crackles for 6, Wheezing for 3 and Crackles for 1. The score of the chosen class "
     "ranged from 31 to 66 percent, with a median of 41 percent (Figure 16). On the same "
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

# ═══════════════════════════════════════════════════ DISCUSSION
H1("Discussion")

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
FILL(p, "consider reporting Cohen's kappa with a confidence interval alongside the "
        "agreement rate, since kappa corrects for the agreement expected by chance")

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
para("The fusion network has since been put into the Resondi application. Because Edge "
     "Impulse provides no chromagram processing, it runs in the browser as an exported "
     "ONNX model, the three seeds combined in one file, with the band-limiting, levelling "
     "and feature extraction rewritten in JavaScript. The rewritten features gave the same "
     "top class as the Python originals on 600 of 600 validation windows. Run on 26 "
     "recordings already made with the Resondi device, the deployed fusion network gave "
     "top-class scores of 31 to 66 percent (median 41; Figure 16), against 27 to 34 "
     "percent for the "
     "Edge Impulse build it replaced. That shows it is more decisive on device audio, not "
     "that it is more often right: none of those recordings has a reference label.",
     first=0)

H2("The Heart Sound Component")
para("The heart component is less advanced than the lung component, and the paper reports "
     "it as such. What exists is the acquisition side: a guided, fixed-order cardiac "
     "sequence that makes heart recordings comparable between visits in the same way as "
     "lung recordings. What does not yet exist is any automated interpretation of them, "
     "and the lung results above carry a direct warning for that work: a classifier trained "
     "on one set of stethoscopes, or one age group, did not transfer to another.", first=0)
para("That warning applies with more force to the heart. CirCor was recorded from Brazilian "
     "children with a commercial electronic stethoscope; Resondi's patients include "
     "Filipino adults, and its microphone may attenuate the lowest heart-sound frequencies. "
     "The work therefore proceeds in a fixed order: confirm the reference labels with the "
     "cardiologist's review, measure the device's low-frequency response, train and test "
     "the murmur classifier on CirCor with a patient-wise split, and only then test it on "
     "heart recordings made with the Resondi device and labelled by a cardiologist.",
     first=0)

H2("Planned Extensions")
para("Two extensions are planned and were not implemented in the work reported here.",
     first=0)
para("The acquisition protocol extends from seven sites to nine. The two additional "
     "sites are an interscapular pair at T3–T4, beside the spine, which sample the "
     "posterior upper lobes; the tracheal reference and the six fields already recorded "
     "are retained. Figure 17 shows the nine sites on the body and Table 4 gives their "
     "landmarks.", first=0)

FIG(15, "Planned Nine-Site Acquisition Protocol",
    "p1_nine_sites.png", 5.9)

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
     "separates the effect of each change, as Table 5 shows. Its first three rows have "
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
     "half of Filipinos can reach a rural health unit within thirty minutes of travel "
     "(Department of Health, 2020).", first=0)

para("Department of Health facility registry figures record approximately 26,504 "
     "barangay health stations, 2,682 rural health units, and 836 municipal and city "
     "health centres nationwide (DOH, 2025) \u2014 roughly 30,000 public facilities at which "
     "auscultation forms part of routine assessment. Of these, the facilities Resondi "
     "can presently serve are narrower: about 3,518 rural health units and "
     "municipal or city health centres that have a resident clinician able to perform the practitioner review the platform depends "
     "on. Nursing and medical schools form a second group, for which the system functions "
     "as a teaching instrument rather than a clinical one.", first=0)

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

p = para("Early engagement has begun in Palawan, with exploratory discussions among "
         "rural health units, private clinics, and nursing and medical schools in and "
         "around Puerto Princesa City regarding pilot deployment and classroom use. These "
         "are exploratory conversations rather than commitments; no memorandum of "
         "agreement is in place, and they are reported only to establish that the "
         "deployment setting described above is reachable.", first=0)
FILL(p, "name the institutions if you can, with dates. An unnamed engagement claim is "
        "the first thing a reviewer or a panel asks you to substantiate, and if you "
        "cannot name one, delete this paragraph rather than leave it unsupported")

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
    "The heart component is not evaluated. Heart recordings are captured and filed, but "
    "no heart-sound measurement or classification result is reported, and the device's "
    "response at the lowest heart-sound frequencies has not been measured.",
    "Speed of automated quality control. The system assesses whether ambient noise, weak "
    "signal, or motion artifact has rendered a recording unusable, but at a mean of 145 "
    "seconds per recording the check is too slow to run routinely before "
    "classification. In practice quality control therefore still rests largely with the "
    "reviewing practitioner.",
]:
    p = para(lim, first=0, after=6, spacing=1.6)
    p.paragraph_format.left_indent = Inches(0.35)

H2("Conclusion")
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
     "which validation with local recordings can now proceed. The heart component has "
     "reached the same starting point on the acquisition side, with its classifier "
     "specified and its training data prepared but not yet built.")
para("The system does not replace clinical judgement and is not designed to. Every "
     "classification is presented to a practitioner who confirms, modifies, or rejects "
     "it, and no result is returned to a patient unreviewed. On the evidence reported "
     "here, that arrangement is not a precaution but a requirement.")

H2("Recommendations")
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
    "agreement with the dataset's labels before training on them.",
    "Train and evaluate the heart-murmur classifier on CirCor with a patient-wise split, "
    "with sensitivity as the primary criterion, and measure the device's frequency "
    "response from 20 Hz before testing it on Resondi heart recordings.",
    "Conduct a prospective evaluation in a rural health unit measuring recordings "
    "captured per week, proportion of abnormal classifications reviewed, and time to "
    "review.",
]:
    p = para("• " + rec, first=0, after=6, spacing=1.6)
    p.paragraph_format.left_indent = Inches(0.35)

# ═══════════════════════════════════════════════════ REFERENCES
H1("References")
REFS = [
 "3M. (2025). Littmann CORE digital stethoscope (Model 8480) [Product listing]. "
 "https://mdmaxx.com/products/3m-8480-littmann-core-digital-stethoscope",
 "Arts, L., Lim, E. H. T., van de Ven, P. M., Heunks, L., & Tuinman, P. R. (2020). The "
 "diagnostic accuracy of lung auscultation in adult patients with acute pulmonary "
 "pathologies: A meta-analysis. Scientific Reports, 10, 7347.",
 "Bohadana, A., Izbicki, G., & Kraman, S. S. (2014). Fundamentals of lung auscultation. "
 "New England Journal of Medicine, 370(8), 744–751.",
 "Department of Health. (2020). Philippine health system review / primary care "
 "access figures. [Add the full citation you used in the concept note.]",
 "Department of Health. (2025). National health facility registry. [Add full citation.]",
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
 "Baraeinejad, B., et al. (2023). Design and implementation of an ultralow-power "
 "digital stethoscope. [Add full citation from your reference list.]",
 "Kim, Y., et al. (2021). Respiratory sound classification for crackles, wheezes, and "
 "rhonchi using a convolutional neural network. [Add full citation from your list.]",
 "Shkarupylo, V., et al. (2024). Intelligent digital stethoscope for neural network "
 "analysis of auscultatory signals: A review of sensors, architectures and algorithms. "
 "https://science.lpnu.ua/node/43249",
]
for r in sorted(REFS):
    p = para(r, first=0, after=8, align=WD_ALIGN_PARAGRAPH.LEFT, size=11, spacing=1.6)
    p.paragraph_format.left_indent = Inches(0.5)
    p.paragraph_format.first_line_indent = Inches(-0.5)

OUT = os.path.normpath(os.path.join(HERE, "..", "..", "imrad", "Resondi-IMRaD-Heart-and-Lung-2026-11-13.docx"))
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
