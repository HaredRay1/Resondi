"""Figure 1 — the device, labelled, from the team's own Blender model."""
import os as _os
_BUILD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))).replace(chr(92), '/')
import sys
sys.path.insert(0, _BUILD + "/figs2")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from PIL import Image
from style import *

SRC = _BUILD + "/figs2/_device_white.png"
OUT = _BUILD + "/figs2/fig01_device.png"

FIG_W, FIG_H = 9.6, 6.1
IMG_X, IMG_W, IMG_Y = 0.055, 0.890, 0.300   # the height is derived from the
                                            # image aspect so that imshow fills
                                            # the axes exactly; otherwise it is
                                            # letterboxed and every leader-line
                                            # anchor lands in the wrong place.

# head, sub, anchor in IMAGE fraction, text anchor in FIGURE coords, align, curve
LABELS = [
    ("Mode and record control", "single press to capture",
     (0.215, 0.075), (0.175, 0.815), "center", 0.0),
    ("Display", "device status and prompts",
     (0.300, 0.200), (0.455, 0.815), "center", 0.0),
    ("Acoustic chest piece", "diaphragm against the chest wall",
     (0.902, 0.130), (0.905, 0.815), "right", 0.0),
    ("Status indicators", "power and recording",
     (0.145, 0.345), (0.050, 0.235), "left", -0.14),
    ("Charging and data port", "",
     (0.085, 0.470), (0.255, 0.140), "center", 0.12),
    ("Enclosure", "3D-printed PLA. Houses the microphone and\npreamplifier, ESP32 with BLE, MicroSD and battery.",
     (0.320, 0.690), (0.560, 0.235), "center", 0.07),
    ("Silicone tubing", "",
     (0.660, 0.340), (0.845, 0.235), "center", -0.10),
]


def build():
    im = Image.open(SRC).convert("RGB")
    aspect = im.height / im.width
    img_h = (IMG_W * FIG_W * aspect) / FIG_H
    IMG = (IMG_X, IMG_Y, IMG_W, img_h)
    fig = figure(FIG_W, FIG_H)

    axi = fig.add_axes(list(IMG)); axi.imshow(im); axi.axis("off")
    axi.set_xlim(0, im.width); axi.set_ylim(im.height, 0)
    axi.set_zorder(1)

    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis("off"); ax.set_zorder(2); ax.patch.set_visible(False)

    fig.text(0.040, 0.962, "Resondi smart stethoscope", fontsize=13,
             fontweight="bold", color=PRIMARY, va="top", zorder=3)
    fig.text(0.040, 0.912, "Rendered from the current enclosure model. Internal "
             "components are named but not visible.", fontsize=9, color=GREY,
             va="top", zorder=3)

    x0, y0, w, h = IMG
    to_fig = lambda fx, fy: (x0 + fx * w, y0 + (1 - fy) * h)

    for head, sub, anchor, (tx, ty), ha, rad in LABELS:
        axp, ayp = to_fig(*anchor)
        ax.add_patch(FancyArrowPatch((tx, ty), (axp, ayp),
                     arrowstyle="-", linewidth=1.1, color=EDGE, zorder=4,
                     shrinkA=9, shrinkB=3,
                     connectionstyle=f"arc3,rad={rad}"))
        ax.plot([axp], [ayp], marker="o", ms=5.2, color=PRIMARY,
                markeredgecolor=SURFACE, markeredgewidth=1.4, zorder=6,
                linestyle="none")
        above = ty > 0.5
        ax.text(tx, ty, head, ha=ha, va="bottom" if above else "top",
                fontsize=9.6, fontweight="bold", color=TEXT, zorder=6)
        if sub:
            ax.text(tx, ty + (0.030 if above else -0.030), sub, ha=ha,
                    va="bottom" if above else "top", fontsize=8.0, color=GREY,
                    zorder=6, linespacing=1.55)

    save(fig, OUT)


if __name__ == "__main__":
    build()
