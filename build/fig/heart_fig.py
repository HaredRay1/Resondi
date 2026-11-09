"""Heart Mode — instructional auscultation sequence.

Landmarks after Oliveira et al. (2022). Erb's point is included as an optional
capture that is filed for the practitioner but not passed to the classifier.
"""
import os as _os
_BUILD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))).replace(chr(92), '/')
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch, Circle, FancyArrowPatch
from matplotlib.gridspec import GridSpec

from anat import (PRIMARY, SECONDARY, ACCENT, GREY, TEXT, SERIF,
                  smooth, body, clavicles, sternum, ribs, vline, point, seq,
                  orient, stage)

OUT = _BUILD + "/fig/"
VALVE = "#5A1830"

ICS = {2: 1.465, 3: 1.310, 4: 1.155, 5: 1.000}
SB, MCL = 0.128, 0.42

#    n  tag   x      y        name            landmark                          guidance
POINTS = [
    (1, "A", -SB, ICS[2], "AORTIC", "2nd ICS, right sternal border",
     "Diaphragm. The second heart sound (A2), and the\nmurmur of aortic stenosis radiating to the neck."),
    (2, "P", SB, ICS[2], "PULMONIC", "2nd ICS, left sternal border",
     "Diaphragm. Splitting of the second heart sound,\nand pulmonary flow murmurs."),
    (3, "E", SB, ICS[3], "ERB'S POINT", "3rd ICS, left sternal border",
     "Diaphragm. The best single point for S1 and S2 together,\nand for aortic regurgitation. Captured, not classified."),
    (4, "T", SB, ICS[5] + 0.075, "TRICUSPID", "4th–5th ICS, left lower sternal border",
     "Diaphragm, then bell. The fourth heart sound,\ntricuspid murmurs, ventricular septal defect."),
    (5, "M", MCL, 0.975, "MITRAL / APEX", "5th ICS, left midclavicular line",
     "Diaphragm, then bell, with the patient rolled onto the left side.\nThe third heart sound and mitral murmurs."),
]
POS = {n: (x, y) for n, _t, x, y, *_ in POINTS}

# where each valve actually sits, and the surface point its sound reaches
VALVES = [("pulmonary", 0.058, 1.345, 2), ("aortic", 0.004, 1.280, 1),
          ("mitral", 0.100, 1.190, 5), ("tricuspid", -0.016, 1.140, 4)]


def heart_silhouette(ax):
    pts = [(-0.085, 1.300), (0.010, 1.372), (0.140, 1.352),
           (0.258, 1.262), (0.356, 1.120), (0.418, 0.998),
           (0.300, 0.948), (0.135, 0.946), (0.008, 1.000),
           (-0.082, 1.130)]
    ax.add_patch(PathPatch(smooth(pts, closed=True), facecolor="#EDA9C2",
                           edgecolor="#C4718F", lw=1.2, zorder=2.2, alpha=0.70))


