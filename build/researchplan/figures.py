"""Figures for the revised research plan (rose theme). Run: python build/researchplan/figures.py"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "research-plan", "figures"))
os.makedirs(OUT, exist_ok=True)
ROSE, DEEP, MUTED, PALE, PALE2, BG = "#E91E76", "#8E2A52", "#9E8892", "#F7D6E4", "#EBD3DE", "#FFF5F9"
FONT = "Poppins" if any("Poppins" in f.name for f in font_manager.fontManager.ttflist) else "DejaVu Sans"
plt.rcParams.update({"font.family": FONT, "font.size": 10})

# Counts from model-rebuild/work/manifest.csv (patient-wise split, seed 20261109)
SPLITS = ["Training\n65 patients", "Validation\n30 patients", "Test\n31 patients"]
CLASSES = ["Healthy", "Crackles", "Wheezing", "Wheezing with Crackles"]
COUNTS = {"Healthy": [2536, 551, 555], "Crackles": [1332, 264, 268],
          "Wheezing": [628, 138, 120], "Wheezing with Crackles": [354, 44, 108]}
COLORS = [PALE, ROSE, DEEP, MUTED]


def partition():
    fig, ax = plt.subplots(figsize=(8, 3.2), dpi=200)
    totals = [sum(COUNTS[c][i] for c in CLASSES) for i in range(3)]
    left = [0, 0, 0]
    for c, col in zip(CLASSES, COLORS):
        pct = [COUNTS[c][i] / totals[i] * 100 for i in range(3)]
        ax.barh(SPLITS, pct, left=left, color=col, edgecolor="white", linewidth=1.2, label=c)
        for i in range(3):
            if pct[i] >= 6:
                ax.text(left[i] + pct[i] / 2, i, f"{COUNTS[c][i]:,}\n{pct[i]:.1f}%", ha="center", va="center",
                        fontsize=7.5, color="white" if col in (ROSE, DEEP, MUTED) else DEEP)
        left = [left[i] + pct[i] for i in range(3)]
    for i, t in enumerate(totals):
        ax.text(101, i, f"{t:,} cycles", va="center", fontsize=8.5, color=DEEP)
    ax.set_xlim(0, 100)
    ax.invert_yaxis()
    ax.set_xlabel("Share of respiratory cycles (%)", color=DEEP)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(MUTED)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=DEEP)
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.28), frameon=False, fontsize=8.5)
    fig.patch.set_facecolor("white")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig5_partition.png"), facecolor="white")
    plt.close(fig)


def box(ax, x, y, w, h, title, sub="", fill="white", bold=True, fs=9.5):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                                linewidth=1.6, edgecolor=DEEP, facecolor=fill))
    ax.text(x, y + (0.09 if sub else 0), title, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", color="#3A2230")
    if sub:
        ax.text(x, y - 0.13, sub, ha="center", va="center", fontsize=7.5, color=MUTED)


def arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=DEEP, lw=1.6))


def fusion():
    fig, ax = plt.subplots(figsize=(10, 3.6), dpi=200)
    ax.set_xlim(0, 10.6)
    ax.set_ylim(-0.1, 3.3)
    ax.axis("off")
    box(ax, 0.75, 1.6, 1.3, 0.8, "Recording", "16 kHz mono", fill=PALE)
    box(ax, 2.35, 1.6, 1.3, 0.8, "1-s windows", "16,000 samples")
    arrow(ax, 1.42, 1.6, 1.68, 1.6)
    rows = [(2.75, "Spectrogram", "energy over time"), (1.6, "MFCC", "13 coefficients"), (0.45, "Chromagram", "12 pitch classes")]
    for y, t, s in rows:
        arrow(ax, 3.02, 1.6, 3.5, y)
        box(ax, 4.2, y, 1.35, 0.72, t, s)
        arrow(ax, 4.9, y, 5.25, y)
        box(ax, 5.95, y, 1.3, 0.72, "CNN branch", "conv · pool")
        arrow(ax, 6.62, y, 7.1, 1.6)
    box(ax, 7.75, 1.6, 1.2, 0.8, "Concatenate", "fused features", fill=PALE)
    arrow(ax, 8.37, 1.6, 8.62, 1.6)
    box(ax, 9.55, 1.6, 1.75, 1.0, "Softmax, 4 classes", "averaged per cycle", fill=PALE, fs=9)
    ax.text(9.55, 0.72, "Crackles · Healthy ·\nWheezing · Wheezing\nwith Crackles", ha="center", va="top", fontsize=7, color=DEEP)
    ax.text(5.3, -0.05, "Baseline for comparison: the MFCC branch alone with its own softmax output.",
            ha="center", va="bottom", fontsize=8, style="italic", color=MUTED)
    fig.patch.set_facecolor("white")
    fig.savefig(os.path.join(OUT, "fig4_fusion.png"), facecolor="white", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


if __name__ == "__main__":
    partition()
    fusion()
    print("figures in", OUT)
