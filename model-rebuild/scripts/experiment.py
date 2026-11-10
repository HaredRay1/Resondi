"""Compare training recipes on the VALIDATION patients only. The test patients are never read here.

    python scripts/experiment.py cache                       # once: cut train/validation audio into 1 s windows
    python scripts/experiment.py run baseline mfe2d ...      # train each recipe with 3 seeds, report validation
    python scripts/experiment.py list                        # show the recipes

Every recipe is something Edge Impulse can rebuild, so a winner can go into the app:
features are the MFCC or MFE (mel filterbank energy) processing blocks, the networks use
Conv1D/Conv2D, BatchNorm, pooling and Dense layers, and augmentation is done during training.

Results are appended to results/experiments-validation.csv. Choose the recipe on these numbers;
score the test patients once, for the chosen recipe only (scripts/final_test.py).
"""
import argparse
import csv
import os
import sys
import time
import zipfile
from collections import defaultdict
from datetime import datetime

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from resondi_model import ROOT, load_config
from resondi_model.data import read_manifest
from resondi_model.dsp import load_audio, windows, MFCC, _filterbank
from resondi_model.metrics import report

EXP = os.path.join(ROOT, "work-exp")          # caches for this script (excluded from Drive and git)
ICBHI = r"C:\Users\Hared\Downloads\archive.zip"
PARTS = ("train", "validation")               # never "test"

# ---------------------------------------------------------------- recipes
# feature: mfcc13 | mfe40 | mfe40_2k (40 mel bands, 50-2000 Hz, where lung sounds are)
# net:     cnn1d (the app's design, [32, 64]) | cnn2d (Conv2D + BatchNorm, global pooling)
# head:    softmax4 (one 4-way output) | twodet (crackles yes/no and wheeze yes/no, combined into the 4 labels)
# aug:     none | spec (time and frequency masking) | spec+gain (also random level for MFE) | +mixup
# The 2-D network took 171 s per epoch on this 4-core PC (about 6 hours per recipe), so the
# comparison uses the 1-D network, which is also Edge Impulse's default for its MFE block.
RECIPES = {
    "baseline":         dict(feature="mfcc13",   net="cnn1d", head="softmax4", aug="none"),
    "mfcc_spec":        dict(feature="mfcc13",   net="cnn1d", head="softmax4", aug="spec"),
    "mfe":              dict(feature="mfe40",    net="cnn1d", head="softmax4", aug="none"),
    "mfe2k":            dict(feature="mfe40_2k", net="cnn1d", head="softmax4", aug="none"),
    "mfe2k_aug":        dict(feature="mfe40_2k", net="cnn1d", head="softmax4", aug="spec+gain"),
    "mfe2k_twodet":     dict(feature="mfe40_2k", net="cnn1d", head="twodet",   aug="spec+gain"),
    "mfe2k_mixup":      dict(feature="mfe40_2k", net="cnn1d", head="softmax4", aug="spec+gain+mixup"),
    "mfe2k_twodet_mixup": dict(feature="mfe40_2k", net="cnn1d", head="twodet", aug="spec+gain+mixup"),
    # Noise floor -72 dB instead of Edge Impulse's default -52: at -52, 41% of ICBHI inputs are clipped to zero.
    "mfe2k_floor72":     dict(feature="mfe40_2k", net="cnn1d", head="softmax4", aug="none", floor=-72.0),
    "mfe2k_floor72_aug": dict(feature="mfe40_2k", net="cnn1d", head="softmax4", aug="spec+gain", floor=-72.0),
    # Full-range MFE beat 50-2000 Hz on validation (11 Nov), so the remaining ideas are tested at full range too.
    "mfe_aug":           dict(feature="mfe40", net="cnn1d", head="softmax4", aug="spec+gain"),
    "mfe_twodet":        dict(feature="mfe40", net="cnn1d", head="twodet",   aug="spec+gain"),
    "mfe_mixup":         dict(feature="mfe40", net="cnn1d", head="softmax4", aug="spec+gain+mixup"),
    "mfe_floor72":       dict(feature="mfe40", net="cnn1d", head="softmax4", aug="none", floor=-72.0),
    "mfe_floor72_aug":   dict(feature="mfe40", net="cnn1d", head="softmax4", aug="spec+gain", floor=-72.0),
    "mfcc_twodet":       dict(feature="mfcc13", net="cnn1d", head="twodet",  aug="spec"),
    "mfe2k_2d_aug":   dict(feature="mfe40_2k", net="cnn2d", head="softmax4", aug="spec+gain"),  # slow; not in the default run
}
DEFAULT_RUN = [k for k in RECIPES if RECIPES[k]["net"] == "cnn1d"]
SEEDS = (11, 22, 33)
NOISE_FLOOR_DB = -52.0   # Edge Impulse MFE default