def chest(ax, app=False):
    stage(ax)
    body(ax)
    clavicles(ax)
    ribs(ax, [1.465, 1.310, 1.155, 1.000, 0.855])
    heart_silhouette(ax)
    sternum(ax, angle_y=1.465)
    vline(ax, -MCL, 1.66, 0.80)
    vline(ax, MCL, 1.66, 0.80)
    orient(ax, "R", "L")

    for _name, vx, vy, tgt in VALVES:
        ax.add_patch(FancyArrowPatch(
            (vx, vy), POS[tgt], arrowstyle="-", color="#9E5C78", lw=1.1,
            linestyle=(0, (2.4, 1.9)), connectionstyle="arc3,rad=0.16",
            shrinkA=2, shrinkB=8, zorder=4.0))
    for _name, vx, vy, _t in VALVES:
        ax.add_patch(Circle((vx, vy), 0.019, facecolor=VALVE,
                            edgecolor="white", lw=0.8, zorder=4.4))

    # listening order, base to apex, routed clear of the markers
    seq(ax, POS[1], POS[2], rad=0.62)
    seq(ax, POS[2], POS[3], rad=-1.05)
    seq(ax, POS[3], POS[4], rad=-0.72)
    seq(ax, POS[4], POS[5], rad=-0.55)

    for n, tag, x, y, *_ in POINTS:
        point(ax, x, y, n, fc=PRIMARY if tag != "E" else "#C07E9B")
        dx = 0.082 if x >= 0 else -0.082
        ax.text(x + dx, y + 0.052, tag, ha="left" if x >= 0 else "right",
                va="center", fontsize=7.8, family=SERIF, color=PRIMARY,
                fontweight="bold", zorder=7)

    for k, y in ICS.items():
        ax.plot([-0.80, -0.74], [y, y], color=GREY, lw=0.8, zorder=2)
        ax.text(-0.82, y, str(k), ha="right", va="center", fontsize=7.2,
                family=SERIF, color=GREY, style="italic")
    ax.text(-0.82, ICS[2] + 0.135, "ICS", ha="right", va="center", fontsize=7.2,
            family=SERIF, color=GREY, style="italic", fontweight="bold")
    ax.text(MCL, 0.74, "midclavicular\nline", ha="center", va="top",
            fontsize=6.7, family=SERIF, color=GREY, style="italic",
            linespacing=1.3)

    ax.text(0, 2.10, "HEART MODE  ·  anterior  ·  A to M", ha="center",
            fontsize=9.0, family=SERIF, color=PRIMARY, fontweight="bold")
    ax.text(0, 0.455,
            "The rose bar is the sternal angle, the landmark\n"
            "for the second rib. Dark dots mark where the valves\n"
            "actually lie; the fine lines run to the surface point\n"
            "where each is heard, downstream in the flow.",
            ha="center", va="top", fontsize=6.7, family=SERIF,
            color=GREY, style="italic", linespacing=1.5)


def panel(ax):
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.text(0.012, 0.985, "LISTENING SEQUENCE", fontsize=9.6, family=SERIF,
            color=PRIMARY, fontweight="bold", va="top")
    ax.text(0.012, 0.938, "Base to apex. Fifteen seconds at each point.",
            fontsize=7.7, family=SERIF, color=GREY, style="italic", va="top")

    y = 0.868
    for n, tag, _x, _y, name, where, how in POINTS:
        ax.add_patch(Circle((0.030, y), 0.0215, facecolor=PRIMARY,
                            edgecolor="none", transform=ax.transAxes, zorder=4))
        ax.text(0.030, y, str(n), ha="center", va="center", fontsize=7.4,
                color="white", family=SERIF, fontweight="bold", zorder=5)
        ax.text(0.072, y, name, fontsize=8.5, family=SERIF, color=PRIMARY,
                fontweight="bold", va="center")
        ax.text(0.335, y, where, fontsize=8.0, family=SERIF, color=TEXT,
                va="center")
        ax.text(0.072, y - 0.042, how, fontsize=7.2, family=SERIF, color=GREY,
                va="top", linespacing=1.5)
        y -= 0.156

    ax.plot([0.012, 0.992], [0.082, 0.082], color="#EBD3DF", lw=1.0)
    ax.text(0.012, 0.062,
            "Patient supine for points 1 to 4, then rolled onto the left side for point 5, which brings the apex\n"
            "against the chest wall. Diaphragm for high-pitched sounds; the bell, applied lightly, for low-pitched\n"
            "ones such as S3, S4 and mitral stenosis. The chest piece must touch skin, never clothing.",
            fontsize=7.3, family=SERIF, color=TEXT, va="top", linespacing=1.6)


if __name__ == "__main__":
    fig = plt.figure(figsize=(11.4, 5.05))
    gs = GridSpec(1, 2, width_ratios=[1.0, 1.46], wspace=0.015,
                  left=0.004, right=0.996, top=0.996, bottom=0.004)
    chest(fig.add_subplot(gs[0]))
    panel(fig.add_subplot(gs[1]))
    fig.savefig(OUT + "ref_heart_sequence.png", dpi=260, bbox_inches="tight",
                pad_inches=0.08, facecolor="white")
    plt.close(fig)

    for name, dpi in (("app_heart.png", 320), ("fig_heart_doc.png", 300)):
        fig = plt.figure(figsize=(5.0, 5.2))
        chest(fig.add_axes([0.02, 0.02, 0.96, 0.96]), app=True)
        fig.savefig(OUT + name, dpi=dpi, bbox_inches="tight", pad_inches=0.10,
                    facecolor="white")
        plt.close(fig)
    print("heart figures written")
