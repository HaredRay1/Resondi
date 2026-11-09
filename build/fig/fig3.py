import os as _os
_BUILD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))).replace(chr(92), '/')
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAVY, GREY = "#1F4E79", "#7F7F7F"
PALETTE = ["#1F4E79", "#2E75B6", "#C0504D", "#4A90CE", "#6AA3D6",
           "#8DBBE3", "#A8CBE8", "#BFD8EF", "#D5E5F5", "#E8F1FA"]

rows = [
    ("Clinical validation", 120000, 24.00),
    ("AI development", 102000, 20.40),
    ("Contingency", 50000, 10.00),
    ("Cloud infrastructure and operation", 48000, 9.60),
    ("Hardware refinement", 42000, 8.40),
    ("Production working capital", 40000, 8.00),
    ("Mobile application", 38000, 7.60),
    ("Intellectual property and registration", 25000, 5.00),
    ("Documentation and compliance", 20000, 4.00),
    ("Deployment and marketing", 15000, 3.00),
]
assert sum(r[1] for r in rows) == 500000, "allocation must total ₱500,000"
assert round(sum(r[2] for r in rows), 2) == 100.00, "shares must total 100%"
sizes = [r[1] for r in rows]
labels = [f"{r[0]}\n₱{r[1]:,}  ·  {r[2]:.2f}%" for r in rows]

fig, ax = plt.subplots(figsize=(9.4, 5.6))
wedges, _ = ax.pie(
    sizes, startangle=90, counterclock=False, colors=PALETTE,
    wedgeprops=dict(width=0.44, edgecolor="white", linewidth=2.2))

ax.text(0, 0.10, "₱500,000", ha="center", va="center", fontsize=19,
        family="serif", color=NAVY, fontweight="bold")
ax.text(0, -0.16, "total requirement", ha="center", va="center", fontsize=9.5,
        family="serif", color=GREY, style="italic")

leg = ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1.00, 0.5),
                frameon=False, labelspacing=0.62,
                prop={"family": "serif", "size": 8.6})
ax.set_aspect("equal")

fig.savefig(_BUILD + "/fig/fig3_financial.png", dpi=240, bbox_inches="tight",
            pad_inches=0.08, facecolor="white")
print("written")
