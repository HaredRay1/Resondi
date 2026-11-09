"""Figure 3 — anatomically specified auscultation sites for Lung Mode and Heart Mode.

Lung sites follow the regional scheme described for digital-stethoscope recording
by Huang et al. (2023) and map onto the chest-location codes used by the ICBHI 2017
database (Rocha et al., 2019).  Heart sites are the four points defined by the
CirCor DigiScope dataset (Oliveira et al., 2022), plus Erb's point as an optional
practitioner-only capture.
"""
import os as _os
_BUILD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))).replace(chr(92), '/')
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, PathPatch, Rectangle
from matplotlib.path import Path

NAVY, MID, LIGHT = "#1F4E79", "#2E75B6", "#DEEAF6"
GREY, TEXT = "#7F7F7F", "#262626"
SKIN, EDGE = "#FAFCFE", "#8FB0CD"
BONE = "#B9CDE0"
SERIF = "serif"
OUT = _BUILD + "/fig/"

TORSO = [
    (-0.12, 1.88), (0.12, 1.88),
    (0.34, 1.80), (0.62, 1.70),
    (0.73, 1.44), (0.75, 1.12),
    (0.72, 0.86), (0.68, 0.66),
    (0.58, 0.52), (0.42, 0.45),
    (-0.42, 0.45), (-0.58, 0.52),
    (-0.68, 0.66), (-0.72, 0.86),
    (-0.75, 1.12), (-0.73, 1.44),
    (-0.62, 1.70), (-0.34, 1.80),
]


def torso(ax):
    ax.add_patch(Polygon(TORSO, closed=True, facecolor=SKIN, edgecolor=EDGE,
                         linewidth=1.5, zorder=1, joinstyle="round"))


def rib(ax, y, side, x0=0.10, x1=0.66, rise=0.07, drop=0.24, lw=1.0):
    """One rib, curving up slightly off the sternum then down and out."""
    s = side
    verts = [(s * x0, y), (s * 0.42, y + rise), (s * x1, y - drop)]
    ax.add_patch(PathPatch(Path(verts, [Path.MOVETO, Path.CURVE3, Path.CURVE3]),
                           fill=False, edgecolor=BONE, lw=lw, zorder=2))


def anterior_frame(ax, ics_labels=False):
    """Clavicles, sternum, ribs and the two vertical reference lines."""
    # clavicles
    for s in (-1, 1):
        ax.plot([s * 0.06, s * 0.30, s * 0.58], [1.62, 1.70, 1.64],
                color=BONE, lw=2.4, solid_capstyle="round", zorder=2)
    # sternum: manubrium + body
    ax.add_patch(Rectangle((-0.075, 1.40), 0.15, 0.22, facecolor="white",
                           edgecolor=BONE, lw=1.2, zorder=3))
    ax.add_patch(Rectangle((-0.065, 0.96), 0.13, 0.44, facecolor="white",
                           edgecolor=BONE, lw=1.2, zorder=3))
    # sternal angle (angle of Louis) — the landmark for the 2nd rib
    ax.plot([-0.13, 0.13], [1.40, 1.40], color=MID, lw=1.5, zorder=4)

    # ribs 2 through 7, descending
    for i, y in enumerate([1.40, 1.26, 1.12, 0.99, 0.87]):
        for s in (-1, 1):
            rib(ax, y, s, x1=0.66 - 0.02 * i, drop=0.24 + 0.02 * i)

    # midclavicular and mid-axillary reference lines
    for s in (-1, 1):
        ax.plot([s * 0.34, s * 0.34], [1.56, 0.70], color=EDGE, lw=0.8,
                ls=(0, (2, 2.5)), zorder=2)
        ax.plot([s * 0.64, s * 0.64], [1.30, 0.86], color=EDGE, lw=0.8,
                ls=(0, (2, 2.5)), zorder=2)

    if ics_labels:
        for y, lab in ((1.33, "2nd ICS"), (1.05, "4th ICS"), (0.92, "5th ICS")):
            ax.text(-0.80, y, lab, ha="right", va="center", fontsize=7.0,
                    family=SERIF, color=GREY, style="italic")
            ax.plot([-0.78, -0.74], [y, y], color=GREY, lw=0.7, zorder=2)


def posterior_frame(ax):
    """Spine with vertebral levels and the two scapulae."""
    ax.plot([0, 0], [1.72, 0.52], color=BONE, lw=1.4, zorder=2)
    for y in [1.68 - i * 0.105 for i in range(12)]:
        ax.plot([-0.038, 0.038], [y, y], color=BONE, lw=0.7, zorder=2)
    # scapulae
    for s in (-1, 1):
        sc = [(s * 0.30, 1.56), (s * 0.66, 1.50), (s * 0.60, 1.20),
              (s * 0.40, 1.06), (s * 0.30, 1.22)]
        ax.add_patch(Polygon(sc, closed=True, facecolor="white", edgecolor=BONE,
                             linewidth=1.2, zorder=2, alpha=0.92))
        ax.text(s * 0.50, 1.16, "scapula", ha="center", va="center", fontsize=5.8,
                family=SERIF, color=BONE, style="italic", zorder=3)
    # posterior ribs, flatter than the anterior ones
    for i, y in enumerate([1.46, 1.30, 1.14, 0.98, 0.84]):
        for s in (-1, 1):
            rib(ax, y, s, x0=0.05, x1=0.62 - 0.015 * i, rise=0.03, drop=0.16, lw=0.8)
    for y, lab in ((1.36, "T3–T4"), (0.92, "T8–T10")):
        ax.text(-0.82, y, lab, ha="right", va="center", fontsize=7.0,
                family=SERIF, color=GREY, style="italic")
        ax.plot([-0.80, -0.74], [y, y], color=GREY, lw=0.7, zorder=2)


