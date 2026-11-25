"""Bill of materials of the version 2.0 device, and the cost-breakdown chart (user, 25 Nov 2026: show Resondi's
budget the way page 9 of the 83-page paper does: a table of materials and a pie chart).

    python build/fig/bom_v2.py   -> figures/Resondi-Cost-Breakdown.png

Source of the items and prices: the VER 2.0 bill of materials (history/final-2026-11-02/
Resondi_Bill_of_Materials_VER2.0-PETG-2875-not-current.docx: 20 x 4 LCD, 32 GB card) with the casing line of
source-material/Resondi_Bill_of_Materials.docx (PLA, 300 pesos, instead of PETG, 400), because the enclosure is PLA
(user, 2 Nov 2026). The total is checked against the project's 2,775 pesos, so a wrong edit stops the build.
"""
import os

TOTAL = 2775.00
# (material as printed, quantity, unit price, category)
ITEMS = [
    ("Acoustic stethoscope set", 1, 600.00, "Acoustic sensing"),
    ("10,000 mAh Li-ion battery", 1, 350.00, "Power supply"),
    ("3D-printed PLA enclosure", 1, 300.00, "Enclosure"),
    ("ESP32 30-pin board", 1, 280.00, "Microcontroller"),
    ("20 × 4 LCD with I²C adapter", 1, 280.00, "Display and controls"),
    ("32 GB microSD card", 1, 280.00, "Storage"),
    ("INMP441 MEMS microphone", 1, 210.00, "Acoustic sensing"),
    ("LM2577 boost converter", 1, 120.00, "Power supply"),
    ("Push buttons", 2, 50.00, "Display and controls"),
    ("7 × 9 cm FR4 circuit board", 1, 80.00, "Circuit board and wiring"),
    ("MicroSD card module", 1, 60.00, "Storage"),
    ("22 AWG stranded wires (lot)", 1, 50.00, "Circuit board and wiring"),
    ("Power rocker switch", 1, 30.00, "Power supply"),
    ("M3 bolts and brass inserts (lot)", 1, 20.00, "Enclosure"),
    ("5 mm LEDs", 2, 5.00, "Display and controls"),
    ("220 Ω resistors", 2, 2.50, "Circuit board and wiring"),
]
assert abs(sum(q * p for _, q, p, _ in ITEMS) - TOTAL) < 1e-9, "the parts no longer add up to 2,775"

CATS = {}
for _n, _q, _p, _c in ITEMS:
    CATS[_c] = CATS.get(_c, 0) + _q * _p
CATS = dict(sorted(CATS.items(), key=lambda kv: -kv[1]))


def table_rows():
    return ([["Materials", "Quantity", "Price (₱)", "Total (₱)"]]
            + [[n, str(q), f"{p:,.2f}", f"{q * p:,.2f}"] for n, q, p, _ in ITEMS]
            + [["Total", "", "", f"{TOTAL:,.2f}"]])


def chart(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    plt.rcParams["font.family"] = "Times New Roman"
    # validated (dataviz validate_palette.js, light, including the wrap-around pair)
    cols = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#6250d6", "#e87ba4", "#008300"]
    ink, mute = "#1a1a1a", "#52514e"
    names, vals = list(CATS), list(CATS.values())
    # one column wide (3 in), printed at its own size, so the point sizes below are the printed ones
    fig = plt.figure(figsize=(3.0, 4.15), dpi=400)
    fig.text(0.5, 0.955, "Cost Breakdown of the Version 2.0 Device", ha="center", fontsize=9.5, fontweight="bold", color=ink)
    fig.text(0.5, 0.918, f"Total cost: ₱{TOTAL:,.2f}", ha="center", fontsize=8.5, color=mute)
    ax = fig.add_axes([0.10, 0.41, 0.80, 0.50])
    wedges, _ = ax.pie(vals, colors=cols, startangle=90, counterclock=False, radius=1.0,
                       wedgeprops=dict(edgecolor="white", linewidth=1.2))
    import math
    for w, v, c in zip(wedges, vals, cols):
        a = math.radians((w.theta1 + w.theta2) / 2)
        pct = v / TOTAL * 100
        r = 0.68 if pct >= 9 else 1.14
        ax.text(r * math.cos(a), r * math.sin(a), f"{pct:.1f}%", ha="center", va="center", fontsize=8.5,
                fontweight="bold", color="white" if c in ("#2a78d6", "#6250d6") and pct >= 9 else ink)
    ax.set_xlim(-1.2, 1.2); ax.set_ylim(-1.12, 1.25)
    lx = fig.add_axes([0.01, 0.01, 0.98, 0.39]); lx.set_xlim(0, 1); lx.set_ylim(0, 1); lx.axis("off")
    lx.add_patch(FancyBboxPatch((0.01, 0.205), 0.98, 0.785, boxstyle="round,pad=0,rounding_size=0.012", fc="white",
                                ec="#c9c9c9", lw=0.7))
    for k, (n, v, c) in enumerate(zip(names, vals, cols)):
        y = 0.93 - k * 0.1105
        lx.plot([0.05], [y], "o", ms=5.5, color=c)
        lx.text(0.095, y, n, va="center", fontsize=8.5, color=ink)
        lx.text(0.785, y, f"₱{v:,.2f}", va="center", ha="right", fontsize=8.5, color=ink)
        lx.text(0.965, y, f"({v / TOTAL * 100:.1f}%)", va="center", ha="right", fontsize=8.5, color=mute)
    lx.add_patch(FancyBboxPatch((0.01, 0.02), 0.98, 0.14, boxstyle="round,pad=0,rounding_size=0.012",
                                fc="#eeeef1", ec="#9a9aa5", lw=0.7))
    lx.text(0.5, 0.088, f"Total cost: ₱{TOTAL:,.2f}", ha="center", va="center", fontsize=9.5, fontweight="bold", color=ink)
    fig.savefig(out, facecolor="white")


if __name__ == "__main__":
    ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    f = os.path.join(ROOT, "figures", "Resondi-Cost-Breakdown.png")
    chart(f)
    print("wrote", f)
    for c, v in CATS.items():
        print(f"  {c:<26} {v:>9,.2f}  {v / TOTAL * 100:5.1f}%")
