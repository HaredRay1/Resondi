# Resondi handoff: lung model rebuild and recent work (9–10 November 2026)

Paste this into Claude chat to bring it up to date. It covers what changed on 9–10 November. The project's full state is in `CLAUDE.md` in the Resondi folder; where they disagree, this file is newer on the points below.

---

## 1. The lung model has been retrained (the main news)

### Why

The old model's reported **71.1% (test), 83.4% (validation) and 83.7% (int8)** were never real. Two faults inflated them:

1. **Data leakage.** ICBHI audio was cut into overlapping 5-second clips at about a 1-second stride and split at random over clips. Near-identical audio from the same patient sat in both training and testing.
2. **Wrong labels.** Each patient's diagnosis (Asthma, Bronchiolitis, Healthy, Pneumonia) was stamped on every second of their audio. A pneumonia patient does not crackle every second, so the model learned to recognise patients, not sounds.

The only honest number for the old model was the field test: **6 of 15 recordings = 40% agreement** (95% CI 19.8–64.3%, p = 0.148 against 25% chance, so not distinguishable from guessing).

### What was changed

- **New labels, from the sound, not the diagnosis.** Each breathing cycle is labelled from ICBHI's own crackle/wheeze annotations:

  | Crackles | Wheezes | Label |
  |---|---|---|
  | no | no | Healthy |
  | yes | no | Crackles |
  | no | yes | Wheezing |
  | yes | yes | Wheezing with Crackles |

  The labels were retrained, not renamed. Class order is alphabetical, `Crackles, Healthy, Wheezing, Wheezing with Crackles`, because Edge Impulse always outputs classes alphabetically. That order is fixed in one config file and checked at every step.
- **Split by patient.** Whole patients go to training, validation or testing, never two of them, before any audio is cut.
- **Split balanced by stethoscope.** ICBHI was recorded on four devices (Meditron, Littmann Classic II SE, Littmann 3200, AKG C417L). The first split balanced only the labels: 79% of training audio came from one stethoscope (AKG), and the model scored at chance on the others (14% on the Littmanns). Balancing devices across the split fixed most of that. **A change of recording device alone broke the model,** which is strong evidence that training on Resondi-device recordings matters.
- **Same input as the app:** 1-second windows at 16 kHz (16,000 samples), 13 MFCCs, a small 1-D CNN. Verified by loading the app's deployed model in Node.

### The data

ICBHI 2017: 920 recordings, 126 patients, 6,898 breathing cycles, all used.

| Group | Patients | Cycles | Used for |
|---|---|---|---|
| Training | 65 | 4,850 | learning |
| Validation | 30 | 997 | choosing the best training round |
| Test | 31 | 1,051 | the final score, used once |

### Results (real, reproduced, on the 31 test patients the model never saw)

Balanced accuracy averages the four classes equally. "Healthy" is about half of all cycles, so a model that always says Healthy gets ~53% plain accuracy but only 25% balanced accuracy.

| Model | Balanced accuracy | Notes |
|---|---|---|
| App-sized network (8/16 filters), 1 s | 32.4% (whole cycles) | local PyTorch |
| **Wider network (32/64 filters), 1 s** | **38.1%** (whole cycles), 34.9% (1 s windows) | local PyTorch; best |
| Wider network, 3 s windows | 34.0% | longer windows did **not** help |
| **Edge Impulse build of the wider network (int8), app-style** | **33.5%**, plain accuracy 44.0% | this is the model for the app |
| Chance | 25% | |

Edge Impulse build, per class on the test clips: Crackles recall **71%**, Healthy 45%, Wheezing **9%**, Wheezing with Crackles **8%**. About half of normal breaths are flagged abnormal (mostly as Crackles).

**How to describe it:** weak but real. It is clearly above chance on unseen patients, catches most crackles and misses most wheezes. It is a screening aid; a practitioner confirms every result. Never call it validated. Never compare 33.5% balanced accuracy directly with the old 40% field agreement: different labels, test sets and metrics.

**Suggested pitch line:** "The original model's reported 71–84% was inflated by data leakage. Retrained without leakage and with sound labels, it scores 33.5% balanced accuracy on unseen patients, against 25% chance. Validating it on our own device's recordings is what the funding pays for."

### Where it stands

