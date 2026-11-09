"""Replacement figures for the 83-page paper: Figures 4.4, 4.6, 4.7 and 4.8.

The paper's own figure images carry the superseded values (CLAUDE.md A5), so the
corrected captions need corrected images. Values come from facts.py only.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from facts import RESPONSE, SIGNAL, NOISE, AGREE, CHANCE, wilson

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "figures", "paperfix")

PRIMARY, SECOND, LIGHT = "#8E2A52", "#B5537E", "#C27396"
INK, GREY, PALE = "#3A2730", "#9E8892", "#F7D6E4"

plt.rcParams.update({
    "font.family": "DejaVu Serif", "font.size": 10,
    "axes.edgecolor": GREY, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
})


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def response():
    """Figure 4.4: Table 5 values with their standard deviations."""
    order = ["Smart-stethoscope connection", "Sound recording", "Recording-quality assessment",
             "Signal preprocessing", "Classification output"]
    means = [RESPONSE[k][0] for k in order]
    sds = [RESPONSE[k][1] for k in order]
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    y = range(len(order))[::-1]
    colors = [LIGHT, LIGHT, PRIMARY, SECOND, LIGHT]
    ax.barh(list(y), means, xerr=sds, color=colors, height=0.55,
            error_kw=dict(ecolor=INK, elinewidth=0.9, capsize=3))
    ax.set_yticks(list(y))
    ax.set_yticklabels(order)
    for yi, m, s in zip(y, means, sds):
        ax.text(m + s + 3, yi, f"{m:.2f} s", va="center", fontsize=9, color=INK)
    ax.set_xlabel("Mean response time (seconds); bars show ±1 SD")
    ax.set_xlim(0, 200)
    return save(fig, "Figure-4.4-Response-Time.png")


def agreement():
    """Figure 4.6: 6 of 15 with its Wilson interval against the chance level."""
    k, n = AGREE
    lo, hi = wilson(k, n)
    fig, ax = plt.subplots(figsize=(6.4, 2.2))
    ax.axvspan(lo * 100, hi * 100, ymin=0.3, ymax=0.7, color=PALE, zorder=1)
    ax.plot([k / n * 100], [0.5], "o", color=PRIMARY, markersize=10, zorder=3)
    ax.axvline(CHANCE * 100, color=GREY, linestyle="--", linewidth=1.2, zorder=2)
    ax.text(CHANCE * 100 - 1, 0.86, "Chance, four classes: 25%", ha="right", fontsize=9, color=GREY)
    ax.text(hi * 100 + 1, 0.12, f"{k} of {n} agreed = {k / n:.0%}", ha="left", fontsize=10,
            color=PRIMARY, fontweight="bold")
    ax.text(hi * 100 + 1, 0.5, f"95% Wilson CI\n{lo:.1%} to {hi:.1%}", va="center", fontsize=9, color=INK)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Agreement with reference labels (%)")
    return save(fig, "Figure-4.6-Classification-Agreement.png")


def signal():
    """Figure 4.7: 45 dB against 32 dB, with the amplitude ratio stated correctly."""
    dev, conv = SIGNAL
    fig, ax = plt.subplots(figsize=(6.4, 2.2))
    ax.barh([1, 0], [dev, conv], color=[PRIMARY, LIGHT], height=0.55)
    ax.set_yticks([1, 0])
    ax.set_yticklabels(["Resondi", "Conventional\nstethoscope"])
    for yi, v in ((1, dev), (0, conv)):
        ax.text(v + 0.8, yi, f"{v} dB", va="center", fontsize=10, color=INK)
    ratio = 10 ** ((dev - conv) / 20)
    ax.text(58, 0.5, f"Difference {dev - conv} dB\n≈ {ratio:.1f}× the amplitude", va="center",
            fontsize=9.5, color=PRIMARY)
    ax.set_xlim(0, 75)
    ax.set_xlabel("Mean signal strength (dB)")
    return save(fig, "Figure-4.7-Signal-Strength.png")


def noise():
    """Figure 4.8: ambient noise per setting, with headroom to the device signal."""
    dev = SIGNAL[0]
    names = list(NOISE)
    vals = [NOISE[k] for k in names]
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    ax.bar(names, vals, color=[LIGHT, SECOND, PRIMARY], width=0.55)
    ax.axhline(dev, color=INK, linestyle="--", linewidth=1.1)
    ax.text(-0.27, dev + 1.2, f"Resondi mean signal, {dev} dB", ha="left", fontsize=9, color=INK)
    for i, v in enumerate(vals):
        ax.text(i, v / 2, f"{v} dB", ha="center", color="white", fontsize=10, fontweight="bold")
        ax.annotate("", xy=(i + 0.32, dev), xytext=(i + 0.32, v),
                    arrowprops=dict(arrowstyle="<->", color=GREY, linewidth=1))
        ax.text(i + 0.36, (v + dev) / 2, f"{dev - v} dB\nmargin", va="center", fontsize=8, color=GREY)
    ax.set_ylim(0, 55)
    ax.set_ylabel("Ambient noise (dB)")
    return save(fig, "Figure-4.8-Ambient-Noise.png")


def build_all():
    return {"4.4": response(), "4.6": agreement(), "4.7": signal(), "4.8": noise()}


if __name__ == "__main__":
    for k, v in build_all().items():
        print(k, v)
