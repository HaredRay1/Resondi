---
tags: [models, lung]
---
# Lung models

Four sound classes: Crackles, Healthy, Wheezing, Wheezing with Crackles. Balanced accuracy; chance is 25%.

| Model | Result | Status |
|---|---|---|
| Original app model (diagnosis labels) | ~~71.1% / 83%~~ leaked, **never quote** | withdrawn |
| Field test, original model, 15 device recordings | 40% (6 of 15), CI 19.8-64.3%, p = .148 | reference labels undocumented |
| Edge Impulse rebuild v1 | 33.5% on 31 test patients | in the app 10-13 Nov |
| MFCC network, 5-fold CV, 126 ICBHI patients | 34.0% (CI 30.4-38.2) | reference |
| **Fusion (MFCC + spectrogram + chromagram) + SPRSound, 5-fold CV** | **40.0% (CI 35.9-43.5)**; children 56% | **in the app since 13 Nov** |
| Same fusion design, pre-specified test (31 patients) | 39.4%; children 57.2% | agrees with CV |

- Fusion gain over MFCC: +5.9 points (95% CI +1.0 to +10.3), p = 0.008.
- With noise added, balanced accuracy fell to chance (Hypothesis 1 rejected).
- On Resondi device audio the scores are close to uniform: never claim it works on the device.

Per category and every run: [[all-models-per-class]] · [[cv-results]] · [[leakage-demo]] · [[LIMITATIONS]]
