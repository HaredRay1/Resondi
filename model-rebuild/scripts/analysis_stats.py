"""Statistical analysis for the research plan's Results (Data Analysis section), on the model already chosen
and tested on 11 Nov (work-exp/final-baseline.pt: MFCC 1-D CNN, seed 11, epoch 6). Nothing here selects a model,
so re-scoring the test patients with it does not leak the test set into any choice.

    python scripts/analysis_stats.py

Writes results/stats/: jamovi-ready CSV files, stats-results.json, stats-report.md and figures.
Analyses: classification metrics with patient-level bootstrap CIs; Cohen's kappa; ICBHI score; McNemar's exact test
for clean vs noise-contaminated cycles (Holm-corrected); recording-level severity score (direct and OLS-calibrated
on validation recordings, beta-regression sensitivity check, VIF), RMSE, MAE and R2 on test recordings;
Kruskal-Wallis with epsilon-squared and Dwass-Steel-Critchlow-Fligner pairwise tests.
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict

import numpy as np
from scipy import optimize, special, stats

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resondi_model import ROOT, load_config
from resondi_model.data import read_manifest
import experiment as E
import final_test as FT

OUT = os.path.join(ROOT, "results", "stats")
os.makedirs(OUT, exist_ok=True)
LABELS = load_config()["labels"]           # Crackles, Healthy, Wheezing, Wheezing with Crackles
H = LABELS.index("Healthy")
RNG = np.random.default_rng(20261111)
SNRS = (20, 10, 5)


# ------------------------------------------------------------------ model and probabilities
def load_model():
    import torch
    ck = torch.load(os.path.join(E.EXP, "final-baseline.pt"), weights_only=False)
    Ftr = np.load(os.path.join(E.EXP, "feat_mfcc13_train.npy"), mmap_mode="r")
    mu = np.asarray(Ftr, dtype=np.float64).mean((0, 1)).astype(np.float32)
    sd = (np.asarray(Ftr, dtype=np.float64).std((0, 1)) + 1e-6).astype(np.float32)
    model = E.build_net("cnn1d", "softmax4", Ftr.shape[1], Ftr.shape[2])
    model.load_state_dict(ck["state"])
    model.eval()
    return model, torch.tensor(mu), torch.tensor(sd), ck


def window_probs(model, mu, sd, F):
    import torch
    out = []
    with torch.no_grad():
        for a in range(0, len(F), 1024):
            x = (torch.tensor(F[a:a + 1024]) - mu) / sd
            out.append(torch.softmax(model(x), 1).numpy())
    return np.concatenate(out)


def cycle_probs(P, cyc):
    by = defaultdict(list)
    for p, c in zip(P, cyc):
        by[int(c)].append(p)
    ids = sorted(by)
    return ids, np.array([np.mean(by[i], 0) for i in ids])


# ------------------------------------------------------------------ metrics
def confusion(y, p, k=4):
    m = np.zeros((k, k), int)
    for a, b in zip(y, p):
        m[a, b] += 1
    return m


def metrics(y, p):
    m = confusion(y, p)
    n = m.sum()
    rec = m.diagonal() / m.sum(1)
    prec = np.divide(m.diagonal(), m.sum(0), out=np.zeros(4), where=m.sum(0) > 0)
    f1 = np.divide(2 * prec * rec, prec + rec, out=np.zeros(4), where=(prec + rec) > 0)
    spec = np.array([(n - m[i].sum() - m[:, i].sum() + m[i, i]) / (n - m[i].sum()) for i in range(4)])
    po = m.diagonal().sum() / n
    pe = (m.sum(1) * m.sum(0)).sum() / n ** 2
    abn = [i for i in range(4) if i != H]
    se_icbhi = sum(m[i, i] for i in abn) / sum(m[i].sum() for i in abn)
    sp_icbhi = m[H, H] / m[H].sum()
    return {"n": int(n), "accuracy": po, "balanced_accuracy": rec.mean(), "macro_f1": f1.mean(),
            "kappa": (po - pe) / (1 - pe), "icbhi_se": se_icbhi, "icbhi_sp": sp_icbhi,
            "icbhi_score": (se_icbhi + sp_icbhi) / 2, "majority_baseline": m.sum(1).max() / n,
            "recall": rec.tolist(), "precision": prec.tolist(), "specificity": spec.tolist(), "f1": f1.tolist(),
            "confusion": m.tolist()}


def bootstrap(y, p, patients, B=1000):
    pts = np.unique(patients)
    idx = {q: np.where(patients == q)[0] for q in pts}
    keys = ("balanced_accuracy", "macro_f1", "kappa", "icbhi_score", "accuracy")
    draws = {k: [] for k in keys}
    for _ in range(B):
        s = np.concatenate([idx[q] for q in RNG.choice(pts, len(pts), replace=True)])
        if len(np.unique(y[s])) < 4:
            continue
        r = metrics(y[s], p[s])
        for k in keys:
            draws[k].append(r[k])
    return {k: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] for k, v in draws.items()}, len(draws[keys[0]])


def wilson(k, n, z=1.959964):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def mcnemar(a_correct, b_correct):
    b = int(np.sum(a_correct & ~b_correct))      # right clean, wrong noisy
    c = int(np.sum(~a_correct & b_correct))      # wrong clean, right noisy
    p = stats.binomtest(b, b + c, 0.5).pvalue if b + c else 1.0
    chi = (abs(b - c) - 1) ** 2 / (b + c) if b + c else 0.0
    return {"b": b, "c": c, "chi2_cc": chi, "p_exact": p, "odds_ratio": (b / c) if c else float("inf")}


def holm(ps):
    order = np.argsort(ps)
    adj = np.empty(len(ps))
    run = 0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - rank) * ps[i]))
        adj[i] = run
    return adj.tolist()


# ------------------------------------------------------------------ severity
def ols(X, y):
    A = np.column_stack([np.ones(len(X)), X])
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ beta
    dof = len(y) - A.shape[1]
    s2 = resid @ resid / dof
    cov = s2 * np.linalg.inv(A.T @ A)
    se = np.sqrt(np.diag(cov))
    t = beta / se
    p = 2 * stats.t.sf(np.abs(t), dof)
    r2 = 1 - resid @ resid / np.sum((y - y.mean()) ** 2)
    return beta, se, p, r2, dof


def vif(X):
    out = []
    for j in range(X.shape[1]):
        others = np.delete(X, j, 1)
        _, _, _, r2, _ = ols(others, X[:, j])
        out.append(1 / (1 - r2))
    return out


def beta_regression(X, y):
    """Beta regression (logit mean link, constant precision) by maximum likelihood; y in (0, 1)."""
    A = np.column_stack([np.ones(len(X)), X])

    def nll(theta):
        b, logphi = theta[:-1], theta[-1]
        mu = special.expit(A @ b)
        phi = np.exp(logphi)
        return -np.sum(special.gammaln(phi) - special.gammaln(mu * phi) - special.gammaln((1 - mu) * phi)
                       + (mu * phi - 1) * np.log(y) + ((1 - mu) * phi - 1) * np.log(1 - y))

    res = optimize.minimize(nll, np.zeros(A.shape[1] + 1), method="BFGS")
    return res.x[:-1], float(np.exp(res.x[-1])), bool(res.success)


def fit_stats(ref, pred):
    e = pred - ref
    return {"rmse": float(np.sqrt(np.mean(e ** 2))), "mae": float(np.mean(np.abs(e))),
            "r2": float(1 - np.sum(e ** 2) / np.sum((ref - ref.mean()) ** 2)),
            "bias": float(np.mean(e)), "spearman_rho": float(stats.spearmanr(ref, pred)[0])}


def dscf(groups):
    """Dwass-Steel-Critchlow-Fligner all-pairs test (tie-corrected)."""
    names = list(groups)
    k = len(names)
    out = []
    for a in range(k):
        for b in range(a + 1, k):
            x, z = np.asarray(groups[names[a]]), np.asarray(groups[names[b]])
            ni, nj = len(x), len(z)
            r = stats.rankdata(np.concatenate([x, z]))
            W = r[:ni].sum()
            ties = Counter(np.concatenate([x, z]).tolist()).values()
            tcorr = sum(t ** 3 - t for t in ties) / ((ni + nj) * (ni + nj - 1))
            var = ni * nj / 12 * ((ni + nj + 1) - tcorr)
            Wst = np.sqrt(2) * (W - ni * (ni + nj + 1) / 2) / np.sqrt(var)
            p = stats.studentized_range.sf(abs(Wst), k, np.inf)
            out.append({"pair": f"{names[a]} vs {names[b]}", "W": float(Wst), "p": float(p)})
    return out


def category(labels):
    """Recording category rule from the plan: Healthy if no adventitious cycle; else the most frequent
    adventitious class, ties resolved in favour of Wheezing with Crackles."""
    adv = [l for l in labels if l != "Healthy"]
    if not adv:
        return "Healthy"
    c = Counter(adv)
    top = max(c.values())
    winners = [l for l in c if c[l] == top]
    return winners[0] if len(winners) == 1 else "Wheezing with Crackles"


# ------------------------------------------------------------------ main
def main():
    model, mu, sd, ck = load_model()
    manifest = read_manifest(os.path.join(ROOT, "work", "manifest.csv"))
    rows_tv = [r for r in manifest if r["split"] in ("train", "validation")]
    rows_te = [r for r in manifest if r["split"] == "test"]

    va = np.load(os.path.join(E.EXP, "raw_validation.npz"))
    te = FT.test_windows()
    Fva = np.load(os.path.join(E.EXP, "feat_mfcc13_validation.npy"))
    Fte = FT.test_features("mfcc13", te["X"])

    ids_va, Pva = cycle_probs(window_probs(model, mu, sd, Fva), va["cycle"])
    ids_te, Pte = cycle_probs(window_probs(model, mu, sd, Fte), te["cycle"])
    y_te = np.array([LABELS.index(rows_te[i]["label"]) for i in ids_te])
    pat_te = np.array([rows_te[i]["patient"] for i in ids_te])
    pred_te = Pte.argmax(1)

    R = {"model": {"recipe": "baseline (MFCC 1-D CNN)", "seed": ck["seed"], "epoch": ck["epoch"]}}
    R["test"] = metrics(y_te, pred_te)
    R["test_ci"], R["bootstrap_valid_draws"] = bootstrap(y_te, pred_te, pat_te)
    R["test_patients"] = int(len(np.unique(pat_te)))
    print(f"test cycles {len(y_te)}, balanced accuracy {R['test']['balanced_accuracy']:.4f} "
          f"CI {R['test_ci']['balanced_accuracy']}, kappa {R['test']['kappa']:.3f}")

    # ---- H1: clean vs noise-contaminated (same cycles), Gaussian noise at fixed SNR per window
    correct_clean = pred_te == y_te
    noisy = {}
    Xte = te["X"].astype(np.float32)
    rms = np.sqrt(np.mean(Xte ** 2, 1, keepdims=True)) + 1e-9
    for snr in SNRS:
        rng = np.random.default_rng(1000 + snr)
        Xn = Xte + rng.standard_normal(Xte.shape).astype(np.float32) * (rms / 10 ** (snr / 20))
        Xn = np.clip(Xn, -32768, 32767)
        Fn = FT.test_features("mfcc13", Xn)
        _, Pn = cycle_probs(window_probs(model, mu, sd, Fn), te["cycle"])
        pn = Pn.argmax(1)
        noisy[snr] = pn
        r = metrics(y_te, pn)
        mc = mcnemar(correct_clean, pn == y_te)
        R[f"noise_{snr}dB"] = {"metrics": r, "mcnemar": mc}
        print(f"SNR {snr} dB: balanced {r['balanced_accuracy']:.4f} accuracy {r['accuracy']:.4f} McNemar b={mc['b']} c={mc['c']} p={mc['p_exact']:.3g}")
    adj = holm([R[f"noise_{s}dB"]["mcnemar"]["p_exact"] for s in SNRS])
    for s, a in zip(SNRS, adj):
        R[f"noise_{s}dB"]["mcnemar"]["p_holm"] = a

    # ---- severity score per recording
    def per_recording(rows, ids, P):
        rec = defaultdict(lambda: {"labels": [], "probs": [], "patient": None})
        for i, p in zip(ids, P):
            r = rows[i]
            d = rec[r["audio"]]
            d["labels"].append(r["label"])
            d["probs"].append(p)
            d["patient"] = r["patient"]
        out = []
        for a, d in sorted(rec.items()):
            pm = np.mean(d["probs"], 0)
            n = len(d["labels"])
            adv = sum(l != "Healthy" for l in d["labels"])
            out.append({"recording": os.path.basename(a), "patient": d["patient"], "cycles": n,
                        "category": category(d["labels"]), "ref": 100 * adv / n,
                        "pred_direct": 100 * (1 - pm[H]),
                        "pC": pm[LABELS.index("Crackles")], "pW": pm[LABELS.index("Wheezing")],
                        "pWC": pm[LABELS.index("Wheezing with Crackles")]})
        return out

    rec_va = per_recording(rows_tv, ids_va, Pva)
    rec_te = per_recording(rows_te, ids_te, Pte)
    Xv = np.array([[r["pW"], r["pC"], r["pWC"]] for r in rec_va])
    yv = np.array([r["ref"] for r in rec_va])
    beta, se, p, r2, dof = ols(Xv, yv)
    R["calibration"] = {"n_recordings": len(rec_va), "coef": dict(zip(["intercept", "p(W)", "p(C)", "p(WC)"], beta.tolist())),
                        "se": se.tolist(), "p": p.tolist(), "r2_fit": r2, "df": dof, "vif": vif(Xv)}
    Xt = np.array([[r["pW"], r["pC"], r["pWC"]] for r in rec_te])
    raw = beta[0] + Xt @ beta[1:]
    cal = np.clip(raw, 0, 100)
    R["calibration"]["clipped_test"] = int(np.sum((raw < 0) | (raw > 100)))
    yt = np.array([r["ref"] for r in rec_te])
    direct = np.array([r["pred_direct"] for r in rec_te])
    # beta regression sensitivity analysis (y squeezed into (0, 1))
    n_v = len(yv)
    yb = ((yv / 100) * (n_v - 1) + 0.5) / n_v
    bb, phi, ok = beta_regression(Xv, yb)
    beta_pred = 100 * special.expit(bb[0] + Xt @ bb[1:])
    R["severity_test"] = {"n_recordings": len(rec_te), "direct": fit_stats(yt, direct),
                          "calibrated_ols": fit_stats(yt, cal), "beta_regression": fit_stats(yt, beta_pred),
                          "beta_coef": bb.tolist(), "beta_phi": phi, "beta_converged": ok,
                          "ref_mean": float(yt.mean()), "ref_sd": float(yt.std(ddof=1))}
    for r, c_, b_ in zip(rec_te, cal, beta_pred):
        r["pred_calibrated"], r["pred_beta"] = float(c_), float(b_)

    # Kruskal-Wallis on calibrated predicted severity across recording categories
    groups = defaultdict(list)
    for r in rec_te:
        groups[r["category"]].append(r["pred_calibrated"])
    order = [g for g in ["Healthy", "Crackles", "Wheezing", "Wheezing with Crackles"] if g in groups]
    Hs, pk = stats.kruskal(*[groups[g] for g in order])
    n = sum(len(groups[g]) for g in order)
    R["kruskal"] = {"H": float(Hs), "df": len(order) - 1, "p": float(pk), "epsilon_sq": float(Hs / (n - 1)),
                    "groups": {g: {"n": len(groups[g]), "median": float(np.median(groups[g])),
                                   "iqr": [float(np.percentile(groups[g], 25)), float(np.percentile(groups[g], 75))]} for g in order},
                    "dscf": dscf({g: groups[g] for g in order})}
    print("KW", R["kruskal"]["H"], R["kruskal"]["p"])

    # ---- field agreement (from the paper: 6 of 15) for the record
    lo, hi = wilson(6, 15)
    R["field_agreement"] = {"k": 6, "n": 15, "pct": 40.0, "wilson_ci": [lo, hi], "binom_p_vs_25": stats.binomtest(6, 15, 0.25, alternative="greater").pvalue}

    # ---- validation comparison table (all recipes, as logged)
    val_rows = []
    with open(os.path.join(ROOT, "results", "experiments-validation.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            val_rows.append(("experiment", r["recipe"], int(r["seed"]), float(r["val_cycle_balanced_acc"]), float(r["val_cycle_macro_f1"])))
    fp = os.path.join(ROOT, "results", "fusion-validation.csv")
    if os.path.exists(fp):
        with open(fp, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["val_set"] == "icbhi":
                    val_rows.append((f"fusion ({r['data']})", r["recipe"], int(r["seed"]), float(r["cycle_balanced_acc"]), float(r["cycle_macro_f1"])))
    summ = defaultdict(list)
    for src, rec, seed, ba, f1 in val_rows:
        summ[(src, rec)].append((ba, f1))
    R["validation_summary"] = [{"source": s, "recipe": r, "seeds": len(v), "bal_mean": float(np.mean([a for a, _ in v])),
                                "bal_sd": float(np.std([a for a, _ in v], ddof=1)) if len(v) > 1 else 0.0,
                                "f1_mean": float(np.mean([b for _, b in v]))} for (s, r), v in summ.items()]

    # ---- write jamovi-ready CSVs
    with open(os.path.join(OUT, "jamovi_test_cycles.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["patient", "true_label", "predicted_label", "correct_clean"] + [f"correct_snr{s}" for s in SNRS]
                   + [f"p_{l.replace(' ', '_')}" for l in LABELS])
        for j in range(len(y_te)):
            w.writerow([pat_te[j], LABELS[y_te[j]], LABELS[pred_te[j]], int(correct_clean[j])]
                       + [int(noisy[s][j] == y_te[j]) for s in SNRS] + [f"{x:.5f}" for x in Pte[j]])
    with open(os.path.join(OUT, "jamovi_recordings_severity.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["subset", "recording", "patient", "cycles", "category", "ref_severity", "pred_direct",
                    "pred_calibrated", "pred_beta", "mean_p_Wheezing", "mean_p_Crackles", "mean_p_WheezingCrackles"])
        for subset, rows in (("validation", rec_va), ("test", rec_te)):
            for r in rows:
                w.writerow([subset, r["recording"], r["patient"], r["cycles"], r["category"], f"{r['ref']:.3f}",
                            f"{r['pred_direct']:.3f}", f"{r.get('pred_calibrated', ''):.3f}" if "pred_calibrated" in r else "",
                            f"{r['pred_beta']:.3f}" if "pred_beta" in r else "", f"{r['pW']:.5f}", f"{r['pC']:.5f}", f"{r['pWC']:.5f}"])
    with open(os.path.join(OUT, "jamovi_validation_models.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["source", "recipe", "seed", "val_balanced_accuracy", "val_macro_f1"])
        w.writerows(val_rows)
    with open(os.path.join(OUT, "stats-results.json"), "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=float)
    figures(R, rec_te)
    print("wrote", OUT)


# ------------------------------------------------------------------ figures (rose theme)
def validation_figure(R):
    """Plan figure "Validation Balanced Accuracy by Configuration": every row of its table, under the same names."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    DEEP, ROSE, MUTED = "#8E2A52", "#E91E76", "#9E8892"
    plt.rcParams.update({"text.color": DEEP, "axes.labelcolor": DEEP, "xtick.color": DEEP, "ytick.color": DEEP,
                         "axes.edgecolor": MUTED})
    rows = [r for r in R["validation_summary"] if r["seeds"] >= 2]
    names = {"late3": "Late fusion of three views", "single_mfcc": "MFCC (fusion study)", "single_spec": "Spectrogram",
             "mfcc_twodet": "MFCC, two yes/no detectors", "baseline": "MFCC (first deployed design)",
             "mfcc_spec": "MFCC + augmentation", "mfe_twodet": "Mel energies, two detectors",
             "single_chroma": "Chromagram", "mfe_floor72": "Mel energies, −72 dB floor",
             "mfe_aug": "Mel energies + augmentation", "mfe": "Mel energies (MFE)", "mfe_mixup": "Mel energies + mixup",
             "mfe_floor72_aug": "Mel energies, −72 dB + augmentation", "mfe2k": "Mel energies, 50–2,000 Hz",
             "fdc3": "Three-branch fusion", "fdc2_nochroma": "Fusion without chromagram"}
    rows.sort(key=lambda r: r["bal_mean"])
    fig, ax = plt.subplots(figsize=(6.4, 0.32 * len(rows) + 0.9), dpi=200)
    y = np.arange(len(rows))
    cols = [ROSE if r["recipe"] in ("late3", "fdc3", "fdc2_nochroma") else (DEEP if "mfcc" in r["recipe"] or r["recipe"] == "baseline" else MUTED) for r in rows]
    ax.barh(y, [r["bal_mean"] * 100 for r in rows], xerr=[r["bal_sd"] * 100 for r in rows], color=cols,
            error_kw={"ecolor": "#3A2230", "lw": 0.8, "capsize": 2})
    ax.set_yticks(y, [names.get(r["recipe"], r["recipe"]) for r in rows], fontsize=8)
    ax.axvline(25, color=MUTED, ls="--", lw=0.8)
    ax.text(25.5, len(rows) - 0.35, "chance 25%", color=MUTED, fontsize=7, va="bottom")
    ax.set_ylim(-0.6, len(rows) + 0.1)
    ax.set_xlim(0, 55)
    ax.set_xlabel("Validation balanced accuracy, mean ± SD over seeds (%)")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_validation_models.png"), facecolor="white")
    plt.close(fig)


