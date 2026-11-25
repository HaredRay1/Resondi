"""Results charts for the Resondi IMRaD. All values from the full paper."""
import matplotlib.pyplot as plt
import numpy as np
from theme import *

import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "figures") + os.sep
W = 6.0                       # inches, the document's text width


# ── R1 recording clarity ────────────────────────────────────────────────
def clarity():
    cats = ["Good", "Acceptable", "Poor"]
    vals = [68, 25, 7]
    cols = [PRIMARY, SECONDARY, MID]        # ordinal: quality is a magnitude
    fig, ax = plt.subplots(figsize=(W, 1.85))
    y = np.arange(len(cats))[::-1]
    ax.barh(y, vals, height=0.56, color=cols, zorder=3)
    for yy, v in zip(y, vals):
        ax.text(v + 1.4, yy, f"{v}%", va="center", ha="left",
                fontsize=10.5, color=INK, fontweight="bold")
    ax.set_yticks(y); ax.set_yticklabels(cats, fontsize=10.5, color=INK)
    ax.set_xlim(0, 78); ax.set_xticks([])
    strip(ax, keep=())
    ax.text(0, 1.22, "93% of recordings were rated good or acceptable",
            transform=ax.transAxes, fontsize=9.5, color=GREY, style="italic")
    save(fig, OUT + "r1_clarity.png")


# ── R2 ambient noise ────────────────────────────────────────────────────
def noise():
    # CLAUDE.md A5: quiet room 24, ward 35, community area 42 dB; device signal 45 dB
    cats = ["Quiet room", "Hospital ward", "Community area"]
    vals = [24, 35, 42]
    signal = 45
    fig, ax = plt.subplots(figsize=(W, 1.95))
    y = np.arange(len(cats))[::-1]
    ax.barh(y, vals, height=0.54, color=PRIMARY, zorder=3)
    for yy, v in zip(y, vals):
        ax.text(v - 0.8, yy, f"{v} dB", va="center", ha="right",       # inside: 42 dB ran into the 45 dB line
                fontsize=10.5, color=SURFACE, fontweight="bold", zorder=5)
    ax.axvline(signal, color=GREY, lw=1.1, ls="--", zorder=2)
    ax.text(signal + 0.6, y[0], f"device\nsignal\n{signal} dB", fontsize=8.5,
            color=GREY, style="italic", va="center", linespacing=1.2)
    ax.set_yticks(y); ax.set_yticklabels(cats, fontsize=10.5, color=INK)
    ax.set_xlim(0, 58)
    ax.set_xlabel("Ambient noise (dB)", fontsize=9.5, color=GREY, labelpad=6)
    strip(ax, keep=(), grid="x")
    ax.set_xticks([0, 10, 20, 30, 40, 50]); ax.tick_params(labelsize=9)
    ax.text(0, 1.20, "The margin below the 45 dB signal falls from 21 dB to 3 dB",
            transform=ax.transAxes, fontsize=9.5, color=GREY, style="italic")
    save(fig, OUT + "r2_noise.png")


# ── R3 response time ────────────────────────────────────────────────────
def response():
    cats = ["Classification output", "Smart-stethoscope connection",
            "Sound recording", "Signal preprocessing",
            "Recording-quality assessment"]
    vals = [3.97, 4.55, 15.00, 20.91, 144.68]
    sds  = [0.87, 0.83, 0.00, 4.18, 28.94]
    cols = [MID, MID, SECONDARY, SECONDARY, PRIMARY]
    fig, ax = plt.subplots(figsize=(W, 2.5))
    y = np.arange(len(cats))[::-1]
    ax.barh(y, vals, height=0.54, color=cols, zorder=3,
            xerr=sds, error_kw=dict(ecolor=INK, lw=1.1, capsize=3, zorder=4))
    for yy, v, sd in zip(y, vals, sds):
        ax.text(v + sd + 3.5, yy, f"{v:.2f}" + (f" ± {sd:.2f}" if sd else ""),
                va="center", ha="left", fontsize=9.8, color=INK)
    ax.set_yticks(y); ax.set_yticklabels(cats, fontsize=10, color=INK)
    ax.set_xlim(0, 215)
    ax.set_xlabel("Mean duration (seconds), bars show ±1 SD",
                  fontsize=9.5, color=GREY, labelpad=6)
    strip(ax, keep=(), grid="x")
    ax.set_xticks([0, 50, 100, 150]); ax.tick_params(labelsize=9)
    ax.text(0, 1.13, "Quality assessment dominates total elapsed time",
            transform=ax.transAxes, fontsize=9.5, color=GREY, style="italic")
    save(fig, OUT + "r3_response.png")


