"""Paired comparison of the cross-validation results (12 Nov): FDC-FS + SPRSound (3-seed ensemble) vs MFCC ICBHI-only.

Both models predict the same 6,898 ICBHI cycles (every patient once, out of fold). The difference in balanced
accuracy is bootstrapped over patients (same resampled patients for both models), giving a 95% CI and a one-sided
p-value for "the new model is not better".

    python scripts/cv_paired.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv


def pooled(name, seeds, y, cyc):
    P = np.zeros((len(y), 4))
    for k in range(cv.K):
        ds = [np.load(os.path.join(cv.CV_DIR, f"{name}_s{s}_f{k}.npz")) for s in seeds]
        P[ds[0]["test_idx"]] = np.mean([d["P"] for d in ds], 0)
    return cv.cycle_level(P, y, cyc)


y, cyc, pat = cv.icbhi_all()
ids, yt, yp_new = pooled("fdc3_sprs", (11, 22, 33), y, cyc)
ids2, yt2, yp_old = pooled("mfcc_icbhi", (11,), y, cyc)
assert (ids == ids2).all() and (yt == yt2).all()
cp = dict(zip(cyc, pat))
pc = np.array([cp[i] for i in ids])
pats = np.unique(pc)
rows = {p: np.where(pc == p)[0] for p in pats}
rng = np.random.default_rng(20261112)
diff = []
for _ in range(5000):
    m = np.concatenate([rows[p] for p in rng.choice(pats, len(pats))])
    diff.append(cv.bal(yt[m], yp_new[m]) - cv.bal(yt[m], yp_old[m]))
diff = np.array(diff)
d0 = cv.bal(yt, yp_new) - cv.bal(yt, yp_old)
per_pat_better = np.mean([np.mean(yp_new[r] == yt[r]) > np.mean(yp_old[r] == yt[r]) for r in rows.values()])
print(f"patients {len(pats)}, cycles {len(ids)}")
print(f"balanced accuracy: FDC-FS+SPRSound ensemble {cv.bal(yt, yp_new):.3f}  vs  MFCC ICBHI-only {cv.bal(yt, yp_old):.3f}")
print(f"difference {d0 * 100:+.1f} points, 95% CI {np.percentile(diff, 2.5) * 100:+.1f} to {np.percentile(diff, 97.5) * 100:+.1f}, "
      f"one-sided p (difference <= 0) = {np.mean(diff <= 0):.4f}")
print(f"patients where the new model gets more of their cycles right: {per_pat_better * 100:.0f}%")
