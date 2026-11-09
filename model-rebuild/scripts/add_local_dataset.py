"""Validate a locally collected dataset and turn it into a manifest the training scripts can use.

    python scripts/add_local_dataset.py data/local

Expected layout (see docs/LOCAL-DATASET-INTEGRATION.md):
    data/local/patients.csv              patient_id, age_group, sex, setting, device, consent_on_file
    data/local/recordings/<patient_id>/<patient_id>_<site>_<YYYYMMDD>_<n>.wav
    data/local/labels.csv                file, start, end, rater1, rater2, final_label

Writes data/local/manifest.csv (only cycles that passed every check) and
data/local/validation-report.txt (everything that was rejected, and why). Nothing is deleted.
"""
import csv
import hashlib
import os
import sys
from collections import Counter, defaultdict

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from resondi_model import ROOT, load_config
from resondi_model.data import write_manifest

SITES = {"Tc", "Al", "Ar", "Pl", "Pr", "Ll", "Lr"}
MIN_SR = 4000
MIN_CYCLE, MAX_CYCLE = 0.3, 10.0
CLIP_LIMIT = 0.01      # more than 1% of samples at full scale = clipped
SILENCE_RMS = 1e-4     # quieter than this throughout = microphone not on the chest


def main():
    folder = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "local"))
    cfg = load_config()
    labels = set(cfg["labels"])
    problems = defaultdict(list)
    pats = {r["patient_id"]: r for r in csv.DictReader(open(os.path.join(folder, "patients.csv"), encoding="utf-8"))}
    for pid, p in pats.items():
        if p.get("consent_on_file", "").strip().lower() != "yes":
            problems["no consent on file (patient excluded)"].append(pid)

    audio_ok, hashes = {}, {}
    rec_dir = os.path.join(folder, "recordings")
    for pid in sorted(os.listdir(rec_dir)):
        for f in sorted(os.listdir(os.path.join(rec_dir, pid))):
            if not f.lower().endswith(".wav"):
                problems["not a WAV file"].append(f"{pid}/{f}")
                continue
            path = os.path.join(rec_dir, pid, f)
            parts = f[:-4].split("_")
            if len(parts) < 4 or parts[0] != pid or parts[1] not in SITES:
                problems["file name does not follow <patient>_<site>_<date>_<n>.wav"].append(f)
                continue
            try:
                x, sr = sf.read(path, dtype="float32", always_2d=True)
            except Exception as e:
                problems["unreadable or corrupted"].append(f"{f}: {e}")
                continue
            x = x.mean(axis=1)
            if sr < MIN_SR:
                problems[f"sample rate below {MIN_SR} Hz"].append(f"{f} ({sr} Hz)")
                continue
            if np.mean(np.abs(x) > 0.999) > CLIP_LIMIT:
                problems["clipped (too loud)"].append(f)
                continue
            if np.sqrt(np.mean(x ** 2)) < SILENCE_RMS:
                problems["silent or nearly silent"].append(f)
                continue
            h = hashlib.sha1(open(path, "rb").read()).hexdigest()
            if h in hashes:
                problems["exact duplicate of another file (second copy ignored)"].append(f"{f} = {hashes[h]}")
                continue
            hashes[h] = f
            audio_ok[f] = (pid, path, len(x) / sr)

    rows, seen, agree = [], set(), Counter()
    for r in csv.DictReader(open(os.path.join(folder, "labels.csv"), encoding="utf-8")):
        f, lab = r["file"], (r.get("final_label") or "").strip()
        if f not in audio_ok:
            problems["label refers to a missing or rejected file"].append(f)
            continue
        pid, path, dur = audio_ok[f]
        if pid not in pats or pats[pid].get("consent_on_file", "").strip().lower() != "yes":
            continue
        try:
            a, b = float(r["start"]), float(r["end"])
        except ValueError:
            problems["start/end not a number"].append(f)
            continue
        if not (0 <= a < b <= dur + 0.05) or not (MIN_CYCLE <= b - a <= MAX_CYCLE):
            problems["cycle times outside the recording or implausible length"].append(f"{f} {a}-{b}")
            continue
        if (f, a) in seen:
            problems["same cycle labelled twice (second ignored)"].append(f"{f} {a}")
            continue
        r1, r2 = (r.get("rater1") or "").strip(), (r.get("rater2") or "").strip()
        if r1 and r2:
            agree["agree" if r1 == r2 else "disagree"] += 1
            if r1 != r2 and not lab:
                problems["raters disagree and no final_label given (excluded until adjudicated)"].append(f"{f} {a}")
                continue
        if lab not in labels:
            problems[f"label not one of {sorted(labels)}"].append(f"{f} {a}: '{lab}'")
            continue
        seen.add((f, a))
        rows.append({"source": "local", "patient": "ph_" + pid, "recording": f[:-4],
                     "audio": os.path.relpath(path, ROOT).replace("\\", "/"),
                     "start": a, "end": b, "label": lab, "split": ""})

    write_manifest(rows, os.path.join(folder, "manifest.csv"))
    c = Counter(r["label"] for r in rows)
    lines = [f"Local dataset check: {folder}",
             f"patients with consent: {sum(1 for p in pats.values() if p.get('consent_on_file','').strip().lower()=='yes')} of {len(pats)}",
             f"recordings accepted: {len(audio_ok)}", f"cycles accepted: {len(rows)}"]
    lines += [f"  {l}: {c[l]}" for l in cfg["labels"]]
    if sum(agree.values()):
        lines.append(f"rater agreement on double-labelled cycles: {agree['agree']}/{sum(agree.values())} "
                     f"({agree['agree'] / sum(agree.values()):.1%})")
    lines.append("")
    for why, items in problems.items():
        lines.append(f"REJECTED - {why}: {len(items)}")
        lines += [f"    {i}" for i in items[:50]]
    text = "\n".join(lines)
    open(os.path.join(folder, "validation-report.txt"), "w", encoding="utf-8").write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
