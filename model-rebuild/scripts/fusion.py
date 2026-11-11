"""Feature-fusion lung sound model (after Tariq, Shah & Lee 2022, FDC-FS), tested honestly.

Three feature views of the same 1 s window:
  mfcc     13 MFCCs (the app's features)
  spec     log power spectrogram, 0-4 kHz (129 bins, 20 ms frames)
  chroma   12-bin chromagram (pitch-class energy, 50-4000 Hz, 64 ms frames)

Recipes (all scored on the VALIDATION patients; the test patients are not read here):
  single_mfcc / single_spec / single_chroma   one CNN per view
  late3                                       average of the three single models' probabilities
  fdc3                                        FDC-FS style: three CNN branches -> concatenate -> dense
  fdc2_nochroma                               fdc3 without the chroma branch (chroma ablation)

Data: --data icbhi (default) or --data icbhi+sprs (adds SPRSound training patients; see sprs below).

    python scripts/fusion.py sprs                      # once: cut SPRSound into windows (needs Downloads\\sprsound)
    python scripts/fusion.py features                  # once: spec and chroma features for the cached windows
    python scripts/fusion.py run --data icbhi          # all recipes, 3 seeds, validation only
    python scripts/fusion.py run --data icbhi+sprs
    python scripts/fusion.py test <recipe> --data ...  # ONE test run for the chosen recipe; logged

Results: results/fusion-validation.csv, results/final-test-log.csv (shared with final_test.py).
"""
import argparse
import csv
import glob
import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resondi_model import ROOT, load_config
from resondi_model.data import split_by_patient
from resondi_model.dsp import load_audio, windows, MFCC
from resondi_model.metrics import report, to_text
import experiment as E

EXP = E.EXP
SR = 16000
SPRS_DIR = r"C:\Users\Hared\Downloads\sprsound"
SEEDS = (11, 22, 33)
VIEWS = ("mfcc", "spec", "chroma")

# SPRSound event types -> our four sound labels. Rhonchi and Stridor are left out: ICBHI's
# annotation has no stridor, and its "wheeze" flag is not documented as covering rhonchi.
SPRS_MAP = {"Normal": "Healthy", "Fine Crackle": "Crackles", "Coarse Crackle": "Crackles",
            "Wheeze": "Wheezing", "Wheeze+Crackle": "Wheezing with Crackles"}


