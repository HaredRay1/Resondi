# Resondi: current state, for a Claude chat session (15 November 2026)

This is a one-file summary of the whole project, written on 15 November 2026 from the project folder. It is the
**newest** status file. Where it disagrees with `CLAUDE.md` or `HANDOFF-2026-11-10-model.md`, this file wins. On
what the papers say, the papers themselves are the final word.

Keep it current: any Claude Code session that changes the project's state updates this file too (see
`START-HERE-PROMPTS.md`).

---

## 1. The project

- **Resondi** is an AI-assisted smart stethoscope with a web platform. It is a screening aid that gives
  decision support; it never gives a diagnosis, and a licensed practitioner confirms every result.
- **The device** is built on an ESP32. It records lung sounds at **7 guided sites** (six lung fields plus the
  trachea) and heart sounds at **5 sites** (the four valve points plus Erb's point).
  - Recording format: 16 kHz, 16-bit mono WAV, 15 seconds per recording, saved to a microSD card.
  - The device raises its own Wi-Fi network and serves its own page at `192.168.4.1`.
- **The platform** is a Base44 web app at `resondi.base44.app`, in English and Filipino. It stores each recording
  against a patient and a site, runs the AI models in the browser, and shows each result to a practitioner, who
  confirms or changes it.
- **Getting recordings from the device to the platform:**
  - On the microSD card, carried by a person.
  - Since 14 November, also by a phone that joins the device's Wi-Fi, downloads the recordings and uploads them
    through the app.
  - The automatic gateway between the two is **not built**.
- **Team Wheezards**, Puerto Princesa City National Science High School, Palawan.
  - Founders: Ahnycca Krish N. Malimban, Hared Ray A. Cabrera and Jarred Paul G. Llacuna.
  - **Ahnycca is the sole author** of both papers below.
- **Credits on the papers:**
  - Research advisers: John Lemuel J. Noche and Genelyn O. Bautista.
  - Qualified scientist: Bemsor T. Caabay, MSc.
  - Consultants: Dr. Kenneth Wilson O. Lim, Dr. Sonia A. Ulanday and Dr. Riza Cornelle C. de la Bajan.
- **History:**
  - The team won the PSC XI regional round (a business competition) on 26 October 2026. That competition is over.
  - **The current work** is the research plan and the IMRaD paper for the **Regional Science and Technology Fair
    (RSTF)**.
- **Approvals and dates:**
  - IRB approval: 16 July 2026.
  - SRC approval: 17 July 2026.
  - Data collection: 20 July to 28 August 2026 (the logbook's start and end of experimentation; both papers changed to these dates on 15 Nov at Ahnycca's request; the signed Form 1A still says 17 July to 20 August).
  - Physicians' certificates: 21 August 2026.
  - SRC review form, signed "Qualified": 5 November 2026.

## 2. The papers (folder `Ahnyccas papers/`)

| File | What it is |
|---|---|
| `Resondi-IMRaD-Heart-and-Lung-FINAL` (.docx, .pdf) | **The IMRaD paper, 62 pages**, covering lung and heart. Title: *Resondi: An IoT-Based AI-Assisted Auscultation Instrument for Cardiopulmonary Monitoring, Longitudinal Tracking, and Rehabilitation-Support System*. The introduction lists the 11 research questions; the Results answer them in order, one heading each, then give "Results by Objective" for the nine objectives. It has a 250-word abstract. |
| `Resondi-Research-Plan-Heart-and-Lung-FINAL` (.docx, .pdf) | **The research plan, 72 pages**, revised from Ahnycca's original. Sections: A Rationale, B Research Questions (numbered 1–11), C Hypotheses, Goals and Expected Outcomes, D Procedures, E Risk and Safety, F Data Analysis, G Results and Discussion, H Bibliography. Its 46 changes from the original are listed in `research-plan/…Revision-Log…`. |
| `Resondi-Compiled-RSTF-FINAL.pdf` | **The full submission, 228 pages**, with bookmarks. Order: title page, checklist and contents; I. Research Plan; II. ISEF Forms (the signed set, the 14 Nov AI disclosure, and last year's paper *SmartSteth* (2025) after Form 7); III. ISEF Abstract; IV. the IMRaD; V. Project Data Book (the scanned logbook, 13 pages, added 15 Nov; 20 Jul to 28 Aug, the dates both papers now use; the signed Form 1A says 17 Jul to 20 Aug); VI. SRC Evaluation. **It contains phone numbers and e-mail addresses from the ISEF forms. Do not share it.** |
| `Resondi-AI-Usage-Disclosure-2026-11-14` | What AI did and did not do in the project. Ahnycca still has to read it and correct it. |
| `Resondi-Missing-Items-Research-Plan-and-IMRaD` | **The plain-language to-do list** (section 6 below). |

**Format of both papers** (set 14–15 November at Ahnycca's request):

- **Text:** Times New Roman 11 pt, justified, with a 0.5-inch first-line indent.
- **Spacing:** double line spacing (2.0), with the original space between paragraphs kept, and widow/orphan
  control on.
- **Kept single-spaced:** tables, pictures and the plan's Procedures flowchart.
- **References:** APA 7, flush left, with a 0.5-inch hanging indent. Every reference has a full citation. The one
  once cited as "Shkarupylo et al. (2024)" is really **Komaryshyn & Kogut (2026)** and was corrected.

**How changes are made.** Both papers are generated by scripts in Claude Code (`build/imrad/build_imrad.py`,
`build/researchplan/build_plan.py`), so a hand edit in Word is lost at the next rebuild. A Claude chat session
should give the exact new text and say where it goes. Ahnycca then pastes it into Claude Code, which edits the
script and rebuilds.

## 3. What the IMRaD answers for each research question

1. **Recording quality.**
   - Signal: about 45 dB with Resondi against 32 dB with a conventional stethoscope, a 13 dB margin (about 4.5 times
     the amplitude). These are indicative margins, not a formal signal-to-noise ratio.
   - Recordings rated good: 68%; acceptable: 25%; poor: 7%.
   - Background noise: 24, 35 and 42 dB in a quiet room, a ward and the community.
2. **Device specifications.**
   - Build (version 2.0, the current device): PLA enclosure, 173 × 80 × 70 mm; ESP32; INMP441 digital MEMS
     microphone; 32 GB microSD; 20 × 4 display; two buttons; 10,000 mAh battery; Wi-Fi.
   - **The field build tested in the study differed in two parts:** an electret microphone on a MAX4466 amplifier
     board, and Bluetooth Low Energy instead of Wi-Fi. The IMRaD says so, and says no result was obtained on
     version 2.0.
   - Cost: **bill of materials ₱2,775, unit cost ₱4,000.** Ahnycca decided to keep the cost figures.
3. **Platform specifications.**
   - A web app with Lung and Heart modes, a body-diagram guide and role-based access.
   - Each recording is filed by site, and the app shows a recording history, a same-site comparison and trend
     charts.
4. **Analysis system.**
   - Preprocessing: audio at 16 kHz mono, cut into 1-second windows.
   - Features: MFCC, a spectrogram and a chromagram. Each feeds its own CNN branch, and the three are joined in a
     fusion layer that outputs four sound classes (Crackles, Healthy, Wheezing, Wheezing with Crackles).
   - The heart models are reported here too. All numbers are in section 4.
5. **Response time.** Connection 4.55 s, recording 15.00 s, quality check **144.68 s**, preprocessing 20.91 s,
   classification 3.97 s.
6. **Clean versus noisy audio (Hypothesis 1): rejected.**
   - With noise added, balanced accuracy fell from 35.0% to 26.6%, 25.4% and 25.3%, which is chance.
   - McNemar's test with Holm correction: p < .001.
   - This used the MFCC model of 11 November.
7. **Reference recordings versus device recordings (Hypothesis 2): not testable yet.**
   - No device recordings with clinician labels exist.
   - Figure 17 shows how the models score unlabelled device recordings. That is not accuracy.
8. **Conventional stethoscope versus Resondi (Hypothesis 3): not tested inferentially.** The paired raw
   measurements were not kept, so only the descriptive 13 dB margin is reported.
9. **Acceptance.**
   - n = 27 (13 patients, 13 general respondents, 1 practitioner); overall 3.95 of 5, "Agree".
   - **These ratings are of the earlier version, which ran the original model.** The current version has not been
     surveyed.
10. **Preferences for instructional support: not yet answered.** The survey had no items on it.
11. **Longitudinal monitoring and rehabilitation support.** These functions are built in the app but were **not
    evaluated with users**: the same-site comparison, the four-week exercise chart, the breathing-exercise and
    cardiac activity plans (which a practitioner must approve first), and practitioner review. No patient was
    recorded repeatedly over time.

## 4. Numbers that may be quoted, and numbers that may not

**Lung model** (balanced accuracy; chance is 25%):

| Model | Result | Status |
|---|---|---|
| Original app model (diagnosis labels) | ~~71.1% / 83%~~ **invalid because of data leakage. Never quote.** | Withdrawn |
| Field test, original model, 15 device recordings | 40% (6 of 15); Wilson 95% CI 19.8–64.3%; p = .148 against 25% chance | Who set the reference labels, and how, is undocumented |
| Edge Impulse rebuild v1 | 33.5% on 31 test patients | In the app 10–13 Nov; replaced |
| MFCC network, 5-fold cross-validation on all 126 ICBHI patients | 34.0% (CI 30.4–38.2) | Reference |
| **Fusion network + SPRSound children's data, 5-fold cross-validation** | **40.0% (CI 35.9–43.5)**; children 56% | **In the app since 13 Nov** |
| Same fusion design, one pre-specified test (31 patients) | 39.4% (CI 28.4–44.6); children 57.2% | Agrees with the cross-validation |

- **The fusion gain is real:** +5.9 points over MFCC (95% CI +1.0 to +10.3, p = 0.008), on the same 126 patients.
- **IMRaD Table 4, the leakage demonstration:** 39.0% patient-wise, 58.2% when patients are shared, 52.5% when
  windows are shared, and 78.5% on the training data. It shows why the study splits the data by patient. **The
  leaky rows are never accuracy.**

**Heart models** (CirCor DigiScope, patient-wise split, 189 test patients; IMRaD Table 5 and Figure 15):

- First and second heart sounds found: 96.8% and 97.3%.
- **Heart rate: mean error 3.0 beats per minute** (CI 2.5–3.6); 85% of patients were within 5 beats per minute.
- **Murmur detection:**
  - **Sensitivity 66.7% (CI 50.0–81.8), short of the pre-specified 80% target.**
  - Specificity 97.1%; AUROC 0.96.
- Tested on CirCor recordings only, not on Resondi heart recordings.
- A cardiologist's blinded review of 25 recordings is still pending.

**Never say:** that the model is validated, that it diagnoses, or that it works on the Resondi device. Never quote
the murmur result as 80%.

## 5. The live app

- **Lung analysis:** the fusion network runs in the browser (13 November).
- **Heart analysis:** "Analyse heart sound" gives the heart rate and a murmur flag, with on-screen caveats. It was
  published on 14 November together with the device Wi-Fi transfer page.
- **Not yet checked by a person:** that the heart result screen shows correctly for a patient account (to-do B12),
  and that the Filipino wording reads well (B13).
- **The next real gain needs data:** clinician-labelled Resondi device recordings of Filipino patients.

## 6. What is still missing (the to-do list in `papers-support/`)

**Both papers are submission-ready (15 Nov, late evening).** Ahnycca can no longer answer questions, so no
`[[TO FILL]]` marker, CONFIRM note or highlight may be added back to either paper; anything unknown is written as
"not recorded". The research plan's last two yellow highlights were removed (its builder now strips all highlights
before saving). One-page table of the lung fusion and heart model results:
`model-rebuild/results/accuracy-summary-lung-heart.md`; the same table is now **IMRaD Table 6** and **research plan
Table 22**. The IMRaD's later tables became 7 (nine-site protocol), 8 (architecture vs data) and 9 (intended users);
it is now 62 pages. **`Ahnyccas papers/` holds only the two papers (Word + PDF) and the compiled PDF**; the AI
disclosure, the to-do list, the title page and the folder README are in `papers-support/`.

**Part A, must do before submitting** (1 item, outside the papers; the logbook scan was added 15 Nov; **the IMRaD has no `[[TO FILL]]` markers left** since the evening of
15 Nov):

1. Tick questions 2, 5 and 6 on the ISEF abstract page.

**The last four markers were filled on 15 Nov at Ahnycca's request** ("if cant, answer it still or use the old ones
answer"), from the earlier papers, because no team record had the answers. Part B item "Check four sentences
filled on 15 November" asks the team to confirm them:

- **Loss function:** categorical cross-entropy, Edge Impulse's default for its classification block (Ahnycca chose
  this).
- **Zones:** the two anterior upper sites form the upper zones and the two posterior infrascapular sites the lower
  zones. The two side (mid-axillary) sites, over the right middle lobe and the lingula, and the trachea are reported
  site by site but are not inputs to the zone rules. Basis: the 83-page paper's rule table names only UL/UR/LL/LR.
  The app's rule layer is not in its code, so this was not checked against it.
- **45 vs 32 dB test:** the IMRaD now says the reference level, the stethoscope's make and model, and how its sound
  was captured were not recorded, so the figures are indicative margins, not a signal-to-noise ratio. No earlier
  paper records the method either.
- **Survey eligibility:** prospective users such as health workers and other authorised end users, or patients
  examined with the system, with its purpose and limitations explained first. This is the 83-page paper's wording;
  no further rule, such as an age limit, was recorded.

**Filled earlier on 15 Nov** (commits `882df5c` and `3930c40`; the IMRaD went from 12 `[[TO FILL]]` markers to 4,
and then to 0 as above). From the project files: recordings are 16-bit and cut into 1-second segments (50% overlap in
training, none in testing and the app); the three hospital patients took part in the survey, as the 83-page paper
says (whether all three are among the 27 responses is not recorded); the notes on the full paper's t-test and on
Cohen's kappa were removed. Confirmed by the team: the research design is developmental–descriptive; **the
field-test device used an electret microphone on a MAX4466 board with Bluetooth Low Energy** (the INMP441 and Wi-Fi
came with version 2.0; the 83-page paper's parts tables list the INMP441, which the team overrode); three health
professionals rated recording quality; the survey used convenience sampling.

**Known contradictions with the 83-page paper:** it reports signal strength as 32.49 dB (Ausculta) against 7.89 dB
(stethoscope), while the IMRaD uses 45 against 32 dB; and it gives 30 survey participants plus the 3 hospital
patients, while the IMRaD analyses n = 27.

**Part B, before the fair** (17 items):

- **Decisions:**
  - APA or MLA: the fair's form says MLA; both papers use APA.
  - Genelyn O. Bautista's two roles: she is listed as an adviser and also signed as the IRB nurse.
- **Form fixes:**
  - Form 1A item 10.
  - The Form 2C tick.
  - The old name "Ausculta" on signed forms. Never edit signed documents.
  - Unsigned letters to the cardiologists.
  - Logbook procedures.
  - Reading the AI disclosure.
  - The Form 7 research plan.
  - A cover page and plagiarism report, if the fair asks.
- **Checks:**
  - The Department of Health facility counts (26,504 / 2,682 / 836).
  - The heart result screen.
  - The Filipino wording.
  - The four sentences filled on 15 November (above).
- **Information to collect:**
  - Repeat the acceptance survey on the new version.
  - The 15 field-test results matched to their reference labels.
  - The cardiologist's answer sheet.

**Part C, future work:**

- Labelled device recordings.
- Side-by-side recordings with a regular stethoscope.
- Repeated recordings of the same patients over weeks.
- Heart recordings on the device.
- A better murmur detector.
- A Filipino lung-sound dataset.
- A faster quality check.

## 7. Rules

- Use only numbers that are in the project files. If something is not in them, say you don't know.
- **Ahnycca's Google Docs and the 83-page full paper:** do not edit them. Give the revised text to paste.
- **Personal data:** never ask for, repeat or put into a document:
  - the survey respondents' names or e-mails;
  - patient details;
  - phone numbers or e-mails from the forms;
  - passwords, API keys or tokens.
- The cardiologist's heart-validation answer key is private and stays out of the shared folder.
- **Never edit names on signed certificates or forms.**
- **The Drive copy of the project folder is out of date.** Drive for desktop syncing has been paused since
  12 November, so files online may be old. Trust the attached files.

## 8. Where things are

- **GitHub:** `HaredRay1/Resondi` (private, branch `master`) holds everything except the compiled PDF and private
  data.
- **The project folder** `Downloads\Resondi`:
  - `Ahnyccas papers/`: the two final papers and the compiled PDF only; `papers-support/`: the to-do list, AI disclosure, title page.
  - `imrad/` and `research-plan/`: working copies, fill-ins and the revision log.
  - `model-rebuild/results/`: every model result.
  - `app-changes/`: every app change.
  - `build/`: the scripts that generate every document.
- **Older background:**
  - `CLAUDE.md`, the 6 November handoff. Its sections §0–§10 are older than its top note.
  - `HANDOFF-2026-11-10-model.md`, the 9–14 November model work, in date order.
