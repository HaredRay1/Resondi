"""Chapter 1 revisions."""
TITLE = ("Resondi: A CNN-Assisted Auscultation Instrument for Lung Sound Monitoring, Longitudinal "
         "Tracking, and Rehabilitation-Support System")
OLD_TITLE = ("Ausculta: A CNN Fusion-Based Smart Auscultation System for Cardiopulmonary Sound "
             "Classification, Longitudinal Monitoring, and Rehabilitation Support")
BUILT = "The model evaluated was MFCC + CNN; fusion is planned, so it must not read as built."
TENSE = "The study is finished, so what was done is now in the past tense."


def apply(c):
    c.sec("Introduction")
    c.sub("Cardiopulmonary health is vital", "As researchers, we believe that", "The researchers believe that",
          "Research papers should not use first person.")
    c.sub("Cardiopulmonary health is vital",
          "Accordingly, this study will develop " + OLD_TITLE + ", integrating an ESP32-based smart stethoscope, "
          "standardized sound recording, recording-quality evaluation, convolutional neural network (CNN) feature "
          "fusion, longitudinal monitoring, and medical-practitioner supervision. The researchers seek to create",
          "Accordingly, this study developed " + TITLE + ", integrating an ESP32-based smart stethoscope, standardized "
          "sound recording at seven sites, recording-quality evaluation, a convolutional neural network (CNN) classifier, "
          "and medical-practitioner supervision. The researchers sought to create",
          "Uses one title across all chapters (the one in the Statement of the Problem and the full paper). " + BUILT)
    c.sub("Worldwide, respiratory", "However, effective monitoring will involve more than simply acquiring audio "
          "recordings, since sound quality, consistent recording procedures, dependable classification, and suitable "
          "clinical interpretation will remain essential considerations.",
          "However, effective monitoring involves more than simply acquiring audio recordings, since sound quality, "
          "consistent recording procedures, dependable classification, and suitable clinical interpretation remain "
          "essential considerations.", "General statements belong in the present tense.")
    c.sub("Progress in artificial intelligence", "Through combining these functions with a CNN fusion-based analysis "
          "method and practitioner review, Ausculta will aim to address",
          "By combining these functions with CNN-based analysis and practitioner review, Resondi aims to address", BUILT)
    c.rep("In the Philippines, respiratory",
          "In the Philippines, respiratory health continues to be a significant public health concern. The Philippine "
          "Statistics Authority (PSA, 2025) identified pneumonia as one of the country's leading causes of death in 2024, "
          "while the Philippine Council for Health Research and Development (PCHRD, 2023) reported an adult asthma "
          "prevalence of 8.7%. These findings emphasize the ongoing need for proper respiratory assessment and continuous "
          "management. The study was conducted in Puerto Princesa City, Palawan, with Puerto Princesa City National Science "
          "High School serving as the research institution for the development and evaluation of Resondi. The project "
          "entailed designing an ESP32-based smart stethoscope and an accompanying monitoring platform to support guided "
          "auscultation, audio recording, quality assessment, and AI-assisted analysis. The study does not include specific "
          "local statistics on respiratory cases or determine the extent of unmet monitoring needs in Puerto Princesa City, "
          "so it evaluated the technology within its intended context without presuming that existing local healthcare "
          "services are inadequate.", TENSE + " “The research plan” wording removed.")
    c.rep("Despite advances in digital stethoscopes",
          "Despite advances in digital stethoscopes, respiratory sound databases, and AI-assisted classification, a research "
          "gap persists in determining how effectively an integrated prototype performs in standardized sound acquisition, "
          "recording-quality assessment, CNN-based classification, and practitioner-supervised review when tested on its own "
          "hardware rather than on a reference database. These assessments are important because inconsistent recording "
          "quality or lower classification performance could compromise the reliability of monitoring information. To address "
          "this gap, the study developed and evaluated Resondi by integrating an ESP32-based smart stethoscope, Bluetooth Low "
          "Energy (BLE) and MicroSD storage, guided auscultation, audio preprocessing, an MFCC-input CNN classifier, and a "
          "medical-practitioner review workflow. The researchers evaluated the system's signal acquisition against a "
          "conventional stethoscope, recording clarity, ambient noise conditions, response time, agreement with reference "
          "labels, and acceptance among prospective users. Feature fusion and same-site comparison across visits were "
          "specified as the next iteration and were not evaluated. Ultimately, the study produced a functional research "
          "prototype that supports structured respiratory sound recording and review under professional supervision. Through "
          "systematic evaluation and identification of its technical limitations, the research contributes to advancing "
          "AI-assisted auscultation technology while preserving the essential role of qualified healthcare professionals in "
          "interpreting findings and making clinical decisions.",
          "Removed tests that were never run (clean versus noisy audio, reference versus device classification). Lists what "
          "was actually evaluated. BLE stays because the evaluated build used it; " + BUILT)

    c.sec("Statement of the Problem")
    c.rep("This study aims to develop and evaluate",
          "This study aimed to develop and evaluate " + TITLE + " in terms of its respiratory sound recording quality, system "
          "specifications, classification agreement, response time, and end-user acceptance.", TENSE)
    c.sub("Specifically, this study seeks", "this study seeks", "this study sought", TENSE)
    q = "Questions now match what Chapter 4 of the full paper reports. A question with no result in the paper would be the first thing a panel asks about. Keep this only if your adviser agrees; see the decisions list."
    c.rep("1. What is the quality", "1. What is the quality of respiratory sound recordings captured using Resondi in terms "
          "of signal strength relative to a conventional stethoscope, clarity ratings, and ambient noise conditions?", q)
    c.rep("2. What are the technical", "2. What are the technical specifications of the Resondi smart stethoscope and "
          "respiratory monitoring platform in terms of hardware components, system architecture, user interface, and data "
          "management?", "Name change only; wording otherwise kept.")
    c.rep("3. What is the performance", "3. To what extent do the CNN-assisted classifications of normal breathing sounds, "
          "wheezing, crackles, and combined wheezing and crackles agree with reference labels on recordings captured using "
          "Resondi, and how does that agreement compare with the 25 percent expected by chance?", q)
    c.rep("4. How does the classification", "4. What is the response time of the system across device connection, recording, "
          "recording-quality assessment, preprocessing, and classification?", q)
    c.rep("5. How do the recording quality", "5. What is the level of end-user acceptance of Resondi in terms of performance "
          "expectancy, effort expectancy, social influence, and facilitating conditions?",
          "The survey actually used the UTAUT constructs; it had no durability or user-friendliness scale. " + q)

    c.sec("Null Hypotheses")
    c.sub("The researchers hypothesize", "The researchers hypothesize at an alpha 0.05 level that",
          "The researchers tested the following hypothesis at an alpha 0.05 level:", TENSE)
    h0 = c.find("1.H₀ (Null Hypothesis): There is no significant difference in the classification performance")
    h0.runs[0].text = "H₀ (Null Hypothesis):"
    p = c.rep("H₀ (Null Hypothesis): There is no significant difference in the classification performance",
              "H₀ (Null Hypothesis): Agreement between the model's classifications and reference labels on Resondi recordings "
              "is no greater than the 25 percent expected by chance across four categories.",
              "This is the one hypothesis the study tested (exact binomial, 6 of 15, p = 0.148).")
    p2 = c.rep("H₁ (Alternative Hypothesis): There is a significant difference in the classification performance",
               "H₁ (Alternative Hypothesis): Agreement between the model's classifications and reference labels on Resondi "
               "recordings is greater than the 25 percent expected by chance across four categories.", "Matches the new H₀.")
    c.delete("2.H₀ (Null Hypothesis)", "Reference versus device classification was designed but never run.")
    c.delete("H₁ (Alternative Hypothesis): There is a significant difference between the classification performance",
             "Pairs with the removed H₀.")
    c.delete("3.H₀ (Null Hypothesis)", "Signal strength and clarity were compared descriptively; no significance test was run.")
    c.delete("H₁ (Alternative Hypothesis): There is a significant difference between the recording quality",
             "Pairs with the removed H₀.")
    c.add_after(p2, "Three further hypotheses were proposed at the outset: differences in classification between clean and "
                "noise-contaminated recordings, between reference-dataset and device recordings, and in recording quality "
                "between a conventional stethoscope and the device. These tests were not carried out in this study and are "
                "carried forward to the next phase of validation.",
                "States openly that the original hypotheses were dropped, rather than quietly changing them.")

    c.sec("Scope and Delimitation")
    c.rep("Problem. This study is entitled",
          "Problem. This study is entitled “" + TITLE + ".” It developed and evaluated Resondi, an ESP32-based smart stethoscope "
          "integrated with a mobile-first application that records, stores, and analyzes lung sound recordings. The study "
          "covered device development, recording quality assessment, audio processing, CNN-based classification into four "
          "categories (normal, wheezing, crackles, and wheezing with crackles), practitioner review, end-user acceptance, and "
          "application functionality. Evaluation is limited to lung sounds: the device also records heart sounds, but no "
          "cardiac classification model was trained or tested. The evaluated build recorded at seven standardized sites and "
          "classified from a single MFCC input. A nine-site protocol, three-branch feature fusion, and comparison of the same "
          "site across visits are planned and were not evaluated. The model was developed on a publicly available reference "
          "dataset, the ICBHI 2017 Respiratory Sound Database. Resondi is a research and decision-support prototype rather than "
          "an independent diagnostic system. It does not diagnose lung disease; its outputs are held for confirmation by a "
          "practitioner and supplement, rather than replace, professional medical assessment.",
          "States what was and was not evaluated. Heart and fusion were written as done; they were not. "
          "“Rehabilitation guidance tailored to users' needs” removed because it was not tested.")
    c.rep("The map of PuertoPrincesa",
          "The map of Puerto Princesa City National Science High School, Puerto Princesa City, Palawan is presented on the next "
          "page. The study was conducted at multiple locations in Puerto Princesa City, including the school, a private "
          "hospital, a hospital ward, a quiet room, and a community area. These locations served as sites for prototype testing "
          "and end-user evaluation.",
          "Fixes “PuertoPrincesa” and “Highschool”. Home-based testing removed: the paper reports three settings and none is a home.")
    c.sub("Figure 1. Location of", "Puerto Princesa City National Science Highschool", "Puerto Princesa City National Science High School", "Spelling.")
    c.rep("The study will be conducted from late September",
          "The study was conducted from [CONFIRM start and end month and year]. This period covered the development of the "
          "Resondi smart stethoscope and its accompanying application, practitioner review, prototype testing, and field "
          "evaluation.", "“Late September to December” cannot be right: the permission letters and certificates are dated August 2026. Only you know the real dates.")
    c.rep("The participants of this study will include",
          "The study involved 27 survey respondents across Puerto Princesa City (13 patients, 13 members of the general public, "
          "and 1 practitioner), three patients at a private hospital recorded under the supervision of an attending physician, "
          "and three pulmonologists, one of whom is also a practising pediatrician, who reviewed reference recordings. The "
          "ICBHI 2017 Respiratory Sound Database supplied the reference data for model development.",
          "Replaces the plan with who actually took part. Cardiologists removed: heart sounds were not evaluated.")

    c.sec("Significance of the Study")
    c.sub("The investigation entitled", OLD_TITLE, TITLE, "One title across all chapters.")
    c.sub("Healthcare Institutions and Medical Practitioners.", "recording, analyzing, and monitoring lung and heart sounds",
          "recording, analyzing, and reviewing lung sounds", "Matches the lung-only scope.")
    c.sub("Healthcare Institutions and Medical Practitioners.", "Ausculta may facilitate the review of recorded sounds over time and provide",
          "Resondi may facilitate the review of recorded sounds and provide", "Comparison over time was not evaluated.")
    c.sub("Residents and Communities.", "the recording and monitoring of lung and heart sounds", "the recording and monitoring of lung sounds", "Matches the lung-only scope.")
    c.sub("Researchers. This study", "processing cardiopulmonary sound recordings", "processing respiratory sound recordings", "Matches the lung-only scope.")
    c.sub("Future Researchers.", "digital stethoscopes, cardiopulmonary sound classification, longitudinal monitoring",
          "digital stethoscopes, respiratory sound classification, longitudinal monitoring", "Matches the lung-only scope.")
