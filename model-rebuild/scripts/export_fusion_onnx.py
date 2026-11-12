"""Export the FDC-FS fusion ensemble (ICBHI + SPRSound, seeds 11/22/33) to one ONNX file for the app.

The graph takes the three raw feature views of a batch of 1 s windows and returns the four class
probabilities, averaged over the three seeds:

    inputs   mfcc   [N, 50, 13]   spec [N, 50, 129]   chroma [N, 47, 12]   (float32)
    output   probs  [N, 4]        Crackles, Healthy, Wheezing, Wheezing with Crackles

Normalisation is built in, using the ICBHI (source 0) statistics, the same ones used to score the
ICBHI test patients and the cross-validation folds. Features are computed in the browser by
app/fusionFeatures.js, which reproduces scripts/fusion.py (lowpass4k, mfcc_feat, spec_feat, chroma_feat).

    python scripts/export_fusion_onnx.py
"""
import json
import os
import sys

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import fusion as Fu  # noqa: E402

SRC = os.path.join(HERE, "..", "models", "fusion-icbhi-sprs-2026-11-11")
OUT = os.path.join(HERE, "..", "deploy", "resondi-lung-fusion-v2")
SEEDS = (11, 22, 33)


class Ensemble(torch.nn.Module):
    def __init__(self, ckpts):
        super().__init__()
        self.models = torch.nn.ModuleList()
        means, stds = [], []
        for c in ckpts:
            m = Fu.build([tuple(s) for s in c["shapes"]])
            m.load_state_dict(c["state_dict"])
            m.eval()
            self.models.append(m)
            means.append([torch.tensor(np.asarray(a)[0], dtype=torch.float32) for a in c["norm_mean"]])
            stds.append([torch.tensor(np.asarray(a)[0], dtype=torch.float32) for a in c["norm_std"]])
        for i, (ms, ss) in enumerate(zip(means, stds)):
            for v, (mu, sd) in enumerate(zip(ms, ss)):
                self.register_buffer(f"mu_{i}_{v}", mu)
                self.register_buffer(f"sd_{i}_{v}", sd)

    def forward(self, mfcc, spec, chroma):
        xs = (mfcc, spec, chroma)
        probs = []
        for i, m in enumerate(self.models):
            z = [(x - getattr(self, f"mu_{i}_{v}")) / getattr(self, f"sd_{i}_{v}") for v, x in enumerate(xs)]
            probs.append(torch.softmax(m(z), dim=1))
        return torch.stack(probs, 0).mean(0)


def main():
    ckpts = [torch.load(os.path.join(SRC, f"fdc3_seed{s}.pt"), weights_only=False) for s in SEEDS]
    for c in ckpts:
        assert c["views"] == ["mfcc", "spec", "chroma"] and c["srcnorm"] and c["bandlimit_100_3900_levelled"]
        assert [tuple(s) for s in c["shapes"]] == [(50, 13), (50, 129), (47, 12)]
    model = Ensemble(ckpts).eval()
    os.makedirs(OUT, exist_ok=True)
    dummy = (torch.zeros(2, 50, 13), torch.zeros(2, 50, 129), torch.zeros(2, 47, 12))
    path = os.path.join(OUT, "resondi-lung-fusion-v2.onnx")
    torch.onnx.export(model, dummy, path, input_names=["mfcc", "spec", "chroma"], output_names=["probs"],
                      dynamic_axes={"mfcc": {0: "n"}, "spec": {0: "n"}, "chroma": {0: "n"}, "probs": {0: "n"}},
                      opset_version=17, dynamo=False)

    # Check the ONNX graph against PyTorch on real validation features.
    import onnxruntime as ort
    Fu.BANDLIMIT = True
    F = [Fu.feature(v, "validation")[:512].astype(np.float32) for v in Fu.VIEWS]
    with torch.no_grad():
        ref = model(*[torch.tensor(f) for f in F]).numpy()
    sess = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
    got = sess.run(None, {"mfcc": F[0], "spec": F[1], "chroma": F[2]})[0]
    diff = float(np.abs(ref - got).max())
    agree = float((ref.argmax(1) == got.argmax(1)).mean())
    print(f"ONNX vs PyTorch on 512 validation windows: max |diff| {diff:.2e}, top-label agreement {agree:.4f}")
    assert diff < 1e-4 and agree == 1.0

    meta = {"model_version": "resondi-lung-fusion-v2", "file": os.path.basename(path),
            "labels": ckpts[0]["labels"], "inputs": {"mfcc": [50, 13], "spec": [50, 129], "chroma": [47, 12]},
            "ensemble": [f"fdc3_seed{s}.pt" for s in SEEDS], "training_data": "ICBHI 2017 (65 train patients) + "
            "SPRSound (rebalanced)", "normalisation": "ICBHI (source 0) statistics, built into the graph",
            "preprocessing": "1 s windows at 16 kHz, int16 scale; exact 100-3900 Hz band cut and -20 dBFS RMS "
            "levelling per window; features as in scripts/fusion.py, rounded to float16",
            "evaluation": "5-fold patient CV on all 126 ICBHI patients: 40.0% balanced accuracy (95% CI 35.9-43.5), "
            "children 56.3% (results/cv-results.md). Not tested on Resondi device audio.",
            "onnx_vs_pytorch_max_abs_diff": diff, "bytes": os.path.getsize(path)}
    json.dump(meta, open(os.path.join(OUT, "model.json"), "w"), indent=1)
    print("wrote", path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()
