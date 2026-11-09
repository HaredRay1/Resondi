"""App-ready auscultation guide: anatomy plates plus site coordinates.

The document figures bake the numbers, the arrows and the captions into the
picture. An app should not: the markers have to light up as the user moves
through the sequence, the copy has to be selectable and translatable, and a
tap target has to be a real element. So this exports two things.

  * a plate per view - torso, bones, organ, reference lines, nothing else,
    on a transparent background, as SVG and as PNG at 1x / 2x / 3x
  * resondi-sites.json - every site with its position given as a percentage
    of the plate box, so the app can absolutely-position its own markers

Because the axes fill the figure exactly and the data limits are fixed, the
percentage of a data point is an exact property of the export, not an
estimate taken off the image.
"""
import os as _os
_BUILD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))).replace(chr(92), '/')
import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from anat import (BONE, EDGE, SERIF, smooth, body, clavicles, sternum, ribs,
                  vline, orient)
from matplotlib.patches import PathPatch
import heart_fig as H
import lung_fig as L

plt.rcParams["svg.fonttype"] = "path"      # no font dependency in the SVG

OUT = pathlib.Path(_BUILD + "/app-assets")
OUT.mkdir(exist_ok=True)

XLIM = (-0.80, 0.80)
YLIM = (0.50, 2.16)
DW, DH = XLIM[1] - XLIM[0], YLIM[1] - YLIM[0]
BASE_W = 600                                # 1x width in CSS pixels
# Inches per data unit. Line widths and type are specified in points, so this
# fixes how heavy the strokes and the marker numerals look against the body;
# it matches the scale the document figures were drawn at.
SCALE_IN = 2.8


def pct(x, y):
    """Data point -> (left%, top%) of the exported plate."""
    return (round((x - XLIM[0]) / DW * 100, 3),
            round((YLIM[1] - y) / DH * 100, 3))


def framed(ax):
    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)
    ax.set_aspect("equal")
    ax.axis("off")


# ── plates ───────────────────────────────────────────────────────────────
def plate_heart(ax):
    framed(ax)
    body(ax)
    clavicles(ax)
    ribs(ax, [1.465, 1.310, 1.155, 1.000, 0.855])
    H.heart_silhouette(ax)
    sternum(ax, angle_y=1.465)
    vline(ax, -H.MCL, 1.66, 0.80)
    vline(ax, H.MCL, 1.66, 0.80)
    orient(ax, "R", "L")


def plate_lung_anterior(ax):
    framed(ax)
    body(ax)
    L.lungs_anterior(ax)
    clavicles(ax)
    ribs(ax, [L.ICS2, 1.310, 1.155, 1.000, 0.855])
    sternum(ax, angle_y=L.ICS2)
    vline(ax, -L.MCL, 1.62, 0.80)
    vline(ax, L.MCL, 1.62, 0.80)
    vline(ax, -L.MAL, 1.34, 0.86)
    vline(ax, L.MAL, 1.34, 0.86)
    orient(ax, "R", "L")


def plate_lung_posterior(ax):
    framed(ax)
    body(ax)
    L.lungs_posterior(ax)
    ax.plot([0, 0], [1.70, 0.60], color=BONE, lw=1.6, zorder=2)
    for i in range(11):
        y = 1.68 - i * 0.105
        ax.plot([-0.034, 0.034], [y, y], color=BONE, lw=0.8, zorder=2)
    for k, y in enumerate([1.56, 1.42, 1.28, 1.14, 1.00, 0.86]):
        for s in (-1, 1):
            ax.add_patch(PathPatch(
                smooth([(s * 0.040, y), (s * 0.260, y - 0.045),
                        (s * 0.470, y - 0.130),
                        (s * (0.625 - 0.028 * k), y - 0.250)], closed=False),
                fill=False, edgecolor=BONE, lw=1.1, zorder=2,
                capstyle="round"))
    for s in (-1, 1):                       # scapulae, unlabelled
        ax.add_patch(PathPatch(
            smooth([(s * 0.225, 1.572), (s * 0.520, 1.545),
                    (s * 0.440, 1.315), (s * 0.305, 1.175),
                    (s * 0.235, 1.345)], closed=True),
            facecolor="#FFFFFF", edgecolor=BONE, lw=1.2, zorder=3, alpha=0.90))
    orient(ax, "L", "R")


