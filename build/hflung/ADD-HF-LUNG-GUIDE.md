# Adding HF_Lung_V1 to the Edge Impulse model

**Read this first.** Do not add HF_Lung_V1 until the patient-wise re-split is done and Run A has a number. Adding a second corpus on top of the leaking split does two bad things at once: it makes the leak worse, and it makes the result unreadable — you will not know whether a change came from the new data or from fixing the split. Your IMRaD already says this in Table 2, and this guide follows that plan.

---

## What you are adding

**HF_Lung_V1** (Hsu et al., 2021) — 9,765 fifteen-second recordings from approximately 279 subjects, collected in Taiwan, released open-access under **CC BY 4.0**. Roughly ten times the recording count of ICBHI 2017, from an East Asian population rather than a European one.

Repository: `github.com/techsupportHF/HF_Lung_V1`

Two things it is **not**: it is not Filipino data, and it does not remove the need for local collection. Its value is that it is free, large, and East Asian, which narrows the population gap between training and deployment before a single Filipino recording is made.

---

## Step 0 — prerequisite

Finish the re-split first:

```bash
python rebuild_dataset.py /path/to/icbhi
```

Upload, retrain, and **write down Run A's accuracy, confusion matrix and per-class recall**. That is your baseline. Without it, nothing after this is measurable.

---

## Step 1 — get the data

```bash
git clone https://github.com/techsupportHF/HF_Lung_V1.git
```

Check the repository's own README for the licence terms and cite it as the licence requires. CC BY 4.0 means you must attribute.

---

## Step 2 — inspect the label format before trusting any parser

**Do not skip this.** The adapter in `merge_corpora.py` is written from the documented format; your copy must be confirmed against it.

```bash
python merge_corpora.py --inspect /path/to/HF_Lung_V1
```

It prints real filenames, durations, sample rates, raw label lines, whether each line parsed, and every event token it found with the class it maps to.

**Stop and fix if you see either:**
- `parsed: False` on any line → the `HF_LINE` regex does not match your files
- `** UNKNOWN **` against a token → add it to `EVENT_MAP`

Expected tokens: `I` and `E` (inhalation, exhalation — not pathology), `D` (discontinuous adventitious sound → **Crackle**), `Wheeze`, `Stridor`, `Rhonchi`.

### One decision you must make

Stridor and rhonchi are continuous adventitious sounds with no slot in your four-class scheme. At the top of the script:

```python
CAS_POLICY = "drop"     # or "wheeze"
```

- `"drop"` — discard those events. Cleaner classes, less data. **Default, and what I would choose.**
- `"wheeze"` — fold them into Wheeze. More data, but you are then claiming a wheeze detector that fires on rhonchi.

State the choice in the paper either way. A reviewer who knows HF_Lung_V1 will ask.

---

## Step 3 — merge

```bash
python merge_corpora.py --icbhi /path/to/icbhi --hflung /path/to/HF_Lung_V1 --out merged_dataset
```

### The three rules it enforces

**Patients are partitioned before any audio is opened.** Same rule as the single-corpus script.

**The test partition is ICBHI patients only, and it never changes.** This is the part people get wrong. Your ablation compares runs trained on different corpora — if the test set grows when the training set grows, no two runs are comparable and the whole table is meaningless. ICBHI is the only corpus present in all four runs, so ICBHI holds the test set.

**HF_Lung_V1 goes entirely into training, except a 20% block of its own patients** kept as a separate `hf_holdout` set. That gives you an East Asian generalisation number reported *alongside* the primary comparison, never mixed into it. It is also the figure that answers "does this work on Asian patients?" directly.

**Patient IDs are namespaced** — `icbhi_101`, `hf_steth_20190812`. ICBHI numbers patients from 101; HF_Lung numbers its own from 1. Without namespacing, two different people collide into one group and the split silently leaks again.

### Output

