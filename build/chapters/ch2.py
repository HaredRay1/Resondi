"""Chapter 2 revisions."""
import copy
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

PLANNED = "Fusion is planned, not built: the evaluated model takes one MFCC input."
DONE = "Rewritten from plan to what the evaluated prototype actually does."

PHRASES = [
    ("CNN fusion-based smart auscultation system", "CNN-assisted smart auscultation system", PLANNED),
    ("CNN fusion-based classification", "CNN-based classification", PLANNED),
    ("its proposed CNN fusion architecture will examine complementary acoustic features to classify",
     "its planned CNN fusion architecture would examine complementary acoustic features to classify", PLANNED),
    ("the proposed CNN fusion architecture will examine acoustic features to classify",
     "the planned CNN fusion architecture would examine acoustic features to classify", PLANNED),
    ("the proposed system will use a CNN fusion architecture to classify",
     "the planned next iteration would use a CNN fusion architecture to classify", PLANNED),
    ("Their work is relevant to the proposed CNN fusion architecture", "Their work is relevant to the planned CNN fusion architecture", PLANNED),
    ("for the proposed CNN fusion approach", "for the planned CNN fusion approach", PLANNED),
    ("the proposed platform will also organize recordings according to date and anatomical location",
     "the platform also organizes recordings according to date and anatomical location", "The platform stores recordings this way today."),
    ("The system will support the organization and interpretation", "The system supports the organization and interpretation", "Tense."),
    ("Raspberry Pi-based hardware", "ESP32-based hardware", "The device has never used a Raspberry Pi; it is built on an ESP32."),
    ("potential screening-support device", "potential decision-support device",
     "“Screening” is a clinical claim the study does not support and the rest of the paper avoids it."),
    ("This dataset is relevant to Ausculta's heart sound classification component, as it may serve",
     "This dataset is relevant to the planned heart sound classification component, as it may serve",
     "Heart Mode records today; no cardiac model exists yet."),
    ("the CirCor DigiScope Phonocardiogram Dataset, described in a 2022 publication on heart murmur detection and classification,",
     "the CirCor DigiScope Phonocardiogram Dataset (Oliveira et al., 2022)",
     "A source needs an author, and this one is named later in the same chapter."),
]

TF = [
    "This study rests on three bodies of theory, one for each thing it set out to measure: how a recording becomes a "
    "classification, whether a recording can be trusted and compared, and whether people will accept the system.",
    "Digital signal processing and supervised machine learning. A sound can be treated as a signal and transformed into "
    "features that describe its frequency content over time. In supervised learning, a model learns the relationship "
    "between such features and labels from annotated examples, and is then tested on data it did not learn from (Pramono et "
    "al., 2017; Rocha et al., 2019). In this study, mel-frequency cepstral coefficients (MFCCs) are the features and a "
    "convolutional neural network (CNN) is the model. The theory also sets the condition for a fair test: an estimate is "
    "only meaningful if the test data are independent of the training data, which is why this study reports the partitioning "
    "of its data and treats field agreement as its main estimate of performance.",
    "Measurement reliability and longitudinal observation. A comparison between two recordings is informative only if a "
    "difference between them reflects the patient and not the procedure. This is why the study fixes the recording sites and "
    "their order, and why recording quality is assessed separately from classification (Tzeng et al., 2025). Longitudinal "
    "observation extends the same logic over time, by pairing recordings of the same site across visits. In this study it "
    "frames the system's design and its next iteration, but it was not itself evaluated.",
    "Unified Theory of Acceptance and Use of Technology (UTAUT). Venkatesh et al. (2003) propose that intention to use a "
    "technology depends on performance expectancy, effort expectancy, social influence, and facilitating conditions. This "
    "theory underlies the acceptance questionnaire used in this study, and its constructs organize the end-user results in "
    "the Statement of the Problem. Acceptance measured this way describes readiness to use the prototype. It does not "
    "establish clinical effectiveness.",
]

