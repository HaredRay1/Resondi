# App change: switch to the 4-class sound model

> **Status, 9 Nov:** applied directly in code (no builder credits), not through the prompt below. Model files are committed for `HaredRay1/Ausculta` at `408971af2537276aa2c8a273bbe2dfa245fa13f1`, awaiting push. The app's new code path, run in Node on the 1,051 held-out clips, reproduces the checker exactly: accuracy 44.0%, balanced 33.5%. Not done from the list below: the "Analysed with the earlier model" note on old results (needs i18n text, so a builder turn). Item A6 (int16 scaling) is done.

**When:** only after the new Edge Impulse model has passed `scripts/check_deployed_model.js` (see `model-rebuild/docs/EDGE-IMPULSE-RETRAINING.md`). Until then the app keeps the old model.

**What changes:** the model's outputs change from diagnoses (Asthma, Bronchiolitis, Healthy, Pneumonia) to sound patterns (Crackles, Healthy, Wheezing, Wheezing with Crackles). Every place that reads a label has to change with it. The input does not change: still 1 s of audio at 16 kHz.

## Prompt to paste into the Base44 builder

> Update the lung sound classifier to a new model with new labels.
>
> 1. In `src/lib/lungClassifier.js`, change `MODEL_BASE` to `https://cdn.jsdelivr.net/gh/HaredRay1/Ausculta@<COMMIT SHA>/model/resondi-lung-4class-v1/browser/` (a fixed commit, not `@main`).
> 2. The model now outputs exactly these labels: `Crackles`, `Healthy`, `Wheezing`, `Wheezing with Crackles`. Add `src/lib/lungLabels.js` with the contents below, and use `DISPLAY` from it everywhere a lung result is shown, including the headline result, the breakdown bars, the practitioner review page and exports. Remove every mapping from Asthma, Bronchiolitis or Pneumonia to a sound name.
> 3. The headline result and the breakdown bars must use the same rule: average each label's score over all 1-second windows of the recording, and show the label with the highest average.
> 4. Save `model_version: 'resondi-lung-4class-v1'` with every new analysis. Show older analyses unchanged, with the note "Analysed with the earlier model", and do not convert their labels.
> 5. Any rule, summary or AI prompt that checks for "Asthma", "Bronchiolitis" or "Pneumonia" must check the new sound labels instead. List each one you change.
> 6. Heart recordings must never be sent to this model.
>
> Do not change the recording flow, the 1-second window or the sample rate.

Contents of `src/lib/lungLabels.js`: copy `model-rebuild/app/labels.js`.

## After publishing, check

- A lung recording returns one of the four new labels, and the bars agree with the headline.
- The practitioner page shows the same label.
- An old analysis still shows its old label, marked as from the earlier model.
- A heart recording offers no AI analysis.

## Also worth testing once (review item A6)

The app feeds audio to the model as values between −1 and 1. Edge Impulse's own recordings, and the clips the new model is trained on, use int16 values (−32768 to 32767). Tested on 9 Nov with the current deployed model on 270 one-second ICBHI windows: the top label was the same at both scales every time, but individual scores moved by up to 0.25. So the label shown is unaffected, while the confidence shown is not reliable. **Multiply the samples by 32768 before calling `classify`,** so the app matches the training data. Then check one recording against Edge Impulse Studio's **Live classification**.