# ------------------------------------------------------------------ SPRSound
def sprs():
    """Cut SPRSound respiratory events into 1 s windows, split by patient (70/15/15)."""
    cfg = load_config()
    labels = cfg["labels"]
    win = SR
    jsons = sorted(glob.glob(os.path.join(SPRS_DIR, "**", "*.json"), recursive=True))
    wav_index = {os.path.basename(p)[:-4]: p for p in glob.glob(os.path.join(SPRS_DIR, "**", "*.wav"), recursive=True)}
    rows, seen, skipped = [], set(), defaultdict(int)
    for jp in jsons:
        stem = os.path.basename(jp)[:-5]
        if stem in seen or stem not in wav_index:
            continue
        try:
            ann = json.load(open(jp, encoding="utf-8"))
        except (ValueError, UnicodeDecodeError):
            continue
        if not isinstance(ann, dict) or "event_annotation" not in ann:
            continue
        if ann.get("record_annotation") == "Poor Quality":
            skipped["poor quality record"] += 1
            continue
        seen.add(stem)
        patient = "sprs_" + stem.split("_")[0]
        for ev in ann["event_annotation"]:
            lab = SPRS_MAP.get(ev.get("type"))
            if lab is None:
                skipped[ev.get("type")] += 1
                continue
            rows.append({"source": "sprs", "patient": patient, "recording": stem, "audio": wav_index[stem],
                         "start": int(ev["start"]) / 1000.0, "end": int(ev["end"]) / 1000.0, "label": lab, "split": ""})
    split_by_patient(rows, cfg, keep_existing=False)
    out = {p: {"X": [], "y": [], "cycle": [], "patient": []} for p in ("train", "validation", "test")}
    by_audio = defaultdict(list)
    for i, r in enumerate(rows):
        by_audio[r["audio"]].append(i)
    rates = defaultdict(int)
    for k, (audio, idx) in enumerate(sorted(by_audio.items())):
        import soundfile as sf
        rates[sf.info(audio).samplerate] += 1
        x = load_audio(audio, SR)
        for i in idx:
            r = rows[i]
            stride = int(SR * (0.5 if r["split"] == "train" else 1.0))
            for w in windows(x, r["start"], r["end"], SR, win, stride):
                o = out[r["split"]]
                o["X"].append(w.astype(np.int16)); o["y"].append(labels.index(r["label"]))
                o["cycle"].append(i); o["patient"].append(r["patient"])
        if k % 500 == 0:
            print(f"  {k}/{len(by_audio)} recordings", flush=True)
    for p, o in out.items():
        np.savez(os.path.join(EXP, f"raw_sprs_{p}.npz"), X=np.stack(o["X"]), y=np.array(o["y"]),
                 cycle=np.array(o["cycle"]), patient=np.array(o["patient"]))
        c = np.bincount(o["y"], minlength=4)
        print(f"sprs {p}: {len(o['y'])} windows, {len(set(o['patient']))} patients, "
              f"{len(set(o['cycle']))} events, windows per class {dict(zip(labels, c.tolist()))}")
    print("sample rates (recordings):", dict(rates))
    print("skipped:", dict(skipped))
    with open(os.path.join(ROOT, "results", "sprs-summary.json"), "w") as f:
        json.dump({"recordings": len(seen), "events_used": len(rows), "skipped": dict(skipped),
                   "sample_rates": {str(k): v for k, v in rates.items()}}, f, indent=1)


# ------------------------------------------------------------------ features
def _frames(X, flen, hop):
    n = 1 + (X.shape[1] - flen) // hop
    return np.arange(flen)[None, :] + hop * np.arange(n)[:, None]


def spec_feat(X):
    idx = _frames(X, 320, 320)
    w = np.hanning(320).astype(np.float32)
    out = np.empty((len(X), idx.shape[0], 129), np.float16)
    for a in range(0, len(X), 1024):
        fr = (X[a:a + 1024].astype(np.float32) / 32768.0)[:, idx] * w
        p = np.abs(np.fft.rfft(fr, n=512, axis=-1))[..., :129] ** 2           # 0-4 kHz at 31.25 Hz bins
        out[a:a + 1024] = 10 * np.log10(p + 1e-10)
    return out


_CHROMA = None


def chroma_feat(X):
    global _CHROMA
    nfft = 1024
    if _CHROMA is None:
        f = np.fft.rfftfreq(nfft, 1 / SR)
        M = np.zeros((12, len(f)), np.float32)
        ok = (f >= 50) & (f <= 4000)
        pc = np.round(12 * np.log2(f[ok] / 16.352)).astype(int) % 12       # pitch class relative to C0
        M[pc, np.where(ok)[0]] = 1.0
        _CHROMA = M
    idx = _frames(X, nfft, 320)
    w = np.hanning(nfft).astype(np.float32)
    out = np.empty((len(X), idx.shape[0], 12), np.float16)
    for a in range(0, len(X), 512):
        fr = (X[a:a + 512].astype(np.float32) / 32768.0)[:, idx] * w
        p = np.abs(np.fft.rfft(fr, axis=-1)) ** 2
        c = p @ _CHROMA.T
        out[a:a + 512] = c / (c.max(-1, keepdims=True) + 1e-10)                # per-frame normalisation
    return out


def mfcc_feat(X):
    m = MFCC(load_config()["mfcc"], SR)
    return np.stack([m(x.astype(np.float32)) for x in X]).astype(np.float16)


FEAT = {"mfcc": mfcc_feat, "spec": spec_feat, "chroma": chroma_feat}


