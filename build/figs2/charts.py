"""Results figures: clarity, ambient noise, response time, agreement."""
import os as _os
_BUILD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))).replace(chr(92), '/')
import sys
sys.path.insert(0, _BUILD + "/figs2")
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from style import *

OUT = _BUILD + "/figs2/"


def rounded_bar(ax, x, y, w, h, color, r=0.055, horiz=False):
    """4px-style rounded data end, square against the baseline."""
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle=f"round,pad=0,rounding_size={r}",
                 facecolor=color, edgecolor=SURFACE, linewidth=1.6, zorder=3))


# ── Figure: recording clarity (ORDINAL -> sequential ramp) ──────────────
def clarity():
    labels = ["Good", "Acceptable", "Poor"]
    vals = [68, 25, 7]
    fig = figure(6.4, 2.5)
    ax = fig.add_axes([0.0, 0.06, 1.0, 0.74])
    ax.set_xlim(0, 100); ax.set_ylim(0, 1); ax.axis("off")
    title(ax, "Recording clarity",
          "n = 920 recordings. 93 percent rated good or acceptable.")
    x = 0.0
    for lab, v, c in zip(labels, vals, SEQ3):
        ax.add_patch(Rectangle((x, 0.30), v - 0.5, 0.26, facecolor=c,
                               edgecolor="none", zorder=3))
        if v >= 12:
            ax.text(x + v / 2, 0.43, f"{v}%", ha="center", va="center",
                    fontsize=11, fontweight="bold",
                    color=SURFACE if c == PRIMARY else TEXT, zorder=4)
        ax.text(x, 0.19, lab, ha="left", va="top", fontsize=9.5, color=TEXT)
        if v < 12:
            ax.text(x, 0.60, f"{v}%", ha="left", va="bottom", fontsize=10,
                    fontweight="bold", color=PRIMARY)
        x += v
    ax.plot([0, 100], [0.285, 0.285], color=RULE, lw=1.0, zorder=1)
    save(fig, OUT + "fig07_clarity.png")


# ── Figure: ambient noise by setting (one series) ───────────────────────
def noise():
    labels = ["Community\narea", "Quiet\nroom", "Hospital\nward"]
    vals = [25.67, 27.88, 32.49]
    fig = figure(5.0, 3.3)
    ax = fig.add_axes([0.13, 0.14, 0.84, 0.66])
    title(ax, "Ambient noise during capture",
          "Recording remained possible in all three settings.")
    xs = np.arange(3)
    ax.bar(xs, vals, width=0.52, color=SECONDARY, edgecolor=SURFACE,
           linewidth=1.6, zorder=3)
    for x, v in zip(xs, vals):
        ax.text(x, v + 0.5, f"{v:.2f}", ha="center", va="bottom",
                fontsize=10, fontweight="bold", color=TEXT)
    ax.set_xticks(xs); ax.set_xticklabels(labels, fontsize=9.5)
    ax.set_ylabel("Sound level (dB)", fontsize=9.5)
    ax.set_ylim(0, 38)
    ax.yaxis.grid(True, color=RULE, lw=0.9, zorder=0)
    ax.set_axisbelow(True)
    strip_axes(ax, keep=("bottom",))
    save(fig, OUT + "fig08_noise.png")


# ── Figure: response time per stage, with SD ────────────────────────────
def response():
    stages = ["Classification\noutput", "Smart-stethoscope\nconnection",
              "Sound\nrecording", "Signal\npreprocessing",
              "Recording-quality\nassessment"]
    mean = [3.97, 4.55, 15.00, 20.91, 144.68]
    sd = [0.87, 0.83, 0.00, 4.18, 28.94]
    fig = figure(6.8, 3.7)
    ax = fig.add_axes([0.29, 0.14, 0.67, 0.60])
    title(ax, "Time taken by each stage", "Mean and standard deviation, in seconds. "
          "Quality assessment dominates.", x=-0.43, y=1.09)
    ys = np.arange(len(stages))
    ax.barh(ys, mean, height=0.56, color=SECONDARY, edgecolor=SURFACE,
            linewidth=1.6, zorder=3)
    ax.errorbar(mean, ys, xerr=sd, fmt="none", ecolor=PRIMARY, elinewidth=1.6,
                capsize=4, capthick=1.6, zorder=4)
    for y, m, s in zip(ys, mean, sd):
        ax.text(m + s + 5, y, f"{m:.2f}" + (f" ± {s:.2f}" if s else ""),
                va="center", fontsize=9.5, color=TEXT)
    ax.set_yticks(ys); ax.set_yticklabels(stages, fontsize=9)
    ax.set_xlabel("Seconds", fontsize=9.5)
    ax.set_xlim(0, 205)
    ax.set_ylim(-0.62, len(stages) - 0.38)
    ax.xaxis.grid(True, color=RULE, lw=0.9, zorder=0)
    ax.set_axisbelow(True)
    strip_axes(ax, keep=("left",))
    save(fig, OUT + "fig09_response.png")


# ── Figure: classification agreement with its interval ──────────────────
def agreement():
    fig = figure(6.8, 3.1)
    ax = fig.add_axes([0.06, 0.26, 0.90, 0.54])
    ax.set_xlim(0, 100); ax.set_ylim(0, 1); ax.axis("off")
    title(ax, "Classification agreement against reference labels",
          "6 of 15 recordings agreed. The interval is what the sample size allows.",
          x=-0.05)
    y = 0.58
    ax.plot([0, 100], [y, y], color=RULE, lw=1.4, zorder=1)
    lo, hi, pt = 19.8, 64.3, 40.0
    ax.add_patch(Rectangle((lo, y - 0.085), hi - lo, 0.17, facecolor=LIGHT,
                           edgecolor=EDGE, linewidth=1.2, zorder=2))
    ax.plot([pt], [y], marker="o", ms=11, color=PRIMARY, zorder=4,
            markeredgecolor=SURFACE, markeredgewidth=1.8, linestyle="none")
    ax.plot([25, 25], [y - 0.20, y + 0.20], color=ACCENT, lw=1.8,
            linestyle=(0, (4, 3)), zorder=3)
    ax.text(25, y + 0.26, "chance, 4 classes", ha="center", va="bottom",
            fontsize=8.5, color=ACCENT)
    ax.text(pt, y - 0.20, "40%", ha="center", va="top", fontsize=12,
            fontweight="bold", color=PRIMARY)
    for v, lab in ((lo, "19.8%"), (hi, "64.3%")):
        ax.plot([v, v], [y - 0.085, y + 0.085], color=EDGE, lw=1.4, zorder=3)
        ax.text(v, y + 0.13, lab, ha="center", va="bottom", fontsize=8.5, color=GREY)
    for t in (0, 25, 50, 75, 100):
        ax.text(t, y - 0.42, f"{t}%", ha="center", va="top", fontsize=8, color=GREY)
    fig.text(0.06, 0.045, "95% Wilson interval spans 44 points and contains chance — "
             "fifteen recordings cannot establish a rate.",
             fontsize=8.5, color=GREY, va="bottom", ha="left")
    save(fig, OUT + "fig10_agreement.png")


if __name__ == "__main__":
    clarity(); noise(); response(); agreement()
