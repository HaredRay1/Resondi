"""Heart component, step 2 (14 Nov 2026): S1 / systole / S2 / diastole segmentation, S1-S2 timing and heart rate.

Fixed before the test patients are scored:
  - Model: frame classifier on the 50 frame/s log-power features (heart_data.py): three 1-D convolutions
    (129 -> 64 channels, kernel 5) and a bidirectional GRU (2 x 48), 4 outputs (S1, systole, S2, diastole).
    Trained on random 8 s crops of the TRAIN patients' annotated frames, class-weighted, AdamW 1e-3,
    up to 15 epochs, early stopping (patience 3) on VALIDATION frame accuracy, seed 11 (the primary model).
    CHANGED 14 Nov 00:55, before any test patient was scored: the first plan was 3 seeds, 40 epochs,
    patience 6, but one epoch took about 5 minutes on this computer (up to 10 hours in all), and
    validation frame accuracy was already 0.89 after 2 epochs.
  - Decoding: Viterbi over the cyclic order S1 -> systole -> S2 -> diastole -> S1, each state may stay or
    advance. The advance probability is chosen on VALIDATION (lowest heart-rate error) from {0.05, 0.1, 0.2, 0.3}.
  - Heart rate: 60 / median interval between consecutive decoded S1 onsets over the whole recording
    (what the app would compute). Reference: the same from the .tsv S1 onsets. Recordings with fewer than
    3 reference S1 onsets are skipped.
  - Timing: each reference S1 (S2) onset is matched to the nearest decoded S1 (S2) onset within 100 ms;
    reported: share matched (sensitivity), share of decoded onsets matched (PPV), mean absolute error (ms).
  - Baseline with no training: autocorrelation of the 25-150 Hz envelope, peak between 0.27 s and 1.5 s.
  - Primary figures: TEST patients, heart rate mean absolute error (BPM) with a patient bootstrap 95% CI,
    and the share of recordings within 5 BPM.

    python scripts/heart_seg.py train     # trains the three seeds -> work-exp/heart/seg_s*.pt
    python scripts/heart_seg.py report    # -> results/heart-segmentation.md / .json
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from heart_data import WORK, FPS

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SEEDS = (11,)
STATES = ["S1", "systole", "S2", "diastole"]
CROP = 400


def load():
    d = np.load(os.path.join(WORK, "data.npz"), allow_pickle=True)
    return {k: d[k] for k in d.files}


def build():
    import torch.nn as nn

    class Seg(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv = nn.Sequential(
                nn.Conv1d(129, 64, 5, padding=2), nn.BatchNorm1d(64), nn.ReLU(), nn.Dropout(0.1),
                nn.Conv1d(64, 64, 5, padding=2), nn.BatchNorm1d(64), nn.ReLU(), nn.Dropout(0.1),
                nn.Conv1d(64, 64, 5, padding=2), nn.BatchNorm1d(64), nn.ReLU())
            self.gru = nn.GRU(64, 48, batch_first=True, bidirectional=True)
            self.out = nn.Linear(96, 4)

        def forward(self, x):                      # x: (B, T, 129)
            h = self.conv(x.transpose(1, 2)).transpose(1, 2)
            h, _ = self.gru(h)
            return self.out(h)                     # (B, T, 4)
    return Seg()


def crops(F, y, rng, n):
    """n random annotated crops of CROP frames (padded when shorter)."""
    X = np.zeros((n, CROP, 129), np.float32); Y = np.zeros((n, CROP), np.int64)
    idx = rng.integers(0, len(F), n)
    for i, j in enumerate(idx):
        f, l = F[j], y[j]
        ann = np.where(l > 0)[0]
        lo = ann[0] if len(ann) else 0
        hi = (ann[-1] + 1) if len(ann) else len(f)
        start = lo if hi - lo <= CROP else rng.integers(lo, hi - CROP + 1)
        seg = slice(start, min(start + CROP, len(f)))
        X[i, :seg.stop - seg.start] = f[seg]; Y[i, :seg.stop - seg.start] = l[seg]
    return X, Y


def predict(models, F):
    import torch
    out = []
    with torch.no_grad():
        for f in F:
            x = torch.tensor(f.astype(np.float32))[None]
            out.append(np.mean([torch.softmax(m(x)[0], 1).numpy() for m in models], 0))
    return out


def frame_acc(P, y):
    ok = n = 0
    for p, l in zip(P, y):
        m = l > 0
        ok += int((p[m].argmax(1) + 1 == l[m]).sum()); n += int(m.sum())
    return ok / max(n, 1)


def train():
    import torch
    torch.set_num_threads(os.cpu_count() or 4)
    d = load()
    tr = np.where((d["part"] == "train"))[0]; va = np.where(d["part"] == "validation")[0]
    Ftr, ytr = d["F"][tr], d["y"][tr]
    has = np.array([(l > 0).any() for l in ytr]); Ftr, ytr = Ftr[has], ytr[has]
    lab = np.concatenate(list(ytr)); cnt = np.bincount(lab[lab > 0] - 1, minlength=4).astype(np.float32)
    w = torch.tensor(cnt.sum() / (4 * cnt))
    for s in SEEDS:
        path = os.path.join(WORK, f"seg_s{s}.pt")
        if os.path.exists(path):
            print(f"seed {s}: done already"); continue
        torch.manual_seed(s); rng = np.random.default_rng(s)
        m = build(); opt = torch.optim.AdamW(m.parameters(), lr=1e-3, weight_decay=1e-3)
        best, best_state, wait, t0 = -1, None, 0, time.time()
        for ep in range(1, 16):
            m.train()
            for _ in range(len(Ftr) // 32):
                X, Y = crops(Ftr, ytr, rng, 32)
                out = m(torch.tensor(X))
                Yt = torch.tensor(Y) - 1
                loss = torch.nn.functional.cross_entropy(out.reshape(-1, 4), Yt.reshape(-1), weight=w, ignore_index=-1)
                opt.zero_grad(); loss.backward(); opt.step()
            m.eval()
            acc = frame_acc(predict([m], d["F"][va]), d["y"][va])
            if acc > best:
                best, wait, best_ep = acc, 0, ep
                best_state = {k: v.clone() for k, v in m.state_dict().items()}
            else:
                wait += 1
                if wait >= 3:
                    break
            print(f"  seed {s} epoch {ep:>2}  val frame acc {acc:.3f}  {time.time() - t0:.0f}s", flush=True)
        torch.save(best_state, path)
        print(f"seed {s}: best epoch {best_ep}, val frame acc {best:.3f}", flush=True)


# ------------------------------------------------------------------ decoding and scoring
def viterbi(P, adv):
    """Cyclic S1->sys->S2->dia; P (T,4) probabilities -> state path 0..3."""
    T = len(P); lp = np.log(P + 1e-9)
    ls, la = np.log(1 - adv), np.log(adv)
    V = lp[0].copy(); back = np.zeros((T, 4), np.int8)
    for t in range(1, T):
        stay = V + ls
        move = np.roll(V, 1) + la                 # from previous state in the cycle
        choose = move > stay
        back[t] = np.where(choose, (np.arange(4) - 1) % 4, np.arange(4))
        V = np.where(choose, move, stay) + lp[t]
    path = np.zeros(T, np.int64); path[-1] = int(V.argmax())
    for t in range(T - 1, 0, -1):
        path[t - 1] = back[t, path[t]]
    return path


def onsets(path, state):
    """Frame indices where `state` starts (path in 0..3 or labels 1..4 shifted by caller)."""
    on = (path == state)
    return np.where(on & ~np.r_[False, on[:-1]])[0]


def bpm_from(on):
    if len(on) < 3:
        return None
    iv = np.diff(on) / FPS
    iv = iv[(iv > 0.25) & (iv < 2.0)]
    return float(60 / np.median(iv)) if len(iv) >= 2 else None


def bpm_autocorr(F):
    """No-training baseline: autocorrelation of the low-band (25-150 Hz) envelope."""
    env = np.exp(F[:, 1:10].astype(np.float32)).mean(1)
    env = (env - env.mean()) / (env.std() + 1e-8)
    ac = np.correlate(env, env, "full")[len(env) - 1:]
    lo, hi = int(0.27 * FPS), int(1.5 * FPS)
    if len(ac) <= hi:
        return None
    lag = lo + int(np.argmax(ac[lo:hi]))
    return float(60 * FPS / lag)


def match(ref, pred, tol=int(0.1 * FPS)):
    if len(ref) == 0:
        return 0, 0, []
    errs, used = [], set()
    for r in ref:
        if len(pred) == 0:
            break
        j = int(np.argmin(np.abs(pred - r)))
        if abs(pred[j] - r) <= tol and j not in used:
            used.add(j); errs.append(abs(pred[j] - r) / FPS * 1000)
    return len(errs), len(used), errs


def evaluate(d, idx, P, adv):
    rows = []
    for i, p in zip(idx, P):
        y = d["y"][i]; ann = np.where(y > 0)[0]
        ref_s1 = onsets(y, 1); ref_s2 = onsets(y, 3)
        ref_bpm = bpm_from(ref_s1)
        if ref_bpm is None:
            continue
        path = viterbi(p, adv)
        est = bpm_from(onsets(path, 0))
        lo, hi = ann[0], ann[-1]
        ps1 = onsets(path, 0); ps1 = ps1[(ps1 >= lo) & (ps1 <= hi)]
        ps2 = onsets(path, 2); ps2 = ps2[(ps2 >= lo) & (ps2 <= hi)]
        m1, u1, e1 = match(ref_s1, ps1); m2, u2, e2 = match(ref_s2, ps2)
        rows.append(dict(patient=str(d["patient"][i]), ref=ref_bpm, est=est, base=bpm_autocorr(d["F"][i]),
                         s1=(m1, len(ref_s1), u1, len(ps1), e1), s2=(m2, len(ref_s2), u2, len(ps2), e2),
                         facc=float(((p.argmax(1) + 1)[y > 0] == y[y > 0]).mean()) if (y > 0).any() else None))
    return rows


def summarise(rows, rng, key="est"):
    pats = sorted({r["patient"] for r in rows})
    err = {p: [] for p in pats}
    for r in rows:
        e = r[key]
        err[r["patient"]].append(abs(e - r["ref"]) if e is not None else np.nan)
    allv = np.array([v for p in pats for v in err[p]])
    valid = allv[~np.isnan(allv)]
    boots = []
    for _ in range(2000):
        s = np.concatenate([err[p] for p in rng.choice(pats, len(pats))])
        s = s[~np.isnan(s)]
        boots.append(np.mean(s))
    return {"mae_bpm": float(np.mean(valid)), "ci95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
            "median_ae": float(np.median(valid)), "within5": float(np.mean(valid <= 5)), "within10": float(np.mean(valid <= 10)),
            "no_estimate": int(np.isnan(allv).sum()), "recordings": int(len(allv)), "patients": len(pats)}


def report():
    import torch
    d = load()
    models = []
    for s in SEEDS:
        m = build(); m.load_state_dict(torch.load(os.path.join(WORK, f"seg_s{s}.pt"))); m.eval(); models.append(m)
    va = np.where(d["part"] == "validation")[0]; te = np.where(d["part"] == "test")[0]
    Pva = predict(models, d["F"][va])
    rng = np.random.default_rng(20261114)
    tune = {a: summarise(evaluate(d, va, Pva, a), rng)["mae_bpm"] for a in (0.05, 0.1, 0.2, 0.3)}
    adv = min(tune, key=tune.get)
    Pte = predict(models, d["F"][te])
    rows = evaluate(d, te, Pte, adv)
    res = {"advance_prob_chosen_on_validation": adv, "validation_mae_by_advance": tune,
           "test": {"model": summarise(rows, rng, "est"), "baseline_autocorr": summarise(rows, rng, "base")}}
    for k, st in (("S1", "s1"), ("S2", "s2")):
        m = sum(r[st][0] for r in rows); n = sum(r[st][1] for r in rows)
        u = sum(r[st][2] for r in rows); q = sum(r[st][3] for r in rows)
        e = [x for r in rows for x in r[st][4]]
        res["test"][k] = {"sensitivity": m / n, "ppv": u / max(q, 1), "mae_ms": float(np.mean(e)), "reference_onsets": n}
    res["test"]["frame_accuracy"] = float(np.mean([r["facc"] for r in rows if r["facc"] is not None]))
    ref = np.array([r["ref"] for r in rows]); est = np.array([np.nan if r["est"] is None else r["est"] for r in rows])
    ok = ~np.isnan(est); diff = est[ok] - ref[ok]
    res["test"]["bland_altman"] = {"bias": float(diff.mean()), "loa": [float(diff.mean() - 1.96 * diff.std()), float(diff.mean() + 1.96 * diff.std())]}
    res["test"]["reference_bpm_range"] = [float(ref.min()), float(np.median(ref)), float(ref.max())]
    json.dump(res, open(os.path.join(ROOT, "results", "heart-segmentation.json"), "w"), indent=1)
    np.savez(os.path.join(WORK, "seg_test_rows.npz"), ref=ref, est=est, patient=np.array([r["patient"] for r in rows]))
    t = res["test"]; mo, ba = t["model"], t["baseline_autocorr"]
    md = [
        "# Heart sound segmentation and heart rate on CirCor test patients (14 Nov 2026)",
        "",
        f"Patient-wise split, {mo['patients']} test patients, {mo['recordings']} recordings with at least 3 reference S1 onsets. "
        "Model: CNN + BiGRU frame classifier (one seed) with cyclic Viterbi decoding (`scripts/heart_seg.py`). "
        f"Viterbi advance probability {adv}, chosen on validation patients.",
        "",
        "| Measure | Trained model | No-training baseline (autocorrelation) |",
        "|---|---|---|",
        f"| Heart rate mean absolute error | **{mo['mae_bpm']:.1f} BPM** (95% CI {mo['ci95'][0]:.1f}–{mo['ci95'][1]:.1f}) | {ba['mae_bpm']:.1f} BPM ({ba['ci95'][0]:.1f}–{ba['ci95'][1]:.1f}) |",
        f"| Median absolute error | {mo['median_ae']:.1f} BPM | {ba['median_ae']:.1f} BPM |",
        f"| Recordings within 5 BPM | {100 * mo['within5']:.0f}% | {100 * ba['within5']:.0f}% |",
        f"| Recordings within 10 BPM | {100 * mo['within10']:.0f}% | {100 * ba['within10']:.0f}% |",
        f"| No estimate | {mo['no_estimate']} | {ba['no_estimate']} |",
        "",
        f"Bland–Altman (model − reference): bias {t['bland_altman']['bias']:+.1f} BPM, 95% limits {t['bland_altman']['loa'][0]:+.1f} to {t['bland_altman']['loa'][1]:+.1f}. "
        f"Reference heart rates: {t['reference_bpm_range'][0]:.0f}–{t['reference_bpm_range'][2]:.0f} BPM, median {t['reference_bpm_range'][1]:.0f} (children and adolescents).",
        "",
        "| Heart sound | Found within 100 ms (sensitivity) | Detections that are real (PPV) | Onset timing error |",
        "|---|---|---|---|",
        f"| S1 | {100 * t['S1']['sensitivity']:.1f}% | {100 * t['S1']['ppv']:.1f}% | {t['S1']['mae_ms']:.0f} ms |",
        f"| S2 | {100 * t['S2']['sensitivity']:.1f}% | {100 * t['S2']['ppv']:.1f}% | {t['S2']['mae_ms']:.0f} ms |",
        "",
        f"Frame accuracy on annotated frames (four states): {100 * t['frame_accuracy']:.1f}%.",
        "",
        "These are results on CirCor recordings (Brazilian children, electronic stethoscope). They have not been "
        "checked on Resondi device recordings, whose microphone may lose the lowest heart-sound frequencies.",
        "",
    ]
    open(os.path.join(ROOT, "results", "heart-segmentation.md"), "w", encoding="utf-8").write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    {"train": train, "report": report}[sys.argv[1]]()
