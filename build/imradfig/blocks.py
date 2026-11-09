"""Rounded-box / arrow primitives for the Resondi flow diagrams."""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from theme import *


WIDTH_IN = 6.05          # the document's text width; every diagram is drawn
                         # at this size so font sizes are REAL points on the
                         # printed page rather than points on a 19-inch canvas


def canvas(px, py, width_in=WIDTH_IN, dpi=300):
    """Coordinate space stays in `px` units; the figure is width_in inches.

    scale = px / width_in, so a fontsize of 9 is 9pt on the page.
    """
    scale = px / width_in
    fig = plt.figure(figsize=(width_in, py / scale), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, px); ax.set_ylim(0, py); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), px, py, facecolor=SURFACE, zorder=0))
    return fig, ax


def upp(ax):
    """Canvas units per typographic point for this axes."""
    x0, x1 = ax.get_xlim()
    return (x1 - x0) / (ax.figure.get_size_inches()[0] * 72.0)


def text_w(ax, text, pt, bold=False):
    """Width of the longest line of `text`, in canvas units."""
    fig = ax.figure; fig.canvas.draw()
    longest = max(text.split("\n"), key=len)
    t = ax.text(0, 0, longest, fontsize=pt, family=SERIF,
                fontweight="bold" if bold else "normal", alpha=0)
    bb = t.get_window_extent(fig.canvas.get_renderer()); t.remove()
    inv = ax.transData.inverted()
    return inv.transform((bb.x1, bb.y1))[0] - inv.transform((bb.x0, bb.y0))[0]


def _fit(ax, text, max_w_units, start_pt, min_pt=4.6, bold=False):
    """Largest point size at or below start_pt whose text fits max_w_units.

    Measured against the real renderer, so it accounts for the actual font
    rather than a guessed average character width.
    """
    fig = ax.figure
    fig.canvas.draw()
    inv = ax.transData.inverted()
    pt = start_pt
    while pt > min_pt:
        t = ax.text(0, 0, text, fontsize=pt, family=SERIF,
                    fontweight="bold" if bold else "normal", alpha=0)
        bb = t.get_window_extent(fig.canvas.get_renderer())
        t.remove()
        x0, _ = inv.transform((bb.x0, bb.y0)); x1, _ = inv.transform((bb.x1, bb.y1))
        widest = max((x1 - x0) / max(1, text.count("\n") + 1), x1 - x0) \
            if "\n" not in text else max(
                (lambda l: l)(x1 - x0) / (text.count("\n") + 1), 0)
        # measure the longest single line properly
        longest = max(text.split("\n"), key=len)
        t = ax.text(0, 0, longest, fontsize=pt, family=SERIF,
                    fontweight="bold" if bold else "normal", alpha=0)
        bb = t.get_window_extent(fig.canvas.get_renderer()); t.remove()
        x0, _ = inv.transform((bb.x0, bb.y0)); x1, _ = inv.transform((bb.x1, bb.y1))
        if (x1 - x0) <= max_w_units:
            return pt
        pt -= 0.2
    return min_pt


def group(ax, x, y, w, h, label=None, fs=7.4):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0,rounding_size=10",
                 facecolor=PALE, edgecolor="none", zorder=1))
    if label:
        ax.text(x + w / 2, y + h + 11, label, ha="center", va="bottom",
                fontsize=fs, color=SECONDARY, fontweight="bold",
                family=SERIF, zorder=4)


def box(ax, x, y, w, h, title, sub=None, *, fill=SURFACE, edge=PRIMARY,
        lw=1.8, ts=8.2, ss=6.4, tc=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0,rounding_size=7",
                 facecolor=fill, edgecolor=edge, linewidth=lw, zorder=2))
    pad = w * 0.10
    ts = _fit(ax, title, w - pad, ts, bold=True)
    if sub:
        ss = _fit(ax, sub, w - pad, ss)
    U = upp(ax)                                   # units per point
    nl = title.count("\n") + 1
    th = ts * 1.18 * nl * U                       # title block height
    sh = (ss * 1.18 * (sub.count("\n") + 1) * U) if sub else 0
    gap = 3.2 * U if sub else 0
    top = y + h / 2 + (th + gap + sh) / 2         # top of the whole text block
    ax.text(x + w / 2, top - th / 2, title, ha="center", va="center",
            fontsize=ts, fontweight="bold", color=tc or INK, family=SERIF,
            zorder=3, linespacing=1.18)
    if sub:
        ax.text(x + w / 2, top - th - gap - sh / 2, sub, ha="center",
                va="center", fontsize=ss, color=GREY, family=SERIF,
                zorder=3, linespacing=1.18)


def arrow(ax, p0, p1, *, color=None, lw=2.0, rad=0.0, ls="-"):
    ax.add_patch(FancyArrowPatch(p0, p1,
                 arrowstyle="-|>", mutation_scale=7,
                 connectionstyle=f"arc3,rad={rad}",
                 color=color or PRIMARY, lw=lw, linestyle=ls,
                 shrinkA=0, shrinkB=0, zorder=3))


def caption(ax, px, text, fs=6.6, y=14):
    ax.text(px / 2, y, text, ha="center", va="bottom", fontsize=fs,
            color=GREY, style="italic", family=SERIF)
