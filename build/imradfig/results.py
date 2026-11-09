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
    ax.text(0, 1.22, "93% of recordings were usable for classification",
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
        ax.text(v + 0.5, yy, f"{v} dB", va="center", ha="left",
                fontsize=10.5, color=INK, fontweight="bold")
    ax.axvline(signal, color=GREY, lw=1.1, ls="--", zorder=2)
    ax.text(signal + 0.6, y[0], f"device\nsignal\n{signal} dB", fontsize=8.5,
            color=GREY, style="italic", va="center", linespacing=1.2)
    ax.set_yticks(y); ax.set_yticklabels(cats, fontsize=10.5, color=INK)
    ax.set_xlim(0, 58)
    ax.set_xlabel("Ambient noise (dB)", fontsize=9.5, color=GREY, labelpad=6)
    strip(ax, keep=(), grid="x")
    ax.set_xticks([0, 10, 20, 30, 40, 50]); ax.tick_params(labelsize=9)
    ax.text(0, 1.20, "Capture remained possible in all three settings; margin to the "
            "signal falls from 21 dB to 3 dB",
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
    ax.text(0, 1.16, "95% Wilson interval spans 44 points — it contains "
            "chance and a usable classifier",
            transform=ax.transAxes, fontsize=9.5, color=GREY, style="italic")
    save(fig, OUT + "r4_agreement.png")


if __name__ == "__main__":
    for f in (clarity, noise, response, agreement):
        f()