BANDLIMIT = False   # --bandlimit: cut every window to 0-4 kHz before features (set in main)


TARGET_RMS = 32768 * 10 ** (-20 / 20)   # -20 dBFS


def lowpass4k(X):
    """Harmonise sources: keep exactly 100-3900 Hz, then level every window to -20 dBFS RMS.

    SPRSound is recorded at 8 kHz (nothing above 4 kHz), about 11 dB quieter than ICBHI, and 82% Healthy.
    Trained on ICBHI + SPRSound as is, the MFCC model found 2% of ICBHI's healthy breaths (11 Nov): it had
    learned which dataset a clip came from. Measured on 1,500 windows each, the band above 4.2 kHz sat 35 dB
    apart (73 vs 38 dB) and the 100-2000 Hz band 11 dB apart. A resampling low-pass left a 30 dB gap, so this
    uses an exact cut in the frequency domain (per 1 s window) plus per-window level normalisation."""
    n = X.shape[1]
    f = np.fft.rfftfreq(n, 1 / SR)
    # 100 Hz high-pass too: ICBHI carries strong <100 Hz rumble (heart, handling), so levelling on total RMS
    # left its 100-2000 Hz breath band 16 dB below SPRSound's. Levelling on 100-3900 Hz matches them.
    keep = (f >= 100) & (f <= 3900)
    out = np.empty(X.shape, np.int16)
    for a in range(0, len(X), 1024):
        S = np.fft.rfft(X[a:a + 1024].astype(np.float32), axis=1)
        S[:, ~keep] = 0
        y = np.fft.irfft(S, n=n, axis=1)
        rms = np.sqrt((y ** 2).mean(1, keepdims=True)) + 1e-3
        out[a:a + 1024] = np.clip(y * (TARGET_RMS / rms), -32768, 32767).astype(np.int16)
    return out


def feature(view, part):
    """part: train | validation | test | sprs_train | sprs_validation | sprs_test"""
    pre = "fusbl" if BANDLIMIT else "fus"
    path = os.path.join(EXP, f"{pre}_{view}_{part}.npy")
    if not os.path.exists(path):
        raw = os.path.join(EXP, f"raw_{part}.npz")
        X = np.load(raw)["X"]
        if BANDLIMIT:
            X = lowpass4k(X)
        F = FEAT[view](X)
        np.save(path, F)
        del X
    return np.load(path)


def features():
    for part in ("train", "validation") + tuple(f"sprs_{p}" for p in ("train", "validation")
                                                   if os.path.exists(os.path.join(EXP, f"raw_sprs_{p}.npz"))):
        for v in VIEWS:
            t = time.time()
            F = feature(v, part)
            print(f"{v:<7} {part:<16} {F.shape}  {time.time() - t:.0f}s", flush=True)


