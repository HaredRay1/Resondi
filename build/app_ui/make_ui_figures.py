"""App screen figures for the IMRaD (user, 18 Nov 2026: "they have the app ui in the results and discussion").

Reads the raw phone screenshots captured from resondi.base44.app (375 x 812 viewport, saved at 267 x 579) in
Downloads/Resondi-private/app-screens-raw/ (kept private: they show account and patient names), masks every name,
age and file name, and writes three phone-frame panels to figures/:

    ui1_patient.png       welcome, patient dashboard, full exam, lung guide, heart guide
    ui2_records.png       device transfer, history by site, recording result, trends
    ui3_practitioner.png  practitioner dashboard, patient record, analysis, exercise approval, admin dashboard

    python build/app_ui/make_ui_figures.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
RAW = os.path.normpath(os.path.join(ROOT, "..", "Resondi-private", "app-screens-raw"))
OUT = os.path.join(ROOT, "figures")
SCALE = 3                       # upscale for print
FONT_B = "C:/Windows/Fonts/arialbd.ttf"
FONT_R = "C:/Windows/Fonts/arial.ttf"
FONT_SERIF = "C:/Windows/Fonts/times.ttf"

# Masks, in the 267 x 579 screenshot's pixels: (box, replacement text or None, font size, bold)
MASKS = {
    "03-pract-dashboard.jpg": [((8, 48, 200, 66), "Welcome, Doctor", 12, True),
                               ((50, 329, 180, 342), "Patient", 7.5, True),
                               ((50, 420, 180, 433), "Patient", 7.5, True),
                               ((50, 511, 180, 524), "Patient", 7.5, True)],
    "04-pract-patient.jpg": [((20, 122, 200, 137), "Patient", 9.5, True),
                             ((20, 139, 200, 153), None, 0, False)],
    "07-pat-dashboard.jpg": [((8, 51, 200, 66), "Hello, Patient", 10.5, True)],
    "13-pat-session.jpg": [((20, 175, 250, 188), None, 0, False)],
}

PANELS = {
    "ui1_patient.png": [("01-welcome.jpg", "(a) Welcome"), ("07-pat-dashboard.jpg", "(b) Patient dashboard"),
                        ("10-pat-full-exam.jpg", "(c) Full examination"),
                        ("08-pat-lung-guide.jpg", "(d) Lung Mode guide"),
                        ("09-pat-heart-guide.jpg", "(e) Heart Mode guide")],
    "ui2_records.png": [("11-pat-device-transfer.jpg", "(a) Transfer from device"),
                        ("12-pat-history.jpg", "(b) History by site"),
                        ("13-pat-session.jpg", "(c) Recording result"),
                        ("14-pat-trends.jpg", "(d) Trends over time")],
    "ui3_practitioner.png": [("03-pract-dashboard.jpg", "(a) Practitioner dashboard"),
                             ("04-pract-patient.jpg", "(b) Patient record"),
                             ("05-pract-analysis.jpg", "(c) Analysis for review"),
                             ("06-pract-exercises.jpg", "(d) Exercise approval"),
                             ("02-admin-dashboard.jpg", "(e) Administrator")],
}


def masked(name):
    im = Image.open(os.path.join(RAW, name)).convert("RGB")
    if im.size != (267, 579):                               # one screen was captured at the full 375 x 812
        im = im.resize((267, 579), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    for (x0, y0, x1, y1), text, size, bold in MASKS.get(name, []):
        # background: the colour at the box's own top-left corner (inside the card, not on its border)
        bg = im.getpixel((x0, y0))
        d.rectangle((x0, y0, x1, y1), fill=bg)
        if text:
            f = ImageFont.truetype(FONT_B if bold else FONT_R, size)
            d.text((x0 + 2, (y0 + y1) / 2), text, font=f, fill=(43, 29, 36), anchor="lm")
    return im.resize((im.width * SCALE, im.height * SCALE), Image.LANCZOS)


def phone(im):
    pad, r = 9 * SCALE, 22 * SCALE
    w, h = im.width + 2 * pad, im.height + 2 * pad
    frame = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=(34, 30, 33))
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=r - pad, fill=255)
    frame.paste(im, (pad, pad), mask)
    return frame


def panel(items, out):
    phones = [phone(masked(f)) for f, _ in items]
    gap, cap_h, margin = 24 * SCALE, 30 * SCALE, 10 * SCALE
    W = sum(p.width for p in phones) + gap * (len(phones) - 1) + 2 * margin
    H = phones[0].height + cap_h + 2 * margin
    canvas = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(FONT_SERIF, 13 * SCALE)
    x = margin
    for p, (_, cap) in zip(phones, items):
        canvas.paste(p, (x, margin), p)
        d.text((x + p.width / 2, margin + p.height + 8 * SCALE), cap, font=f, fill=(30, 30, 30), anchor="ma")
        x += p.width + gap
    canvas.save(os.path.join(OUT, out), dpi=(300, 300))
    print("wrote", out, canvas.size)


if __name__ == "__main__":
    for out, items in PANELS.items():
        panel(items, out)
