"""Step 1. Build the labelled, patient-split manifest and the MFCC feature files.

    python scripts/prepare_data.py --icbhi "C:\\Users\\Hared\\Downloads\\archive.zip"
    python scripts/prepare_data.py --icbhi <zip> --local data/local/manifest.csv   (after add_local_dataset.py)

Writes work/manifest.csv (one row per breathing cycle, with its split) and
work/features_{train,validation,test}.npz.
"""
import argparse
import os
import sys
import zipfile
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from resondi_model import ROOT, load_config
from resondi_model.data import icbhi_cycles, read_manifest, write_manifest, split_by_patient, summary
from resondi_model.dsp import load_audio, windows, MFCC

WORK = os.path.join(ROOT, "work")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--icbhi", required=True, help="ICBHI 2017 zip (Kaggle 'Respiratory Sound Database')")
    ap.add_argument("--local", help="manifest.csv written by add_local_dataset.py")
    ap.add_argument("--config", help="alternative config file")
    ap.add_argument("--work", default="work", help="folder for this run's manifest and features")
    a = ap.parse_args()
    global WORK
    WORK = os.path.join(ROOT, a.work)
    os.makedirs(WORK, exist_ok=True)
    cfg = load_config(a.config)
    labels = cfg["labels"]

    rows = list(icbhi_cycles(a.icbhi, cfg))
    old = os.path.join(WORK, "manifest.csv")
    if os.path.exists(old):  # keep earlier patient assignments so the test set never changes
        prev = {r["patient"]: r["split"] for r in read_manifest(old)}
        for r in rows:
            r["split"] = prev.get(r["patient"], "")
    if a.local:
        local = read_manifest(a.local)
        clash = {r["patient"] for r in local} & {r["patient"] for r in rows if r["source"] == "icbhi"}
        assert not clash, f"local patient IDs collide with ICBHI: {sorted(clash)[:5]}"
        rows += local
    rows = split_by_patient(rows, cfg)
    write_manifest(rows, old)
    for part, pats, n, counts in summary(rows, labels):
        print(f"{part:<11} patients {pats:>4}  cycles {n:>5}  " + "  ".join(f"{l}={c}" for l, c in zip(labels, counts)))

    sr = cfg["audio"]["sample_rate"]
    win = int(sr * cfg["audio"]["window_ms"] / 1000)
    mfcc = MFCC(cfg["mfcc"], sr)
    z = zipfile.ZipFile(a.icbhi)
    by_audio = defaultdict(list)
    for i, r in enumerate(rows):
        by_audio[r["audio"]].append(i)
    out = {p: {"X": [], "y": [], "cycle": [], "patient": []} for p in ("train", "validation", "test")}
    for k, (audio, idx) in enumerate(sorted(by_audio.items())):
        data = z.read(audio[4:]) if audio.startswith("zip:") else os.path.join(ROOT, audio)
        x = load_audio(data, sr)
        for i in idx:
            r = rows[i]
            stride = cfg["audio"]["train_stride_ms" if r["split"] == "train" else "eval_stride_ms"]
            for w in windows(x, r["start"], r["end"], sr, win, int(sr * stride / 1000)):
                o = out[r["split"]]
                o["X"].append(mfcc(w))
                o["y"].append(labels.index(r["label"]))
                o["cycle"].append(i)
                o["patient"].append(r["patient"])
        if k % 100 == 0:
            print(f"  features: {k}/{len(by_audio)} recordings")
    for part, o in out.items():
        np.savez_compressed(os.path.join(WORK, f"features_{part}.npz"), X=np.stack(o["X"]), y=np.array(o["y"]),
                            cycle=np.array(o["cycle"]), patient=np.array(o["patient"]))
        print(f"{part}: {len(o['y'])} one-second windows, feature shape {o['X'][0].shape}")
    # Guard against the original leak: no patient may appear in two partitions
    seen = {p: set(o["patient"]) for p, o in out.items()}
    assert not (seen["train"] & seen["test"]) and not (seen["train"] & seen["validation"]) and not (seen["validation"] & seen["test"])
    print("check passed: no patient appears in more than one partition")


if __name__ == "__main__":
    main()
