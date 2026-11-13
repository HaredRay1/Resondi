"""Heart component, step 3 (14 Nov 2026): murmur present / absent, patient level.

Fixed before the test patients are scored (design from the IMRaD's "Heart Sound Component"):
  - Unit of training: one recording (one chest site). Label 1 if the patient's murmur was heard at that
    site (CirCor "Murmur locations"), else 0. Patients labelled "Unknown" are not trained on.
  - Model: 1-D CNN over the 50 frame/s log-power features (heart_data.py): 129 -> 64 -> 96 -> 128 channels,
    kernel 5, max-pool 2 after each, then global mean + max pooling and a linear output. Random 6 s crops,
    class-weighted, AdamW 1e-3, up to 40 epochs, early stopping (patience 6) on VALIDATION patient-level
    AUROC (Present vs Absent). Seeds 11, 22, 33, probabilities averaged (the primary model).
  - Recording score: mean over 6 s windows at a 3 s hop. Patient score: the maximum over the patient's sites
    (a murmur counts as present when it is detected at any site).
  - Threshold: PRE-SPECIFIED SENSITIVITY 80%. On VALIDATION patients, the highest threshold whose
    sensitivity is at least 0.80. Specificity at that threshold is reported as the cost of that choice.
  - Primary figures (TEST patients, Present vs Absent): sensitivity, specificity, PPV, F1, Cohen's kappa,
    AUROC, confusion matrix, 95% patient bootstrap intervals. Unknown test patients: share flagged, shown
    separately. Murmur timing (systolic / diastolic) is not attempted in this step.

    python scripts/heart_murmur.py train
    python scripts/heart_murmur.py report   # -> results/heart-murmur.md / .json
"""
import json
import os
import sys
import time
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from heart_data import WORK

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SEEDS = (11, 22, 33)
CROP, HOP = 300, 150
TARGET_SENS = 0.80


def load():
    d = np.load(os.path.join(WORK, "data.npz"), allow_pickle=True)
    return {k: d[k] for k in d.files}


def build():
    import torch
    import torch.nn as nn

    class Mur(nn.Module):
        def __init__(self):
            super().__init__()
            def blk(a, b):
                return [nn.Conv1d(a, b, 5, padding=2), nn.BatchNorm1d(b), nn.ReLU(), nn.MaxPool1d(2), nn.Dropout(0.15)]
            self.f = nn.Sequential(*blk(129, 64), *blk(64, 96), *blk(96, 128))
            self.out = nn.Linear(256, 1)

        def forward(self, x):                      # (B, T, 129)
            h = self.f(x.transpose(1, 2))
            return self.out(torch.cat([h.mean(2), h.amax(2)], 1))[:, 0]
    return Mur()


def windows(f):
    if len(f) <= CROP:
        w = np.zeros((1, CROP, 129), np.float32); w[0, :len(f)] = f; return w
    starts = list(range(0, len(f) - CROP + 1, HOP))
    return np.stack([f[s:s + CROP].astype(np.float32) for s in starts])


def rec_scores(models, F):
    import torch
    out = []
    with torch.no_grad():
        for f in F:
            x = torch.tensor(windows(f))
            out.append(float(np.mean([torch.sigmoid(m(x)).numpy().mean() for m in models])))
    return np.array(out)


def patient_scores(d, idx, s):
    by = defaultdict(list)
    for i, v in zip(idx, s):
        by[str(d["patient"][i])].append(v)
    lab = {str(d["patient"][i]): str(d["patient_murmur"][i]) for i in idx}
    pats = sorted(by)
    return pats, np.array([max(by[p]) for p in pats]), np.array([lab[p] for p in pats])


