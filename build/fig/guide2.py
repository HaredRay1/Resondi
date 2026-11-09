"""The auscultation guide, split into a Lung Mode figure and a Heart Mode figure.

The single combined guide was 7.9in wide but is placed at 6.25in in the
document, so every label rendered at 0.79x its design size. Splitting the
content across two narrower figures (5.6in) reverses that: the same type is
displayed at 1.12x instead, and the key text is enlarged on top of it.

Key rows are laid out in row units with the y axis inverted, so spacing is
predictable and the tag markers stay circular whatever the axes aspect.
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
    ("5", "Interscapular T3–T4, right of the spine", "right upper lobe"),
    ("6", "Interscapular T3–T4, left of the spine", "left upper lobe"),
    ("7", "Infrascapular T8–T10, right", "right lower lobe"),
    ("8", "Infrascapular T8–T10, left", "left lower lobe"),
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
    ("Lung Mode.", "Open mouth, breathing deeper than at rest; at least one "
                   "full breath in and out at each site. Twenty seconds."),
    ("Heart Mode.", "Quiet breathing. Diaphragm for high-pitched sounds, the bell "
                    "applied lightly for low-pitched ones. Fifteen seconds."),
    ("Order matters.", "Follow the numbering. Right and left are taken as a pair "
                       "at each level before the sequence moves down."),
    ("Position.", "Seated, arms forward for the posterior sites; the arm raised "
                  "for the lateral sites; left side for point M."),
]

FS_HEAD, FS_SUB, FS_TITLE = 11.5, 8.6, 9.8
FS_WHERE, FS_WHAT, FS_HOW = 9.0, 8.4, 9.0
TAG_1, TAG_2 = 7.6, 6.3
WRAP = 56


def rows_axes(ax, n_rows):
    ax.set_xlim(0, 1)
    ax.set_ylim(n_rows, 0)          # inverted: row 0 at the top
    ax.axis("off")


def site_rows(ax, y, title, rows, fc=PRIMARY):
    """Draw a titled block of site rows; returns the next free row index."""
    ax.text(0.0, y, title, fontsize=FS_TITLE, family=SERIF, color=SECONDARY,
            fontweight="bold", va="center")
    ax.plot([0.0, 1.0], [y + 0.42, y + 0.42], color="#F0DCE5", lw=1.0)
    y += 1.05
    for tag, where, what in rows:
        ax.plot([0.021], [y], marker="o", ms=13.5, color=fc, zorder=4,
                linestyle="none")
        ax.text(0.021, y, tag, ha="center", va="center",
                fontsize=TAG_2 if len(tag) > 1 else TAG_1, color="white",
                family=SERIF, fontweight="bold", zorder=5)
        ax.text(0.055, y, where, fontsize=FS_WHERE, family=SERIF, color=TEXT,
                va="center")
        ax.text(1.0, y, what, fontsize=FS_WHAT, family=SERIF, color=GREY,
                style="italic", va="center", ha="right")
        y += 1.0
    return y


# ── Figure A — Lung Mode ────────────────────────────────────────────────
figL = plt.figure(figsize=(5.6, 6.35))
gsL = GridSpec(2, 2, height_ratios=[1.0, 0.56], wspace=0.02, hspace=0.06,
               left=0.012, right=0.988, top=0.985, bottom=0.015)
anterior(figL.add_subplot(gsL[0, 0]), app=True)
posterior(figL.add_subplot(gsL[0, 1]), app=True)

axk = figL.add_subplot(gsL[1, :])
rows_axes(axk, 13.2)
axk.text(0.0, 0.35, "SITE KEY  ·  LUNG MODE", fontsize=FS_HEAD, family=SERIF,
         color=PRIMARY, fontweight="bold", va="center")
axk.text(0.0, 1.25, "The number on the chest is the order of capture. "
         "Twenty seconds per site.", fontsize=FS_SUB, family=SERIF, color=GREY,
         style="italic", va="center")
site_rows(axk, 2.5, "NINE SITES, TRACHEAL REFERENCE FIRST", LUNG)

figL.savefig(OUT + "fig_ausc_lung.png", dpi=400, bbox_inches="tight",
             pad_inches=0.08, facecolor="white")
plt.close(figL)

# ── Figure B — Heart Mode and recording protocol ────────────────────────
figH = plt.figure(figsize=(5.6, 7.3))
gsH = GridSpec(3, 1, height_ratios=[1.0, 0.40, 0.62], hspace=0.20,
               left=0.012, right=0.988, top=0.985, bottom=0.015)
chest(figH.add_subplot(gsH[0, 0]), app=True)

axh = figH.add_subplot(gsH[1, 0])
rows_axes(axh, 8.6)
axh.text(0.0, 0.35, "SITE KEY  ·  HEART MODE", fontsize=FS_HEAD, family=SERIF,
         color=PRIMARY, fontweight="bold", va="center")
axh.text(0.0, 1.25, "From the base of the heart to its apex. "
         "Fifteen seconds per point.", fontsize=FS_SUB, family=SERIF, color=GREY,
         style="italic", va="center")
site_rows(axh, 2.5, "FIVE POINTS", HEART)

axw = figH.add_subplot(gsH[2, 0])
rows_axes(axw, 15.6)
axw.text(0.0, 0.35, "HOW TO RECORD", fontsize=FS_HEAD, family=SERIF,
         color=SECONDARY, fontweight="bold", va="center")
axw.plot([0.0, 1.0], [0.78, 0.78], color="#F0DCE5", lw=1.0)
y = 1.45
for lead, rest in HOW:
    axw.text(0.0, y, lead, fontsize=FS_HOW, family=SERIF, color=PRIMARY,
             fontweight="bold", va="top")
    wrapped = textwrap.fill(rest, WRAP)
    axw.text(0.26, y, wrapped, fontsize=FS_HOW, family=SERIF, color=TEXT,
             va="top", linespacing=1.25)
    y += 1.15 * (1 + wrapped.count("\n")) + 0.45

if y > 15.6:
    print(f"  WARNING: how-to block overruns, needs {y:.1f} rows")

figH.savefig(OUT + "fig_ausc_heart.png", dpi=400, bbox_inches="tight",
             pad_inches=0.08, facecolor="white")
plt.close(figH)

from PIL import Image
for f in ("fig_ausc_lung.png", "fig_ausc_heart.png"):
    print(" ", f, Image.open(OUT + f).size)
print("split guide written")
