"""Labelled figure of the version 2.0 device, from the Blender render (user, 16 Nov 2026: replace the old labelled
prototype figure with the new 3D model).

    python build/dev2/label_render.py   -> figures/Resondi-Device-3D-Labelled.png

Input: figures/Resondi-Device-3D.png (build/dev2/render_blend.py). Labels name only parts stated in the project
records (spec sheet, component figure); the render is a concept render, about 160 x 100 x 60 mm, not the
173 x 80 x 70 mm of the specification, so the paper captions say so.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRC = os.path.join(ROOT, "figures", "Resondi-Device-3D.png")
OUT = os.path.join(ROOT, "figures", "Resondi-Device-3D-Labelled.png")

ROSE, PLUM, MUTED, INK = "#E91E76", "#8E2A52", "#9E8892", "#2B1D24"

img = Image.open(SRC).convert("RGB")
x0, y0, x1, y1 = 320, 100, 1230, 815          # crop to the device
img = img.crop((x0, y0, x1, y1))
W, H = img.size

# (label, sub-label, point on the render in original pixels, label position in axes units 0-1, alignment)
LABELS = [
    ("20 × 4 status display", "site prompts and device state", (780, 210), (0.33, 1.07), "center"),
    ("Status LEDs", "power and recording activity", (967, 236), (0.80, 1.07), "center"),
    ("HEART and LUNGS buttons", "one recording mode each", (1078, 250), (1.06, 0.80), "left"),
    ("Cable connector", "joins the sensor cable\nto the enclosure", (1160, 400), (1.06, 0.50), "left"),
    ("Enclosure", "3D-printed PLA; houses\nthe ESP32, microSD card\nand 10,000 mAh battery", (600, 420),
     (-0.06, 0.74), "right"),
    ("Chest piece", "placed on the chest\nat each site", (395, 572), (-0.06, 0.36), "right"),
    ("Sensor cable", "carries the chest-piece\nsignal to the enclosure", (905, 781), (1.06, 0.14), "left"),
]

FW, FH = 13.0, 6.6
AX_W = 0.48
ax_h = AX_W * FW * H / W / FH                 # keep the render's true aspect ratio
fig = plt.figure(figsize=(FW, FH), dpi=200)
ax = fig.add_axes([0.26, 0.05, AX_W, ax_h])
ax.imshow(img, extent=(0, 1, 0, 1), aspect="auto")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

for title, sub, (px, py), (lx, ly), ha in LABELS:
    u, v = (px - x0) / W, 1 - (py - y0) / H
    ax.plot([u], [v], "o", ms=6, color=PLUM, zorder=5, clip_on=False)
    top = ly >= 1
    ax.annotate("", xy=(u, v), xytext=(lx, ly - 0.012 if top else ly + 0.02), annotation_clip=False,
                arrowprops=dict(arrowstyle="-", color=ROSE, lw=1.2, alpha=0.8, shrinkA=0, shrinkB=4))
    ax.text(lx, ly + 0.065 if top else ly + 0.03, title, ha=ha, va="bottom", fontsize=12.5,
            fontweight="bold", color=INK, family="DejaVu Serif", clip_on=False)
    ax.text(lx, ly + 0.06 if top else ly + 0.022, sub, ha=ha, va="top", fontsize=10, color=MUTED,
            family="DejaVu Serif", clip_on=False, linespacing=1.3)

fig.savefig(OUT, facecolor="white")
print("wrote", OUT)
