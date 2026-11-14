# Heart models through the app's audio path (CirCor test patients, 14 Nov 2026)

631 test recordings, each upsampled to 16 kHz (as a device recording would arrive) and then put through the app's path: FIR low-pass, every 4th sample, the training features, the ONNX models (`scripts/heart_app_path.py`).

| Measure | Training path (4 kHz wav) | App path (16 kHz -> 4 kHz) |
|---|---|---|
| Heart rate mean absolute error | 3.01 BPM | 3.03 BPM |
| Within 5 BPM | 85.3% | 85.7% |
| Murmur sensitivity | 66.7% (24/36) | 69.4% (25/36) |
| Murmur specificity | 97.1% | 97.1% |
| Murmur AUROC | 0.959 | 0.961 |

Heart rate within 1 BPM of the training path on 94.3% of recordings; murmur flag the same on 99.7%. The training-path column should equal results/heart-segmentation.md and heart-murmur.md (all recordings here, including those with fewer than 3 reference S1 onsets for the murmur rows).

This checks the software path only. It says nothing about how the models do on the Resondi microphone.
