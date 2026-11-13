"""Leakage demonstration (13 Nov 2026): what the SAME fusion network scores when the split leaks.

This is NOT an accuracy estimate. It shows how much a leaky split inflates the number, which is why
the study splits by patient. The honest figure stays the patient-wise cross-validation (40.0% balanced,
results/cv-results.md).

Same recipe as the cross-validation's fdc3_sprs (MFCC + spectrogram + chromagram, ICBHI + rebalanced
SPRSound, band-limited, per-source normalisation, (source, class) weighting, seed 11, 30 epochs,
early stopping patience 8, cv.train_fold). Only the split changes:

  patients_shared : ICBHI breathing cycles assigned at random, 70% train / 10% validation / 20% test.
                    A test patient's other cycles are in training (patient leakage).
  windows_shared  : ICBHI 1 s windows assigned at random, 70 / 10 / 20. Windows of one breathing cycle,
                    which overlap by half a second in the training part, land on both sides
                    (the kind of split the original Edge Impulse model used).
  training_data   : the patients_shared model scored on its own training cycles (pure memory).

Comparator: patient-wise 5-fold cross-validation of the same recipe, seed 11 (results/cv-results.json).

    python scripts/leak_demo.py run      # trains the two leaky models (about 40 minutes on CPU)
    python scripts/leak_demo.py report   # -> results/leakage-demo.md / .json
"""
import json
import os
import sys
import time
from datetime import datetime

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv as CV
import fusion as Fu
from resondi_model import ROOT

OUT_DIR = os.path.join(Fu.EXP, "leak")
VIEWS = ["mfcc", "spec", "chroma"]
SEED = 11
SPLIT_SEED = 20261113


def assign(n, rng):
    u = rng.random(n)
    return np.where(u < 0.7, 0, np.where(u < 0.8, 1, 2))   # 0 train, 1 validation, 2 test


def run():
    import torch
    torch.set_num_threads(os.cpu_count() or 4)
    os.makedirs(OUT_DIR, exist_ok=True)
    Fu.BANDLIMIT, Fu.SRCNORM = True, True
    y, cyc, pat = CV.icbhi_all()
    F = CV.icbhi_feats(VIEWS)
    st = np.load(os.path.join(Fu.EXP, "raw_sprs_train.npz"))
    Fs_all = [Fu.feature(v, "sprs_train") for v in VIEWS]

    rng = np.random.default_rng(SPLIT_SEED)
    ucyc = np.unique(cyc)
    cyc_part = dict(zip(ucyc, assign(len(ucyc), rng)))
    splits = {
        "patients_shared": np.array([cyc_part[c] for c in cyc]),
        "windows_shared": assign(len(y), np.random.default_rng(SPLIT_SEED + 1)),
    }
    for name, part in splits.items():
        path = os.path.join(OUT_DIR, f"{name}.npz")
        if os.path.exists(path):
            print(f"{name}: done already", flush=True)
            continue
        t0 = time.time()
        tr, va, te = part == 0, part == 1, part == 2
        Ftr, ytr = [f[tr] for f in F], y[tr]
        keep = Fu.sprs_balanced_rows(st["y"], st["cycle"], int((ytr == Fu.HEALTHY).sum()))
        Ftr = [np.concatenate([a, b[keep]]) for a, b in zip(Ftr, Fs_all)]
        ytr = np.concatenate([ytr, st["y"][keep]])
        src = np.concatenate([np.zeros(int(tr.sum()), int), np.ones(len(keep), int)])
        model, prep, ep, vbest = CV.train_fold(Ftr, ytr, src, [f[va] for f in F], y[va], cyc[va], SEED, True)
        del Ftr
        out = {"part": part, "P_test": Fu.predict(model, prep, [f[te] for f in F], 0), "epoch": ep, "val": vbest}
        if name == "patients_shared":
            out["P_train"] = Fu.predict(model, prep, [f[tr] for f in F], 0)
        np.savez(os.path.join(OUT_DIR, f"{name}.npz"), **out)
        r = Fu.score(out["P_test"], y[te], cyc[te])["cycle"]
        print(f"{name:<16} epoch {ep:>2}  val {vbest:.3f}  TEST bal {r['balanced_accuracy']:.3f}  "
              f"acc {r['accuracy']:.3f}  {time.time() - t0:.0f}s", flush=True)
    print("all done", flush=True)


