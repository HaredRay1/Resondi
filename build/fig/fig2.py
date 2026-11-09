import os as _os
_BUILD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))).replace(chr(92), '/')
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

NAVY, MID = "#8E2A52", "#B5537E"
GREY, TEXT = "#7F7F7F", "#262626"

fig, ax = plt.subplots(figsize=(9.6, 5.0))
ax.set_xlim(0, 9.6); ax.set_ylim(0, 5.0); ax.axis("off")
ax.text(4.8, 4.72, "Serviceable market for Resondi in the Philippines",
        ha="center", fontsize=12.5, family="serif", color=NAVY, fontweight="bold")

tiers = [
    ("TAM", "Total addressable market", "~30,000 public health facilities",
     "26,504 barangay health stations, 2,682 rural health units,\n836 municipal and city health centres", NAVY),
    ("SAM", "Serviceable available market", "~3,500 facilities",
     "RHUs and municipal/city health centres — facilities with a\nbudget line and a resident clinician, plus nursing and medical schools", MID),
    ("SOM", "Serviceable obtainable market", "~50 facilities, 15 schools by Year 3",
     "MIMAROPA and partner LGUs; 10 facilities and 3 schools in Year 1,\nrising to roughly 25 and 7 in Year 2", "#C27396"),
]

top_w, bot_w, y0, h = 5.9, 4.0, 4.25, 1.18
for i, (tag, name, figure, detail, col) in enumerate(tiers):
    w_t = top_w - (top_w - bot_w) * (i / 3)
    w_b = top_w - (top_w - bot_w) * ((i + 1) / 3)
    yt, yb = y0 - i * (h + 0.09), y0 - i * (h + 0.09) - h
    cx = 2.95
    ax.add_patch(Polygon([(cx - w_t / 2, yt), (cx + w_t / 2, yt),
                          (cx + w_b / 2, yb), (cx - w_b / 2, yb)],
                         facecolor=col, edgecolor="white", linewidth=1.6))
    ax.text(cx, (yt + yb) / 2 + 0.17, f"{tag}  ·  {figure}", ha="center", va="center",
            color="white", fontsize=9.0, family="serif", fontweight="bold")
    ax.text(cx, (yt + yb) / 2 - 0.22, name, ha="center", va="center",
            color="white", fontsize=8.4, family="serif", style="italic")
    ax.text(6.10, (yt + yb) / 2, detail, ha="left", va="center",
            fontsize=8.3, family="serif", color=TEXT, linespacing=1.5)

ax.text(0.15, 0.30, "Facility counts: Department of Health, National Health Facility Registry (May 2025).",
        fontsize=7.6, family="serif", color=GREY)
ax.text(0.15, 0.08, "Obtainable market derived from the Year 1 and Year 2 revenue projections in the business model.",
        fontsize=7.6, family="serif", color=GREY)

fig.savefig(_BUILD + "/fig/fig2_market.png", dpi=240, bbox_inches="tight",
            pad_inches=0.05, facecolor="white")
print("written")
