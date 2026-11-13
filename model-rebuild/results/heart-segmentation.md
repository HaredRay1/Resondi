# Heart sound segmentation and heart rate on CirCor test patients (14 Nov 2026)

Patient-wise split, 189 test patients, 631 recordings with at least 3 reference S1 onsets. Model: CNN + BiGRU frame classifier (one seed) with cyclic Viterbi decoding (`scripts/heart_seg.py`). Viterbi advance probability 0.3, chosen on validation patients.

| Measure | Trained model | No-training baseline (autocorrelation) |
|---|---|---|
| Heart rate mean absolute error | **3.0 BPM** (95% CI 2.5–3.6) | 35.4 BPM (29.9–40.8) |
| Median absolute error | 1.8 BPM | 4.3 BPM |
| Recordings within 5 BPM | 85% | 54% |
| Recordings within 10 BPM | 96% | 63% |
| No estimate | 0 | 0 |

Bland–Altman (model − reference): bias +0.1 BPM, 95% limits -13.7 to +14.0. Reference heart rates: 49–171 BPM, median 103 (children and adolescents).

| Heart sound | Found within 100 ms (sensitivity) | Detections that are real (PPV) | Onset timing error |
|---|---|---|---|
| S1 | 96.8% | 95.7% | 15 ms |
| S2 | 97.3% | 96.5% | 12 ms |

Frame accuracy on annotated frames (four states): 87.1%.

These are results on CirCor recordings (Brazilian children, electronic stethoscope). They have not been checked on Resondi device recordings, whose microphone may lose the lowest heart-sound frequencies.
