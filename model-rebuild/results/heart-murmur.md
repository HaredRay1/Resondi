# Heart murmur detection on CirCor test patients (14 Nov 2026)

Patient-wise split. Test: 36 patients with a murmur, 139 without (plus 14 'unknown', reported separately). Model: 3-seed 1-D CNN on log-power spectra (`scripts/heart_murmur.py`); a patient is positive when any site is.

Threshold set on validation patients for a pre-specified sensitivity of 80% (validation: sensitivity 80.6%, specificity 97.1%).

| Measure (test patients) | Value (95% CI) |
|---|---|
| Sensitivity | **66.7% (50.0–81.8)** |
| Specificity | 97.1% (93.9–99.3) |
| Positive predictive value | 85.7% (71.0–96.7) |
| F1 | 0.75 (0.61–0.86) |
| Cohen's kappa | 0.70 (0.54–0.82) |
| AUROC | 0.96 (0.92–0.99) |

| | Model: murmur | Model: no murmur |
|---|---|---|
| Reference: murmur | 24 | 12 |
| Reference: no murmur | 4 | 135 |

'Unknown' test patients flagged as murmur: 2 of 14.

CirCor recordings only (Brazilian children, electronic stethoscope). Not checked on Resondi device recordings. A screening flag for practitioner review, never a diagnosis. Murmur timing (systolic / diastolic) not yet attempted.
