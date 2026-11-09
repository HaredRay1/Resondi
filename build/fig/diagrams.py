import os as _os
_BUILD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))).replace(chr(92), '/')
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Polygon, Rectangle
from matplotlib.path import Path
import matplotlib.patches as mpatches

NAVY, MID, LIGHT = "#8E2A52", "#B5537E", "#FBE9F0"
PALE, GREY, TEXT = "#FDF4F8", "#7F7F7F", "#262626"
SERIF = "serif"
OUT = _BUILD + "/fig/"


def box(ax, x, y, w, h, label, sub=None, fc="white", ec=NAVY, lw=1.3,
        fs=8.6, subfs=7.2, tc=TEXT, bold=True, r=0.045):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle=f"round,pad=0.008,rounding_size={r}",
                 facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3))
    cy = y + h / 2 + (0.09 * h if sub else 0)
    ax.text(x + w / 2, cy, label, ha="center", va="center", fontsize=fs,
            family=SERIF, color=tc, fontweight="bold" if bold else "normal",
            linespacing=1.3, zorder=4)
    if sub:
        ax.text(x + w / 2, y + h / 2 - 0.26 * h, sub, ha="center", va="center",
                fontsize=subfs, family=SERIF, color=GREY, linespacing=1.35, zorder=4)


def arrow(ax, p1, p2, color=NAVY, lw=1.4, style="-|>", rad=0.0, ls="solid"):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=11,
                 color=color, linewidth=lw, linestyle=ls,
                 connectionstyle=f"arc3,rad={rad}", zorder=2,
                 shrinkA=1, shrinkB=1))


# ══════════════════════════════════════════ FIGURE A — six-stage workflow
fig, ax = plt.subplots(figsize=(10.2, 2.75))
ax.set_xlim(0, 10.2); ax.set_ylim(0, 2.75); ax.axis("off")

stages = [
    ("1", "Mode\nselection", "Lung or Heart"),
    ("2", "Guided\nplacement", "standardized site"),
    ("3", "Capture and\norganize", "tagged, filed"),
    ("4", "AI-assisted\nanalysis", "MFCC · CNN"),
    ("5", "Practitioner\nreview", "confirm · modify"),
    ("6", "Compare and\nrehabilitate", "same site, later"),
]
W, H, GAP, Y = 1.42, 0.98, 0.26, 0.95
xs = [0.19 + i * (W + GAP) for i in range(6)]

for i, (num, lab, sub) in enumerate(stages):
    x = xs[i]
    gate = i == 4
    box(ax, x, Y, W, H, lab, sub,
        fc=LIGHT if gate else "white", ec=NAVY, lw=1.8 if gate else 1.3,
        fs=8.3, subfs=6.9)
    ax.add_patch(Circle((x + 0.135, Y + H - 0.115), 0.10,
                        facecolor=NAVY, edgecolor="none", zorder=5))
    ax.text(x + 0.135, Y + H - 0.115, num, ha="center", va="center",
            fontsize=7.0, color="white", family=SERIF, fontweight="bold", zorder=6)
    if i < 5:
        arrow(ax, (x + W, Y + H / 2), (x + W + GAP, Y + H / 2))

BR = "arc,angleA=-90,angleB=-90,armA=22,armB=22,rad=6"
TR = "arc,angleA=90,angleB=90,armA=24,armB=24,rad=6"

# repeat loop: stage 5 -> stage 3 (below)
ax.add_patch(FancyArrowPatch((xs[4] + W / 2, Y), (xs[2] + W / 2, Y),
             arrowstyle="-|>", mutation_scale=11, color=MID, linewidth=1.3,
             linestyle=(0, (4, 2)), connectionstyle=BR, zorder=2,
             shrinkA=1, shrinkB=1))
ax.text((xs[2] + xs[4]) / 2 + W / 2, 0.33, "poor recording — repeat",
        ha="center", va="center", fontsize=7.4, family=SERIF, color=MID, style="italic")

