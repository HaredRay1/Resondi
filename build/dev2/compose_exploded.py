"""Exploded view of the version 2.0 device (user, 25 Nov 2026, after a phone exploded view they saw on TikTok).

    python build/dev2/compose_exploded.py           -> figures/Resondi-Exploded-View.png        (light, for the paper)
                                                       figures/Resondi-Exploded-View-Dark.png   (1080 x 1920 poster)
    python build/dev2/compose_exploded.py --video   -> figures/Resondi-Exploded-View.mp4        (assembles, opens, labels)

Stacks the layers of render_layers.py. Names and specifications come from the version 2.0 bill of materials and the
product specification sheet only. The internal layout is illustrative (it is not recorded).
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
LAY = os.path.join(HERE, "out", "layers")
FIGS = os.path.normpath(os.path.join(HERE, "..", "..", "figures"))
J = json.load(open(os.path.join(LAY, "layers.json")))
W, H = J["W"], J["H"]
UP = J["px_per_mm_up"]

# how far each layer is lifted when fully open, in millimetres of the model
LIFT = {"sensor": 0, "body": 0, "battery": 62, "board": 112, "cover": 172, "lcd": 224, "leds": 176, "buttons": 232,
        "screws": 318, "mic": 34}
ORDER = ["body", "battery", "board", "front", "sensor", "mic", "cover", "leds", "lcd", "buttons", "screws"]
# callout: (point in layers.json, layer it belongs to, name, specification)
PARTS = [
    ("screws", "screws", "M3 bolts and brass inserts", "fasten the enclosure"),
    ("buttons", "buttons", "HEART and LUNGS buttons", "2 push buttons"),
    ("leds", "leds", "Status LEDs", "5 mm · 220 Ω resistors"),
    ("lcd", "lcd", "Character LCD", "20 × 4 · I²C adapter"),
    ("cover", "cover", "Top cover", "3D-printed PLA"),
    ("esp", "board", "ESP32 board", "dual-core · 240 MHz · Wi-Fi"),
    ("boost", "board", "Boost converter", "LM2577 · DC-DC"),
    ("pcb", "board", "Circuit board", "FR4 · 7 × 9 cm"),
    ("sd", "board", "MicroSD module and card", "32 GB"),
    ("battery", "battery", "Li-ion battery", "10,000 mAh"),
    ("rocker", "body", "Power rocker switch", "on / off"),
    ("body", "body", "Enclosure body", "3D-printed PLA"),
    ("mic", "mic", "INMP441 microphone", "digital MEMS · I²S"),
    ("sensor", "sensor", "Chest piece", "with 22 AWG sensor wires"),
]


def load():
    L = {}
    for n in LIFT:
        L[n] = Image.open(os.path.join(LAY, n + ".png")).convert("RGBA")
    for n in ("lcd_top", "buttons_top"):
        L[n] = Image.open(os.path.join(LAY, n + ".png")).convert("RGBA")
    # the body's front walls, drawn again over whatever is still inside it: everything below the opening's front edges
    (x0, y0), (x1, y1), (x2, y2) = J["rim"]
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(0, y0), (x0, y0), (x1, y1), (x2, y2), (W, y2), (W, H), (0, H)], fill=255)
    f = L["body"].copy()
    a = f.getchannel("A")
    f.putalpha(Image.composite(a, Image.new("L", (W, H), 0), m))
    L["front"] = f
    return L


def font(kind, size):
    return ImageFont.truetype({"b": "C:/Windows/Fonts/seguisb.ttf", "r": "C:/Windows/Fonts/segoeui.ttf",
                               "m": "C:/Windows/Fonts/consola.ttf", "sb": "C:/Windows/Fonts/timesbd.ttf",
                               "s": "C:/Windows/Fonts/times.ttf"}[kind], size)


CLEAR = {"lcd": 4, "buttons": 20}      # millimetres


def stack(L, t, pad_top):
    """The device opened by t (0 closed, 1 open) on a transparent canvas, with pad_top pixels added above."""
    c = Image.new("RGBA", (W, H + pad_top), (0, 0, 0, 0))
    for n in ORDER:
        im = L[n]
        # until a part has risen clear of the cover, only what is above the cover is visible
        if n in CLEAR and (LIFT[n] - LIFT["cover"]) * t < CLEAR[n]:
            im = L[n + "_top"]
        if n == "mic":
            if t <= 0.02:
                continue
            im = im.copy()
            im.putalpha(im.getchannel("A").point(lambda v, k=min(1, t * 4): int(v * k)))
        dy = int(round(LIFT.get(n, 0) * UP * t))
        c.alpha_composite(im, (0, pad_top - dy))
    return c


import math  # noqa: E402


def px(x, y, z):
    """Screen position of a point of the model in millimetres (the projection of render_layers.py)."""
    a, e = J["az"], J["el"]
    dx, dy, dz = x - J["target"][0], y - J["target"][1], z - J["target"][2]
    r = dx * math.cos(a) + dy * math.sin(a)
    u = -dx * math.sin(a) * math.sin(e) + dy * math.cos(a) * math.sin(e) + dz * math.cos(e)
    return W / 2 + r * J["px_per_mm"], H / 2 - u * J["px_per_mm"]


# callout anchors that differ from layers.json: p = the printed version, d = the dark poster
ANCHOR = {"p": {"lcd": (-60, 8, 54), "cover": (30, -46, 50), "leds": (24, -1, 52), "screws": (74, 44, 51)},
          "d": {"lcd": (12, 30, 54), "cover": (76, 10, 50), "esp": (-6, 32, 35), "pcb": (25, 12, 26.6),
                "battery": (44, 0, 18), "boost": (-10, -6, 30)}}


def point(name, layer, t, pad_top, style="p"):
    x, y = px(*ANCHOR[style][name]) if name in ANCHOR[style] else J["points"][name]
    return x, y + pad_top - LIFT[layer] * UP * t


PAD = int(LIFT["screws"] * UP) - 180


def background(w, h):
    """Dark plum gradient with a soft vignette."""
    g = Image.new("RGB", (1, h))
    for y in range(h):
        k = 1 - abs(y / h - 0.45) * 1.5
        g.putpixel((0, y), (int(17 + 22 * max(k, 0)), int(14 + 12 * max(k, 0)), int(18 + 17 * max(k, 0))))
    g = g.resize((w, h))
    glow = Image.new("L", (w, h), 0)
    ImageDraw.Draw(glow).ellipse((-w * 0.25, h * 0.2, w * 0.95, h * 0.8), fill=70)
    glow = glow.filter(ImageFilter.GaussianBlur(220))
    return Image.composite(Image.new("RGB", (w, h), (74, 46, 60)), g, glow)


def callouts(d, pts, x_label, y_top, y_step, x_elbow, fonts, cols, alpha=None, r=5, dy=(0, 24, 62)):
    """pts: [(x, y, name, spec)] already in label order. Draws the elbow leaders and the numbered labels."""
    num, name, spec, line, dot = cols
    fn, fb, fs = fonts
    for i, (x, y, nm, sp) in enumerate(pts):
        a = 255 if alpha is None else int(255 * max(0, min(1, alpha - i * 0.55)))
        if a <= 0:
            continue
        ly = y_top + i * y_step
        yy = ly + dy[1] - 2
        d.line([(x, y), (x_elbow, yy), (x_label - 14, yy)], fill=(*line, int(a * 0.85)), width=2, joint="curve")
        d.ellipse((x - r, y - r, x + r, y + r), fill=(*dot, a))
        d.text((x_label, ly), f"{i + 1:02d}", font=fn, fill=(*num, a))
        d.text((x_label, ly + dy[1]), nm, font=fb, fill=(*name, a))
        d.text((x_label, ly + dy[2]), sp, font=fs, fill=(*spec, a))


D_LABELS = {"buttons": ("Buttons and status LEDs", "2 push buttons · 2 × 5 mm LEDs")}
D_SKIP = {"leds", "mic", "sensor"}


def poster(L, t=1.0, label_alpha=None, base=None):
    w, h = 1080, 1920
    img = (base.copy() if base else background(w, h)).convert("RGBA")
    dev = stack(L, t, PAD)
    k = 0.60
    ds = dev.resize((int(dev.width * k), int(dev.height * k)), Image.LANCZOS)
    ox, oy = -8, 1770 - ds.height
    oy -= int((1 - t) * 330)                       # the closed device sits nearer the middle
    img.alpha_composite(ds, (0, max(oy, 0)), (-ox, max(-oy, 0), ds.width, ds.height))
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    fm = font("m", 27)
    d.text((70, 92), "RESONDI", font=fm, fill=(245, 238, 242, 255))
    d.text((70 + d.textlength("RESONDI ", font=fm), 92), "/ EXPLODED VIEW", font=fm, fill=(150, 132, 142, 255))
    if label_alpha is None or label_alpha > 0:
        cols = ((240, 120, 130), (245, 240, 243), (165, 150, 158), (205, 195, 200), (240, 110, 120))
        fonts = (font("m", 18), font("b", 25), font("m", 17))
        pts = []
        for nm, lay, a, b in PARTS:
            if nm in D_SKIP:
                continue
            a, b = D_LABELS.get(nm, (a, b))
            x, y = point(nm, lay, t, PAD, "d")
            pts.append((x * k + ox, y * k + oy, a, b))
        pts.sort(key=lambda q: q[1] - (80 if q[2] == "Boost converter" else 0))   # keeps its line clear of the ESP32's
        callouts(d, pts, 748, 250, 128, 706, fonts, cols, alpha=label_alpha, dy=(0, 22, 56))
        # the two parts on the left keep their labels beside them
        n = len(pts)
        for i, (nm, lx, ly, lines, spec) in enumerate((("mic", 48, 1118, ("INMP441", "microphone"), "digital MEMS"),
                                                       ("sensor", 48, 1668, ("Chest piece",), "22 AWG sensor wires"))):
            al = 255 if label_alpha is None else int(255 * max(0, min(1, label_alpha - (n + i) * 0.55)))
            if al <= 0:
                continue
            x, y = point(nm, nm, t, PAD, "d")
            x, y = x * k + ox, y * k + oy
            end = (lx + 34, ly + 118) if nm == "mic" else (lx + 34, ly - 8)
            d.line([(x, y), end], fill=(*cols[3], int(al * 0.85)), width=2)
            d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(*cols[4], al))
            d.text((lx, ly), f"{n + i + 1:02d}", font=fonts[0], fill=(*cols[0], al))
            for m, t_ in enumerate(lines):
                d.text((lx, ly + 22 + 30 * m), t_, font=fonts[1], fill=(*cols[1], al))
            d.text((lx, ly + 26 + 30 * len(lines)), spec, font=fonts[2], fill=(*cols[2], al))
    d.text((70, 1850), "Internal layout illustrative. Parts from the version 2.0 bill of materials.", font=font("r", 20),
           fill=(140, 124, 133, 255))
    img.alpha_composite(ov)
    return img.convert("RGB")


def paper(L):
    """Light version for print: labels in two columns, left and right of the device."""
    t = 1.0
    dev = stack(L, t, PAD)
    box = dev.getbbox()
    k = 1.0
    w, h = 2620, box[3] - box[1] + 120
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    ox, oy = (w - (box[2] - box[0])) // 2 - box[0], 60 - box[1]
    img.alpha_composite(dev, (ox, oy) if oy >= 0 else (ox, 0), (0, max(-oy, 0), dev.width, dev.height))
    d = ImageDraw.Draw(img)
    fb, fs, fn = font("sb", 47), font("s", 41), font("s", 41)
    pts = []
    for i, (nm, lay, a, b) in enumerate(PARTS):
        x, y = point(nm, lay, t, PAD)
        pts.append([x + ox, y + oy, a, b])
    pts.sort(key=lambda q: q[1])
    for i, q in enumerate(pts):
        q.append(i + 1)
    left = [q for q in pts if q[2] in LEFT]
    right = [q for q in pts if q[2] not in LEFT]
    for side, qs in (("L", left), ("R", right)):
        step = (h - 190) / max(len(qs) - 1, 1)
        ys = [40 + j * step for j in range(len(qs))]
        for (x, y, a, b, n), ly in zip(qs, ys):
            yy = ly + 28
            tw = max(d.textlength(f"{n}. {a}", font=fb), d.textlength(b, font=fs))
            if side == "R":
                lx = w - 690
                d.line([(x, y), (lx - 70, yy), (lx - 16, yy)], fill=(142, 42, 82), width=4)
                d.text((lx, ly), f"{n}. {a}", font=fb, fill=(26, 26, 26)); d.text((lx, ly + 54), b, font=fs, fill=(95, 85, 90))
            else:
                rx = 610
                d.line([(x, y), (rx + 70, yy), (rx + 16, yy)], fill=(142, 42, 82), width=4)
                d.text((rx, ly), f"{n}. {a}", font=fb, fill=(26, 26, 26), anchor="ra")
                d.text((rx, ly + 54), b, font=fs, fill=(95, 85, 90), anchor="ra")
            d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=(142, 42, 82), outline=(255, 255, 255), width=3)
    return img.convert("RGB")


LEFT = {"Character LCD", "Status LEDs", "ESP32 board", "Boost converter", "Chest piece", "INMP441 microphone"}


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * x * (x * (6 * x - 15) + 10)


if __name__ == "__main__":
    L = load()
    if "--video" in sys.argv:
        import numpy as np
        import subprocess
        import imageio_ffmpeg
        out = os.path.join(FIGS, "Resondi-Exploded-View.mp4")
        fps = 30
        base = background(1080, 1920)
        cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r",
               str(fps), "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
               "-movflags", "+faststart", out]
        pr = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
        # 0.8 s closed, 2.4 s opening, 3.4 s labels appearing, 3 s hold
        last = None
        for f in range(int(9.6 * fps)):
            s = f / fps
            t = ease((s - 0.8) / 2.4)
            la = max(0.0, (s - 3.0) / 3.2) * (len(PARTS) * 0.55 + 1)
            key = (round(t, 4), round(min(la, len(PARTS) * 0.55 + 1), 3))
            if key != (last[0] if last else None):
                last = (key, np.asarray(poster(L, t, la, base)).tobytes())
            pr.stdin.write(last[1])
        pr.stdin.close()
        pr.wait()
        print("wrote", out)
    else:
        p = paper(L)
        p.save(os.path.join(FIGS, "Resondi-Exploded-View.png"), dpi=(400, 400))
        q = poster(L)
        q.save(os.path.join(FIGS, "Resondi-Exploded-View-Dark.png"))
        print("wrote", p.size, q.size)
