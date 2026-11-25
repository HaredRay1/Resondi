"""Lung Mode — instructional auscultation sequence.

Regional scheme after Huang et al. (2023); site codes map onto the chest
locations carried in the ICBHI 2017 database (Rocha et al., 2019).
"""
import os as _os
_BUILD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))).replace(chr(92), '/')
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch, Circle
from matplotlib.gridspec import GridSpec

from anat import (PRIMARY, SECONDARY, ACCENT, GREY, TEXT, BONE, EDGE, SERIF,
                  smooth, body, clavicles, sternum, ribs, vline, point, seq,
                  orient, stage)

OUT = _BUILD + "/fig/"

MCL, MAL = 0.42, 0.625
ICS2, LAT_Y = 1.465, 1.095
UP_Y, LOW_Y = 1.448, 0.962

ANT = [("Tc", 0.000, 1.605), ("1", -MCL, ICS2), ("2", MCL, ICS2),
       ("3", -MAL, LAT_Y), ("4", MAL, LAT_Y)]
POST = [("5", 0.300, LOW_Y), ("6", -0.300, LOW_Y)]

ROWS = [
    ("head", "TRACHEAL REFERENCE", "", ""),
    ("Tc", "Trachea", "Suprasternal notch", "central airway · optional"),
    ("head", "ANTERIOR · seated or supine", "", ""),
    ("1", "Right upper", "2nd ICS, right midclavicular line", "right upper lobe"),
    ("2", "Left upper", "2nd ICS, left midclavicular line", "left upper lobe"),
    ("head", "LATERAL · arm raised", "", ""),
    ("3", "Right lateral", "4th–5th ICS, right mid-axillary line", "right middle lobe"),
    ("4", "Left lateral", "4th–5th ICS, left mid-axillary line", "lingula"),
    ("head", "POSTERIOR · seated, arms forward", "", ""),
    ("5", "Right lower", "Infrascapular, T8–T10, right of the spine", "right lower lobe"),
    ("6", "Left lower", "Infrascapular, T8–T10, left of the spine", "left lower lobe"),
]


LUNG_FILL, LUNG_EDGE = "#F6DBE7", "#D49FB8"


def _lung(ax, pts, mirror=False):
    q = [(-x, y) for x, y in pts] if mirror else pts
    ax.add_patch(PathPatch(smooth(q, closed=True), facecolor=LUNG_FILL,
                           edgecolor=LUNG_EDGE, lw=1.0, zorder=1.6, alpha=0.55))


def _fissure(ax, pts, mirror=False):
    q = [(-x, y) for x, y in pts] if mirror else pts
    ax.add_patch(PathPatch(smooth(q, closed=False), fill=False,
                           edgecolor=LUNG_EDGE, lw=0.9, zorder=1.8, alpha=0.9))


R_ANT = [(0.200, 1.730), (0.100, 1.595), (0.092, 1.120), (0.118, 0.880),
         (0.215, 0.745), (0.390, 0.705), (0.540, 0.770), (0.615, 0.985),
         (0.622, 1.285), (0.555, 1.520), (0.375, 1.685)]
L_ANT = [(0.200, 1.730), (0.100, 1.595), (0.094, 1.235), (0.158, 1.120),
         (0.182, 1.000), (0.150, 0.880), (0.228, 0.752), (0.390, 0.705),
         (0.540, 0.770), (0.615, 0.985), (0.622, 1.285), (0.555, 1.520),
         (0.375, 1.685)]
POST_LUNG = [(0.200, 1.730), (0.088, 1.610), (0.082, 1.020), (0.125, 0.800),
             (0.255, 0.715), (0.430, 0.710), (0.565, 0.790), (0.620, 1.010),
             (0.625, 1.300), (0.558, 1.525), (0.378, 1.688)]


def lungs_anterior(ax):
    _lung(ax, R_ANT, mirror=True)          # patient's right, viewer's left
    _lung(ax, L_ANT)
    _fissure(ax, [(0.098, 1.108), (0.300, 1.095), (0.500, 1.068)], mirror=True)
    _fissure(ax, [(0.615, 1.225), (0.420, 0.985), (0.215, 0.778)], mirror=True)
    _fissure(ax, [(0.615, 1.225), (0.425, 0.995), (0.235, 0.792)])


def lungs_posterior(ax):
    _lung(ax, POST_LUNG)
    _lung(ax, POST_LUNG, mirror=True)
    for m in (False, True):
        _fissure(ax, [(0.085, 1.385), (0.350, 1.215), (0.615, 0.990)], mirror=m)


