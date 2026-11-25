"""Test-set evaluation of the ICBHI fusion study: every individual model and every fusion model, scored once.

    python scripts/fusion_eval.py

Pre-specified before any test patient was read (11 Nov): the PRIMARY model is late fusion (late3), the
configuration with the best mean balanced accuracy on the 30 ICBHI validation patients (48.2%). Every other
configuration is scored too, so the individual models can be compared with fusion, but none of them can
replace the primary model on the strength of its test score.

Each configuration uses the seed that scored best on ICBHI validation in results/fusion-validation.csv
(single_mfcc 22, single_spec 11, single_chroma 33, fdc3 11, fdc2_nochroma 11; late3 11 = the seed-11 single
models averaged). The script retrains exactly those runs, checks that each reproduces its logged validation score,
then scores the 31 ICBHI test patients and, as an external check, the held-out SPRSound test children.

Writes results/stats/: fusion-comparison.json, fusion-report.md, jamovi_fusion_cycles.csv,
fig_fusion_test.png, fig_fusion_recall.png; and one row per configuration in results/final-test-log.csv.
"""
import csv
import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime

import numpy as np
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resondi_model import ROOT, load_config
import fusion as Fu

OUT = os.path.join(ROOT, "results", "stats")
os.makedirs(OUT, exist_ok=True)
LABELS = load_config()["labels"]            # Crackles, Healthy, Wheezing, Wheezing with Crackles
H = LABELS.index("Healthy")
RNG = np.random.default_rng(20261111)
PRIMARY = "late3"
CHOSEN = {"single_mfcc": 22, "single_spec": 11, "single_chroma": 33, "fdc3": 11, "fdc2_nochroma": 11, "late3": 11}
NAMES = {"single_mfcc": "MFCC alone", "single_spec": "Spectrogram alone", "single_chroma": "Chromagram alone",
         "late3": "Late fusion (3 views)", "fdc3": "FDC-FS three-branch fusion", "fdc2_nochroma": "Fusion without chromagram"}
ORDER = ["single_mfcc", "single_spec", "single_chroma", "fdc2_nochroma", "fdc3", "late3"]
CACHE = os.path.join(Fu.EXP, "fusion-eval")
os.makedirs(CACHE, exist_ok=True)


def logged_val(recipe, seed):
    with open(os.path.join(ROOT, "results", "fusion-validation.csv")) as f:
        for r in csv.DictReader(f):
            if r["recipe"] == recipe and r["data"] == "icbhi" and int(r["seed"]) == seed and r["val_set"] == "icbhi":
                return float(r["cycle_balanced_acc"])


def window_probs(recipe, seed):
    """Validation and test window probabilities for one trained run (cached)."""
    path = os.path.join(CACHE, f"{recipe}_s{seed}.npz")
    if os.path.exists(path):
        return dict(np.load(path))
    views = Fu.RECIPES[recipe]
    t = time.time()
    model, prep, ep, probs, vals = Fu.train(list(views), "icbhi", seed)
    out = {"val": probs["icbhi"], "epoch": np.array(ep)}
    for key, part in (("test", "test"), ("sprs_test", "sprs_test")):
        if os.path.exists(os.path.join(Fu.EXP, f"raw_{part}.npz")):
            out[key] = Fu.predict(model, prep, [Fu.feature(v, part) for v in views])
    np.savez(path, **out)
    print(f"  trained {recipe} seed {seed}: epoch {ep}, {time.time() - t:.0f}s", flush=True)
    return out


def cycles(P, y, cyc, patient):
    """Average window probabilities within each cycle (sorted cycle ids, as fusion.score does)."""
    by = defaultdict(list)
    for p, c in zip(P, cyc):
        by[c].append(p)
    ids = sorted(by)
    first = {}
    for i, c in enumerate(cyc):
        first.setdefault(c, i)
    Pc = np.array([np.mean(by[i], 0) for i in ids])
    return Pc, np.array([y[first[i]] for i in ids]), np.array([patient[first[i]] for i in ids])