# ---------------------------------------------------------------- step 1: raw windows, train + validation only
def cache():
    cfg = load_config()
    sr = cfg["audio"]["sample_rate"]
    win = int(sr * cfg["audio"]["window_ms"] / 1000)
    rows = read_manifest(os.path.join(ROOT, "work", "manifest.csv"))
    rows = [r for r in rows if r["split"] in PARTS]
    assert rows and all(r["split"] != "test" for r in rows)
    labels = cfg["labels"]
    z = zipfile.ZipFile(ICBHI)
    by_audio = defaultdict(list)
    for i, r in enumerate(rows):
        by_audio[r["audio"]].append(i)
    out = {p: {"X": [], "y": [], "cycle": [], "patient": []} for p in PARTS}
    for k, (audio, idx) in enumerate(sorted(by_audio.items())):
        x = load_audio(z.read(audio[4:]), sr)
        for i in idx:
            r = rows[i]
            stride = cfg["audio"]["train_stride_ms" if r["split"] == "train" else "eval_stride_ms"]
            for w in windows(x, r["start"], r["end"], sr, win, int(sr * stride / 1000)):
                o = out[r["split"]]
                o["X"].append(w.astype(np.int16))
                o["y"].append(labels.index(r["label"]))
                o["cycle"].append(i)
                o["patient"].append(r["patient"])
        if k % 100 == 0:
            print(f"  {k}/{len(by_audio)} recordings")
    os.makedirs(EXP, exist_ok=True)
    for p, o in out.items():
        np.savez(os.path.join(EXP, f"raw_{p}.npz"), X=np.stack(o["X"]), y=np.array(o["y"]),
                 cycle=np.array(o["cycle"]), patient=np.array(o["patient"]))
        print(f"{p}: {len(o['y'])} windows from {len(set(o['patient']))} patients")


# ---------------------------------------------------------------- features
def log_mel_db(X, sr, n_mels, low, high, flen=0.02, fstep=0.02, nfft=256):
    """Mel filterbank energies in dB, unclipped (Edge Impulse MFE before its noise-floor step)."""
    fl, fs = int(round(flen * sr)), int(round(fstep * sr))
    n = 1 + (X.shape[1] - fl) // fs
    idx = np.arange(fl)[None, :] + fs * np.arange(n)[:, None]
    fb = _filterbank(n_mels, nfft, sr, low, high)
    out = np.empty((len(X), n, n_mels), np.float32)
    for a in range(0, len(X), 2048):
        fr = X[a:a + 2048].astype(np.float32)[:, idx]                     # (b, n, fl)
        power = np.abs(np.fft.rfft(fr, n=nfft, axis=-1)) ** 2 / nfft
        e = np.maximum(power @ fb.T, 1e-10)
        out[a:a + 2048] = 10 * np.log10(e)
    return out


def features(name, part):
    path = os.path.join(EXP, f"feat_{name}_{part}.npy")
    if os.path.exists(path):
        return np.load(path)
    cfg = load_config()
    sr = cfg["audio"]["sample_rate"]
    X = np.load(os.path.join(EXP, f"raw_{part}.npz"))["X"]
    if name == "mfcc13":
        m = MFCC(cfg["mfcc"], sr)
        F = np.stack([m(x.astype(np.float32)) for x in X])
    elif name == "mfe40":
        F = log_mel_db(X, sr, 40, 0, None)
    elif name == "mfe40_2k":
        F = log_mel_db(X, sr, 40, 50, 2000)
    else:
        raise ValueError(name)
    np.save(path, F.astype(np.float32))
    return F


FULL_SCALE_DB = 20 * np.log10(32768.0)   # windows are int16-scale; dB must be relative to full scale


def mfe_scale(db, floor=NOISE_FLOOR_DB):
    """Edge Impulse MFE output scaling: clip at the noise floor, then map to roughly 0..1.

    Fixed 11 Nov: the energies come from int16-scale samples, so they sit ~90 dB above full-scale dB.
    Without subtracting FULL_SCALE_DB, 72% of inputs saturated at 1.0 and every MFE recipe collapsed
    to one class (the 00:38 run, kept in experiments-validation.csv, is invalid for MFE recipes)."""
    import torch
    db = torch.clamp(db - FULL_SCALE_DB, min=floor)
    return torch.clamp((db - floor) / (-floor + 12.0), 0.0, 1.0)