def export(name, draw):
    # figsize carries the data aspect exactly, so dpi alone sets the pixels
    figsize = (DW * SCALE_IN, DH * SCALE_IN)
    for suffix, scale in (("", 1), ("@2x", 2), ("@3x", 3)):
        dpi = BASE_W * scale / figsize[0]
        fig = plt.figure(figsize=figsize, dpi=dpi)
        draw(fig.add_axes([0, 0, 1, 1]))
        fig.savefig(OUT / f"{name}{suffix}.png", dpi=dpi, transparent=True,
                    pad_inches=0)
        plt.close(fig)
    fig = plt.figure(figsize=figsize)
    draw(fig.add_axes([0, 0, 1, 1]))
    fig.savefig(OUT / f"{name}.svg", transparent=True, pad_inches=0,
                format="svg")
    plt.close(fig)


# ── site data ────────────────────────────────────────────────────────────
HEART_SITES = [
    dict(order=1, code="AV", tag="A", name="Aortic",
         landmark="2nd intercostal space, right sternal border",
         piece="diaphragm", seconds=15,
         listen="The second heart sound, and the murmur of aortic stenosis "
                "radiating to the neck.",
         xy=(-H.SB, H.ICS[2])),
    dict(order=2, code="PV", tag="P", name="Pulmonic",
         landmark="2nd intercostal space, left sternal border",
         piece="diaphragm", seconds=15,
         listen="Splitting of the second heart sound, and pulmonary flow "
                "murmurs.",
         xy=(H.SB, H.ICS[2])),
    dict(order=3, code="ERB", tag="E", name="Erb's point",
         landmark="3rd intercostal space, left sternal border",
         piece="diaphragm", seconds=15, optional=True,
         listen="The best single point for S1 and S2 together, and for "
                "aortic regurgitation. Captured for the practitioner, not "
                "passed to the classifier.",
         xy=(H.SB, H.ICS[3])),
    dict(order=4, code="TV", tag="T", name="Tricuspid",
         landmark="4th to 5th intercostal space, left lower sternal border",
         piece="diaphragm, then bell", seconds=15,
         listen="The fourth heart sound, tricuspid murmurs, ventricular "
                "septal defect.",
         xy=(H.SB, H.ICS[5] + 0.075)),
    dict(order=5, code="MV", tag="M", name="Mitral / apex",
         landmark="5th intercostal space, left midclavicular line",
         piece="diaphragm, then bell", seconds=15,
         position="Roll the patient onto the left side.",
         listen="The third heart sound and mitral murmurs.",
         xy=(H.MCL, 0.975)),
]

LUNG_ANT_SITES = [
    dict(order=1, code="Tc", tag="Tc", name="Trachea",
         landmark="Suprasternal notch", icbhi="Tc", seconds=20, optional=True,
         listen="Central airway reference. Stridor and transmitted upper "
                "airway sound.", xy=(0.000, 1.605)),
    dict(order=2, code="Ar", tag="1", name="Right upper, anterior",
         landmark="2nd intercostal space, right midclavicular line",
         icbhi="Ar", region="right upper lobe", seconds=20,
         listen="Right upper lobe air entry.", xy=(-L.MCL, L.ICS2)),
    dict(order=3, code="Al", tag="2", name="Left upper, anterior",
         landmark="2nd intercostal space, left midclavicular line",
         icbhi="Al", region="left upper lobe", seconds=20,
         listen="Left upper lobe air entry.", xy=(L.MCL, L.ICS2)),
    dict(order=4, code="Lr", tag="3", name="Right lateral",
         landmark="4th to 5th intercostal space, right mid-axillary line",
         icbhi="Lr", region="right middle lobe", seconds=20,
         position="Raise the patient's arm.",
         listen="Right middle lobe, the lobe most often missed.",
         xy=(-L.MAL, L.LAT_Y)),
    dict(order=5, code="Ll", tag="4", name="Left lateral",
         landmark="4th to 5th intercostal space, left mid-axillary line",
         icbhi="Ll", region="lingula", seconds=20,
         position="Raise the patient's arm.",
         listen="The lingula.", xy=(L.MAL, L.LAT_Y)),
]

