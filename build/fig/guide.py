"""One consolidated auscultation guide: both lung views, the cardiac view,
and a key covering every site, sized to sit on a single page of the concept note."""
import os as _os
_BUILD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))).replace(chr(92), '/')
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.gridspec import GridSpec
import textwrap

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


def block(ax, y, title, rows, fc=PRIMARY, small=False):
    ax.text(0.000, y, title, fontsize=7.9, family=SERIF, color=SECONDARY,
            fontweight="bold", va="center")
    ax.plot([0.000, 1.000], [y - 0.0155, y - 0.0155], color="#F0DCE5", lw=0.9)
    y -= 0.0415
    for tag, where, what in rows:
        ax.add_patch(Circle((0.0175, y), 0.0128, facecolor=fc, edgecolor="none",
                            transform=ax.transAxes, zorder=4))
        ax.text(0.0175, y, tag, ha="center", va="center",
                fontsize=5.0 if len(tag) > 1 else 6.0, color="white",
                family=SERIF, fontweight="bold", zorder=5)
        ax.text(0.047, y, where, fontsize=7.0, family=SERIF, color=TEXT,
                va="center")
        ax.text(1.000, y, what, fontsize=6.7, family=SERIF, color=GREY,
                style="italic", va="center", ha="right")
        y -= 0.0345
    return y


def key(ax):
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.text(0.000, 0.982, "SITE KEY", fontsize=9.0, family=SERIF, color=PRIMARY,
            fontweight="bold", va="center")
    ax.text(0.000, 0.948,
            "The number on the chest is the order of capture.",
            fontsize=6.9, family=SERIF, color=GREY, style="italic", va="center")

    y = block(ax, 0.898, "LUNG MODE  ·  20 seconds per site", LUNG)
    y = block(ax, y - 0.022, "HEART MODE  ·  15 seconds per point", HEART)

    y -= 0.030
    ax.text(0.000, y, "HOW TO RECORD", fontsize=7.9, family=SERIF, color=SECONDARY,
            fontweight="bold", va="center")
    ax.plot([0.000, 1.000], [y - 0.0155, y - 0.0155], color="#F0DCE5", lw=0.9)
    y -= 0.048
    for lead, rest in HOW:
        ax.text(0.000, y, lead, fontsize=6.9, family=SERIF, color=PRIMARY,
                fontweight="bold", va="top")
        wrapped = textwrap.fill(rest, 60)
        ax.text(0.225, y, wrapped, fontsize=6.9, family=SERIF, color=TEXT,
                va="top", linespacing=1.55)
        y -= 0.0335 * (1 + wrapped.count("\n")) + 0.009


fig = plt.figure(figsize=(7.9, 8.75))
gs = GridSpec(2, 2, wspace=0.015, hspace=0.045,
              left=0.005, right=0.995, top=0.978, bottom=0.018)
anterior(fig.add_subplot(gs[0, 0]), app=True)
posterior(fig.add_subplot(gs[0, 1]), app=True)
chest(fig.add_subplot(gs[1, 0]), app=True)
key(fig.add_subplot(gs[1, 1]))

for name, kw in (("fig_auscultation_guide.png", dict(dpi=300)),
                 ("fig_auscultation_guide@600.png", dict(dpi=600)),
                 ("fig_auscultation_guide.svg", {}),
                 ("fig_auscultation_guide.pdf", {})):
    fig.savefig(OUT + name, bbox_inches="tight", pad_inches=0.10,
                facecolor="white", **kw)
print("guide written")
