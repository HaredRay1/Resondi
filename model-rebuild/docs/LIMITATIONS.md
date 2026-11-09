# Requirements and Limitations

## What you need

| Need | Why |
|---|---|
| Python 3.11+ with the packages in `requirements.txt` | Data preparation, training, evaluation, export |
| The ICBHI 2017 archive (`archive.zip`, about 4 GB, Kaggle "Respiratory Sound Database") | The training data. Not included in this package. |
| Node.js 18+ | Only for `scripts/check_deployed_model.js` |
| The Edge Impulse account that owns the app's project, and the Edge Impulse CLI | Only to build the model the app actually runs |
| Access to the Base44 app and the GitHub repository `HaredRay1/Ausculta` | Only to put the new model in the app |
| About 2 GB of free disk space | Feature files and the Edge Impulse clips (`export/edge-impulse` is about 600 MB) |

## Limitations

1. **The retrained model is weak.** The best version scores 38% balanced accuracy on whole cycles of 31 unseen patients, against 25% chance (README, "Results"). It catches most crackles but few wheezes and almost no combined cycles, and calls about half of normal cycles abnormal. It is an honest baseline, not a validated screening tool, and every result must still go to a practitioner.

2. **The model in the app has not been rebuilt.** The app runs an Edge Impulse WebAssembly export, which only Edge Impulse can produce, and that needs your account. `docs/EDGE-IMPULSE-RETRAINING.md` gives every step. Until it is done and checked with `check_deployed_model.js`, the app still outputs the old diagnosis labels.

3. **The local PyTorch build does not reproduce Edge Impulse exactly.** It uses the same data, patient split, MFCC settings, architecture and optimiser, and the MFCC follows Edge Impulse's method. Small differences remain, so Edge Impulse's results will be similar, not identical. Compare both on the same test patients.

4. **The ONNX export is for checking, not for the app.** It takes MFCC features, not raw audio. Using it in the app would mean computing MFCC in JavaScript and switching to ONNX Runtime Web, which nothing here does.

5. **One-second windows carry noisy labels.** A breathing cycle averages 2.7 s and a crackle lasts a few milliseconds, so many 1-second windows cut from a "Crackles" cycle contain no crackle at all. Longer windows (2 s and 3 s) were tested on 9 Nov and did not do better, so the app's 1-second input stays.

6. **The recording device dominates.** With 79% of training audio from one stethoscope, the model failed on the others (14% on the Littmanns). Balancing devices across the split fixed most of that, but it shows the model will not transfer to the Resondi device without Resondi recordings in training.

7. **The test group is small** (31 patients, 1,051 cycles), and results move between patient groups (the best model scored 48% on validation patients, 38% on test patients). Report the confusion matrix, not one number.

8. **ICBHI is not Filipino data, and Resondi recordings are not ICBHI recordings.** ICBHI was recorded in Portugal and Greece on four other stethoscopes, mostly from adults with COPD. Results on ICBHI patients say nothing directly about Filipino patients recorded on the Resondi device. Only the local dataset answers that.

9. **This is a lung model only.** It must never be run on heart recordings.

10. **The model detects sounds, not diseases.** It does not diagnose asthma, pneumonia or anything else, and every result still goes to a practitioner.

11. **Results from the old model cannot be converted.** The old model learned diagnoses, not sounds, so "Asthma" from it does not mean "Wheezing". Old results stay as they were, marked as from the earlier model.
