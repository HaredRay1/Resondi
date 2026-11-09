# HYPOTHESIS 2 — DESIGN AND ANALYSIS (REVISED)

**Ho:** There is no significant difference between the classification results
obtained from the reference dataset recordings and those obtained from Ausculta
device recordings.

**Ha:** There is a significant difference between the classification results
obtained from the reference dataset recordings and those obtained from Ausculta
device recordings.

---

## 1. Design: paired acoustic playback

Each reference recording is played through a speaker and re-captured with the
Ausculta chestpiece. Every sound therefore exists in two versions — the original
digital file and the device capture — and the only difference between them is
the acquisition path. This gives a **paired** design, which is more powerful at
small sample sizes than comparing independent groups and removes patient
variability as a confounder.

## 2. Sample

Twenty recordings, five per respiratory-sound category (Healthy, Crackles,
Wheezing, Wheezing with Crackles), each from a different patient. The selection
is in `hypothesis2_DOWNLOAD_LIST.csv`. Twenty pairs meets the practical minimum
for the tests below; the comparison should still be described as a pilot.

## 3. Measured variable: why the predicted class, not the percentage

Repeated classification of the same recording in the Ausculta application
produces **stable predicted classes but varying confidence percentages**. The
top-ranked sound pattern is reproducible across runs, while the numeric
percentages shift between runs on identical input.

This is consistent with the application analysing a different portion of the
recording on each run: a recording contains both quiet and active passages, so
scores depend on which segment is sampled, while the dominant pattern remains
dominant regardless.

The consequence for this hypothesis is direct. A test performed on the
percentages would partly measure run-to-run variability of the application
rather than the difference between acquisition paths. The **predicted class is
therefore the primary measured variable**, and the confidence percentages are
recorded for description only.

## 4. Playback procedure

Hold everything constant except the acquisition path:

1. Quiet room; fans and air conditioning off.
2. Fixed speaker volume, set once and never adjusted.
3. Fixed distance and orientation between chestpiece and speaker; mark
   positions with tape.
4. Play each recording in full; capture for the duration used in your protocol.
5. Name each capture to map to its source, e.g. `dev_120_1b1_Pl`.
6. Log the setup for the methodology: speaker model, volume setting, distance,
   room, coupling material.

Complete all 20 reference classifications first, then all 20 device
classifications, rather than alternating.

## 5. Data collection

Use `hypothesis2_data_collection_sheet.csv`, pre-filled with `pair_no`,
`source_recording`, and `true_category`.

| Column | How to obtain |
|---|---|
| `ref_predicted` | Highest-ranked class when classifying the original .wav |
| `ref_top_pct` | That class's displayed percentage (descriptive only) |
| `dev_predicted` | Highest-ranked class when classifying the device capture |
| `dev_top_pct` | That class's displayed percentage (descriptive only) |
| `ref_correct` | 1 if `ref_predicted` = `true_category`, else 0 |
| `dev_correct` | 1 if `dev_predicted` = `true_category`, else 0 |
| `notes` | Anything unusual during the trial |

The application's classification breakdown already uses the four
respiratory-sound categories, so no label mapping is required.

## 6. Statistical tests

### Test A (PRIMARY) — McNemar's test on classification correctness

Whether the proportion of correct classifications differs between acquisition
paths. Uses the predicted class, which is reproducible.

- jamovi: **Analyses → Frequencies → Paired Samples (McNemar test)**
- Rows: `ref_correct`. Columns: `dev_correct`
- Report: χ²(1) = __, p = __, and both accuracy percentages
- With 20 pairs, expect small discordant cell counts; report the exact
  (binomial) p-value if jamovi provides it

### Test B (SECONDARY) — Agreement between acquisition paths

How often both versions produce the same predicted class, regardless of
correctness. This measures whether the device alters the classification outcome
at all.

- jamovi: **Analyses → Frequencies → Independent Samples (χ² test of
  association)**; Rows `ref_predicted`, Columns `dev_predicted`; tick
  **Cohen's κ**
- Report: percentage agreement and κ
- κ bands: <0.20 slight; 0.21–0.40 fair; 0.41–0.60 moderate; 0.61–0.80
  substantial; >0.80 almost perfect

### Test C (SUPPLEMENTARY) — Test-retest reliability of the percentages

Documents the variability observed in Section 3.

- Procedure: classify one recording five times without changing anything;
  record the predicted class and top percentage each run in
  `hypothesis2_testretest_sheet.csv`
- Report the range of percentages and whether the predicted class was identical
  across runs
- This justifies the choice of measured variable and is a finding in its own
  right

**Not used:** a paired t-test on the confidence percentages, because those
values are not stable on repeated classification of identical input.

## 7. Reporting

**If p ≥ .05 on McNemar:**
> No statistically significant difference was found between the classification
> results obtained from the reference recordings and those obtained from
> Ausculta device recordings, χ²(1) = __, p = __. Reference recordings were
> classified correctly in __ of 20 cases (__%) and device recordings in __ of
> 20 cases (__%). Under the tested conditions, the acquisition path did not
> produce a detectable change in classification correctness.

**If p < .05 on McNemar:**
> A statistically significant difference was found between the classification
> results obtained from the reference recordings and those obtained from
> Ausculta device recordings, χ²(1) = __, p = __. Reference recordings were
> classified correctly in __ of 20 cases (__%) compared with __ of 20 cases
> (__%) for device recordings, indicating that the acquisition characteristics
> of the prototype measurably affected classification correctness.

**Test-retest sentence:**
> Repeated classification of a single recording produced top-class percentages
> ranging from __% to __% across five runs, while the predicted class was
> identical in all runs. Classification percentages were therefore treated as
> descriptive values and the predicted class was used as the measured variable
> for hypothesis testing.

## 8. Threats to validity

**8.1 Percentage instability.** Addressed by using the predicted class as the
measured variable and documenting the variability in Test C. State this in the
methodology rather than leaving it for a reader to discover.

**8.2 A non-significant result is not evidence of equivalence.** Failing to
reject Ho means no difference was detected, not that none exists — especially at
n = 20. Do not write that the device "performs the same as" the reference
recordings.

**8.3 Baseline performance bounds what the test can show.** If classification
accuracy is near chance in both conditions, the two sets of outputs will not
differ significantly for reasons unrelated to the hardware. Report the
reference-condition accuracy alongside the test result so the reader can judge
whether the comparison was informative.

**8.4 Playback is not auscultation.** A speaker does not reproduce chest-wall
transmission, skin contact, or ambient point-of-care conditions. Describe the
procedure as a controlled comparison of the acquisition path, not as clinical
validation.

**8.5 The narrative interpretation is out of scope.** The application's
generated summary and qualitative severity descriptor are produced by a language
model and are not deterministic measurements. They are not used as variables in
this analysis.

## 9. What to report in Chapter 4

- Table of the 20 pairs: predicted classes, percentages, correctness
- Test A (McNemar) with both accuracy percentages
- Test B (agreement and κ)
- Test C (test-retest range)
- The decision on Ho, with Section 8 caveats carried into the limitations
