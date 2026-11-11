"""ONE test run for the ICBHI + SPRSound fusion round, from the SAVED models (no retraining).

Primary (pre-specified in results/prespec-icbhi-sprs-round.md, 11 Nov 23:45, before any test read): fdc3 seed 33.
The other versions are scored with their best-ICBHI-validation seed, for comparison only.

    python scripts/test_saved.py

Writes results/final-test-icbhi-sprs.md and .json, and appends to results/final-test-log.csv.
"""
import csv
import json
import os
import sys
from datetime import datetime

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resondi_model import ROOT, load_config
from resondi_model.metrics import to_text
import fusion as Fu

MODELS = os.path.join(ROOT, "models", "fusion-icbhi-sprs-2026-11-11")
PRIMARY = ("fdc3", 33)
COMPARE = [("fdc3", 33), ("late3", 22), ("fdc2_nochroma", 11), ("single_spec", 33),
           ("single_mfcc", 22), ("single_chroma", 33)]
TESTS = {"icbhi": ("test", 0), "sprs": ("sprs_test", 1)}   # part, normalisation source


def load(name, seed):
    import torch
    ck = torch.load(os.path.join(MODELS, f"{name}_seed{seed}.pt"), weights_only=False)
    model = Fu.build([tuple(s) for s in ck["shapes"]])
    model.load_state_dict(ck["state_dict"])
    stats = [(torch.tensor(m, dtype=torch.float32), torch.tensor(s, dtype=torch.float32))
             for m, s in zip(ck["norm_mean"], ck["norm_std"])]

    def prep(xs, g=0):
        return [(torch.as_tensor(x, dtype=torch.float32) - m[g][None, None, :]) / s[g][None, None, :]
                for x, (m, s) in zip(xs, stats)]
    return model, prep, ck["views"]


def probs(name, seed, part, g):
    if name == "late3":   # average of the three single models of that seed
        return np.mean([probs(f"single_{v}", seed, part, g) for v in Fu.VIEWS], 0)
    model, prep, views = load(name, seed)
    return Fu.predict(model, prep, [Fu.feature(v, part) for v in views], g)


def main():
    import torch
    torch.set_num_threads(os.cpu_count() or 4)
    Fu.BANDLIMIT = True                      # the round's features: 0.1-3.9 kHz, levelled
    import final_test as FT
    FT.test_windows()                        # ICBHI test windows (cached)
    labels = load_config()["labels"]
    out, lines = {}, []
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    for key, (part, g) in TESTS.items():
        raw = np.load(os.path.join(Fu.EXP, f"raw_{part}.npz"))
        out[key] = {}
        for name, seed in COMPARE:
            r = Fu.score(probs(name, seed, part, g), raw["y"], raw["cycle"])
            out[key][f"{name}_seed{seed}"] = r
            c = r["cycle"]
            tag = " (PRIMARY)" if (name, seed) == PRIMARY else ""
            lines.append(f"{key:<6} {name + tag:<24} seed {seed}  balanced {c['balanced_accuracy']:.3f}  "
                         f"F1 {c['macro_f1']:.3f}  " + " ".join(f"{p['label'][:4]}={p['recall']:.2f}" for p in c["per_class"]))
            print(lines[-1], flush=True)
    text = [f"# ICBHI + SPRSound fusion round: test results ({stamp})", "",
            "Primary, pre-specified before any test read: **fdc3 seed 33** (results/prespec-icbhi-sprs-round.md).",
            "Scored from the saved models, without retraining. Other rows are for comparison only.", ""]
    for key, (part, _) in TESTS.items():
        raw = np.load(os.path.join(Fu.EXP, f"raw_{part}.npz"))
        text.append(f"## {key.upper()} test: {len(set(raw['patient']))} patients, {len(set(raw['cycle']))} cycles/events\n")
        text.append(to_text(out[key][f"{PRIMARY[0]}_seed{PRIMARY[1]}"]["cycle"], labels, "PRIMARY fdc3 seed 33, cycle level"))
        text.append("")
    text.append("## All versions\n\n```\n" + "\n".join(lines) + "\n```")
    open(os.path.join(ROOT, "results", "final-test-icbhi-sprs.md"), "w", encoding="utf-8").write("\n".join(text))
    json.dump({"evaluated": stamp, "primary": f"{PRIMARY[0]}_seed{PRIMARY[1]}", "results": out},
              open(os.path.join(ROOT, "results", "final-test-icbhi-sprs.json"), "w"), indent=1)
    with open(os.path.join(ROOT, "results", "final-test-log.csv"), "a", newline="") as f:
        w = csv.writer(f)
        for name, seed in COMPARE:
            r = out["icbhi"][f"{name}_seed{seed}"]
            tag = " (PRIMARY)" if (name, seed) == PRIMARY else ""
            w.writerow([stamp, f"icbhi+sprs:{name}{tag}", seed, "", "", f"{r['cycle']['balanced_accuracy']:.4f}",
                        f"{r['cycle']['macro_f1']:.4f}", f"{r['window']['balanced_accuracy']:.4f}"])
    print("wrote results/final-test-icbhi-sprs.md")


if __name__ == "__main__":
    main()
