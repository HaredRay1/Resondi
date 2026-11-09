"""Step 4b (the verification route). Export work/model.pt to ONNX and check it matches PyTorch.

    python scripts/export_onnx.py

Writes export/onnx/resondi-lung-4class.onnx and labels.json. The ONNX model takes MFCC features
(1, 50, 13) and returns probabilities in config label order. It is NOT a drop-in replacement for
the app's Edge Impulse WebAssembly model, which takes raw audio; see docs/EDGE-IMPULSE-RETRAINING.md.
"""
import json
import os
import sys

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from resondi_model import ROOT, load_config
from resondi_model.model import build


class WithSoftmax(torch.nn.Module):
    def __init__(self, m):
        super().__init__()
        self.m = m

    def forward(self, x):
        return torch.softmax(self.m(x), 1)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="model.pt", help="file name in work/")
    a = ap.parse_args()
    cfg = load_config()
    ck = torch.load(os.path.join(ROOT, "work", a.model))
    if "model_cfg" in ck:
        cfg["model"] = ck["model_cfg"]
    model = build(cfg, ck["n_frames"])
    model.load_state_dict(ck["state"])
    model.eval()
    net = WithSoftmax(model).eval()
    out = os.path.join(ROOT, "export", "onnx")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "resondi-lung-4class" + ("" if a.model == "model.pt" else "-" + a.model[:-3]) + ".onnx")
    dummy = torch.zeros(1, ck["n_frames"], cfg["mfcc"]["num_cepstral"])
    torch.onnx.export(net, dummy, path, input_names=["mfcc"], output_names=["probabilities"],
                      dynamic_axes={"mfcc": {0: "batch"}, "probabilities": {0: "batch"}}, dynamo=False)
    with open(os.path.join(out, "labels.json"), "w", encoding="utf-8") as f:
        json.dump({"labels": cfg["labels"], "input": [ck["n_frames"], cfg["mfcc"]["num_cepstral"]],
                   "mfcc": cfg["mfcc"], "audio": cfg["audio"]}, f, indent=1)
    import onnxruntime as ort
    X = np.load(os.path.join(ROOT, "work", "features_test.npz"))["X"][:256]
    a = ort.InferenceSession(path).run(None, {"mfcc": X})[0]
    with torch.no_grad():
        b = net(torch.tensor(X)).numpy()
    diff = float(np.abs(a - b).max())
    assert diff < 1e-4, diff
    print(f"exported {path}; ONNX and PyTorch agree on 256 test windows (max difference {diff:.1e})")


if __name__ == "__main__":
    main()
