"""Shared style for the Resondi IMRaD figures.

Palette is the app theme already used across the concept note figures
(anat.py). Two deliberate choices, following the dataviz rules:

* Nearly every figure here is a diagram or a SINGLE-series chart, so no
  categorical palette is needed — one rose plus ink and grey.
* Recording clarity is ORDINAL (good > acceptable > poor), so it uses a
  sequential ramp of one hue, light to dark, not four brand colours used
  categorically. The two brand roses fail CVD separation against each other
  and must never encode different categories.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PRIMARY   = "#8E2A52"    # deep rose
SECONDARY = "#B5537E"    # mid rose
LIGHT     = "#F8DCE7"    # pale rose fill
MID       = "#E0A5BE"    # between LIGHT and SECONDARY
EDGE      = "#C98EA9"
ACCENT    = "#0F7B76"    # teal, only for a genuinely separate layer
TEXT      = "#3A2730"
GREY      = "#9C8490"
RULE      = "#EADCE3"
SURFACE   = "#FFFFFF"

# sequential, light -> dark. Monotone in lightness; for ordinal data only.
SEQ3 = [LIGHT, MID, PRIMARY]
SEQ4 = [LIGHT, MID, SECONDARY, PRIMARY]

FONT = "DejaVu Sans"
plt.rcParams.update({
    "font.family": FONT,
    "text.color": TEXT,
    "axes.labelcolor": TEXT,
    "xtick.color": TEXT,
    "ytick.color": TEXT,
    "axes.edgecolor": RULE,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})


def figure(w, h, dpi=300):
    fig = plt.figure(figsize=(w, h), dpi=dpi)
    return fig


def title(ax, text, sub=None, x=0.0, y=1.0):
    ax.text(x, y, text, transform=ax.transAxes, fontsize=12.5, fontweight="bold",
            color=PRIMARY, va="bottom", ha="left")
    if sub:
        ax.text(x, y - 0.065, sub, transform=ax.transAxes, fontsize=9,
                color=GREY, va="bottom", ha="left")


def strip_axes(ax, keep=("left", "bottom")):
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(s in keep)
    ax.tick_params(length=0, labelsize=9)
    ax.grid(False)


def save(fig, path, pad=0.14):
    fig.savefig(path, bbox_inches="tight", pad_inches=pad,
                facecolor=SURFACE)
    plt.close(fig)
    from PIL import Image
    im = Image.open(path)
    print(f"  {path.split('/')[-1]:<34} {im.size[0]}x{im.size[1]}")
    return im.size
