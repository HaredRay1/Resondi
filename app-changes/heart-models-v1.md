# App change, 14 Nov 2026: heart-sound models v1 (PUBLISHED)

## Status

- **Saved in the app** as checkpoint `6af81b7f647d6ad4c4c7ac20` ("Heart models v1: heart rate + murmur screening"). Every changed file compiles on the preview.
- **Published 14 Nov 2026 09:30 UTC (17:30 PHT)** at the user's request: checkpoint `6af81b7f647d6ad4c4c7ac20`, app commit `c89b50a5`. The live bundle loads the heart models from Ausculta `1e34348b` (chunk `HeartAnalysisCard-mpsoYAhW.js`); the lung model is unchanged (`c9cd3fa2`).
- **This also published the 13 Nov device Wi-Fi transfer page** (chunk `DeviceTransfer-C1Q4MX-K.js`), which was in the same saved version.
- **Rollback:** checkpoint `6af819488ec579cffb113985` ("Before heart models v1"). The `HeartAnalysis` entity was created before that checkpoint; it is new and nothing else reads it.

## What the app now does with a heart recording

On the recording page (and as a compact row on the exam summary), "Analyse heart sound" runs two models in the browser and saves a `HeartAnalysis` record:

- **Estimated heart rate (BPM):** a segmentation model labels every 20 ms as S1, systole, S2 or diastole, decoded in cardiac-cycle order; heart rate is 60 / the median interval between successive S1 sounds. When no regular heartbeat is found, it says so instead of giving a number.
- **Murmur screening flag:** a murmur model scores 6 s windows; the recording is flagged when the mean score reaches the threshold fixed on validation patients (0.7096). A patient counts as flagged when any site is, which is the same rule as the test in the IMRaD.
- **On-screen caveats (English and Filipino):** screening aid, not a diagnosis; tested on public recordings of children (CirCor), not yet on Resondi device recordings; misses about 1 in 3 murmurs, so "no murmur flagged" does not rule one out.
- **Practitioners** see the patient's result read-only on the review card. The result carries the session's `practitioner_ids` and is added and removed with the case (`src/lib/caseAssignment.js`).
- **Text updates:** the Heart Mode screen and the heart mode card no longer say analysis is unavailable. Those texts are kept in the components, because the shared `src/lib/i18n.jsx` cannot be rewritten through the API. The i18n keys `heart.modelPending`, `heart.completeDesc`, `mode.heartDesc` and `spec.cardiacDesc` still hold the old "not available" wording and are no longer shown, except `spec.cardiacDesc` (practitioner specialisation text).

## Files

| App file | Local copy |
|---|---|
| `src/lib/heartConstants.js` (generated) | `model-rebuild/app/heartConstants.js` |
| `src/lib/heartFeatures.js` | `model-rebuild/app/heartFeatures.js` |
| `src/lib/heartAnalyzer.js` | `model-rebuild/app/heartAnalyzer.js` |
| `src/components/patient/HeartAnalysisCard.jsx` (new) | `app-changes/HeartAnalysisCard.jsx` |
| `src/pages/patient/SessionDetail.jsx`, `ExamSummary.jsx`, `HeartExam.jsx`, `RecordingHistory.jsx`; `src/components/practitioner/SessionReviewCard.jsx`; `src/components/patient/AuscultationModeCards.jsx`; `src/lib/caseAssignment.js` | edited in place (show the card, delete heart results with the recording, practitioner access, texts) |

- **Entity `HeartAnalysis`:** `session_id`, `practitioner_ids`, `heart_rate_bpm`, `beats_detected`, `murmur_score`, `murmur_flag`, `seconds_analyzed`, `model_version` (`resondi-heart-v1`), `generated_at`. Same row-level rules as `AIAnalysis`. It is kept apart from `AIAnalysis` so that the lung charts, trends and severity code never read a heart result.
- **Models:** `model-rebuild/scripts/export_heart_onnx.py` → `model-rebuild/deploy/resondi-heart-v1/` (segmentation 0.47 MB, murmur 3-seed ensemble 1.6 MB; ONNX vs PyTorch max difference 1e-6). Hosted at `HaredRay1/Ausculta` commit `1e34348bf5cd536cc35b33fbfa43137cac5052c5`, `model/resondi-heart-v1/`, via jsDelivr (pinned). `model.json` carries the CirCor ODC-By attribution. Runtime: the same `onnxruntime-web@1.20.1` as the lung model.

## Checks

- **App audio path in Python** (`scripts/heart_app_path.py`, `results/heart-app-path-check.md`): the 631 CirCor test recordings were upsampled to 16 kHz and put through the app's path (FIR low-pass, every 4th sample).
  - Heart rate error 3.03 BPM, against 3.01 on the training path.
  - Murmur: sensitivity 25/36 against 24/36, specificity 97.1% for both, and the murmur flag the same on 99.7% of recordings.
- **Browser code against Python in Node** (`scripts/check_heart_js.mjs`, `results/heart-js-parity.json`): 25 test recordings, with the same heart rate and murmur flag on 25 of 25. The largest murmur score difference was 2e-5.
- **Real browser on the app preview (Chrome):** `analyzeHeart` was run on 8 CirCor test recordings. Heart rate, S1 count and murmur score matched Python to 4 decimals. The first run took 4.4 s including the model download, later runs 0.3–0.8 s.
- **Not checked:**
  - the result card by eye with a patient account (admin is redirected away from patient pages);
  - any Resondi device heart recording. The 5 stored heart sessions are short test uploads of 0–12 s.

## What this does not change

The heart models are tested on CirCor only. The IMRaD and research plan were updated on 14 Nov to say the models run in the application, which is now true. The papers also say that the models went into the application before the device test the plan had put first, and that every heart result there is marked as a screening aid.