# longitudinal loop: stage 6 -> stage 3 (above)
ax.add_patch(FancyArrowPatch((xs[5] + W / 2, Y + H), (xs[2] + W / 2, Y + H),
             arrowstyle="-|>", mutation_scale=11, color=NAVY, linewidth=1.3,
             connectionstyle=TR, zorder=2, shrinkA=1, shrinkB=1))
ax.text((xs[2] + xs[5]) / 2 + W / 2, 2.49,
        "next session compared against the same anatomical site",
        ha="center", va="center", fontsize=7.6, family=SERIF, color=NAVY)

fig.savefig(OUT + "figA_workflow.png", dpi=240, bbox_inches="tight",
            pad_inches=0.06, facecolor="white")
plt.close(fig)


# ══════════════════════════════════════════ FIGURE B — device block diagram
fig, ax = plt.subplots(figsize=(10.2, 3.75))
ax.set_xlim(0, 10.2); ax.set_ylim(0, 3.75); ax.axis("off")

def band(x0, y0, x1, y1, label, lx=None):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0,
                 boxstyle="round,pad=0.01,rounding_size=0.05",
                 facecolor=PALE, edgecolor="#EBCFDC", linewidth=1.0, zorder=0))
    ax.text(lx if lx else (x0 + x1) / 2, y1 + 0.13, label, ha="center",
            fontsize=7.3, family=SERIF, color=GREY, fontweight="bold")

band(0.20, 2.26, 3.40, 3.26, "ACOUSTIC")
band(3.58, 0.30, 6.72, 3.26, "ELECTRONIC")
band(6.90, 1.02, 10.02, 3.00, "TRANSMISSION")

box(ax, 0.36, 2.40, 1.32, 0.72, "Chest piece", "diaphragm", fs=8.2, subfs=6.9)
box(ax, 1.92, 2.40, 1.32, 0.72, "Tubing", "silicone", fs=8.2, subfs=6.9)
box(ax, 3.75, 2.40, 1.25, 0.72, "MEMS mic", "INMP441", fs=8.2, subfs=6.9)
box(ax, 5.20, 2.40, 1.35, 0.72, "Preamplifier", None, fs=8.2)

arrow(ax, (1.68, 2.76), (1.92, 2.76))
arrow(ax, (3.24, 2.76), (3.75, 2.76))
arrow(ax, (5.00, 2.76), (5.20, 2.76))

box(ax, 3.90, 1.35, 2.45, 0.72, "ESP32 microcontroller", None, fs=8.6,
    fc=LIGHT, lw=1.7)
arrow(ax, (5.87, 2.40), (5.60, 2.07))

box(ax, 3.80, 0.45, 1.15, 0.60, "20×4 LCD", "I²C", fs=7.8, subfs=6.7, lw=1.1)
box(ax, 5.25, 0.45, 1.25, 0.60, "Li-ion cell", "charge + protect",
    fs=7.8, subfs=6.7, lw=1.1)
ax.plot([4.38, 4.38], [1.35, 1.05], color=GREY, linewidth=1.0, zorder=1)
ax.plot([5.87, 5.87], [1.35, 1.05], color=GREY, linewidth=1.0, zorder=1)

box(ax, 7.05, 2.12, 1.30, 0.66, "BLE", "live transfer", fs=8.2, subfs=6.9)
box(ax, 7.05, 1.18, 1.30, 0.66, "MicroSD", "offline, manual", fs=8.2, subfs=6.9)
arrow(ax, (6.35, 1.86), (7.05, 2.45), rad=-0.16)
arrow(ax, (6.35, 1.56), (7.05, 1.51), rad=0.14)

box(ax, 8.62, 1.62, 1.28, 0.72, "Mobile\nplatform", None, fs=8.4, fc=LIGHT, lw=1.7)
arrow(ax, (8.35, 2.45), (8.62, 2.16), rad=0.12)
arrow(ax, (8.35, 1.51), (8.62, 1.80), rad=-0.12)