```
merged_dataset/
    manifest.csv                     patient, corpus, label, category per clip
    training/{Healthy,Crackle,Wheeze,Both}/*.wav
    testing/{...}/*.wav              ICBHI test patients — the fixed comparison
    hf_holdout/{...}/*.wav           HF_Lung held-out patients — reported separately
```

The script asserts zero patients cross a partition and refuses to finish otherwise.

---

## Step 4 — check the size before you upload

HF_Lung_V1 is about **7× the audio of ICBHI**. Expect tens of thousands of clips.

```bash
find merged_dataset/training -name '*.wav' | wc -l
du -sh merged_dataset
```

**Edge Impulse's free tier caps total data and compute.** If the merged set exceeds it you have three options, in order of preference:

1. **Apply for the free Edge Impulse education/research plan** — you are a student research project and this is exactly what it exists for. Highest limits, costs nothing, takes a few days. Start this now rather than when you hit the wall.
2. **Subsample HF_Lung by patient, never by clip.** Keep every clip from a random subset of patients. Taking random clips would reintroduce the exact leak you just fixed.
3. **Train outside Edge Impulse** (TensorFlow/Keras locally) and import the model. More control, more work, and it breaks your current deployment path.

---

## Step 5 — upload

```bash
cd merged_dataset
for lab in Healthy Crackle Wheeze Both; do
  edge-impulse-uploader --category training --label $lab training/$lab/*.wav
  edge-impulse-uploader --category testing  --label $lab testing/$lab/*.wav
done
```

Hold `hf_holdout/` back. Upload it only when you are ready to score it, as a separate project or a later testing batch — otherwise it ends up in training by accident.

**Never press "Perform train/test split" afterwards.** It reshuffles at clip level and destroys every partition you just built.

Impulse settings stay as before: window size 5000 ms, **window increase 5000 ms** (equal — anything smaller re-creates overlap inside a clip), frequency 16000 Hz.

---

## Step 6 — run the ablation your IMRaD already promises

Four runs, one fixed test partition:

| Run | Training corpus | Architecture | Question it answers |
|---|---|---|---|
| **A** | ICBHI only | MFCC + CNN | The honest baseline |
| **B** | ICBHI only | Three-branch fusion | Is fusion worth its parameters on the data you already have? |
| **C** | ICBHI + HF_Lung_V1 | Best of A/B | Do more recordings help more than a better architecture? |
| **D** | ICBHI + HF_Lung + local | Best of A/B | Does Filipino data add beyond East Asian data? |

Run D is the one that matters for the funding argument, and it is the one you cannot run until the ₱46,000 recording line is spent. That is the point: C is free and you can do it now, D is what the money buys.

Report each run on the fixed ICBHI test partition. Report the `hf_holdout` score separately, labelled as East Asian external validation.

**McNemar's test is correct here** — comparing two classifiers on the same fixed test set, paired predictions. This is the one place in the project it belongs.

---

## Step 7 — what to expect, and what to report

Accuracy may not rise much. HF_Lung_V1 is a different recording setup, different microphones, different clinical population — a model trained on both has a harder job than one trained on either. **Per-class recall is where to look**, particularly Wheeze: your MFCC-only classifier is predicted to be weakest there, because MFCCs discard the pitch that defines a wheeze, and HF_Lung_V1 is rich in continuous adventitious sounds.

Report, for every run:

- Accuracy **against the 53% majority-class baseline**, not against 25% chance
- Confusion matrix
- Per-class precision, recall and F1
- The `hf_holdout` figure, separately

A run that moves accuracy by two points but lifts Wheeze recall by fifteen is a success, and only the per-class numbers will show it.

---

## What this lets you say

Right now your concept note says the corpus is European and silent on everything else. After Run C you can say:

> The model is trained on ICBHI 2017 together with HF_Lung_V1, an open-access Taiwanese corpus of 9,765 recordings, which narrows the population gap between training and deployment at no cost. It remains trained on no Filipino recordings, which is the single component obtainable from no public source and what the recording and annotation line funds.

That converts "we have no Asian data" from a weakness a judge finds into a step you have already taken.
