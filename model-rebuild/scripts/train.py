"""Step 2. Train the CNN on work/features_train.npz, choosing the epoch with the best validation macro F1.

    python scripts/train.py

Writes work/model.pt and work/training_log.csv. The test partition is not read here.
"""
import csv
import os
import sys

import numpy as np
import torch
from torch import nn

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from resondi_model import ROOT, load_config
from resondi_model.model import build
from resondi_model.metrics import report

WORK = os.path.join(ROOT, "work")


def load(part):
    d = np.load(os.path.join(WORK, f"features_{part}.npz"))
    return torch.tensor(d["X"]), torch.tensor(d["y"])


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", help="alternative config file (default config/config.json)")
    ap.add_argument("--out", default="model.pt", help="file name in work/ for the trained model")
    ap.add_argument("--work", default="work", help="folder with this run's features")
    a = ap.parse_args()
    global WORK
    WORK = os.path.join(ROOT, a.work)
    cfg = load_config(a.config)
    t = cfg["training"]
    torch.manual_seed(t["seed"])
    np.random.seed(t["seed"])
    Xtr, ytr = load("train")
    Xva, yva = load("validation")
    k = len(cfg["labels"])
    counts = torch.bincount(ytr, minlength=k).float()
    weights = counts.sum() / (k * counts) if t["class_weighting"] == "balanced" else torch.ones(k)
    model = build(cfg, Xtr.shape[1])
    opt = torch.optim.Adam(model.parameters(), lr=t["learning_rate"], betas=(t["beta1"], t["beta2"]))
    loss_fn = nn.CrossEntropyLoss(weight=weights)
    best, best_epoch, wait, log = -1.0, 0, 0, []
    for epoch in range(1, t["epochs"] + 1):
        model.train()
        perm = torch.randperm(len(ytr))
        total = 0.0
        for i in range(0, len(perm), t["batch_size"]):
            b = perm[i:i + t["batch_size"]]
            opt.zero_grad()
            loss = loss_fn(model(Xtr[b]), ytr[b])
            loss.backward()
            opt.step()
            total += loss.item() * len(b)
        model.eval()
        with torch.no_grad():
            pred = model(Xva).argmax(1).numpy()
        r = report(yva.numpy(), pred, cfg["labels"])
        log.append((epoch, total / len(ytr), r["accuracy"], r["balanced_accuracy"], r["macro_f1"]))
        print(f"epoch {epoch:>3}  loss {total / len(ytr):.4f}  val acc {r['accuracy']:.3f}  "
              f"val balanced {r['balanced_accuracy']:.3f}  val macro F1 {r['macro_f1']:.3f}")
        if r["macro_f1"] > best:
            best, best_epoch, wait = r["macro_f1"], epoch, 0
            torch.save({"state": model.state_dict(), "n_frames": Xtr.shape[1], "labels": cfg["labels"],
                        "epoch": epoch, "model_cfg": cfg["model"], "audio_cfg": cfg["audio"]}, os.path.join(WORK, a.out))
        else:
            wait += 1
            if wait >= t["early_stopping_patience"]:
                print(f"stopping: no validation improvement for {wait} epochs")
                break
    with open(os.path.join(WORK, a.out[:-3] + "-training-log.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["epoch", "train_loss", "val_accuracy", "val_balanced_accuracy", "val_macro_f1"])
        w.writerows(log)
    print(f"kept epoch {best_epoch} (validation macro F1 {best:.3f}) -> work/{a.out}")


if __name__ == "__main__":
    main()
