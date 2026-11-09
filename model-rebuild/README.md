# Resondi Lung Sound Model: Rebuild Package

This package rebuilds the Resondi lung sound classifier with the corrected labels:

| Old labels (diagnoses) | New labels (sound patterns) |
|---|---|
| Asthma, Bronchiolitis, Healthy, Pneumonia | **Crackles, Healthy, Wheezing, Wheezing with Crackles** |

The labels were not renamed. The old model was trained on each patient's diagnosis stamped on every second of their audio, which is why it learned to recognise patients instead of sounds. This package relabels the data from the ICBHI annotations of **each breathing cycle** (crackles yes/no, wheezes yes/no), splits by **patient** before any audio is cut, and trains the model again from scratch.

## Results (real, 9 November 2026)

Trained and evaluated on this PC. Test patients: 31 ICBHI patients, 1,051 breathing cycles, none of them used in training or model selection. The split balances both the four labels and the four ICBHI stethoscopes across train, validation and test (see "What went wrong first" below).

| Model | Input window | Test balanced accuracy (1 s windows) | Test balanced accuracy (whole cycles) | Test macro F1 (cycles) |
|---|---|---|---|---|
| Same network as the app (8 and 16 filters) | 1 s | 30.0% | 32.4% | 0.27 |
| **Wider network (32 and 64 filters)** | **1 s** | **34.9%** | **38.1%** | **0.35** |
| Wider network | 3 s | 32.5% | 34.0% | 0.32 |
| Chance, four classes | | 25% | 25% | |

Best model, per class, on whole cycles: Crackles recall 0.74, Healthy 0.45, Wheezing 0.25, Wheezing with Crackles 0.08. Full reports with confusion matrices are in `results/`.

**What this means.** The wider 1-second network is clearly above chance on patients it has never heard, and it catches about three in four crackling cycles. It is still weak: it misses most wheezes and almost every combined cycle, and it calls about half of normal cycles abnormal. It is the first honest result for this model (the old 71–84% came from data leakage) and the baseline everything else is measured against. It is a screening aid for a practitioner to check, never a result to act on alone. Longer windows did not help: 3 s scored below 1 s, so the app's 1-second input can stay.

**The Edge Impulse build for the app (9 Nov).** The wider network was rebuilt in Edge Impulse project `Resondi-Lung-4class` (deploy version 1, int8) and saved in `deploy/resondi-lung-4class-v1/browser/`. `check_deployed_model.js` passed: labels `Crackles | Healthy | Wheezing | Wheezing with Crackles`, 16,000-sample input. Classifying the 1,051 held-out test clips the way the app does (1 s windows, scores averaged): accuracy 44.0%, recall Crackles 0.71, Healthy 0.45, Wheezing 0.09, Wheezing with Crackles 0.08, so balanced accuracy 33.5%. That is a little below the local PyTorch build (38.1%), as expected from Edge Impulse's slightly different signal processing. Edge Impulse Studio's own test page showed 39.2% accuracy for int8 on 1-second windows. It is not published to GitHub or connected to the app yet.

**What went wrong first, and why it matters.** The first split balanced the labels but not the stethoscopes. 79% of its training cycles came from one microphone (the AKG C417L), and the model scored at chance on test patients recorded with other stethoscopes (14% on the Littmanns). Those results are kept in `results/run1-split-by-class-only/`. Balancing devices took the same networks from 22–26% to 30–35%. A change of recording device alone is enough to break this model, which is the strongest reason to train on recordings from the Resondi device itself (`docs/LOCAL-DATASET-INTEGRATION.md`).

## What is in the package

```
model-rebuild/
├── README.md                     this file
├── requirements.txt              Python packages
├── config/config.json            labels, label order, audio, MFCC, network, training, split: one source of truth
├── config/config-wider.json      the wider network (best result; recommended)
├── config/config-2s*.json, config-3s*.json   longer-window experiments
├── resondi_model/                the code the scripts share
│   ├── data.py                   reads ICBHI and local data, labels each cycle, splits by patient
│   ├── dsp.py                    audio loading, resampling, 1 s windows, MFCC
│   ├── model.py                  the 1-D CNN (same design as the app's model)
│   └── metrics.py                accuracy, balanced accuracy, precision, recall, specificity, F1, confusion matrix
├── scripts/
│   ├── prepare_data.py           step 1: manifest and features
│   ├── train.py                  step 2: train, pick the best epoch on validation patients
│   ├── evaluate.py               step 3: test on held-out patients
│   ├── export_onnx.py            step 4b: ONNX export, checked against PyTorch
│   ├── export_edge_impulse.py    step 4a: clips and info.labels for Edge Impulse (the app route)
│   ├── check_deployed_model.js   checks an Edge Impulse export before it goes into the app
│   └── add_local_dataset.py      checks and imports the local dataset
├── app/labels.js                 labels, display names and model version for the app
├── docs/
│   ├── LOCAL-DATASET-INTEGRATION.md   adding your own recordings, step by step
│   ├── EDGE-IMPULSE-RETRAINING.md     rebuilding the model the app runs
│   └── LIMITATIONS.md                 requirements and limitations
├── results/                      evaluation reports (generated)
├── work/                         manifest, features, trained models, training logs (generated)
├── export/                       ONNX model and Edge Impulse clips (generated)
└── deploy/resondi-lung-4class-v1/ the Edge Impulse WebAssembly build for the app (checked)
```

