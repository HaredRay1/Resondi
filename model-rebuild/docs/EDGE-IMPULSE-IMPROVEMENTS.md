# Raising the model's test accuracy in Edge Impulse

Written 11 Nov 2026. Start from the project `Resondi-Lung-4class` (v1: MFCC + 1-D CNN, int8; 44.0% accuracy, 33.5% balanced on the 31 test patients). Setup and upload are in `EDGE-IMPULSE-RETRAINING.md`; this file lists what to change, one thing at a time.

**Rules for every change**
- Keep the same 31 test patients, and never move one into training.
- Choose settings by the **validation** score, then look at **Model testing** once per version you keep. Write down every test score, not only the best.
- Keep **Split train/validation set on metadata key: `patient`** switched on. Without it, Edge Impulse picks validation windows at random, which is the old leak.
- In Model testing, set the **classification threshold to 0**. At 0.6 most clips come out "uncertain" (the 0.20% result on 9 Nov).
- Report **balanced accuracy** (the average of the four per-class recalls) next to plain accuracy. Healthy and Crackles dominate the test set, so plain accuracy flatters the model.

**None of the changes in parts A and B need an app change.** The app still sends 1 s of raw 16 kHz audio, and the exported model carries its own feature step. Part C does need app changes.

The Python experiment (`scripts/experiment.py`) tests most of these on the validation patients first. Its results go to `results/experiments-validation.csv`, and they show which setting to try first in Edge Impulse.

## A. Feature block (Create impulse)

| # | Change | Setting | Python recipe |
|---|---|---|---|
| A1 | **Replace MFCC with MFE** (mel filterbank energy, the mel spectrogram). MFCC compresses away detail that wheezes and crackles carry. | Create impulse → remove *MFCC*, add *Audio (MFE)* | `mfe` |
| A2 | **Limit MFE to the lung-sound band.** Lung sounds sit below about 2 kHz, and heartbeats and rumble sit below 50 Hz. | MFE: frame length 0.02, frame stride 0.01, filter number 40, FFT length 256, **low frequency 50, high frequency 2000**, noise floor −52 dB | `mfe2k` |
| A3 | Try the *Spectrogram* block instead, if MFE plateaus. | frame length 0.02, stride 0.01, FFT 256, noise floor −52 | — |
| A4 | **Window settings.** Keep the window at 1000 ms, because that is what the app sends. | Time series data: window size 1000 ms, **window increase 500 ms** (more training windows), zero-pad on | already used |

Click **Generate features** after each change. The feature explorer shows whether the four classes separate at all.

## B. Neural network block (Classifier)

| # | Change | Setting | Python recipe |
|---|---|---|---|
| B1 | **Turn on data augmentation.** It helps against noise and different microphones. | Classifier → *Data augmentation* ✔: add noise (low), mask time bands (low), mask frequency bands (low), warp time axis ✔ | `mfe2k_aug` |
| B2 | **Balance the classes.** Wheezing and Wheezing with Crackles are rare, and the model ignores them (recall 0.09 and 0.08 in v1). | Advanced → **Auto-balance dataset** ✔ | — (Python uses class weights) |
| B3 | **Train longer, with a smaller learning rate.** | 100–200 epochs, learning rate 0.0005, batch 32 | — |
| B4 | **Use a 2-D CNN** instead of the 1-D one: MFE gives an image-like time × frequency grid. | Classifier → architecture presets → *2D Convolutional*, or Keras expert mode (Conv2D 16/32/64 + BatchNorm + global average pooling) | `mfe2k_2d_aug` (slow on this PC) |
| B5 | **Compare int8 and float32** in Model testing. If int8 loses more than 1–2 points, deploy float32; the browser runs it fine. | Deployment → optimisations → *Unoptimized (float32)* | — |
| B6 | **EON Tuner** searches feature and network combinations for you. It chooses on validation, so it is safe, but limits may apply on the free plan. | EON Tuner → target: browser/WebAssembly, window 1000 ms | — |

## C. Changes that need app work

| # | Change | Why | App change |
|---|---|---|---|
| C1 | **Two yes/no detectors** (crackles present? wheeze present?) combined into the four labels | A rare class like Wheezing with Crackles is just "both detectors say yes", so it borrows data from the other classes | Two models, plus a combining rule (`twodet` recipes test it) |
| C2 | **Longer input** (2–3 s) | — | Tested 9 Nov: 3 s was no better (34.0%). Not worth it. |

