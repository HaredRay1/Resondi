"""Score ONE chosen recipe on the held-out test patients. Run this once, after choosing on validation.

    python scripts/final_test.py mfe2k_2d_aug

It trains the recipe with the same three seeds used in experiment.py, keeps the seed with the best
VALIDATION score (the test patients play no part in that choice), and only then reads the test
patients and scores that one model. The result is written to results/final-test-<recipe>.txt/.json,
and every run is logged in results/final-test-log.csv. If that log already lists earlier runs, the
script says so: picking whichever of several test runs scored best would leak the test set into the
choice, so report every run listed there.

The trained model is saved to work-exp/final-<recipe>.pt for export.
"""
import csv
import json
import os
import sys
import zipfile
from collections import defaultdict
from datetime import datetime

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resondi_model import ROOT, load_config
from resondi_model.data import read_manifest
from resondi_model.dsp import load_audio, windows, MFCC
from resondi_model.metrics import to_text
import experiment as E


def test_windows():
    """Cut the test patients' cycles into 1 s windows (eval stride), the same way as validation."""
    path = os.path.join(E.EXP, "raw_test.npz")
    if os.path.exists(path):
        return np.load(path)
    cfg = load_config()
    sr = cfg["audio"]["sample_rate"]
    win = int(sr * cfg["audio"]["window_ms"] / 1000)
    stride = int(sr * cfg["audio"]["eval_stride_ms"] / 1000)
    rows = [r for r in read_manifest(os.path.join(ROOT, "work", "manifest.csv")) if r["split"] == "test"]
    z = zipfile.ZipFile(E.ICBHI)
    by_audio = defaultdict(list)
    for i, r in enumerate(rows):
        by_audio[r["audio"]].append(i)
    X, y, cyc, pat = [], [], [], []
    for audio, idx in sorted(by_audio.items()):
        x = load_audio(z.read(audio[4:]), sr)
        for i in idx:
            for w in windows(x, rows[i]["start"], rows[i]["end"], sr, win, stride):
                X.append(w.astype(np.int16)); y.append(cfg["labels"].index(rows[i]["label"])); cyc.append(i); pat.append(rows[i]["patient"])
    np.savez(path, X=np.stack(X), y=np.array(y), cycle=np.array(cyc), patient=np.array(pat))
    return np.load(path)


def test_features(name, raw):
    cfg = load_config()
    sr = cfg["audio"]["sample_rate"]
    if name == "mfcc13":
        m = MFCC(cfg["mfcc"], sr)
        return np.stack([m(x.astype(np.float32)) for x in raw]).astype(np.float32)
    if name == "mfe40":
        return E.log_mel_db(raw, sr, 40, 0, None)
    if name == "mfe40_2k":
        return E.log_mel_db(raw, sr, 40, 50, 2000)
    raise ValueError(name)


def main():
    import torch
    if len(sys.argv) != 2 or sys.argv[1] not in E.RECIPES:
        sys.exit(f"usage: python scripts/final_test.py <recipe>, one of: {', '.join(E.RECIPES)}")
    name = sys.argv[1]
    rec = E.RECIPES[name]
    log_path = os.path.join(ROOT, "results", "final-test-log.csv")
    if os.path.exists(log_path):
        with open(log_path) as f:
            earlier = list(csv.DictReader(f))
        if earlier:
            print(f"NOTE: {len(earlier)} earlier test run(s) are logged in results/final-test-log.csv. "
                  "Report all of them, not only the best.")
    torch.set_num_threads(os.cpu_count() or 4)

    tr = np.load(os.path.join(E.EXP, "raw_train.npz"))
    va = np.load(os.path.join(E.EXP, "raw_validation.npz"))
    Ftr, Fva = E.features(rec["feature"], "train"), E.features(rec["feature"], "validation")
    best = None
    for seed in E.SEEDS:
        model, prep, r, ep = E.train_one(rec, seed, Ftr, tr["y"], Fva, va["y"], va["cycle"], quiet=True)
        v = r["cycle"]["balanced_accuracy"]
        print(f"seed {seed}: epoch {ep}, validation cycle balanced accuracy {v:.3f}")
        if best is None or v > best[0]:
            best = (v, seed, ep, model, prep, r)
    v, seed, ep, model, prep, rval = best
    print(f"chosen on validation: seed {seed} (validation {v:.3f}). Now reading the test patients, once.")

    te = test_windows()
    Fte = torch.tensor(test_features(rec["feature"], te["X"]))
    r = E.evaluate(model, prep, rec["head"], Fte, te["y"], te["cycle"])
    labels = load_config()["labels"]
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    head = (f"Resondi lung sound model, TEST partition, evaluated {stamp}\n"
            f"Recipe {name}: {rec}. Seed {seed}, epoch {ep}, chosen on validation (cycle balanced accuracy {v:.3f}).\n"
            f"Test patients: {len(set(te['patient']))}, none used in training or in choosing the recipe, seed or epoch.\n")
    text = head + "\n" + to_text(r["window"], labels, "Window level (1 s windows)") + "\n\n" + \
        to_text(r["cycle"], labels, "Cycle level (windows of one breathing cycle averaged)") + "\n"
    with open(os.path.join(ROOT, "results", f"final-test-{name}.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    with open(os.path.join(ROOT, "results", f"final-test-{name}.json"), "w", encoding="utf-8") as f:
        json.dump({"evaluated": stamp, "recipe": name, "settings": rec, "seed": seed, "epoch": ep,
                   "validation": rval, "test": r}, f, indent=1)
    new = not os.path.exists(log_path)
    with open(log_path, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["time", "recipe", "seed", "epoch", "val_cycle_balanced_acc", "test_cycle_balanced_acc",
                        "test_cycle_macro_f1", "test_window_balanced_acc"])
        w.writerow([stamp, name, seed, ep, f"{v:.4f}", f"{r['cycle']['balanced_accuracy']:.4f}",
                    f"{r['cycle']['macro_f1']:.4f}", f"{r['window']['balanced_accuracy']:.4f}"])
    torch.save({"state": model.state_dict(), "recipe": rec, "labels": labels, "seed": seed, "epoch": ep},
               os.path.join(E.EXP, f"final-{name}.pt"))
    print(text)


if __name__ == "__main__":
    main()
