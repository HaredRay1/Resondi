# Resondi model results: lung fusion model and heart models (summary, 15 Nov 2026)

Every number below is copied from the result files named in the last column. All are on **public datasets,
patient-wise** (no test patient was heard in training). **None is on Resondi device recordings**, and none of these
models has been validated clinically. Chance for the four lung classes is 25% balanced accuracy.

## Lung: fusion network (MFCC + spectrogram + chromagram), trained on ICBHI + SPRSound

| Test | Patients | Balanced accuracy (95% CI) | Plain accuracy | Macro F1 | Source |
|---|---|---|---|---|---|
| **5-fold cross-validation, 3-seed ensemble (the model in the app)** | 126 adults (ICBHI, all) | **40.0% (35.9–43.5)** | 43.0% | 0.37 | `cv-results.md` |
| Same, on held-out children | 230 children (SPRSound test) | **56.3%** | — | — | `cv-results.md` |
| Single pre-specified test, seed 33 | 31 adults (ICBHI test) | 39.4% (28.4–44.6) | 47.2% | 0.38 | `final-test-icbhi-sprs.md` |
| Same, on held-out children | 230 children (SPRSound test) | 57.2% (46.7–63.4) | 66.2% | 0.45 | `final-test-icbhi-sprs.md` |
| *Comparison: MFCC network, ICBHI only, 5-fold CV* | *126 adults* | *34.0% (30.4–38.2)* | *36.6%* | *0.31* | `cv-results.md` |

**Fusion vs MFCC on the same 126 patients:** +5.9 points (95% CI +1.0 to +10.3), one-sided p = 0.008
(`cv-paired.txt`).

**Per-class recall, cross-validation ensemble (126 adults):** Crackles 56%, Healthy 40%, Wheezing 38%,
Wheezing with Crackles 26%.

## Heart: two models on CirCor DigiScope (children and adolescents, Brazil), 189 test patients

These are **not** fusion models: one CNN + BiGRU segmenter (heart sounds and heart rate) and one 1-D CNN murmur
detector (3 seeds).

| Model | Measure | Result (95% CI) | Source |
|---|---|---|---|
| Heart-sound segmentation | S1 found (within 100 ms) | 96.8% | `heart-segmentation.md` |
| | S2 found (within 100 ms) | 97.3% | `heart-segmentation.md` |
| | Heart rate, mean absolute error | **3.0 BPM (2.5–3.6)** | `heart-segmentation.md` |
| | Recordings within 5 BPM | 85% | `heart-segmentation.md` |
| Murmur detection | Sensitivity | **66.7% (50.0–81.8)**, short of the pre-specified 80% target | `heart-murmur.md` |
| | Specificity | 97.1% (93.9–99.3) | `heart-murmur.md` |
| | AUROC | 0.96 (0.92–0.99) | `heart-murmur.md` |
| | Cohen's kappa | 0.70 (0.54–0.82) | `heart-murmur.md` |

Through the app's audio path (16 kHz in, as from the device) the heart results are unchanged: heart rate error
3.03 BPM, murmur sensitivity 69.4%, specificity 97.1% (`heart-app-path-check.md`).

## Do not quote

- 71.1% / 83%: the withdrawn model's leaked scores.
- The leaky rows of IMRaD Table 4 (58.2%, 52.5%, 78.5%).
- The murmur detector as "80%": 80% was the target, 66.7% the result.
