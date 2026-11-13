# App changes, 13 Nov 2026: fusion model v2 (LIVE) and device Wi-Fi transfer (saved, NOT published)

## 1. Fusion lung model v2: PUBLISHED

- **Live since** 13 Nov 2026 03:43 PHT (19:43 UTC on 12 Nov). Deployed checkpoint `6af616ece0e4bcab64cebaa1`, app commit `2c5d4be9`. Rollback: checkpoint `6af615ea1b4884b2d1659ea3` ("Before fusion model v2", the Edge Impulse 4-class v1).
- **Model:** the FDC-FS fusion ensemble (seeds 11/22/33, MFCC + spectrogram + chromagram, ICBHI + SPRSound) as one ONNX file, 2.3 MB, with ICBHI normalisation built in. Exported by `model-rebuild/scripts/export_fusion_onnx.py` to `model-rebuild/deploy/resondi-lung-fusion-v2/`; ONNX vs PyTorch max difference 2.7e-7.
- **Hosting:** `HaredRay1/Ausculta` commit `c9cd3fa2ca625a585efc6fb3f75734f585badfae`, `model/resondi-lung-fusion-v2/`, served by jsDelivr. Runtime: `onnxruntime-web@1.20.1` (wasm, 1 thread) from jsDelivr.
- **App files:** `src/lib/lungClassifier.js` (copy: `model-rebuild/app/lungClassifier.fusion-v2.js`) and the new `src/lib/fusionFeatures.js` (copy: `model-rebuild/app/fusionFeatures.js`), which reproduces `scripts/fusion.py` in the browser: 100–3900 Hz band cut + -20 dBFS levelling per 1 s window, MFCC, spectrogram, chromagram, float16 rounding. Interface unchanged (`analyzeAudio`, `MODEL_VERSION`), so no page changed.
- **`model_version` saved with new analyses:** `resondi-lung-fusion-v2`. Analyses from 10–13 Nov carry `resondi-lung-4class-v1`; empty = the withdrawn diagnosis model.
- **Checks:**
  - browser feature code vs Python: same top label on 600/600 validation windows (`model-rebuild/results/fusion-browser-parity.txt`); the full browser path (JS features + onnxruntime-web) in Node: 300/300.
  - Chrome, app preview: a synthetic 15 s recording gave the same four scores as Python to 4 decimals; 5.4 s including the first model download.
  - live bundle verified to load commit `c9cd3fa2` (chunk `lungClassifier-C0psc4D0.js`).
  - **live test on all 45 stored lung recordings, read-only:** 45/45 ran. On the 26 unique Resondi device recordings the top score is 31–66% (median 41%), against 27–34% for v1. More decisive, not proven more correct: no reference labels. `model-rebuild/results/live-app-device-test-fusion-2026-11-13.md`.
- **Not checked:** the result screens by eye with a patient account (admin is redirected away from patient pages).

## 2. Device Wi-Fi transfer page: SAVED, NOT PUBLISHED

- **Status:** written into the app and compiles on the preview, saved as checkpoint `6af61921f6933d43a3bb0ce0` ("Device Wi-Fi transfer page + fusion v2"). Publishing it was blocked by a permission check on 13 Nov, so the live app does not have it yet. To publish: Base44 editor → Publish, or deploy that checkpoint.
- **Files:** new `src/pages/patient/DeviceTransfer.jsx` (copy: `app-changes/DeviceTransfer.jsx`); `src/App.jsx` adds the route `/patient/record/device`; `src/pages/patient/FullExam.jsx` adds a "Transfer from Resondi device (Wi-Fi)" button under "Start exam".
- **What it does:**
  1. tells the user to join `RESONDI_WIFI`;
  2. opens the device's own page `http://192.168.4.1` in a new tab to download the recordings (AUSCULTA00xx.WAV);
  3. tells the user to reconnect to the internet;
  4. the user picks the downloaded WAVs (several at once), sets each chest site (or "Fill sites in guided exam order"), and uploads. Each becomes an `AuscultationSession` (private file, duration read from the WAV header) in one exam group, then "Open exam and run analysis" opens the exam summary.
- **Why not a direct transfer:** the app is HTTPS, the device serves plain HTTP on a local address, and browsers block an HTTPS page from fetching `http://192.168.4.1` (mixed content / private network access). The phone also has no internet while it is on the device's Wi-Fi. So the phone carries the files.
- **What this does and does not change in the pitch:** it replaces "memory card carried by a person" with "phone carries the file over the device's Wi-Fi". It is **not** the Tier 2 gateway: nothing moves from device to platform automatically. That still needs a firmware change (device joins a clinic Wi-Fi and uploads, or a native app), which is what the ₱38,000 builds. The page says so.
- **Unknown:** the device firmware is not on this PC, so the exact download links on the device's page were not checked. The page only opens the device page; it does not depend on its routes.
- **Text:** English and Filipino, kept in the component (no builder credits). Have a Filipino speaker check the wording.
