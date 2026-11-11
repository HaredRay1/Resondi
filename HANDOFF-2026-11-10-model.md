# Resondi handoff: lung model rebuild and recent work (9–11 November 2026)

Paste this into Claude chat to bring it up to date. It covers what changed on 9–11 November. The project's full state is in `CLAUDE.md` in the Resondi folder; where they disagree, this file is newer on the points below.

> **Latest (11 Nov), in five lines:**
> 1. **The new 4-class model is live in the app** and works end to end. On Resondi device recordings, however, its output is close to a random guess (section 5).
> 2. **Ten training versions were tried** (MFE, augmentation, two detectors, mixup). The best scored **35.0% balanced on the 31 test patients**, no better than the deployed v1 (33.5%). Tuning on public data has hit its ceiling (section 4).
> 3. **The next gain needs data:** clinician-labelled Resondi device recordings first, then HF_Lung_V1 once a working copy is found.
> 4. **The 40% field figure:** the paper gives no record of who set the 15 reference labels or how (section 5).
> 5. **Everything is on GitHub** (`HaredRay1/Resondi`, private, branch `master`).
>
> **12 Nov 00:45, NEW BEST MODEL:** FDC-FS three-branch fusion trained on **ICBHI + rebalanced SPRSound** (pre-specified on validation) scored **39.4% balanced accuracy on the 31 ICBHI test patients** (95% CI 28.4–44.6, patient bootstrap) and **57.2% on 230 held-out SPRSound children** (46.7–63.4). It is the best pre-specified test result of the project; previous results were 32.9–36.7%, and the deployed v1 scored 33.5%. Every confidence interval still overlaps, so it is an improvement, not yet a proven one. See section 6, "ICBHI + SPRSound round".
>
> **11 Nov afternoon:** the fusion study's single test run is done. **Fusion did not beat the single models on unseen patients**: late fusion (pre-specified) scored 32.9% balanced, FDC-FS 36.7%, MFCC 36.1%, and every confidence interval overlaps. Adding SPRSound unbalanced broke healthy-breath detection; a rebalanced version is being gate-checked. The ICBHI-only models are saved as a checkpoint. See section 6.
>
> **In progress (11 Nov, morning), see section 6:**
> - A feature-fusion study (MFCC + spectrogram + chromagram, after Tariq et al. 2022) is training.
> - The SPRSound dataset (Asian children, CC BY 4.0) is downloading, to be added as training data.
> - The 3-D spin video is rendering.

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
- **The app (Base44):** published to the live app on 10 Nov, 00:12 UTC (checkpoint `6af2615526e226d3ac75e9f5`); the live bundle loads commit `408971af`. **Tested end to end on 10 Nov** on all 45 stored lung recordings (section 5). The "earlier model" note on old results was published at 08:12 UTC (checkpoint `6af2d12594c68b17af6d8aca`). The switch, applied in the app's code on 9 Nov:
  - the model URL is pinned to that commit;
  - the new labels are used;
  - audio is scaled to int16.

  Run in Node, the app's new code path reproduced the checker exactly (44.0% accuracy, 33.5% balanced). The "Analysed with the earlier model" note is now done: English and Filipino, shown on the patient result page, the practitioner review card and the PDF export. A Filipino speaker should check its wording.
- **Scaling finding (app review item A6):** the app fed −1..1 audio while the model expects int16 scale. On the old model this never changed the top label (270/270 windows), but moved scores by up to 0.25. Fixed in the new code path.

### Next steps, in order

1. ~~Test one real recording end to end in the live app.~~ Done 10 Nov (section 5). Still to check by eye: the result screens, using a patient test account and a new recording.
2. **Collect the local dataset:** Filipino patients, recorded on the Resondi device, each breathing cycle labelled independently by two clinicians, with ethics approval and consent. Target: at least 100 patients and at least 100 cycles per class. This is what the ₱46,000 local recording line pays for. The full procedure is in `model-rebuild/docs/LOCAL-DATASET-INTEGRATION` (Markdown, Word and PDF).
3. Add HF_Lung_V1 (Taiwan; event-labelled, which fits these sound labels), **once a working copy is found** (see section 4).
4. Optional: 5-fold patient cross-validation, so every ICBHI patient is tested once (about 30–40 minutes on the PC). Offered, not yet run.
5. ~~Try mel-spectrogram input.~~ Done 11 Nov with a 1-D CNN: no gain (section 4). A 2-D CNN on MFE is the one untested idea; it is about 6 hours per version on this PC but quick on Edge Impulse's servers.

Measure every change on the same 31 test patients.

### Files (in `C:\Users\Hared\Downloads\Resondi\model-rebuild\`)

