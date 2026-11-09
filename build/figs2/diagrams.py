"""Pipeline and architecture diagrams, in the Resondi rose theme."""
import os as _os
_BUILD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))).replace(chr(92), '/')
import sys
sys.path.insert(0, _BUILD + "/figs2")
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from style import *

OUT = _BUILD + "/figs2/"


def box(ax, x, y, w, h, head, sub=None, fill=SURFACE, edge=SECONDARY,
        head_fill=None, fs=9.6, fs_sub=8.2, lw=1.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0,rounding_size=0.055",
                 facecolor=fill, edgecolor=edge, linewidth=lw, zorder=3))
    if head_fill:
        ax.add_patch(Rectangle((x + 0.012, y + h - 0.20), w - 0.024, 0.185,
                               facecolor=head_fill, edgecolor="none", zorder=4))
        ax.text(x + w / 2, y + h - 0.107, head, ha="center", va="center",
                fontsize=fs, fontweight="bold", color=TEXT, zorder=5)
        if sub:
            ax.text(x + w / 2, y + (h - 0.20) / 2, sub, ha="center", va="center",
                    fontsize=fs_sub, color=GREY, zorder=5, linespacing=1.45)
    else:
        cy = y + h / 2 + (0.055 if sub else 0)
        ax.text(x + w / 2, cy, head, ha="center", va="center", fontsize=fs,
                fontweight="bold", color=TEXT, zorder=5)
        if sub:
            ax.text(x + w / 2, y + h / 2 - 0.085, sub, ha="center", va="center",
                    fontsize=fs_sub, color=GREY, zorder=5, linespacing=1.45)


def arrow(ax, x1, y1, x2, y2, color=EDGE, lw=1.7, rad=0.0):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                 arrowstyle="-|>", mutation_scale=13, linewidth=lw,
                 color=color, zorder=2,
                 connectionstyle=f"arc3,rad={rad}"))


# ── Figure 4 — audio preprocessing chain ───────────────────────────────
def preprocessing():
    steps = [("Raw recording", "WAV, as captured"),
             ("Resample", "to 16 kHz"),
             ("Noise reduction", "suppress background"),
             ("Normalise", "standardise amplitude"),
             ("Segment", "fixed-length windows"),
             ("Mel-spectrogram", "via STFT, 224 × 224")]
    fig = figure(9.4, 2.35)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    title(ax, "Audio preprocessing", "Every recording follows the same chain before "
          "it reaches the classifier.", x=0.012, y=0.80)
    n = len(steps); gap = 0.019
    w = (1 - 0.024 - gap * (n - 1)) / n
    for i, (h, s) in enumerate(steps):
        x = 0.012 + i * (w + gap)
        last = i == n - 1
        box(ax, x, 0.20, w, 0.40, h, s,
            fill=LIGHT if last else SURFACE,
            edge=PRIMARY if last else SECONDARY,
            lw=1.9 if last else 1.5)
        if i:
            arrow(ax, x - gap - 0.001, 0.40, x - 0.002, 0.40)
    save(fig, OUT + "fig04_preprocessing.png")


# ── Figure 5 — the classifier AS EVALUATED (single input) ──────────────
def architecture():
    fig = figure(9.4, 2.7)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    title(ax, "Classification model", "Single mel-spectrogram input. This is the model "
          "the results in this paper describe.", x=0.012, y=0.82)
    stages = [("Mel-spectrogram", "224 × 224 input"),
              ("Convolutional\nlayers", "local patterns"),
              ("Pooling layers", "reduce dimensions"),
              ("Fully connected", "higher-level features"),
              ("Softmax", "class probabilities")]
    n = len(stages); gap = 0.022
    w = (0.80 - gap * (n - 1)) / n
    for i, (h, s) in enumerate(stages):
        x = 0.012 + i * (w + gap)
        box(ax, x, 0.30, w, 0.36, h, s,
            fill=LIGHT if i == 0 else SURFACE,
            edge=PRIMARY if i == 0 else SECONDARY)
        if i:
            arrow(ax, x - gap - 0.001, 0.48, x - 0.002, 0.48)
    xo = 0.012 + n * (w + gap)
    box(ax, xo, 0.24, 1 - xo - 0.012, 0.48, "Four classes",
        "Normal\nWheezing\nCrackles\nWheezing with crackles",
        fill=LIGHT, edge=PRIMARY, lw=1.9, fs_sub=8.0)
    arrow(ax, xo - gap - 0.001, 0.48, xo - 0.002, 0.48, color=PRIMARY)
    ax.text(0.012, 0.075, "Sound patterns, not diseases. Every classification is "
            "presented to a practitioner for confirmation.",
            fontsize=8.6, color=GREY, va="bottom")
    save(fig, OUT + "fig05_architecture.png")


