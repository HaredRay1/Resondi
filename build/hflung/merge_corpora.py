"""Merge ICBHI 2017 and HF_Lung_V1 into one Edge Impulse upload set.

Design rules, in order of importance:

1. PATIENTS ARE PARTITIONED BEFORE ANY AUDIO IS OPENED. Same rule as
   rebuild_dataset.py. Windowing inside a partition, never across one.

2. THE TEST PARTITION IS ICBHI PATIENTS ONLY, AND IT NEVER CHANGES.
   The ablation compares runs trained on different corpora. If the test set
   changes with the training set, no two runs are comparable. ICBHI is the
   only corpus present in every run, so it holds the test set.

3. HF_Lung_V1 GOES ENTIRELY INTO TRAINING, except a held-out block of its own
   patients kept as a SECOND, separately reported test set. That gives an
   East Asian generalisation figure without touching the primary comparison.

4. PATIENT IDS ARE NAMESPACED. ICBHI numbers its patients 101-226; HF_Lung_V1
   numbers its own from 1. Un-namespaced, two different people collide into
   one group and the split silently leaks again.

Usage:
    python merge_corpora.py --inspect  /path/to/hf_lung    # ALWAYS RUN FIRST
    python merge_corpora.py --icbhi /path/to/icbhi --hflung /path/to/hf_lung
"""
from __future__ import annotations

import argparse
import csv
import random
import re
import shutil
from collections import Counter, defaultdict
from math import gcd
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

SR = 16_000
CLIP = 5.0
MIN_EVENT = 0.40
SEED = 42
HF_TEST_FRACTION = 0.20      # of HF_Lung patients, for the secondary test set

LABELS = ("Healthy", "Crackle", "Wheeze", "Both")

# ── HF_Lung_V1 label vocabulary ─────────────────────────────────────────
# Its annotations are EVENT level: breath phases plus adventitious sounds.
#   I / E            inhalation, exhalation            -> not adventitious
#   D                discontinuous adventitious sound  -> Crackle
#   Wheeze           continuous adventitious sound     -> Wheeze
#   Stridor, Rhonchi continuous adventitious sounds    -> see CAS_POLICY
#
# CAS_POLICY decides what to do with stridor and rhonchi, which have no slot
# in the four-class scheme. "wheeze" folds them in (more data, less precise);
# "drop" discards those events (cleaner, less data). State your choice in the
# paper either way.
CAS_POLICY = "drop"

EVENT_MAP = {
    "d": "Crackle",
    "wheeze": "Wheeze",
    "stridor": "Wheeze" if CAS_POLICY == "wheeze" else None,
    "rhonchi": "Wheeze" if CAS_POLICY == "wheeze" else None,
    "i": None, "e": None,            # breath phases, not pathology
}


