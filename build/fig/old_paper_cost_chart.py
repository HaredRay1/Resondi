"""Corrected Figure 3 (cost pie) for page 9 of the 83-page Ausculta paper (user, 26 Nov 2026).

The paper's Table 4 totals 2,094.47 pesos, but its pie chart's slices totalled 2,344.47 (power supply 716.00 against a
330.00 power bank). These slices are built only from Table 4's rows and must add up to its total, or the script stops.
Landscape, like the original, drawn at about one column's width so the printed type sizes are real.

    python build/fig/old_paper_cost_chart.py   -> figures/Ausculta-Cost-Breakdown-Corrected.png
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

TOTAL = 2094.47
# slice: (amount, Table 4 rows)
SLICES = [
    ("Acoustic Sensing", 127.00 + 63.00 + 146.72 + 207.00),   # chest piece, diaphragm, MAX9814, INMP441
    ("Storage", 156.00 + 355.00),                             # 2 card reader modules, 16 GB card
    ("Microcontroller", 350.00),                              # ESP32
    ("Power Supply", 330.00),                                 # power bank
    ("Display", 239.00),                                      # 20x4 LCD with I2C
    ("Casing", 70.00),                                        # 3D-printed PLA casing
    ("Wiring and Resistors", 47.25 + 3.50),                   # jumper wires, resistors
]
assert abs(sum(v for _, v in SLICES) - TOTAL) < 0.005, "the slices no longer add up to Table 4's total"

# same validated palette as build/fig/bom_v2.py
COLS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#6250d6", "#e87ba4", "#008300"]
INK, MUTE = "#1a1a1a", "#52514e"


def main():
    plt.rcParams["font.family"] = "Times New Roman"
    fig = plt.figure(figsize=(3.4, 2.15), dpi=500)
    fig.text(0.5, 0.945, "Cost Breakdown of the Prototype", ha="center", fontsize=8.5, fontweight="bold", color=INK)
    fig.text(0.5, 0.875, f"Total Cost: PHP {TOTAL:,.2f}", ha="center", fontsize=7, color=MUTE)

    ax = fig.add_axes([0.0, 0.02, 0.42, 0.80])
    vals = [v for _, v in SLICES]
    wedges, _ = ax.pie(vals, colors=COLS, startangle=90, counterclock=False,
                       wedgeprops=dict(edgecolor="white", linewidth=0.9))
    small = 0
    for w, v, c in zip(wedges, vals, COLS):
        pct = v / TOTAL * 100
        a = math.radians((w.theta1 + w.theta2) / 2)
        if pct >= 9:
            light = c in ("#2a78d6", "#6250d6", "#1baf7a", "#eb6834")
            ax.text(0.64 * math.cos(a), 0.64 * math.sin(a), f"{pct:.1f}%", ha="center", va="center", fontsize=6.3,
                    fontweight="bold", color="white" if light else INK)
            continue
        # small slices: label outside with a leader, spread left and right so they do not overlap
        x0, y0 = 1.0 * math.cos(a), 1.0 * math.sin(a)
        tx, ty = (-0.55, 1.22) if small == 0 else (0.45, 1.22)
        ax.plot([x0, tx + (0.12 if tx < 0 else -0.12)], [y0, ty - 0.06], color=MUTE, lw=0.4)
        ax.text(tx, ty, f"{pct:.1f}%", ha="center", va="center", fontsize=6.3, fontweight="bold", color=INK)
        small += 1
    ax.set_xlim(-1.32, 1.32)
    ax.set_ylim(-1.32, 1.32)
    ax.set_aspect("equal")

    lx = fig.add_axes([0.43, 0.04, 0.555, 0.78])
    lx.set_xlim(0, 1)
    lx.set_ylim(0, 1)
    lx.axis("off")
    lx.add_patch(FancyBboxPatch((0.0, 0.215), 1.0, 0.775, boxstyle="round,pad=0,rounding_size=0.02", fc="white",
                                ec="#c9c9c9", lw=0.6))
    for k, ((name, v), c) in enumerate(zip(SLICES, COLS)):
        y = 0.92 - k * 0.1035
        lx.plot([0.05], [y], "o", ms=4.2, color=c)
        lx.text(0.095, y, name, va="center", fontsize=6.3, color=INK)
        lx.text(0.775, y, f"PHP {v:,.2f}", va="center", ha="right", fontsize=6.3, color=INK)
        lx.text(0.975, y, f"({v / TOTAL * 100:.1f}%)", va="center", ha="right", fontsize=6.3, color=MUTE)
    lx.add_patch(FancyBboxPatch((0.0, 0.02), 1.0, 0.14, boxstyle="round,pad=0,rounding_size=0.02",
                                fc="#eeeef1", ec="#9a9aa5", lw=0.6))
    lx.text(0.5, 0.09, f"Total Cost: PHP {TOTAL:,.2f}", ha="center", va="center", fontsize=7, fontweight="bold",
            color=INK)

    root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    out = os.path.join(root, "figures", "Ausculta-Cost-Breakdown-Corrected.png")
    fig.savefig(out, facecolor="white")
    print("wrote", out)
    for name, v in SLICES:
        print(f"  {name:<22} {v:>9,.2f}  {v / TOTAL * 100:5.1f}%")


if __name__ == "__main__":
    main()