# ------------------------------------------------------------------ networks
def branch(n_feat, n_frames):
    from torch import nn
    pooled = -(-(-(-n_frames // 2)) // 2)
    return nn.Sequential(
        nn.Conv1d(n_feat, 32, 3, padding=1), nn.ReLU(), nn.MaxPool1d(2, ceil_mode=True), nn.Dropout(0.25),
        nn.Conv1d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool1d(2, ceil_mode=True), nn.Dropout(0.25),
        nn.Flatten(), nn.Linear(64 * pooled, 64), nn.ReLU())


def build(shapes):
    """shapes: list of (frames, feats) per view. One view = single model; several = FDC-FS fusion."""
    import torch
    from torch import nn

    class Fusion(nn.Module):
        def __init__(self):
            super().__init__()
            self.br = nn.ModuleList([branch(f, t) for t, f in shapes])
            self.head = nn.Sequential(nn.Dropout(0.3), nn.Linear(64 * len(shapes), 4))

        def forward(self, xs):
            return self.head(torch.cat([b(x.transpose(1, 2)) for b, x in zip(self.br, xs)], 1))
    return Fusion()


RECIPES = {
    "single_mfcc": ["mfcc"], "single_spec": ["spec"], "single_chroma": ["chroma"],
    "fdc3": ["mfcc", "spec", "chroma"], "fdc2_nochroma": ["mfcc", "spec"],
    "late3": "late",  # built from the three single models
}


# ------------------------------------------------------------------ data
def load_parts(views, data):
    """Train arrays (ICBHI [+ SPRSound]) and the two validation sets, per view."""
    tr = np.load(os.path.join(EXP, "raw_train.npz"))
    va = np.load(os.path.join(EXP, "raw_validation.npz"))
    Ftr = [feature(v, "train") for v in views]
    ytr = tr["y"]
    src = np.zeros(len(ytr), int)
    if data == "icbhi+sprs":
        st = np.load(os.path.join(EXP, "raw_sprs_train.npz"))
        keep = np.arange(len(st["y"]))
        if BALANCE:
            keep = sprs_balanced_rows(st["y"], st["cycle"], int((ytr == HEALTHY).sum()))
        Ftr = [np.concatenate([a, feature(v, "sprs_train")[keep]]) for a, v in zip(Ftr, views)]
        ytr = np.concatenate([ytr, st["y"][keep]])
        src = np.concatenate([src, np.ones(len(keep), int)])
    val = {"icbhi": ([feature(v, "validation") for v in views], va["y"], va["cycle"])}
    if os.path.exists(os.path.join(EXP, "raw_sprs_validation.npz")):
        sv = np.load(os.path.join(EXP, "raw_sprs_validation.npz"))
        val["sprs"] = ([feature(v, "sprs_validation") for v in views], sv["y"], sv["cycle"])
    return Ftr, ytr, val, src


SRC_ID = {"icbhi": 0, "sprs": 1}
BALANCE = False   # --balance: cap SPRSound's healthy windows at ICBHI's count, and weight sources and classes equally
HEALTHY = 1       # label index of Healthy (alphabetical order)


def sprs_balanced_rows(y, cycle, cap):
    """All SPRSound adventitious windows, plus healthy windows from whole randomly chosen events until `cap`.

    Unbalanced, SPRSound (82% healthy, children) supplied most healthy examples, and the model learned
    "healthy = a child's breath": it found 0-2% of ICBHI's healthy adult breaths (11 Nov). The subset is
    fixed (its own seed), so every recipe and training seed sees the same SPRSound windows."""
    rng = np.random.default_rng(20261111)
    keep = list(np.where(y != HEALTHY)[0])
    h_events = np.unique(cycle[y == HEALTHY])
    rng.shuffle(h_events)
    rows_of = defaultdict(list)
    for i in np.where(y == HEALTHY)[0]:
        rows_of[cycle[i]].append(i)
    n = 0
    for e in h_events:
        if n + len(rows_of[e]) > cap:
            continue
        keep += rows_of[e]
        n += len(rows_of[e])
    return np.sort(np.array(keep))


SRCNORM = False   # --srcnorm: standardise each feature band per data source (ICBHI = 0, SPRSound = 1)


def _band_stats(F, rows):
    mu = np.zeros(F.shape[2], np.float64); sq = np.zeros(F.shape[2], np.float64); n = 0
    for a in range(0, len(rows), 4096):
        b = F[rows[a:a + 4096]].astype(np.float64)
        mu += b.sum((0, 1)); sq += (b ** 2).sum((0, 1)); n += b.shape[0] * b.shape[1]
    mu /= n
    return mu, np.sqrt(np.maximum(sq / n - mu ** 2, 1e-12))


def standardiser(Ftr, src=None):
    """Per-band standardisation fitted on training data. With SRCNORM, one set of statistics per source:
    SPRSound's stethoscope is 16-22 dB duller above 500 Hz than ICBHI's even after band-limiting and levelling,
    so a shared normalisation would let the model tell the datasets apart by tone. prep(xs, g) takes the
    source id(s) g of the batch (int or array)."""
    import torch
    if src is None:
        src = np.zeros(len(Ftr[0]), int)
    groups = sorted(set(src.tolist())) if SRCNORM else [0]
    stats = []
    for F in Ftr:
        mus, sds = [], []
        for g in (groups if SRCNORM else [None]):
            rows = np.arange(len(F)) if g is None else np.where(src == g)[0]
            m, s = _band_stats(F, rows)
            mus.append(m); sds.append(s)
        while len(mus) < 2:                      # unseen source at test time falls back to source 0
            mus.append(mus[0]); sds.append(sds[0])
        stats.append((torch.tensor(np.stack(mus), dtype=torch.float32), torch.tensor(np.stack(sds), dtype=torch.float32)))

    def prep(xs, g=0):
        gi = torch.as_tensor(np.broadcast_to(np.asarray(g if SRCNORM else 0), (len(xs[0]),)).copy(), dtype=torch.long)
        return [(torch.as_tensor(x, dtype=torch.float32) - m[gi][:, None, :]) / s[gi][:, None, :]
                for x, (m, s) in zip(xs, stats)]
    prep.stats = stats            # kept so saved models carry their normalisation
    return prep


def predict(model, prep, Fs, g=0):
    import torch
    model.eval()
    out = []
    with torch.no_grad():
        for a in range(0, len(Fs[0]), 1024):
            out.append(torch.softmax(model(prep([F[a:a + 1024].astype(np.float32) for F in Fs], g)), 1).numpy())
    return np.concatenate(out)


def score(P, y, cyc):
    labels = load_config()["labels"]
    win = report(y, P.argmax(1), labels)
    by = defaultdict(list)
    for p, c in zip(P, cyc):
        by[c].append(p)
    ids = sorted(by)
    cy = dict(zip(cyc, y))
    return {"window": win, "cycle": report(np.array([cy[i] for i in ids]),
                                           np.array([np.mean(by[i], 0).argmax() for i in ids]), labels)}


# ------------------------------------------------------------------ training
def train(views, data, seed, epochs=30, patience=8):
    import torch
    torch.manual_seed(seed); np.random.seed(seed)
    Ftr, ytr, val, src = load_parts(views, data)
    prep = standardiser(Ftr, src)
    model = build([(F.shape[1], F.shape[2]) for F in Ftr])
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-3)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
    counts = np.bincount(ytr, minlength=4).astype(np.float32)
    w = torch.tensor(counts.sum() / (4 * counts))
    Y = torch.tensor(ytr)
    sw = None
    if BALANCE:   # every (source, class) cell carries the same total weight; mean sample weight 1
        cell = src * 4 + ytr
        n_cell = np.bincount(cell, minlength=8).astype(np.float64)
        filled = (n_cell > 0).sum()
        sw = torch.tensor(len(ytr) / (filled * n_cell[cell]), dtype=torch.float32)
    Fv, yv, cv = val["icbhi"]
    best, best_state, best_ep, wait = -1, None, 0, 0
    for ep in range(1, epochs + 1):
        model.train()
        perm = np.random.permutation(len(Y))
        for a in range(0, len(perm), 64):
            b = np.sort(perm[a:a + 64])
            out = model(prep([F[b].astype(np.float32) for F in Ftr], src[b]))
            if sw is None:
                loss = torch.nn.functional.cross_entropy(out, Y[b], weight=w)
            else:
                wb = sw[b]
                loss = (torch.nn.functional.cross_entropy(out, Y[b], reduction="none") * wb).sum() / wb.sum()
            opt.zero_grad(); loss.backward(); opt.step()
        sched.step()
        s = score(predict(model, prep, Fv), yv, cv)["cycle"]["balanced_accuracy"]   # choose on ICBHI validation
        if s > best:
            best, best_ep, wait = s, ep, 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            wait += 1
            if wait >= patience:
                break
    model.load_state_dict(best_state)
    probs = {k: predict(model, prep, F, SRC_ID[k]) for k, (F, _, _) in val.items()}
    return model, prep, best_ep, probs, val


def log_row(name, data, seed, ep, res):
    path = os.path.join(ROOT, "results", "fusion-validation.csv")
    new = not os.path.exists(path)
    labels = load_config()["labels"]
    with open(path, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["time", "recipe", "data", "seed", "epoch", "val_set", "cycle_balanced_acc", "cycle_macro_f1",
                        "window_balanced_acc"] + [f"recall_{l}" for l in labels])
        for vs, r in res.items():
            c = r["cycle"]
            w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), name, data, seed, ep, vs,
                        f"{c['balanced_accuracy']:.4f}", f"{c['macro_f1']:.4f}", f"{r['window']['balanced_accuracy']:.4f}"]
                       + [f"{p['recall']:.4f}" for p in c["per_class"]])


