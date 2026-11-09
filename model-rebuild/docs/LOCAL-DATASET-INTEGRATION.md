# Adding the Local Respiratory Sound Dataset to the Model

This is the step-by-step procedure for adding recordings collected by the Resondi team to the training data, retraining the model, and putting the new model in the app.

It assumes the setup in the README is done and that the ICBHI-only model has already been built once (`prepare_data.py`, `train.py`, `evaluate.py`). That first build is your baseline: every result with local data is compared against it.

---

## 1. Before any recording is made

These are conditions for using the data at all, not paperwork to do afterwards.

- **Ethics approval.** Get approval from an ethics committee for collecting and using patient recordings. Physician supervision is not the same thing.
- **Written consent from every patient** (and from a parent or guardian, plus assent, for anyone under 18). The consent must cover using the recording to train software. Record each patient's consent in `patients.csv` (`consent_on_file = yes`). The scripts drop every patient without it.
- **No names anywhere in the dataset.** Give each patient a code such as `P001`. Keep the list that links codes to people on paper or in a separate locked file, never in the dataset folder. Lung recordings are sensitive personal information under the Data Privacy Act of 2012.

## 2. Recording requirements

| Item | Requirement |
|---|---|
| Device | The Resondi device (record which version in `patients.csv`). Recordings from other stethoscopes go in a separate dataset, not this one. |
| Format | WAV, 16-bit PCM, mono. The device's own format (16 kHz, 16-bit, mono) is ideal. |
| Sample rate | At least 4,000 Hz. The scripts resample everything to 16,000 Hz. |
| Sites | The seven standard sites: `Tc` trachea, `Al` `Ar` left and right upper anterior, `Ll` `Lr` left and right lateral, `Pl` `Pr` left and right posterior. |
| Length | One 15-second capture per file, as the firmware records. Two files per lung site if the protocol's 20 s is needed. |
| Breathing | Mouth open, deeper than normal, at least three full breaths in the file. Chest piece on bare skin. |
| Noise | Write down the setting (RHU, ward, home) in `patients.csv`. Do not throw noisy recordings away: the model has to work in noise. Only reject recordings where breath sounds cannot be heard at all. |

## 3. Folder structure and file names

```
data/local/
├── patients.csv
├── labels.csv
└── recordings/
    ├── P001/
    │   ├── P001_Al_20261120_1.wav
    │   ├── P001_Al_20261120_2.wav
    │   └── P001_Pr_20261120_1.wav
    └── P002/
        └── ...
```

File name: `<patient code>_<site>_<YYYYMMDD>_<number>.wav`. The scripts reject any file that does not follow it.

**patients.csv**

| patient_id | age_group | sex | setting | device | consent_on_file |
|---|---|---|---|---|---|
| P001 | Adult | F | RHU | Resondi VER 2.0 | yes |
| P002 | Child | M | Hospital ward | Resondi VER 2.0 | yes |

Do not add a diagnosis column for training. The model learns sounds, not diseases (section 4).

## 4. Labelling: sounds, not diagnoses

This is the most important rule in the whole procedure. The old model was trained on each patient's diagnosis (asthma, pneumonia and so on) stamped on every second of their audio. A pneumonia patient does not crackle in every second, so the model learned to recognise patients instead of sounds. Do not repeat it.

**Label each breathing cycle** (one inhale and exhale) with what can be heard in that cycle:

| Label (exact spelling) | When to use it |
|---|---|
| `Crackles` | Crackles in this cycle, no wheeze |
| `Wheezing` | Wheeze in this cycle, no crackle |
| `Wheezing with Crackles` | Both in this cycle |
| `Healthy` | Neither |

**labels.csv**, one row per breathing cycle:

| file | start | end | rater1 | rater2 | final_label |
|---|---|---|---|---|---|
| P001_Al_20261120_1.wav | 0.42 | 3.10 | Crackles | Crackles | Crackles |
| P001_Al_20261120_1.wav | 3.10 | 5.86 | Healthy | Wheezing | Healthy |

- `start` and `end` are in seconds from the start of the file. Mark them in Audacity (free): select one cycle with the mouse and read the selection start and end.
- **Two raters label every cycle independently**, without seeing each other's labels or any AI result. Use clinicians: a pulmonologist, or a physician or nurse trained in auscultation.
- **Where they disagree,** a third person, or the two together, decides and writes `final_label`. A disagreement with no `final_label` is left out until it is settled.
- Keep the raters' columns. The script reports their agreement, which belongs in the paper: a model cannot be judged more reliably than its labels.

## 5. Check the dataset

```powershell
python scripts\add_local_dataset.py data\local
```

This writes `data\local\manifest.csv` (only the cycles that passed) and `data\local\validation-report.txt` (what was rejected, and why). It never deletes anything.