The app change is in `../app-changes/model-4-class-labels.md`.

## Setup (Windows, PowerShell)

```powershell
cd C:\Users\Hared\Downloads\Resondi\model-rebuild
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
```

You also need the ICBHI archive, `C:\Users\Hared\Downloads\archive.zip`.

## Rebuild, train, test, export

```powershell
python scripts\prepare_data.py --icbhi "C:\Users\Hared\Downloads\archive.zip"
python scripts\train.py
python scripts\evaluate.py validation
python scripts\evaluate.py
python scripts\export_onnx.py
python scripts\export_edge_impulse.py --icbhi "C:\Users\Hared\Downloads\archive.zip"
```

1. **prepare_data.py** labels every breathing cycle from its annotation, assigns whole patients to train (70%), validation (15%) or test (15%), cuts 1-second windows and computes MFCC features. It balances the four labels and the recording devices, and stops with an error if any patient lands in two groups. Run on 9 Nov: 65, 30 and 31 patients; 22,919, 3,442 and 3,555 windows. `--config` and `--work` run an experiment in its own folder.
2. **train.py** trains for up to 100 epochs with Adam (learning rate 0.005, batch size 32), weights the classes so the rare ones count, and keeps the epoch with the best validation macro F1. It never reads the test patients. `--config config\config-wider.json --out model-wider.pt` trains the experiment.
3. **evaluate.py** reports window-level and cycle-level results. Run it on the test partition once you have finished choosing, not while choosing. `--model model-wider.pt` evaluates the experiment.
4. **export_onnx.py** writes `export/onnx/resondi-lung-4class.onnx` (`--model model-wider.pt` for the wider one) and checks it against PyTorch (they agreed to 1e-7 on 9 Nov). It is for checking: the app cannot load it as it stands.
5. **export_edge_impulse.py** writes 6,898 clips with `info.labels`, which keeps the labels and the patient split when uploaded. This is how the app's model gets rebuilt: `docs/EDGE-IMPULSE-RETRAINING.md`.

The same seed gives the same split and the same model every time.

## Labels and class order

The four labels are listed once, in `config/config.json`, in alphabetical order: `Crackles`, `Healthy`, `Wheezing`, `Wheezing with Crackles`. That is the order Edge Impulse always outputs classes in, so every step uses it:

| Where | How the order is kept |
|---|---|
| Labelling | `label_from_annotation` in the config maps each crackle/wheeze combination to one label |
| Training | Class indices come from the config list |
| Saved model | The label list is saved inside `model.pt` |
| Evaluation | Refuses to run if the saved list differs from the config |
| ONNX export | `labels.json` is written beside the model |
| Edge Impulse | Labels travel in `info.labels`; Edge Impulse sorts them alphabetically, the same order |
| Deployed model | `check_deployed_model.js` fails unless its labels equal the config list |
| App | `app/labels.js`; the app should read each result's own label, not its position |

`load_config()` refuses to start if the list is not alphabetical.

## Compatibility with the app

Checked on 9 Nov by loading the app's deployed model (Edge Impulse "SmartStethoscope", deploy version 5) in Node:

- It takes 16,000 samples, which is 1 second at 16 kHz. This package keeps exactly that window (longer windows were tested and did no better), so the app's recording and windowing code does not change.
- It outputs four labels, alphabetically. The new model also outputs four labels, alphabetically. Only the label names change.
- Feeding it −1..1 audio instead of int16-scale audio never changed the top label on 270 test windows, but moved scores by up to 0.25. The app change asks for int16 scaling to match the training data.

## Next experiments, in order

Already tried: longer windows (2 s and 3 s did not beat 1 s).

1. **Rebuild the wider network in Edge Impulse** and check it with `check_deployed_model.js` (docs/EDGE-IMPULSE-RETRAINING.md).
2. **Add the local Resondi dataset** (docs/LOCAL-DATASET-INTEGRATION.md). The device result above says this matters more than anything else.
3. **Add HF_Lung_V1** (Taiwan). It is event-labelled, which fits these sound labels, and adds patients and devices.
4. **Try mel-spectrogram input with a 2-D CNN,** the usual stronger approach on ICBHI.

Test each one on the same 31 test patients, and keep `results/` from every run.
