"""Composite the podium render onto white with a soft pink glow behind the device.

Run after render_podium.py:  python build/dev2/compose_podium.py
Writes figures/Resondi-Device-Podium.png (and a .jpg copy).
"""
import os
from PIL import Image, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "figures"))
full = Image.open(os.path.join(HERE, "out", "podium_full.png")).convert("RGBA")
mask = Image.open(os.path.join(HERE, "out", "podium_mask.png")).convert("RGBA").split()[3]

W, H = full.size
GLOW = (233, 120, 170)  # soft version of the rose #E91E76

# Thicken the device silhouette, shift it up and to the right, then blur it
m = mask.point(lambda a: 255 if a > 20 else 0).filter(ImageFilter.MaxFilter(41))
shifted = Image.new("L", (W, H), 0)
shifted.paste(m, (38, -38))
glow_a = shifted.filter(ImageFilter.GaussianBlur(22)).point(lambda a: int(a * 0.85))

canvas = Image.new("RGBA", (W, H), (255, 255, 255, 255))
canvas.paste(Image.new("RGBA", (W, H), GLOW + (255,)), (0, 0), glow_a)
canvas = Image.alpha_composite(canvas, full)

png = os.path.join(OUT, "Resondi-Device-Podium.png")
canvas.save(png)
canvas.convert("RGB").save(png[:-4] + ".jpg", quality=93)
print("wrote", png)
