# Leakage demonstration: the same fusion network on leaky splits (2026-11-14 00:39)

**This is not the model's accuracy.** It shows how far a leaky split inflates the score, and so why the study splits by patient. The model's accuracy on unseen patients is the first row.

Same recipe in every row: FDC-FS fusion (MFCC + spectrogram + chromagram), ICBHI + rebalanced SPRSound, band-limited, per-source normalisation, seed 11, `cv.train_fold`. Only the split changes. Scored per breathing cycle on ICBHI. Chance is 25%.

| Split | Balanced accuracy (95% CI) | Plain accuracy |
|---|---|---|
| **Patient-wise** (5-fold CV, 126 unseen patients): the honest figure | 39.0% (35.2–42.4) | 41.1% |
| Patients shared: test patients' other cycles were in training | 58.2% (55.0–61.3) | 56.6% |
| Windows shared: pieces of the same breath on both sides | 52.5% (50.7–54.5) | 50.2% |
| Training data: the model scored on cycles it was trained on | 78.5% (77.3–79.6) | 68.9% |

- Patients shared: 119 of 119 test patients also had cycles in training; 1370 test cycles.
- Windows shared: 3822 of 4008 test cycles had windows in training; 4008 test cycles.
- Leaky-split intervals resample cycles, not patients, so they are too narrow; they are shown for scale only.

Per-class recall (Crackles / Healthy / Wheezing / Wheezing with Crackles):

- patient_wise_cv_seed11: 54% / 37% / 37% / 27%
- patients_shared: 57% / 55% / 55% / 65%
- windows_shared: 62% / 43% / 47% / 57%
- training_data: 71% / 60% / 84% / 98%

How to say it: "When the test patients' recordings also appear in training, the same network scores X%. On patients it has never heard, it scores 40%. The first number measures memory; the second is the one we report." Never quote the leaky rows as accuracy.