def run(data, names):
    import torch
    torch.set_num_threads(os.cpu_count() or 4)
    names = names or ["single_mfcc", "single_spec", "single_chroma", "late3", "fdc3", "fdc2_nochroma"]
    single_probs = defaultdict(dict)     # seed -> view -> probs per val set
    vals = None
    summary = {}
    for name in names:
        scores = []
        for seed in SEEDS:
            t0 = time.time()
            if name == "late3":
                if not all(v in single_probs[seed] for v in VIEWS):
                    print("late3 needs single_mfcc, single_spec and single_chroma in the same run; skipped")
                    break
                res = {vs: score(np.mean([single_probs[seed][v][vs] for v in VIEWS], 0), vals[vs][1], vals[vs][2])
                       for vs in vals}
                ep = 0
            else:
                views = RECIPES[name]
                _, _, ep, probs, vals = train(views, data, seed)
                if len(views) == 1:
                    single_probs[seed][views[0]] = probs
                res = {vs: score(probs[vs], vals[vs][1], vals[vs][2]) for vs in probs}
            log_row(name, data + ("-bl4k" if BANDLIMIT else "") + ("-srcnorm" if SRCNORM else "") + ("-bal" if BALANCE else ""), seed, ep, res)
            c = res["icbhi"]["cycle"]
            scores.append(c["balanced_accuracy"])
            extra = f"  sprs-val {res['sprs']['cycle']['balanced_accuracy']:.3f}" if "sprs" in res else ""
            rec = " ".join(f"{p['label'][:4]}={p['recall']:.2f}" for p in c["per_class"])
            print(f"{name:<15} {data + ('-bl4k' if BANDLIMIT else '') + ('-sn' if SRCNORM else '') + ('-bal' if BALANCE else ''):<23} seed {seed}  epoch {ep:>2}  icbhi-val bal {c['balanced_accuracy']:.3f}  "
                  f"F1 {c['macro_f1']:.3f}{extra}  [{rec}]  {time.time() - t0:.0f}s", flush=True)
        if scores:
            summary[name] = (np.mean(scores), np.std(scores))
            print(f"== {name} ({data}{'-bl4k' if BANDLIMIT else ''}{'-srcnorm' if SRCNORM else ''}{'-bal' if BALANCE else ''}): ICBHI validation cycle balanced accuracy {np.mean(scores):.3f} +/- {np.std(scores):.3f}\n", flush=True)
    return summary