# ── R4 classification agreement with its interval ───────────────────────
def agreement():
    p, lo, hi, chance = 40.0, 19.8, 64.3, 25.0
    fig, ax = plt.subplots(figsize=(W, 1.75))
    ax.set_xlim(0, 100); ax.set_ylim(-1.15, 1.15)

    ax.add_patch(plt.Rectangle((lo, -0.30), hi - lo, 0.60,
                               facecolor=LIGHT, edgecolor="none", zorder=2))
    ax.plot([lo, hi], [0, 0], color=PRIMARY, lw=2.0, zorder=3)
    for x in (lo, hi):
        ax.plot([x, x], [-0.22, 0.22], color=PRIMARY, lw=2.0, zorder=3)
    ax.plot([p], [0], marker="o", ms=11, color=PRIMARY,
            markeredgecolor=SURFACE, markeredgewidth=2.0, zorder=5)

    ax.plot([chance, chance], [-0.62, 0.62], color=TEAL, lw=1.8,
            ls=(0, (4, 2.5)), zorder=4)
    ax.text(chance, 0.78, "chance, 4 classes (25%)", ha="center",
            fontsize=9, color=TEAL)

    ax.text(p, -0.52, "40%", ha="center", va="top", fontsize=12,
            fontweight="bold", color=PRIMARY)
    ax.text(p, -0.92, "6 of 15 recordings", ha="center", va="top",
            fontsize=9, color=GREY)
    ax.text(lo, 0.36, f"{lo}%", ha="center", fontsize=9, color=SECONDARY)
    ax.text(hi, 0.36, f"{hi}%", ha="center", fontsize=9, color=SECONDARY)

    ax.set_yticks([])
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["0", "25", "50", "75", "100%"], fontsize=9)
    strip(ax, keep=())
    ax.text(0, 1.16, "The 95% Wilson interval contains the 25% chance level",
            transform=ax.transAxes, fontsize=9.5, color=GREY, style="italic")
    save(fig, OUT + "r4_agreement.png")


# ── R5 deployed fusion network on Resondi device recordings ─────────────────
# Source: model-rebuild/results/live-app-device-test-fusion-2026-11-13.md
# (26 unique AUSCULTA recordings; scores Crackles / Healthy / Wheezing / W+C).
# The Edge Impulse build's per-file scores were not kept, only its range
# (27-34%, median 30%, live-app-device-test-2026-11-10.md), so it is a band.
DEVICE_SCORES = [
    (0.422, 0.307, 0.095, 0.176), (0.104, 0.153, 0.344, 0.399),
    (0.248, 0.495, 0.072, 0.185), (0.117, 0.118, 0.416, 0.349),
    (0.157, 0.326, 0.199, 0.318), (0.317, 0.398, 0.073, 0.213),
    (0.277, 0.482, 0.101, 0.140), (0.188, 0.348, 0.240, 0.224),
    (0.115, 0.295, 0.401, 0.189), (0.195, 0.377, 0.198, 0.231),
    (0.143, 0.301, 0.309, 0.247), (0.217, 0.315, 0.171, 0.297),
    (0.181, 0.437, 0.272, 0.110), (0.183, 0.380, 0.164, 0.273),
    (0.155, 0.358, 0.109, 0.378), (0.246, 0.363, 0.076, 0.315),
    (0.069, 0.307, 0.114, 0.511), (0.187, 0.330, 0.063, 0.420),
    (0.205, 0.151, 0.047, 0.597), (0.082, 0.387, 0.112, 0.419),
    (0.250, 0.357, 0.068, 0.325), (0.284, 0.398, 0.026, 0.292),
    (0.302, 0.444, 0.060, 0.194), (0.249, 0.454, 0.059, 0.238),
    (0.228, 0.418, 0.024, 0.330), (0.155, 0.657, 0.123, 0.066),
]
LABELS4 = ["Crackles", "Healthy", "Wheezing", "Wheezing with Crackles"]


