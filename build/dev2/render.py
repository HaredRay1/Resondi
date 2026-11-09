"""Render the Resondi VER2.0 enclosure from its STLs.

Painter's-algorithm renderer: project each triangle, shade it by its normal
against a key light, sort back-to-front, draw as a 2D polygon collection.
Faster and cleaner than matplotlib's 3D axes at this face count.
"""
import glob
import os
import sys

import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

import os
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "source-material", "stl")
PART = {os.path.splitext(os.path.basename(f))[0]: f for f in glob.glob(f"{A}/*.stl")}


def rot(ax, deg):
    t = np.radians(deg)
    c, s = np.cos(t), np.sin(t)
    if ax == "x":
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if ax == "y":
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def shade(mesh, M, base_rgb, light=np.array([-0.35, -0.55, 0.76])):
    """Return (polys2d, facecolors, depth) for one mesh under rotation M."""
    v = mesh.vertices @ M.T
    tris = v[mesh.faces]                      # (n,3,3)
    n = mesh.face_normals @ M.T
    n /= (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)
    lam = np.clip(n @ light, 0, 1)
    amb = 0.34
    k = (amb + (1 - amb) * lam)[:, None]
    base = np.array(base_rgb)[None, :]
    rgb = np.clip(base * k * 1.12, 0, 1)
    # rim: faces near-perpendicular to view pick up a touch of light
    rim = np.clip(1 - np.abs(n[:, 2]), 0, 1)[:, None] ** 3
    rgb = np.clip(rgb + rim * 0.18, 0, 1)
    depth = tris[:, :, 2].mean(axis=1)
    return tris[:, :, :2], rgb, depth


def draw(ax, parts, M, scale=1.0, offset=(0, 0)):
    polys, cols, deps = [], [], []
    for mesh, rgb, dz in parts:
        m = mesh.copy()
        m.apply_translation([0, 0, dz])
        p, c, d = shade(m, M, rgb)
        polys.append(p); cols.append(c); deps.append(d)
    P = np.concatenate(polys); C = np.concatenate(cols); D = np.concatenate(deps)
    order = np.argsort(D)
    P, C = P[order], C[order]
    P = P * scale + np.array(offset)
    ax.add_collection(PolyCollection(P, facecolors=C, edgecolors="none",
                                     linewidths=0, zorder=2, antialiased=True))
    return P.reshape(-1, 2)


def bounds(pts, pad=0.04):
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    r = (hi - lo).max()
    c = (lo + hi) / 2
    return c, r * (1 + pad)


if __name__ == "__main__":
    base = trimesh.load(PART["RESONDI_BASE_VER2.0"])
    cover = trimesh.load(PART["RESONDI_COVER_VER2.0"])
    mount = trimesh.load(PART["STETH_MOUNT"])
    scov = trimesh.load(PART["STETH_COVER"])
    for m in (base, cover, mount, scov):
        m.apply_translation(-m.bounding_box.centroid)

    view = sys.argv[1] if len(sys.argv) > 1 else "iso"
    ANG = {"iso": (("x", -62), ("z", 26)), "front": (("x", -90), ("z", 0)),
           "top": (("x", 0), ("z", 0)), "side": (("x", -90), ("z", 90))}[view]
    M = np.eye(3)
    for ax_, d in ANG:
        M = rot(ax_, d) @ M

    fig, ax = plt.subplots(figsize=(10, 7), dpi=150)
    ax.set_facecolor("white")
    ROSE = (0.78, 0.22, 0.42)
    GREY = (0.62, 0.60, 0.61)
    pts = draw(ax, [(base, GREY, 0.0), (cover, ROSE, 48.0)], M)
    c, r = bounds(pts)
    ax.set_xlim(c[0] - r / 2, c[0] + r / 2)
    ax.set_ylim(c[1] - r / 2, c[1] + r / 2)
    ax.set_aspect("equal"); ax.axis("off")
    fig.savefig(f"probe_{view}.png", facecolor="white", bbox_inches="tight")
    print("wrote", f"probe_{view}.png")
