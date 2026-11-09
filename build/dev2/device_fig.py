"""Figure: Resondi VER2.0 — labelled front face, plus an exploded assembly.

Two panels, because one view cannot do both jobs: a face-on cover where every
control is unoccluded and the leaders land exactly, and a small exploded view
that shows how the parts go together. Feature coordinates come from
rasterising the cover's top face, so no label position is guessed.
"""
import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

import os
HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "..", "..", "source-material", "stl")
SRC = {"base": f"{A}/RESONDI_BASE_VER2.0.stl",
       "cover": f"{A}/RESONDI_COVER_VER2.0.stl",
       "mount": f"{A}/STETH_MOUNT.stl",
       "scov":  f"{A}/STETH_COVER.stl"}

INK, MUT, ROSE, DEEP = "#2A1A22", "#8A7A82", "#C01A5F", "#8E2A52"
LINE = "#C9BCC2"
FONT = "DejaVu Sans"
C_COVER, C_BASE, C_MOUNT = (0.80, 0.26, 0.45), (0.66, 0.64, 0.65), (0.54, 0.52, 0.54)
LIGHT = np.array([-0.28, -0.46, 0.84]); LIGHT /= np.linalg.norm(LIGHT)


def rot(ax, deg):
    t = np.radians(deg); c, s = np.cos(t), np.sin(t)
    return {"x": np.array([[1,0,0],[0,c,-s],[0,s,c]]),
            "y": np.array([[c,0,s],[0,1,0],[-s,0,c]]),
            "z": np.array([[c,-s,0],[s,c,0],[0,0,1]])}[ax]


def load(k):
    m = trimesh.load(SRC[k]); m.apply_translation(-m.bounding_box.centroid); return m


def paint(ax, parts, M, scale, origin):
    polys, cols, deps = [], [], []
    for mesh, rgb, shift in parts:
        v = (mesh.vertices + np.array(shift)) @ M.T
        tris = v[mesh.faces]
        n = mesh.face_normals @ M.T
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
        d = n @ LIGHT
        k = (0.46 + 0.48 * np.clip(d, 0, 1) + 0.22 * np.clip(-d, 0, 1))[:, None]
        c = np.clip(np.array(rgb)[None, :] * k * 1.14, 0, 1)
        c = np.clip(c + (np.clip(1 - np.abs(n[:, 2]), 0, 1)[:, None] ** 3) * 0.12, 0, 1)
        polys.append(tris[:, :, :2]); cols.append(c); deps.append(tris[:, :, 2].mean(axis=1))
    P = np.concatenate(polys) * scale + np.array(origin)
    C = np.concatenate(cols); D = np.concatenate(deps)
    o = np.argsort(D)
    ax.add_collection(PolyCollection(P[o], facecolors=C[o], edgecolors="none",
                                     linewidths=0, zorder=2, antialiased=True))
    return P.reshape(-1, 2)


def proj(pt, M, scale, origin, shift=(0, 0, 0)):
    return ((np.asarray(pt) + np.array(shift)) @ M.T)[:2] * scale + np.array(origin)


base, cover, mount, scov = load("base"), load("cover"), load("mount"), load("scov")

fig, ax = plt.subplots(figsize=(13.4, 7.6), dpi=240)
fig.patch.set_facecolor("white"); ax.set_facecolor("white")

# ── Panel A: cover, face on ─────────────────────────────────────────────
MA = rot("z", 0) @ rot("x", 0)
SA, OA = 1.0, (-250.0, -6.0)
paint(ax, [(cover, C_COVER, (0, 0, 0))], MA, SA, OA)

FACE = [
 ("20 × 4 character LCD", "I²C · 40 × 98 mm window", (0, 24.1), (-104, 4), "right"),
 ("Status LEDs", "Red and yellow", (9.4, -35.4), (100, 6), "left"),
 ("HEART and LUNGS buttons", "Ø 27.7 mm · one recording mode each", (18.7, -59.8), (100, -46), "left"),
 ("M3 brass inserts", "Eight fixing points", (-36.5, 83.0), (-104, 16), "right"),
]
for text, sub, (fx, fy), (ox, oy), side in FACE:
    p = proj((fx, fy, 17.0), MA, SA, OA)
    tx, ty = p[0] + ox, p[1] + oy
    ha = "left" if side == "left" else "right"
    ax.annotate("", xy=tuple(p), xytext=(tx, ty),
                arrowprops=dict(arrowstyle="-", color=MUT, lw=1.0, shrinkA=2, shrinkB=2,
                                connectionstyle="angle,angleA=0,angleB=90,rad=0"), zorder=5)
    ax.plot([p[0]], [p[1]], "o", ms=3.8, color=DEEP, zorder=6)
    ax.text(tx, ty, text, ha=ha, va="bottom", fontsize=11.4, family=FONT,
            fontweight="bold", color=INK, zorder=6)
    ax.text(tx, ty - 5.5, sub, ha=ha, va="top", fontsize=9.2, family=FONT, color=MUT, zorder=6)

