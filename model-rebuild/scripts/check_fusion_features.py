"""Parity check: the browser feature code (app/fusionFeatures.js, run in Node) against scripts/fusion.py.

Takes N ICBHI validation windows and N SPRSound validation windows, computes the three feature views in
Python and in JavaScript, and runs the exported ONNX ensemble on both. Reports the feature differences
and how often the two give the same top label. Validation data only; the test patients are not read.

    python scripts/check_fusion_features.py [N]
"""
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import fusion as Fu  # noqa: E402

ROOT = os.path.join(HERE, "..")
ONNX = os.path.join(ROOT, "deploy", "resondi-lung-fusion-v2", "resondi-lung-fusion-v2.onnx")
SHAPES = {"mfcc": (50, 13), "spec": (50, 129), "chroma": (47, 12)}


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    import onnxruntime as ort
    sess = ort.InferenceSession(ONNX, providers=["CPUExecutionProvider"])
    out_dir = os.path.join(Fu.EXP, "parity")
    os.makedirs(out_dir, exist_ok=True)
    rng = np.random.default_rng(7)
    lines = []
    for part in ("validation", "sprs_validation"):
        X = np.load(os.path.join(Fu.EXP, f"raw_{part}.npz"))["X"]
        X = X[np.sort(rng.choice(len(X), size=min(n, len(X)), replace=False))]
        Y = Fu.lowpass4k(X)
        py = {v: Fu.FEAT[v](Y).astype(np.float32) for v in Fu.VIEWS}
        raw = os.path.join(out_dir, f"{part}.raw.bin")
        X.astype("<i2").tofile(raw)
        node = subprocess.run(["node", os.path.join(HERE, "check_fusion_features.mjs"), raw,
                               os.path.join(out_dir, part), str(len(X))], capture_output=True, text=True)
        print(node.stdout.strip(), node.stderr.strip())
        js = {v: np.fromfile(os.path.join(out_dir, f"{part}.{v}.bin"), dtype="<f4").reshape(len(X), *SHAPES[v])
              for v in Fu.VIEWS}
        lines.append(f"{part}: {len(X)} windows")
        for v in Fu.VIEWS:
            d = np.abs(py[v] - js[v])
            scale = np.abs(py[v]).max()
            lines.append(f"  {v:<7} max |diff| {d.max():.4g}  mean |diff| {d.mean():.3g}  (values up to {scale:.3g}); "
                         f"exactly equal {np.mean(d == 0):.1%}")
        Pp = sess.run(None, {v: py[v] for v in Fu.VIEWS})[0]
        Pj = sess.run(None, {v: js[v] for v in Fu.VIEWS})[0]
        lines.append(f"  model: top label agrees on {np.mean(Pp.argmax(1) == Pj.argmax(1)):.2%} of windows; "
                     f"max probability difference {np.abs(Pp - Pj).max():.4f}")
    text = "\n".join(lines)
    print(text)
    open(os.path.join(ROOT, "results", "fusion-browser-parity.txt"), "w", encoding="utf-8").write(
        "Browser feature code (app/fusionFeatures.js) vs scripts/fusion.py, validation windows only\n" + text + "\n")


if __name__ == "__main__":
    main()