# ── shared audio helpers ────────────────────────────────────────────────
def to_sr(x, sr, target=SR):
    if sr == target:
        return x.astype(np.float32)
    g = gcd(int(sr), target)
    return resample_poly(x, target // g, int(sr) // g).astype(np.float32)


def fixed_clip(x, t0, t1):
    n = int(CLIP * SR)
    seg = x[int(t0 * SR):int(t1 * SR)]
    if len(seg) >= n:
        o = (len(seg) - n) // 2
        return seg[o:o + n]
    out = np.zeros(n, dtype=np.float32)
    o = (n - len(seg)) // 2
    out[o:o + len(seg)] = seg
    return out


def load_mono(path):
    x, sr = sf.read(path, dtype="float32", always_2d=False)
    if x.ndim > 1:
        x = x.mean(axis=1)
    return to_sr(x, sr)


# ── ICBHI adapter ───────────────────────────────────────────────────────
def icbhi_items(root: Path):
    """Yield (patient_key, recording_stem, wav_path, [(t0,t1,label), ...])."""
    for wav in sorted(root.glob("*.wav")):
        txt = wav.with_suffix(".txt")
        if not txt.exists():
            continue
        pid = f"icbhi_{wav.name.split('_')[0]}"
        events = []
        for line in txt.read_text(errors="replace").splitlines():
            f = line.split()
            if len(f) != 4:
                continue
            try:
                t0, t1, cr, wh = float(f[0]), float(f[1]), int(f[2]), int(f[3])
            except ValueError:
                continue
            lab = LABELS[(min(cr, 1)) + 2 * (min(wh, 1))] if False else {
                (0, 0): "Healthy", (1, 0): "Crackle",
                (0, 1): "Wheeze", (1, 1): "Both"}[(min(cr, 1), min(wh, 1))]
            events.append((t0, t1, lab))
        yield pid, wav.stem, wav, events


# ── HF_Lung_V1 adapter ──────────────────────────────────────────────────
# VERIFY THIS AGAINST THE REAL FILES WITH --inspect BEFORE TRUSTING IT.
# The label files are plain text, one event per line, carrying an event type
# and a start and end time in seconds. The exact column order and separator
# must be confirmed; --inspect prints real lines so you can check.
HF_LINE = re.compile(r"^\s*([A-Za-z]+)\s*[,\t ]\s*([\d.]+)\s*[,\t ]\s*([\d.]+)\s*$")


def hf_patient_key(wav: Path) -> str:
    """HF_Lung_V1 filenames encode the recording, not obviously the subject.

    Default: treat each recording as its own group. That is CONSERVATIVE —
    it can only over-separate, never leak. If the release ships a
    subject-to-recording mapping, load it here instead and you keep more
    patients together.
    """
    return f"hf_{wav.stem}"


def hf_items(root: Path):
    for wav in sorted(root.rglob("*.wav")):
        txt = wav.with_suffix(".txt")
        if not txt.exists():
            txt = wav.with_suffix(".label")
        if not txt.exists():
            continue
        spans = defaultdict(list)          # label -> [(t0,t1)]
        for line in txt.read_text(errors="replace").splitlines():
            m = HF_LINE.match(line)
            if not m:
                continue
            kind, a, b = m.group(1).lower(), float(m.group(2)), float(m.group(3))
            lab = EVENT_MAP.get(kind, "SKIP")
            if lab == "SKIP":
                continue                    # unknown token: ignore, report later
            if lab:
                spans[lab].append((a, b))
        yield hf_patient_key(wav), wav.stem, wav, spans


def hf_events(spans, duration):
    """Turn overlapping adventitious spans into non-overlapping labelled windows.

    Walk the recording in CLIP-second steps. A window is Both if it overlaps a
    crackle AND a wheeze span, Crackle or Wheeze if only one, Healthy if neither.
    """
    out = []
    t = 0.0
    while t + CLIP <= duration + 1e-6:
        a, b = t, t + CLIP
        hit = {k for k, sp in spans.items()
               if any(s < b and e > a for s, e in sp)}
        if "Crackle" in hit and "Wheeze" in hit:
            lab = "Both"
        elif "Crackle" in hit:
            lab = "Crackle"
        elif "Wheeze" in hit:
            lab = "Wheeze"
        else:
            lab = "Healthy"
        out.append((a, b, lab))
        t += CLIP                            # NO OVERLAP between windows
    return out


# ── inspection mode ─────────────────────────────────────────────────────
def inspect(hf_root: Path):
    wavs = sorted(hf_root.rglob("*.wav"))
    print(f"wav files found: {len(wavs)}")
    if not wavs:
        print("  nothing found — check the path and that the archive is extracted")
        return
    labs = [p for p in hf_root.rglob("*") if p.suffix in (".txt", ".label")]
    print(f"label files found: {len(labs)}")
    print("\nfirst three wav names:")
    for w in wavs[:3]:
        x, sr = sf.read(w, dtype="float32", always_2d=False)
        print(f"  {w.name}   {len(x)/sr:.1f}s @ {sr} Hz")
    print("\nfirst label file, raw:")
    if labs:
        print(f"  {labs[0].name}")
        for line in labs[0].read_text(errors='replace').splitlines()[:8]:
            print(f"    {line!r}   -> parsed: {bool(HF_LINE.match(line))}")
    toks = Counter()
    for lb in labs[:400]:
        for line in lb.read_text(errors="replace").splitlines():
            m = HF_LINE.match(line)
            if m:
                toks[m.group(1).lower()] += 1
    print(f"\nevent tokens seen in the first 400 label files:")
    for k, v in toks.most_common():
        dest = EVENT_MAP.get(k, "** UNKNOWN — add it to EVENT_MAP **")
        print(f"    {k:10s} {v:7d}  -> {dest}")
    print("\nIf any token says UNKNOWN, or 'parsed: False' appears above,")
    print("fix HF_LINE / EVENT_MAP before running the merge.")


# ── main ────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--icbhi", type=Path)
    ap.add_argument("--hflung", type=Path)
    ap.add_argument("--out", type=Path, default=Path("merged_dataset"))
    ap.add_argument("--inspect", type=Path, metavar="HFLUNG_DIR")
    a = ap.parse_args()

    if a.inspect:
        inspect(a.inspect)
        return
    if not (a.icbhi and a.hflung):
        ap.error("--icbhi and --hflung are both required (or use --inspect)")

    # STEP 1 — partition patients, before opening any audio
    icbhi = list(icbhi_items(a.icbhi))
    icbhi_pts = sorted({p for p, *_ in icbhi})
    official = a.icbhi / "ICBHI_challenge_train_test.txt"
    if official.exists():
        side = {}
        for line in official.read_text(errors="replace").splitlines():
            f = line.split()
            if len(f) >= 2:
                side[f"icbhi_{f[0].split('_')[0]}"] = f[1].lower()
        test_pts = {p for p, s in side.items() if s.startswith("test")}
        how = "official ICBHI challenge split"
    else:
        sh = icbhi_pts[:]
        random.Random(SEED).shuffle(sh)
        test_pts = set(sh[int(len(sh) * 0.7):])
        how = f"random ICBHI patient split, seed {SEED}"

    hf = list(hf_items(a.hflung))
    hf_pts = sorted({p for p, *_ in hf})
    sh = hf_pts[:]
    random.Random(SEED).shuffle(sh)
    hf_holdout = set(sh[:int(len(sh) * HF_TEST_FRACTION)])

    if a.out.exists():
        shutil.rmtree(a.out)
    manifest, counts, skipped = [], Counter(), Counter()

    def emit(pid, stem, wav, events, corpus, category):
        nonlocal manifest
        try:
            x = load_mono(wav)
        except Exception as e:
            skipped[f"unreadable: {type(e).__name__}"] += 1
            return
        for i, (t0, t1, lab) in enumerate(events):
            if lab is None or t1 - t0 < MIN_EVENT:
                skipped["too short"] += 1
                continue
            seg = fixed_clip(x, t0, t1)
            peak = float(np.abs(seg).max())
            if peak < 1e-4:
                skipped["silent"] += 1
                continue
            seg = seg / peak * 0.95
            d = a.out / category / lab
            d.mkdir(parents=True, exist_ok=True)
            name = f"{corpus}_{stem}_c{i:04d}.wav"
            sf.write(d / name, seg, SR, subtype="PCM_16")
            manifest.append({"file": f"{category}/{lab}/{name}", "label": lab,
                             "category": category, "patient": pid,
                             "corpus": corpus, "recording": stem})
            counts[(corpus, category, lab)] += 1

    # STEP 2 — cut inside each partition
    for pid, stem, wav, events in icbhi:
        emit(pid, stem, wav, events, "icbhi",
             "testing" if pid in test_pts else "training")

    for pid, stem, wav, spans in hf:
        try:
            info = sf.info(wav)
            dur = info.frames / info.samplerate
        except Exception:
            skipped["unreadable header"] += 1
            continue
        emit(pid, stem, wav, hf_events(spans, dur), "hflung",
             "hf_holdout" if pid in hf_holdout else "training")

    if not manifest:
        raise SystemExit("no samples written — run --inspect and check the adapters")

    with (a.out / "manifest.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(manifest[0]))
        w.writeheader()
        w.writerows(manifest)

    # STEP 3 — prove no patient crosses any partition
    where = defaultdict(set)
    for r in manifest:
        where[r["patient"]].add(r["category"])
    crossing = sorted(p for p, c in where.items() if len(c) > 1)

    print(f"\nICBHI split: {how}")
    print(f"  ICBHI patients  {len(icbhi_pts):4d}  "
          f"({len(icbhi_pts) - len(test_pts)} train / {len(test_pts)} test)")
    print(f"  HF_Lung groups  {len(hf_pts):4d}  "
          f"({len(hf_pts) - len(hf_holdout)} train / {len(hf_holdout)} holdout)")
    print(f"\n  {'':10s} {'train':>18s} {'test (ICBHI)':>14s} {'holdout (HF)':>14s}")
    for lab in LABELS:
        tr = counts[("icbhi", "training", lab)] + counts[("hflung", "training", lab)]
        te = counts[("icbhi", "testing", lab)]
        ho = counts[("hflung", "hf_holdout", lab)]
        print(f"  {lab:10s} {tr:18d} {te:14d} {ho:14d}")
    tot = len(manifest)
    print(f"  {'TOTAL':10s} {sum(v for (c,k,l),v in counts.items() if k=='training'):18d}"
          f" {sum(v for (c,k,l),v in counts.items() if k=='testing'):14d}"
          f" {sum(v for (c,k,l),v in counts.items() if k=='hf_holdout'):14d}")
    if skipped:
        print("\n  skipped: " + ", ".join(f"{v} {k}" for k, v in skipped.items()))
    print(f"\n  patients crossing a partition: {len(crossing)}   <- must be 0")
    assert not crossing, crossing[:10]
    print(f"  {tot} clips written to {a.out.resolve()}")


if __name__ == "__main__":
    main()