- **Edge Impulse:** new project `Resondi-Lung-4class` (user account Hared123), deploy version 1, int8. Studio's own test page: 39.2% accuracy on 1 s windows. Its validation used the `patient` metadata key, and Auto-weight classes was on.
- **Checked export:** the WebAssembly (browser) build passed `check_deployed_model.js`: correct four labels and 16,000-sample input.
- **GitHub:** the model is pushed to `HaredRay1/Ausculta` at commit `408971af2537276aa2c8a273bbe2dfa245fa13f1`, folder `model/resondi-lung-4class-v1/browser/`. The old model folder is kept.
- **The app (Base44):** published to the live app on 10 Nov, 00:12 UTC (checkpoint `6af2615526e226d3ac75e9f5`); the live bundle loads commit `408971af`. **Not yet tested end to end with a real recording.** The switch, applied in the app's code on 9 Nov:
  - the model URL is pinned to that commit;
  - the new labels are used;
  - audio is scaled to int16.

  Run in Node, the app's new code path reproduced the checker exactly (44.0% accuracy, 33.5% balanced). Still not done: an "Analysed with the earlier model" note on old results (needs a builder turn for the i18n text).
- **Scaling finding (app review item A6):** the app fed −1..1 audio while the model expects int16 scale. On the old model this never changed the top label (270/270 windows), but moved scores by up to 0.25. Fixed in the new code path.

### Next steps, in order

1. Test one real recording end to end in the live app.
2. **Collect the local dataset:** Filipino patients, recorded on the Resondi device, each breathing cycle labelled independently by two clinicians, with ethics approval and consent. Target: at least 100 patients and at least 100 cycles per class. This is what the ₱46,000 local recording line pays for. The full procedure is in `model-rebuild/docs/LOCAL-DATASET-INTEGRATION` (Markdown, Word and PDF).
3. Add HF_Lung_V1 (Taiwan; event-labelled, which fits these sound labels), **once a working copy is found** (see section 4).
4. Optional: 5-fold patient cross-validation, so every ICBHI patient is tested once (about 30–40 minutes on the PC). Offered, not yet run.
5. Try mel-spectrogram input with a 2-D CNN.

Measure every change on the same 31 test patients.

### Files (in `C:\Users\Hared\Downloads\Resondi\model-rebuild\`)

- `README.md`: setup, commands, results.
- `config/config.json`: the single source for labels, audio, MFCC, network, training and split.
- `scripts/`:
  - `prepare_data.py`, `train.py`, `evaluate.py`: the pipeline;
  - `export_onnx.py`, `export_edge_impulse.py`: exports;
  - `check_deployed_model.js`: checks an Edge Impulse export;
  - `add_local_dataset.py`: checks and imports local data.
- `docs/EDGE-IMPULSE-RETRAINING.md`, `docs/LOCAL-DATASET-INTEGRATION.*`, `docs/LIMITATIONS.md`.
- `results/`: every evaluation report. The first, unbalanced split's results are in `results/run1-split-by-class-only/`.
- `deploy/resondi-lung-4class-v1/browser/`: the checked Edge Impulse build.
- `app/labels.js`: labels, display names and model version for the app.
- `../app-changes/model-4-class-labels.md`: the app change and its status.

---

## 2. Other work since 6 November

