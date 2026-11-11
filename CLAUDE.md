# RESONDI — Project Handoff

> **This folder (added 6 Nov).** The handoff below uses cloud paths: `proj/build/...` is this folder's `build/...`. `final/01`, `03`, `15`, `16` are the 6 Nov documents **as supplied**. **Their builders are not in this folder:** `build/cn2/build.js`, `build/script6/` and `build/qa/` here are the 2 Nov versions, so rebuilding from them brings back old facts (₱2,735, cloud not built, free first month). Edit those four documents only after the 6 Nov builders are supplied. `final/02`, `04`, `05`, `06`, `07`, `10`, `12`, `13` were rebuilt to these 6 Nov facts on 6 Nov from this folder's builders (their earlier versions are in `history/builders-2026-11-02/`); `08` is deliberately unchanged. **Device render:** `source-material/3d/Resondi_.blend` renders to `figures/Resondi-Device-3D.png` via `build/dev2/render_blend.py` (Cycles on CPU; headless EEVEE gave black frames). It is a concept render: the model is about 160 × 100 × 60 mm, not 173 × 80 × 70, so every caption says so. In `final/01` it was inserted by `build/srcfix/add_render_to_note.py`, so add it to the 6 Nov builder when that is supplied. The 2 Nov handoff and replaced files are in `history/final-2026-11-02/`. Windows build setup and PDF export: see that handoff's section B3. **Chapters 1–3 (6 Nov):** `chapters/original/` holds the untouched Drive downloads; `build/chapters/build_chapters.py` applies `ch1.py`, `ch2.py`, `ch3.py` and writes `chapters/Resondi-Chapter-N-Revised.docx` plus the revision log, which is generated from the same edits. They describe the evaluated lung-only build in the past tense, matching the IMRaD. The originals held text from other papers (Makati cybersecurity, chronic kidney disease, *Ardisia squamulosa*, body shaming); do not restore it. **Figure 2 of `final/01`** was swapped in place for `figures/Resondi-Hardware-Block-VER2.png` (`build/fig/fig2_device_v2.py`); add it to the 6 Nov builder when that is supplied. **Signed certificates:** never edit the name on them (user asked 6 Nov; declined, because it would alter a signed record). `final/17` holds unsigned copies for the doctors to sign (`build/srcfix/build_cert_reissue.py`). **CirCor heart set (9 Nov):** full dataset (1.0.3, ODC-By) unpacked at `Downloads\circor\`. `build/heart/build_validation_set.py` draws a blinded set of 25 (5 each: no murmur, holosystolic, early-, mid-systolic, diastolic) into `heart-validation/` for a cardiologist, with the key in `C:\Users\Hared\Downloads\Resondi-private\heart-validation-key\`, outside this folder so Drive sync never uploads it (never share it with the reviewer; moved there 9 Nov). Drive folder “Resondi – CirCor Heart Sound Review” in cabrera.haredray's Drive holds the instructions, answer sheet and an empty `recordings` folder; the 25 WAVs must be dragged in by hand. **Model rebuild (9 Nov):** `model-rebuild/` retrains the lung model on per-cycle sound labels (Crackles, Healthy, Wheezing, Wheezing with Crackles; alphabetical = Edge Impulse output order) with a patient split. First split balanced labels only; 79% of training audio was one stethoscope and test scores were chance (kept in `results/run1-split-by-class-only/`). Split now balances labels **and devices** (65/30/31 patients). Verified on 31 test patients, whole cycles: wider 1 s network (32/64 filters) **38.1%** balanced accuracy, app-sized network 32.4%, 3 s windows no better (34.0%); chance 25%. Weak but real: never quote it as validated. **Edge Impulse rebuild done (9 Nov):** project `Resondi-Lung-4class` (Hared123) deploy v1 int8, unzipped to `model-rebuild/deploy/resondi-lung-4class-v1/browser/`; checker PASS; on 1,051 held-out clips, app-style averaging: accuracy 44.0%, balanced 33.5%. **Integrated into the app (9 Nov; PUBLISHED 10 Nov 00:12 UTC, checkpoint `6af2615526e226d3ac75e9f5`, live bundle verified to load commit `408971af`, model files reachable on jsDelivr. **Live test 10 Nov** (`model-rebuild/results/live-app-device-test-2026-11-10.md`): the pipeline works end to end on all 45 stored lung recordings, but on the 33 Resondi device recordings the top scores are only 27–34%, close to uniform. The cause is the microphone, not loudness (normalising changed 0 labels). Never claim it performs on device audio):** `src/lib/lungClassifier.js` now loads it from jsDelivr pinned to Ausculta commit `408971af2537276aa2c8a273bbe2dfa245fa13f1` (`model/resondi-lung-4class-v1/browser/`), scales samples to int16 (A6), uses non-overlapping 1 s windows (the tested method), maps the combined label before the single ones (the old regex sent "Wheezing with Crackles" to crackles), and saves `model_version: 'resondi-lung-4class-v1'` on AIAnalysis (new schema field; empty = the withdrawn model). That commit was made locally in the session scratchpad and **must be pushed to GitHub before the app can load the model**; then publish. The app's deployed model (EI 'SmartStethoscope' v5) was loaded in Node: 1 s / 16,000-sample input, labels Asthma/Bronchiolitis/Healthy/Pneumonia. The app is unchanged; rebuilding its model needs the user's Edge Impulse account (`model-rebuild/docs/EDGE-IMPULSE-RETRAINING.md`), and the app edit is `app-changes/model-4-class-labels.md`. **HF_Lung_V1 is NOT on this PC (checked 10 Nov):** `HF_Lung_V1/` is an empty broken clone, and `github.com/techsupportHF/HF_Lung_V1` now returns 404. Find an author-sanctioned copy before relying on it; §5 and §9 below predate this. **Latest model status, accuracy plan, Canva p29/p31 fixes and Drive privacy rules:** `HANDOFF-2026-11-10-model.md` sections 4–5. **11 Nov experiments:** 10 training versions (MFCC/MFE, augmentation, two detectors, mixup) on validation; the chosen one scored **35.0% balanced on the 31 test patients**, no better than the deployed v1, so tuning has reached its ceiling and the deployed model stays. The 40% field figure's reference labels are undocumented in the paper (see section 5). **In progress (section 6):** feature-fusion study (`model-rebuild/scripts/fusion.py`: MFCC + spectrogram + chromagram after Tariq et al. 2022), SPRSound (CC BY 4.0, Asian children) being added at `Downloads\sprsound\`, and the product video `figures/Resondi-Device-Video.mp4` rendering. **Decision to carry (user, 2 Nov):** same-site comparison belongs in Essential; the 6 Nov note's tier table still has it in Clinical, so confirm before editing. **BOM file:** the only VER 2.0 BOM on this PC is PETG / ₱2,875 and was kept out of `source-material/`; the ₱2,775 PLA version has not been supplied. **Old name:** left on purpose in signed certificates, `assess/` (it discusses the rename itself), `final/07` and `build/paperfix/` (find-and-replace instructions), `src/` (deck builder input) and the paper's extracted text; `final/14` lists the rest.

