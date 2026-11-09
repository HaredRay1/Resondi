"""Chapter 3 revisions. Methods facts follow build/imrad/build_imrad.py and the full paper."""
from ch1 import TITLE

TENSE = "The study is finished, so methods are in the past tense and say what was done."
SPECS = ("Methods now describe the build that was tested. Fusion, noise-contamination tests and the longer metric list were "
         "plans that were not carried out.")


def apply(c):
    c.sec("Research Design")
    c.rep("This study will employ",
          "This study employed a developmental-descriptive research design to develop and assess " + TITLE + ". The developmental "
          "component focused on designing, assembling, and integrating the electronic stethoscope, ESP32 microcontroller, companion "
          "monitoring platform, audio-processing pipeline, and artificial intelligence (AI) classification model. The descriptive "
          "component characterized the prototype across signal acquisition relative to a conventional stethoscope, recording "
          "clarity, ambient noise conditions, system response time, agreement with reference labels, and end-user acceptance. No "
          "experimental manipulation or control group was involved. Escudero-Mancebo et al. (2023) explain that engineering design "
          "research may employ different research approaches and data-collection methods depending on the objectives and design "
          "problem, which supports a design that combines prototype development with systematic technical evaluation.",
          TENSE + " “Developmental-descriptive” matches the IMRaD and what was actually done.")
    c.rep("The research procedures will be organized",
          "The research procedures were organized according to the study's research questions. First, the researchers developed and "
          "documented the prototype's hardware specifications, platform functions, Bluetooth Low Energy (BLE) connectivity, recording "
          "operations, and preprocessing procedures, and measured the duration of each processing stage.", TENSE)
    c.rep("Second, the recording quality",
          "Second, the recording quality of Resondi was evaluated using mean signal strength relative to a conventional acoustic "
          "stethoscope under the same conditions, clarity ratings by qualified healthcare professionals, and ambient noise measured "
          "in each testing environment.", SPECS)
    c.rep("Third, the CNN-based classification",
          "Third, the CNN-based classification model was developed using the ICBHI 2017 Respiratory Sound Database. Classification was "
          "then assessed by comparing the model's output on fifteen recordings with reference labels for the same recordings.", SPECS)
    c.rep("Fourth, the researchers will conduct",
          "Fourth, the researchers assessed end-user acceptance through a five-point Likert-scale questionnaire adapted from the "
          "Unified Theory of Acceptance and Use of Technology (Venkatesh et al., 2003). Responses were summarized using frequencies, "
          "percentages, weighted means, and standard deviations.",
          "Noise-robustness testing was never run, so it is removed here along with Zulfiqar et al. (2021). If you keep that citation elsewhere, move it to Chapter 2 or further work. The survey is UTAUT, not usability and durability.")
    c.delete("Fifth, the researchers will assess", "Merged into the “Fourth” paragraph above.")
    c.rep("The system's longitudinal-monitoring",
          "Same-site comparison across visits and rehabilitation support were not evaluated in this study. They are treated as design "
          "functions of the prototype, not as evidence of improved clinical outcomes. Likewise, the AI-generated classifications are "
          "treated as computational outputs for research and monitoring support, not as independent medical diagnoses.", TENSE)
    c.sub("Overall, the selected research design", "because the study aims to develop a working technology prototype and systematically evaluate", "because the study aimed to develop a working technology prototype and systematically evaluate", TENSE)
    c.sub("Overall, the selected research design", "It allows the researchers", "It allowed the researchers", TENSE)

    c.sec("Research Participants")
    c.rep("The human participants of the study will consist",
          "The human participants of the study consisted of 27 survey respondents across Puerto Princesa City (13 patients, 13 members "
          "of the general public, and 1 practitioner); three patients at a private hospital recorded under the guidance of an attending "
          "physician; and three pulmonologists, one of whom is also a practising pediatrician, who reviewed reference recordings.",
          "Replaces the plan with who actually took part.")
    c.rep("The study population will therefore",
          "Only one practitioner responded to the survey, so its results mainly describe patients and the general public, not "
          "clinicians. [CONFIRM whether the three hospital patients are among the 13 patients who answered the survey]",
          "A limitation worth stating. The overlap is not recorded anywhere (IMRaD open item 13).")
    c.rep("The researchers will use purposive sampling",
          "[CONFIRM the sampling method and inclusion criteria used for the 27 respondents.] Eligible participants had to be willing to "
          "participate, able to understand the instructions and questionnaire, and able to evaluate the applicable features of Resondi "
          "after an orientation.",
          "The original says purposive sampling, but no record shows how respondents were actually recruited (IMRaD open item 10). Do not leave this as an assumption.")
    c.rep("Participants will be excluded",
          "Individuals who declined to participate or did not provide the required consent or assent were not included. "
          "[CONFIRM whether any respondent was a minor and, if so, how parental consent was obtained]",
          TENSE + " Minors need a stated answer.")
    c.rep("Before data collection, the researchers will explain",
          "Before data collection, the researchers explained the study's purpose, procedures, and the system's stated limitations to "
          "participants. Participation was voluntary. Survey responses and recordings were handled confidentially and stored without "
          "direct patient identifiers.", TENSE)
    c.rep("The participant selection process",
          "The findings are interpreted in relation to the actual participants and are not generalized to all patients, health "
          "professionals, or potential users.", TENSE)

    c.sec("Samples and Sampling Techniques")
    c.rep("In addition to human participants",
          "In addition to human participants, the study used digital audio recordings. The reference sample was the ICBHI 2017 "
          "Respiratory Sound Database (Rocha et al., 2019), which contains 920 annotated recordings from 126 subjects and 6,898 "
          "annotated respiratory cycles, captured at seven chest locations.", SPECS + " Adds the database's size.")
    c.rep("The study will employ purposive sampling",
          "The model was trained on patient-level condition labels (asthma, bronchiolitis, pneumonia, and healthy) applied to every "
          "segment of a patient's audio and displayed as four sound patterns. Because a condition is not audible in every segment, "
          "this labelling is itself a limitation. The database is 793 of 920 recordings chronic obstructive pulmonary disease, which is "
          "not one of the four classes, and the study documentation does not record how those recordings were handled.",
          "Must be disclosed. It is the largest open question about the model, and a judge who knows ICBHI will ask.")
    c.rep("The dataset will be divided into training",
          "The audio was cut into 19,246 five-second samples at a stride of about one second, and these were divided at random over "
          "individual samples into training, validation, and test partitions, with no grouping by recording or subject. Segments that "
          "share four of their five seconds therefore sit on both sides of the split, and a model can score well by recognizing the "
          "patient rather than the sound. The reported corpus accuracies are therefore not independent of the training data and are not "
          "used as evidence of performance. The fifteen-recording field agreement is the only independent estimate in this study. "
          "Patient-separated retraining is the first task of the next phase.",
          "The original said data would be split by subject “where feasible”, and the sentence was cut off. They were not split that way. This is the data leakage finding.")
    c.delete(". Where feasible, the division", "Second half of the same broken sentence.")
    c.rep("For noise-robustness testing", "No data augmentation or synthetic noise was applied.", "Noise-robustness testing was not run.")
    c.rep("Locally acquired recordings obtained",
          "Locally acquired recordings obtained through the Resondi prototype formed a separate set of evaluation samples. They were "
          "assessed for recording quality and, for the fifteen recordings with reference labels, for classification agreement. They were "
          "not combined with the public dataset, since differences in recording devices, acquisition conditions, and sample "
          "characteristics may affect model performance.", TENSE)
    c.rep("If cardiac-sound classification is included",
          "Cardiac-sound classification was outside this study. The device records heart sounds, but no cardiac model was trained or "
          "evaluated, and the ICBHI 2017 database does not establish performance on cardiac sounds.", "Settles an “if” left open.")

    c.sec("Research Instrument / Materials")
    c.rep("The study will utilize technical testing",
          "The primary instrument was the Resondi prototype, which pairs a conventional acoustic chest piece and silicone tubing with a "
          "microphone and preamplifier, an ESP32 microcontroller, Bluetooth Low Energy communication, MicroSD storage, a 20 × 4 character "
          "LCD, and a 10,000 mAh power bank, housed in a 3D-printed polylactic acid (PLA) casing. All results in this study were obtained "
          "with that build. The device has since been revised as enclosure version 2.0, which was not used in this evaluation: an INMP441 "
          "digital microphone is read over I²S with no analogue preamplifier, and Bluetooth is replaced by a Wi-Fi access point. Whether "
          "the revised build changes recording quality has not yet been measured.",
          "States the tested build and keeps it apart from the newer one, which is the same wording as the IMRaD.")
    c.rep("For recording-quality assessment, a structured",
          "For recording-quality assessment, a structured evaluation sheet was used to rate each recording as good, acceptable, or poor. "
          "A separate operational testing sheet documented connection time, recording time, recording-quality assessment time, "
          "preprocessing time, and classification time. The classifier was developed on the Edge Impulse platform and deployed as a "
          "WebAssembly build that runs in the browser.", SPECS)
    c.rep("A structured questionnaire using a five-point",
          "A questionnaire adapted from the Unified Theory of Acceptance and Use of Technology (Venkatesh et al., 2003), using a "
          "five-point Likert scale, was used to assess end-user acceptance. Its items were grouped into performance expectancy, effort "
          "expectancy, social influence, and facilitating conditions. Materials also included electronic stethoscope components, a "
          "computer for software development and analysis, data sheets, a timer, and consent forms.",
          "The survey had no durability or user-friendliness scale; it measured UTAUT. This is the fix your earlier acceptance guide also made.")
    c.rep("To establish the validity of the research instruments",
          "To establish validity, the questionnaire and evaluation sheets were reviewed by the research adviser and qualified reviewers "
          "for clarity, relevance, and alignment with the objectives of the study; instrument validation forms are on file. Reliability "
          "of the questionnaire was assessed using Cronbach's alpha for each multi-item construct. Technical measurements were repeated "
          "under consistent conditions, and the equipment and procedures used were documented.", TENSE + " Adds the validation forms in your Drive folder.")
    c.delete_range("Ensuring validity", "Data Gathering Procedures",
                   "Qualitative “trustworthiness” section, left over from another paper. It mentions interviews and “senior high school students who have experienced body shaming”. This study has no qualitative data: all open-ended survey items returned no responses.")

    c.sec("Data Gathering Procedures")
    c.sub("The procedures employed by the researchers", "The procedures employed by the researchers were outlined in the following schematic diagram:", "The procedures employed by the researchers are outlined in the following schematic diagram:", "Tense.")
    c.rep("The data gathering procedures will be conducted",
          "The data gathering procedures were conducted systematically to collect the information needed to develop and evaluate Resondi. "
          "Data were recorded using standardized evaluation sheets and electronic spreadsheets.", TENSE)

    step = "Steps now match the procedures actually carried out, in the diagram and in the headings below it."
    for old, new in [("Reference Cardiopulmonary Sound Collection and Validation", "Reference Respiratory Sound Collection and Validation"),
                     ("Cardiopulmonary Sound Recording and Quality Assessment", "Respiratory Sound Recording and Quality Assessment"),
                     ("Audio Preprocessing and CNN-Fusion Model Evaluation", "Audio Preprocessing and CNN Model Development"),
                     ("Noise-Robustness Testing", "Ambient Noise Measurement"),
                     ("Longitudinal Monitoring and Practitioner Review Testing", "Classification Agreement Against Reference Labels")]:
        for _ in range(2):
            c.rep(old, new, step)

    c.rep("The researchers will obtain respiratory-sound",
          "The researchers obtained respiratory-sound recordings from the ICBHI 2017 Respiratory Sound Database for model development. "
          "Reference recordings were additionally reviewed by three pulmonologists, one of whom is also a practising pediatrician, and "
          "certificates of their review are on file. Reference labels were stored separately from model predictions.",
          TENSE + " Adds the clinician review your certificates document.")
    c.rep("The researchers will develop the Ausculta smart",
          "The researchers developed the Resondi smart stethoscope using an ESP32 microcontroller, a microphone and preamplifier, an "
          "acoustic stethoscope chest piece, a power bank, and MicroSD storage in a 3D-printed PLA casing. The hardware was integrated "
          "with the companion platform, Bluetooth Low Energy communication, and the audio-processing and AI classification components. "
          "The development process and modifications were recorded on a technical documentation sheet.", TENSE)
    c.rep("The researchers will test the Ausculta prototype",
          "The researchers acquired recordings at seven standardized sites: a tracheal reference followed by six lung fields in "
          "left-right pairs. The application presents an anatomical lung map, the user selects a location, positions the chest piece, "
          "confirms placement, and records, and each recording is saved with its location and metadata. The patient breathes through an "
          "open mouth more deeply than at rest, with the chest piece on bare skin. Where human participants were involved, recordings "
          "were collected after the required permissions and consent. Before analysis, recordings were assessed for background noise, "
          "amplitude, duration, clipping, and motion artifact where technically possible, and rated Good, Acceptable, Poor, or Invalid. "
          "Poor or invalid recordings were recommended for repetition rather than classified.",
          TENSE + " Seven sites stated, as in the rest of the paper.")
    c.rep("To evaluate the recording quality of Ausculta against",
          "Mean signal strength from the device was compared with that of a conventional acoustic stethoscope recorded under the same "
          "conditions, and recordings from both were rated for clarity by qualified healthcare professionals against predetermined "
          "criteria. [CONFIRM the number of raters, the stethoscope make and model, and how signal strength was measured]",
          "The comparison was descriptive; no significance test was run. The three details are not recorded (IMRaD open items 7 and 8).")
    c.rep("The researchers will preprocess eligible",
          "Each recording was resampled to 16 kHz, then passed through noise reduction, amplitude normalization, and segmentation. Each "
          "window was reduced to 13 mel-frequency cepstral coefficients (MFCCs) using a 32-filter mel filterbank and a 256-point FFT. The "
          "classifier is a one-dimensional convolutional neural network with two convolutional blocks of 8 and 16 filters and a "
          "four-unit softmax output, trained with the Adam optimizer at a learning rate of 0.005 for 100 epochs. A three-branch "
          "feature-fusion architecture is planned as the next iteration and was not used to produce any result in this study.",
          "Real model settings, from the IMRaD. Fusion was written as done.")
    c.rep("To determine the effect of noise",
          "Recordings were obtained in three settings: a quiet room, a hospital ward, and a community area. Ambient noise was measured in "
          "each. No noise-contamination experiment was carried out.", "Noise-robustness testing was not run; ambient noise measurement was.")
    c.rep("The researchers will conduct repeated trials",
          "The researchers measured the duration of each operation of the Resondi system: device connection, recording, "
          "recording-quality assessment, signal preprocessing, and classification output. The results were summarized to describe the "
          "system's response time.", TENSE)
    c.rep("The researchers will test the platform's ability",
          "Fifteen recordings classified by the model were compared with reference labels for the same recordings. Reference labels were "
          "kept separate from model predictions. [CONFIRM whether the reviewers were blinded to the model output] Same-site comparison "
          "across visits was not tested in this study.",
          "This was the procedure actually run. Whether reviewers were blinded is not recorded, so it must not be assumed.")
    c.rep("After the prototype and its applicable functions",
          "After the prototype was demonstrated, respondents evaluated the system using the five-point Likert-scale UTAUT questionnaire. "
          "The purpose, functions, limitations, and research-only nature of the prototype were explained first. Participation was "
          "voluntary, and responses were collected confidentially.", TENSE + " Survey constructs corrected.")
    c.rep("After data collection, the researchers will review",
          "After data collection, the researchers reviewed the evaluation sheets, recording metadata, performance logs, model "
          "predictions, and questionnaire responses for completeness and consistency. Recordings were stored without direct patient "
          "identifiers, and reference labels were kept separate from AI predictions. Quantitative results were organized into electronic "
          "spreadsheets for statistical analysis.", TENSE)

    c.sec("Data Analysis")
    c.sub("The data analyses employed", "were outlined", "are outlined", "Tense.")
    why = "The whole Data Analysis section was from another paper, on propagating the plant Ardisia squamulosa. This study's analysis was missing entirely. Written from the analysis actually performed."
    c.replace_textbox("Morphological Characterization", "Descriptive Analysis of System and Device Specifications", why)
    c.replace_textbox("Survival and Propagation Success", "Recording Quality and System Performance", why)
    c.replace_textbox("Comparative Testing of Treatments (if applicable)", "Classification Agreement", why)
    c.replace_textbox("Qualitative Observations", "End-User Acceptance", why)
    c.head_body("Morphological Characterization", "Descriptive Analysis of System and Device Specifications",
                "The specifications of the Resondi smart stethoscope and monitoring platform were presented through technical specification tables, system architecture and workflow diagrams, screenshots, and narrative description.", why)
    c.head_body("Survival and Propagation Success", "Recording Quality and System Performance",
                "Descriptive statistics, mean and standard deviation, were used to summarize signal strength, ambient noise, and the response time of each system operation. Clarity ratings were reported as the percentage of recordings rated good, acceptable, and poor. Decibel values were compared by their difference and never as a ratio, because the decibel scale is logarithmic.", why)
    c.delete_math("The plant survival-rate formula.")
    c.delete("This calculation will provide", "Rest of the plant-propagation analysis.")
    c.head_body("Comparative Testing of Treatments", "Classification Agreement",
                "Classification agreement was reported as the proportion of the fifteen recordings on which the model and the reference labels matched, with a 95 percent Wilson score interval. It was tested against the 25 percent agreement expected by chance across four categories using an exact one-sided binomial test at the 0.05 level of significance. A McNemar test was not used, because it addresses the direction of disagreement rather than the extent of agreement, and a paired t-test was not used, because it cannot be applied to class labels.", why + " Also explains why McNemar and the t-tests in the full paper are removed.")
    c.head_body("Qualitative Observations", "End-User Acceptance",
                "Weighted mean, standard deviation, and Cronbach's alpha were computed for each UTAUT construct and interpreted against the five-point acceptance scale. Items with a yes or no response format were reported as frequencies rather than means. Three behavioral-intention items and all open-ended items returned no responses and were not analyzed.", why)
    c.head_body("Overall Data Management", "Overall Data Management",
                "All data were recorded in standardized data sheets or electronic spreadsheets to ensure accuracy, consistency, and traceability. Summarized data were organized into tables and graphs for interpretation. [CONFIRM the statistical software used]", why)
    c.delete_range("EXAMPLE 2", "Ethical Considerations", "A second template example for interview analysis, including the note “(Discuss thoroughly)”. This study conducted no interviews for analysis.")

    c.sec("Ethical Considerations")
    c.rep("In order to address ethical considerations",
          "The study was conducted under the supervision of the research adviser of the Puerto Princesa City National Science High "
          "School research programme. Participation was voluntary throughout. Written consent forms and data recording sheets were used, "
          "and the purpose and stated limitations of the system were explained to participants before any recording was made or any survey "
          "administered. Resondi was presented as a research prototype and decision-support platform rather than an independent diagnostic "
          "device, and AI-generated results remained subject to professional interpretation. [CONFIRM whether a school research committee, "
          "hospital, or Provincial Health Office approved the study. If none did, keep the next sentence.] Formal review by an institutional "
          "ethics committee was not obtained for this work, and ethics committee review is part of the clinical validation planned for the "
          "next phase.",
          "The original promised ethics approval. No approval is on record, and physician supervision is not the same thing. State it plainly unless you can name the body (IMRaD open item 12).")
    c.rep("The study will involve appropriate prospective",
          "Survey respondents assessed the system on the UTAUT constructs after its objectives, procedures, and limitations were explained. "
          "Informed consent was obtained, and participants could decline any question or withdraw without penalty. Recordings of the three "
          "hospital patients were obtained under the guidance and direct supervision of an attending physician, who reviewed the procedure "
          "and consented to it. Lung sound recordings are sensitive personal information under Republic Act No. 10173, the Data Privacy Act "
          "of 2012; they were stored without direct patient identifiers, and research exports exclude personally identifiable information. "
          "Resondi does not independently diagnose respiratory diseases, and AI classifications are kept distinct from interpretations made "
          "by medical practitioners.", TENSE + " Adds the physician supervision and the Data Privacy Act.")
