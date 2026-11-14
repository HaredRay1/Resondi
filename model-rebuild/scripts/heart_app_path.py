"""Check the heart models through the app's audio path, on the CirCor test patients.

The app receives 16 kHz device audio, so it low-passes and decimates to 4 kHz (app/heartFeatures.js)
before the training features. This script is the Python reference of that path:

    CirCor 4 kHz wav -> resample_poly x4 (stand-in for a 16 kHz recording) -> FIR + every 4th sample
    -> training features -> ONNX models -> Viterbi -> heart rate; murmur windows -> mean -> patient max

and compares the result with the training path (features straight from the 4 kHz wav), so that any loss
from the extra resampling is measured. It also writes a fixture of 25 test recordings for the Node parity
check of the browser code (scripts/check_heart_js.mjs).

    python scripts/heart_app_path.py      # -> results/heart-app-path-check.md / .json
"""
import csv
import json
import os
import sys

import numpy as np
import onnxruntime as ort
import soundfile as sf
from scipy.signal import resample_poly

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import heart_data as HD  # noqa: E402
import heart_murmur as HM  # noqa: E402
import heart_seg as HS  # noqa: E402

DEP = os.path.join(ROOT, "deploy", "resondi-heart-v1")
FIX = os.path.join(HD.WORK, "js-fixture")
_C = {}
for line in open(os.path.join(ROOT, "app", "heartConstants.js")):
    if line.startswith("export const"):
        k, v = line[len("export const "):].rstrip(";\n").split(" = ", 1)
        _C[k] = json.loads(v)
FIR = np.array(_C["FIR"])
ADV, THR = _C["ADVANCE"], _C["MURMUR_THRESHOLD"]

SEG = ort.InferenceSession(os.path.join(DEP, "resondi-heart-seg-v1.onnx"), providers=["CPUExecutionProvider"])
MUR = ort.InferenceSession(os.path.join(DEP, "resondi-heart-murmur-v1.onnx"), providers=["CPUExecutionProvider"])


def app_features(x16):
    return HD.features(np.convolve(x16, FIR, "same")[::4])


def run(F):
    f = F.astype(np.float32)
    P = SEG.run(None, {"feats": f[None]})[0][0]
    path = HS.viterbi(P, ADV)
    bpm = HS.bpm_from(HS.onsets(path, 0))
    mur = float(MUR.run(None, {"wins": HM.windows(f)})[0].mean())
    return bpm, mur, len(HS.onsets(path, 0))


def auroc(y, s):
    pos, neg = s[y == 1], s[y == 0]
    return float(((pos[:, None] > neg[None]).sum() + 0.5 * (pos[:, None] == neg[None]).sum()) / (len(pos) * len(neg)))


