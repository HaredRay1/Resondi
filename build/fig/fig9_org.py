"""Organizational structure: three founders as CEO, CTO and COO, under an Advisory Board.

Black and white, light blue headers only. The functions under each officer match
Table 10 of the concept note; the phase each owns is in Table 9.
"""
import os
import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

BLACK = "#000000"
LBLUE = "#DCE9F5"          # the one colour, reserved for headers
WHITE = "#FFFFFF"
FONT = "Segoe UI"

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "figures",
                   "fig9_org.png")

CEO = ("CHIEF EXECUTIVE OFFICER (CEO)", "Ahnycca Krish N. Malimban",
       ["Data and model operations", "Product and AI",
        "Regulatory and compliance", "Sales and partnerships"])
REPORTS = [
    ("CHIEF TECHNOLOGY OFFICER (CTO)", "Hared Ray Cabrera",
     ["Platform operations", "Application development",
      "Information security", "Data Protection Officer"]),
    ("CHIEF OPERATING OFFICER (COO)", "Jarred Paul Llacuna",
     ["Production and supply chain", "Device maintenance and field service",
      "Clinical affairs and validation", "Finance and administration"]),
]

ADVISERS = [
    ("Research Adviser (mentor)", "PPCNSHS research programme — academic supervision and ethics endorsement"),
    ("Consulting Clinicians", "Three pulmonologists and one pediatrician — labelling, content approval, reference assessment"),
    ("Electronics Engineer", "Circuit design review and acoustic testing support"),
    ("Practitioner Reviewer Network", "Reviewing clinicians in the live workflow from Phase 4 onward"),
]

FS_HDR, FS_NAME, FS_FOUNDER, FS_FN = 13.5, 18, 12.5, 13
FS_BOR, FS_BOR_ROLE, FS_BOR_SUB = 15, 13.5, 11.5

PX = 1180
L, R = 24, 1156
TITLE_H = 120
BOR_H, BOR_GAP = 168, 40
HDR_H, NAME_H, FN_H = 36, 62, 25
CARD_H = HDR_H + NAME_H + 4 * FN_H + 22
SPINE = 40
PY = TITLE_H + BOR_H + BOR_GAP + CARD_H + SPINE * 2 + CARD_H + 30

fig = plt.figure(figsize=(PX / 100, PY / 100), dpi=100)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, PX); ax.set_ylim(0, PY); ax.axis("off")
ax.add_patch(Rectangle((0, 0), PX, PY, facecolor=WHITE, zorder=0))


def box(x, top, w, h, *, fill=WHITE, lw=1.7):
    ax.add_patch(FancyBboxPatch((x, top - h), w, h,
                                boxstyle="round,pad=0,rounding_size=5",
                                facecolor=fill, edgecolor=BLACK, linewidth=lw,
                                zorder=2))


def header_strip(x, top, w, h, text, *, fs):
    ax.add_patch(Rectangle((x + 1.5, top - h), w - 3, h - 1.5, facecolor=LBLUE,
                           edgecolor="none", zorder=3))
    ax.text(x + w / 2, top - h / 2, text, fontsize=fs, fontweight="bold",
            family=FONT, color=BLACK, ha="center", va="center", zorder=4)


def card(x, top, w, title, name, functions, *, lw=1.9):
    box(x, top, w, CARD_H, lw=lw)
    header_strip(x, top, w, HDR_H, title, fs=FS_HDR)
    y = top - HDR_H - 24
    ax.text(x + w / 2, y, name, fontsize=FS_NAME, fontweight="bold", family=FONT,
            color=BLACK, ha="center", va="center", zorder=5)
    ax.text(x + w / 2, y - 25, "Founder", fontsize=FS_FOUNDER, family=FONT,
            color=BLACK, ha="center", va="center", zorder=5, style="italic")
    rule = top - HDR_H - NAME_H
    ax.plot([x + 30, x + w - 30], [rule, rule], color=BLACK, lw=0.8, zorder=4)
    fy = rule - 20
    for fn in functions:
        ax.text(x + 46, fy, "•  " + fn, fontsize=FS_FN, family=FONT, color=BLACK,
                ha="left", va="center", zorder=5)
        fy -= FN_H


vline = lambda x, a, b: ax.plot([x, x], [a, b], color=BLACK, lw=1.5, zorder=1)
hline = lambda a, b, y: ax.plot([a, b], [y, y], color=BLACK, lw=1.5, zorder=1)

# ── title ────────────────────────────────────────────────────────────────
ax.text(L, PY - 22, "Resondi — Organizational Structure", fontsize=24,
        fontweight="bold", family=FONT, color=BLACK, va="top")
SUB = ("Three student founders form the registered startup team, guided by their research "
       "adviser and reviewed by an Advisory Board. Table 9 gives the phase each founder "
       "owns; Table 10 gives the functions each holds.")
_y = PY - 60
for _ln in textwrap.wrap(SUB, 118):
    ax.text(L, _y, _ln, fontsize=13, family=FONT, color=BLACK, va="top")
    _y -= 19

# ── advisory board ───────────────────────────────────────────────────────
BOR_T = PY - TITLE_H
box(L, BOR_T, R - L, BOR_H)
header_strip(L, BOR_T, R - L, 38, "ADVISORY BOARD  ·  REVIEWS AND ENDORSES, "
             "HOLDS NO PHASE", fs=FS_BOR)
bw = (R - L - 44) / 2
for i, (name, desc) in enumerate(ADVISERS):
    r, c = divmod(i, 2)
    bx, by = L + 22 + c * bw, BOR_T - 62 - r * 56
    ax.text(bx, by, name, fontsize=FS_BOR_ROLE, fontweight="bold", family=FONT,
            color=BLACK, va="top", zorder=4)
    yy = by - 19
    for ln in textwrap.wrap(desc, int((bw - 34) / 7.6))[:2]:
        ax.text(bx, yy, ln, fontsize=FS_BOR_SUB, family=FONT, color=BLACK,
                va="top", zorder=4)
        yy -= 16

# ── CEO ──────────────────────────────────────────────────────────────────
GAP = 34
CW = (R - L - GAP) / 2
CEO_T = BOR_T - BOR_H - BOR_GAP
ceo_x = (PX - CW) / 2
vline(PX / 2, BOR_T - BOR_H, CEO_T)
card(ceo_x, CEO_T, CW, *CEO, lw=2.3)

# ── CTO and COO ──────────────────────────────────────────────────────────
spine = CEO_T - CARD_H - SPINE
vline(PX / 2, CEO_T - CARD_H, spine)
colx = lambda c: L + c * (CW + GAP)
hline(colx(0) + CW / 2, colx(1) + CW / 2, spine)
ROW_T = spine - SPINE
for c, (title, name, fns) in enumerate(REPORTS):
    vline(colx(c) + CW / 2, spine, ROW_T)
    card(colx(c), ROW_T, CW, title, name, fns)

print(f"  canvas {PX}x{PY}, bottom margin {ROW_T - CARD_H:.0f}px")
fig.savefig(OUT, facecolor=WHITE, dpi=250)
plt.close(fig)
from PIL import Image
print("fig9_org.png", Image.open(OUT).size)