> **State of the project as of 6 November 2026**, written so a new Claude Code session can pick it up cold. It **supersedes** `handoff3/CLAUDE.md` (2 Nov), `UPDATE-2026-11-03.md`, and the two older handoffs. Where this file disagrees with any of them, **this file wins** — several of their numbers are now wrong, and §0 lists which.
>
> **How to use it.** Put this file in the project root as `CLAUDE.md`, then say: *"Read CLAUDE.md, then continue from the Open Work list."*
>
> **Read §0 and §1 before changing anything.**

---

# §0. WHAT CHANGED SINCE 2 NOVEMBER

The concept note went through a full adversarial review on 3 November and a pre-submission hardening pass on 3–4 November. Roughly forty corrections were applied. These are the ones that invalidate the earlier handoffs.

| Fact | Old handoff said | **Now** |
|---|---|---|
| Bill of materials | ₱2,735 | **₱2,775** (20×4 LCD replaced the OLED, 32 GB card, both repriced) |
| Enclosure material | "PETG vs PLA unresolved" | **PLA.** Settled by the user 2 Nov. The spec sheet was corrected to match. |
| Mentor | unnamed placeholder | **Still a placeholder.** A name was supplied on 3 Nov and withdrawn on 6 Nov; the note, the org chart and the script all carry a visible `[RESEARCH ADVISER NAME]` marker so it cannot be submitted unfilled. |
| Founder names | short form | **Ahnycca Krish N. Malimban · Hared Ray A. Cabrera · Jarred Paul G. Llacuna** |
| Concept note tables | 16 | **17** — new Table 4, *Projected Reach* |
| **The cloud tier** | "not built; ₱48,000 builds it" | **IT IS BUILT.** See §2 — this is the single biggest correction in this file. |
| Free first month | "costs the model nothing" | **Replaced entirely by a limited trial.** See §3. |
| Year 3 facility-months | 450 | **468** (450 was an estimate; the model says 468, examinations 28,080) |
| SAM | "approximately 3,500" | **3,518**, and now stated as a reachable-segment count, not a qualified one |
| Org chart | boxes with blue headers | **Redesigned** — editorial, no boxes, serif names, rose accents |
| Model metrics | printed 0.84 / 0.83 / 0.83 | **Removed.** They are internally impossible; the note says so and omits them. |
| Corpus derivation | presented as sound | **Disclosed as unreconcilable.** See §4 — the most important open item. |

