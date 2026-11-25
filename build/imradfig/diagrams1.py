"""D1 hardware block diagram, D3 preprocessing chain, D4 classifier."""
from blocks import *
from theme import *

import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "figures") + os.sep


def d1_hardware():
    PX, PY = 1900, 580
    fig, ax = canvas(PX, PY)
    TOP, BH = 300, 132                       # one row of boxes
    group(ax, 40, 268, 540, 196, "ACOUSTIC")
    group(ax, 628, 120, 586, 344, "ELECTRONIC")
    group(ax, 1376, 150, 488, 314, "TRANSMISSION")

    box(ax, 72, TOP, 222, BH, "Chest piece", "diaphragm")
    box(ax, 330, TOP, 222, BH, "Tubing", "silicone")
    arrow(ax, (296, TOP + BH / 2), (326, TOP + BH / 2))

    box(ax, 660, TOP, 240, BH, "Microphone", "electret +\nMAX4466")
    arrow(ax, (554, TOP + BH / 2), (656, TOP + BH / 2))
    box(ax, 942, TOP, 240, BH, "ESP32", "microcontroller",
        fill=LIGHT, lw=2.3)
    arrow(ax, (902, TOP + BH / 2), (938, TOP + BH / 2))

    # 25 Nov 2026: the field build has a 20 x 4 LCD and a power bank (it was drawn with an OLED and a Li-ion cell)
    box(ax, 660, 150, 240, 96, "Power bank", "10,000 mAh", ts=7.6, ss=6.1)
    box(ax, 942, 150, 240, 96, "20 × 4 LCD", "device status", ts=7.6, ss=6.1)
    ax.plot([1062, 1062], [246, TOP], color=MID, lw=1.5, zorder=1)                     # LCD to ESP32
    ax.plot([900, 921, 921, 942], [198, 198, 318, 318], color=MID, lw=1.5, zorder=1)   # power to ESP32

    box(ax, 1404, 322, 212, 112, "BLE", "live transfer")
    box(ax, 1404, 180, 212, 112, "MicroSD", "offline buffer")
    arrow(ax, (1184, TOP + 80), (1400, 386), rad=-0.10)
    arrow(ax, (1184, TOP + 40), (1400, 244), rad=0.10)

    box(ax, 1652, 252, 196, 140, "Mobile\napplication", fill=LIGHT, lw=2.3, ts=8.2)
    arrow(ax, (1618, 378), (1650, 350), rad=-0.10)
    arrow(ax, (1618, 236), (1650, 292), rad=0.10)

    caption(ax, PX, "Field build used in the evaluation. BLE is used where a phone is present, "
                    "MicroSD where it is not", y=40)
    save(fig, OUT + "d1_hardware.png")


def d3_preprocess():
    PX, PY = 1900, 260
    fig, ax = canvas(PX, PY)
    steps = [("Raw recording", "WAV"), ("Resample", "16 kHz"),
             ("Noise reduction", "background"), ("Normalise", "amplitude"),
             ("Segment", "fixed length"), ("MFCC", "13 coefficients")]
    w, gap, h, y = 255, 52, 124, 88
    x = (PX - (len(steps) * w + (len(steps) - 1) * gap)) / 2
    for i, (t, s) in enumerate(steps):
        fill = LIGHT if i in (0, len(steps) - 1) else SURFACE
        box(ax, x, y, w, h, t, s, fill=fill, ts=7.9, ss=6.3)
        if i:
            arrow(ax, (x - gap + 6, y + h / 2), (x - 6, y + h / 2))
        x += w + gap
    caption(ax, PX, "Every recording is standardised before features are "
                    "extracted", y=30)
    save(fig, OUT + "d3_preprocess.png")


def d4_classifier():
    PX, PY = 1900, 430
    fig, ax = canvas(PX, PY)
    stages = [("MFCC", "13 coefficients"),
              ("Conv 1-D ×2", "8, 16 filters"),
              ("Max pooling", "+ dropout 0.25"),
              ("Flatten", "feature vector"),
              ("Softmax", "class probabilities")]
    w, gap, h, y = 288, 50, 136, 210
    x = (PX - (len(stages) * w + (len(stages) - 1) * gap)) / 2
    for i, (t, s) in enumerate(stages):
        fill = LIGHT if i in (0, len(stages) - 1) else SURFACE
        box(ax, x, y, w, h, t, s, fill=fill, ts=8.2, ss=6.3)
        if i:
            arrow(ax, (x - gap + 6, y + h / 2), (x - 6, y + h / 2))
        x += w + gap

    labels = ["Normal", "Wheezing", "Crackles", "Wheezing with crackles"]
    from blocks import text_w, upp
    widths = [text_w(ax, l, 7.0) + 14 * upp(ax) for l in labels]
    total = sum(widths) + 14 * (len(labels) - 1)
    cx = (PX - total) / 2
    ax.text(PX / 2, 160, "Output classes", ha="center", fontsize=7.2,
            color=SECONDARY, fontweight="bold", family=SERIF)
    for lab, wd in zip(labels, widths):
        ax.add_patch(FancyBboxPatch((cx, 88), wd, 46,
                     boxstyle="round,pad=0,rounding_size=6",
                     facecolor=PALE, edgecolor=MID, lw=1.3, zorder=2))
        ax.text(cx + wd / 2, 111, lab, ha="center", va="center",
                fontsize=7.0, color=INK, family=SERIF, zorder=3)
        cx += wd + 14

    caption(ax, PX, "A single MFCC input. The model classifies sound "
                    "patterns, not diseases", y=22)
    save(fig, OUT + "d4_classifier.png")


if __name__ == "__main__":
    d1_hardware(); d3_preprocess(); d4_classifier()
