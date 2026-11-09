# RESONDI — Project Handoff

> **What this is.** The current state of the Resondi project as of **30 October 2026**, written so a new Claude Code session can pick the work up cold. It supersedes `RESONDI-HANDOFF.md` (27 Oct). That older file still holds the turn-by-turn history of the original 503-turn conversation; keep it for provenance, but **this file is the source of truth for what is true now.**
>
> **How to use it.** Put this file in the project root as `CLAUDE.md`, unzip the workspace next to it, then say: *"Read CLAUDE.md, then continue from the Open Work list."*
>
> **Read all of Part A before changing anything.** Several numbers in the older handoff are now wrong, and Part A says which.

---

# PART A — WHAT IS TRUE NOW

## A1. The project in one paragraph

**Resondi** is an AI-assisted smart stethoscope and mobile monitoring platform. An ESP32-based digital stethoscope records lung sounds at guided, standardized chest sites. A mobile-first app (built on Base44) tags each recording by site, stores it, and runs a CNN that sorts it into four sound patterns. A rule layer turns the pattern across chest zones into a literature-backed *possibility*, never a diagnosis, and a practitioner confirms, modifies or rejects every result. Longitudinal comparison at the same site across visits supports rehabilitation tracking. The team is **Team Wheezards**, from **Puerto Princesa City National Science High School (PPCNSHS)**, Palawan. They **won the DICT Philippine Startup Challenge XI regional round on 26 October 2026**; nationals are next. It is also a school research paper.

## A2. Names

| Era | Name |
|---|---|
| Earliest research | SmartSteth (the Edge Impulse project is still called "SmartStethoscope") |
| 8–25 Oct 2026 | Ausculta |
| 26–27 Oct 2026 | Auscora (short-lived) |
| **Now** | **RESONDI** |

When renaming, replace only the product name. **Never** touch *auscultation* / *auscultatory* / *auscultate*. Safe pattern:

```python
PAT = re.compile(r"\b(AUSCULTA|Ausculta|ausculta|AUSCORA|Auscora|auscora)\b")
def sub(m):
    w = m.group(1)
    return "RESONDI" if w.isupper() else ("Resondi" if w[0].isupper() else "resondi")
```

The following still carry the old name and need changing: the GitHub repo (`https://github.com/HaredRay1/Resondi` — renamed, but check contents), the Base44 app's meta tags (canonical domain still reads `ausculta.base44.app` even though the site serves at `resondi.base44.app`), the Edge Impulse project, and the 83-page research paper PDF.

## A3. People — CHANGED 30 OCT, read this

PSC rules allow **3 students + 1 mentor**. The concept note previously described "ten proponents" reporting to a "Board of Regents", which was an eligibility risk and a naming error.

**Now stated as:**