ax.text(5.10, 0.09,
        "Dual storage: BLE where a phone is present, MicroSD where connectivity is unreliable",
        ha="center", fontsize=7.6, family=SERIF, color=GREY, style="italic")

fig.savefig(OUT + "figB_device.png", dpi=240, bbox_inches="tight",
            pad_inches=0.06, facecolor="white")
plt.close(fig)


# ══════════════════════════════════════════ FIGURE C — auscultation map
def torso(ax, cx, cy, s=1.0, fc="#FFF9FC", ec="#C98EA9"):
    """Simple schematic torso, unit height 1.0 scaled by s, centred on cx."""
    pts = [
        (-0.13, 0.98), (0.13, 0.98),            # neck
        (0.30, 0.92), (0.46, 0.84),             # shoulder
        (0.50, 0.70), (0.47, 0.46),             # upper arm line
        (0.42, 0.20), (0.38, 0.02),             # waist
        (-0.38, 0.02), (-0.42, 0.20),
        (-0.47, 0.46), (-0.50, 0.70),
        (-0.46, 0.84), (-0.30, 0.92),
    ]
    poly = [(cx + x * s, cy + y * s) for x, y in pts]
    ax.add_patch(Polygon(poly, closed=True, facecolor=fc, edgecolor=ec,
                         linewidth=1.3, zorder=1))
    # sternum / spine guide
    ax.plot([cx, cx], [cy + 0.06 * s, cy + 0.88 * s], color=ec,
            linewidth=0.8, linestyle=(0, (3, 2)), zorder=2)


def site(ax, x, y, n, r=0.135, fc=NAVY, fs=8.2):
    ax.add_patch(Circle((x, y), r, facecolor=fc, edgecolor="white",
                        linewidth=1.4, zorder=5))
    ax.text(x, y, str(n), ha="center", va="center", fontsize=fs,
            color="white", family=SERIF, fontweight="bold", zorder=6)


fig, ax = plt.subplots(figsize=(9.6, 5.05))
ax.set_xlim(0, 9.6); ax.set_ylim(0, 5.05); ax.axis("off")

S, BY = 2.72, 1.36          # torso scale, torso baseline


def panel(cx, title, subtitle, sites, legend, left_tag, right_tag, fc):
    """One torso panel with its sites, orientation tags and legend beneath."""
    torso(ax, cx, BY, S)
    ax.text(cx, BY + 0.98 * S + 0.30, title, ha="center", fontsize=9.6,
            family=SERIF, color=NAVY, fontweight="bold")
    ax.text(cx, BY + 0.98 * S + 0.09, subtitle, ha="center", fontsize=7.8,
            family=SERIF, color=GREY, style="italic")
    # patient-orientation tags, inside the torso at shoulder height
    ax.text(cx - 0.33 * S, BY + 0.86 * S, left_tag, ha="center", va="center",
            fontsize=8.6, family=SERIF, color="#C98EA9", fontweight="bold")
    ax.text(cx + 0.33 * S, BY + 0.86 * S, right_tag, ha="center", va="center",
            fontsize=8.6, family=SERIF, color="#C98EA9", fontweight="bold")
    for dx, dy, tag in sites:
        site(ax, cx + dx * S, BY + dy * S, tag, fc=fc)
    # legend: two columns beneath the torso
    half = (len(legend) + 1) // 2
    for i, (tag, name) in enumerate(legend):
        col, row = i // half, i % half
        x = cx - 1.22 + col * 1.62
        y = 1.02 - row * 0.265
        ax.add_patch(Circle((x, y + 0.025), 0.085, facecolor=fc,
                            edgecolor="white", linewidth=1.0, zorder=5))
        ax.text(x, y + 0.025, tag, ha="center", va="center", fontsize=6.4,
                color="white", family=SERIF, fontweight="bold", zorder=6)
        ax.text(x + 0.16, y + 0.025, name, ha="left", va="center",
                fontsize=7.8, family=SERIF, color=TEXT)