**Also new since 2 Nov:** a cardiac output scheme, three Innovativeness sections (novelty/IP, the data asset, design decisions), an incorporation-by-minors position, an ethics position, a dB methodology caveat, churn and acquisition-cost assumptions named, and the quality-check contradiction closed in **seven** places.

---

# §1. THE PROJECT

**Resondi** is an AI-assisted smart stethoscope and mobile platform. An ESP32 device records lung and heart sounds at guided, standardised chest sites; an app classifies lung sounds into four patterns; a rule layer turns the pattern across zones into a literature-backed *possibility*, never a diagnosis; a practitioner confirms every result. **Team Wheezards**, Puerto Princesa City National Science High School, Palawan. Won the **PSC XI regional round, 26 October 2026**. Nationals is what everything is being prepared for.

The user is **Ahnycca Krish N. Malimban**, CEO. She works on **Windows** — write PowerShell, not bash.

## The four PSC XI criteria — the concept note is scored only on these

| Concept note | | Live pitch | |
|---|---|---|---|
| Business Model | **30%** | Clarity | **40%** |
| Innovativeness | **30%** | Delivery | 25% |
| Technology Viability | 20% | Visual Presentation | 20% |
| Social Impact & Relevance | 20% | Time Management | 15% |

An earlier external assessment scored against a different, older rubric (Viability 25 / Relevance 25 / Impact 20 / Creativity 20 / Presentation 10). **That rubric is wrong.** The corrected assessment is in `assess/`.

**The note's page budget is still inverted against these weights:** Business Model ~55%, Technology Viability ~32%, Innovativeness ~9%, Social Impact ~7%. Three sections were added on 3 Nov to improve Innovativeness; the imbalance is reduced, not fixed.

## Standing instructions from the user

1. **"Do not edit directly, provide the revised part here."** Applies to her Google Docs and the 83-page paper. Documents *Claude built* are edited and rebuilt directly.
2. **Code in Python and Rust.**
3. **Rose theme:** Poppins / `#FFF5F9` / `#E91E76` / `#8E2A52` / `#9E8892` / `#F7D6E4` / `#EBD3DE`.
4. **Two deliberate exceptions:** the business model canvas and all tables *inside the note* are monotone. Standalone figures are rose. The org chart is black/white with rose accents and **no fills** — do not reintroduce tinted header bands.
5. **IMRaD paper is lung-only.** The note covers both modes.
6. **Three-branch fusion and the nine-site protocol stay PLANNED**, never present tense.
7. **"40% means classifier accuracy"** — 6 of 15 recordings matched reference labels. Not device equivalence.
8. Keep note, script, deck, Q&A and paper agreeing. They have drifted repeatedly.

---

# §2. THE ARCHITECTURE — READ THIS CAREFULLY

This was wrong in every document until 4 November, and it is wrong in the **submitted** concept note.

```
Tier 1  DEVICE      ✅ BUILT     ESP32, records to microSD, raises its own Wi-Fi AP,
                                serves its own web app at http://192.168.4.1.
                                Fully offline. No app install needed.

Tier 2  GATEWAY     ❌ NOT BUILT  The link. Today a recording crosses from device to
                                platform ON A MEMORY CARD, CARRIED BY A PERSON.
                                ₱38,000 builds it.

Tier 3  PLATFORM    ✅ BUILT     Base44 app. Stores recordings against a patient record,
                                runs the classifier, presents results to a practitioner
                                for confirmation.
                                ₱48,000 RUNS it — operating cost, not build cost.
```

