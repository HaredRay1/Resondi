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


def feature(view, part):
    """part: train | validation | test | sprs_train | sprs_validation | sprs_test"""
    path = os.path.join(EXP, f"fus_{view}_{part}.npy")
    if not os.path.exists(path):
        raw = os.path.join(EXP, f"raw_{part}.npz")
        X = np.load(raw)["X"]
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
    if data == "icbhi+sprs":
        st = np.load(os.path.join(EXP, "raw_sprs_train.npz"))
        Ftr = [np.concatenate([a, feature(v, "sprs_train")]) for a, v in zip(Ftr, views)]
        ytr = np.concatenate([ytr, st["y"]])
    val = {"icbhi": ([feature(v, "validation") for v in views], va["y"], va["cycle"])}
    if os.path.exists(os.path.join(EXP, "raw_sprs_validation.npz")):
        sv = np.load(os.path.join(EXP, "raw_sprs_validation.npz"))
        val["sprs"] = ([feature(v, "sprs_validation") for v in views], sv["y"], sv["cycle"])
    return Ftr, ytr, val


def standardiser(Ftr):
    import torch
    stats = []
    for F in Ftr:
        mu = np.zeros(F.shape[2], np.float64); sq = np.zeros(F.shape[2], np.float64); n = 0
        for a in range(0, len(F), 4096):
            b = F[a:a + 4096].astype(np.float32)
            mu += b.sum((0, 1)); sq += (b.astype(np.float64) ** 2).sum((0, 1)); n += b.shape[0] * b.shape[1]
        mu /= n
        sd = np.sqrt(np.maximum(sq / n - mu ** 2, 1e-12))
        stats.append((torch.tensor(mu, dtype=torch.float32), torch.tensor(sd, dtype=torch.float32)))
    return lambda xs: [(torch.as_tensor(x, dtype=torch.float32) - m) / s for x, (m, s) in zip(xs, stats)]


def predict(model, prep, Fs):
    import torch
    model.eval()
    out = []
    with torch.no_grad():
        for a in range(0, len(Fs[0]), 1024):
            out.append(torch.softmax(model(prep([F[a:a + 1024].astype(np.float32) for F in Fs])), 1).numpy())
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
    Ftr, ytr, val = load_parts(views, data)
    prep = standardiser(Ftr)
    model = build([(F.shape[1], F.shape[2]) for F in Ftr])
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-3)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
    counts = np.bincount(ytr, minlength=4).astype(np.float32)
    w = torch.tensor(counts.sum() / (4 * counts))
    Y = torch.tensor(ytr)
    Fv, yv, cv = val["icbhi"]
    best, best_state, best_ep, wait = -1, None, 0, 0
    for ep in range(1, epochs + 1):
        model.train()
        perm = np.random.permutation(len(Y))
        for a in range(0, len(perm), 64):
            b = np.sort(perm[a:a + 64])
            out = model(prep([F[b].astype(np.float32) for F in Ftr]))
            loss = torch.nn.functional.cross_entropy(out, Y[b], weight=w)
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
    probs = {k: predict(model, prep, F) for k, (F, _, _) in val.items()}
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
            log_row(name, data, seed, ep, res)
            c = res["icbhi"]["cycle"]
            scores.append(c["balanced_accuracy"])
            extra = f"  sprs-val {res['sprs']['cycle']['balanced_accuracy']:.3f}" if "sprs" in res else ""
            rec = " ".join(f"{p['label'][:4]}={p['recall']:.2f}" for p in c["per_class"])
            print(f"{name:<15} {data:<10} seed {seed}  epoch {ep:>2}  icbhi-val bal {c['balanced_accuracy']:.3f}  "
                  f"F1 {c['macro_f1']:.3f}{extra}  [{rec}]  {time.time() - t0:.0f}s", flush=True)
        if scores:
            summary[name] = (np.mean(scores), np.std(scores))
            print(f"== {name} ({data}): ICBHI validation cycle balanced accuracy {np.mean(scores):.3f} +/- {np.std(scores):.3f}\n", flush=True)
    return summary


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
    tag = f"{name}-{data.replace('+', '-')}"
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
    ap.add_argument("cmd", choices=["sprs", "features", "run", "test"])
    ap.add_argument("recipes", nargs="*")
    ap.add_argument("--data", default="icbhi", choices=["icbhi", "icbhi+sprs"])
    a = ap.parse_args()
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