| Problem | What the script does | What you do |
|---|---|---|
| File cannot be opened (corrupted) | Rejects the file | Copy it again from the device's card; if still bad, re-record |
| Exact duplicate of another file | Keeps the first, rejects the copy | Check the file names; a duplicate under a different site name is a filing mistake |
| Clipped (more than 1% of samples at full scale) | Rejects the file | Re-record with the chest piece pressed less hard |
| Silent | Rejects the file | Check the microphone and the contact with the skin |
| Wrong file name or site code | Rejects the file | Rename it |
| Cycle outside the file, or shorter than 0.3 s or longer than 10 s | Rejects the cycle | Fix the times in `labels.csv` |
| Same cycle labelled twice | Keeps the first | Remove the duplicate row |
| Label not one of the four | Rejects the cycle | Fix the spelling |
| Raters disagree, no final label | Leaves the cycle out | Adjudicate |
| Patient without consent | Leaves the patient out | Do not use the data until consent is on file |

**Noisy recordings** are not rejected automatically. Keep them if the breath sounds can still be heard, and note the setting in `patients.csv`. If the raters cannot label a cycle because of noise, leave that cycle out of `labels.csv`.

**Suspected wrong labels.** After training, open `results\test-report.txt`. If a few local cycles are confidently misclassified, have a rater listen to them again before blaming the model. Correct `labels.csv` only on a rater's decision, never because the model disagreed.

Run the check until the report shows nothing you did not expect. Then repeat it whenever recordings or labels are added.

## 6. How much data is enough

Aim for at least **100 patients**, including children and adults and including patients with and without abnormal sounds. Every one of the four labels needs at least **100 cycles**; `Wheezing with Crackles` is the hardest to collect, so look for it on purpose. Patients matter more than recordings: 100 patients with 5 recordings each are worth more than 20 patients with 25.

## 7. Combine with ICBHI and split by patient

```powershell
python scripts\prepare_data.py --icbhi "C:\Users\Hared\Downloads\archive.zip" --local data\local\manifest.csv
```

What this does:

- **Combines** ICBHI and the local cycles into one `work\manifest.csv`. Local patient codes are prefixed `ph_` so they can never collide with ICBHI's numbers.
- **Splits by patient,** about 70% train, 15% validation and 15% test. Every recording of a patient goes to the same group. This is what keeps the test honest.
- **Keeps every ICBHI patient where it was before.** Only the new local patients are assigned. So the ICBHI test patients stay the same, and results before and after adding local data can be compared.
- **Cuts each cycle into 1-second windows and computes MFCC features**, with the same settings as the app's model.
- **Stops with an error** if any patient ends up in two groups.

Never move a test patient into training to get more data, and never look at test results to decide anything about training.

## 8. Retrain

```powershell
python scripts\train.py
```

This trains the same model architecture on the combined training set, uses the validation patients to pick the best epoch, and saves `work\model.pt`. It does not touch the test patients.

## 9. Evaluate

```powershell
python scripts\evaluate.py
```

This writes `results\test-report.txt`. Read these numbers, not accuracy alone (Healthy is about half of all cycles, so a model that always says Healthy scores about 55%):

- **Recall per class.** Of the cycles that really had crackles, how many did the model catch? This matters most for a screening aid.
- **Precision per class.** When the model says crackles, how often is it right?
- **Balanced accuracy and macro F1.** These average the four classes equally, so the rare classes count.
- **Confusion matrix.** It shows which sounds are confused with which.
- **The majority-class baseline,** printed next to accuracy. A model must beat it to be worth anything.

**Compare against the baseline.** Copy `results\test-report.txt` from the ICBHI-only build before retraining (for example to `results\run-A-icbhi-only.txt`). The local data helped only if the same ICBHI test patients do at least as well as before and local test patients do better.

**Report local test patients separately.** For the paper and the pitch, the most important number is performance on the local test patients, because they are the people the device is for.

## 10. Export and put it in the app

The app runs an Edge Impulse WebAssembly model. Follow `docs\EDGE-IMPULSE-RETRAINING.md`:

1. `python scripts\export_edge_impulse.py --icbhi "<path to archive.zip>"` writes every labelled cycle, local ones included, as clips with an `info.labels` file that keeps the patient split.
2. Upload them to Edge Impulse, train with the same settings, and test on the testing category.
3. Deploy as WebAssembly (browser), then run `node scripts\check_deployed_model.js <deployment folder> export\edge-impulse\testing`. It must print PASS, and its test accuracy should be close to `results\test-report.txt`.
4. Publish the model to its own folder on GitHub, and point the app at that exact commit (`app-changes\model-4-class-labels.md`).

## 11. Record what you did

Keep together, for the paper and for anyone who checks your work later:
- `data\local\validation-report.txt`, including the raters' agreement;
- `work\manifest.csv`, which shows which patient went to which group;
- `results\test-report.txt` for each run, with its date;
- the Edge Impulse project name and deployment version, and the GitHub commit the app uses.