## D. Add a local dataset (the biggest single gain on the device)

The 10 Nov live test showed that on Resondi device recordings the model's top score is only 27–34%, close to the 25% of a random guess. The device microphone sounds different from ICBHI's stethoscopes, and no setting above can fix that. Only recordings from the device itself can.

1. **Collect.** Use the Resondi device, at the seven lung sites, with consent and ethics approval. Record the patient code, device, site, date and room noise for each recording, and no names.
2. **Label per breathing cycle.** A clinician, ideally two, marks crackles yes/no and wheeze yes/no for each cycle, without seeing the AI's answer. Two raters give you Cohen's kappa.
3. **Prepare.** Run `scripts/add_local_dataset.py`, as described in `LOCAL-DATASET-INTEGRATION`. It splits by patient and keeps the same four labels.
4. **Upload** with `patient`, `device=resondi` and `source=local` metadata. Put whole local patients into Edge Impulse's **Test** category, as their own test group.
5. **Report two numbers separately:** ICBHI test patients, and Resondi device test patients. The device number is the one that matters for the pitch.

Even 20–30 local patients in training help, because the model then learns what the INMP441 microphone sounds like. The concept note budgets ₱46,000 for this.

## Click-by-click: v2 (MFE + augmentation)

Menu names can shift slightly between Edge Impulse releases. If a setting is not where these steps say, check the page's *Advanced* or ⋮ menu.

0. **Save v1 first.** Dashboard → *Versioning* → *Store a new version*, named "v1 MFCC". You can restore it at any time.
1. **Create impulse.**
   - Time series data: window size **1000 ms**, window increase **500 ms**, frequency **16000 Hz**, zero-pad **on**.
   - Delete the **MFCC** block, then *Add a processing block* → **Audio (MFE)**.
   - Keep the **Classification** learning block, ticked to use MFE.
   - **Save Impulse.**
2. **MFE page.**
   - Set frame length **0.02**, frame stride **0.02**, filter number **40**, FFT length **256**, low frequency **50**, high frequency **2000**, noise floor **−52**.
   - Click **Save parameters**, then **Generate features**.
3. **Classifier page.**
   - Training cycles **100**, learning rate **0.0005**, batch size **32**.
   - Advanced: validation size **15%**, **split on metadata key `patient`**, **Auto-balance dataset ✔**.
   - **Data augmentation ✔:** add noise **Low**, mask time bands **Low**, mask frequency bands **Low**, warp time axis **✔**.
   - Network: two 1-D conv layers with **32** and **64** filters, kernel **3**, dropout **0.25**.
   - **Start training**, then write down the validation accuracy and confusion matrix.
4. **Model testing.**
   - ⋮ → *Set confidence thresholds* → **0**.
   - Click **Classify all**.
   - Write down accuracy and each class's row of the confusion matrix. Balanced accuracy is the average of the four diagonal percentages.
5. **Store a new version** ("v2 MFE aug").
6. **Optional v3, a 2-D CNN.**
   - Classifier: replace the 1-D conv layers with 2-D conv layers of **16, 32 and 64** filters (kernel 3), each followed by pooling, then Flatten and dropout **0.25**.
   - Retrain, then test as in step 4.
7. **Deploy the best by validation.**
   - *Deployment* → **WebAssembly (browser, SIMD)**.
   - Compare **Quantized (int8)** and **Unoptimized (float32)**. Pick float32 if int8 loses more than 1–2 points.
   - Click **Build**, then give the .zip to Claude to run `check_deployed_model.js` before it goes into the app.

| Version | Validation acc. | Test acc. | Test balanced | Crackles | Healthy | Wheezing | W+C |
|---|---|---|---|---|---|---|---|
| v1 MFCC (9 Nov) | — | 39.2% (Studio, windows) | — | | | | |
| v2 MFE + aug | | | | | | | |
| v3 2-D CNN | | | | | | | |

## Do not
- Move test patients into training, or re-split until a lucky split appears.
- Choose a version by its test score, or tune the threshold on the test set.
- Drop the hard classes, or report plain accuracy without balanced accuracy.
- Quote any of these numbers as the accuracy on the Resondi device until part D is done.
