"""Option H (12 Nov): 5-fold patient cross-validation over all 126 ICBHI patients.

Why: the 31-patient test set gives a wide interval (39.4%, CI 28-45%) and has now been read three times.
Cross-validation tests every ICBHI patient exactly once, each by a model that never saw that patient,
so the estimate uses 126 patients instead of 31 and no single split decides it.

Design (fixed before any fold is scored):
  - Folds: 126 ICBHI patients dealt greedily into 5 folds, balanced by (label, stethoscope), fixed seed.
  - Fold k: TEST = fold k, VALIDATION (early stopping only) = fold k+1, TRAIN = the other three folds.
  - Configs:
      mfcc_icbhi  : MFCC 1-D CNN, ICBHI only, plain features      (the app's design; comparator), seed 11
      fdc3_sprs   : FDC-FS three-branch, ICBHI + rebalanced SPRSound, 0.1-3.9 kHz levelled features,
                    per-source normalisation, (source, class) weighting   (the 12 Nov best), seeds 11/22/33
                    and their 3-seed ENSEMBLE (option A: +0.8 ICBHI / +1.7 SPRSound on validation)
  - Headline metric: cycle-level balanced accuracy pooled over all 126 patients, with a patient bootstrap CI;
    also the mean +/- SD over the 5 folds, macro F1, plain accuracy, per-class recall.
  - SPRSound test children (230) are scored by every fold model; reported as the mean over folds.

Resumable: each (config, seed, fold) saves its window probabilities to work-exp/cv/, and finished ones are skipped.

    python scripts/cv.py run          # train everything missing (hours)
    python scripts/cv.py report       # pooled results -> results/cv-results.md / .json
"""
import csv
import json
import os
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resondi_model import ROOT, load_config
from resondi_model.data import read_manifest, device
from resondi_model.metrics import report
import fusion as Fu

CV_DIR = os.path.join(Fu.EXP, "cv")
K = 5
PARTS = ("train", "validation", "test")
CONFIGS = {
    "mfcc_icbhi": dict(views=["mfcc"], sprs=False, bandlimit=False, srcnorm=False, seeds=(11,)),
    "fdc3_sprs": dict(views=["mfcc", "spec", "chroma"], sprs=True, bandlimit=True, srcnorm=True, seeds=(11, 22, 33)),
}
LABELS = load_config()["labels"]


# ------------------------------------------------------------------ data
def icbhi_all():
    """All ICBHI windows (train, validation and test parts), with globally unique cycle ids."""
    y, cyc, pat = [], [], []
    for i, part in enumerate(PARTS):
        d = np.load(os.path.join(Fu.EXP, f"raw_{part}.npz"))
        y.append(d["y"]); cyc.append(d["cycle"] + i * 1_000_000); pat.append(d["patient"])
    return np.concatenate(y), np.concatenate(cyc), np.concatenate(pat)


def icbhi_feats(views):
    return [np.concatenate([Fu.feature(v, part) for part in PARTS]) for v in views]


def make_folds():
    """Deal patients into K folds, balancing (label, stethoscope) cycle counts; largest patients first."""
    rows = read_manifest(os.path.join(ROOT, "work", "manifest.csv"))
    by_pat = defaultdict(Counter)
    for r in rows:
        by_pat[r["patient"]][(r["label"], device(r))] += 1
    totals = Counter()
    for c in by_pat.values():
        totals.update(c)
    pats = sorted(by_pat)
    np.random.default_rng(20261112).shuffle(pats)
    pats.sort(key=lambda p: -sum(by_pat[p].values()))
    have = [Counter() for _ in range(K)]
    fold = {}
    for p in pats:
        def deficit(k):
            return sum(max(0.0, totals[key] / K - have[k][key]) / max(totals[key], 1) * n for key, n in by_pat[p].items())
        k = max(range(K), key=lambda k: (deficit(k), -sum(have[k].values())))
        fold[p] = k
        have[k].update(by_pat[p])
    return fold


