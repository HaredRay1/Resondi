"""D5 rule-based interpretation layer, P2 the planned fusion architecture."""
import os as _os
_BUILD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))).replace(chr(92), '/')
from blocks import *
from theme import *
import textwrap


def wrap_to(ax, text, max_units, pt):
    """Wrap `text` so no rendered line exceeds max_units at `pt`."""
    from blocks import text_w
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if cur and text_w(ax, trial, pt) > max_units:
            lines.append(cur); cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return "\n".join(lines)

OUT = _BUILD + "/imradfig/"

RULES = [
 ("1", "All four zones Healthy",
      "Healthy — no adventitious sounds detected"),
 ("2", "Both upper zones contain a wheeze component",
      "Possible asthma — bilateral airway obstruction"),
 ("3", "Upper zone wheeze with lower zone crackles",
      "Possible bronchiolitis — mixed inflammation and secretions"),
 ("4", "Crackles in one or both lower zones",
      "Possible pneumonia or pulmonary edema — alveolar involvement"),
 ("5", "All four zones Wheezing with Crackles",
      "Possible severe bronchiolitis or diffuse inflammation"),
 ("6", "No preceding rule is satisfied",
      "Further clinical evaluation needed — no single possibility"),
]


def d5_rules():
    PX, PY = 1900, 1090
    fig, ax = canvas(PX, PY)

    # the four zones the rules read
    ax.text(150, 905, "PER-ZONE INPUT", fontsize=7.6,
            color=SECONDARY, fontweight="bold", family=SERIF, va="center")
    zx, zy, zw, zh = 60, 740, 128, 112
    for i, (lab, name) in enumerate([("UL", "upper left"), ("UR", "upper right"),
                                     ("LL", "lower left"), ("LR", "lower right")]):
        x = zx + (i % 2) * (zw + 14)
        y = zy - (i // 2) * (zh + 14)
        box(ax, x, y, zw, zh, lab, name, fill=PALE, edge=MID, lw=1.5,
            ts=9.0, ss=5.8)
    ax.text(zx + zw + 7, 586, "four zones, four classes each",
            ha="center", fontsize=6.0, color=GREY, style="italic", family=SERIF)

    arrow(ax, (zx + zw + 7, 552), (zx + zw + 7, 504), lw=2.2)
    ax.text(zx + zw + 7, 480, "rule layer", ha="center", va="top",
            fontsize=6.8, color=PRIMARY, family=SERIF, style="italic")

    # the six rules
    x0, w_cond, w_out, h, gap = 450, 600, 760, 128, 18
    y = PY - 132 - h
    ax.text(x0, PY - 92, "CONDITION", fontsize=6.8, color=SECONDARY,
            fontweight="bold", family=SERIF)
    ax.text(x0 + w_cond + 90, PY - 92, "LITERATURE-SUPPORTED POSSIBILITY",
            fontsize=6.8, color=SECONDARY, fontweight="bold", family=SERIF)
    for n, cond, out in RULES:
        ax.add_patch(FancyBboxPatch((x0 - 46, y), 40, h,
                     boxstyle="round,pad=0,rounding_size=5",
                     facecolor=PRIMARY, edgecolor="none", zorder=2))
        ax.text(x0 - 26, y + h / 2, n, ha="center", va="center", fontsize=8.8,
                color="white", fontweight="bold", family=SERIF, zorder=3)
        fill = PALE if n == "6" else SURFACE
        ax.add_patch(FancyBboxPatch((x0, y), w_cond, h,
                     boxstyle="round,pad=0,rounding_size=5",
                     facecolor=fill, edgecolor=RULE, lw=1.4, zorder=2))
        ax.text(x0 + 20, y + h / 2, wrap_to(ax, cond, w_cond - 46, 7.0),
                va="center",
                fontsize=7.0, color=INK, family=SERIF, zorder=3,
                linespacing=1.45)
        arrow(ax, (x0 + w_cond + 8, y + h / 2), (x0 + w_cond + 62, y + h / 2),
              lw=1.7)
        ax.add_patch(FancyBboxPatch((x0 + w_cond + 72, y), w_out, h,
                     boxstyle="round,pad=0,rounding_size=5",
                     facecolor=fill, edgecolor=MID if n != "6" else RULE,
                     lw=1.4, zorder=2))
        ax.text(x0 + w_cond + 94, y + h / 2,
                wrap_to(ax, out, w_out - 46, 7.0),
                va="center", fontsize=7.0, color=INK, family=SERIF, zorder=3,
                linespacing=1.45)
        y -= h + gap

    caption(ax, PX, "Every output is framed as a possibility requiring clinical "
                    "evaluation. None is a diagnosis.", y=16)
    save(fig, OUT + "d5_rules.png")


def p2_fusion():
    PX, PY = 1900, 660
    fig, ax = canvas(PX, PY)
    views = [("Mel-spectrogram", "energy over time", "crackles — transient"),
             ("MFCC", "spectral envelope", "overall timbre"),
             ("Chromagram", "pitch classes", "wheezes — tonal")]
    bw, bh, vgap = 300, 124, 66
    y0 = 480
    box(ax, 60, 280, 200, 150, "Recording", "preprocessed", fill=LIGHT, lw=2.2)

    for i, (t, s, why) in enumerate(views):
        y = y0 - i * (bh + vgap)
        box(ax, 350, y, bw, bh, t, s, ts=7.9, ss=6.2)
        ax.text(350 + bw / 2, y - 22, why, ha="center", fontsize=5.9,
                color=GREY, style="italic", family=SERIF)
        arrow(ax, (264, 355), (346, y + bh / 2), rad=0.0, lw=1.8)
        box(ax, 730, y, 250, bh, "CNN branch", "conv · pool", ts=7.9, ss=6.2)
        arrow(ax, (654, y + bh / 2), (726, y + bh / 2))
        arrow(ax, (984, y + bh / 2), (1186, 355), rad=0.0, lw=1.8)

    box(ax, 1190, 280, 250, 150, "Concatenate", "fused vector",
        fill=LIGHT, lw=2.2)
    arrow(ax, (1444, 355), (1512, 355))
    box(ax, 1516, 280, 230, 150, "Softmax", "four classes",
        fill=LIGHT, lw=2.2)

    caption(ax, PX, "Feature-level fusion: three representations of one "
                    "recording, combined before a single decision. "
                    "Planned — not implemented at the time of evaluation.",
            y=30)
    save(fig, OUT + "p2_fusion.png")


if __name__ == "__main__":
    d5_rules(); p2_fusion()