LUNG_POST_SITES = [
    dict(order=6, code="Pr", tag="5", name="Right upper, posterior",
         landmark="Interscapular, T3 to T4, medial to the scapula",
         icbhi="Pr", region="right upper lobe", seconds=20,
         listen="Right upper lobe from behind.", xy=(0.135, L.UP_Y)),
    dict(order=7, code="Pl", tag="6", name="Left upper, posterior",
         landmark="Interscapular, T3 to T4, medial to the scapula",
         icbhi="Pl", region="left upper lobe", seconds=20,
         listen="Left upper lobe from behind.", xy=(-0.135, L.UP_Y)),
    dict(order=8, code="Pr-low", tag="7", name="Right lower, posterior",
         landmark="Infrascapular, T8 to T10", icbhi="Pr",
         region="right lower lobe", seconds=20,
         listen="Right lower lobe, where crackles collect.",
         xy=(0.300, L.LOW_Y)),
    dict(order=9, code="Pl-low", tag="8", name="Left lower, posterior",
         landmark="Infrascapular, T8 to T10", icbhi="Pl",
         region="left lower lobe", seconds=20,
         listen="Left lower lobe, where crackles collect.",
         xy=(-0.300, L.LOW_Y)),
]


def pack(sites):
    out = []
    for s in sites:
        s = dict(s)
        x, y = s.pop("xy")
        left, top = pct(x, y)
        s["left"] = left
        s["top"] = top
        out.append(s)
    return out


def baked(plate, sites, arcs):
    """Plate with the markers and the sequence drawn in — a fallback for
    anywhere the app cannot overlay its own elements."""
    from anat import ACCENT, PRIMARY, SECONDARY, point
    from matplotlib.patches import FancyArrowPatch

    def arrow(ax, p1, p2, rad):
        # heavier head than the document figure: at app size a 12pt head
        # disappears, and the direction of travel is the whole point
        ax.add_patch(FancyArrowPatch(
            p1, p2, arrowstyle="-|>", mutation_scale=26, color=ACCENT,
            lw=2.4, linestyle=(0, (3.0, 1.9)),
            connectionstyle=f"arc3,rad={rad}", shrinkA=11, shrinkB=13,
            zorder=5))

    def draw(ax):
        plate(ax)
        pos = {s["order"]: s["xy"] for s in sites}
        for a, b, rad in arcs:
            arrow(ax, pos[a], pos[b], rad)
        for s in sites:
            x, y = s["xy"]
            fc = SECONDARY if s.get("optional") else PRIMARY
            point(ax, x, y, s["tag"], fc=fc,
                  fs=6.2 if len(str(s["tag"])) > 1 else 7.4)
    return draw


if __name__ == "__main__":
    export("heart-anterior", plate_heart)
    export("lung-anterior", plate_lung_anterior)
    export("lung-posterior", plate_lung_posterior)

    export("heart-anterior-static",
           baked(plate_heart, HEART_SITES,
                 [(1, 2, 0.62), (2, 3, -1.05), (3, 4, -0.72), (4, 5, -0.55)]))
    export("lung-anterior-static",
           baked(plate_lung_anterior, LUNG_ANT_SITES,
                 [(1, 2, 0.22), (2, 3, 0.34), (3, 4, 0.30), (4, 5, -0.28)]))
    export("lung-posterior-static",
           baked(plate_lung_posterior, LUNG_POST_SITES,
                 [(6, 7, -0.30), (7, 8, -0.22), (8, 9, -0.26)]))

    data = {
        "note": ("left and top are percentages of the plate's own box. "
                 "Position a marker with left:<left>%, top:<top>% and "
                 "transform: translate(-50%,-50%)."),
        "plate": {"aspectRatio": round(DW / DH, 5),
                  "width": BASE_W, "height": round(BASE_W * DH / DW)},
        "theme": {"marker": "#8E2A52", "markerOptional": "#C07E9B",
                  "active": "#E91E76", "done": "#0F7B76",
                  "onMarker": "#FFFFFF", "surface": "#FFF5F9"},
        "views": {
            "heart": {"plate": "heart-anterior", "orientation": "anterior",
                      "order": "base to apex, A-P-E-T-M",
                      "sites": pack(HEART_SITES)},
            "lungAnterior": {"plate": "lung-anterior",
                             "orientation": "anterior",
                             "order": "top to bottom, right against left",
                             "sites": pack(LUNG_ANT_SITES)},
            "lungPosterior": {"plate": "lung-posterior",
                              "orientation": "posterior",
                              "order": "top to bottom, right against left",
                              "sites": pack(LUNG_POST_SITES)},
        },
    }
    (OUT / "resondi-sites.json").write_text(
        json.dumps(data, indent=2), encoding="utf-8")

    for f in sorted(OUT.iterdir()):
        print(f"{f.name:28s} {f.stat().st_size // 1024:5d} KB")