def metrics(yt, yp):
    k = len(LABELS)
    cm = np.zeros((k, k), int)
    for a, b in zip(yt, yp):
        cm[a, b] += 1
    sup = cm.sum(1)
    rec = np.divide(np.diag(cm), sup, out=np.zeros(k), where=sup > 0)
    pred = cm.sum(0)
    prec = np.divide(np.diag(cm), pred, out=np.zeros(k), where=pred > 0)
    f1 = np.divide(2 * prec * rec, prec + rec, out=np.zeros(k), where=(prec + rec) > 0)
    n = cm.sum()
    po = np.trace(cm) / n
    pe = (cm.sum(0) * cm.sum(1)).sum() / n ** 2
    spec = np.array([(n - sup[i] - pred[i] + cm[i, i]) / (n - sup[i]) for i in range(k)])
    se = (np.trace(cm) - cm[H, H]) / (n - sup[H])          # ICBHI: abnormal cycles put in the right abnormal class
    sp = cm[H, H] / sup[H]
    present = sup > 0
    return {"n": int(n), "balanced_accuracy": float(rec[present].mean()), "accuracy": float(po),
            "macro_f1": float(f1[present].mean()), "kappa": float((po - pe) / (1 - pe)),
            "icbhi_se": float(se), "icbhi_sp": float(sp), "icbhi_score": float((se + sp) / 2),
            "recall": rec.tolist(), "precision": prec.tolist(), "specificity": spec.tolist(), "f1": f1.tolist(),
            "support": sup.tolist(), "confusion": cm.tolist(), "majority_baseline": float(sup.max() / n)}


def boot(yt, preds, pat, keys, B=1000):
    """Patient-level bootstrap: CIs for each model and for each model minus the primary (balanced accuracy)."""
    up = np.unique(pat)
    idx = {p: np.where(pat == p)[0] for p in up}
    draws = defaultdict(list)
    for _ in range(B):
        s = np.concatenate([idx[p] for p in RNG.choice(up, len(up), replace=True)])
        if len(np.unique(yt[s])) < len(LABELS):
            continue
        m = {k: metrics(yt[s], preds[k][s]) for k in keys}
        for k in keys:
            draws[k].append(m[k]["balanced_accuracy"])
            draws[k + "_f1"].append(m[k]["macro_f1"])
            draws[k + "_minus_primary"].append(m[k]["balanced_accuracy"] - m[PRIMARY]["balanced_accuracy"])
    ci = {k: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] for k, v in draws.items()}
    return ci, len(draws[keys[0]])


def mcnemar(a, b):
    """a, b: boolean correct arrays on the same cycles. Exact binomial McNemar; b_ = a right & b wrong."""
    b_ = int(np.sum(a & ~b)); c_ = int(np.sum(~a & b))
    p = float(stats.binomtest(min(b_, c_), b_ + c_, 0.5).pvalue) if b_ + c_ else 1.0
    return {"b": b_, "c": c_, "odds_ratio": (b_ + 0.5) / (c_ + 0.5), "p": p}


def holm(ps):
    order = np.argsort(ps)
    adj = np.empty(len(ps)); run = 0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - r) * ps[i]))
        adj[i] = run
    return adj.tolist()


