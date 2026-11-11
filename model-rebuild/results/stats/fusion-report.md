# Fusion study: test-set comparison

Primary model (pre-specified on validation): **Late fusion (3 views)**. Every configuration below was scored once.

## ICBHI test: 31 patients, 1051 cycles/events

| Model | Balanced acc. (95% CI) | Macro-F1 | Kappa | ICBHI score | Crackles | Healthy | Wheezing | W+C | vs primary: b / c, p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| MFCC alone | 36.1 (28.3–44.0) | 0.317 | 0.161 | 39.4 | 75 | 29 | 25 | 16 | 183 / 140, 0.058 |
| Spectrogram alone | 26.7 (18.8–33.4) | 0.268 | 0.074 | 37.0 | 43 | 47 | 12 | 5 | 112 / 56, 0.000 |
| Chromagram alone | 42.1 (31.0–48.7) | 0.353 | 0.189 | 40.4 | 78 | 23 | 28 | 39 | 187 / 150, 0.099 |
| Fusion without chromagram | 34.5 (24.7–41.5) | 0.325 | 0.176 | 43.5 | 65 | 45 | 21 | 6 | 91 / 98, 0.663 |
| FDC-FS three-branch fusion | 36.7 (26.0–43.0) | 0.358 | 0.212 | 47.7 | 56 | 57 | 24 | 9 | 59 / 115, 0.000 |
| Late fusion (3 views) | 32.9 (23.9–40.9) | 0.313 | 0.156 | 42.7 | 60 | 47 | 21 | 4 | — |

## SPRSound test (external, children): 230 patients, 3643 cycles/events

| Model | Balanced acc. (95% CI) | Macro-F1 | Kappa | ICBHI score | Crackles | Healthy | Wheezing | W+C | vs primary: b / c, p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| MFCC alone | 23.3 (19.8–28.5) | 0.149 | -0.013 | 19.4 | 20 | 16 | 31 | 27 | 711 / 140, 0.000 |
| Spectrogram alone | 24.4 (21.3–26.7) | 0.145 | -0.019 | 36.3 | 76 | 21 | 0 | 0 | 243 / 62, 0.000 |
| Chromagram alone | 27.6 (24.5–30.5) | 0.165 | 0.008 | 25.5 | 12 | 23 | 73 | 2 | 611 / 279, 0.000 |
| Fusion without chromagram | 32.2 (21.9–37.5) | 0.109 | -0.027 | 17.7 | 36 | 3 | 17 | 73 | 1051 / 191, 0.000 |
| FDC-FS three-branch fusion | 31.7 (21.1–36.1) | 0.162 | 0.015 | 19.4 | 0 | 29 | 20 | 78 | 604 / 300, 0.000 |
| Late fusion (3 views) | 29.9 (25.7–33.8) | 0.238 | 0.004 | 39.9 | 68 | 27 | 24 | 0 | — |

## Reproducibility

- single_mfcc: seed 22, validation logged 0.4588, retrained 0.4658
- single_spec: seed 11, validation logged 0.4894, retrained 0.4664
- single_chroma: seed 33, validation logged 0.4259, retrained 0.4259
- fdc3: seed 11, validation logged 0.4880, retrained 0.4880
- fdc2_nochroma: seed 11, validation logged 0.4750, retrained 0.4750
- late3: seed 11, validation logged 0.5024, retrained 0.4872
