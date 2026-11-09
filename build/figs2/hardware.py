"""Figure 2 — hardware block diagram, in the Resondi rose theme."""
import os as _os
_BUILD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))).replace(chr(92), '/')
import sys
sys.path.insert(0, _BUILD + "/figs2")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from style import *

OUT = _BUILD + "/figs2/fig02_hardware.png"


def build():
    fig = figure(9.4, 3.5)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    title(ax, "Hardware block diagram",
          "Two storage paths: Bluetooth where a phone is present, MicroSD where it "
          "is not.", x=0.012, y=0.885)

    def group(x, y, w, h, label):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                     boxstyle="round,pad=0,rounding_size=0.016",
                     facecolor="#FDF6F9", edgecolor=RULE, linewidth=1.2, zorder=1))
        ax.text(x + w / 2, y + h + 0.028, label, ha="center", va="bottom",
                fontsize=8.4, fontweight="bold", color=SECONDARY, zorder=2)

    def blk(x, y, w, h, head, sub=None, strong=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                     boxstyle="round,pad=0,rounding_size=0.015",
                     facecolor=LIGHT if strong else SURFACE,
                     edgecolor=PRIMARY if strong else SECONDARY,
                     linewidth=1.8 if strong else 1.3, zorder=3))
        cy = y + h / 2 + (0.035 if sub else 0)
        ax.text(x + w / 2, cy, head, ha="center", va="center",
                fontsize=9.0 if strong else 8.6, fontweight="bold",
                color=TEXT, zorder=4)
        if sub:
            ax.text(x + w / 2, y + h / 2 - 0.055, sub, ha="center", va="center",
                    fontsize=7.4, color=GREY, zorder=4)

    def arr(x1, y1, x2, y2, rad=0.0):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                     mutation_scale=11, linewidth=1.5, color=EDGE, zorder=2,
                     connectionstyle=f"arc3,rad={rad}"))

    group(0.012, 0.455, 0.250, 0.230, "ACOUSTIC")
    blk(0.030, 0.495, 0.105, 0.150, "Chest piece", "diaphragm")
    blk(0.150, 0.495, 0.095, 0.150, "Tubing", "silicone")
    arr(0.137, 0.570, 0.148, 0.570)

    arr(0.247, 0.570, 0.300, 0.570)
    group(0.285, 0.130, 0.345, 0.555, "ELECTRONIC")
    blk(0.302, 0.495, 0.140, 0.150, "MEMS microphone", "INMP441")
    blk(0.458, 0.495, 0.155, 0.150, "Preamplifier")
    arr(0.444, 0.570, 0.456, 0.570)
    blk(0.302, 0.330, 0.311, 0.130, "ESP32 microcontroller", strong=True)
    arr(0.535, 0.493, 0.480, 0.462)
    blk(0.302, 0.168, 0.140, 0.132, "Display", "status and prompts")
    blk(0.458, 0.168, 0.155, 0.132, "Li-ion cell", "charge and protect")
    ax.plot([0.372, 0.372], [0.328, 0.302], color=EDGE, lw=1.3, zorder=2)
    ax.plot([0.535, 0.535], [0.328, 0.302], color=EDGE, lw=1.3, zorder=2)

    group(0.655, 0.300, 0.333, 0.385, "TRANSMISSION")
    blk(0.672, 0.500, 0.128, 0.140, "Bluetooth LE", "live transfer")
    blk(0.672, 0.330, 0.128, 0.140, "MicroSD", "store and forward")
    arr(0.615, 0.410, 0.668, 0.560, rad=-0.18)
    arr(0.615, 0.390, 0.668, 0.400, rad=0.10)
    blk(0.828, 0.395, 0.145, 0.175, "Mobile\napplication", strong=True)
    arr(0.802, 0.565, 0.826, 0.510, rad=0.12)
    arr(0.802, 0.398, 0.826, 0.455, rad=-0.12)

    ax.text(0.012, 0.055, "Capture never depends on connectivity: a recording is "
            "written locally and synchronised when a network is next reached.",
            fontsize=8.4, color=GREY, va="bottom")
    save(fig, OUT)


if __name__ == "__main__":
    build()