# ---------------------------------------------------------------- networks
def build_net(net, head, n_frames, n_feat):
    import torch
    from torch import nn
    n_out = 2 if head == "twodet" else 4
    if net == "cnn1d":
        class Net(nn.Module):
            def __init__(self):
                super().__init__()
                self.f = nn.Sequential(
                    nn.Conv1d(n_feat, 32, 3, padding=1), nn.ReLU(), nn.MaxPool1d(2, ceil_mode=True), nn.Dropout(0.25),
                    nn.Conv1d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool1d(2, ceil_mode=True), nn.Dropout(0.25))
                self.h = nn.Linear(64 * (-(-(-(-n_frames // 2)) // 2)), n_out)

            def forward(self, x):
                return self.h(self.f(x.transpose(1, 2)).flatten(1))
        return Net()

    def block(i, o):
        return [nn.Conv2d(i, o, 3, padding=1), nn.BatchNorm2d(o), nn.ReLU(), nn.MaxPool2d(2), nn.Dropout(0.2)]

    class Net2(nn.Module):
        def __init__(self):
            super().__init__()
            self.f = nn.Sequential(*block(1, 16), *block(16, 32), *block(32, 64))
            self.h = nn.Sequential(nn.Dropout(0.3), nn.Linear(64, n_out))

        def forward(self, x):                      # x: (b, frames, bands)
            x = self.f(x.unsqueeze(1))
            return self.h(x.mean((2, 3)))          # global average pooling
    return Net2()


def four_class_logprob(out, head):
    """Log-probabilities over (Crackles, Healthy, Wheezing, Wheezing with Crackles)."""
    import torch
    if head == "softmax4":
        return torch.log_softmax(out, 1)
    lc, lw = torch.nn.functional.logsigmoid(out[:, 0]), torch.nn.functional.logsigmoid(out[:, 1])
    nc, nw = torch.nn.functional.logsigmoid(-out[:, 0]), torch.nn.functional.logsigmoid(-out[:, 1])
    return torch.stack([lc + nw, nc + nw, nc + lw, lc + lw], 1)   # label order is alphabetical


# ---------------------------------------------------------------- training
def train_one(recipe, seed, Ftr, ytr, Fva, yva, cyc_va, epochs=30, patience=8, quiet=False):
    import torch
    torch.manual_seed(seed)
    np.random.seed(seed)
    rng = np.random.default_rng(seed)
    is_mfe = recipe["feature"].startswith("mfe")
    aug = recipe["aug"]
    head = recipe["head"]

    # Per-band standardisation for MFCC (fitted on training only); MFE uses Edge Impulse's fixed scaling.
    if is_mfe:
        floor = recipe.get("floor", NOISE_FLOOR_DB)
        prep = lambda x: mfe_scale(x, floor)
    else:
        mu, sd = Ftr.mean((0, 1)), Ftr.std((0, 1)) + 1e-6
        mu_t, sd_t = torch.tensor(mu), torch.tensor(sd)
        prep = lambda x: (x - mu_t) / sd_t
    Xtr, Xva = torch.tensor(Ftr), torch.tensor(Fva)
    Ytr = torch.tensor(ytr)
    model = build_net(recipe["net"], head, Ftr.shape[1], Ftr.shape[2])
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-3)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
    counts = np.bincount(ytr, minlength=4).astype(np.float32)
    w4 = torch.tensor(counts.sum() / (4 * counts))
    # attribute weights for the two-detector head (crackles = classes 0 and 3, wheeze = 2 and 3)
    att = torch.stack([(Ytr == 0) | (Ytr == 3), (Ytr == 2) | (Ytr == 3)], 1).float()
    pos = att.mean(0)
    posw = (1 - pos) / pos

    def augment(xb, yb):
        if "gain" in aug and is_mfe:
            xb = xb + torch.tensor(rng.uniform(-20, 20, (len(xb), 1, 1)), dtype=torch.float32)
        xb = prep(xb)
        if "spec" in aug:
            b, T, Fq = xb.shape
            t0, tw = rng.integers(0, T, b), rng.integers(0, T // 5 + 1, b)
            f0, fw = rng.integers(0, Fq, b), rng.integers(0, Fq // 5 + 1, b)
            ti, fi = np.arange(T)[None, :], np.arange(Fq)[None, :]
            tmask = torch.tensor((ti >= t0[:, None]) & (ti < (t0 + tw)[:, None]))
            fmask = torch.tensor((fi >= f0[:, None]) & (fi < (f0 + fw)[:, None]))
            xb = xb.masked_fill(tmask[:, :, None] | fmask[:, None, :], 0.0)
        return xb, yb

    best, best_state, best_ep, wait = -1, None, 0, 0
    bs = 64
    for ep in range(1, epochs + 1):
        model.train()
        perm = torch.randperm(len(Ytr))
        for a in range(0, len(perm), bs):
            b = perm[a:a + bs]
            xb, yb = augment(Xtr[b].clone(), Ytr[b])
            mix = "mixup" in aug
            if mix:
                lam = float(rng.beta(0.4, 0.4))
                j = torch.randperm(len(b))
                xb = lam * xb + (1 - lam) * xb[j]
            out = model(xb)
            if head == "softmax4":
                lp = torch.log_softmax(out, 1)
                l1 = torch.nn.functional.nll_loss(lp, yb, weight=w4)
                loss = lam * l1 + (1 - lam) * torch.nn.functional.nll_loss(lp, yb[j], weight=w4) if mix else l1
            else:
                tb = att[b]
                if mix:
                    tb = lam * tb + (1 - lam) * tb[j]
                loss = torch.nn.functional.binary_cross_entropy_with_logits(out, tb, pos_weight=posw)
            opt.zero_grad()
            loss.backward()
            opt.step()
        sched.step()
        r = evaluate(model, prep, head, Xva, yva, cyc_va)
        if not quiet:
            print(f"    seed {seed} epoch {ep:>2}  val cycle balanced {r['cycle']['balanced_accuracy']:.3f}  "
                  f"window balanced {r['window']['balanced_accuracy']:.3f}", flush=True)
        score = r["cycle"]["balanced_accuracy"]
        if score > best:
            best, best_ep, wait = score, ep, 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
            best_r = r
        else:
            wait += 1
            if wait >= patience:
                break
    model.load_state_dict(best_state)
    return model, prep, best_r, best_ep


def evaluate(model, prep, head, X, y, cyc):
    import torch
    labels = load_config()["labels"]
    model.eval()
    with torch.no_grad():
        P = torch.cat([four_class_logprob(model(prep(X[a:a + 1024])), head).exp() for a in range(0, len(X), 1024)]).numpy()
    win = report(y, P.argmax(1), labels)
    by = defaultdict(list)
    for p, c in zip(P, cyc):
        by[c].append(p)
    ids = sorted(by)
    cy = {c: yy for c, yy in zip(cyc, y)}
    cycr = report(np.array([cy[i] for i in ids]), np.array([np.mean(by[i], 0).argmax() for i in ids]), labels)
    return {"window": win, "cycle": cycr}


def run(names):
    import torch
    torch.set_num_threads(os.cpu_count() or 4)
    va = np.load(os.path.join(EXP, "raw_validation.npz"))
    tr = np.load(os.path.join(EXP, "raw_train.npz"))
    ytr, yva, cyc_va = tr["y"], va["y"], va["cycle"]
    out_csv = os.path.join(ROOT, "results", "experiments-validation.csv")
    new = not os.path.exists(out_csv)
    for name in names:
        rec = RECIPES[name]
        Ftr, Fva = features(rec["feature"], "train"), features(rec["feature"], "validation")
        scores = []
        for seed in SEEDS:
            t0 = time.time()
            _, _, r, ep = train_one(rec, seed, Ftr, ytr, Fva, yva, cyc_va, quiet=True)
            c, w = r["cycle"], r["window"]
            scores.append(c["balanced_accuracy"])
            rec_str = " ".join(f"{p['label'][:4]}={p['recall']:.2f}" for p in c["per_class"])
            print(f"{name:<24} seed {seed}  epoch {ep:>2}  val cycle bal {c['balanced_accuracy']:.3f}  "
                  f"F1 {c['macro_f1']:.3f}  window bal {w['balanced_accuracy']:.3f}  [{rec_str}]  {time.time() - t0:.0f}s", flush=True)
            with open(out_csv, "a", newline="") as f:
                wr = csv.writer(f)
                if new:
                    wr.writerow(["time", "recipe", "feature", "net", "head", "aug", "seed", "epoch",
                                 "val_cycle_balanced_acc", "val_cycle_macro_f1", "val_window_balanced_acc"]
                                + [f"val_cycle_recall_{p['label']}" for p in c["per_class"]])
                    new = False
                wr.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), name, rec["feature"], rec["net"], rec["head"],
                             rec["aug"], seed, ep, f"{c['balanced_accuracy']:.4f}", f"{c['macro_f1']:.4f}",
                             f"{w['balanced_accuracy']:.4f}"] + [f"{p['recall']:.4f}" for p in c["per_class"]])
        print(f"== {name}: validation cycle balanced accuracy {np.mean(scores):.3f} +/- {np.std(scores):.3f} over {len(SEEDS)} seeds\n", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["cache", "run", "list"])
    ap.add_argument("recipes", nargs="*")
    a = ap.parse_args()
    if a.cmd == "cache":
        cache()
    elif a.cmd == "list":
        for k, v in RECIPES.items():
            print(k, v)
    else:
        run(a.recipes or DEFAULT_RUN)


if __name__ == "__main__":
    main()
