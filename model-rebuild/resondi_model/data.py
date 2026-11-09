"""Read ICBHI 2017 and local recordings into one manifest of labelled breathing cycles.

A manifest row is one breathing cycle: source, patient, recording, start, end, label.
Labels come from each cycle's own crackle and wheeze annotation, never from the patient's
diagnosis. That is the label correction: the old model learned Asthma / Bronchiolitis /
Healthy / Pneumonia from diagnoses applied to every second of a patient's audio.
"""
import csv
import hashlib
import os
import random
import zipfile
from collections import Counter, defaultdict

FIELDS = ["source", "patient", "recording", "audio", "start", "end", "label", "split"]


def label_for(crackles, wheezes, cfg):
    return cfg["label_from_annotation"][f"crackles={int(crackles)},wheezes={int(wheezes)}"]


def icbhi_cycles(zip_path, cfg):
    """Yield manifest rows from the Kaggle ICBHI archive (audio stays inside the zip)."""
    z = zipfile.ZipFile(zip_path)
    names = z.namelist()
    base = next(n for n in names if n.endswith("audio_and_txt_files/") or "/audio_and_txt_files/" in n)
    base = base.split("audio_and_txt_files/")[0] + "audio_and_txt_files/"
    for n in sorted(x for x in names if x.startswith(base) and x.endswith(".txt")):
        rec = n[len(base):-4]
        wav = n[:-4] + ".wav"
        if wav not in names:
            continue
        patient = "icbhi_" + rec.split("_")[0]
        for line in z.read(n).decode("utf-8").splitlines():
            p = line.split()
            if len(p) != 4:
                continue
            yield {"source": "icbhi", "patient": patient, "recording": rec, "audio": "zip:" + wav,
                   "start": float(p[0]), "end": float(p[1]), "label": label_for(p[2], p[3], cfg), "split": ""}


def read_manifest(path):
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["start"], r["end"] = float(r["start"]), float(r["end"])
    return rows


def write_manifest(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in FIELDS})


def device(r):
    """Recording device: the last part of an ICBHI file name (Meditron, LittC2SE, Litt3200, AKGC417L);
    'resondi' for local recordings."""
    return r["recording"].rsplit("_", 1)[-1] if r["source"] == "icbhi" else "resondi"


def split_by_patient(rows, cfg, keep_existing=True):
    """Assign every patient wholly to train, validation or test.

    Patients are shuffled with a fixed seed, then dealt greedily so that each partition gets
    close to its share of every (class, recording device) combination. Balancing devices matters:
    a first split that balanced classes only put 79% of training cycles on one stethoscope, and
    the model learned the microphone instead of the sound. With keep_existing, patients that
    already have a split keep it, so adding local data never moves an ICBHI patient.
    """
    s = cfg["split"]
    by_pat = defaultdict(Counter)
    fixed = {}
    for r in rows:
        by_pat[r["patient"]][(r["label"], device(r))] += 1
        if keep_existing and r.get("split"):
            fixed[r["patient"]] = r["split"]
    parts = ["train", "validation", "test"]
    share = {"train": s["train"], "validation": s["validation"], "test": s["test"]}
    totals = Counter()
    for c in by_pat.values():
        totals.update(c)
    have = {p: Counter() for p in parts}
    for pat, part in fixed.items():
        have[part].update(by_pat[pat])
    pats = sorted(p for p in by_pat if p not in fixed)
    random.Random(s["seed"]).shuffle(pats)
    # Largest patients first so they do not unbalance the small partitions at the end
    pats.sort(key=lambda p: -sum(by_pat[p].values()))
    assign = dict(fixed)
    for pat in pats:
        def deficit(part):
            return sum(max(0.0, share[part] * totals[k] - have[part][k]) / max(totals[k], 1) * n
                       for k, n in by_pat[pat].items())
        part = max(parts, key=deficit)
        assign[pat] = part
        have[part].update(by_pat[pat])
    for r in rows:
        r["split"] = assign[r["patient"]]
    return rows


def audio_hash(data):
    return hashlib.sha1(data).hexdigest()


def summary(rows, labels):
    out = []
    for part in ("train", "validation", "test"):
        sub = [r for r in rows if r["split"] == part]
        c = Counter(r["label"] for r in sub)
        out.append((part, len({r["patient"] for r in sub}), len(sub), [c[l] for l in labels]))
    return out
