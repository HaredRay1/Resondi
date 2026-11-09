"""Render each slide HTML to a 3840x2160 PNG (1920x1080 at 2x)."""
import pathlib
import sys
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
names = sys.argv[1:] or sorted(p.stem for p in HERE.glob("slide*.html"))

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1920, "height": 1080},
                     device_scale_factor=2)
    for n in names:
        src = HERE / f"{n}.html"
        pg.goto(src.as_uri())
        pg.wait_for_timeout(450)          # let Poppins settle
        out = HERE / f"{n}.png"
        pg.screenshot(path=str(out))
        print(f"{out.name}  {out.stat().st_size // 1024} KB")
    br.close()
