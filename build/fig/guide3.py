"""One combined auscultation guide, laid out so the key text stays readable.

Readability here is governed by characters per line, not by resolution: the
original put the key in a half-width quadrant, which is why it printed small.
This version gives the lung key and the recording protocol the full width and
keeps only the heart key beside a panel, which roughly halves the characters
per line for the longest lists.
"""
import os as _os
_BUILD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))).replace(chr(92), '/')
import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from anat import PRIMARY, SECONDARY, GREY, TEXT, SERIF
from lung_fig import anterior, posterior
from heart_fig import chest

OUT = _BUILD + "/fig/"

LUNG = [
    ("Tc", "Suprasternal notch, over the trachea", "central airway"),
    ("1", "2nd ICS, right midclavicular line", "right upper lobe"),
    ("2", "2nd ICS, left midclavicular line", "left upper lobe"),
    ("3", "4th–5th ICS, right mid-axillary line", "right middle lobe"),
    ("4", "4th–5th ICS, left mid-axillary line", "lingula"),
    ("5", "Infrascapular T8–T10, right of the spine", "right lower lobe"),
    ("6", "Infrascapular T8–T10, left of the spine", "left lower lobe"),
]
HEART = [
    ("A", "2nd ICS, right sternal border", "aortic"),
    ("P", "2nd ICS, left sternal border", "pulmonary"),
    ("E", "3rd ICS, left sternal border", "Erb's — not classified"),
    ("T", "4th–5th ICS, left lower sternal border", "tricuspid"),
    ("M", "5th ICS, left midclavicular line (apex)", "mitral"),
]
HOW = [
    ("Bare skin.", "The chest piece touches skin, never clothing."),
    ("Lung Mode.", "Open mouth, breathing deeper than at rest; at least one full "
                   "breath in and out at each site. Twenty seconds."),
    ("Heart Mode.", "Quiet breathing. Diaphragm for high-pitched sounds, the bell "
                    "applied lightly for low-pitched ones. Fifteen seconds."),
    ("Order matters.", "Follow the numbering. Right and left are taken as a pair at "
                       "each level before the sequence moves down."),
    ("Position.", "Seated, arms forward for the posterior sites; the arm raised for "
                  "the lateral sites; left side for point M."),
]

FS_HEAD, FS_TITLE = 12.0, 10.4
FS_WHERE, FS_WHAT, FS_HOW = 9.6, 9.0, 9.6
TAG_1, TAG_2 = 7.8, 6.4


def rows_axes(ax, n):
    ax.set_xlim(0, 1); ax.set_ylim(n, 0); ax.axis("off")


def site_rows(ax, y, title, rows, ms=13.0):
    ax.text(0.0, y, title, fontsize=FS_TITLE, family=SERIF, color=SECONDARY,
            fontweight="bold", va="center")
    ax.plot([0.0, 1.0], [y + 0.42, y + 0.42], color="#F0DCE5", lw=1.0)
    y += 1.05
    for tag, where, what in rows:
        ax.plot([0.020], [y], marker="o", ms=ms, color=PRIMARY, zorder=4,
                linestyle="none")
        ax.text(0.020, y, tag, ha="center", va="center",
                fontsize=TAG_2 if len(tag) > 1 else TAG_1, color="white",
                family=SERIF, fontweight="bold", zorder=5)
        ax.text(0.052, y, where, fontsize=FS_WHERE, family=SERIF, color=TEXT,
                va="center")
        ax.text(1.0, y, what, fontsize=FS_WHAT, family=SERIF, color=GREY,
                style="italic", va="center", ha="right")
        y += 1.0
    return y


fig = plt.figure(figsize=(7.5, 10.5))
gs = GridSpec(4, 2, height_ratios=[3.30, 2.95, 2.25, 1.85],
              wspace=0.03, hspace=0.17,
              left=0.010, right=0.990, top=0.988, bottom=0.012)

anterior(fig.add_subplot(gs[0, 0]), app=True)
posterior(fig.add_subplot(gs[0, 1]), app=True)
chest(fig.add_subplot(gs[1, 0]), app=True)

# heart key, beside the cardiac panel
axh = fig.add_subplot(gs[1, 1])
rows_axes(axh, 9.4)
axh.text(0.0, 0.40, "SITE KEY  ·  HEART MODE", fontsize=FS_HEAD, family=SERIF,
         color=PRIMARY, fontweight="bold", va="center")
axh.text(0.0, 1.35, "Base of the heart to its apex. Fifteen seconds per point.",
         fontsize=FS_WHAT, family=SERIF, color=GREY, style="italic", va="center")
site_rows(axh, 2.7, "FIVE POINTS", HEART, ms=12.0)

# lung key, full width
axl = fig.add_subplot(gs[2, :])
rows_axes(axl, 12.4)
axl.text(0.0, 0.40, "SITE KEY  ·  LUNG MODE", fontsize=FS_HEAD, family=SERIF,
         color=PRIMARY, fontweight="bold", va="center")
axl.text(0.0, 1.35, "The number on the chest is the order of capture. "
         "Twenty seconds per site.", fontsize=FS_WHAT, family=SERIF, color=GREY,
         style="italic", va="center")
site_rows(axl, 2.7, "SEVEN SITES, TRACHEAL REFERENCE FIRST", LUNG)

# how to record, full width
axw = fig.add_subplot(gs[3, :])
rows_axes(axw, 14.4)
axw.text(0.0, 0.40, "HOW TO RECORD", fontsize=FS_HEAD, family=SERIF,
         color=SECONDARY, fontweight="bold", va="center")
axw.plot([0.0, 1.0], [0.85, 0.85], color="#F0DCE5", lw=1.0)
y = 1.55
for lead, rest in HOW:
    axw.text(0.0, y, lead, fontsize=FS_HOW, family=SERIF, color=PRIMARY,
             fontweight="bold", va="top")
    wrapped = textwrap.fill(rest, 78)
    axw.text(0.175, y, wrapped, fontsize=FS_HOW, family=SERIF, color=TEXT,
             va="top", linespacing=1.3)
    y += 1.18 * (1 + wrapped.count("\n")) + 0.38
if y > 14.4:
    print(f"  WARNING: how-to needs {y:.1f} of 14.4 rows")

fig.savefig(OUT + "fig_ausc_combined.png", dpi=400, bbox_inches="tight",
            pad_inches=0.08, facecolor="white")
plt.close(fig)

from PIL import Image
im = Image.open(OUT + "fig_ausc_combined.png")
print("  fig_ausc_combined.png", im.size, "aspect", round(im.height / im.width, 3))