- `README.md`: setup, commands, results.
- `config/config.json`: the single source for labels, audio, MFCC, network, training and split.
- `scripts/`:
  - `prepare_data.py`, `train.py`, `evaluate.py`: the pipeline;
  - `export_onnx.py`, `export_edge_impulse.py`: exports;
  - `check_deployed_model.js`: checks an Edge Impulse export;
  - `add_local_dataset.py`: checks and imports local data.
- `scripts/experiment.py` (compares versions on validation only) and `scripts/final_test.py` (scores one chosen version on test, once, and logs every test run).
- `docs/EDGE-IMPULSE-RETRAINING.md`, `docs/EDGE-IMPULSE-IMPROVEMENTS.md` (what to change in Edge Impulse, click by click), `docs/LOCAL-DATASET-INTEGRATION.*`, `docs/LIMITATIONS.md`.
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
- The new model **is** live in the app (checked 10 Nov). Say "deployed and working end to end." **Never say it performs on the Resondi device:** on device recordings its output is close to a random guess.
- Never swap the 40% field figure for a test-set figure. They measure different models on different audio (section 5).
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

### Plan to raise test accuracy honestly (run on 11 Nov; the results follow below)
Keep the 31 test patients untouched throughout. In order:
1. **Mel-spectrogram input with a 2-D CNN** instead of 13 MFCCs. In Edge Impulse this is the **MFE** block, so the app still sends 1 s of raw audio and needs no change.
2. **Data augmentation** (clinic noise, small time shifts, gain). Edge Impulse has a Data augmentation checkbox.
3. **Two yes/no detectors** (crackles present?, wheeze present?) combined into the four labels.
4. **HF_Lung_V1,** once a working copy exists.
5. **Local Resondi recordings,** the only route to performance on the device and on Filipino patients.

Never: move test patients into training, pick the model by its test score, re-split until a lucky split, or drop hard classes. Realistic expectation: strong published ICBHI 4-class models reach about 50–60% on the standard benchmark score; reaching the 40s would be a solid, defensible gain.

### Result of that plan (run 11 Nov, 00:38–02:50)
`scripts/experiment.py` trained 10 versions with 3 seeds each and scored them on the **30 validation patients only**. Cycle balanced accuracy, chance 25%:

| Version | Score | ± |
|---|---|---|
| MFCC + two detectors | 44.2% | 1.3 |
| MFCC (the app's design) | 43.9% | 2.8 |
| MFCC + augmentation | 43.1% | 2.4 |
| MFE + two detectors | 42.7% | 1.4 |
| MFE: full range, −72 dB floor, augmentation, mixup | 34–38% | |
| MFE 50–2000 Hz | 31.4% | 0.6 |

- An MFE scaling bug (int16 energies saturating 72% of inputs) was found and fixed during the run. The invalid first MFE results are kept in `results/experiments-validation-run1-mfe-bug.csv`.
- **The two-detector head was the only idea that clearly helped,** and only for MFE (+5 points). Nothing beat the app's MFCC design by more than the seed-to-seed spread. A 2-D CNN was not run, because it takes about 6 hours per version on this PC.
- **Single test run** (`scripts/final_test.py baseline`, logged in `results/final-test-log.csv`): the app's MFCC design, best of 3 seeds chosen on validation (47.2%), scored **35.0% balanced** on the 31 test patients (accuracy 38.5%, macro F1 0.31). Per-class recall: Crackles 0.73, Healthy 0.30, Wheezing 0.11, Wheezing with Crackles 0.26.
  - The 12-point drop from validation to test shows that choosing among many versions on 30 patients flatters the winner.
  - On test, this is no better than the deployed v1 (33.5%) or the 9 Nov local model (38.1%).
- **Conclusion:** changing settings on ICBHI has reached its ceiling at about 33–38% on test patients. The next real gain needs **more or different data**: HF_Lung_V1 once a sanctioned copy exists, and above all clinician-labelled Resondi device recordings. Keep the deployed v1. Do not redeploy for this result.

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
- **Done 10 Nov:** the app security review (`app-review-2026-11-09.md`, which describes exploitable flaws step by step) now lives in `Downloads\Resondi-private\app-security-review\`, outside the synced and pushed project. It was removed from Drive and from the current GitHub tree, but it is still in the private repo's history (commits `33be00e`–`163a0cc`).
- **Already excluded from sync and git:** `model-rebuild\export`, `work`, `work-3s`, `work-exp` (the 1 GB experiment cache, added 11 Nov), `history-run1`, `.git`, `node_modules`, `.claude`.
- **Still yours to do:** set the Drive folder's sharing to Restricted.
- **Scan on 10 Nov:** no real e-mails, phone numbers or keys found in the synced folder.

### Q&A
`final/04` now has 126 questions, including the section "The retrained model". Its question about whether the model is live can now be answered "yes, the app runs it". It has been tested end to end; add that on Resondi device audio it is not yet reliable (section 5).

---

## 5. Added 11 November

### Live-app test of the new model (10 Nov, read-only)
Full write-up: `model-rebuild/results/live-app-device-test-2026-11-10.md`.
- **Pipeline:** the published app's own classifier ran on all **45 stored lung recordings** with no errors, about 1.8 s each, and every result carried the new model version. Nothing was saved or changed.
- **On the 33 Resondi device recordings** (`AUSCULTA00xx.WAV`), the top score is only **27–34%** (median 30%), close to the 25% of a random guess. Labels: Healthy 20, Crackles 7, Wheezing with Crackles 6, Wheezing 0. On ICBHI-style files the top scores reach 41–48%.
- **Cause: the microphone, not loudness.** Normalising every device file to −20 dBFS changed 0 of 33 labels. The INMP441 MEMS microphone sounds different from ICBHI's four stethoscopes. The first training run showed the same effect: a model trained mostly on one stethoscope scored at chance on the others.
- **Not checked by eye:** the result page, the practitioner page and the earlier-model note. Use a patient test account and a new recording, because re-analysing a stored recording deletes its result and reviews.

### Where the 40% field figure comes from
- **Source:** the 83-page paper, abstract (page 1) and Results, Figure 4.6 "Classification Agreement Summary" (page 12): "Of the 15 recordings evaluated, 6 produced matching classifications," meaning 40%, with McNemar p = 1.000.
- **Most likely from:** the Methods describe "Device Unit Testing" and clinical validation "among three patients at a private hospital in Puerto Princesa City" under an attending physician.
- **The paper does not record:**
  - what the reference label was;
  - who assigned it;
  - whether that person saw the AI's answer first;
  - which 15 recordings were used;
  - the per-recording results.
- **The three pulmonologists** in the paper reviewed the ICBHI training sounds, not these 15.
- In the AM-P02 interview (page 20), the user describes an earlier validation where a teammate joined a doctor's appointment. That was about the earlier prototype, so it may not apply here.
- **Ask the team:** which 15 files, what each reference label was, who gave it, and whether it was blinded. If the 15 can be matched to the `AUSCULTA00xx.WAV` files, the new model can be scored on them: the first honest device-audio number.
- **Do not replace 40% with a test-set figure.** They measure different models on different audio. Report both, labelled. Suggested wording: *"In field testing, the first model agreed with the reference on 6 of 15 device recordings (40%). We then found that model's training was flawed and rebuilt it with sound labels and a patient-wise split. On 31 unseen patients it scores 44.0% accuracy (33.5% balanced, chance 25%). On our device's recordings it is not yet reliable; clinician-labelled device recordings are what the funding buys."*

### Model experiments (11 Nov)
See section 4, "Result of that plan". In short, the best test result is **35.0% balanced**, and tuning has reached its ceiling. A bug that made the mel-spectrogram (MFE) features meaningless was found and fixed mid-run. For Edge Impulse:
- Keep MFCC.
- If you change anything, turn on Auto-balance and Data augmentation.
- If you try MFE, leave the high frequency at 8000 (cutting it to 2000 cost about 6 points), and pair it with a 2-D CNN.
- Click-by-click steps are in `model-rebuild/docs/EDGE-IMPULSE-IMPROVEMENTS.md`.

### Other 11 Nov items
- **GitHub:** `HaredRay1/Resondi` (private, branch `master`) holds the project. Large datasets and caches are excluded.
- **Product image:** `figures/Resondi-Device-Podium.png` (and `.jpg`) recreates the old Ausculta podium photo with the new device render. It uses `build/dev2/render_podium.py` (Blender, Cycles) and `build/dev2/compose_podium.py` (pink glow). It is not yet committed to git.
- **Video:** the user asked for `ayun.mov` to be recreated, but no file by that name was found in the user profile or on Google Drive. Another session built a product video that copies the camera work of the team's earlier clip: 6.7 s, 1080p, 30 fps, four camera moves, dark studio floor, no text (`build/dev2/render_spin_video.py`). It stopped after 16 frames when the app restarted and was resumed at 06:28 (see section 6).
- **"Why us?" line** (for the deck): *"We've already built both ends: a working stethoscope and a live platform. Now we're making every breath and heartbeat count."*

### Open items
1. Find out where the 15 field-test reference labels came from (see above).
2. Check the result screens by eye with a patient test account.
3. Collect clinician-labelled Resondi device recordings: the only route to device accuracy.
4. Find an author-sanctioned copy of HF_Lung_V1, or email the authors.
5. Optional: train an MFE 2-D CNN in Edge Impulse (on their servers).
6. Set the Drive folder to Restricted, and have a Filipino speaker check the earlier-model note.
7. Find or re-supply `ayun.mov` if it still needs recreating, and finish the spin video.

---

## 6. In progress, 11 November (status at 08:15)

### Feature-fusion study (the user's request)
**Why:** the concept note and deck describe a planned three-branch fusion model after **Tariq, Shah & Lee (2022), *Sensors* 22(4), 1521, "FDC-FS"**: three CNNs on a spectrogram, MFCC and chromagram, joined and passed to a dense layer. Its reported 99.1% is almost certainly inflated by the same random split that leaked in our old model. This study tests whether fusion helps under the honest patient split.

**What runs** (`model-rebuild/scripts/fusion.py`): same 1-second windows, same patient split, same 1-D CNN branch (32/64 filters), 3 seeds each, chosen on the **30 ICBHI validation patients only**. Results go to `results/fusion-validation.csv` and the log `results/fusion-run-icbhi.log`. The versions:

| Version | Input |
|---|---|
| `single_mfcc` | 13 MFCCs (the app's design) |
| `single_spec` | log power spectrogram, 0–4 kHz, 129 bins, 20 ms frames |
| `single_chroma` | 12-bin chromagram, 50–4000 Hz, 64 ms frames |
| `late3` | the three single models vote (their probabilities averaged) |
| `fdc3` | FDC-FS style: three branches → concatenate (3 × 64) → dense → 4 classes (190k parameters) |
| `fdc2_nochroma` | `fdc3` without the chroma branch (chroma ablation) |

**Results so far** (cycle balanced accuracy, chance 25%):
- `single_mfcc` **45.5% ± 0.3**. Recall: Crackles about 0.80, Healthy 0.25, Wheezing 0.41–0.50, W+C 0.27–0.36.
- `single_spec` **44.8% ± 3.0** (48.9, 43.1, 42.3). It finds about twice as many healthy breaths (0.46–0.51) and more wheezes. MFCC is stronger on crackles.
- `single_chroma` **41.2% ± 1.0**. It is weak alone, and its best epoch came early.
- **`late3` (the three models vote): 48.2% ± 2.4** (50.2, 49.6, 44.9), F1 up to 0.46. **The best result of the whole project, and the first change that clearly beat MFCC alone (+2.7 points).** Recall: Crackles 0.73–0.78, Wheezing 0.63–0.69, Healthy 0.33–0.41; Wheezing with Crackles is still weak (0.02–0.20).
- **`fdc3` (FDC-FS, three branches trained as one network): 46.9% ± 1.4** (48.8, 46.1, 45.7). Steadier than `late3`, with Healthy recall 0.50 in every seed (MFCC alone gets about 0.25, so fewer false alarms).
- `fdc2_nochroma` **43.9% ± 3.3**. Dropping chroma costs 3 points, so the chromagram adds information even though it is weakest alone.
- **ICBHI-only round complete (11:56).** Ranking: late3 48.2 > fdc3 46.9 > MFCC 45.5 > spec 44.8 > fdc2 43.9 > chroma 41.2. Both fusion methods beat every single model.
### TEST RESULT of the ICBHI fusion study (another session's `scripts/fusion_eval.py`, finished 14:53)
- **Pre-registration:** late fusion (late3) was named the primary model, on validation, before any test patient was read. Every version was then scored once on the 31 ICBHI test patients (1,051 cycles).
- **Outputs:** full report in `model-rebuild/results/stats/fusion-report.md`, with charts and jamovi CSVs in the same folder; every row is logged in `results/final-test-log.csv`.

| Model | Test balanced acc. (95% CI) | Macro-F1 | Kappa | ICBHI score* |
|---|---|---|---|---|
| **Late fusion (PRIMARY)** | **32.9%** (23.9–40.9) | 0.31 | 0.16 | 42.7 |
| FDC-FS three-branch | 36.7% (26.0–43.0) | 0.36 | 0.21 | **47.7** |
| MFCC alone | 36.1% (28.3–44.0) | 0.32 | 0.16 | 39.4 |
| Chromagram alone | 42.1% (31.0–48.7) | 0.35 | 0.19 | 40.4 |
| Fusion without chroma | 34.5% (24.7–41.5) | 0.33 | 0.18 | 43.5 |
| Spectrogram alone | 26.7% (18.8–33.4) | 0.27 | 0.07 | 37.0 |

\*ICBHI challenge score = mean of sensitivity and specificity.

- **Fusion did not carry its validation gain to the test patients.** Late fusion led on validation (48.2%) but scored 32.9% on test, below MFCC alone. Every confidence interval overlaps the others, so with 31 patients none of these models is clearly better than another.
- **Chromagram alone scored best on test (42.1%), but it cannot be chosen now:** picking a model by its test score would leak the test set. Report it as an observation only.
- **FDC-FS** has the best ICBHI challenge score (47.7) and finds the most healthy breaths (57%), meaning fewer false alarms. It is still not significantly better.
- **Honest summary:** fusion, like every other tuning tried on ICBHI, lands at about 33–37% balanced accuracy on unseen patients. The deployed v1 (33.5%) is no worse. More and better data, not architecture, is what limits the model.
- **All of these models fail on children:** 23–32% on the SPRSound test children (chance 25%).

### SPRSound round (in progress)
1. **First attempt (unbalanced), stopped:** with SPRSound added, MFCC found 0–2% of ICBHI's healthy breaths. SPRSound is 82% healthy and recorded from children, so the model learned "healthy = a child's breath". Band-limiting to 0.1–3.9 kHz, levelling and per-source normalisation (`--bandlimit --srcnorm`) did not fix it.
2. **Fair baseline (ICBHI only, same filtering, `icbhi-bl4k`):** the filtering alone costs 1–4 points on ICBHI validation: MFCC 43.4%, spectrogram 43.5%, chromagram 39.9%, late fusion 44.0%, FDC-FS 46.9% (1 seed).
3. **Now running:** `--balance`, which keeps all SPRSound crackles and wheezes plus only as many healthy breaths as ICBHI has (20,590 of 49,417 windows), with every (dataset, class) cell weighted equally. A one-seed MFCC gate check (`scripts/run_save_and_gate.cmd`, log `results/fusion-gate.log`) decides whether the full round runs. **The user's rule: keep SPRSound only if it raises ICBHI accuracy.**

### ICBHI + SPRSound round: RESULT (user chose "option B", 11 Nov 20:31 – 12 Nov 00:24)
**Why option B:** the one-seed gate check showed SPRSound left ICBHI validation about the same (42.0% vs 43.2%) but lifted children from 12% to 48%. Resondi screens children too (childhood pneumonia), so the user chose to keep it.

**Setup:**
- **Training data:** ICBHI plus rebalanced SPRSound: all SPRSound crackles and wheezes, and SPRSound healthy capped at ICBHI's count (20,590 of 49,417 SPRSound windows).
- **Weighting:** every (dataset, class) cell carries equal weight.
- **Features:** 0.1–3.9 kHz, levelled, normalised per dataset (`fusion.py run --data icbhi+sprs --bandlimit --srcnorm --balance`).
- **Seeds and saving:** 3 seeds; every model is saved to `model-rebuild/models/fusion-icbhi-sprs-2026-11-11/` (15 files).

**Validation** (ICBHI 30 patients | SPRSound validation children):

| Version | ICBHI val | SPRSound val | Same setup, ICBHI only |
|---|---|---|---|
| **FDC-FS three-branch** | **48.7% ± 1.0** | 49.5–51.3% | 46.9% (1 seed) |
| Late fusion | 48.1% ± 1.8 | 51.6–52.9% | 44.0% |
| FDC-FS without chroma | 47.8% ± 0.4 | 50.5–52.1% | — |
| Spectrogram | 47.1% ± 0.9 | 47.1–48.8% | 43.5% |
| MFCC | 43.2% ± 1.1 | 48.2–49.6% | 43.4% |
| Chromagram | 41.2% ± 2.6 | 38.9–47.0% | 39.9% |

- **SPRSound added about 2–4 points on ICBHI validation** for fusion and the spectrogram, and lifted children from about 12–25% to about 50%.
- **The chromagram adds about 1 point inside FDC-FS** (48.7 vs 47.8). The user asked to keep it.

**Pre-specified primary:** `fdc3` seed 33, written to `results/prespec-icbhi-sprs-round.md` at 23:45, before any test read. It was scored from the saved model (`scripts/test_saved.py`). Loading was verified first: the saved models reproduce their validation scores exactly (49.9%, 50.5%).

**TEST** (`results/final-test-icbhi-sprs.md`, rows in `results/final-test-log.csv`):

| | ICBHI test (31 adults) | SPRSound test (230 children) |
|---|---|---|
| **Primary FDC-FS (seed 33)** | **39.4%** (95% CI 28.4–44.6), F1 0.38 | **57.2%** (46.7–63.4), F1 0.45 |
| ↳ Recall: Crackles / Healthy / Wheezing / W+C | 57 / **52** / 24 / 25% | 53 / 70 / 55 / 51% |
| Comparison only: late fusion s22 | 35.7% | 52.8% |
| FDC-FS without chroma s11 | 36.5% | 53.4% |
| MFCC s22 | 36.7% | 51.3% |
| Spectrogram s33 | 34.6% | 51.0% |
| Chromagram s33 | 38.9% | 45.9% |

- **The best pre-specified test result of the project.** Earlier results: MFCC baseline 35.0%; ICBHI-only late fusion (primary) 32.9%; ICBHI-only FDC-FS 36.7%; deployed v1 33.5%.
- **The validation pick held up on test:** FDC-FS was best on validation and is also the best version on both test sets.
- **Healthy recall is 52% on ICBHI,** against about 25–30% for MFCC models, so there are far fewer false alarms.
- **Caveats:**
  - The 31-patient interval (28–45%) still overlaps earlier models, so call it an improvement on unseen patients, not a proven one.
  - Wheezing remains weak on adults (24%).
  - This is the third read of the ICBHI test set; report all three.
  - Still not tested on the Resondi device.
- **Deployment:** this model cannot go into Edge Impulse as is (no chromagram block, three inputs, per-source normalisation). It would need an ONNX export run in the browser, the same 0.1–3.9 kHz filtering and levelling in the app, and, for the Resondi device, its own normalisation statistics computed from local recordings.

### ICBHI-only checkpoint (user's request: "so I can rewind")
- **Where:** `model-rebuild/models/fusion-icbhi-only-2026-11-11/`, written by `python scripts/fusion.py save`. It holds each model's weights, its normalisation and its validation score, plus `manifest.json`.
- **Saved (all 7):** MFCC seeds 22 and 11, spectrogram 11, chromagram 33 and 11, FDC-FS 11, FDC-FS without chroma 11. Late fusion = the three seed-11 single models averaged.
- **Reproducibility:** retrained scores differ from the morning logs by up to 2.3 points (spectrogram), because multi-threaded CPU arithmetic is not bit-identical. The manifest records each saved model's own score.
- **Caution:** these are validation scores. The 11 Nov MFCC winner fell from 47.2% on validation to 35.0% on test. Only the single test run counts.

**After that:**
1. Rerun the same versions with `--data icbhi+sprs`, adding SPRSound training patients.
2. Choose by ICBHI validation only.
3. Run **one** test (`python scripts/fusion.py test <recipe> --data <...>`). It scores the 31 ICBHI test patients and the held-out SPRSound test children separately, and logs to `results/final-test-log.csv`.

The bar to beat on test is **35.0%** (11 Nov, MFCC) and 33.5% (deployed v1).

**Deployment caveat:** Edge Impulse has no chromagram block, and the app runs a single Edge Impulse model. If fusion wins, it needs a different route into the app (an ONNX model run in the browser) or a custom Edge Impulse processing block.

### Added dataset: SPRSound (for training)
- **What:** SJTU Paediatric Respiratory Sound Database (Shanghai Children's Medical Center, Yunting model II stethoscope). Children aged 1 month–18 years, 292 participants in the 2022 release. **CC BY 4.0.** [github.com/SJTU-YONGFU-RESEARCH-GRP/SPRSound](https://github.com/SJTU-YONGFU-RESEARCH-GRP/SPRSound).
- **Why this one:**
  - it is labelled per breath by sound type, which fits our four labels;
  - Asian children are close to a core Resondi group (childhood pneumonia);
  - it adds a fifth stethoscope type.
- **Label mapping:**
  - Normal → Healthy;
  - Fine Crackle or Coarse Crackle → Crackles;
  - Wheeze → Wheezing;
  - Wheeze+Crackle → Wheezing with Crackles;
  - **Rhonchi and Stridor are left out** (ICBHI has no stridor, and its wheeze flag is not documented to include rhonchi);
  - "Poor Quality" records are skipped.
- **Split:** by patient, 70/15/15, separately from ICBHI. ICBHI's 31 test patients stay the main comparison.
- **Download: COMPLETE.** All 13,136 files (1.2 GB, years 2022–2025) are size-checked in `C:\Users\Hared\Downloads\sprsound\`, outside the project, so they never sync to Drive or git. git clone stalled on this connection, so they were fetched one by one with `model-rebuild/scripts/download_sprsound.py` (resumable).
- **Philippine data:** the only Filipino lung-sound corpus found is **HINGA V1** (Baguio, 51 patients). It has no public download and is diagnosis-labelled (healthy/asthma only), so it cannot train sound labels. Resondi's own clinician-labelled device recordings remain the real fix.

### Product video: DONE 08:22
- **`figures/Resondi-Device-Video.mp4`:** 6.7 s, 1920×1080, 30 fps, H.264, 1.9 MB, no text or audio. It is a concept render of the Blender model, so like the stills it is about 160 × 100 × 60 mm, not the real 173 × 80 × 70.
- **Four camera moves:** a three-quarter view of the box, a low close-up sliding along the chest piece and cable, a top-down drift, then a pull-back to a wide three-quarter view.
- **To rebuild:** `build/dev2/resume_video.ps1` renders any missing frames, then encodes.
- **Housekeeping:** the frames in `build/dev2/out/` are excluded from git and Drive.

### PC limits to know
- **Hardware:** 4 cores and 7.8 GB RAM, with free memory down to about 0.5 GB while rendering, training and downloading at once. Claude Code stopped one watcher script for low memory (the work itself kept running).
- **Long jobs:** run them as detached processes (`Start-Process`), so an app restart does not kill them, as happened at 01:52.
- **Running now (12 Nov, 00:45):** nothing. All training has finished.
- **Committed:** the research plan (`research-plan/`), the 3-minute pitch script (`final/18`) and the user guide (`final/19`), all from other sessions.

---

## 7. ALL RESULTS: comparison tables (12 Nov 2026)

**How to read them:**
- **Balanced accuracy** averages the four sounds equally; guessing scores **25%**. It is the fair single number.
- **Plain accuracy** is inflated by the many Healthy breaths.
- **Test results** come from patients the model never saw, and only they support claims. **Validation results** were used to choose versions.
- **Sources:** `model-rebuild/results/final-test-log.csv`, `fusion-validation.csv`, `experiments-validation.csv` and the run logs.

### Table 7.1 Test results: 31 unseen ICBHI adults (1,051 breathing cycles)

| Date | Model | Training data | Plain acc. | **Balanced acc.** | Macro F1 | Children (SPRSound test, 230) |
|---|---|---|---|---|---|---|
| before 9 Nov | Old app model (diagnosis labels) | ICBHI, leaky split | ~~71.1%~~ invalid | — | — | — |
| 9 Nov | Local CNN, app-sized | ICBHI | — | 32.4% | — | — |
| 9 Nov | Local CNN, wider | ICBHI | — | 38.1% | — | — |
| 9 Nov | Local CNN, 3 s windows | ICBHI | — | 34.0% | — | — |
| 9 Nov | **Edge Impulse v1 (LIVE in the app)** | ICBHI | 44.0% | **33.5%** | — | — |
| 11 Nov | MFCC (best of 10 versions) | ICBHI | 38.5% | 35.0% | 0.31 | — |
| 11 Nov | ICBHI-only fusion: late fusion (primary) | ICBHI | — | 32.9% | 0.31 | 29.9% |
| 11 Nov | ICBHI-only fusion: FDC-FS | ICBHI | — | 36.7% | 0.36 | 31.7% |
| 11 Nov | ICBHI-only fusion: MFCC | ICBHI | — | 36.1% | 0.32 | 23.3% |
| 11 Nov | ICBHI-only fusion: spectrogram | ICBHI | — | 26.7% | 0.27 | 24.4% |
| 11 Nov | ICBHI-only fusion: chromagram | ICBHI | — | 42.1%* | 0.35 | 27.6% |
| 11 Nov | ICBHI-only fusion: FDC-FS without chroma | ICBHI | — | 34.5% | 0.33 | 32.2% |
| **12 Nov** | **FDC-FS + SPRSound (primary) ⭐** | **ICBHI + SPRSound** | **47.2%** | **39.4%** (CI 28.4–44.6) | **0.38** | **57.2%** (CI 46.7–63.4) |
| 12 Nov | Late fusion + SPRSound | ICBHI + SPRSound | 46.1% | 35.7% | 0.34 | 52.8% |
| 12 Nov | FDC-FS without chroma + SPRSound | ICBHI + SPRSound | 43.1% | 36.5% | 0.35 | 53.4% |
| 12 Nov | MFCC + SPRSound | ICBHI + SPRSound | 39.3% | 36.7% | 0.32 | 51.3% |
| 12 Nov | Spectrogram + SPRSound | ICBHI + SPRSound | 38.3% | 34.6% | 0.32 | 51.0% |
| 12 Nov | Chromagram + SPRSound | ICBHI + SPRSound | 37.5% | 38.9% | 0.31 | 45.9% |

\*Not pre-specified, so it cannot be claimed (choosing by test score leaks the test set). ~~71.1%~~ was inflated by data leakage; never quote it.

**Not comparable to these:** the field test, 6 of 15 Resondi recordings = 40% (old model, device audio, reference labels undocumented).

**The ICBHI test set has been read three times** (11 Nov 02:50, 11 Nov 14:52, 12 Nov 00:25). Each time the primary model was fixed in advance. Report all three.

### Table 7.2 Validation results: 30 ICBHI patients, mean of 3 seeds (used only to choose)

| Version | ICBHI only | ICBHI only, filtered 0.1–3.9 kHz | **ICBHI + SPRSound** (filtered) |
|---|---|---|---|
| MFCC | 45.5% | 43.4% | 43.2% |
| Spectrogram | 44.8% | 43.5% | 47.1% |
| Chromagram | 41.2% | 39.9% | 41.2% |
| Late fusion | 48.2% | 44.0% | 48.1% |
| **FDC-FS three-branch** | 46.9% | 46.9% (1 seed) | **48.7%** |
| FDC-FS without chroma | 43.9% | — | 47.8% |
| *Children (SPRSound validation)* | *12–24%* | *12–24%* | ***about 48–53%*** |

**Earlier versions (11 Nov, `experiment.py`, ICBHI only, validation):**

| Version | Validation |
|---|---|
| MFCC + two detectors | 44.2% |
| MFCC | 43.9% |
| MFCC + augmentation | 43.1% |
| MFE + two detectors | 42.7% |
| Other MFE versions | 31.4–37.9% |

### Table 7.3 Per-class recall of the main models on the ICBHI test

| Model | Crackles | Healthy | Wheezing | W + C | Balanced |
|---|---|---|---|---|---|
| Edge Impulse v1 (live app) | 71% | 45% | 9% | 8% | 33.5% |
| MFCC (11 Nov) | 73% | 30% | 11% | 26% | 35.0% |
| Late fusion, ICBHI only | 60% | 47% | 21% | 4% | 32.9% |
| FDC-FS, ICBHI only | 56% | 57% | 24% | 9% | 36.7% |
| **FDC-FS + SPRSound** | 57% | 52% | 24% | **25%** | **39.4%** |

### What to say
> "We rebuilt the model without data leakage and tested fifteen designs honestly. The best is a three-branch fusion network on MFCC, spectrogram and chromagram, trained on ICBHI plus SPRSound, an Asian paediatric dataset. On unseen adult patients it scores 39.4% balanced accuracy against 25% chance. The model in our app today scores 33.5%. On unseen children it scores 57.2%. With 31 test patients the confidence interval is still wide, which is why the funding pays for clinician-labelled recordings from our own device."

**Do not say:** that it is validated, that it diagnoses, or that it works on the Resondi device. It has not been tested on device audio, and it is not yet in the app (it needs an ONNX browser route; Edge Impulse has no chromagram block).

---

## 8. In progress, 12 Nov: options A and H (user's choice)

### A. Averaging the three FDC-FS seeds (validation only, `scripts/ensemble_val.py`, `results/ensemble-validation.txt`)

| | ICBHI val | SPRSound val |
|---|---|---|
| FDC-FS single seeds 11 / 22 / 33 | 48.9 / 47.4 / 49.9% (mean 48.7) | 50.3 / 49.5 / 51.3% |
| **3-seed ensemble** | **49.5%** | **52.0%** |
| FDC-FS + late fusion, all 6 averaged | 49.3% | 52.3% |

- **About +0.8 / +1.7 points over a typical seed.** It is below the best seed (49.9%), but that seed was picked on the same patients.
- **Not tested on the 31 test patients:** that would be a fourth read. It is evaluated inside H instead.

### H. 5-fold patient cross-validation over all 126 ICBHI patients (`scripts/cv.py`, `scripts/run_cv.cmd`)
- **Why:** the 31-patient test gives a wide interval (28–45%) and has been read three times. Cross-validation tests every patient exactly once, each by a model that never saw them.
- **Folds:** 126 patients in 5 folds balanced by (label, stethoscope): 23–28 patients and about 1,370 cycles each, 6,898 cycles in total. In fold k, test = fold k, validation (early stopping only) = fold k+1, train = the other three (+ rebalanced SPRSound for FDC-FS).
- **Compared:** MFCC on ICBHI only (the app's design, seed 11) vs FDC-FS + SPRSound (seeds 11/22/33 and their 3-seed ensemble). Every fold model is also scored on the 230 SPRSound test children.
- **Resumable:** window probabilities are saved per (config, seed, fold) in `work-exp/cv/`. Re-run `scripts\run_cv.cmd` to continue. The final report goes to `results/cv-results.md` / `.json`.

**Results so far (01:45; log `results/cv-run.log`), fold test balanced accuracy:**

| Model | F0 | F1 | F2 | F3 | F4 | Mean |
|---|---|---|---|---|---|---|
| MFCC, ICBHI only | 35.9 | 37.9 | 33.7 | 33.1 | 30.0 | **≈ 34.1%** |
| FDC-FS + SPRSound, seed 11 | **40.7** | … | | | | |

- **The current design scores about 34% across all 126 patients,** matching the live app (33.5%).
- **On fold 0, FDC-FS + SPRSound beats it by about 5 points on the same patients.**
- **Expected to finish:** about 05:00. The pooled number with a 95% CI comes from `cv.py report`.