def figures(R, rec_te):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    from matplotlib.colors import LinearSegmentedColormap
    DEEP, ROSE, MUTED, PALE = "#8E2A52", "#E91E76", "#9E8892", "#F7D6E4"
    font = "Poppins" if any("Poppins" in f.name for f in font_manager.fontManager.ttflist) else "DejaVu Sans"
    plt.rcParams.update({"font.family": font, "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": DEEP,
                         "xtick.color": DEEP, "ytick.color": DEEP})
    short = ["Crackles", "Healthy", "Wheezing", "Wheezing +\nCrackles"]

    # confusion matrix (row-normalised)
    m = np.array(R["test"]["confusion"])
    pct = m / m.sum(1, keepdims=True) * 100
    fig, ax = plt.subplots(figsize=(5.2, 4.2), dpi=200)
    ax.imshow(pct, cmap=LinearSegmentedColormap.from_list("r", ["#FFFFFF", PALE, ROSE, DEEP]), vmin=0, vmax=100)
    for i in range(4):
        for j in range(4):
            ax.text(j, i, f"{m[i, j]}\n{pct[i, j]:.0f}%", ha="center", va="center", fontsize=8,
                    color="white" if pct[i, j] > 55 else DEEP)
    ax.set_xticks(range(4), short, fontsize=8)
    ax.set_yticks(range(4), short, fontsize=8)
    ax.set_xlabel("Predicted class")
    ax.set_ylabel("Reference class")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_confusion_test.png"), facecolor="white")
    plt.close(fig)

    # validation comparison
    validation_figure(R)

    # severity scatter
    ref = np.array([r["ref"] for r in rec_te])
    cal = np.array([r["pred_calibrated"] for r in rec_te])
    fig, ax = plt.subplots(figsize=(4.6, 4.2), dpi=200)
    cmap = {"Healthy": PALE, "Crackles": ROSE, "Wheezing": DEEP, "Wheezing with Crackles": MUTED}
    for g, c in cmap.items():
        sel = [i for i, r in enumerate(rec_te) if r["category"] == g]
        ax.scatter(ref[sel], cal[sel], s=16, color=c, edgecolor=DEEP, linewidth=0.4, label=f"{g} (n={len(sel)})")
    ax.plot([0, 100], [0, 100], color=MUTED, lw=0.8, ls="--")
    ax.set_xlim(-3, 103)
    ax.set_ylim(-3, 103)
    ax.set_xlabel("Reference severity (% adventitious cycles)")
    ax.set_ylabel("Predicted severity, calibrated (%)")
    ax.legend(fontsize=6.5, frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_severity_test.png"), facecolor="white")
    plt.close(fig)

    # noise robustness
    xs = ["Clean"] + [f"{s} dB" for s in SNRS]
    ba = [R["test"]["balanced_accuracy"] * 100] + [R[f"noise_{s}dB"]["metrics"]["balanced_accuracy"] * 100 for s in SNRS]
    ac = [R["test"]["accuracy"] * 100] + [R[f"noise_{s}dB"]["metrics"]["accuracy"] * 100 for s in SNRS]
    fig, ax = plt.subplots(figsize=(5.2, 3.0), dpi=200)
    ax.plot(xs, ba, "-o", color=ROSE, label="Balanced accuracy")
    ax.plot(xs, ac, "-s", color=DEEP, label="Accuracy")
    ax.axhline(25, color=MUTED, ls="--", lw=0.8)
    ax.set_ylabel("Test-set score (%)")
    ax.set_xlabel("Signal-to-noise ratio of added noise")
    ax.set_ylim(15, 60)
    ax.legend(frameon=False, fontsize=8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_noise_test.png"), facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
