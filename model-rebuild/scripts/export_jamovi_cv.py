"""Export the 5-fold cross-validation predictions (12 Nov) as jamovi-ready CSV files (13 Nov).

Writes to results/stats/:
  jamovi_cv_cycles.csv : one row per ICBHI breathing cycle (6,898): patient, fold, stethoscope-free label,
                         the MFCC model's prediction and the FDC-FS + SPRSound ensemble's prediction.
  jamovi_cv_folds.csv  : one row per fold: balanced accuracy of each model (for the paired comparison).
  jamovi_cv_patients.csv : one row per patient: share of their cycles each model got right.

    python scripts/export_jamovi_cv.py
"""
import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv

OUT = os.path.join(cv.ROOT, "results", "stats")
NAMES = ["Crackles", "Healthy", "Wheezing", "Wheezing with Crackles"]
assert list(cv.LABELS) == NAMES, cv.LABELS

y, cyc, pat = cv.icbhi_all()
fold_of_window = np.full(len(y), -1)
P = {"mfcc": np.zeros((len(y), 4)), "fusion": np.zeros((len(y), 4))}
for k in range(cv.K):
    d = np.load(os.path.join(cv.CV_DIR, f"mfcc_icbhi_s11_f{k}.npz"))
    P["mfcc"][d["test_idx"]] = d["P"]
    fold_of_window[d["test_idx"]] = k
    ds = [np.load(os.path.join(cv.CV_DIR, f"fdc3_sprs_s{s}_f{k}.npz")) for s in (11, 22, 33)]
    assert all((x["test_idx"] == d["test_idx"]).all() for x in ds)
    P["fusion"][d["test_idx"]] = np.mean([x["P"] for x in ds], 0)
assert (fold_of_window >= 0).all()

ids, yt, yp_m = cv.cycle_level(P["mfcc"], y, cyc)
ids2, yt2, yp_f = cv.cycle_level(P["fusion"], y, cyc)
assert (ids == ids2).all()
cyc_pat = dict(zip(cyc, pat))
cyc_fold = dict(zip(cyc, fold_of_window))

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "jamovi_cv_cycles.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["cycle", "patient", "fold", "true_label", "pred_mfcc", "correct_mfcc", "pred_fusion", "correct_fusion"])
    for n, (i, t, a, b) in enumerate(zip(ids, yt, yp_m, yp_f), 1):
        w.writerow([n, str(cyc_pat[i]), int(cyc_fold[i]) + 1, NAMES[t], NAMES[a], int(a == t), NAMES[b], int(b == t)])

with open(os.path.join(OUT, "jamovi_cv_folds.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["fold", "balacc_mfcc", "balacc_fusion"])
    folds = np.array([cyc_fold[i] for i in ids])
    for k in range(cv.K):
        m = folds == k
        w.writerow([k + 1, round(cv.bal(yt[m], yp_m[m]) * 100, 2), round(cv.bal(yt[m], yp_f[m]) * 100, 2)])

with open(os.path.join(OUT, "jamovi_cv_patients.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["patient", "cycles", "pct_correct_mfcc", "pct_correct_fusion"])
    pats = np.array([cyc_pat[i] for i in ids])
    for p in np.unique(pats):
        m = pats == p
        w.writerow([str(p), int(m.sum()), round(np.mean(yp_m[m] == yt[m]) * 100, 2), round(np.mean(yp_f[m] == yt[m]) * 100, 2)])

print(f"cycles {len(ids)}  patients {len(np.unique(pat))}")
print(f"balanced accuracy  MFCC {cv.bal(yt, yp_m):.3f}  fusion ensemble {cv.bal(yt, yp_f):.3f}")