def main():
    import torch
    torch.set_num_threads(os.cpu_count() or 4)
    va = np.load(os.path.join(Fu.EXP, "raw_validation.npz"))
    te = np.load(os.path.join(Fu.EXP, "raw_test.npz"))
    sp = np.load(os.path.join(Fu.EXP, "raw_sprs_test.npz")) if os.path.exists(os.path.join(Fu.EXP, "raw_sprs_test.npz")) else None

    runs = {}
    needed = sorted({(r, s) for r, s in CHOSEN.items() if r != "late3"} | {(f"single_{v}", 11) for v in Fu.VIEWS})
    for r, s in needed:
        runs[(r, s)] = window_probs(r, s)
    runs[("late3", 11)] = {k: np.mean([runs[(f"single_{v}", 11)][k] for v in Fu.VIEWS], 0)
                           for k in ("val", "test", "sprs_test") if k in runs[("single_mfcc", 11)]}

    # Reproducibility check against the logged validation scores
    repro = {}
    for r, s in CHOSEN.items():
        Pc, yc, _ = cycles(runs[(r, s)]["val"], va["y"], va["cycle"], va["patient"])
        now = metrics(yc, Pc.argmax(1))["balanced_accuracy"]
        repro[r] = {"seed": s, "logged": logged_val(r, s), "retrained": now}
        print(f"{r:<15} seed {s}: validation logged {repro[r]['logged']:.4f}, retrained {now:.4f}", flush=True)

    result = {"primary": PRIMARY, "chosen_seeds": CHOSEN, "reproducibility": repro, "sets": {}}
    for key, raw in (("icbhi", te), ("sprs", sp)):
        if raw is None:
            continue
        part = "test" if key == "icbhi" else "sprs_test"
        preds, probs = {}, {}
        for r in ORDER:
            Pc, yt, pat = cycles(runs[(r, CHOSEN[r])][part], raw["y"], raw["cycle"], raw["patient"])
            preds[r], probs[r] = Pc.argmax(1), Pc
        M = {r: metrics(yt, preds[r]) for r in ORDER}
        ci, nb = boot(yt, preds, pat, ORDER)
        comps = [r for r in ORDER if r != PRIMARY]
        mc = {r: mcnemar(preds[PRIMARY] == yt, preds[r] == yt) for r in comps}
        for r, a in zip(comps, holm([mc[r]["p"] for r in comps])):
            mc[r]["p_holm"] = a
        result["sets"][key] = {"patients": int(len(np.unique(pat))), "cycles": int(len(yt)), "metrics": M, "ci": ci,
                               "bootstrap_draws": nb, "mcnemar_vs_primary": mc}
        if key == "icbhi":
            write_jamovi(yt, pat, preds)
    json.dump(result, open(os.path.join(OUT, "fusion-comparison.json"), "w"), indent=1)
    log_tests(result)
    figures(result)
    report(result)
    print("wrote", OUT)


def write_jamovi(yt, pat, preds):
    base = os.path.join(OUT, "jamovi_test_cycles.csv")
    old = list(csv.DictReader(open(base, encoding="utf-8"))) if os.path.exists(base) else None
    if old is not None:
        assert len(old) == len(yt) and all(o["true_label"] == LABELS[t] for o, t in zip(old, yt)), "cycle order differs"
    with open(os.path.join(OUT, "jamovi_fusion_cycles.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        hdr = ["cycle", "patient", "true_label"]
        if old is not None:
            hdr += ["pred_deployed_mfcc", "correct_deployed_mfcc"]
        for r in ORDER:
            hdr += [f"pred_{r}", f"correct_{r}"]
        w.writerow(hdr)
        for i, t in enumerate(yt):
            row = [i + 1, pat[i], LABELS[t]]
            if old is not None:
                row += [old[i]["predicted_label"], old[i]["correct_clean"]]
            for r in ORDER:
                row += [LABELS[preds[r][i]], int(preds[r][i] == t)]
            w.writerow(row)


def log_tests(result):
    path = os.path.join(ROOT, "results", "final-test-log.csv")
    M = result["sets"]["icbhi"]["metrics"]
    with open(path, "a", newline="") as f:
        w = csv.writer(f)
        for r in ORDER:
            rp = result["reproducibility"][r]
            w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), f"fusion-eval:{r}{' (PRIMARY)' if r == PRIMARY else ''}",
                        rp["seed"], "", f"{rp['retrained']:.4f}", f"{M[r]['balanced_accuracy']:.4f}",
                        f"{M[r]['macro_f1']:.4f}", ""])


