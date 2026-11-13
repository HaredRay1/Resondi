"""Heart component, step 1 (14 Nov 2026): CirCor DigiScope 1.0.3 -> patient-wise split and features.

Follows the design written into the IMRaD before any heart model was trained ("Heart Sound Component"):
  - divide CirCor by patient (no patient in more than one partition), as for the lung data;
  - murmur present / absent at the patient level; "Unknown" marks recordings too poor to judge,
    so those patients are kept out of the present/absent classes and reported on their own;
  - S1 and S2 located and timed against the dataset's reference boundaries (the .tsv files).

Split (fixed before any training, seed 20261114): 60% train / 20% validation / 20% test of the
942 patients, stratified by (murmur label, data-collection campaign).

Features, shared by both models: CirCor audio is 4 kHz. Each recording is band-passed 25-1,900 Hz
and levelled to a fixed RMS; a 64 ms Hann
STFT (256 points) at a 20 ms hop gives 50 frames per second; log power, bins 0-2 kHz (129).
Frame labels from the .tsv: 1 S1, 2 systole, 3 S2, 4 diastole, 0 unannotated (ignored).
Resondi device audio (16 kHz) is resampled to 4 kHz before the same features.

    python scripts/heart_data.py      # -> work-exp/heart/{split.json, data.npz}
"""
import csv
import json
import os
import sys
from collections import defaultdict

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfiltfilt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
CIRCOR = os.path.normpath(os.path.join(ROOT, "..", "..", "circor", "the-circor-digiscope-phonocardiogram-dataset-1.0.3"))
WORK = os.path.join(ROOT, "work-exp", "heart")
SR = 4000
HOP = 80            # 20 ms -> 50 frames/s
NFFT = 256          # 64 ms
FPS = SR / HOP
SEED = 20261114


def stft_logpow(x):
    x = np.asarray(x, np.float32)
    pad = NFFT // 2
    xp = np.pad(x, (pad, pad), mode="reflect")
    n = 1 + (len(xp) - NFFT) // HOP
    idx = np.arange(NFFT)[None, :] + HOP * np.arange(n)[:, None]
    win = np.hanning(NFFT + 1)[:-1].astype(np.float32)
    S = np.abs(np.fft.rfft(xp[idx] * win, axis=1)) ** 2
    return np.log(S + 1e-10).astype(np.float32)          # (frames, 129)


_SOS = butter(4, [25, 1900], btype="bandpass", fs=SR, output="sos")


def features(x):
    """x: float audio at 4 kHz -> (frames, 129) log power, per-recording standardised."""
    x = sosfiltfilt(_SOS, x).astype(np.float32)
    x = x / (np.sqrt(np.mean(x ** 2)) + 1e-8) * 0.1
    F = stft_logpow(x)
    return ((F - F.mean(0)) / (F.std(0) + 1e-5)).astype(np.float16)


def frame_labels(tsv, n_frames):
    y = np.zeros(n_frames, np.int8)
    t = np.arange(n_frames) / FPS
    for line in open(tsv):
        a, b, s = line.split()
        a, b, s = float(a), float(b), int(s)
        y[(t >= a) & (t < b)] = s
    return y


def main():
    os.makedirs(WORK, exist_ok=True)
    rows = list(csv.DictReader(open(os.path.join(CIRCOR, "training_data.csv"))))
    pats = {r["Patient ID"]: r for r in rows}
    # split: stratified by (murmur, campaign)
    rng = np.random.default_rng(SEED)
    strata = defaultdict(list)
    for pid, r in pats.items():
        strata[(r["Murmur"], r["Campaign"])].append(pid)
    part = {}
    for key in sorted(strata):
        ids = sorted(strata[key])
        rng.shuffle(ids)
        n = len(ids)
        n_te, n_va = round(0.2 * n), round(0.2 * n)
        for i, pid in enumerate(ids):
            part[pid] = "test" if i < n_te else "validation" if i < n_te + n_va else "train"
    json.dump({"seed": SEED, "part": part}, open(os.path.join(WORK, "split.json"), "w"), indent=0)

    tdir = os.path.join(CIRCOR, "training_data")
    recs = sorted(f[:-4] for f in os.listdir(tdir) if f.endswith(".wav"))
    out = defaultdict(list)
    for name in recs:
        pid, loc = name.split("_")[0], name.split("_")[1]
        r = pats[pid]
        x, sr = sf.read(os.path.join(tdir, name + ".wav"), dtype="float32")
        assert sr == SR, (name, sr)
        F = features(x)
        tsv = os.path.join(tdir, name + ".tsv")
        y = frame_labels(tsv, len(F)) if os.path.exists(tsv) else np.zeros(len(F), np.int8)
        mlocs = set(r["Murmur locations"].split("+")) if r["Murmur"] == "Present" else set()
        out["name"].append(name); out["patient"].append(pid); out["part"].append(part[pid])
        out["loc"].append(loc); out["patient_murmur"].append(r["Murmur"])
        out["rec_murmur"].append(int(loc in mlocs))
        out["sys_timing"].append(r["Systolic murmur timing"]); out["dia_timing"].append(r["Diastolic murmur timing"])
        out["F"].append(F); out["y"].append(y); out["seconds"].append(len(x) / SR)
    obj = {k: np.array(v, dtype=object) if k in ("F", "y") else np.array(v) for k, v in out.items()}
    np.savez(os.path.join(WORK, "data.npz"), **obj)
    n_by = defaultdict(lambda: defaultdict(int))
    for pid, p in part.items():
        n_by[p][pats[pid]["Murmur"]] += 1
    print(f"{len(recs)} recordings, {len(pats)} patients")
    for p in ("train", "validation", "test"):
        nrec = sum(1 for q in out["part"] if q == p)
        print(f"  {p:<10} patients {dict(n_by[p])}  recordings {nrec}")
    lab = np.concatenate(list(obj["y"]))
    print("  annotated frames:", {s: int((lab == s).sum()) for s in range(5)})


if __name__ == "__main__":
    main()
