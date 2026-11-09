"""Step 4a (the app route). Write every labelled breathing cycle as a WAV clip for Edge Impulse.

    python scripts/export_edge_impulse.py --icbhi "C:\\Users\\Hared\\Downloads\\archive.zip"

Writes export/edge-impulse/<training|testing>/<clip>.wav and export/edge-impulse/info.labels.
info.labels carries each clip's label, its category (training or testing) and its patient, so
Edge Impulse keeps this script's patient split instead of reshuffling. Validation patients go
into Edge Impulse's training category; tell Edge Impulse to split validation on the `patient`
metadata key (see docs/EDGE-IMPULSE-RETRAINING.md).
"""
import argparse
import json
import os
import sys
import zipfile

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from resondi_model import ROOT, load_config
from resondi_model.data import read_manifest
from resondi_model.dsp import load_audio


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--icbhi", required=True)
    a = ap.parse_args()
    cfg = load_config()
    sr = cfg["audio"]["sample_rate"]
    rows = read_manifest(os.path.join(ROOT, "work", "manifest.csv"))
    out = os.path.join(ROOT, "export", "edge-impulse")
    z = zipfile.ZipFile(a.icbhi)
    files, cache_key, x = [], None, None
    for i, r in enumerate(sorted(rows, key=lambda r: r["audio"])):
        if r["audio"] != cache_key:
            cache_key = r["audio"]
            src = z.read(r["audio"][4:]) if r["audio"].startswith("zip:") else os.path.join(ROOT, r["audio"])
            x = load_audio(src, sr)
        seg = x[int(r["start"] * sr):int(r["end"] * sr)]
        if len(seg) == 0:
            continue
        cat = "testing" if r["split"] == "test" else "training"
        name = f"{r['recording']}_{int(r['start'] * 1000):07d}.wav"
        os.makedirs(os.path.join(out, cat), exist_ok=True)
        sf.write(os.path.join(out, cat, name), np.clip(seg, -32768, 32767).astype(np.int16), sr, subtype="PCM_16")
        files.append({"path": f"{cat}/{name}", "category": cat,
                      "label": {"type": "label", "label": r["label"]},
                      "metadata": {"patient": r["patient"], "split": r["split"], "source": r["source"]}})
    with open(os.path.join(out, "info.labels"), "w", encoding="utf-8") as f:
        json.dump({"version": 1, "files": files}, f)
    print(f"{len(files)} clips -> {out}")


if __name__ == "__main__":
    main()
