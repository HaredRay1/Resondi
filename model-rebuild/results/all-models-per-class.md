# Every Resondi model: accuracy and accuracy per category (27 Nov 2026)

Every number is copied from the result files named under each table. All are on **public datasets, patient-wise**
(no test patient was in training). **None is on Resondi device recordings**, and no model has been validated
clinically. "Per category" is the recall of each class: of the breathing cycles that really were Crackles, the share
the model called Crackles, and so on. Balanced accuracy is the mean of the four recalls; chance is 25%.
Plain accuracy is inflated by the Healthy majority (52.8% of ICBHI test cycles, 77.3% of SPRSound test cycles).

Left out on purpose: the original model (71.1% / 83%, a leaky split, withdrawn) and the leaky rows of the leakage
demonstration (IMRaD Table 5). The original model's field result (6 of 15 recordings, 40%) has no per-category record.

## 1. Lung models that have run in the app

| Model | Trained on | Tested on | Accuracy | Balanced accuracy | Crackles | Healthy | Wheezing | Wheezing with Crackles |
|---|---|---|---|---|---|---|---|---|
| Edge Impulse MFCC v1, int8 (in the app 10–13 Nov) | ICBHI | 31 ICBHI test patients, 1,051 cycles | 44.0% | 33.5% | 71% | 45% | 9% | 8% |
| **Fusion network, 3-seed ensemble (in the app since 13 Nov)** | ICBHI + SPRSound | 5-fold cross-validation, all 126 ICBHI patients, 6,898 cycles | 43.0% | **40.0%** (CI 35.9–43.5) | 56% | 40% | 38% | 26% |
| Same ensemble | ICBHI + SPRSound | 230 SPRSound test children | not recorded | 56.3% | not recorded | not recorded | not recorded | not recorded |

Sources: `model-rebuild/README.md` (v1), `cv-results.md`.

## 2. Lung models compared on the 31 ICBHI test patients (1,051 cycles)

Each scored once on the test patients. First round trained on ICBHI only; second round on ICBHI + SPRSound.

| Model | Trained on | Accuracy | Balanced accuracy | Crackles | Healthy | Wheezing | Wheezing with Crackles |
|---|---|---|---|---|---|---|---|
| MFCC network, chosen 11 Nov (seed 11) | ICBHI | 38.5% | 35.0% | 73% | 30% | 11% | 26% |
| MFCC alone | ICBHI | 38.8% | 36.1% | 75% | 29% | 25% | 16% |
| Spectrogram alone | ICBHI | 37.6% | 26.7% | 43% | 47% | 13% | 5% |
| Chromagram alone | ICBHI | 39.4% | 42.1% | 78% | 23% | 28% | 39% |
| Two-branch fusion (no chromagram) | ICBHI | 43.6% | 34.5% | 65% | 45% | 21% | 6% |
| Three-branch fusion | ICBHI | 48.2% | 36.7% | 56% | 57% | 24% | 9% |
| Late fusion of three models | ICBHI | 42.9% | 32.9% | 60% | 47% | 21% | 4% |
| **Three-branch fusion, seed 33 (pre-specified)** | ICBHI + SPRSound | 47.2% | **39.4%** (CI 28.4–44.6) | 57% | 52% | 24% | 25% |
| MFCC alone, seed 22 | ICBHI + SPRSound | 39.3% | 36.7% | 74% | 30% | 27% | 17% |
| Spectrogram alone, seed 33 | ICBHI + SPRSound | 38.3% | 34.6% | 46% | 40% | 17% | 36% |
| Chromagram alone, seed 33 | ICBHI + SPRSound | 37.5% | 38.9% | 81% | 21% | 8% | 45% |
| Two-branch fusion, seed 11 | ICBHI + SPRSound | 43.1% | 36.5% | 55% | 46% | 25% | 20% |
| Late fusion, seed 22 | ICBHI + SPRSound | 46.1% | 35.7% | 62% | 51% | 18% | 12% |

Sources: `stats/stats-results.json` (11 Nov model), `stats/fusion-comparison.json` (first round),
`final-test-icbhi-sprs.json` (second round).

## 3. Lung models on 230 SPRSound test children (3,643 events)