def device():
    top = [(LABELS4[int(np.argmax(s))], 100 * max(s)) for s in DEVICE_SCORES]
    rows = ["Healthy", "Wheezing with Crackles", "Wheezing", "Crackles"]
    med = float(np.median([v for _, v in top]))
    fig, ax = plt.subplots(figsize=(W, 2.35))
    ax.set_xlim(20, 70)
    ax.set_ylim(-0.7, len(rows) + 0.05)
    y_of = {r: len(rows) - 1 - i for i, r in enumerate(rows)}

    ax.axvspan(27, 34, color=PALE, zorder=1)
    ax.text(30.5, len(rows), "previous build\n27–34%", ha="center",
            va="top", fontsize=8.3, color=GREY, style="italic", linespacing=1.15)
    ax.axvline(25, color=TEAL, lw=1.6, ls=(0, (4, 2.5)), zorder=2)
    ax.text(25.4, -0.62, "chance 25%", ha="left", va="bottom", fontsize=8.3,
            color=TEAL, linespacing=1.15)
    ax.axvline(med, color=PRIMARY, lw=1.0, ls=":", zorder=2)
    ax.text(med + 0.5, -0.55, f"median {med:.0f}%", ha="left", va="bottom",
            fontsize=8.5, color=PRIMARY)

    rng = np.random.default_rng(7)
    for lab, v in top:
        yy = y_of[lab] + rng.uniform(-0.17, 0.17)
        ax.plot(v, yy, "o", ms=6.5, color=PRIMARY, alpha=0.85,
                markeredgecolor=SURFACE, markeredgewidth=0.8, zorder=4)
    counts = {r: sum(1 for lab, _ in top if lab == r) for r in rows}
    ax.set_yticks([y_of[r] for r in rows])
    ax.set_yticklabels([f"{r} ({counts[r]})" for r in rows], fontsize=9.5, color=INK)
    ax.set_xticks([25, 30, 40, 50, 60, 70])
    ax.set_xticklabels(["25", "30", "40", "50", "60", "70%"], fontsize=9)
    ax.set_xlabel("Score of the top class, per recording", fontsize=9.5,
                  color=GREY, labelpad=6)
    strip(ax, keep=(), grid="x")
    ax.text(0, 1.06, "26 device recordings, by the class chosen; no reference labels",
            transform=ax.transAxes, fontsize=9.5, color=GREY, style="italic")
    save(fig, OUT + "r5_device.png")


# ── R6 heart rate on CirCor test patients ───────────────────────────────────
# Source: model-rebuild/work-exp/heart/seg_test_rows.npz, written by
# model-rebuild/scripts/heart_seg.py report (reference vs estimated BPM per recording).
def heart_rate():
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "model-rebuild",
                       "work-exp", "heart", "seg_test_rows.npz")
    d = np.load(src)
    ref, est = d["ref"], d["est"]
    ok = ~np.isnan(est)
    err = np.abs(est[ok] - ref[ok])
    lo, hi = min(40, float(ref.min()) - 5), max(200, float(np.nanmax(est)) + 5, float(ref.max()) + 5)
    fig, ax = plt.subplots(figsize=(W * 0.62, W * 0.62))
    ax.fill_between([lo, hi], [lo - 5, hi - 5], [lo + 5, hi + 5], color=PALE, zorder=1, lw=0)
    ax.plot([lo, hi], [lo, hi], color=GREY, lw=1.0, ls="--", zorder=2)
    far = err > 10
    ax.scatter(ref[ok][~far], est[ok][~far], s=11, color=PRIMARY, alpha=0.55, lw=0, zorder=3)
    ax.scatter(ref[ok][far], est[ok][far], s=13, color=TEAL, alpha=0.8, lw=0, zorder=4)
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi); ax.set_aspect("equal")
    ax.set_xlabel("Reference heart rate (BPM)", fontsize=9.5, color=GREY)
    ax.set_ylabel("Estimated heart rate (BPM)", fontsize=9.5, color=GREY)
    ax.tick_params(labelsize=8.5)
    strip(ax, keep=("left", "bottom"), grid="both")
    ax.text(0.02, 0.97, f"{ok.sum()} recordings\n{100 * np.mean(err <= 5):.0f}% within 5 BPM (band)\n"
            f"teal: off by more than 10", transform=ax.transAxes, va="top", fontsize=8.3,
            color=INK, linespacing=1.3)
    save(fig, OUT + "r6_heart_rate.png")


if __name__ == "__main__":
    import sys
    wanted = sys.argv[1:]
    for f in (clarity, noise, response, agreement, device, heart_rate):
        if not wanted or f.__name__ in wanted:
            f()