**The budget corroborates this and always did.** The ₱48,000 cloud category contains hosting ₱15,000, operation ₱18,000, storage ₱5,000, backup ₱5,000, domain ₱3,000, API ₱2,000 — **zero development lines**. That is an operating budget for something that exists. An adversarial review flagged "the cloud tier's software has zero budget" as a hole; there is no hole, because there is nothing left to build.

**The pitch framing**, in the script and the Q&A bank: deliver the tiers in the order **1 → 3 → 2**. Naming the gap last is what makes the ask land. *"Both ends work. The bridge doesn't. That's the ask."*

> ### ⚠ The submitted note says otherwise
> The concept note was submitted on **3 November** saying the platform *"will store recordings"* and that ₱48,000 *"funds it."* The builder was corrected on **6 November**; the submitted PDF was not. If this comes up:
>
> *"The note is conservative there — the platform runs, and we can show you. What it's honest about is that nothing moves from device to platform automatically yet."*
>
> Understating what you built is a survivable error. Do not let anyone "correct" it into an overstatement.

---

# §3. PRICING — the trial model changed on 4 November

| Tier | Price | Cloud | Reserve | Review ops | **Contribution** | Available |
|---|---|---|---|---|---|---|
| Essential | ₱1,500 | ₱350 | ₱250 | — | **₱900** | now |
| Clinical | ₱2,900 | ₱450 | ₱250 | — | **₱2,200** | after the build |
| Network (min 3) | ₱4,500 | ₱600 | ₱250 | ₱350 | **₱3,300** | after the build |

School licence **₱30,000/yr**, ₱4,200 platform cost, **₱25,800 contribution** — the figure `finpack/model.py` uses as `LIC`.

**Bundles** (Table 8): Starter ₱24,500 · Clinic ₱52,000 · Cluster ₱168,000 · Teaching ₱42,000. The governing rule: **no discount comes out of the ₱600/month on Essential, ₱700 on Clinical or ₱1,200 on Network** that pays cloud and the replacement reserve. Essential has zero headroom, so its discount comes out of device margin only.

## Trials — this replaced the free month

| Offer | Bound | Cost | Note |
|---|---|---|---|
| **Limited trial** | 14 days **or** 25 guided examinations, whichever first | **≈ ₱750** per facility | Full Essential capability, no payment details taken |
| **Feature trial** | 60 days of Clinical features **while paying Essential** | **₱200** per facility | Gives away capability, not revenue. **Cannot be offered until the ₱38,000 is spent.** |

The free-month costing was wrong three times before landing: "costs nothing" → "₱900" → **₱1,500** (the facility still consumes ₱350 cloud and ₱250 reserve during a free month, so a month that would contribute +₱900 instead costs ₱600). That is why it was replaced with a bounded trial. **Neither offer stacks; no trial auto-converts** — `onExpiry: 'prompt_tier_choice'`.

App-side config is in `pricing/subscription-tiers-spec.md`.

---

# §4. THE TWO EVIDENCE PROBLEMS

## 4a. Data leakage — still unfixed

The reported model scores are **inflated and must not be quoted**. ICBHI audio was cut into 19,246 five-second samples at a ~1-second stride, then split **at random over samples** with Edge Impulse's metadata key left empty. Near-identical audio sits on both sides of every split. Worse, training used **patient-level diagnosis labels** applied to every window, so the only consistent signal is the patient's acoustic fingerprint — the model learned *who*, not *what*.

**Affected: 71.1% (test), 83.4% (validation), 83.7% (int8).** All three. **The 40% field agreement is the only unleaked estimate.** Expect 45–60% after the fix, against a **53% majority-class baseline** (not 25% chance). `newdata/rebuild_dataset.py` is written and tested.

## 4b. The corpus cannot be reconciled — the critical open item

ICBHI is **793 of 920 recordings COPD**, and COPD is not one of the four output classes. If COPD was dropped, 127 recordings remain, which yields ~2,200 five-second windows at a one-second stride — **not 19,246**. If COPD was kept, 86% of the corpus is filed under a class that does not exist. Separately, asthma has **one patient and one recording** but reports **F1 = 0.95**, which needs ~20 test instances.

**Nobody knows which happened.** The study documentation does not record it. The note now **discloses this** before quoting any figure rather than presenting an impossible derivation. Resolving it is the first output of the Phase 2 rebuild.

**If the user ever supplies the Edge Impulse data-acquisition screen or the real class mapping, this is the highest-value thing to fix in the whole project.**

---

# §5. VERIFIED FACTS — use these

