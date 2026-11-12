# Reproducing the statistics in jamovi

The numbers in the research plan's Results were computed in Python (`scripts/analysis_stats.py`; NumPy and SciPy) from the model chosen and tested on 11 November. The CSV files in this folder let you reproduce each analysis in jamovi. Menu names are those of jamovi 2.x.

| File | One row per | Used for |
|---|---|---|
| `jamovi_test_cycles.csv` | test breathing cycle (1,051 rows, 31 patients) | classification metrics, McNemar |
| `jamovi_recordings_severity.csv` | recording (158 validation, 164 test) | severity calibration, RMSE/MAE/R², Kruskal–Wallis |
| `jamovi_validation_models.csv` | training run (recipe × seed) | model comparison on validation |
| `jamovi_cv_cycles.csv`, `jamovi_cv_folds.csv`, `jamovi_cv_patients.csv` | cycle / fold / patient of the 5-fold cross-validation | IMRaD Table 3, Figures 12–14 (section 11) |
| `jamovi_fusion_cycles.csv` | test breathing cycle (1,051 rows, 31 patients); one `pred_` and one `correct_` column per model | fusion vs individual models (Tables 14–15) |

## 1. Confusion matrix (Table 9 and Figure 7)
Open `jamovi_test_cycles.csv`, then go to **Frequencies → Independent Samples (Contingency Tables)**.
- Rows: `true_label`.
- Columns: `predicted_label`.
- Cells: tick *Row %*.

Per-class recall is the row percentage on the diagonal. Balanced accuracy is the average of the four diagonal row percentages. Expected: 73.1, 30.3, 10.8 and 25.9%, so balanced accuracy is **35.0%**.

Cohen's kappa is not in jamovi's core menus. Either install an agreement module from the jamovi library (search "kappa"), or report the Python value (κ = 0.146).

## 2. Clean vs noise-contaminated: McNemar (Hypothesis 1, Table 11)
Go to **Frequencies → Paired Samples (McNemar test)**.
- Rows: `correct_clean`.
- Columns: `correct_snr20`.

Repeat with `correct_snr10` and `correct_snr5`. The discordant cells are b (right when clean, wrong when noisy) and c (the reverse).
- **20 dB:** b = 183, c = 75.
- **10 dB:** b = 205, c = 69.
- **5 dB:** b = 209, c = 72.

Every one gives p < .001. jamovi reports the χ² version; the plan's exact binomial p-values are in `stats-results.json`.

## 3. Severity calibration: OLS on validation recordings (Table 12)
Open `jamovi_recordings_severity.csv`, then go to **Data → Filters**.
- Filter: `subset == "validation"` (158 recordings).

Then go to **Regression → Linear Regression**.
- Dependent: `ref_severity`.
- Covariates: `mean_p_Wheezing`, `mean_p_Crackles`, `mean_p_WheezingCrackles`.
- Assumption checks: tick *Collinearity statistics* (VIF).

Expected: intercept −281.8; coefficients 570.4 (W), 419.0 (C), 364.8 (WC); R² = 0.154; VIF 13.3, 13.0, 1.3.

## 4. Severity accuracy on test recordings: RMSE, MAE, R²
Change the filter to `subset == "test"` (164 recordings). Then go to **Data → Compute** and make two new variables:
- `err2 = (pred_calibrated - ref_severity)^2`
- `abserr = ABS(pred_calibrated - ref_severity)`

Then use **Exploration → Descriptives** to get their means.
- RMSE = √mean(err2) = **43.4**.
- MAE = mean(abserr) = **39.7**.

For the uncalibrated estimator, repeat with `pred_direct`: RMSE 48.8, MAE 41.1.

## 5. Kruskal–Wallis (Table 13)
Keep the `subset == "test"` filter, then go to **ANOVA → One-Way ANOVA (Non-parametric)** (Kruskal–Wallis).
- Dependent: `pred_calibrated`.
- Grouping: `category`.
- Tick *Effect size* (ε²) and *DSCF pairwise comparisons*.

Expected: H(3) = 8.12, p = .044, ε² = 0.050. Only Crackles vs Wheezing with Crackles is significant (p = .029).

## 6. Field agreement, 6 of 15
Make a 15-row variable with 6 "match" and 9 "no match". Then go to **Frequencies → 2 Outcomes (Binomial test)**.
- Test value 0.25, hypothesis *> test value*, tick *Confidence intervals*.

Expected: p = .148. jamovi's interval is Clopper–Pearson; the plan reports Wilson's (19.8–64.3%).

## 7. Validation comparison (Table 8 and Figure 6)
Open `jamovi_validation_models.csv`, then go to **Exploration → Descriptives**.
- Variable: `val_balanced_accuracy`.
- Split by: `recipe`.
- Tick mean and SD.

These are validation scores, used only to choose a model. Do not test them against each other: three seeds per recipe is too few, and repeated testing on validation inflates false positives.

## 8. Fusion vs individual models: per-class recall and balanced accuracy (Tables 14–15)
Open `jamovi_fusion_cycles.csv`, then go to **Frequencies → Independent Samples (Contingency Tables)**.
- Rows: `true_label`.
- Columns: one model's `pred_` column, e.g. `pred_late3`.
- Cells: tick *Row %*.

Repeat for each model. The diagonal row percentages are the per-class recalls (Crackles, Healthy, Wheezing, Wheezing with Crackles), and balanced accuracy is their average. Expected:

| Model | Column | Recall C / H / W / W+C (%) | Balanced accuracy |
|---|---|---|---|
| Deployed design (retrained 11 Nov) | `pred_deployed_mfcc` | 73.1 / 30.3 / 10.8 / 25.9 | 35.0% |
| MFCC alone | `pred_single_mfcc` | 75.0 / 28.8 / 25.0 / 15.7 | 36.1% |
| Spectrogram alone | `pred_single_spec` | 42.9 / 46.8 / 12.5 / 4.6 | 26.7% |
| Chromagram alone | `pred_single_chroma` | 78.0 / 23.2 / 28.3 / 38.9 | 42.1% |
| Two-branch fusion | `pred_fdc2_nochroma` | 65.3 / 45.2 / 20.8 / 6.5 | 34.5% |
| Three-branch fusion | `pred_fdc3` | 56.0 / 57.3 / 24.2 / 9.3 | 36.7% |
| **Late fusion (primary)** | `pred_late3` | 59.7 / 47.2 / 20.8 / 3.7 | **32.9%** |

## 9. Fusion vs individual models: McNemar (Table 14, last column)
Go to **Frequencies → Paired Samples (McNemar test)**.
- Rows: `correct_late3`.
- Columns: the other model's `correct_` column, e.g. `correct_single_mfcc`.

Repeat for each of the five other study models. In the table, b = late fusion right and the other model wrong; c = the reverse. Expected b / c:

| Comparison | b | c |
|---|---|---|
| Late fusion vs MFCC alone | 183 | 140 |
| Late fusion vs spectrogram alone | 112 | 56 |
| Late fusion vs chromagram alone | 187 | 150 |
| Late fusion vs two-branch fusion | 91 | 98 |
| Late fusion vs three-branch fusion | 59 | 115 |
| Late fusion vs deployed design (not in the Holm family) | 182 | 136 |

jamovi gives the χ² version and no correction. The plan reports exact binomial p-values with **Holm correction across the five study comparisons** (from `fusion-comparison.json`). To apply Holm by hand:
1. Sort the five p-values from smallest to largest.
2. Multiply the k-th smallest by (6 − k).
3. Keep each adjusted value at least as large as the one before it, capped at 1.

Expected Holm-adjusted p: spectrogram < .001, three-branch < .001, MFCC .058, chromagram .099, two-branch .663.

Note that b counts *cycles*, so these tests treat the 1,051 cycles as independent although they come from 31 patients. The patient-level bootstrap intervals in Table 14 (computed in Python) are the more conservative check.

## 10. SPRSound external check (Table 16)
The SPRSound predictions are summarised in `fusion-comparison.json` (`sets.sprs`). No jamovi file is exported for them; report the Python values.

## 11. Cross-validation, IMRaD Tables 3 and Figures 12–14 (added 13 Nov)
The IMRaD's jamovi figures were made by `build/imrad/jamovi_figures.R`, which runs jamovi's own engine (R package jmv 2.8). Every number below is what jamovi shows from its menus; the full output is in `build/imrad/jamovi-output.txt`.

**Fold comparison (Figure 12).** Open `jamovi_cv_folds.csv`, then go to **T-Tests → Paired Samples T-Test**.
- Pair: `balacc_mfcc` with `balacc_fusion`.
- Tick *Student's*, *Wilcoxon rank*, *Mean difference* with *Confidence interval*, *Effect size*, *Descriptives* and *Descriptives plots*.
- Expected: t(4) = −4.747, p = .009, mean difference −5.76 (95% CI −9.13 to −2.39), Cohen's d = −2.12; Wilcoxon W = 0, p = .062 (the smallest p possible with 5 pairs). Means 34.14 and 39.90.

**Patient comparison (Figure 13).** Open `jamovi_cv_patients.csv`, same analysis with `pct_correct_mfcc` and `pct_correct_fusion`.
- Expected: Wilcoxon W = 2092, p = .009 (18 tied pairs); Student's t(125) = −2.08, p = .040. Means 39.58% and 44.57%.

**Confusion matrices (Figure 14).** Open `jamovi_cv_cycles.csv`, then **Frequencies → Independent Samples**.
- Rows: `true_label`. Columns: `pred_mfcc` (then again with `pred_fusion`). Cells: *Row %*.
- Under **Plots**, tick *Bar plot*, Y-axis *Percentages within rows*, X-axis *Rows*, *Side by side*.
- Expected recall (diagonal row %): MFCC 50.4 / 32.9 / 31.2 / 21.7; fusion 55.8 / 40.1 / 38.0 / 25.9. Balanced accuracy is their mean: 34.0% and 40.0%.

**McNemar on the same cycles.** **Frequencies → Paired Samples (McNemar test)**.
- Rows: `correct_mfcc`. Columns: `correct_fusion`.
- Expected: 831 cycles right only for MFCC, 1,277 right only for fusion; χ² = 94.36, p < .001. This treats the 6,898 cycles as independent, so report the patient-level results above as the main ones.

**Field agreement of the original model.** **Frequencies → 2 Outcomes (Binomial test)** on a 15-row variable with 6 "Match" and 9 "No match".
- Test value 0.25, hypothesis *> test value*. Expected: p = .148. jamovi's interval is Clopper–Pearson; the paper reports Wilson's (19.8–64.3%).

**Not computable in jamovi:** the pooled balanced accuracy with patient-bootstrap CIs, and the paired patient bootstrap (+5.9 points, CI +1.0 to +10.3, p = 0.008). These come from `model-rebuild/scripts/cv.py` and `cv_paired.py`.

## Not computable here
- **Patient-level bootstrap 95% CIs** (1,000 resamples): computed in Python. jamovi has no patient-clustered bootstrap.
- **Beta regression** (sensitivity check): Python only. RMSE 42.8, R² 0.043.
- **Bootstrap CI for the difference between two models** (Table 14): Python only, resampling patients.