# ------------------------------------------------------------------ saved checkpoint of the ICBHI-only models
SAVE_DIR = os.path.join(ROOT, "models", "fusion-icbhi-only-2026-11-11")
# The runs that scored best on ICBHI validation in the ICBHI-only round (results/fusion-validation.csv, data=icbhi).
# late3 = the three seed-11 single models averaged, so those are saved as well.
SAVE_RUNS = [("single_mfcc", 22), ("single_mfcc", 11), ("single_spec", 11), ("single_chroma", 33),
             ("single_chroma", 11), ("fdc3", 11), ("fdc2_nochroma", 11)]


def save_icbhi_models():
    """Retrain the chosen ICBHI-only runs (same seeds, same code path) and save each model with its
    normalisation, so this state can be restored later without SPRSound. Each run's validation score is
    compared with the score logged this morning; a mismatch is reported, not hidden."""
    import torch
    assert not (BANDLIMIT or SRCNORM or BALANCE), "the checkpoint is the plain ICBHI-only setup"
    torch.set_num_threads(os.cpu_count() or 4)
    os.makedirs(SAVE_DIR, exist_ok=True)
    logged = {}
    with open(os.path.join(ROOT, "results", "fusion-validation.csv")) as f:
        for r in csv.DictReader(f):
            if r["data"] == "icbhi" and r["val_set"] == "icbhi":
                logged[(r["recipe"], int(r["seed"]))] = float(r["cycle_balanced_acc"])
    manifest = []
    for name, seed in SAVE_RUNS:
        t0 = time.time()
        views = RECIPES[name]
        model, prep, ep, probs, vals = train(list(views), "icbhi", seed)
        s = score(probs["icbhi"], vals["icbhi"][1], vals["icbhi"][2])["cycle"]
        was = logged.get((name, seed))
        path = os.path.join(SAVE_DIR, f"{name}_seed{seed}.pt")
        torch.save({"state_dict": model.state_dict(), "views": list(views),
                    "shapes": [(F.shape[1], F.shape[2]) for F in vals["icbhi"][0]],
                    "norm_mean": [m[0].numpy() for m, _ in prep.stats], "norm_std": [sd[0].numpy() for _, sd in prep.stats],
                    "labels": load_config()["labels"], "seed": seed, "epoch": ep,
                    "val_cycle_balanced_acc": s["balanced_accuracy"], "data": "icbhi",
                    "features": "1 s at 16 kHz; mfcc = config.json MFCC; spec = log power 0-4 kHz, 320-sample "
                                "frames/hop, 512-pt FFT, 129 bins; chroma = 12 bins 50-4000 Hz, 1024-pt frames, 320 hop"},
                   path)
        manifest.append({"file": os.path.basename(path), "recipe": name, "seed": seed, "epoch": ep,
                         "val_cycle_balanced_acc": round(s["balanced_accuracy"], 4),
                         "logged_this_morning": was, "reproduced": was is not None and abs(was - s["balanced_accuracy"]) < 0.005})
        print(f"saved {name} seed {seed}: epoch {ep}, validation {s['balanced_accuracy']:.3f} "
              f"(logged {was if was is None else f'{was:.3f}'})  {time.time() - t0:.0f}s", flush=True)
    json.dump({"created": datetime.now().strftime("%Y-%m-%d %H:%M"), "training_data": "ICBHI 2017 only (65 train patients)",
               "chosen_on": "30 ICBHI validation patients", "late3": "average the probabilities of single_mfcc_seed11, "
               "single_spec_seed11 and single_chroma_seed11", "runs": manifest},
              open(os.path.join(SAVE_DIR, "manifest.json"), "w"), indent=1)
    print("checkpoint written to", SAVE_DIR)


