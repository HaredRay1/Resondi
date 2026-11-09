"""Figure 2 of the concept note: hardware block diagram, enclosure VER 2.0.

Replaces figB_device.png, which drew the earlier build (preamplifier, BLE, tubing).
Solid lines exist today; the dashed path is what the ₱38,000 line builds.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

NAVY, LIGHT, PALE = "#8E2A52", "#FBE9F0", "#FDF4F8"
GREY, TEXT = "#6F6F6F", "#262626"
SERIF = "serif"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "figures",
                   "Resondi-Hardware-Block-VER2.png")


def box(x, y, w, h, label, sub=None, fc="white", ec=NAVY, lw=1.2, ls="solid", fs=7.5, subfs=6.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.045",
                 facecolor=fc, edgecolor=ec, linewidth=lw, linestyle=ls, zorder=3))
    lines = 1 + (sub.count("\n") + 1 if sub else 0)
    cy = y + h / 2 + (0.11 * h * (lines - 1) if sub else 0)
    ax.text(x + w / 2, cy, label, ha="center", va="center", fontsize=fs, family=SERIF,
            color=TEXT, fontweight="bold", zorder=4)
    if sub:
        ax.text(x + w / 2, cy - 0.15, sub, ha="center", va="top", fontsize=subfs, family=SERIF,
                color=GREY, linespacing=1.25, zorder=4)


def arrow(p1, p2, ls="solid", color=NAVY, style="-|>"):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=10, color=color,
                 linewidth=1.3, linestyle=ls, zorder=2, shrinkA=1, shrinkB=1))


def band(x0, y0, x1, y1, label):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0,
                 boxstyle="round,pad=0.01,rounding_size=0.05",
                 facecolor=PALE, edgecolor="#EBCFDC", linewidth=1.0, zorder=0))
    ax.text((x0 + x1) / 2, y1 + 0.09, label, ha="center", fontsize=7.3, family=SERIF,
            color=GREY, fontweight="bold")


W, H = 10.2, 3.85
fig, ax = plt.subplots(figsize=(W, H))
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")

band(0.15, 2.28, 2.95, 3.46, "ACOUSTIC")
band(3.10, 0.42, 7.02, 3.46, "RESONDI DEVICE (BUILT)")
band(7.17, 0.42, 10.05, 3.46, "BEYOND THE DEVICE")

box(0.27, 2.45, 1.20, 0.85, "Chest piece", "diaphragm")
box(1.65, 2.45, 1.18, 0.85, "Printed mount", "acoustic coupling")
arrow((1.47, 2.87), (1.65, 2.87))
arrow((2.83, 2.87), (3.25, 2.87))

box(3.25, 2.45, 1.45, 0.85, "MEMS microphone", "INMP441, digital")
box(4.92, 2.45, 1.98, 0.85, "Controls", "Heart and Lungs buttons\ntwo status LEDs")

box(3.25, 1.45, 2.25, 0.72, "ESP32 microcontroller", "dual-core, up to 240 MHz", fc=LIGHT, lw=1.7)
arrow((3.97, 2.45), (3.97, 2.17))
ax.text(3.91, 2.31, "I²S", ha="right", va="center", fontsize=6.8, family=SERIF, color=GREY)
arrow((5.40, 2.45), (5.18, 2.17))

box(5.74, 1.45, 1.16, 0.72, "Wi-Fi access", "RESONDI_WIFI", subfs=6.2)
arrow((5.50, 1.81), (5.74, 1.81), style="<|-|>")

box(3.25, 0.55, 1.08, 0.66, "20×4 LCD", "I²C")
box(4.45, 0.55, 1.05, 0.66, "Battery", "10,000 mAh")
box(5.62, 0.55, 1.28, 0.66, "MicroSD", "32 GB, WAV files")
arrow((3.79, 1.45), (3.79, 1.21))
arrow((4.97, 0.55 + 0.66), (4.97, 1.45))
arrow((5.40, 1.45), (5.95, 1.21))

box(7.30, 2.45, 2.62, 0.85, "Browser on a phone or computer",
    "web app served by the device" + chr(10) + "at 192.168.4.1: record, list, play")
arrow((6.60, 2.17), (7.30, 2.70), style="<|-|>")

box(7.30, 1.45, 1.20, 0.72, "Mobile gateway", "not built", ec=NAVY, ls=(0, (3, 2)), fs=7.1)
arrow((6.90, 1.81), (7.30, 1.81), ls=(0, (3, 2)))
box(8.72, 0.55, 1.20, 1.62, "Resondi\nplatform", None, fc=LIGHT, lw=1.7, fs=8.0)
ax.text(9.32, 0.86, "built: records,\nAI, review", ha="center", va="center", fontsize=6.6,
        family=SERIF, color=GREY, zorder=4)
arrow((8.50, 1.81), (8.72, 1.81), ls=(0, (3, 2)))

arrow((6.90, 0.88), (8.72, 0.88))
ax.text(7.81, 0.95, "memory card, carried", ha="center", va="bottom", fontsize=6.6,
        family=SERIF, color=GREY, style="italic")
ax.text(7.81, 0.81, "by a person, today", ha="center", va="top", fontsize=6.6, family=SERIF, color=GREY,
        style="italic")

ax.text(W / 2, 0.14, "Solid lines work today. The dashed path is the link the ₱38,000 mobile "
        "application line builds.", ha="center", fontsize=7.8, family=SERIF, color=GREY, style="italic")

fig.savefig(OUT, dpi=240, bbox_inches="tight", pad_inches=0.06, facecolor="white")
print("saved", os.path.normpath(OUT))
