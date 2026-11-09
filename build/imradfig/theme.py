"""Shared theme for the Resondi IMRaD figures.

Rose family carried over from the app theme (#FFF5F9) and the concept note.
The sequential ramp is lightness-monotonic (L* 21 -> 83, min step 13.1), so
its steps stay separable in greyscale print as well as on screen. TEAL is the
one non-rose data colour; it was re-stepped from #0F7B76 to #0E8F86 so the
rose/teal pair clears the CVD and chroma checks.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PRIMARY   = "#8E2A52"
SECONDARY = "#B5537E"
DEEP      = "#5E1636"
MID       = "#D189A8"
LIGHT     = "#F0C3D5"
PALE      = "#FBE9F0"
TEAL      = "#0E8F86"
INK       = "#3A2730"
GREY      = "#9C8490"
RULE      = "#E6CCD8"
SURFACE   = "#FFFFFF"

RAMP = [DEEP, PRIMARY, SECONDARY, MID, LIGHT]
SERIF = "DejaVu Serif"

plt.rcParams.update({
    "font.family": SERIF,
    "text.color": INK,
    "axes.labelcolor": INK,
    "xtick.color": GREY,
    "ytick.color": GREY,
    "axes.edgecolor": RULE,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})


def strip(ax, keep=("left",), grid=None):
    """Recessive axes: drop spines, optional single-direction grid."""
    for s in ("top", "right", "bottom", "left"):
        ax.spines[s].set_visible(s in keep)
        if s in keep:
            ax.spines[s].set_color(RULE)
    if grid:
        ax.grid(axis=grid, color=RULE, lw=0.7, alpha=0.9, zorder=0)
        ax.set_axisbelow(True)


def save(fig, path, dpi=300):
    fig.savefig(path, dpi=dpi, bbox_inches="tight", pad_inches=0.06,
                facecolor=SURFACE)
    plt.close(fig)
    from PIL import Image
    im = Image.open(path)
    print(f"  {path.split('/')[-1]:34} {im.size[0]}x{im.size[1]}  "
          f"aspect {im.size[1]/im.size[0]:.3f}")
