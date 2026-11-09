import os as _os
_BUILD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))).replace(chr(92), '/')
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

NAVY, MID, LIGHT = "#8E2A52", "#B5537E", "#FBE9F0"
GREY, TEXT = "#7F7F7F", "#262626"

CAPS = [
    "Preserves the original sound as a replayable recording",
    "Guides placement across standardized auscultation points",
    "Separates lung and heart capture automatically",
    "AI-assisted identification of sound patterns",
    "Compares a recording against the same site over time",
    "Structured practitioner review and confirmation",
    "Practitioner-released rehabilitation support",
    "Low enough in cost for a rural health unit",
    "Automated recording-quality screening",
]
COLS = ["Conventional\nacoustic\nstethoscope", "Commercial\nelectronic\nstethoscope",
        "Phone voice\nmemo +\nwritten notes", "Resondi"]
# 3 = planned, 2 = full, 1 = partial, 0 = none
MARKS = [
    [0, 2, 2, 2],
    [0, 0, 0, 2],
    [0, 0, 0, 2],
    [0, 1, 0, 2],
    [0, 1, 1, 2],
    [0, 0, 0, 2],
    [0, 0, 0, 2],
    [2, 0, 2, 2],
    [0, 1, 0, 3],
]

fig, ax = plt.subplots(figsize=(10.1, 6.5))
ax.set_xlim(0, 10.1); ax.set_ylim(0, 6.5); ax.axis("off")

ax.add_patch(FancyBboxPatch((0.08, 5.70), 9.94, 0.68,
                            boxstyle="round,pad=0.015,rounding_size=0.06",
                            facecolor=NAVY, edgecolor="none"))
ax.text(5.05, 6.15, "One platform that turns auscultation from a moment of listening",
        ha="center", va="center", color="white", fontsize=11.5, family="serif")
ax.text(5.05, 5.89, "into a record that can be compared, followed, and reviewed.",
        ha="center", va="center", color="white", fontsize=11.5, family="serif", style="italic")

LEFT, LABEL_W, TOP, ROW_H = 0.08, 5.05, 5.44, 0.47
COL_W = (10.02 - LABEL_W - LEFT) / 4

for j, name in enumerate(COLS):
    x = LEFT + LABEL_W + j * COL_W
    us = j == 3
    ax.add_patch(Rectangle((x, TOP - 0.74), COL_W, 0.74,
                           facecolor=LIGHT if us else "white",
                           edgecolor="#BFBFBF", linewidth=0.6))
    ax.text(x + COL_W / 2, TOP - 0.37, name, ha="center", va="center", fontsize=8.3,
            family="serif", color=NAVY if us else GREY,
            fontweight="bold" if us else "normal", linespacing=1.35)

y = TOP - 0.74
for i, cap in enumerate(CAPS):
    y -= ROW_H
    planned_row = 3 in MARKS[i]
    if i % 2 == 0:
        ax.add_patch(Rectangle((LEFT, y), 9.94, ROW_H, facecolor="#FAF4F7",
                               edgecolor="none", zorder=0))
    ax.text(LEFT + 0.12, y + ROW_H / 2, cap, ha="left", va="center",
            fontsize=8.9, family="serif", color=TEXT,
            style="italic" if planned_row else "normal")
    for j in range(4):
        cx, cy = LEFT + LABEL_W + j * COL_W + COL_W / 2, y + ROW_H / 2
        m = MARKS[i][j]
        if m == 2:
            ax.add_patch(Circle((cx, cy), 0.105, facecolor=MID if j < 3 else NAVY,
                                edgecolor="none", zorder=3))
        elif m == 1:
            ax.add_patch(Circle((cx, cy), 0.105, facecolor=MID, edgecolor="none", zorder=3))
            ax.add_patch(Rectangle((cx, cy - 0.105), 0.105, 0.21, facecolor="white",
                                   edgecolor="none", zorder=4))
            ax.add_patch(Circle((cx, cy), 0.105, facecolor="none", edgecolor=MID,
                                linewidth=1.3, zorder=5))
        elif m == 3:
            ax.add_patch(Circle((cx, cy), 0.105, facecolor="none", edgecolor=NAVY,
                                linewidth=1.5, linestyle=(0, (2, 1.6)), zorder=3))
        else:
            ax.add_patch(Circle((cx, cy), 0.105, facecolor="white",
                                edgecolor="#C9C9C9", linewidth=1.1, zorder=3))

ax.add_patch(Rectangle((LEFT + LABEL_W + 3 * COL_W, y), COL_W, (TOP - 0.74) - y,
                       facecolor="none", edgecolor=NAVY, linewidth=1.4, zorder=7))

ly = y - 0.30
for dx, col, edge, lab, dashed in [
        (0.22, MID, None, "fully supported", False),
        (1.76, MID, MID, "partial or device-dependent", False),
        (4.32, "white", "#C9C9C9", "not supported", False),
        (5.90, "none", NAVY, "in development (see funding ask)", True)]:
    c = Circle((LEFT + dx, ly), 0.095,
               facecolor="none" if col == "none" else col,
               edgecolor=edge or "none", linewidth=1.3,
               linestyle=(0, (2, 1.6)) if dashed else "solid")
    ax.add_patch(c)
    if lab.startswith("partial"):
        ax.add_patch(Rectangle((LEFT + dx, ly - 0.095), 0.095, 0.19,
                               facecolor="white", edgecolor="none", zorder=5))
        ax.add_patch(Circle((LEFT + dx, ly), 0.095, facecolor="none",
                            edgecolor=MID, linewidth=1.2, zorder=6))
    ax.text(LEFT + dx + 0.16, ly, lab, va="center", fontsize=8.2,
            family="serif", color=GREY)

fig.savefig(_BUILD + "/fig/fig1_value_proposition.png", dpi=240,
            bbox_inches="tight", pad_inches=0.05, facecolor="white")
print("written")
