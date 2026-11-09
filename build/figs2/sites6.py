"""Figure 3 — the six standardised lung locations the application guides to.

Composed from the shared anatomy primitives rather than lung_fig.anterior(),
because that function draws the nine-site concept-note scheme with its own
markers and sequence arrows. This paper's device records six.
"""
import os as _os
_BUILD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))).replace(chr(92), '/')
import sys
sys.path.insert(0, _BUILD + "/figs2")
sys.path.insert(0, _BUILD + "/fig")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch
from style import *
from anat import (body, clavicles, sternum, ribs, vline, orient, stage, SERIF)
from lung_fig import lungs_anterior, MCL, MAL, ICS2

OUT = _BUILD + "/figs2/"

# x negative is the patient's RIGHT, matching orient(ax, "R", "L")
SITES = [
    (-MCL, ICS2,  "RU", "Right upper",  "2nd ICS, midclavicular"),
    ( MCL, ICS2,  "LU", "Left upper",   "2nd ICS, midclavicular"),
    (-0.50, 1.13, "RM", "Right middle", "4th–5th ICS"),
    ( 0.50, 1.13, "LM", "Left middle",  "4th–5th ICS"),
    (-0.44, 0.88, "RL", "Right lower",  "lower zone"),
    ( 0.44, 0.88, "LL", "Left lower",   "lower zone"),
]


def build():
    fig = figure(8.0, 5.05)

    axd = fig.add_axes([0.015, 0.02, 0.49, 0.80])
    stage(axd, xlim=(-0.90, 0.90), ylim=(0.55, 1.95))
    body(axd); lungs_anterior(axd); clavicles(axd)
    ribs(axd, [ICS2, 1.310, 1.155, 1.000, 0.855])
    sternum(axd, angle_y=ICS2)
    vline(axd, -MCL, 1.62, 0.80); vline(axd, MCL, 1.62, 0.80)
    orient(axd, "R", "L")
    for x, y, tag, *_ in SITES:
        axd.add_patch(Circle((x, y), 0.072, facecolor=PRIMARY,
                             edgecolor=SURFACE, linewidth=2.0, zorder=12))
        axd.text(x, y, tag, ha="center", va="center", fontsize=7.6,
                 fontweight="bold", color=SURFACE, zorder=13)
    axd.text(-MCL, 0.76, "midclavicular", ha="center", va="top", fontsize=6.6,
             family=SERIF, color=GREY, style="italic")
    axd.text(0, 0.60, "Anterior view. Shaded: the lungs, with their fissures.",
             ha="center", va="top", fontsize=6.8, family=SERIF, color=GREY,
             style="italic")

    axk = fig.add_axes([0.535, 0.02, 0.45, 0.80])
    axk.set_xlim(0, 1); axk.set_ylim(0, 1); axk.axis("off")
    axk.text(0.0, 0.955, "SIX STANDARDISED LOCATIONS", fontsize=9.8,
             fontweight="bold", color=PRIMARY, va="center")
    axk.plot([0, 1], [0.915, 0.915], color=RULE, lw=1.1)
    y = 0.835
    for _, _, tag, name, land in SITES:
        axk.add_patch(Circle((0.042, y), 0.030, facecolor=PRIMARY,
                             edgecolor="none", zorder=4))
        axk.text(0.042, y, tag, ha="center", va="center", fontsize=6.6,
                 fontweight="bold", color=SURFACE, zorder=5)
        axk.text(0.105, y + 0.016, name, ha="left", va="center", fontsize=9.6,
                 color=TEXT)
        axk.text(0.105, y - 0.030, land, ha="left", va="center", fontsize=7.8,
                 color=GREY, style="italic")
        y -= 0.112
    box_top = y + 0.03
    axk.add_patch(FancyBboxPatch((0.0, box_top - 0.245), 1.0, 0.235,
                  boxstyle="round,pad=0,rounding_size=0.02",
                  facecolor=LIGHT, edgecolor=EDGE, linewidth=1.1))
    axk.text(0.035, box_top - 0.052, "HOW A SITE IS RECORDED", fontsize=8.4,
             fontweight="bold", color=PRIMARY, va="top")
    axk.text(0.035, box_top - 0.105,
             "The application names the location; the user confirms\n"
             "placement on bare skin and records. The file is saved\n"
             "with its location and metadata, and repeats are allowed.",
             fontsize=8.0, color=TEXT, va="top", linespacing=1.55)

    fig.text(0.015, 0.975, "Guided auscultation locations", fontsize=12.5,
             fontweight="bold", color=PRIMARY, va="top")
    fig.text(0.015, 0.925, "Site attribution is automatic, so a recording can be "
             "compared against the same location at a later visit.",
             fontsize=9, color=GREY, va="top")
    save(fig, OUT + "fig03_sites.png")


if __name__ == "__main__":
    build()
