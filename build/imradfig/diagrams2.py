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

OUT = _os.path.join(_BUILD, "..", "figures") + "/"

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
    zx, zy, zw, zh = 60, 740, 128, 112
    ax.text(zx + zw + 7, 890, "PER-ZONE INPUT", fontsize=6.8, ha="center",
            color=SECONDARY, fontweight="bold", family=SERIF, va="center")
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
    """The network as trained (model-rebuild/scripts/fusion.py, fdc3). Until 25 Nov 2026 this drew the plan's
    mel-spectrogram version, captioned "Planned", under a figure titled "as Built". Used by both papers."""
    PX, PY = 1900, 640
    fig, ax = canvas(PX, PY)
    views = [("Spectrogram", "log power, 0–4 kHz"),
             ("MFCC", "13 coefficients"),
             ("Chromagram", "12 pitch classes")]
    bh, vgap, y0, mid = 116, 40, 440, 342
    box(ax, 24, mid - 75, 222, 150, "Recording", "16 kHz mono", fill=LIGHT, lw=2.2, ts=7.9)
    box(ax, 292, mid - 75, 222, 150, "Window", "1 second", lw=1.8, ts=7.9)
    arrow(ax, (250, mid), (288, mid))
    for i, (t, sub) in enumerate(views):
        y = y0 - i * (bh + vgap)
        c = y + bh / 2
        arrow(ax, (518, mid), (586, c), lw=1.8)
        box(ax, 590, y, 310, bh, t, sub, ts=7.9, ss=6.2)
        arrow(ax, (904, c), (946, c))
        box(ax, 950, y, 250, bh, "CNN branch", "64 units", ts=7.9, ss=6.2)
        arrow(ax, (1204, c), (1290, mid), lw=1.8)
    box(ax, 1294, mid - 75, 250, 150, "Concatenate", "3 × 64 units", fill=LIGHT, lw=2.2, ts=7.9)
    arrow(ax, (1548, mid), (1588, mid))
    box(ax, 1592, mid - 75, 284, 150, "Dense, softmax", "four sound classes", fill=LIGHT, lw=2.2, ts=7.9)
    caption(ax, PX, "Three representations of one window are combined before a single decision;\n"
                    "window scores are then averaged over the breathing cycle or recording.", y=24)
    save(fig, OUT + "p2_fusion.png")


if __name__ == "__main__":
    d5_rules(); p2_fusion()