ax.text(OA[0], OA[1] - 122, "Front face", ha="center", fontsize=11, family=FONT,
        fontweight="bold", color=DEEP)
ax.text(OA[0], OA[1] - 133, "cover, viewed square on", ha="center", fontsize=9.2,
        family=FONT, color=MUT)

# ── Panel B: exploded assembly ──────────────────────────────────────────
MB = rot("z", 24) @ rot("x", -62)
SB, OB = 0.74, (268.0, 2.0)
LIFT, MX, MY = 112.0, -104.0, -86.0
paint(ax, [(base, C_BASE, (0, 0, 0)),
           (cover, C_COVER, (0, 0, LIFT)),
           (mount, C_MOUNT, (MX, MY, 0)),
           (scov, C_MOUNT, (MX, MY, 44.0))], MB, SB, OB)

for cx, cy in [(-36.5, 83.0), (36.5, 83.0), (-36.5, -80.0), (36.5, -80.0)]:
    a = proj((cx, cy, -17.0), MB, SB, OB, (0, 0, LIFT))
    b = proj((cx, cy, 31.0), MB, SB, OB)
    ax.plot([a[0], b[0]], [a[1], b[1]], color=LINE, lw=0.9, ls=(0, (3, 3)), zorder=1)
a = proj((0, 0, -19.0), MB, SB, OB, (MX, MY, 44.0))
b = proj((0, 0, 19.0), MB, SB, OB, (MX, MY, 0))
ax.plot([a[0], b[0]], [a[1], b[1]], color=LINE, lw=0.9, ls=(0, (3, 3)), zorder=1)

ASM = [
 ("PLA cover", "FDM 3D printed", (46, 60, 17.0), (0, 0, LIFT), (62, 30), "left"),
 ("Enclosure base", "Houses the ESP32, INMP441 microphone,\nMicroSD card and 10,000 mAh battery",
  (46, 40, 31.0), (0, 0, 0), (72, -26), "left"),
 ("Chestpiece mount\nand cover", "Acoustic coupling to\nthe stethoscope head",
  (0, 0, 19.0), (MX, MY, 44.0), (-62, 24), "right"),
]
for text, sub, pt, shift, (ox, oy), side in ASM:
    p = proj(pt, MB, SB, OB, shift)
    tx, ty = p[0] + ox, p[1] + oy
    ha = "left" if side == "left" else "right"
    ax.annotate("", xy=tuple(p), xytext=(tx, ty),
                arrowprops=dict(arrowstyle="-", color=MUT, lw=1.0, shrinkA=2, shrinkB=2,
                                connectionstyle="angle,angleA=0,angleB=90,rad=0"), zorder=5)
    ax.plot([p[0]], [p[1]], "o", ms=3.8, color=DEEP, zorder=6)
    nl = text.count("\n")
    ax.text(tx, ty, text, ha=ha, va="bottom", fontsize=11.4, family=FONT,
            fontweight="bold", color=INK, zorder=6, linespacing=1.3)
    ax.text(tx, ty - 6 - nl * 13, sub, ha=ha, va="top", fontsize=9.2, family=FONT,
            color=MUT, zorder=6, linespacing=1.4)

ax.text(OB[0], OB[1] - 142, "Exploded assembly", ha="center", fontsize=11, family=FONT,
        fontweight="bold", color=DEEP)
ax.text(OB[0], OB[1] - 153, "173 × 80 × 70 mm assembled", ha="center", fontsize=9.2,
        family=FONT, color=MUT)

# ── frame, title, spec strip ────────────────────────────────────────────
ax.set_xlim(-470, 470); ax.set_ylim(-226, 150)
ax.set_aspect("equal"); ax.axis("off")

ax.text(-470, 143, "Resondi", fontsize=19, fontweight="bold", family=FONT,
        color=DEEP, va="top")
ax.text(-470, 122, "Enclosure VER 2.0 — rendered from the production STL files",
        fontsize=10.8, family=FONT, color=MUT, va="top")

ax.plot([-470, 470], [-196, -196], color=LINE, lw=1.0)
strip = ("ESP32 dual-core, up to 240 MHz   ·   INMP441 digital MEMS microphone, I²S   ·   "
         "16 kHz / 16-bit mono PCM WAV   ·   16 GB microSD   ·   "
         "2.4 GHz Wi-Fi access point   ·   10,000 mAh battery   ·   PLA, FDM printed")
ax.text(0, -211, strip, ha="center", va="center", fontsize=9.8, family=FONT, color=INK)

fig.savefig(os.path.join(HERE, "..", "..", "figures", "Resondi-Device-Components.png"), facecolor="white",
            bbox_inches="tight", pad_inches=0.22)
print("wrote Resondi-Device-Components.png")