- **Founders (the registered startup team):** Ahnycca Krish N. Malimban (Managing Director, data and model operations), Hared Ray Cabrera (Platform operations and security), Jarred Paul Llacuna (Production and supply chain). These three are marked `Founder ·` in Figure 10 and are the pitch presenters (A / H / J in the script).
- **Mentor:** the research adviser from the PPCNSHS research programme.
- **Seven contributing members**, shown in Figure 10 without the Founder marker, described in the text as positions staffed as the business grows: David James Segay (application development), Arvin Rogel Coronado (product and AI), Paul Brent Gabayan (device maintenance and field service), Andee Marie Biaco (clinical affairs), Chesca Jomaicha Trajano (regulatory, compliance, Data Protection Officer), Angela Naverra (sales and customer success), Jared Zai Elli (finance and administration).
- **"Board of Regents" is now "Advisory Board"** everywhere. (A Board of Regents is a state university's governing body — wrong term for a startup.)

> **Open:** nobody has confirmed with DICT MIMAROPA whether contributors beyond the three founders are permitted. The current wording is written to be safe either way, but the user should confirm.

## A4. Standing instructions from the user

1. **"do not edit directly, provide the revised part here."** Applies to the user's own Google Docs and the 83-page paper. Give pasteable text; never write to their documents. Documents *Claude built* (concept note, script, Q&A, IMRaD) are edited and rebuilt directly.
2. **Code in Python and Rust.**
3. **Keep the Resondi rose theme.** Poppins / `#FFF5F9` background / `#E91E76` app pink / `#8E2A52` deep rose / `#9E8892` muted / `#F7D6E4` pale. Older matplotlib figures use DejaVu Serif with `#8E2A52` primary, `#B5537E` secondary, `#C27396` light.
4. **Two deliberate exceptions to the rose theme**, set 28 Oct: the **business model canvas** and **all tables** are monotone (black / grey / white) for legibility. Do not "fix" them back to pink.
5. **IMRaD paper is lung-only.** The concept note covers both Lung and Heart modes.
6. **Keep three-branch fusion and the nine-site protocol as PLANNED**, never present tense. The deployed model is MFCC + CNN over seven sites.
7. **"40% means classifier accuracy"** — 6 of 15 recordings agreed with reference labels. Not device equivalence.
8. Keep the concept note, script, slides and paper agreeing with each other. They have drifted repeatedly.

## A5. Verified facts — use these numbers, not the older handoff's

| Fact | Value | Source / note |
|---|---|---|
| Signal strength | **45 dB** vs **32 dB** conventional | 13 dB gap = **~4.5× amplitude**. The old "32.49 vs 7.89 dB, 4× stronger" is wrong twice over: wrong figures *and* dB can't be divided. |
| Ambient noise | quiet room **24**, ward **35**, community area **42** dB | Headroom against a 45 dB signal: 21 / 10 / **3** dB |
| Recording quality | **68% good, 25% acceptable, 7% poor** | **Denominator unknown** — not stated anywhere in the paper. The concept note now reports proportions without a count. |
| Response times | connection **4.55 s**, recording **15.00 s**, quality assessment **144.68 s**, preprocessing **20.91 s**, classification **3.97 s** | **Table 5 of the paper is authoritative** (user confirmed 28 Oct). Figure 4.4 of the same paper gives different values for all five and is wrong. |
| Field agreement | **6 of 15 = 40%**, Wilson 95% CI **19.8–64.3%**, exact binomial vs 25% chance **p = 0.148** | 8 of 15 would have been needed for significance |
| Chance level | **25%** (four classes) | A reviewer's note claiming 33% / three classes is wrong |
| Acceptance survey | **n = 27** (13 patients, 13 general respondents, 1 practitioner) | **Not 30.** See A7. |
| Prototype parts cost | **₱2,735.00** | New BOM, 30 Oct. Excludes battery protection/BMS and charging by its own note. Supersedes ₱2,094.47. |
| Unit economics | ~**₱4,000** fully loaded cost, **₱8,000** price | ~50% gross margin from first unit |
| Seed requested | **₱500,000** | Not ₱300,000 — that figure appears only as a deliberate comparison |
| Revenue (cash) | Y1 **₱175,900** · Y2 **₱426,900** · Y3 **₱885,700** · cum36 **₱1,488,500** | Run-rate equivalents: Y1 ₱225,400, Y2 ₱510,600 |
| Seed recovery | **commercial month 21** = **month 35 from funding** | Investor 40% share resolves later, in commercial Year 3 |
| Auscultation sites | **SEVEN**: Tc, Al, Ar, Pl, Pr, Ll, Lr | Six lung fields + tracheal reference. Confirmed against the ICBHI corpus itself. Nine sites is the *planned* protocol. |
| PSA mortality | IHD **134,074**, pneumonia **47,260**, total deaths **701,884** | Updated figures; older decks use 133,373 / 46,718 |
| ICBHI corpus | 920 recordings, 126 patients, 6,898 cycles | Cycle-level: Healthy **52.8%**, Crackle **27.0%**, Wheeze **12.8%**, Both **7.3%** |

## A6. THE LEAKAGE FINDING — the most important thing in this file

The model's reported scores are **inflated and should not be quoted as evidence of field performance.**

**What happened.** The ICBHI audio was cut into 19,246 five-second samples at a ~1-second stride (5/S = 4.86× expansion over ~19,800 s of source audio). Consecutive samples therefore share four of their five seconds. Those overlapping samples were then split into train/validation/test **at random, over individual samples**, with Edge Impulse's "split train/validation set on metadata key" field left **empty**. Near-identical audio sits on both sides of every split.

**Three separate errors, in order of severity:**

1. **Windowing before splitting.** Patients must be partitioned *first*; windowing happens inside each partition.
2. **No grouping key on either split.** The metadata key governs only train/validation; the train/test split is a separate operation and does not honour it.
3. **Label granularity.** The model was trained on *patient-level diagnosis labels* (Asthma / Bronchiolitis / Pneumonia / Healthy) applied to every window of that patient's audio. A pneumonia patient does not have crackles in every second. The only signal consistent across all of one patient's windows is **that patient's acoustic fingerprint**, so the model learned *who*, not *what*.

**Affected numbers:** 71.1% (test), 83.4% (validation), 83.7% (int8 validation). **All three.** The **40% field agreement is the only unleaked estimate.**

**The fix** is written and tested: `rebuild_dataset.py` (see B2). It partitions the 126 patients first, prefers the official ICBHI challenge split, cuts one 5-second clip per annotated respiratory cycle with **no overlap**, labels each from its own crackle/wheeze flags, and asserts zero patients cross the split. Then upload with `--category training` / `--category testing` explicitly, set window increase = window size = 5000 ms, and never press "Perform train/test split" (it reshuffles at sample level and destroys the partition).

**Expect accuracy to fall to roughly 45–60%.** That is the correct outcome. Note the majority-class baseline is **53%** (Healthy), not 25% — report the confusion matrix and per-class recall, not accuracy alone.

If the class names change to Healthy / Crackle / Wheeze / Both, the app's `DISPLAY` dict and the interpretation rule layer both key off the old disease names and must be updated:

```javascript
const DISPLAY = {
  Wheeze:  'High Pitched Wheezing',
  Both:    'Wheezing With Crackles',
  Crackle: 'Crackles',
  Healthy: 'Healthy (Soft)',
};
```

## A7. The acceptance survey — rewritten 28 Oct

The Google Forms export did **not** measure what the paper said it measured. The paper described five dimensions (user-friendliness, usability, durability, functionality, community impact). The actual instrument is a **UTAUT** questionnaire. There is no durability item and no community-impact item anywhere in it.

**Decision taken (user approved):** rewrite the methodology around UTAUT rather than force-map the items. UTAUT (Venkatesh et al., 2003) is an established, citable framework and is the stronger position.

| Construct | Items | n | Mean | SD | Verbal | α |
|---|---|---|---|---|---|---|
| Performance expectancy | 3 | 27 | 4.09 | 0.59 | Agree | 0.51 |
| Effort expectancy | 3 | 27 | 4.09 | 0.60 | Agree | 0.76 |
| Regulatory assurance | 5 | 27 | 3.84 | 0.61 | Agree | 0.59 |
| Social influence | 1 | 27 | 3.63 | 1.21 | Agree | — |
| **Overall (12 Likert items)** | 12 | 27 | **3.95** | — | **Agree** | — |

Dichotomous items (report as frequencies, never means): peers encourage use 21/27 (78%); institution provides resources 20/27 (74%); access to training — maybe 12 (44%), yes 8 (30%), no 7 (26%); prior device experience 11/27 (41%).

**Known weaknesses, all disclosed in the documents:** three behavioural-intention items and all open-ended items returned **zero responses** (respondents never reached that page); four items are Yes/No and cannot be averaged; the option list contains a typo (`Stongly Agree`, 9 occurrences) alongside two other spellings; only one practitioner responded, so items about institutional resources and professional practice were largely answered by people they don't apply to; five of twelve Likert items ask about ISO conformity the device has **not** achieved.

Rerun with `newdata/analyse_acceptance.py`. It never reads the name, e-mail or timestamp columns.

## A8. Privacy rules — carry these forward

- Earlier app screenshots contained **a named minor patient with medical history**, a **PRC number**, phone numbers and e-mail addresses. All excluded from every deliverable. App screenshots are masked to "Hello, Patient" / "Welcome, Doctor".
- The acceptance CSV contains **respondent names and e-mail addresses**. Never put them in a deliverable; never print them in output.
- The user once screenshotted a **live Kaggle API token**. It was redacted and they were told to revoke it. Never reproduce it.
- **Never enter credentials into any login form.** This previously blocked reading Edge Impulse directly; the workaround is to ask the user for screenshots.
## A9. Competitive position — researched 30 Oct 2026

Table 6 of the concept note is a named-device comparison. Every price and clearance was verified against a source on 30 October 2026; where a source could not be found, the table says so rather than estimating.

**The four findings that carry the argument:**

1. **No vendor reviewed documents same-site longitudinal comparison.** Not Eko, not Littmann, not Thinklabs, not HD Steth, not StethoMe. Eko comes closest — it records position metadata and patient profiles — but publishes no feature for comparing a new recording against an earlier one from the same site. State this as "not documented by any vendor reviewed", never as "does not exist".
2. **Eko's AI is not sold in the Philippines.** It is delivered through the Eko+ subscription, and Eko publishes the supported-country list: US, Canada, 20 European countries, Australia, New Zealand. No ASEAN member appears. A Philippine facility can import the hardware and get amplified listening, but cannot license the analysis.
3. **Eko stores all cloud recordings in the United States.** Relevant to any Data Privacy Act discussion.
4. **Guided placement exists only as a paid four-point cardiac exam.** No reviewed device guides a non-expert through a lung field sequence.

**The finding that cuts against Resondi — do not hide it.** The **Eko CORE 300** launched on **22 October 2026** at **USD 199–249** (FDA K261694, cleared 23 Jul 2026), the first cleared murmur-AI device priced near Resondi's ₱8,000. It detects one cardiac finding, has no lung AI, no guided lung placement, no longitudinal comparison, and its analysis is unavailable in the Philippines — so Resondi's position holds. But **price alone is no longer a defensible differentiator**, and the concept note now says so explicitly. Expect a judge to raise it.

**Verified reference prices (USD list, Oct 2026):** Eko CORE 500 $449 · Eko CORE 300 $199–249 · 3M Littmann CORE $379 · Thinklabs One $499 (no AI at all) · HD Steth $499 bundle (2021 price, current availability unverified) · Littmann Classic III ~$100 street · basic acoustic ~$15–26.

**Philippine benchmark:** DOST-PCHRD reports electronic stethoscopes in the Philippines cost **at least ₱30,000–₱40,000**, in its write-up of **E-Steth** (UP College of Medicine, DOST-PCHRD funded) — a local acoustic-electronic stethoscope with no AI, at technology readiness level 5, not commercialised. It is the closest Philippine precedent and is cited as evidence of recognised domestic need, not as a competitor.

**Flagged source problems, carried into the concept note's hedging:** CORE 300 price differs between Eko's store ($249) and the launch announcement ($199); Eko DUO is discontinued at retail but still listed as app-compatible; Thinklabs' regulatory page was last modified March 2021 and gives no K number; HD Steth's marketing claims AI cardiac evaluation while its 510(k) states the device "is not intended to be used as a diagnostic device"; Littmann CORE amplification is given as both 40x and 140x on the same page. **No PH distributor or peso price was found for any imported device.**

# PART B — FILES, BUILD COMMANDS, AND OPEN WORK

## B1. Deliverables and how to rebuild them

Everything is generated from source. **Never hand-edit a `.docx` — edit the builder and rebuild.**

| Deliverable | Builder | Rebuild | State |
|---|---|---|---|
| `Resondi-Concept-Note-FINAL.docx` | `cn2/build.js` (Node, `docx` lib) | `cd cn2 && node build.js` | **45 pp, 12 figures, 13 tables, 0 placeholders. Submittable.** Two landscape pages: Figure 8 (canvas) and Table 6 (device comparison). |
| `script6/Resondi-Pitch-Script.docx` | `script6/build_script.py` from `script5/revised_long.txt` | `cd script6 && python build_script.py` | 1,177 spoken words, **7:50** at 150 wpm |
| `qa/Resondi-Judge-QA.docx` | `qa/build_qa.py` + `qa/part5.py` | `cd qa && python build_qa.py` | **111 questions, 34 flagged DECIDE** |
| `imrad/Resondi-IMRaD-Lung-Only.docx` | `imrad/build_imrad.py` | `cd imrad && python build_imrad.py` | 6,852 words, **16 TO FILL markers**, 3 tables |
| `stats/Resondi-Model-Statistics-Summary.docx` | built inline (script not retained) | — | 3 pp, the leakage explanation |
| `stats/Resondi-jamovi-Statistics-Guide.docx` | built inline (script not retained) | — | 8 pp |
| `accept/Resondi-Acceptance-Survey-jamovi-Guide.docx` | `accept/build_guide.py` | `cd accept && python build_guide.py` | 8 pp, click-by-click |
| `finpack/Resondi-Financial-Revision-Pack.docx` | `finpack/build_pack.py` | `cd finpack && python build_pack.py` | 17 pp paste-ready |
| `cue/Resondi-Spoken-Answers.docx` | `cue/` scripts | — | 14 spoken answers |

**Figures:**

| Script | Produces |
|---|---|
| `finpack/model.py` | **Single source of truth for every money figure.** Import it; never retype a number. |
| `deckfigs/build.py` | Figures 8 (business model canvas, **monotone**), 11, 12. Playwright → HTML → PNG. |
| `fig/fig1.py`, `fig/fig2.py`, `fig/diagrams.py` | Figures 7, 9, A, B, D — rose palette since 28 Oct |
| `fig/fig9_org.py` | Figure 10, org chart — founders marked, Advisory Board |
| `imradfig/results.py` | IMRaD result figures; response-time figure uses Table 5 values with SDs |
| `slides/*.py` + `slides/capture.py` | Pitch slides, 3840×2160 PNG |
| `newdata/rebuild_dataset.py` | **The leakage fix.** Patient-disjoint ICBHI rebuild. |
| `newdata/analyse_acceptance.py` | UTAUT analysis of the survey CSV |

**Build environment:** Node with `docx`; Python with `python-docx`, `python-pptx`, `matplotlib`, `playwright` (Chromium preinstalled), `scipy`, `soundfile`, `pypdf`, `Pillow`. LibreOffice (`soffice --headless --convert-to pdf`) for render checks. **Do not run project builds with `python -I`** — isolated mode drops the script directory from `sys.path` and local imports like `part5` fail.

## B2. The leakage fix script

`newdata/rebuild_dataset.py`. Tested against a synthetic ICBHI fixture (12 patients, mixed 4/10/44.1 kHz). Usage:

```bash
pip install --break-system-packages numpy scipy soundfile
python rebuild_dataset.py /path/to/icbhi
```

Order of operations, which *is* the fix:

1. Collect the 126 patient IDs from filenames — **before opening any audio**
2. Partition patients into disjoint train/test (prefers `ICBHI_challenge_train_test.txt` if present, so results are comparable to published work)
3. *Then* cut one 5-second clip per annotated respiratory cycle, inside each partition, **no overlap**
4. Label each clip from its own crackle/wheeze flags in the `.txt` sidecar
5. Assert zero patients cross the split; refuse to finish if any do

Outputs `resondi_dataset/{training,testing}/{Healthy,Crackle,Wheeze,Both}/*.wav` plus `manifest.csv` carrying the patient ID per sample. A 70/30 patient split gives 88/38 patients, 604/316 recordings, 4,305/2,593 cycles.

**Useful asset:** `newdata/dataset920.csv` — the user's own derived index of all 920 ICBHI recordings with columns `recording, patient, zone, equipment, total_cycles, crackle_cycles, wheeze_cycles, both_cycles, abnormal_cycles, abnormal_sound_percent, sound_category`. The `patient` column is the grouping variable. This lets you plan and verify the split **without touching any audio**.

## B3. What changed between 27 and 30 October

1. **Leakage diagnosed and the fix written** (A6). The concept note now discloses the mechanism in full, in plain language, without the word "leakage".
2. **Acceptance survey rewritten around UTAUT**, 30 → **27 respondents**, across concept note, script, Q&A, slides and IMRaD (A7).
3. **McNemar removed from the IMRaD**, which still reported p = 1.000 while the concept note said no such test was used. Three *correct* McNemar references were deliberately kept: comparing successive model versions on a fixed test partition is its proper use. The IMRaD Discussion now explains the distinction.
4. **Table 5 confirmed authoritative** for response times; Figure 4.4 of the paper contradicts it and is wrong.
5. **Clarity denominator removed rather than invented.** The sentence now reports proportions without a count.
6. **All figures converted to the rose palette**; canvas and tables deliberately monotone; canvas type enlarged from ~6.5 pt to **~8.8 pt** at print size by shortening block text and dropping the in-figure title bar.
7. **Workflow figure fixed:** step 4 said "CNN fusion" (planned, not built) → now "MFCC · CNN".
8. **Compliance review applied** (B4).
9. **New BOM**: prototype parts ₱2,094.47 → **₱2,735.00**.
10. **Table 6 added** — named device comparison against Eko, Littmann, Thinklabs, HD Steth, StethoMe and E-Steth (A9). Tables 6–12 renumbered to 7–13; all 13 captions and prose references verified consistent.

## B4. The PSC XI compliance review — what was applied and what was rejected

An external review (`Ausculta_PSC_XI_Compliance_Review.docx`, 27 Oct) was written against the **older Ausculta** materials. Much of it was already fixed. Disposition:

**Applied to the concept note (30 Oct):**
- Ten proponents → three founders + seven contributing members (A3)
- "Board of Regents" → "Advisory Board"
- Prototype cost → ₱2,735.00
- Built-vs-planned contradiction resolved: the note had said quality assessment was *not* an existing feature while elsewhere correctly saying it *is* implemented but slow. Now states precisely what exists (guided acquisition, organization, quality assessment, lung classification) versus what ₱38,000 builds (longitudinal views, practitioner dashboard, rehabilitation support) and that cardiac classification is in development.
- Target market restructured: buying segments in sales order (RHUs → schools → private clinics), patients moved to **indirect beneficiaries, explicitly not purchasers**, home self-recording removed.

**Already fixed before the review arrived:** figure/table numbering drift, the garbled "Figure 89ssable" text, the duplicated §IX paragraph, McNemar in the concept note, the "4× stronger" dB claim.

**Rejected — the review is wrong or works from stale numbers:**

| Review says | Why rejected |
|---|---|
| Signal gap is "+24.6 dB, about 17×" | Built on the old wrong figures (32.49 vs 7.89). Real: **45 vs 32 dB = 13 dB ≈ 4.5×**. |
| "chance is about 33%, 3 lung classes" | There are **four** classes. Chance is **25%**. |
| Ask is ₱300,000; AI ₱64K; validation ₱51K | Superseded. **₱500,000**, AI ₱102K, clinical validation ₱120K. |
| PSA 133,373 / 46,718 | Superseded by **134,074 / 47,260**. |

**Not actioned — belongs to the user:** get the full PSC XI guidelines from DICT MIMAROPA; confirm the team-size rule; clean logo on transparent background plus a one-colour version and 32 px app icon; rehearse the pitch.

## B5. The pitch deck needs a correction pass — NOT YET DONE

`Ausculta-Pitch-Deck-PSC-XI-Revised-Annotated.pptx` is a well-structured 17-slide rebuild with revision notes in the speaker notes. **It is out of sync with the verified concept note.** Before it is used:

| Slide | Problem | Correct value |
|---|---|---|
| all | Named "Ausculta" throughout | **Resondi** |
| 3 | 133,373 / 46,718 | **134,074 / 47,260** |
| 8, 17 | "8 chest sites + trachea" / "9 sites" | **Seven sites** (6 lung fields + trachea). Nine is *planned*. |
| 10 | "+24.6 dB (32.49 vs 7.89 dB)" | **45 dB vs 32 dB, 13 dB ≈ 4.5× amplitude** |
| 11 | "about 33% by chance", "3 classes" | **25%, four classes.** Also add the leakage disclosure, not just domain shift. |
| 14 | "seed recovered by month 31", "157,900" | **Commercial month 21 = month 35 from funding**; Y1 cash **₱175,900** |
| 15 | "₱300,000 and three partners" | **₱500,000** |
| — | No acceptance result | **3.95/5 across 27 respondents** |

Also, per the review's own notes: delete the yellow "WHAT CHANGED" annotation from every slide, export a flat PDF with no build steps, and keep it under 10 MB.

## B6. Open work, in priority order

### 1. Re-split and retrain — the only item that changes a number a judge will ask about
Run `rebuild_dataset.py`, upload with explicit categories, retrain. Expect 45–60%. Then update: concept note §VIII model paragraph, `stats/Resondi-Model-Statistics-Summary.docx`, IMRaD results, slide 11, and the `DISPLAY` dict if class names change.

### 2. Correct the 83-page paper (`RIM-FULLPAPER-2026-9_1.pdf`)
User's document — provide pasteable text, do not edit. Needs: McNemar removed; the three paired t-tests removed; signal 32.49/7.89 → 45/32; ambient noise → 24/35/42; **Figure 4.4 corrected to match Table 5**; six locations → seven; the Data Analysis section reworded (it describes a device comparison, not a classifier test); the leakage disclosure added; and Section G ("End-User Preference Evaluation") either reported or deleted — it has no results anywhere.

### 3. Fix the pitch deck (B5)

### 4. The 16 IMRaD TO FILL markers
Genuine unknowns. The load-bearing ones: **#2** microphone part (documentation cites both INMP441 and MAX4466); **#5** the rule layer operates on four zones while recording uses seven sites — state the mapping; **#7** signal measurement unit, reference level, comparator stethoscope make and model; **#8** how many professionals rated clarity and whether inter-rater agreement was assessed; **#9** whether the pulmonologists were blinded; **#10** sampling method for the 27 respondents; **#12** ethics approval versus physician supervision; **#13** whether the 3 hospital patients overlap the 13 self-identified patients in the survey.

### 5. Smaller, still open
- **Clarity denominator** — 68/25/7 of how many? Not in the paper. 170 values between 28 and 300 fit after rounding, so it cannot be derived.
- **Confirm the live Google Sheet** still has 27 rows, not more.
- **IP ownership** is written as "to be formalized with the school" — unresolved commitment.
- **Base44 app meta tags** still say `ausculta.base44.app`.
- **Hypothesis 2** (`Hypothesis_2_design_and_analysis.md`) is designed but never run: 20 paired reference-vs-device playback recordings. **McNemar is correct for this design.** Run it *after* the re-split, or §8.3 of that document applies — a near-chance classifier in both conditions produces no detectable difference for reasons unrelated to hardware.
- **A third agreement study** exists as an empty template (`agreement_analysis_TEMPLATE.csv`, 30 rows, six interpretation-layer categories: Healthy / Possible asthma / Possible bronchiolitis / Possible pneumonia or pulmonary edema / Possible severe bronchiolitis / Further evaluation needed). Never run.

## B7. The jamovi analyses that are circular — fix before reporting

The user's jamovi output compares `abnormal_sound_percent` across the four sound categories (Kruskal-Wallis χ² = 633, p < .001). **Healthy recordings have a value of 0.0 with SD 0.00 by definition** — a recording is *called* Healthy when it has no abnormal cycles. Three of the six pairwise comparisons are tautological.

Rerun without Healthy and the finding survives: **H = 32.53, df = 2, p < .001**, all three pairwise comparisons surviving Bonferroni correction. Wheezing with Crackles (84.7%) > Crackles alone (70.6%) > Wheezing alone (64.7%). Report that, and say in one line why Healthy was excluded.

## B8. Where the source material lives

| File | What it is |
|---|---|
| `RIM-FULLPAPER-2026-9_1.pdf` | The 83-page research paper. Figure 4.5 p.12 is the source of 68/25/7; Table 5 pp.13–14 is the authoritative response-time table. |
| `ausculta_dataset_FULL_920.csv` | The 920-recording ICBHI index with the `patient` column |
| `Ausculta_Survey_Questionnaire__Responses_` | The acceptance survey export (contains PII) |
| `Resondi_Bill_of_Materials.docx` | New BOM, ₱2,735.00 |
| `Ausculta_PSC_XI_Compliance_Review.docx` | The external review (B4) |
| `Ausculta_Respiratory_Rules_Evidence_Citations.pdf` | The rule layer with citations — this is the Figure 7 evidence base, keep it |
| `Hypothesis_2_design_and_analysis.md` | Paired playback study design, not yet run |
| `RESONDI-HANDOFF.md` (27 Oct) | Turn-by-turn history of the original conversation. Provenance only — **its Part A numbers are superseded by this file.** |
