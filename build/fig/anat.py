"""Shared anatomical drawing primitives for the Resondi auscultation figures."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
from matplotlib.patches import Circle, PathPatch, FancyArrowPatch
from matplotlib.path import Path
from matplotlib.colors import LinearSegmentedColormap

# Resondi app theme, built out from the app's own theme-color, #FFF5F9.
PRIMARY = "#8E2A52"          # deep rose: site markers, headings
SECONDARY = "#B5537E"        # mid rose: section headers, landmark rules
LIGHT = "#F8DCE7"            # pale rose fill
ACCENT = "#0F7B76"           # teal: the listening sequence, so it reads
                             # as a separate layer from the brand rose
GREY, TEXT = "#9C8490", "#3A2730"
EDGE = "#C98EA9"             # body outline
BONE = "#E6C6D4"             # ribs, sternum, scapulae, spine
SERIF = "serif"
SKIN_CMAP = LinearSegmentedColormap.from_list(
    "skin", ["#FBE6EE", "#FFF5F9", "#FFFCFD"])


def smooth(pts, closed=True):
    """Catmull-Rom spline through pts, returned as a cubic Bezier Path."""
    pts = list(pts)
    n = len(pts)
    if closed:
        at = lambda i: pts[i % n]
        last = n
    else:                      # clamp, so an open curve does not flare at its tail
        at = lambda i: pts[min(max(i, 0), n - 1)]
        last = n - 1
    verts, codes = [pts[0]], [Path.MOVETO]
    for i in range(last):
        p0, p1 = at(i - 1), at(i)
        p2, p3 = at(i + 1), at(i + 2)
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        verts += [c1, c2, p2]
        codes += [Path.CURVE4] * 3
    return Path(verts, codes)


# half-outline, from the neck down to the lower costal margin; mirrored on draw
_HALF = [
    (0.00, 2.10), (0.105, 2.08), (0.145, 1.955),
    (0.270, 1.885), (0.440, 1.825), (0.600, 1.755),
    (0.682, 1.640), (0.700, 1.500), (0.688, 1.345),
    (0.660, 1.170), (0.632, 0.980), (0.608, 0.790),
    (0.592, 0.690), (0.548, 0.616), (0.432, 0.572),
    (0.228, 0.552), (0.000, 0.546),
]


def torso_path():
    right = _HALF
    left = [(-x, y) for x, y in reversed(_HALF[1:-1])]
    return smooth(right + left, closed=True)


def body(ax, shade=True):
    """Torso silhouette with a soft vertical gradient so it reads as a body."""
    path = torso_path()
    patch = PathPatch(path, facecolor="#FFF8FB", edgecolor=EDGE,
                      linewidth=1.8, zorder=1, joinstyle="round")
    ax.add_patch(patch)
    if shade:
        g = np.linspace(0, 1, 256).reshape(-1, 1)
        im = ax.imshow(g, extent=[-0.75, 0.75, 0.53, 2.12], origin="upper",
                       cmap=SKIN_CMAP, aspect="auto", zorder=1.1,
                       interpolation="bilinear")
        im.set_clip_path(patch)
    return patch


def clavicles(ax):
    for s in (-1, 1):
        ax.add_patch(PathPatch(
            smooth([(s * 0.045, 1.700), (s * 0.230, 1.780), (s * 0.420, 1.772),
                    (s * 0.580, 1.690)], closed=False),
            fill=False, edgecolor=BONE, lw=3.0, zorder=2,
            capstyle="round"))


def sternum(ax, angle_y=1.50):
    """Manubrium, body and xiphoid, with the sternal angle marked."""
    ax.add_patch(PathPatch(
        smooth([(-0.070, 1.640), (0.070, 1.640), (0.074, 1.545),
                (0.058, 1.430), (0.046, 1.180), (0.030, 1.020),
                (0.000, 0.975), (-0.030, 1.020), (-0.046, 1.180),
                (-0.058, 1.430), (-0.074, 1.545)], closed=True),
        facecolor="#FFFFFF", edgecolor=BONE, lw=1.3, zorder=2.5, alpha=0.95))
    ax.plot([-0.105, 0.105], [angle_y, angle_y], color=SECONDARY, lw=1.7, zorder=4)


def ribs(ax, ys, x_out=0.64, lift=0.085, fall=0.20, lw=1.5, color=BONE):
    """Anterior ribs: cartilage rises off the sternum, then the rib falls away."""
    cart = "#F0D6E1"
    for k, y in enumerate(ys):
        xo = x_out - 0.035 * k
        for s in (-1, 1):
            ax.add_patch(PathPatch(
                smooth([(s * 0.055, y), (s * 0.135, y + lift * 0.72),
                        (s * 0.225, y + lift)], closed=False),
                fill=False, edgecolor=cart, lw=lw + 0.5, zorder=2,
                capstyle="round"))
            ax.add_patch(PathPatch(
                smooth([(s * 0.225, y + lift), (s * 0.400, y + lift * 0.30),
                        (s * (0.545 - 0.028 * k), y - fall * 0.42),
                        (s * xo, y - fall - 0.012 * k)], closed=False),
                fill=False, edgecolor=color, lw=lw, zorder=2,
                capstyle="round"))


def vline(ax, x, y0, y1, label=None, color=EDGE, fs=7.0):
    ax.plot([x, x], [y0, y1], color=color, lw=0.9, ls=(0, (2.2, 2.6)), zorder=2)
    if label:
        ax.text(x, y1 + 0.05, label, ha="center", va="bottom", fontsize=fs,
                family=SERIF, color=GREY, style="italic")


def point(ax, x, y, n, fc=PRIMARY, r=0.058, fs=7.4):
    ax.add_patch(Circle((x, y), r, facecolor=fc, edgecolor="white",
                        linewidth=1.7, zorder=6))
    ax.text(x, y, str(n), ha="center", va="center", fontsize=fs, color="white",
            family=SERIF, fontweight="bold", zorder=7)


def seq(ax, p1, p2, rad=0.0, color=ACCENT, lw=1.5, shrink=7):
    ax.add_patch(FancyArrowPatch(
        p1, p2, arrowstyle="-|>", mutation_scale=12, color=color, lw=lw,
        linestyle=(0, (3.4, 2.0)), connectionstyle=f"arc3,rad={rad}",
        shrinkA=shrink, shrinkB=shrink, zorder=5))


def orient(ax, left, right, y=1.655, x=0.515):
    for xx, t in ((-x, left), (x, right)):
        ax.text(xx, y, t, ha="center", va="center", fontsize=9.5,
                family=SERIF, color="#D7AABF", fontweight="bold", zorder=4)


def stage(ax, xlim=(-0.95, 0.95), ylim=(0.33, 2.16)):
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.axis("off"); ax.set_aspect("equal")