# ------------------------------------------------------------------ training (mirrors fusion.train)
def train_fold(Ftr, ytr, src, Fva, yva, cva, seed, balance, epochs=30, patience=8):
    import torch
    torch.manual_seed(seed); np.random.seed(seed)
    prep = Fu.standardiser(Ftr, src)
    model = Fu.build([(F.shape[1], F.shape[2]) for F in Ftr])
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-3)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
    Y = torch.tensor(ytr)
    if balance:
        cell = src * 4 + ytr
        n_cell = np.bincount(cell, minlength=8).astype(np.float64)
        sw = torch.tensor(len(ytr) / ((n_cell > 0).sum() * n_cell[cell]), dtype=torch.float32)
    else:
        counts = np.bincount(ytr, minlength=4).astype(np.float32)
        w = torch.tensor(counts.sum() / (4 * counts))
    best, best_state, best_ep, wait = -1, None, 0, 0
    for ep in range(1, epochs + 1):
        model.train()
        perm = np.random.permutation(len(Y))
        for a in range(0, len(perm), 64):
            b = np.sort(perm[a:a + 64])
            out = model(prep([F[b].astype(np.float32) for F in Ftr], src[b]))
            if balance:
                wb = sw[b]
                loss = (torch.nn.functional.cross_entropy(out, Y[b], reduction="none") * wb).sum() / wb.sum()
            else:
                loss = torch.nn.functional.cross_entropy(out, Y[b], weight=w)
            opt.zero_grad(); loss.backward(); opt.step()
        sched.step()
        s = Fu.score(Fu.predict(model, prep, Fva, 0), yva, cva)["cycle"]["balanced_accuracy"]
        if s > best:
            best, best_ep, wait = s, ep, 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            wait += 1
            if wait >= patience:
                break
    model.load_state_dict(best_state)
    return model, prep, best_ep, best


def run():
    import torch
    torch.set_num_threads(os.cpu_count() or 4)
    os.makedirs(CV_DIR, exist_ok=True)
    y, cyc, pat = icbhi_all()
    fold_of = make_folds()
    fold = np.array([fold_of[p] for p in pat])
    json.dump({p: int(k) for p, k in fold_of.items()}, open(os.path.join(CV_DIR, "folds.json"), "w"), indent=0)
    for k in range(K):
        print(f"fold {k}: {len({p for p, f in fold_of.items() if f == k})} patients, "
              f"{len(set(cyc[fold == k]))} cycles, labels {np.bincount(y[fold == k], minlength=4).tolist()}", flush=True)
    for name, cfg in CONFIGS.items():
        Fu.BANDLIMIT, Fu.SRCNORM = cfg["bandlimit"], cfg["srcnorm"]
        todo = [(s, k) for s in cfg["seeds"] for k in range(K)
                if not os.path.exists(os.path.join(CV_DIR, f"{name}_s{s}_f{k}.npz"))]
        if not todo:
            continue
        F = icbhi_feats(cfg["views"])
        if cfg["sprs"]:
            st = np.load(os.path.join(Fu.EXP, "raw_sprs_train.npz"))
            Fs_all = [Fu.feature(v, "sprs_train") for v in cfg["views"]]
            sp_test = np.load(os.path.join(Fu.EXP, "raw_sprs_test.npz"))
            Fs_test = [Fu.feature(v, "sprs_test") for v in cfg["views"]]
        for s, k in todo:
            t0 = time.time()
            te, va = fold == k, fold == (k + 1) % K
            tr = ~(te | va)
            Ftr, ytr = [f[tr] for f in F], y[tr]
            src = np.zeros(len(ytr), int)
            if cfg["sprs"]:
                keep = Fu.sprs_balanced_rows(st["y"], st["cycle"], int((ytr == Fu.HEALTHY).sum()))
                Ftr = [np.concatenate([a, b[keep]]) for a, b in zip(Ftr, Fs_all)]
                ytr = np.concatenate([ytr, st["y"][keep]])
                src = np.concatenate([src, np.ones(len(keep), int)])
            model, prep, ep, vbest = train_fold(Ftr, ytr, src, [f[va] for f in F], y[va], cyc[va], s, cfg["sprs"])
            out = {"test_idx": np.where(te)[0], "P": Fu.predict(model, prep, [f[te] for f in F], 0),
                   "epoch": ep, "val": vbest}
            if cfg["sprs"]:
                out["P_sprs"] = Fu.predict(model, prep, Fs_test, 1)
            np.savez(os.path.join(CV_DIR, f"{name}_s{s}_f{k}.npz"), **out)
            r = Fu.score(out["P"], y[te], cyc[te])["cycle"]
            print(f"{name:<11} seed {s} fold {k}: epoch {ep:>2}  val {vbest:.3f}  TEST-FOLD bal {r['balanced_accuracy']:.3f}  "
                  f"F1 {r['macro_f1']:.3f}  {time.time() - t0:.0f}s", flush=True)
            del Ftr
    print("all folds done", flush=True)