def heart_shape(ax):
    v = [(-0.10, 1.22), (0.10, 1.30), (0.26, 1.22), (0.33, 1.05),
         (0.31, 0.93), (0.22, 0.86), (0.05, 0.86), (-0.08, 0.94),
         (-0.13, 1.08), (-0.10, 1.22)]
    c = [Path.MOVETO] + [Path.CURVE3] * 8 + [Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(v, c), facecolor="#F3DEDE", edgecolor="#C98A8A",
                           lw=1.1, zorder=4, alpha=0.72))


def marker(ax, x, y, tag, fc=NAVY, r=0.082, fs=7.4):
    ax.add_patch(Circle((x, y), r, facecolor=fc, edgecolor="white",
                        linewidth=1.3, zorder=6))
    ax.text(x, y, tag, ha="center", va="center", fontsize=fs, color="white",
            family=SERIF, fontweight="bold", zorder=7)


def orient(ax, left, right):
    for x, t in ((-0.60, left), (0.60, right)):
        ax.text(x, 1.48, t, ha="center", va="center", fontsize=8.6,
                family=SERIF, color=EDGE, fontweight="bold", zorder=4)


def frame(ax, title, sub):
    ax.set_xlim(-1.02, 1.02); ax.set_ylim(0.12, 2.24); ax.axis("off")
    ax.set_aspect("equal")
    ax.text(0, 2.14, title, ha="center", fontsize=9.6, family=SERIF,
            color=NAVY, fontweight="bold")
    ax.text(0, 1.98, sub, ha="center", fontsize=7.6, family=SERIF,
            color=GREY, style="italic")


fig, axes = plt.subplots(1, 3, figsize=(9.8, 3.62))

# ── Panel 1 — Lung Mode, anterior (patient's left falls on the viewer's right)
ax = axes[0]
frame(ax, "LUNG MODE · anterior", "sites 1–4 and the tracheal reference")
torso(ax); anterior_frame(ax)
orient(ax, "R", "L")
marker(ax, 0.00, 1.60, "Tc", fc=MID, r=0.088, fs=6.4)
marker(ax, -0.34, 1.33, "1")      # right anterior upper, 2nd ICS MCL
marker(ax, 0.34, 1.33, "2")       # left anterior upper
marker(ax, -0.64, 1.05, "3")      # right lateral, mid-axillary
marker(ax, 0.64, 1.05, "4")       # left lateral
ax.text(0, 0.27, "midclavicular and mid-axillary\nlines shown dashed",
        ha="center", va="center", fontsize=6.6, family=SERIF, color=GREY,
        style="italic", linespacing=1.4)

# ── Panel 2 — Lung Mode, posterior (patient's left stays on the viewer's left)
ax = axes[1]
frame(ax, "LUNG MODE · posterior", "sites 5–8")
torso(ax); posterior_frame(ax)
orient(ax, "L", "R")
marker(ax, 0.22, 1.36, "5")       # right posterior upper, interscapular
marker(ax, -0.22, 1.36, "6")      # left posterior upper
marker(ax, 0.30, 0.92, "7")       # right posterior lower, infrascapular
marker(ax, -0.30, 0.92, "8")      # left posterior lower
ax.text(0, 0.27, "upper sites medial to the scapula,\nlower sites below its angle",
        ha="center", va="center", fontsize=6.6, family=SERIF, color=GREY,
        style="italic", linespacing=1.4)

# ── Panel 3 — Heart Mode, anterior
ax = axes[2]
frame(ax, "HEART MODE · anterior", "four classified points, one optional")
torso(ax); anterior_frame(ax, ics_labels=True); heart_shape(ax)
orient(ax, "R", "L")
marker(ax, -0.16, 1.33, "A", fc=NAVY)
marker(ax, 0.16, 1.33, "P", fc=NAVY)
marker(ax, 0.16, 1.19, "E", fc="#9DB9D2")
marker(ax, 0.16, 1.00, "T", fc=NAVY)
marker(ax, 0.36, 0.92, "M", fc=NAVY)
ax.text(0, 0.27, "shaded: cardiac silhouette. E (Erb's point) is\ncaptured for the practitioner but not classified",
        ha="center", va="center", fontsize=6.6, family=SERIF, color=GREY,
        style="italic", linespacing=1.4)

fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.105, wspace=0.03)
fig.text(0.5, 0.030,
         "R and L mark the patient's own right and left. Every capture is tagged with its site code, "
         "so a recording can be compared only against the same site.",
         ha="center", fontsize=7.4, family=SERIF, color=GREY, style="italic")

fig.savefig(OUT + "figC_sites.png", dpi=240, bbox_inches="tight",
            pad_inches=0.06, facecolor="white")
print("written")