# ------------------------------------------------------------------ the one test run
def test(name, data):
    import torch
    torch.set_num_threads(os.cpu_count() or 4)
    log_path = os.path.join(ROOT, "results", "final-test-log.csv")
    if os.path.exists(log_path):
        print("NOTE: earlier test runs are logged in results/final-test-log.csv; report all of them.")
    sys.argv = [sys.argv[0]]
    import final_test as FT
    FT.test_windows()                                         # ICBHI test windows (cached)
    views = VIEWS if name == "late3" else RECIPES[name]
    best = None
    models = {}
    for seed in SEEDS:
        if name == "late3":
            ps, parts = [], []
            for v in VIEWS:
                m, prep, ep, probs, vals = train([v], data, seed)
                parts.append((m, prep)); ps.append(probs["icbhi"])
            P = np.mean(ps, 0)
            s = score(P, vals["icbhi"][1], vals["icbhi"][2])["cycle"]["balanced_accuracy"]
            obj = parts
        else:
            m, prep, ep, probs, vals = train(list(views), data, seed)
            s = score(probs["icbhi"], vals["icbhi"][1], vals["icbhi"][2])["cycle"]["balanced_accuracy"]
            obj = (m, prep)
        print(f"seed {seed}: validation {s:.3f}")
        if best is None or s > best[0]:
            best = (s, seed, obj)
    s, seed, obj = best
    print(f"chosen on validation: seed {seed} ({s:.3f}). Reading the test patients once.")
    labels = load_config()["labels"]
    tests = {"icbhi": "test"}
    if os.path.exists(os.path.join(EXP, "raw_sprs_test.npz")):
        tests["sprs"] = "sprs_test"
    text = [f"Resondi fusion model, TEST partitions, evaluated {datetime.now():%Y-%m-%d %H:%M}",
            f"Recipe {name} ({', '.join(views)}), training data {data}, seed {seed} chosen on ICBHI validation ({s:.3f})."]
    out = {}
    for key, part in tests.items():
        raw = np.load(os.path.join(EXP, f"raw_{part}.npz"))
        if name == "late3":
            P = np.mean([predict(m, prep, [feature(v, part)]) for (m, prep), v in zip(obj, VIEWS)], 0)
        else:
            m, prep = obj
            P = predict(m, prep, [feature(v, part) for v in views])
        r = score(P, raw["y"], raw["cycle"])
        out[key] = r
        text.append(f"\n### {key.upper()} test: {len(set(raw['patient']))} patients\n")
        text.append(to_text(r["cycle"], labels, "Cycle level (windows of one breathing cycle / event averaged)"))
    text = "\n".join(text)
    tag = f"{name}-{data.replace('+', '-')}" + ("-bl4k" if BANDLIMIT else "") + ("-srcnorm" if SRCNORM else "") + ("-bal" if BALANCE else "")
    open(os.path.join(ROOT, "results", f"final-test-fusion-{tag}.txt"), "w", encoding="utf-8").write(text)
    json.dump({"recipe": name, "data": data, "seed": seed, "val": s, "test": out},
              open(os.path.join(ROOT, "results", f"final-test-fusion-{tag}.json"), "w"), indent=1)
    new = not os.path.exists(log_path)
    with open(log_path, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["time", "recipe", "seed", "epoch", "val_cycle_balanced_acc", "test_cycle_balanced_acc",
                        "test_cycle_macro_f1", "test_window_balanced_acc"])
        c = out["icbhi"]["cycle"]
        w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), f"fusion:{tag}", seed, "", f"{s:.4f}",
                    f"{c['balanced_accuracy']:.4f}", f"{c['macro_f1']:.4f}", f"{out['icbhi']['window']['balanced_accuracy']:.4f}"])
    print(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["sprs", "features", "run", "test", "save"])
    ap.add_argument("recipes", nargs="*")
    ap.add_argument("--data", default="icbhi", choices=["icbhi", "icbhi+sprs"])
    ap.add_argument("--bandlimit", action="store_true", help="cut all audio to 0-4 kHz before features")
    ap.add_argument("--srcnorm", action="store_true", help="standardise features per data source")
    ap.add_argument("--balance", action="store_true", help="cap SPRSound healthy windows; weight sources and classes equally")
    ap.add_argument("--seeds", default="11,22,33", help="comma-separated training seeds (a quick gate check can use one)")
    a = ap.parse_args()
    global BANDLIMIT, SRCNORM, BALANCE, SEEDS
    BANDLIMIT, SRCNORM, BALANCE = a.bandlimit, a.srcnorm, a.balance
    SEEDS = tuple(int(s) for s in a.seeds.split(","))
    if a.cmd == "save":
        save_icbhi_models()
        return
    if a.cmd == "sprs":
        sprs()
    elif a.cmd == "features":
        features()
    elif a.cmd == "run":
        run(a.data, a.recipes)
    else:
        test(a.recipes[0], a.data)


if __name__ == "__main__":
    main()