def anterior(ax, app=False):
    stage(ax, xlim=(-0.86, 0.86))
    body(ax); lungs_anterior(ax); clavicles(ax)
    ribs(ax, [ICS2, 1.310, 1.155, 1.000, 0.855])
    sternum(ax, angle_y=ICS2)
    vline(ax, -MCL, 1.62, 0.80); vline(ax, MCL, 1.62, 0.80)
    vline(ax, -MAL, 1.34, 0.86); vline(ax, MAL, 1.34, 0.86)
    orient(ax, "R", "L")

    pos = {t: (x, y) for t, x, y in ANT}
    seq(ax, pos["Tc"], pos["1"], rad=0.22)
    seq(ax, pos["1"], pos["2"], rad=0.34)
    seq(ax, pos["2"], pos["3"], rad=0.30)
    seq(ax, pos["3"], pos["4"], rad=-0.28)

    for t, x, y in ANT:
        point(ax, x, y, t, fc=SECONDARY if t == "Tc" else PRIMARY,
              r=0.062 if t == "Tc" else 0.058, fs=6.2 if t == "Tc" else 7.4)

    ax.text(0, 2.16, "LUNG MODE  ·  anterior  ·  Tc to 4", ha="center", fontsize=9.0,
            family=SERIF, color=PRIMARY, fontweight="bold")
    ax.text(-MCL, 0.76, "midclavicular", ha="center", va="top", fontsize=6.5,
            family=SERIF, color=GREY, style="italic")
    ax.text(MAL - 0.01, 0.76, "mid-axillary", ha="center", va="top", fontsize=6.5,
            family=SERIF, color=GREY, style="italic")
    ax.text(0, 0.47,
            "Shaded: the lungs, with their fissures.\nSites 3 and 4 lie on the side of the chest,\nreached with the patient's arm raised.",
            ha="center", va="top", fontsize=6.7, family=SERIF, color=GREY,
            style="italic", linespacing=1.5)


POST9 = [("5", 0.130, 1.465), ("6", -0.130, 1.465), ("7", 0.300, LOW_Y), ("8", -0.300, LOW_Y)]


def posterior(ax, app=False, nine=False):
    """nine=True draws the planned nine-site scheme (interscapular pair added)."""
    stage(ax, xlim=(-0.86, 0.86))
    body(ax); lungs_posterior(ax)
    # spine with vertebral bodies
    ax.plot([0, 0], [1.70, 0.60], color=BONE, lw=1.6, zorder=2)
    for i in range(11):
        y = 1.68 - i * 0.105
        ax.plot([-0.034, 0.034], [y, y], color=BONE, lw=0.8, zorder=2)
    # posterior ribs, flatter than the anterior ones
    for k, y in enumerate([1.56, 1.42, 1.28, 1.14, 1.00, 0.86]):
        for sgn in (-1, 1):
            ax.add_patch(PathPatch(
                smooth([(sgn * 0.040, y), (sgn * 0.260, y - 0.045),
                        (sgn * 0.470, y - 0.130),
                        (sgn * (0.625 - 0.028 * k), y - 0.250)], closed=False),
                fill=False, edgecolor=BONE, lw=1.1, zorder=2, capstyle="round"))
    # scapulae
    for sgn in (-1, 1):
        ax.add_patch(PathPatch(
            smooth([(sgn * 0.225, 1.572), (sgn * 0.520, 1.545),
                    (sgn * 0.440, 1.315), (sgn * 0.305, 1.175),
                    (sgn * 0.235, 1.345)], closed=True),
            facecolor="#FFFFFF", edgecolor=BONE, lw=1.2, zorder=3, alpha=0.90))
        ax.text(sgn * 0.360, 1.405, "scapula", ha="center", va="center",
                fontsize=6.0, family=SERIF, color="#D7AABF", style="italic",
                zorder=3.5)
    orient(ax, "L", "R")

    sites = POST9 if nine else POST
    pos = {t: (x, y) for t, x, y in sites}
    seq(ax, pos["5"], pos["6"], rad=-0.30)
    if nine:
        seq(ax, pos["6"], pos["7"], rad=-0.22)
        seq(ax, pos["7"], pos["8"], rad=-0.30)
    for t, x, y in sites:
        point(ax, x, y, t)

    for y, lab in (((1.465, "T3–T4"),) if nine else ()) + ((LOW_Y, "T8–T10"),):
        ax.plot([-0.74, -0.68], [y, y], color=GREY, lw=0.8, zorder=2)
        ax.text(-0.76, y, lab, ha="right", va="center", fontsize=6.9,
                family=SERIF, color=GREY, style="italic")

    ax.text(0, 2.16, "LUNG MODE  ·  posterior  ·  " + ("5 to 8" if nine else "5 and 6"), ha="center", fontsize=9.0,
            family=SERIF, color=PRIMARY, fontweight="bold")
    ax.text(0, 0.47,
            "Most of the lung surface is reached from the back.\nThe oblique fissure divides the upper lobe above\nfrom the lower lobe below.",
            ha="center", va="top", fontsize=6.7, family=SERIF, color=GREY,
            style="italic", linespacing=1.5)


