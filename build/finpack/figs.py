"""Figures 11 and 12 for the Resondi concept note, in the Resondi rose theme.

Drawn at the width they are placed at in the document (6.0 in), so the point
sizes below are the point sizes a reader sees.
"""
import os as _os
_BUILD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))).replace(chr(92), '/')
import sys
sys.path.insert(0, _BUILD + "/finpack")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from model import ROWS, Y1, Y2, X500, OFFSET

PRIMARY, DEEP, SECONDARY = "#8E2A52", "#5E1636", "#B5537E"
REST    = "#C27396"     # validated against PRIMARY: all six checks pass
PALE, RULE = "#FBE9F0", "#E6CCD8"
INK, GREY = "#3A2730", "#8A7480"
SERIF = "DejaVu Serif"
W = 6.0

plt.rcParams.update({"font.family": SERIF, "text.color": INK,
                     "axes.edgecolor": RULE, "axes.labelcolor": INK,
                     "xtick.color": GREY, "ytick.color": GREY})

# ── Figure 11: allocation of the requirement ─────────────────────────────
rows = [
    ("Clinical validation",                    120_000, True),
    ("AI development",                         102_000, True),
    ("Contingency",                             50_000, False),
    ("Cloud infrastructure and operation",      48_000, False),
    ("Hardware refinement",                     42_000, False),
    ("Production working capital",              40_000, False),
    ("Mobile application",                      38_000, False),
    ("Intellectual property and registration",  25_000, False),
    ("Documentation and compliance",            20_000, False),
    ("Deployment and marketing",                15_000, False),
]
TOTAL = sum(r[1] for r in rows)
assert TOTAL == 500_000

fig, ax = plt.subplots(figsize=(W, 3.75), dpi=300)
n = len(rows)
for i, (name, amt, drv) in enumerate(rows):
    y = n - 1 - i
    ax.barh(y, amt, height=0.62, color=PRIMARY if drv else REST, zorder=3)
    ax.text(-3_000, y, name, ha="right", va="center", fontsize=8.2, color=INK)
    t = ax.text(amt + 2_500, y, f"₱{amt:,}", ha="left", va="center",
                fontsize=8.0, color=INK, fontweight="bold")
    ax.annotate(f"{amt / TOTAL * 100:.1f}%", xycoords=t, xy=(1, 0.5),
                xytext=(5, 0), textcoords="offset points",
                va="center", ha="left", fontsize=8.0, color=GREY)
ax.set_xlim(0, 172_000)
ax.set_ylim(-1.05, n - 0.35)
ax.axis("off")
drv = sum(r[1] for r in rows if r[2])
ax.text(172_000, -1.0, f"Darker bars: the two commitments that drive the requirement, "
        f"₱{drv:,} ({drv / TOTAL * 100:.1f}%)", ha="right", va="bottom",
        fontsize=7.4, color=GREY, style="italic")
fig.subplots_adjust(left=0.40, right=0.99, top=0.99, bottom=0.03)
fig.savefig("fig11_allocation_rose.png", facecolor="white")
plt.close(fig)

# ── Figure 12: cumulative cash contribution against the seed ─────────────
m   = [r["m"] for r in ROWS]
cum = [r["cum"] for r in ROWS]

fig, ax = plt.subplots(figsize=(W, 3.3), dpi=300)
ax.fill_between(m, cum, color=PALE, zorder=1, step=None)
ax.plot(m, cum, color=PRIMARY, lw=2.0, zorder=3, solid_capstyle="round")
ax.axhline(500_000, color=DEEP, lw=1.0, ls=(0, (4, 3)), zorder=2)
ax.text(1.0, 512_000, "₱500,000 seed", fontsize=8.0, color=DEEP, va="bottom")

# year boundary
ax.axvline(12.5, color=RULE, lw=1.0, zorder=0)
ax.text(6.5, 640_000, f"Commercial Year 1\n₱{Y1:,} in cash", ha="center",
        va="top", fontsize=7.8, color=GREY, linespacing=1.3)
ax.text(18.5, 640_000, f"Commercial Year 2\n₱{Y2:,} in cash", ha="center",
        va="top", fontsize=7.8, color=GREY, linespacing=1.3)

# crossing
xr = ROWS[X500 - 1]
ax.plot([X500], [xr["cum"]], "o", ms=7, color=PRIMARY, mec="white", mew=1.6, zorder=5)
ax.annotate(f"Seed recovered in\ncommercial month {X500}\n"
            f"(month {X500 + OFFSET} from\nfunding)",
            xy=(X500, xr["cum"]), xytext=(X500 + 0.4, 330_000),
            fontsize=7.8, color=INK, ha="left", va="center", linespacing=1.3,
            arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8, shrinkA=0, shrinkB=5,
                            connectionstyle="angle,angleA=0,angleB=90,rad=0"))
ax.text(24.15, cum[-1], f"₱{cum[-1]:,}", fontsize=7.6, color=INK,
        va="center", ha="left", fontweight="bold")

ax.set_xlim(0.5, 27.5)
ax.set_ylim(0, 660_000)
ax.set_xticks([1, 6, 12, 18, 24])
ax.set_xlabel("Month of commercial operation (month 1 = month 15 from funding)",
              fontsize=7.8, color=GREY, labelpad=5)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: "₱0" if v == 0 else f"₱{v/1000:.0f}k"))
ax.set_yticks([0, 200_000, 400_000, 600_000])
ax.tick_params(labelsize=7.6, length=0)
ax.grid(axis="y", color=RULE, lw=0.6, zorder=0)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(RULE)
fig.subplots_adjust(left=0.10, right=0.97, top=0.97, bottom=0.17)
fig.savefig("fig12_recovery_rose.png", facecolor="white")
plt.close(fig)
print("figures written")