# ---- Lung Mode (posterior view: the patient's left stays on the viewer's left)
panel(
    2.45, "LUNG MODE", "six posterior fields",
    [(0.22, 0.74, 1), (-0.22, 0.74, 2),
     (0.24, 0.54, 3), (-0.24, 0.54, 4),
     (0.25, 0.34, 5), (-0.25, 0.34, 6)],
    [("1", "Right upper"), ("2", "Left upper"), ("3", "Right middle"),
     ("4", "Left middle"), ("5", "Right lower"), ("6", "Left lower")],
    "L", "R", NAVY)

# ---- Heart Mode (anterior view: the patient's left falls on the viewer's right)
panel(
    7.15, "HEART MODE", "four anterior valve points",
    [(-0.15, 0.74, "A"), (0.15, 0.74, "P"),
     (0.09, 0.55, "T"), (0.26, 0.45, "M")],
    [("A", "Aortic"), ("P", "Pulmonic"), ("T", "Tricuspid"), ("M", "Mitral")],
    "R", "L", MID)

ax.text(4.8, 0.14, "R and L mark the patient's own right and left. The application directs the user to each site in sequence "
        "and tags every recording with its location.",
        ha="center", fontsize=7.8, family=SERIF, color=GREY, style="italic")

fig.savefig(OUT + "figC_sites.png", dpi=240, bbox_inches="tight",
            pad_inches=0.06, facecolor="white")
plt.close(fig)


# ══════════════════════════════════════════ FIGURE D — CNN fusion
fig, ax = plt.subplots(figsize=(10.2, 3.9))
ax.set_xlim(0, 10.2); ax.set_ylim(0, 3.9); ax.axis("off")

box(ax, 0.22, 1.52, 1.34, 0.86, "Recording", "preprocessed\naudio segment",
    fs=8.4, subfs=6.9, fc=LIGHT, lw=1.6)

feats = [("Mel-spectrogram", 2.92), ("MFCC", 1.72), ("Chromagram", 0.52)]
for name, yy in feats:
    box(ax, 2.16, yy, 1.74, 0.78, name, None, fs=8.0)
    arrow(ax, (1.56, 1.95), (2.16, yy + 0.39), rad=0.0, lw=1.2)

cnn_y = []
for _, yy in feats:
    box(ax, 4.34, yy, 1.56, 0.78, "CNN branch", "conv · pool", fs=8.0, subfs=6.8)
    arrow(ax, (3.90, yy + 0.39), (4.34, yy + 0.39), lw=1.2)
    cnn_y.append(yy + 0.39)

box(ax, 6.40, 1.52, 1.34, 0.86, "Concatenate", "fused feature\nvector",
    fs=8.4, subfs=6.9, fc=LIGHT, lw=1.6)
for yy in cnn_y:
    arrow(ax, (5.90, yy), (6.40, 1.95), lw=1.2)

box(ax, 8.18, 1.52, 1.34, 0.86, "Softmax", "four classes",
    fs=8.4, subfs=6.9, fc=LIGHT, lw=1.6)
arrow(ax, (7.74, 1.95), (8.18, 1.95))

classes = "normal  ·  wheeze  ·  crackle  ·  both"
ax.text(8.85, 1.22, classes, ha="center", fontsize=7.6, family=SERIF, color=NAVY)

ax.text(5.10, 0.14, "Three representations of the same recording are classified in parallel and combined before a single prediction",
        ha="center", fontsize=7.6, family=SERIF, color=GREY, style="italic")

fig.savefig(OUT + "figD_cnn.png", dpi=240, bbox_inches="tight",
            pad_inches=0.06, facecolor="white")
plt.close(fig)

print("four diagrams written")