# ── Figure 6 — rule-based interpretation layer ─────────────────────────
def rules():
    R = [("1", "All four zones healthy", "No adventitious sounds detected"),
         ("2", "Both upper zones wheeze", "Possible asthma — bilateral obstruction"),
         ("3", "Upper wheeze + lower crackles", "Possible bronchiolitis"),
         ("4", "Crackles in one or both lower zones",
              "Possible pneumonia or pulmonary edema"),
         ("5", "All four zones wheeze with crackles",
              "Possible severe bronchiolitis or diffuse inflammation"),
         ("6", "No preceding rule is satisfied",
              "Further clinical evaluation needed")]
    fig = figure(7.6, 4.3)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    title(ax, "Rule-based interpretation", "Zone patterns map to literature-supported "
          "possibilities, never to a diagnosis.", x=0.012, y=0.90)
    top, rh, gap = 0.80, 0.108, 0.013
    for i, (num, cond, poss) in enumerate(R):
        y = top - (i + 1) * (rh + gap)
        last = i == len(R) - 1
        ax.add_patch(FancyBboxPatch((0.012, y), 0.976, rh,
                     boxstyle="round,pad=0,rounding_size=0.012",
                     facecolor=LIGHT if last else SURFACE,
                     edgecolor=EDGE, linewidth=1.2, zorder=2))
        ax.add_patch(Rectangle((0.012, y), 0.052, rh,
                               facecolor=PRIMARY if not last else SECONDARY,
                               edgecolor="none", zorder=3))
        ax.text(0.038, y + rh / 2, num, ha="center", va="center", fontsize=10,
                fontweight="bold", color=SURFACE, zorder=4)
        ax.text(0.080, y + rh / 2, cond, ha="left", va="center", fontsize=9.2,
                color=TEXT, zorder=4)
        ax.text(0.978, y + rh / 2, poss, ha="right", va="center", fontsize=8.8,
                color=GREY, style="italic", zorder=4)
    ax.text(0.012, 0.035, "Each possibility carries its supporting source in the "
            "paper. Outputs are possibilities requiring clinical evaluation.",
            fontsize=8.5, color=GREY, va="bottom")
    save(fig, OUT + "fig06_rules.png")


if __name__ == "__main__":
    preprocessing(); architecture(); rules()


# ── Figure 12 — the PLANNED three-branch fusion model ──────────────────
def fusion():
    fig = figure(9.4, 3.5)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    title(ax, "Planned three-branch fusion model",
          "Not implemented at the time of evaluation. Shown for comparison with the "
          "single-input model above.", x=0.012, y=0.885)

    branches = [("Mel-spectrogram", "energy over time;\ncrackles read as transients", 0.645),
                ("MFCC", "spectral envelope;\noverall timbre", 0.445),
                ("Chromagram", "pitch classes;\nwheezes read as tone", 0.245)]
    bx, bw, bh = 0.185, 0.205, 0.165
    cx, cw = 0.520, 0.150
    ox, ow = 0.760, 0.215

    ax.add_patch(FancyBboxPatch((0.012, 0.385), 0.135, 0.165,
                 boxstyle="round,pad=0,rounding_size=0.015",
                 facecolor=LIGHT, edgecolor=PRIMARY, linewidth=1.8, zorder=3))
    ax.text(0.0795, 0.492, "Recording", ha="center", va="center", fontsize=9.2,
            fontweight="bold", color=TEXT, zorder=4)
    ax.text(0.0795, 0.437, "one preprocessed\naudio segment", ha="center",
            va="center", fontsize=7.4, color=GREY, zorder=4, linespacing=1.5)

    for head, sub, y in branches:
        ax.add_patch(FancyBboxPatch((bx, y - bh / 2), bw, bh,
                     boxstyle="round,pad=0,rounding_size=0.015",
                     facecolor=SURFACE, edgecolor=SECONDARY, linewidth=1.3, zorder=3))
        ax.text(bx + bw / 2, y + 0.040, head, ha="center", va="center",
                fontsize=8.8, fontweight="bold", color=TEXT, zorder=4)
        ax.text(bx + bw / 2, y - 0.025, sub, ha="center", va="center",
                fontsize=7.3, color=GREY, zorder=4, linespacing=1.5)
        ax.text(bx + bw + 0.028, y, "CNN\nbranch", ha="center", va="center",
                fontsize=7.8, color=SECONDARY, fontweight="bold", zorder=4,
                linespacing=1.4)
        arrow(ax, 0.149, 0.467, bx - 0.004, y, rad=0.0)
        arrow(ax, bx + bw + 0.058, y, cx - 0.004, 0.455,
              rad=0.0 if abs(y - 0.455) < 0.05 else (0.10 if y < 0.455 else -0.10))

    ax.add_patch(FancyBboxPatch((cx, 0.370), cw, 0.175,
                 boxstyle="round,pad=0,rounding_size=0.015",
                 facecolor=SURFACE, edgecolor=SECONDARY, linewidth=1.3, zorder=3))
    ax.text(cx + cw / 2, 0.487, "Concatenate", ha="center", va="center",
            fontsize=8.8, fontweight="bold", color=TEXT, zorder=4)
    ax.text(cx + cw / 2, 0.425, "one fused\nfeature vector", ha="center",
            va="center", fontsize=7.3, color=GREY, zorder=4, linespacing=1.5)
    arrow(ax, cx + cw + 0.004, 0.457, ox - 0.004, 0.457)

    ax.add_patch(FancyBboxPatch((ox, 0.330), ow, 0.255,
                 boxstyle="round,pad=0,rounding_size=0.015",
                 facecolor=LIGHT, edgecolor=PRIMARY, linewidth=1.8, zorder=3))
    ax.text(ox + ow / 2, 0.535, "Softmax", ha="center", va="center", fontsize=9.2,
            fontweight="bold", color=TEXT, zorder=4)
    ax.text(ox + ow / 2, 0.432, "Normal\nWheezing\nCrackles\nWheezing with crackles",
            ha="center", va="center", fontsize=7.4, color=GREY, zorder=4,
            linespacing=1.6)

    ax.text(0.012, 0.055, "Feature-level fusion: the branches share one classifier "
            "rather than voting. A crackle is a transient and a wheeze is a tone, so "
            "no single representation captures both well.",
            fontsize=8.4, color=GREY, va="bottom")
    save(fig, OUT + "fig12_fusion.png")
