# Live app test of resondi-lung-4class-v1 on stored recordings (10 Nov 2026)

## What was run

The **published** app code (`lungClassifier` chunk on resondi.base44.app, which loads the model from Ausculta commit `408971af`) ran inside the live app in Chrome, signed in as the app admin. It used the app's own `resolveAudioSrc` and `analyzeAudio`. It ran on every stored lung recording that has audio (45 recordings). It was read-only: no analysis was saved, and no existing result or practitioner review was touched.

## Pipeline: works end to end

- 45 of 45 recordings ran without error: the model downloaded from jsDelivr, the audio was signed and decoded (WAV 4/8/16/44.1 kHz, phone `.webm`, `.mp3`), and the 1 s windows were classified and averaged.
- Every result carried `modelVersion: resondi-lung-4class-v1`.
- Median time per recording was 1.8 s, after the model's first load.
- A separate re-implementation of the same windowing gave the same labels on all 33 device files, so the harness matches the live function.

## Result on the 33 Resondi device recordings (AUSCULTA00xx.WAV, 16 kHz, 16-bit, ~15 s)

| | Count |
|---|---|
| Healthy | 20 |
| Crackles | 7 |
| Wheezing with Crackles | 6 |
| Wheezing | 0 |

**The model is barely discriminating on device audio.** On every device file the top score is between 27% and 34% (median 30%). Four uniform classes would give 25% each. On the ICBHI-style and other non-device files the top scores reach 41–48%.

On the 29 device files with an old-model result, the old and new labels agree on 14. There are no reference labels, so this says nothing about which model is right.

## Why: a microphone/domain shift, not loudness

- The device audio is much quieter than the training audio: RMS −29.5 to −46.9 dBFS on the sampled device files, against −7.9 to −21.6 dBFS on the ICBHI files.
- Normalising each device file to −20 dBFS RMS before classifying changed **0 of 33** labels, and the top scores stayed at 27–34%. The feature step is effectively level-invariant.
- The remaining explanation is that the device's INMP441 MEMS microphone sounds different from the four ICBHI stethoscopes. Run 1 showed the same thing: a model trained mostly on one stethoscope scored at chance on the others.

## What this means

- Say "deployed and working end to end." Do not say it performs on the Resondi device: on device recordings its output is close to uniform.
- This is direct evidence for the funded step: recordings from the Resondi device, labelled by clinicians, are needed before the classifier can be trusted on the device (`model-rebuild/docs/LOCAL-DATASET-INTEGRATION`).
- The field test's 15 reference labels, if they can be matched to these AUSCULTA files, would give a first unleaked accuracy for the new model on device audio.

## Not checked

The on-screen result page, the practitioner page and the earlier-model note were not checked by eye. The admin account is redirected away from patient pages, and running a new analysis on a stored recording would delete its existing result and practitioner reviews. Check these with a patient test account and a new recording.