- **Q&A:** `final/04-Resondi-Judge-QA` now has 126 questions, including a new section "The retrained model" with nine answers. One is marked to decide before pitch day: whether the new model is live in the app. `final/16` (the 30-question Answer Bank, 4 Nov) does not yet mention the retrain.
- **Heart validation set:** the CirCor DigiScope dataset (Oliveira et al., 2022; PhysioNet; ODC-By) is downloaded to `Downloads\circor\`.
  - **The set:** 25 blinded recordings, S01–S25, 5 each of: no murmur, holosystolic, early-systolic, mid-systolic, and diastolic (4 of the 5 also have a systolic murmur). They are in `Resondi\heart-validation\` with instructions and an answer sheet.
  - **The key:** in `Downloads\Resondi-private\heart-validation-key\`. Never give it to the cardiologist.
  - **Drive folder:** "Resondi – CirCor Heart Sound Review" in Hared's Drive. The 25 WAVs must be dragged into its `recordings` folder by hand.
- **Chapters 1–3** of the research paper are revised in `Resondi\chapters\`, with a full revision log. The originals held text from other papers: a cybersecurity framework, chronic kidney disease, *Ardisia squamulosa* data analysis, and body shaming. Yellow highlights mark facts only the team can supply.
- **Concept note:** Figure 2 was replaced by a correct VER 2.0 block diagram (no Bluetooth, no preamplifier; Wi-Fi access point; the gateway shown as not built). The Blender concept render was added after Figure 1.
- **Certificates:** the signed certificates still say "Ausculta" and must not be edited. Unsigned re-sign copies with the Resondi name are in `final/17-Resondi-Certificates-to-Re-sign`. The draft CirCor certificate in Drive calls heart samples "respiratory"; fix that before a doctor signs it.
- **Google Drive:** Drive for desktop is installed and was syncing all of Downloads. The user is switching it to sync only `Downloads\Resondi`, so large datasets and private files stay off Drive.

## 3. Rules that still hold

- Never quote 71–84% as model performance.
- Never call the model validated, or say it diagnoses anything. It describes sounds, and a practitioner confirms every result.
- Never say the new model is live in the app without checking.
- The lung model must never be run on heart recordings. Heart Mode records only; there is no heart model yet.
- Keep the answer key, the survey CSV (names and e-mails) and any credentials out of anything shared.

---

## 4. Added 10 November (later)

### Test split, for quick reference
Test = **31 patients, 1,051 breathing cycles**, none used in training. Split by cycles **70 / 15 / 15** (train 65 patients / 4,850 cycles; validation 30 / 997; test 31 / 1,051). By patients about 52 / 24 / 25%, because patients have different numbers of recordings. Stethoscopes are balanced across all three groups.

### HF_Lung_V1 is NOT available (correction)
- `Resondi\HF_Lung_V1\` is an **empty, broken git clone** from 2 Nov, 21:06 (64 KB, no audio).
- The source repository `github.com/techsupportHF/HF_Lung_V1` (the address in Hsu et al., 2021, PLOS ONE, CC BY 4.0) now returns **404 Not Found**. Every project document that gives this link points at a dead address.
- Before using HF_Lung, find a copy that clearly comes from the original authors under the same licence, or email the authors (the paper lists a contact). Not yet done.

### Plan to raise test accuracy honestly (agreed direction, not yet run)
Keep the 31 test patients untouched throughout. In order:
1. **Mel-spectrogram input with a 2-D CNN** instead of 13 MFCCs. In Edge Impulse this is the **MFE** block, so the app still sends 1 s of raw audio and needs no change.
2. **Data augmentation** (clinic noise, small time shifts, gain). Edge Impulse has a Data augmentation checkbox.
3. **Two yes/no detectors** (crackles present?, wheeze present?) combined into the four labels.
4. **HF_Lung_V1,** once a working copy exists.
5. **Local Resondi recordings,** the only route to performance on the device and on Filipino patients.

Never: move test patients into training, pick the model by its test score, re-split until a lucky split, or drop hard classes. Realistic expectation: strong published ICBHI 4-class models reach about 50–60% on the standard benchmark score; reaching the 40s would be a solid, defensible gain. Options 1–2 were offered as a local run (about 1–2 hours) and have not been started.

### Canva deck fixes given to the user (pages 29 and 31; the user edits Canva herself)
- **Page 31 blank:** "Target: ≥ 50% agreement on ≥ 300 recordings by month 16, every result still confirmed by a practitioner."
  - 300 = the concept note's clinical validation target (300 paired recordings, ₱120,000).
  - Month 16 = end of Phase 5 (Validation, months 12–16).
  - 50% on 300 gives a 95% CI of about 44–56%, clearly above 25% chance.
- **Page 31, other fixes:** "about 33% by chance across 3 lung classes" → "25% by chance across 4 lung sound classes"; "Ausculta hardware" → "Resondi hardware"; funded fix "₱22K / ₱15K / ₱51K" → "₱46K Filipino recordings labelled by clinicians · ₱20K noise reduction and faster quality check · ₱120K clinical validation". Optional: add the leakage disclosure and the 33.5% retrained result to "Why the gap".
- **Page 29:** 0.79 → 0.92 (Kim et al., 2025; 2,402 recordings) is correct, but needs the arrow and the citation next to it. Steps 02/03 describe planned fusion as built:
  - 02 → "Convert the sound into MFCC features";
  - 03 → "Classify with a CNN: lungs normal / wheeze / crackle / both*";
  - footnote → "*Feature fusion and heart classification are planned".

### Google Drive
- **How it syncs:** the local folder mirrors to the link-shared My Drive folder "Resondi" via the scheduled task "Resondi Drive Sync" (robocopy; the PC is the master copy). Anyone with the link can open what syncs.
- **Keep out of it:** names or e-mails (survey export, `workspace-members.csv`), patient data and screenshots, PRC and phone numbers, future local recordings, the heart-validation answer key, and any passwords or tokens. Put private files in `Downloads\Resondi-private\`.
- **Recommended, not yet done:** move `app-changes\app-review-2026-11-09.md` into `Resondi-private`. It describes exploitable app security flaws step by step.
- **Already excluded from sync:** `model-rebuild\export`, `work`, `work-3s`, `history-run1`, `.git`, `node_modules`, `.claude`.
- **Scan on 10 Nov:** no real e-mails, phone numbers or keys found in the synced folder.

### Q&A
`final/04` now has 126 questions, including the section "The retrained model". Its question about whether the model is live can now be answered "yes, the app runs it", because the app was published 10 Nov. Still test one real recording first.