INPUT = ("For the input part, it includes the variables of the study. These are the specifications of the Resondi device and "
         "platform, covering the hardware components, cost of materials, user interface, role-based access control, and data "
         "management processes; the respiratory sound recordings, drawn from the ICBHI 2017 Respiratory Sound Database as the "
         "reference dataset and from recordings captured on Resondi hardware at seven standardized sites (six lung fields and a "
         "tracheal reference); the recording quality indicators of signal strength, clarity ratings, and ambient noise levels "
         "across three testing environments; the system response times across device connection, sound recording, "
         "recording-quality assessment, signal preprocessing, and classification output; the classification outputs of normal, "
         "wheezing, crackles, and wheezing with crackles, with reference labels on fifteen recordings; and the end-user "
         "acceptance ratings gathered from 27 respondents across Puerto Princesa City.")
PROCESS = ("For the process part, it contains the developmental and analytical methods applied to those variables. These are the "
           "design and development of the smart stethoscope and monitoring platform, integrating the acoustic chest piece, "
           "microphone and preamplifier, ESP32 microcontroller, Bluetooth Low Energy communication, MicroSD storage, and a "
           "mobile-first application; the audio preprocessing pipeline of resampling, noise reduction, normalization, "
           "segmentation, and MFCC extraction; the training of the convolutional neural network and its classification of "
           "respiratory sound patterns; the descriptive analysis of device and system specifications; the statistical treatment "
           "using mean, standard deviation, and weighted mean, Cronbach's alpha, a 95 percent Wilson score interval, and an exact "
           "binomial test against 25 percent chance at the 0.05 level of significance; and the interpretation of end-user ratings "
           "against the five-point Likert acceptance scale.")
OUTPUT = ("For the output part, it contains the outcomes of the processed variables. These are a developed and documented Resondi "
          "smart stethoscope and monitoring platform with guided auscultation at seven standardized sites; the determined "
          "recording quality and the measured system response times; the established agreement between the model's "
          "classifications and reference labels; the signal strength of the device relative to a conventional stethoscope; and "
          "the assessed level of end-user acceptance.")
TERMS = [
    "Auscultation - The clinical practice of listening to sounds inside the body, in this study through a stethoscope placed at defined chest sites.",
    "Classification agreement - The proportion of recordings on which the model's classification matches the reference label. In this study, 6 of 15 recordings.",
    "Convolutional neural network (CNN) - A deep-learning model that learns patterns from structured input. In this study it classifies MFCC features of lung sounds.",
    "Data leakage - A flaw in which test data are not independent of training data, which makes a model's test scores look better than its real performance.",
    "Digital auscultation - Recording body sounds electronically so they can be stored, replayed, and analyzed.",
    "End-user acceptance - Respondents' ratings of the prototype on the UTAUT constructs, measured on a five-point Likert scale.",
    "Longitudinal monitoring - Comparing recordings of the same site across visits. In this study it is a planned function and was not evaluated.",
    "Mel-frequency cepstral coefficients (MFCCs) - Numeric features that summarize the frequency content of a short segment of sound. In this study they are the model's input.",
    "Practitioner review - The step in which a qualified practitioner confirms, modifies, or rejects an AI classification before it is used.",
    "Recording quality - How suitable a recording is for review or analysis, rated in this study as good, acceptable, or poor.",
    "Resondi - The smart stethoscope and monitoring platform developed in this study, formerly called Ausculta in early project documents.",
    "Standardized sites - The seven fixed recording locations used in this study: a tracheal reference and six lung fields.",
]