def main():
    os.makedirs(FIX, exist_ok=True)
    split = json.load(open(os.path.join(HD.WORK, "split.json")))["part"]
    pats = {r["Patient ID"]: r for r in csv.DictReader(open(os.path.join(HD.CIRCOR, "training_data.csv")))}
    tdir = os.path.join(HD.CIRCOR, "training_data")
    names = sorted(f[:-4] for f in os.listdir(tdir) if f.endswith(".wav") and split[f.split("_")[0]] == "test")
    rows, fixture = [], []
    for k, name in enumerate(names):
        x4, sr = sf.read(os.path.join(tdir, name + ".wav"), dtype="float32")
        x16 = resample_poly(x4, 4, 1).astype(np.float32)
        Fo, Fa = HD.features(x4), app_features(x16)
        y = HD.frame_labels(os.path.join(tdir, name + ".tsv"), len(Fa)) if os.path.exists(os.path.join(tdir, name + ".tsv")) else np.zeros(len(Fa), np.int8)
        bo, mo, _ = run(Fo)
        ba, ma, ns1 = run(Fa)
        rows.append(dict(name=name, patient=name.split("_")[0], ref=HS.bpm_from(HS.onsets(y, 1)), bpm_orig=bo, bpm_app=ba,
                         mur_orig=mo, mur_app=ma, frames_orig=len(Fo), frames_app=len(Fa)))
        if k < 25:
            x16.tofile(os.path.join(FIX, f"{k:02d}.f32"))
            Fa.astype(np.float32).tofile(os.path.join(FIX, f"{k:02d}.F.f32"))
            fixture.append(dict(i=k, name=name, n=len(x16), T=len(Fa), bpm=ba, murmur=ma, s1=ns1))
    json.dump(fixture, open(os.path.join(FIX, "fixture.json"), "w"), indent=0)

    def summary(key_b, key_m):
        e = np.array([abs(r[key_b] - r["ref"]) for r in rows if r["ref"] is not None and r[key_b] is not None])
        nores = sum(1 for r in rows if r["ref"] is not None and r[key_b] is None)
        pm = {}
        for r in rows:
            pm[r["patient"]] = max(pm.get(r["patient"], 0.0), r[key_m])
        lab = {p: pats[p]["Murmur"] for p in pm}
        known = [p for p in pm if lab[p] in ("Present", "Absent")]
        yy = np.array([int(lab[p] == "Present") for p in known]); ss = np.array([pm[p] for p in known])
        tp = int(((ss >= THR) & (yy == 1)).sum()); fn = int(((ss < THR) & (yy == 1)).sum())
        tn = int(((ss < THR) & (yy == 0)).sum()); fp = int(((ss >= THR) & (yy == 0)).sum())
        return {"recordings_scored": int(len(e)), "no_estimate": nores, "mae_bpm": float(e.mean()),
                "within5": float((e <= 5).mean()), "murmur": {"tp": tp, "fn": fn, "tn": tn, "fp": fp,
                "sensitivity": tp / (tp + fn), "specificity": tn / (tn + fp), "auroc": auroc(yy, ss)}}

    res = {"training_path": summary("bpm_orig", "mur_orig"), "app_path": summary("bpm_app", "mur_app"),
           "same_frames": int(sum(r["frames_orig"] == r["frames_app"] for r in rows)), "recordings": len(rows),
           "bpm_app_vs_orig_within1": float(np.mean([abs(r["bpm_app"] - r["bpm_orig"]) <= 1 for r in rows
                                                     if r["bpm_app"] is not None and r["bpm_orig"] is not None])),
           "murmur_flag_agreement": float(np.mean([(r["mur_app"] >= THR) == (r["mur_orig"] >= THR) for r in rows]))}
    json.dump(res, open(os.path.join(ROOT, "results", "heart-app-path-check.json"), "w"), indent=1)
    t, a = res["training_path"], res["app_path"]
    md = ["# Heart models through the app's audio path (CirCor test patients, 14 Nov 2026)", "",
          f"{len(rows)} test recordings, each upsampled to 16 kHz (as a device recording would arrive) and then put "
          "through the app's path: FIR low-pass, every 4th sample, the training features, the ONNX models "
          "(`scripts/heart_app_path.py`).", "",
          "| Measure | Training path (4 kHz wav) | App path (16 kHz -> 4 kHz) |", "|---|---|---|",
          f"| Heart rate mean absolute error | {t['mae_bpm']:.2f} BPM | {a['mae_bpm']:.2f} BPM |",
          f"| Within 5 BPM | {100 * t['within5']:.1f}% | {100 * a['within5']:.1f}% |",
          f"| Murmur sensitivity | {100 * t['murmur']['sensitivity']:.1f}% ({t['murmur']['tp']}/{t['murmur']['tp'] + t['murmur']['fn']}) | {100 * a['murmur']['sensitivity']:.1f}% ({a['murmur']['tp']}/{a['murmur']['tp'] + a['murmur']['fn']}) |",
          f"| Murmur specificity | {100 * t['murmur']['specificity']:.1f}% | {100 * a['murmur']['specificity']:.1f}% |",
          f"| Murmur AUROC | {t['murmur']['auroc']:.3f} | {a['murmur']['auroc']:.3f} |", "",
          f"Heart rate within 1 BPM of the training path on {100 * res['bpm_app_vs_orig_within1']:.1f}% of recordings; "
          f"murmur flag the same on {100 * res['murmur_flag_agreement']:.1f}%. The training-path column should equal "
          "results/heart-segmentation.md and heart-murmur.md (all recordings here, including those with fewer than "
          "3 reference S1 onsets for the murmur rows).", "",
          "This checks the software path only. It says nothing about how the models do on the Resondi microphone."]
    open(os.path.join(ROOT, "results", "heart-app-path-check.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
