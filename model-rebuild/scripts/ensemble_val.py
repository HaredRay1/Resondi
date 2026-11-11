"""Option A (12 Nov): does averaging the three saved FDC-FS seeds help? VALIDATION ONLY, no test patients read.

    python scripts/ensemble_val.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fusion as Fu
import test_saved as T

Fu.BANDLIMIT = True


def fmt(c):
    return (f"bal {c['balanced_accuracy']:.3f}  F1 {c['macro_f1']:.3f}  recall "
            + " ".join(f"{p['label'][:4]}={p['recall']:.2f}" for p in c["per_class"]))


for key, part, g in [("ICBHI val", "validation", 0), ("SPRS val", "sprs_validation", 1)]:
    raw = np.load(os.path.join(Fu.EXP, f"raw_{part}.npz"))
    sc = lambda p: Fu.score(p, raw["y"], raw["cycle"])["cycle"]
    P = {s: T.probs("fdc3", s, part, g) for s in (11, 22, 33)}
    L = {s: T.probs("late3", s, part, g) for s in (11, 22, 33)}
    for s in (11, 22, 33):
        print(f"{key:<10} fdc3 seed {s}            {fmt(sc(P[s]))}")
    print(f"{key:<10} fdc3 3-seed ensemble     {fmt(sc(np.mean(list(P.values()), 0)))}")
    print(f"{key:<10} fdc3+late3, all seeds    {fmt(sc(np.mean(list(P.values()) + list(L.values()), 0)))}")