def panel(ax):
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.text(0.012, 0.988, "LISTENING SEQUENCE", fontsize=9.6, family=SERIF,
            color=PRIMARY, fontweight="bold", va="top")
    ax.text(0.012, 0.944,
            "Top to bottom, right against left at every level. Twenty seconds at each site.",
            fontsize=7.6, family=SERIF, color=GREY, style="italic", va="top")

    y = 0.878
    for tag, name, where, region in ROWS:
        if tag == "head":
            y -= 0.012
            ax.text(0.012, y, name, fontsize=7.5, family=SERIF, color=SECONDARY,
                    fontweight="bold", va="center")
            ax.plot([0.012, 0.992], [y - 0.026, y - 0.026], color="#F0DCE5", lw=0.9)
            y -= 0.056
            continue
        ax.add_patch(Circle((0.030, y), 0.0205, facecolor=PRIMARY, edgecolor="none",
                            transform=ax.transAxes, zorder=4))
        ax.text(0.030, y, tag, ha="center", va="center",
                fontsize=6.1 if tag == "Tc" else 7.2, color="white",
                family=SERIF, fontweight="bold", zorder=5)
        ax.text(0.070, y, name, fontsize=8.0, family=SERIF, color=PRIMARY,
                fontweight="bold", va="center")
        ax.text(0.250, y, where, fontsize=7.9, family=SERIF, color=TEXT, va="center")
        ax.text(0.790, y, region, fontsize=7.5, family=SERIF, color=GREY,
                style="italic", va="center")
        y -= 0.053

    ax.plot([0.012, 0.992], [0.112, 0.112], color="#EBD3DF", lw=1.0)
    ax.text(0.012, 0.090,
            "The patient breathes through an open mouth, somewhat deeper than at rest, for at least one full inspiration\n"
            "and expiration at each site. Right and left are recorded as a pair at every level before the sequence moves\n"
            "down, so that asymmetry between the sides appears in adjacent records. The chest piece must touch skin.",
            fontsize=7.3, family=SERIF, color=TEXT, va="top", linespacing=1.65)


if __name__ == "__main__":
    fig = plt.figure(figsize=(13.0, 5.05))
    gs = GridSpec(1, 3, width_ratios=[1.0, 1.0, 1.72], wspace=0.015,
                  left=0.004, right=0.996, top=0.996, bottom=0.004)
    anterior(fig.add_subplot(gs[0]))
    posterior(fig.add_subplot(gs[1]))
    panel(fig.add_subplot(gs[2]))
    fig.savefig(OUT + "ref_lung_sequence.png", dpi=260, bbox_inches="tight",
                pad_inches=0.08, facecolor="white")
    plt.close(fig)

    for name, fn in (("app_lung_anterior.png", anterior),
                     ("app_lung_posterior.png", posterior)):
        fig = plt.figure(figsize=(5.0, 5.2))
        fn(fig.add_axes([0.02, 0.02, 0.96, 0.96]), app=True)
        fig.savefig(OUT + name, dpi=320, bbox_inches="tight", pad_inches=0.10,
                    facecolor="white")
        plt.close(fig)

    # both views side by side, sized for the concept note
    fig = plt.figure(figsize=(7.9, 4.35))
    gs2 = GridSpec(1, 2, wspace=0.015, left=0.005, right=0.995, top=0.995,
                   bottom=0.005)
    anterior(fig.add_subplot(gs2[0]), app=True)
    posterior(fig.add_subplot(gs2[1]), app=True)
    fig.savefig(OUT + "fig_lung_doc.png", dpi=300, bbox_inches="tight",
                pad_inches=0.08, facecolor="white")
    plt.close(fig)
    print("lung figures written")
