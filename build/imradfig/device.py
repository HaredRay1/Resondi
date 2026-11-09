"""D6 the device, labelled. Render is one frame of the turntable on white."""
import os as _os
_BUILD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))).replace(chr(92), '/')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle
from PIL import Image
from theme import *

OUT = _BUILD + "/imradfig/"
SRC = _BUILD + "/imradfig/_device_raw.png"

PX, PY = 2900, 1250
WIDTH_IN = 6.05
SCALE = PX / WIDTH_IN          # canvas units per inch
UPT = SCALE / 72.0              # canvas units per typographic point
IMG_W = 2160                       # placed width of the render
im = Image.open(SRC)
IMG_H = int(im.height * IMG_W / im.width)
IX = (PX - IMG_W) / 2
IY = (PY - IMG_H) / 2 - 10
U = IMG_W / im.width               # source px -> canvas px

# (source x, source y, label, sub, side)  y measured from the TOP of the render
CALL = [
 (381,   30, "Mode and record", "single press to capture",  "up"),
 (430,  115, "Status display",  "state and prompts",        "up"),
 (2263, 255, "Chest piece",     "diaphragm",                "up"),
 (108,  155, "Status LEDs",     "power, recording",         "down"),
 (363,  330, "Enclosure",       "3D-printed, houses the electronics", "down"),
 (1331, 309, "Silicone tubing", "acoustic path",            "down"),
 (1815, 250, "Stem",            "connector",                "down"),
]

def sx(x): return IX + x * U
def sy(y): return IY + IMG_H - y * U        # source y is top-down


def d6_device():
    fig = plt.figure(figsize=(WIDTH_IN, PY / SCALE), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, PX); ax.set_ylim(0, PY)
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), PX, PY, facecolor=SURFACE, zorder=0))
    ax.imshow(im, extent=[IX, IX + IMG_W, IY, IY + IMG_H], zorder=1,
              interpolation="lanczos")

    LH_T, LH_S = 8.0 * 1.3 * UPT, 6.2 * 1.3 * UPT   # real point sizes

    def place(group, anchor_y, direction):
        """direction +1 = labels above the render, -1 = below."""
        group = sorted(group, key=lambda c: c[0])
        n = len(group)
        for i, (x, y, lab, sub, _) in enumerate(group):
            tx = PX * (i + 0.5) / n
            sublines = sub.count("\n") + 1 if sub else 0
            # the text block grows away from the render
            if direction > 0:                      # above: title on top
                ty_title = anchor_y
                ty_sub = anchor_y - LH_T
                inner = ty_sub - LH_S * sublines + 6   # bottom edge of block
            else:                                  # below: title still on top
                ty_title = anchor_y + LH_S * sublines + 10
                ty_sub = anchor_y + LH_S * (sublines - 1)
                inner = ty_title + LH_T - 10           # top edge of block
            ax.text(tx, ty_title, lab, ha="center", va="top", fontsize=8.0,
                    fontweight="bold", color=INK, family=SERIF, zorder=5)
            if sub:
                ax.text(tx, ty_sub, sub, ha="center", va="top", fontsize=6.2,
                        color=GREY, family=SERIF, zorder=5, linespacing=1.45)
            ax.plot([sx(x)], [sy(y)], marker="o", ms=2.6, color=PRIMARY,
                    zorder=4)
            ax.add_patch(FancyArrowPatch((tx, inner), (sx(x), sy(y)),
                         arrowstyle="-", color=SECONDARY, lw=0.7,
                         connectionstyle="arc3,rad=0.04",
                         shrinkA=2, shrinkB=5, zorder=3))

    place([c for c in CALL if c[4] == "up"],   PY - 40, +1)
    place([c for c in CALL if c[4] == "down"], 78,      -1)

    save(fig, OUT + "d6_device.png", dpi=300)


if __name__ == "__main__":
    d6_device()
