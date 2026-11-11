# Resondi handoff: lung model rebuild and recent work (9–11 November 2026)

Paste this into Claude chat to bring it up to date. It covers what changed on 9–11 November. The project's full state is in `CLAUDE.md` in the Resondi folder; where they disagree, this file is newer on the points below.

> **Latest (11 Nov), in five lines:**
> 1. **The new 4-class model is live in the app** and works end to end. On Resondi device recordings, however, its output is close to a random guess (section 5).
> 2. **Ten training versions were tried** (MFE, augmentation, two detectors, mixup). The best scored **35.0% balanced on the 31 test patients**, no better than the deployed v1 (33.5%). Tuning on public data has hit its ceiling (section 4).
> 3. **The next gain needs data:** clinician-labelled Resondi device recordings first, then HF_Lung_V1 once a working copy is found.
> 4. **The 40% field figure:** the paper gives no record of who set the 15 reference labels or how (section 5).
> 5. **Everything is on GitHub** (`HaredRay1/Resondi`, private, branch `master`).
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
- **Next (started 11:56, detached, log `results/fusion-run-sprs.log`):** prepare SPRSound, then rerun all six with `--data icbhi+sprs`, about 3–4 hours. Then one test run for the version best on ICBHI validation.
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
- **Running now:** the training (`fusion.py run --data icbhi`), the video render and the SPRSound download are all detached processes.
- **Untracked folder:** `research-plan/` is another session's work in progress and is deliberately not committed.