def summarise(P, yy, cc, pp, rng):
    ids, yt, yp = CV.cycle_level(P, yy, cc)
    cp = dict(zip(cc, pp))
    pc = np.array([cp[i] for i in ids])
    boots = []
    for _ in range(2000):
        m = rng.integers(0, len(ids), len(ids))
        boots.append(CV.bal(yt[m], yp[m]))
    return {"balanced": CV.bal(yt, yp), "ci95_cycle_bootstrap": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
            "accuracy": float(np.mean(yt == yp)), "cycles": int(len(ids)), "patients": int(len(np.unique(pc))),
            "recall": {CV.LABELS[c]: float(np.mean(yp[yt == c] == c)) for c in range(4)}}


def report():
    y, cyc, pat = CV.icbhi_all()
    rng = np.random.default_rng(SPLIT_SEED)
    res = {}
    for name in ("patients_shared", "windows_shared"):
        d = np.load(os.path.join(OUT_DIR, f"{name}.npz"))
        part = d["part"]
        te = part == 2
        res[name] = summarise(d["P_test"], y[te], cyc[te], pat[te], rng)
        res[name]["epoch"] = int(d["epoch"])
        if name == "patients_shared":
            tr = part == 0
            res["training_data"] = summarise(d["P_train"], y[tr], cyc[tr], pat[tr], rng)
            test_pats, train_pats = set(pat[te]), set(pat[tr])
            res[name]["test_patients_also_in_training"] = f"{len(test_pats & train_pats)} of {len(test_pats)}"
        if name == "windows_shared":
            te_c, tr_c = set(cyc[te]), set(cyc[part == 0])
            res[name]["test_cycles_with_windows_in_training"] = f"{len(te_c & tr_c)} of {len(te_c)}"
    cvr = json.load(open(os.path.join(ROOT, "results", "cv-results.json")))["results"]
    honest = cvr["fdc3_sprs seed 11"]
    res["patient_wise_cv_seed11"] = {"balanced": honest["pooled_balanced"], "ci95": honest["ci95"],
                                     "accuracy": honest["accuracy"], "recall": honest["recall"]}
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    json.dump({"evaluated": stamp, "results": res}, open(os.path.join(ROOT, "results", "leakage-demo.json"), "w"), indent=1)

    def row(label, r, ci_key):
        lo, hi = r[ci_key]
        return f"| {label} | {100 * r['balanced']:.1f}% ({100 * lo:.1f}–{100 * hi:.1f}) | {100 * r['accuracy']:.1f}% |"

    lines = [
        f"# Leakage demonstration: the same fusion network on leaky splits ({stamp})",
        "",
        "**This is not the model's accuracy.** It shows how far a leaky split inflates the score, and so why the "
        "study splits by patient. The model's accuracy on unseen patients is the first row.",
        "",
        "Same recipe in every row: FDC-FS fusion (MFCC + spectrogram + chromagram), ICBHI + rebalanced SPRSound, "
        "band-limited, per-source normalisation, seed 11, `cv.train_fold`. Only the split changes. "
        "Scored per breathing cycle on ICBHI. Chance is 25%.",
        "",
        "| Split | Balanced accuracy (95% CI) | Plain accuracy |",
        "|---|---|---|",
        row("**Patient-wise** (5-fold CV, 126 unseen patients): the honest figure", res["patient_wise_cv_seed11"], "ci95"),
        row("Patients shared: test patients' other cycles were in training", res["patients_shared"], "ci95_cycle_bootstrap"),
        row("Windows shared: pieces of the same breath on both sides", res["windows_shared"], "ci95_cycle_bootstrap"),
        row("Training data: the model scored on cycles it was trained on", res["training_data"], "ci95_cycle_bootstrap"),
        "",
        f"- Patients shared: {res['patients_shared']['test_patients_also_in_training']} test patients also had cycles in training; "
        f"{res['patients_shared']['cycles']} test cycles.",
        f"- Windows shared: {res['windows_shared']['test_cycles_with_windows_in_training']} test cycles had windows in training; "
        f"{res['windows_shared']['cycles']} test cycles.",
        "- Leaky-split intervals resample cycles, not patients, so they are too narrow; they are shown for scale only.",
        "",
        "Per-class recall (Crackles / Healthy / Wheezing / Wheezing with Crackles):",
        "",
    ]
    for k in ("patient_wise_cv_seed11", "patients_shared", "windows_shared", "training_data"):
        rc = res[k]["recall"]
        lines.append(f"- {k}: " + " / ".join(f"{100 * rc[l]:.0f}%" for l in CV.LABELS))
    lines += ["", "How to say it: \"When the test patients' recordings also appear in training, the same network scores "
              "X%. On patients it has never heard, it scores 40%. The first number measures memory; the second is the "
              "one we report.\" Never quote the leaky rows as accuracy.", ""]
    open(os.path.join(ROOT, "results", "leakage-demo.md"), "w", encoding="utf-8").write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    {"run": run, "report": report}[sys.argv[1]]()