| Fact | Value |
|---|---|
| Signal | **45 dB vs 32 dB** = 13 dB ≈ **4.5× amplitude**. Never divide decibels. Now labelled *indicative margins*, not a formal SNR — the two figures were not captured against a common reference. |
| Ambient noise | 24 / 35 / 42 dB (quiet room / ward / community) |
| Recording quality | 68% good, 25% acceptable, 7% poor. **Denominator unknown** — report proportions only. |
| Response times | connection 4.55 s · recording 15.00 s · **quality check 144.68 s** · preprocessing 20.91 s · classification 3.97 s. **Table 5 of the paper is authoritative;** Figure 4.4 contradicts it and is wrong. |
| Examination time | 145 s × **14 captures** (a 20 s lung site is two 15 s recordings) ≈ **34 minutes** of screening, 45+ with Heart Mode |
| Field agreement | 6 of 15 = **40%**, Wilson CI **19.8–64.3%**, exact binomial vs 25% **p = 0.148** |
| Chance level | **25%** — four classes |
| Acceptance | **n = 27**, UTAUT, overall **3.95**. Fourth construct is **facilitating conditions** (was mislabelled "regulatory assurance"). Venkatesh et al. 2003 now cited. |
| BOM / unit cost / price | **₱2,775** → +₱625 = ₱3,400 components → +₱600 = **₱4,000** fully loaded → **₱8,000** price, 50% margin |
| Seed | **₱500,000**: validation 120k · AI 102k · contingency 50k · cloud 48k · hardware 42k · production 40k · app 38k · IP 25k · docs 20k · deployment 15k |
| Revenue (cash) | Y1 **₱175,900** · Y2 ₱426,900 · Y3 ₱885,700 · cum36 ₱1,488,500 |
| Payback | **commercial month 21 = month 35 from funding** |
| Sites | **7 lung** (6 fields + trachea) · **5 cardiac** (4 valve points **+ Erb's point** — not "five valve points") |
| Market | TAM ~30,000 · SAM **3,518** · SOM 50 facilities + 15 schools |
| Reach (Table 4) | facility-months 75 / 222 / **468**; examinations 4,500 / 13,320 / **28,080**; workers 40/100/200; students 180/420/900 |
| Mortality 2024 | IHD **134,074** · pneumonia **47,260** · together **181,334** = **25.8%** of 701,884 |
| ICBHI | 920 recordings · 126 patients · 6,898 cycles · **793 COPD recordings, 64 COPD patients** · asthma 1/1 |
| HF_Lung_V1 | 9,765 recordings · ~279 subjects · Taiwan · CC BY 4.0. **Event-labelled, not diagnosis-labelled** — cannot be merged until the output scheme moves to sound classes. |
| CirCor DigiScope | 5,282 recordings · 1,568 patients · murmur presence/timing/grading **plus S1/systole/S2/diastole segmentation** · same four valve points. **Primary cardiac corpus.** |
| ZCHSound | 941 recordings, labelled by **diagnosis** (VSD/ASD/PFO/PDA/control), smallest class 32. **External validation only — never train sound classes on it.** |
| Device | ESP32 240 MHz · INMP441 digital MEMS on I²S (no preamp) · 16 kHz/16-bit mono WAV · 15 s · 480 kB · 32 GB microSD · 20×4 I²C LCD · 2 buttons · 2.4 GHz Wi-Fi AP `RESONDI_WIFI` · 10,000 mAh · **PLA**, FDM, **173 × 80 × 70 mm** |
| Competitors | Eko CORE 500 $449 · **CORE 300 $199–249 ≈ ₱11,500–14,500** (more than Resondi) · Littmann CORE $379 ≈ ₱22,000 · Thinklabs One $499 · E-Steth (UP/PCHRD, TRL 5) · **Auscultate (SLU), 1st runner-up PSC X Dec 2025** |

**Eko's AI is not sold in the Philippines or anywhere in ASEAN**, and Eko stores all cloud recordings in the United States. No vendor reviewed documents same-site longitudinal comparison — say *"not documented by any vendor reviewed"*, never *"does not exist"*.

---

# §6. CARDIAC OUTPUT SCHEME (added 3 Nov)

Heart Mode records today and classifies nothing. The planned output follows the lung discipline — acoustic description, never a diagnosis:

- **Delivered by the funded work** (CirCor-supported): S1 and S2 identified and timed; murmur present/absent; murmur timing (systolic/diastolic); quality gate.
- **Named but NOT promised:** S3 and S4. No public corpus labels them at a usable patient count. Claiming them would repeat the asthma-is-one-patient error. Scoped to local annotation.

---

# §7. FILES AND BUILDS

> **Only `proj/build/cn2/build.js` is current.** An older `cn2/build.js` may exist; it is stale and will silently rebuild an old document. Check the date before editing.

```bash
cd proj/build/cn2 && node build.js      # → proj/deliverables/Resondi-Concept-Note-FINAL.docx
```

**`package.json` pins `docx@^9.15.0`.** A different version inserts three stray blank paragraphs. Figures are read from `proj/figures/`, so copy a new figure there *before* building.

| Deliverable | Builder | State |
|---|---|---|
| `proj/deliverables/Resondi-Concept-Note-FINAL.docx` | `proj/build/cn2/build.js` | **352 paras, 17 tables, 12 figures, 0 placeholders.** Current, and ahead of the submitted version. |
| `brief/Resondi-Pitch-and-QA-Brief.docx` | `brief/gen.py` | **NEW 4 Nov.** Six parts: numbers to know cold, five critical answers, 13 one-liners, what never to say, delivery, known gaps. |
| `qa/Resondi-QA-Answer-Bank.docx` | `qa/gen.py` | **NEW 4 Nov.** 30 questions, spoken answers, CEO/CTO/COO assignments. |
| `script7/Resondi-Pitch-Script-REVISED.docx` | `script7/gen.py` | **NEW 4 Nov.** 772 words ≈ 5:31; 649 ≈ 4:38 with CUT lines. Includes the architecture walkthrough. |
| `assess/Resondi_Concept_Note_PSC_XI_Assessment.docx` | built inline | Rescored against the **real** criteria |
| `spec/RESONDI_Product_Specifications.docx` | — | Corrected to PLA |
| `bom/Resondi_Bill_of_Materials_VER2.0.docx` | — | ₱2,775 |
| `changelist/…Change-List.docx` | built inline | 69 OLD/NEW blocks from a parallel revision |
| `qa/Resondi-Judge-QA.docx` | `qa/build_qa.py` | 111 questions, 34 flagged DECIDE. **Table references may be stale** — three tables were inserted. |
| `imrad/`, `script6/`, `accept/`, `finpack/`, `stats/`, `cue/` | their own builders | Unchanged since 30 Oct |

**Figure scripts:** `finpack/model.py` is the **single source of truth for every money figure — import it, never retype**. `fig/fig9_org.py` (org chart, redesigned), `dev2/device_fig.py` (device render from the STLs), `figs_nov/{tiers,bundles}.py`, `deckfigs/build.py`, `newdata/rebuild_dataset.py`, `hflung/merge_corpora.py`.

**Environment:** Node + `docx@^9.15`; Python with `python-docx`, `openpyxl`, `matplotlib`, `trimesh`, `playwright`, `scipy`, `soundfile`, `pypdf`, `Pillow`. LibreOffice for PDF. **Never run project builds with `python -I`** — it drops the script directory from `sys.path`.

---

# §8. FIVE TRAPS

1. **The stale builder.** Check the date on `build.js` before editing.
2. **Table renumbering.** Inserting one table moves every later number *and* every prose reference. Substitute **descending** with a negative lookahead so `Table 1` never eats `Table 11`, protect new captions with placeholders first, then verify captions come out `1..N` and no reference dangles.
3. **The user is on Windows.** Bash loops and `*.wav` globbing do not work. She has hit the PowerShell execution-policy wall — `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, with `npm.cmd` as fallback.
4. **Grep false positives.** `BLE` matches inside `PROBLEM`. `PLA` inside `PLAN`/`PLATFORM`. `OLED` inside `pooled`. `Ausculta` inside `auscultation`. **Read the context of every hit.** Two "findings" in an external review were this and nothing more.
5. **Batch edits abort as a unit.** The edit scripts used here write nothing if any one pattern misses. Read the output — "PARTIAL" means *nothing was saved*, not "most of it worked."

---

# §9. OPEN WORK

### Blocking
1. **Resolve the corpus question (§4b).** Needs the Edge Impulse screen or the real class mapping. Highest value in the project.
2. **Run the patient-wise re-split** (`newdata/rebuild_dataset.py`), record Run A's accuracy, confusion matrix and per-class recall. Then update the note's model section, `stats/`, the IMRaD, slide 11 and the `DISPLAY` dict.
3. **Then** add HF_Lung_V1 (`hflung/merge_corpora.py --inspect` first). Four-run ablation on one fixed ICBHI test partition. **C is free and runnable now; D is what the ₱46,000 buys.**

### Owed by the user, not by Claude
- One signed letter of intent. Still the cheapest point gain available.
- The 15 paired classifications, so Cohen's kappa and the confusion matrix can be computed — the protocol specified both and neither was done.
- Test–retest repeatability (record the same site twice). A morning's work, and the most relevant number for a device selling comparability.
- Battery life in hours; time for a midwife to complete a seven-site exam.
- Palawan baseline: RHU count, facilities without a resident physician, cost of a referral trip.
- **PhilHealth Konsulta — now rebranded YAKAP.** Whether a guided auscultation is reimbursable, or the subscription chargeable against the per-capita fund. Scores against Business Model *and* Social Impact. Any older material will say "Konsulta".
- Pilot devices are **unbudgeted** — roughly ₱32,000 including two cluster spares and six school units.
- Confirm with DICT MIMAROPA whether contributors beyond the three founders are allowed.
- **The research adviser's name.** Three files carry a visible placeholder: `proj/build/cn2/build.js` (§IX prose), `fig/fig9_org.py` (Figure 10), `script7/gen.py` (Slide 16). Change the string in each and rebuild — one line per file.

### Documents still out of sync
- **The pitch deck.** Still needs: name → Resondi, PSA 134,074/47,260, seven sites, 45 vs 32 dB, 25% four-class chance + leakage disclosure, month 21/35, Y1 ₱175,900, ask ₱500,000, acceptance 3.95/27 — and now the VER 2.0 device, the three-tier framing, and the tier ladder. Placeholders: founder achievements, logo on transparent background, one-colour logo, 32 px icon, LOI.
- **The 83-page paper** (`RIM-FULLPAPER-2026-9_1.pdf`). User's document — **provide pasteable text, do not edit.** Needs McNemar and the three paired t-tests removed; signal → 45/32; noise → 24/35/42; Figure 4.4 corrected against Table 5; six locations → seven; Data Analysis reworded; leakage disclosure added; Section G reported or deleted.
- **The live Base44 app still guides nine lung sites** while every document says seven. `app-changes/seven-sites.md` has the fix. Unapplied.
- **IP ownership** still "to be formalized with the school".
- **Base44 meta tags** still say `ausculta.base44.app`.

### Pitch-day items
- Confirm the **actual time limit**. The script runs 4:38–5:31. Seventeen slides in three minutes is ten seconds a slide and is not deliverable; if the limit really is three minutes, **merge slides, don't shave lines**.
- Check whether the practitioner queue in Figure 4 is live or test data. The note says test recordings.
- Agree who answers what. The Q&A bank carries CEO/CTO/COO tags; a panel tests consistency by asking two founders the same question.

---

# §10. THE EDITORIAL STANDARD

Every deliverable separates **what exists** from **what the funding builds**, present tense and future tense respectively, and never blurs them. That discipline is why the device section survived contact with the real spec sheet, why the leakage finding reads as rigour instead of failure, and why a 40% accuracy figure does not sink the pitch. When a new fact contradicts a claim, the move is to **state the gap and what closes it** — never to quietly soften the claim.

Four examples now in the note:

- *"Asian representation is therefore not absent from the plan; Filipino representation is what remains to be bought."*
- *"Both ends of this system work. The link between them is what this round funds."*
- On blinding: it was not recorded, so the note says so and commits to a protocol that records it.
- On the corpus: the derivation cannot be reconciled, so the note says that **before** quoting any figure from it.

The user has been consistently willing to publish an unflattering number. That is the project's main asset. **Do not let an edit trade it for a better-looking one.**

## Privacy — carry forward

- The acceptance CSV holds respondent **names and e-mail addresses**. Never put them in a deliverable; never print them.
- Earlier app screenshots held a **named minor patient with medical history**, a PRC number, phone numbers and e-mails. All excluded; screenshots are masked to "Hello, Patient" / "Welcome, Doctor".
- The user once screenshotted a **live Kaggle API token**. It was redacted and she was told to revoke it. Never reproduce it.
- **Never enter credentials into any login form.** This blocked reading Edge Impulse directly; the workaround is to ask her for screenshots.
