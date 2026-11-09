"""Step 3. Evaluate work/model.pt on the held-out test patients (or another partition).

    python scripts/evaluate.py             # test partition
    python scripts/evaluate.py validation

Reports two levels:
  window level: every 1-second window on its own, which is what the app classifies;
  cycle level:  the window probabilities of one breathing cycle averaged, which is how a
                labelled cycle is judged.
Writes results/<partition>-report.txt and .json. Run the test partition once, at the end.
"""
import json
import os
import sys
from datetime import datetime

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from resondi_model import ROOT, load_config
from resondi_model.model import build
from resondi_model.metrics import report, to_text


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("partition", nargs="?", default="test")
    ap.add_argument("--model", default="model.pt", help="file name in work/")
    ap.add_argument("--work", default="work", help="folder with this run's features and model")
    a = ap.parse_args()
    part = a.partition
    cfg = load_config()
    labels = cfg["labels"]
    ck = torch.load(os.path.join(ROOT, a.work, a.model))
    if "model_cfg" in ck:
        cfg["model"] = ck["model_cfg"]
    assert ck["labels"] == labels, "model was trained with a different label order"
    model = build(cfg, ck["n_frames"])
    model.load_state_dict(ck["state"])
    model.eval()
    d = np.load(os.path.join(ROOT, a.work, f"features_{part}.npz"))
    with torch.no_grad():
        prob = torch.softmax(model(torch.tensor(d["X"])), 1).numpy()
    win = report(d["y"], prob.argmax(1), labels)
    cyc_p, cyc_y = {}, {}
    for p, y, c in zip(prob, d["y"], d["cycle"]):
        cyc_p.setdefault(c, []).append(p)
        cyc_y[c] = y
    ids = sorted(cyc_p)
    cyc = report(np.array([cyc_y[i] for i in ids]), np.array([np.mean(cyc_p[i], 0).argmax() for i in ids]), labels)
    suffix = ("" if a.work == "work" else "-" + a.work) + ("" if a.model == "model.pt" else "-" + a.model[:-3])
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    head = (f"Resondi lung sound model, {part} partition, evaluated {stamp}\n"
            f"Run {a.work}, window {ck.get('audio_cfg', cfg['audio'])['window_ms']} ms. Model {a.model}, epoch {ck['epoch']}, filters {cfg['model']['conv_filters']}. Patients in this partition: {len(set(d['patient']))} "
            f"(none of them used in training).\n")
    text = head + "\n" + to_text(win, labels, "Window level (1 s windows)") + "\n\n" + \
        to_text(cyc, labels, "Cycle level (windows of one breathing cycle averaged)") + "\n"
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    with open(os.path.join(ROOT, "results", f"{part}-report{suffix}.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    with open(os.path.join(ROOT, "results", f"{part}-report{suffix}.json"), "w", encoding="utf-8") as f:
        json.dump({"evaluated": stamp, "partition": part, "epoch": ck["epoch"],
                   "patients": len(set(d["patient"])), "window_level": win, "cycle_level": cyc}, f, indent=1)
    print(text)


if __name__ == "__main__":
    main()
