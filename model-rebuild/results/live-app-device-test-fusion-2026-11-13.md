# Live app test of resondi-lung-fusion-v2 on stored recordings (13 Nov 2026)

## What was run

The **published** app code (chunk `lungClassifier-C0psc4D0.js` on resondi.base44.app, published 13 Nov 2026 03:43 PHT, checkpoint `6af616ece0e4bcab64cebaa1`, which loads the model from Ausculta commit `c9cd3fa2`) ran in Chrome inside the live app, signed in as the app admin. It used the app's own signed-URL route and `analyzeAudio`, on every stored lung recording with audio (45). Read-only: no analysis was saved, and no result or practitioner review was touched. Same method as `live-app-device-test-2026-11-10.md`.

## Pipeline

- 45 of 45 recordings ran without error. Median time per recording was 2.0 s, including fetching the audio.
- Before publishing, the browser path was checked against the training code in Python: 600 of 600 validation windows gave the same top label (`results/fusion-browser-parity.txt`), and a synthetic 15 s recording gave the same four scores to 4 decimals in Chrome and Python.

## Result on the Resondi device recordings (AUSCULTA00xx.WAV, 16 kHz, ~15 s)

33 entries. 26 are unique recordings: some files were uploaded more than once and score identically.

| | Unique recordings (26) | All entries (33) |
|---|---|---|
| Healthy | 16 | 19 |
| Wheezing with Crackles | 6 | 8 |
| Wheezing | 3 | 5 |
| Crackles | 1 | 1 |

**Top score per recording: 31% to 66%, median 42%** (four uniform classes would give 25% each).

The previous model (Edge Impulse 4-class v1) scored 27% to 34%, median 30%, on the same files (10 Nov). So the fusion model is clearly **more decisive on device audio**, plausibly because every window is now band-limited to 100–3900 Hz and levelled to -20 dBFS before features, which removes part of the microphone and loudness difference.

**More decisive is not the same as more correct.** These recordings have no reference labels, so this test cannot say whether the labels are right. Do not quote it as accuracy on the device.

## What this means

- Say: "the new model runs in the app end to end, and on our device's recordings it no longer outputs near-uniform scores."
- Do not say: that it is accurate on the Resondi device. That needs device recordings labelled by clinicians (`docs/LOCAL-DATASET-INTEGRATION`), and the field test's 15 reference labels, if they can be matched to these AUSCULTA files.

## Per-recording scores (unique recordings; Crackles / Healthy / Wheezing / Wheezing with Crackles)

| File | Top label | Scores |
|---|---|---|
| AUSCULTA0001 (a) | Crackles | 0.422 / 0.307 / 0.095 / 0.176 |
| AUSCULTA0001 (b) | Wheezing with Crackles | 0.104 / 0.153 / 0.344 / 0.399 |
| AUSCULTA0002 (a) | Healthy | 0.248 / 0.495 / 0.072 / 0.185 |
| AUSCULTA0002 (b) | Wheezing | 0.117 / 0.118 / 0.416 / 0.349 |
| AUSCULTA0002 (c) | Healthy | 0.157 / 0.326 / 0.199 / 0.318 |
| AUSCULTA0006 | Healthy | 0.317 / 0.398 / 0.073 / 0.213 |
| AUSCULTA0008 | Healthy | 0.277 / 0.482 / 0.101 / 0.140 |
| AUSCULTA0009 | Healthy | 0.188 / 0.348 / 0.240 / 0.224 |
| AUSCULTA0010 | Wheezing | 0.115 / 0.295 / 0.401 / 0.189 |
| AUSCULTA0011 | Healthy | 0.195 / 0.377 / 0.198 / 0.231 |
| AUSCULTA0012 | Wheezing | 0.143 / 0.301 / 0.309 / 0.247 |
| AUSCULTA0013 | Healthy | 0.217 / 0.315 / 0.171 / 0.297 |
| AUSCULTA0014 | Healthy | 0.181 / 0.437 / 0.272 / 0.110 |
| AUSCULTA0015 | Healthy | 0.183 / 0.380 / 0.164 / 0.273 |
| AUSCULTA0016 | Wheezing with Crackles | 0.155 / 0.358 / 0.109 / 0.378 |
| AUSCULTA0017 | Healthy | 0.246 / 0.363 / 0.076 / 0.315 |
| AUSCULTA0018 | Wheezing with Crackles | 0.069 / 0.307 / 0.114 / 0.511 |
| AUSCULTA0019 | Wheezing with Crackles | 0.187 / 0.330 / 0.063 / 0.420 |
| AUSCULTA0021 | Wheezing with Crackles | 0.205 / 0.151 / 0.047 / 0.597 |
| AUSCULTA0022 | Wheezing with Crackles | 0.082 / 0.387 / 0.112 / 0.419 |
| AUSCULTA0023 | Healthy | 0.250 / 0.357 / 0.068 / 0.325 |
| AUSCULTA0025 | Healthy | 0.284 / 0.398 / 0.026 / 0.292 |
| AUSCULTA0028 | Healthy | 0.302 / 0.444 / 0.060 / 0.194 |
| AUSCULTA0029 | Healthy | 0.249 / 0.454 / 0.059 / 0.238 |
| AUSCULTA0030 | Healthy | 0.228 / 0.418 / 0.024 / 0.330 |
| AUSCULTA0031 | Healthy | 0.155 / 0.657 / 0.123 / 0.066 |

The same file name with different scores (AUSCULTA0001, 0002) means different recordings: the device's counter restarts, so names repeat across sessions.

## Other recordings (12 entries: phone .webm/.mp3, ICBHI and other test files)

All ran. Not analysed further; they are not device audio.
