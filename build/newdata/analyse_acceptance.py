"""Resondi - acceptance survey analysis.

Reads the Google Forms export, normalises the response spellings, groups the
usable Likert items into constructs, and reports weighted mean, SD and
Cronbach's alpha per construct.

Names, e-mail addresses and timestamps are never read or written.
"""
import csv
import statistics as st
from collections import Counter

SCALE = {
    "strongly disagree": 1,
    "disagree": 2,
    "neutral": 3,
    "agree": 4,
    "strongly agree": 5,
    "stongly agree": 5,      # typo present in the form's own option list
}

VERBAL = [(4.21, "Strongly Agree"), (3.41, "Agree"), (2.61, "Neutral"),
          (1.81, "Disagree"), (1.00, "Strongly Disagree")]


def verbal(m):
    return next(v for lo, v in VERBAL if m >= lo)


def alpha(item_scores):
    """Cronbach's alpha. item_scores: list of per-item lists, equal length."""
    k = len(item_scores)
    if k < 2:
        return None
    n = len(item_scores[0])
    if n < 2:
        return None
    item_var = sum(st.variance(s) for s in item_scores)
    total = [sum(s[i] for s in item_scores) for i in range(n)]
    tv = st.variance(total)
    if tv == 0:
        return None
    return (k / (k - 1)) * (1 - item_var / tv)


rows = list(csv.DictReader(open("survey_raw.csv")))
cols = list(rows[0])
Q = {i: cols[i] for i in range(len(cols))}

CONSTRUCTS = {
    "Performance expectancy": [5, 6, 7],
    "Effort expectancy":      [9, 10, 11],
    "Regulatory assurance":   [8, 12, 15, 18, 19],
    "Social influence":       [14],
}
BINARY = {13: "Peers encourage use", 16: "Access to training/support",
          17: "Institution provides resources", 4: "Prior device/app experience"}

ROLE = cols[3]


def scores(idx, subset=None):
    out = []
    for r in (subset if subset is not None else rows):
        v = (r[Q[idx]] or "").strip().lower()
        if v in SCALE:
            out.append(SCALE[v])
    return out


def report(label, subset):
    print(f"\n{'=' * 72}\n{label}  (n = {len(subset)})\n{'=' * 72}")
    print(f"  {'Construct':24s} {'items':>5s} {'n':>4s} {'Mean':>6s} "
          f"{'SD':>5s}  {'Verbal':18s} {'alpha':>6s}")
    for name, idxs in CONSTRUCTS.items():
        per_item = [scores(i, subset) for i in idxs]
        per_item = [s for s in per_item if s]
        if not per_item:
            continue
        n = min(len(s) for s in per_item)
        per_item = [s[:n] for s in per_item]
        means = [sum(s[j] for s in per_item) / len(per_item) for j in range(n)]
        m, sd = st.mean(means), (st.stdev(means) if n > 1 else 0.0)
        a = alpha(per_item)
        astr = f"{a:.2f}" if a is not None else "  n/a"
        print(f"  {name:24s} {len(per_item):5d} {n:4d} {m:6.2f} {sd:5.2f}  "
              f"{verbal(m):18s} {astr:>6s}")

    overall = []
    for idxs in CONSTRUCTS.values():
        for i in idxs:
            overall += scores(i, subset)
    if overall:
        print(f"\n  Overall across all {sum(len(v) for v in CONSTRUCTS.values())}"
              f" Likert items: mean {st.mean(overall):.2f}, "
              f"{verbal(st.mean(overall))}")


print(f"respondents in file: {len(rows)}")
print("\nrole breakdown:")
for k, v in Counter(r[ROLE] for r in rows).most_common():
    print(f"  {k:36s} {v}")

report("ALL RESPONDENTS", rows)
for role in sorted({r[ROLE] for r in rows}):
    sub = [r for r in rows if r[ROLE] == role]
    if len(sub) >= 3:
        report(f"ROLE: {role}", sub)

print(f"\n{'=' * 72}\nBINARY ITEMS - report as frequencies, not means\n{'=' * 72}")
for i, label in BINARY.items():
    c = Counter((r[Q[i]] or "").strip() for r in rows if (r[Q[i]] or "").strip())
    tot = sum(c.values())
    parts = ", ".join(f"{k} {v} ({v / tot * 100:.0f}%)" for k, v in c.most_common())
    print(f"  {label:32s} n={tot:3d}  {parts}")

print(f"\n{'=' * 72}\nNOT REPORTABLE - no responses recorded\n{'=' * 72}")
for c in cols:
    if all(not (r[c] or "").strip() for r in rows):
        print(f"  - {c.strip()}")