def auroc(y, s):
    pos, neg = s[y == 1], s[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    return float(((pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean()))


def train():
    import torch
    torch.set_num_threads(os.cpu_count() or 4)
    d = load()
    known = d["patient_murmur"] != "Unknown"
    tr = np.where((d["part"] == "train") & known)[0]
    va = np.where(d["part"] == "validation")[0]
    Ftr, ytr = d["F"][tr], d["rec_murmur"][tr].astype(np.float32)
    pos_w = torch.tensor((ytr == 0).sum() / max((ytr == 1).sum(), 1))
    for s in SEEDS:
        path = os.path.join(WORK, f"mur_s{s}.pt")
        if os.path.exists(path):
            print(f"seed {s}: done already"); continue
        torch.manual_seed(s); rng = np.random.default_rng(s)
        m = build(); opt = torch.optim.AdamW(m.parameters(), lr=1e-3, weight_decay=1e-3)
        best, wait, t0 = -1, 0, time.time()
        for ep in range(1, 41):
            m.train()
            order = rng.permutation(len(Ftr))
            for a in range(0, len(order), 32):
                b = order[a:a + 32]
                X = np.zeros((len(b), CROP, 129), np.float32)
                for k, j in enumerate(b):
                    f = Ftr[j]
                    st = rng.integers(0, max(len(f) - CROP, 0) + 1)
                    seg = f[st:st + CROP]; X[k, :len(seg)] = seg
                loss = torch.nn.functional.binary_cross_entropy_with_logits(
                    m(torch.tensor(X)), torch.tensor(ytr[b]), pos_weight=pos_w)
                opt.zero_grad(); loss.backward(); opt.step()
            m.eval()
            pats, ps, lab = patient_scores(d, va, rec_scores([m], d["F"][va]))
            k = lab != "Unknown"
            auc = auroc((lab[k] == "Present").astype(int), ps[k])
            if auc > best:
                best, wait, best_ep = auc, 0, ep
                best_state = {kk: v.clone() for kk, v in m.state_dict().items()}
            else:
                wait += 1
                if wait >= 6:
                    break
            print(f"  seed {s} epoch {ep:>2}  val patient AUROC {auc:.3f}  {time.time() - t0:.0f}s", flush=True)
        torch.save(best_state, path)
        print(f"seed {s}: best epoch {best_ep}, val AUROC {best:.3f}", flush=True)


def metrics(y, s, thr):
    p = (s >= thr).astype(int)
    tp = int(((p == 1) & (y == 1)).sum()); fn = int(((p == 0) & (y == 1)).sum())
    tn = int(((p == 0) & (y == 0)).sum()); fp = int(((p == 1) & (y == 0)).sum())
    n = tp + fn + tn + fp
    sens = tp / max(tp + fn, 1); spec = tn / max(tn + fp, 1); ppv = tp / max(tp + fp, 1)
    f1 = 2 * tp / max(2 * tp + fp + fn, 1)
    po = (tp + tn) / n; pe = ((tp + fp) * (tp + fn) + (fn + tn) * (fp + tn)) / n ** 2
    kappa = (po - pe) / (1 - pe) if pe < 1 else 0.0
    return dict(sensitivity=sens, specificity=spec, ppv=ppv, f1=f1, kappa=kappa, auroc=auroc(y, s),
                tp=tp, fn=fn, tn=tn, fp=fp)


def report():
    import torch
    d = load()
    models = []
    for s in SEEDS:
        m = build(); m.load_state_dict(torch.load(os.path.join(WORK, f"mur_s{s}.pt"))); m.eval(); models.append(m)
    va = np.where(d["part"] == "validation")[0]; te = np.where(d["part"] == "test")[0]
    vp, vs, vl = patient_scores(d, va, rec_scores(models, d["F"][va]))
    k = vl != "Unknown"; vy = (vl[k] == "Present").astype(int); vsk = vs[k]
    cands = sorted(set(vsk), reverse=True)
    thr = next(t for t in cands if ((vsk >= t) & (vy == 1)).sum() / vy.sum() >= TARGET_SENS)
    tp_, ts, tl = patient_scores(d, te, rec_scores(models, d["F"][te]))
    k = tl != "Unknown"; ty = (tl[k] == "Present").astype(int); tsk = ts[k]
    res = {"threshold": float(thr), "validation": metrics(vy, vsk, thr), "test": metrics(ty, tsk, thr)}
    rng = np.random.default_rng(20261114)
    boots = defaultdict(list)
    for _ in range(2000):
        b = rng.integers(0, len(ty), len(ty))
        mb = metrics(ty[b], tsk[b], thr)
        for key in ("sensitivity", "specificity", "ppv", "f1", "kappa", "auroc"):
            boots[key].append(mb[key])
    res["test_ci95"] = {key: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))] for key, v in boots.items()}
    unk = ts[tl == "Unknown"]
    res["test_unknown"] = {"patients": int(len(unk)), "flagged": int((unk >= thr).sum())}
    res["test_patients"] = {"present": int(ty.sum()), "absent": int((ty == 0).sum())}
    json.dump(res, open(os.path.join(ROOT, "results", "heart-murmur.json"), "w"), indent=1)
    t, c = res["test"], res["test_ci95"]

    def f(key):
        return f"{100 * t[key]:.1f}% ({100 * c[key][0]:.1f}–{100 * c[key][1]:.1f})"
    md = [
        "# Heart murmur detection on CirCor test patients (14 Nov 2026)",
        "",
        f"Patient-wise split. Test: {res['test_patients']['present']} patients with a murmur, "
        f"{res['test_patients']['absent']} without (plus {res['test_unknown']['patients']} 'unknown', reported separately). "
        "Model: 3-seed 1-D CNN on log-power spectra (`scripts/heart_murmur.py`); a patient is positive when any site is.",
        "",
        f"Threshold set on validation patients for a pre-specified sensitivity of {int(100 * TARGET_SENS)}% "
        f"(validation: sensitivity {100 * res['validation']['sensitivity']:.1f}%, specificity {100 * res['validation']['specificity']:.1f}%).",
        "",
        "| Measure (test patients) | Value (95% CI) |",
        "|---|---|",
        f"| Sensitivity | **{f('sensitivity')}** |",
        f"| Specificity | {f('specificity')} |",
        f"| Positive predictive value | {f('ppv')} |",
        f"| F1 | {t['f1']:.2f} ({c['f1'][0]:.2f}–{c['f1'][1]:.2f}) |",
        f"| Cohen's kappa | {t['kappa']:.2f} ({c['kappa'][0]:.2f}–{c['kappa'][1]:.2f}) |",
        f"| AUROC | {t['auroc']:.2f} ({c['auroc'][0]:.2f}–{c['auroc'][1]:.2f}) |",
        "",
        "| | Model: murmur | Model: no murmur |",
        "|---|---|---|",
        f"| Reference: murmur | {t['tp']} | {t['fn']} |",
        f"| Reference: no murmur | {t['fp']} | {t['tn']} |",
        "",
        f"'Unknown' test patients flagged as murmur: {res['test_unknown']['flagged']} of {res['test_unknown']['patients']}.",
        "",
        "CirCor recordings only (Brazilian children, electronic stethoscope). Not checked on Resondi device recordings. "
        "A screening flag for practitioner review, never a diagnosis. Murmur timing (systolic / diastolic) not yet attempted.",
        "",
    ]
    open(os.path.join(ROOT, "results", "heart-murmur.md"), "w", encoding="utf-8").write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    {"train": train, "report": report}[sys.argv[1]]()