def apply(c):
    c.sec("Chapter opening")
    c.rep("This chapter presents the relevant literature",
          "This chapter presents relevant local and foreign literature and studies taken from books, journals, published theses "
          "and dissertations, and the internet.", "Grammar.")
    c.delete_range("Guidelines: Discusses", "AI-Assisted Cardiopulmonary",
                   "These are your school's writing instructions, left in the text. They should not appear in the paper.")

    for old, new, why in PHRASES:
        hit = [p for p in c.paras() if old in p.text]
        assert hit, old[:60]
        for p in hit:
            c._set_text(p, p.text.replace(old, new))
        c.sec("Across the themes")
        c.log.append((c.section, "Revised", old, new, why + (f" ({len(hit)} places.)" if len(hit) > 1 else "")))

    c.sec("Theme headings")
    h = "Theme numbers were missing or repeated (two Theme 5s, no Theme 1 or 2, and Themes 2 and 3 had the same title)."
    c.rep("AI-Assisted Cardiopulmonary Sound Classification", "Theme 1. AI-Assisted Cardiopulmonary Sound Classification", h)
    c.rep("CNN-BASED DIGITAL AUSCULTATION", "Theme 2. CNN-BASED DIGITAL AUSCULTATION, SOUND CLASSIFICATION, AND LONGITUDINAL MONITORING", h)
    c.rep("Theme 3 CNN-BASED", "Theme 3. CNN FEATURE FUSION AND RESPIRATORY SOUND CLASSIFICATION", h)
    c.rep("Theme 4 RECORDING", "Theme 4. RECORDING QUALITY, AI MODEL VALIDATION, AND PRACTITIONER-ASSISTED ASSESSMENT", h)
    c.rep("Theme 5 LONGITUDINAL", "Theme 5. LONGITUDINAL RESPIRATORY SOUND MONITORING AND TRACKING CHANGES OVER TIME", h)
    c.rep("Theme 5 Digital", "Theme 6. Digital Auscultation and Computer-Assisted Heart Murmur Detection for the Planned Heart Mode", h + " The heart theme also now says it is about a planned function.")

    c.sec("Theme 1, Connect the concepts")
    c.rep("The reviewed literature will guide",
          "The reviewed literature guided the development and evaluation of Resondi, a CNN-assisted smart auscultation system. "
          "The prototype uses an ESP32-based device to acquire respiratory sounds and an accompanying mobile-first platform to "
          "organize recordings, display AI outputs, and manage practitioner reviews.", DONE)
    c.rep("The respiratory sound classification component will use",
          "The respiratory sound classification component uses audio preprocessing and a CNN that takes mel-frequency cepstral "
          "coefficients as its input to classify four categories: normal, wheezing, crackles, and wheezing with crackles. A "
          "feature-fusion architecture is planned as the next iteration. The ICBHI 2017 Respiratory Sound Database served as the "
          "reference dataset for model development. Although the database is older, it remains relevant; recent research, "
          "including Tzeng et al. (2025), continues to use it when investigating respiratory sound classification. Its continued "
          "use is justified by its annotations and suitability for the research objectives, rather than by its publication date "
          "alone.", DONE + " " + PLANNED)
    c.rep("The study will evaluate classification performance",
          "The study evaluated classification by comparing the model's output with reference labels on recordings captured with "
          "the prototype, and assessed recording quality separately using good, acceptable, and poor ratings.",
          "Noise-contamination testing and the larger metric set were not carried out.")
    c.rep("An additional evaluation will compare",
          "This comparison matters because differences in the recording hardware and environment may affect model performance. "
          "The study therefore does not assume that results on the reference dataset represent the performance of the prototype.",
          "The reference-versus-device classification test was not run; the reasoning still holds.")

    c.sec("Theme 2")
    c.sub("However, the effectiveness of CNN-based", "Therefore, Ausculta will incorporate recording-quality assessment and evaluate how recording conditions affect its classification performance.",
          "Therefore, Resondi incorporates recording-quality assessment, and the study measured ambient noise in each recording environment.", DONE)
    c.sub("The literature also emphasizes", "For this reason, Ausculta will use the ICBHI 2017 Respiratory Sound Database as its primary reference dataset and separately evaluate recordings acquired through the prototype, where feasible. This approach will help determine whether the model performs consistently across the different recording sources.",
          "For this reason, Resondi was developed on the ICBHI 2017 Respiratory Sound Database, and its classifications were then checked against reference labels on recordings acquired through the prototype.", DONE)
    c.rep("The concepts discussed in the literature directly support",
          "The concepts discussed in the literature directly support the development of Resondi. The system integrates an "
          "ESP32-based sound acquisition device with a mobile-first platform for managing recordings, assessing recording "
          "quality, displaying AI-generated classifications, and supporting practitioner review. The classification model uses "
          "audio preprocessing and a CNN on MFCC features. Its technical performance was evaluated through recording-quality "
          "measures and agreement with reference labels, while acceptance was assessed using UTAUT constructs. Organizing "
          "repeated recordings for comparison across visits and feature fusion are planned functions.",
          DONE + " The acceptance dimensions listed were not the ones the survey measured.")
    c.rep("In this study, the research of Shehab",
          "In this study, the research of Shehab et al. (2024) provides a recent methodological basis for the planned CNN-based "
          "feature fusion in Resondi. The evaluated model does not yet use fusion: it classifies from a single MFCC input into "
          "normal sounds, wheezing, crackles, and wheezing with crackles. The performance reported by previous researchers cannot "
          "automatically be applied to Resondi because the device uses different recording hardware, preprocessing procedures, "
          "and testing conditions. The model was therefore evaluated on recordings acquired through the prototype.", DONE + " " + PLANNED)

    c.sec("Theme 3, Connect the concepts")
    c.rep("The concepts discussed in the literature will guide",
          "The concepts discussed in the literature guided the development and evaluation of Resondi. The system uses an "
          "ESP32-based device to acquire respiratory sounds and a mobile-first platform to manage recordings, display "
          "AI-generated classifications, and organize practitioner feedback.", DONE)
    c.rep("The respiratory classification component will use",
          "The respiratory classification component uses audio preprocessing and a CNN on MFCC features to classify the sound "
          "categories defined for the study. The ICBHI 2017 Respiratory Sound Database served as the reference dataset for model "
          "development. Classification was evaluated by agreement with reference labels on prototype recordings, and recording "
          "quality and ambient noise were examined separately.", DONE)
    c.rep("The study will further compare",
          "Comparing model performance on reference-dataset recordings with performance on prototype recordings, and comparing "
          "the same site across visits, remain for the next phase. Both depend on a model evaluated on patient-separated data.",
          "These were written as done; they were not run.")
    c.rep("A practitioner-review workflow will allow",
          "A practitioner-review workflow allows qualified reviewers to confirm or disagree with an AI prediction, modify their "
          "interpretation, or request another recording. AI predictions, reference labels, and practitioner interpretations are "
          "kept as separate information. The prototype also underwent end-user evaluation using UTAUT constructs. These measures "
          "assess the technical performance and acceptance of the system without assuming that prototype testing establishes "
          "clinical effectiveness.", DONE)

    c.sec("Theme 4, Connect the concepts")
    c.rep("This literature is directly connected",
          "This literature is directly connected to the development and evaluation of Resondi, an intelligent respiratory "
          "auscultation, monitoring, and rehabilitation-support system. The device acquires respiratory sounds through its "
          "stethoscope-based recording hardware and transfers the recordings for processing and classification. Before a "
          "recording is analyzed, the system assesses its quality and identifies recordings that may require repetition. The AI "
          "model classifies normal sounds, wheezes, crackles, and the combination of wheezes and crackles. The ICBHI 2017 "
          "Respiratory Sound Database served as the dataset for model development. This literature also exposes a weakness in "
          "the evaluated model: its training and test data were not separated by individual, so its corpus scores are not "
          "treated as evidence of performance, and the next phase partitions patients before any segmentation. Practitioner "
          "review is a separate step in which a reviewer may confirm, disagree with, or request a repeat of a recording or "
          "classification. By integrating these features, Resondi addresses not only automated sound classification but also "
          "the quality, review, and organization of respiratory recordings.",
          DONE + " It said the data “should be separated”; in fact they were not, and Chapter 3 now discloses this.")

    c.sec("Theme 5, Connect the concepts")
    c.rep("The concept of longitudinal monitoring is directly",
          "The concept of longitudinal monitoring is directly connected to Resondi. The device acquires respiratory sounds and "
          "the mobile-first application saves each recording with its date, anatomical location, and AI-generated classification. "
          "Same-site comparison across visits is the function this design is built toward, and it is planned rather than "
          "evaluated in this study. When it is tested, it will need separate testing from the classification model, using "
          "repeated recordings under consistent procedures. Any displayed changes will represent differences in recorded sound "
          "patterns, not definitive evidence of disease progression, treatment effectiveness, or recovery.",
          "Same-site comparison is not built yet; it is what the funding builds. " + DONE)

    c.sec("Synthesis")
    c.sub("These findings support Ausculta", "These findings support Ausculta’s proposed recording quality control process, which will classify recordings as good, acceptable, poor, or invalid according to predefined criteria.",
          "These findings support Resondi's recording quality assessment, which classifies recordings as good, acceptable, poor, or invalid according to predefined criteria.", DONE)
    c.sub("These findings support Resondi", "The proposed CNN fusion model will then be evaluated using appropriate classification metrics and a carefully separated testing dataset. Data partitioning should also prevent recordings from the same individual from appearing in both training and testing sets when this is relevant to the dataset structure. This approach is intended to reduce the risk of overly optimistic results and provide a clearer assessment of the model's performance.".replace("model's", "model’s"),
          "The literature also requires that recordings from the same individual not appear in both training and testing sets. The evaluated model did not meet this requirement, as Chapter 3 discloses, and patient-separated retraining is the first task of the next phase.",
          "States the leakage problem instead of implying the data were properly split.")
    c.rep("Ausculta proposes to address this need",
          "Resondi is designed to address this need by organizing respiratory recordings by date and anatomical recording location "
          "within a mobile-first application. Comparison of earlier and more recent recordings at the same site is planned and "
          "was not evaluated in this study. It will need to be evaluated separately from the classification model. Any changes "
          "displayed by the system should be interpreted as differences in recorded sound patterns rather than definitive "
          "evidence of disease progression, treatment effectiveness, or recovery.", DONE)
    c.rep("The proposed workflow begins",
          "The workflow begins with respiratory sound acquisition through the ESP32-based hardware and connected stethoscope "
          "components. The recording is then assessed for quality before being processed by the classification model, which was "
          "developed using the ICBHI 2017 Respiratory Sound Database. The application stores recordings with their date and "
          "anatomical location, displays the classification results, and provides a process for practitioner review. "
          "Classification was assessed by agreement with reference labels, using an exact binomial test at the 0.05 level, while "
          "recording quality, response time, and acceptance were evaluated as separate aspects of the prototype.",
          DONE + " Also removes the Raspberry Pi mention and “if hypothesis testing is included”.")
    c.sub("Despite progress in respiratory sound classification", "Fifth, the literature does not automatically establish the usability or practical effectiveness of Ausculta’s proposed combination of recording quality control, CNN-based classification, longitudinal recording management, and practitioner review. These gaps justify the development and evaluation of the proposed prototype. Ausculta will investigate the performance of its respiratory sound classification model, assess recording quality and application usability, and examine whether its recording-management workflow can support organized review over time. However, the prototype’s actual effectiveness must be determined through systematic testing, and its outputs should remain decision-support information rather than independent medical diagnoses.",
          "Fifth, the literature does not establish the usability or practical effectiveness of the combination of recording quality control, CNN-based classification, and practitioner review in Resondi. Sixth, ICBHI 2017 contains no Filipino recordings. East Asian corpora such as HF_Lung_V1 (Hsu et al., 2021) narrow this gap, but no public corpus closes it for Filipino patients. These gaps justify the development and evaluation of this prototype. The study investigated the agreement of its classifier with reference labels, recording quality, response time, and acceptance. The prototype's effectiveness must be determined through further testing, and its outputs remain decision-support information rather than independent medical diagnoses.",
          "Adds the population gap, which matters for a device tested on Filipino patients. " + DONE)

    c.sec("Theme 6, heart sounds")
    c.sub("The development of phonocardiogram", "These resources are relevant to the development of Ausculta, a device intended to record and analyze heart sounds.",
          "These resources are relevant to the planned Heart Mode of Resondi. The device records heart sounds today; no cardiac classification model has been trained, and heart sounds are outside the evaluation reported in this study.",
          "This study's classifier is lung-only, and the theme should say so.")

    # Synthesis belongs after the last theme
    ps = c.paras()
    a = [i for i, p in enumerate(ps) if p.text.strip() == "Synthesis"][0]
    b = [i for i, p in enumerate(ps) if p.text.strip().startswith("Theme 6.")][0]
    t = [i for i, p in enumerate(ps) if p.text.strip() == "Theoretical Framework"][0]
    assert a < b < t
    anchor = ps[t]._p
    for p in ps[a:b]:
        anchor.addprevious(p._p)
    c.sec("Chapter order")
    c.log.append((c.section, "Revised", "Synthesis came before the last theme.", "Synthesis now comes after all six themes.", "A synthesis has to cover every theme."))

    c.sec("Theoretical Framework")
    first = c.rep("In order to assess the level of knowledge", TF[0],
                  "The whole framework came from another paper, on cybersecurity at Makati City Hall. It has nothing to do with this study. New framework written from the theories this study actually uses.", action="Replaced")
    c.delete_range("Data security ideas", "Research Paradigm",
                   "Rest of the cybersecurity framework: Amit (2016), Cybermeter, NIST, three figures, and the instruction “MAKE SURE ALL LITERATURES ARE PROPERLY CITED”.")
    prev = first
    for text in TF[1:]:
        prev = c.add_after(prev, text, "New theoretical framework. Uses only sources already in this paper, plus Venkatesh et al. (2003), which the acceptance survey is built on.")

    c.sec("Research Paradigm")
    c.rep("The research framework will be based", "The research framework is based on the theories and models discussed in the theoretical framework and literature review, from which the statements of the problem were crafted.", "Tense.")
    c.sub("Figure 4. The Conceptual Framework", "Figure 4.", "Figure 2.", "Three cybersecurity figures were removed, so numbering moves. Chapter 1 ends on Figure 1.")
    c.sub("Figure 4 represents", "Figure 4 represents", "Figure 2 represents", "Follows the figure number.")
    nums = "It listed six sites, thirty participants, heart classification, Mel-spectrograms, a t-test and McNemar. The study used seven sites, 27 respondents, a lung-only MFCC model and an exact binomial test. The figure was redrawn to match."
    c.rep("For the input part", INPUT, nums)
    c.rep("For the process part", PROCESS, nums)
    c.rep("For the output part", OUTPUT, nums)
    c.sub("This model identifies the contribution", "the respiratory and cardiac classification outputs", "the respiratory classification outputs", "Lung-only evaluation.")
    c.sub("This model identifies", "as a supportive tool for cardiopulmonary assessment and professional review", "as a supportive tool for respiratory assessment and professional review", "Lung-only evaluation.")

    c.sec("Definition of Terms")
    c.sub("In order to facilitate a common understanding", "the important term used in the study has been defined", "the important terms used in the study have been defined", "Grammar.")
    first = c.find("Chronic Kidney Disease")
    old = first.text.strip()

    def term(p, text):
        name, body = text.split(" - ", 1)
        runs = [r for r in p.runs if r._r.findall(qn("w:t"))]
        runs[0]._r.findall(qn("w:t"))[0].text = name + " - "
        runs[0]._r.findall(qn("w:t"))[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        runs[1]._r.findall(qn("w:t"))[0].text = body

    template = copy.deepcopy(first._p)
    term(first, TERMS[0])
    c.log.append((c.section, "Replaced", old, TERMS[0], "“Chronic Kidney Disease” was a leftover from another paper. The section had no terms from this study. These are written from it, in alphabetical order."))
    c.delete("(ALPHABETICALLY ARRANGED)", "Template instruction left in the text.")
    prev = first
    for text in TERMS[1:]:
        el = copy.deepcopy(template)
        prev._p.addnext(el)
        prev = Paragraph(el, first._parent)
        term(prev, text)
        c.log.append((c.section, "Added", "", text, "New definition."))