def figures(result):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ROSE, DEEP, MUTED, PALE = "#E91E76", "#8E2A52", "#9E8892", "#F7D6E4"
    S = result["sets"]["icbhi"]
    M, CI = S["metrics"], S["ci"]
    labels = ["Deployed MFCC\n(11 Nov)"] + [NAMES[r].replace(" (3 views)", "").replace("FDC-FS three-branch fusion", "FDC-FS\nthree-branch").replace(" alone", "").replace("Fusion without chromagram", "Fusion, no\nchromagram") for r in ORDER]
    vals = [0.3504] + [M[r]["balanced_accuracy"] for r in ORDER]
    lo = [0.246] + [CI[r][0] for r in ORDER]
    hi = [0.403] + [CI[r][1] for r in ORDER]
    cols = [MUTED, MUTED, MUTED, MUTED, PALE, PALE, ROSE]
    fig, ax = plt.subplots(figsize=(8.5, 3.8), dpi=200)
    x = np.arange(len(vals))
    ax.bar(x, np.array(vals) * 100, color=cols, edgecolor=DEEP, linewidth=0.8)
    ax.errorbar(x, np.array(vals) * 100, yerr=[(np.array(vals) - lo) * 100, (np.array(hi) - vals) * 100], fmt="none",
                ecolor=DEEP, capsize=3, lw=1)
    for i, v in enumerate(vals):
        ax.text(i, hi[i] * 100 + 1.2, f"{v * 100:.1f}", ha="center", fontsize=8, color=DEEP)
    ax.axhline(25, ls="--", color=MUTED, lw=1)
    ax.set_xlim(-0.6, len(vals) + 0.15)
    ax.text(len(vals) + 0.15, 25.8, "chance 25%", ha="right", fontsize=7.5, color=DEEP)
    ax.set_xticks(x, labels, fontsize=7.5)
    ax.set_ylabel("Test balanced accuracy (%)", color=DEEP)
    ax.set_ylim(0, max(hi) * 100 + 8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_fusion_test.png"), facecolor="white")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.5, 3.6), dpi=200)
    show = ["single_mfcc", "single_spec", "single_chroma", "fdc3", "late3"]
    cl = [MUTED, "#C9B8BE", PALE, DEEP, ROSE]
    wdt = 0.16
    for j, r in enumerate(show):
        ax.bar(np.arange(4) + (j - 2) * wdt, np.array(M[r]["recall"]) * 100, wdt, color=cl[j], edgecolor=DEEP,
               linewidth=0.5, label=NAMES[r])
    ax.set_xticks(np.arange(4), LABELS, fontsize=8.5)
    ax.set_ylabel("Test recall (%)", color=DEEP)
    ax.legend(fontsize=7.5, ncol=3, frameon=False, loc="upper right")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_fusion_recall.png"), facecolor="white")
    plt.close(fig)


def report(result):
    L = ["# Fusion study: test-set comparison", "",
         f"Primary model (pre-specified on validation): **{NAMES[PRIMARY]}**. Every configuration below was scored once.", ""]
    for key, S in result["sets"].items():
        L += [f"## {'ICBHI test' if key == 'icbhi' else 'SPRSound test (external, children)'}: {S['patients']} patients, {S['cycles']} cycles/events", "",
              "| Model | Balanced acc. (95% CI) | Macro-F1 | Kappa | ICBHI score | Crackles | Healthy | Wheezing | W+C | vs primary: b / c, p (Holm) |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for r in ORDER:
            m, c = S["metrics"][r], S["ci"][r]
            mc = S["mcnemar_vs_primary"].get(r)
            cmp_ = f"{mc['b']} / {mc['c']}, {mc['p_holm']:.3f}" if mc else "—"
            L.append(f"| {NAMES[r]} | {m['balanced_accuracy']*100:.1f} ({c[0]*100:.1f}–{c[1]*100:.1f}) | {m['macro_f1']:.3f} | "
                     f"{m['kappa']:.3f} | {m['icbhi_score']*100:.1f} | " + " | ".join(f"{x*100:.0f}" for x in m["recall"]) + f" | {cmp_} |")
        L.append("")
    L += ["## Reproducibility", ""] + [f"- {r}: seed {v['seed']}, validation logged {v['logged']:.4f}, retrained {v['retrained']:.4f}"
                                        for r, v in result["reproducibility"].items()]
    open(os.path.join(OUT, "fusion-report.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