| Model | Trained on | Accuracy | Balanced accuracy | Crackles | Healthy | Wheezing | Wheezing with Crackles |
|---|---|---|---|---|---|---|---|
| MFCC alone | ICBHI only | 17.4% | 23.3% | 20% | 16% | 31% | 27% |
| Spectrogram alone | ICBHI only | 28.1% | 24.4% | 76% | 21% | 0% | 0% |
| Chromagram alone | ICBHI only | 23.9% | 27.6% | 12% | 23% | 73% | 2% |
| Two-branch fusion | ICBHI only | 9.4% | 32.2% | 36% | 3% | 17% | 73% |
| Three-branch fusion | ICBHI only | 24.7% | 31.7% | 0% | 29% | 20% | 78% |
| Late fusion | ICBHI only | 33.1% | 29.9% | 68% | 27% | 24% | 0% |
| **Three-branch fusion, seed 33 (pre-specified)** | ICBHI + SPRSound | 66.2% | **57.2%** (CI 46.7–63.4) | 53% | 70% | 55% | 51% |
| MFCC alone, seed 22 | ICBHI + SPRSound | 61.2% | 51.3% | 40% | 67% | 46% | 53% |
| Spectrogram alone, seed 33 | ICBHI + SPRSound | 61.4% | 51.0% | 47% | 66% | 42% | 49% |
| Chromagram alone, seed 33 | ICBHI + SPRSound | 22.1% | 45.9% | 51% | 14% | 36% | 82% |
| Two-branch fusion, seed 11 | ICBHI + SPRSound | 64.0% | 53.4% | 45% | 69% | 46% | 53% |
| Late fusion, seed 22 | ICBHI + SPRSound | 64.6% | 52.8% | 48% | 70% | 44% | 49% |

Models trained on adults alone fail on children; adding SPRSound to training fixes most of that.
Sources: `stats/fusion-comparison.json`, `final-test-icbhi-sprs.json`.

## 4. Five-fold cross-validation, all 126 ICBHI patients (6,898 cycles)

| Model | Trained on | Accuracy | Balanced accuracy (95% CI) | Crackles | Healthy | Wheezing | Wheezing with Crackles |
|---|---|---|---|---|---|---|---|
| MFCC network (the first app design) | ICBHI | 36.6% | 34.0% (30.4–38.2) | 50% | 33% | 31% | 22% |
| Fusion network, seed 11 | ICBHI + SPRSound | 41.1% | 39.0% (35.2–42.4) | 54% | 37% | 37% | 27% |
| Fusion network, seed 22 | ICBHI + SPRSound | 40.2% | 39.1% (35.2–42.9) | 50% | 37% | 39% | 30% |
| Fusion network, seed 33 | ICBHI + SPRSound | 43.0% | 39.5% (35.6–43.4) | 54% | 41% | 37% | 25% |
| **Fusion network, ensemble of the three (in the app)** | ICBHI + SPRSound | 43.0% | **40.0%** (35.9–43.5) | 56% | 40% | 38% | 26% |

Fusion against MFCC on the same 126 patients: +5.9 points (95% CI +1.0 to +10.3), one-sided p = 0.008.
Source: `cv-results.md`, `cv-paired.txt`.

## 5. Heart models, 189 CirCor test patients (children and adolescents, Brazil)

| Model | Category | Result (95% CI) |
|---|---|---|
| Heart-sound segmentation | S1 found within 100 ms | 96.8% |
| | S2 found within 100 ms | 97.3% |
| | Heart rate, mean absolute error | 3.0 BPM (2.5–3.6); 85% of recordings within 5 BPM |
| Murmur detection (175 patients with a known label) | Murmur present: found (sensitivity) | **66.7%** (50.0–81.8), 24 of 36; target was 80% |
| | Murmur absent: found (specificity) | 97.1% (93.9–99.3), 135 of 139 |
| | Accuracy | 90.9% (159 of 175) |
| | Balanced accuracy | 81.9% |
| | AUROC; Cohen's kappa | 0.96 (0.92–0.99); 0.70 (0.54–0.82) |
| Murmur detection through the app's audio path (16 kHz in) | Sensitivity; specificity | 69.4%; 97.1% |

Accuracy and balanced accuracy for murmurs are computed from the confusion counts in `heart-murmur.md`
((24 + 135) / 175; (66.7 + 97.1) / 2). Sources: `heart-segmentation.md`, `heart-murmur.md`, `heart-app-path-check.md`.

## Never quote

- 71.1% / 83%: the withdrawn model's leaked scores.
- The leaky rows of the leakage demonstration (58.2%, 52.5%, 78.5%).
- The murmur detector as "80%": 80% was the target, 66.7% the result.