# ------------------------------------------------------------------ report
def cycle_level(P, y, cyc):
    by = defaultdict(list)
    for p, c in zip(P, cyc):
        by[c].append(p)
    ids = sorted(by)
    cy = dict(zip(cyc, y))
    return np.array(ids), np.array([cy[i] for i in ids]), np.array([np.mean(by[i], 0).argmax() for i in ids])


def bal(yt, yp):
    return float(np.mean([np.mean(yp[yt == c] == c) for c in range(4) if (yt == c).any()]))


def report_cv():
    y, cyc, pat = icbhi_all()
    fold_of = json.load(open(os.path.join(CV_DIR, "folds.json")))
    rng = np.random.default_rng(20261112)
    results, lines = {}, []
    variants = [("mfcc_icbhi", (11,)), ("fdc3_sprs", (11,)), ("fdc3_sprs", (22,)), ("fdc3_sprs", (33,)),
                ("fdc3_sprs", (11, 22, 33))]
    sp = np.load(os.path.join(Fu.EXP, "raw_sprs_test.npz"))
    for name, seeds in variants:
        tag = f"{name} " + ("ensemble 11+22+33" if len(seeds) > 1 else f"seed {seeds[0]}")
        P = np.zeros((len(y), 4)); per_fold, sprs_scores = [], []
        ok = True
        for k in range(K):
            files = [os.path.join(CV_DIR, f"{name}_s{s}_f{k}.npz") for s in seeds]
            if not all(os.path.exists(f) for f in files):
                ok = False; break
            ds = [np.load(f) for f in files]
            idx = ds[0]["test_idx"]
            Pk = np.mean([d["P"] for d in ds], 0)
            P[idx] = Pk
            _, yt, yp = cycle_level(Pk, y[idx], cyc[idx])
            per_fold.append(bal(yt, yp))
            if "P_sprs" in ds[0]:
                _, yt2, yp2 = cycle_level(np.mean([d["P_sprs"] for d in ds], 0), sp["y"], sp["cycle"])
                sprs_scores.append(bal(yt2, yp2))
        if not ok:
            lines.append(f"{tag:<34} (incomplete)"); continue
        ids, yt, yp = cycle_level(P, y, cyc)
        cp = dict(zip(cyc, pat)); pc = np.array([cp[i] for i in ids])
        pats = np.unique(pc); rows = {p: np.where(pc == p)[0] for p in pats}
        boots = []
        for _ in range(2000):
            m = np.concatenate([rows[p] for p in rng.choice(pats, len(pats))])
            boots.append(bal(yt[m], yp[m]))
        r = report(yt, yp, LABELS)
        res = {"pooled_balanced": bal(yt, yp), "ci95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
               "fold_mean": float(np.mean(per_fold)), "fold_sd": float(np.std(per_fold)), "per_fold": per_fold,
               "accuracy": r["accuracy"], "macro_f1": r["macro_f1"],
               "recall": {p["label"]: p["recall"] for p in r["per_class"]}, "patients": int(len(pats)), "cycles": int(len(ids)),
               "sprs_test_mean": float(np.mean(sprs_scores)) if sprs_scores else None}
        results[tag] = res
        lines.append(f"{tag:<34} pooled bal {res['pooled_balanced']:.3f} (CI {res['ci95'][0]:.3f}-{res['ci95'][1]:.3f})  "
                     f"folds {res['fold_mean']:.3f}+/-{res['fold_sd']:.3f}  acc {res['accuracy']:.3f}  F1 {res['macro_f1']:.3f}  "
                     + " ".join(f"{k[:4]}={v:.2f}" for k, v in res["recall"].items())
                     + (f"  SPRS-test {res['sprs_test_mean']:.3f}" if res["sprs_test_mean"] is not None else ""))
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    print("\n".join(lines))
    json.dump({"evaluated": stamp, "folds": K, "results": results}, open(os.path.join(ROOT, "results", "cv-results.json"), "w"), indent=1)
    with open(os.path.join(ROOT, "results", "cv-results.md"), "w", encoding="utf-8") as f:
        f.write(f"# 5-fold patient cross-validation over all ICBHI patients ({stamp})\n\n"
                "Every ICBHI patient is tested exactly once, by a model that never saw them. Cycle-level balanced accuracy is "
                "pooled over all patients, with a 95% patient-bootstrap CI.\n\n```\n" + "\n".join(lines) + "\n```\n")


if __name__ == "__main__":
    {"run": run, "report": report_cv}[sys.argv[1]]()
