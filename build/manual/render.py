"""Render manual.html to final/19-Resondi-User-Guide.pdf (A5, page numbers in the footer)."""
import os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "final", "19-Resondi-User-Guide.pdf")
FOOT = ("<div style='width:100%;font-family:Arial;font-size:7px;color:#9E8892;padding:0 14mm;"
        "display:flex;justify-content:space-between'><span>Resondi User Guide</span>"
        "<span class='pageNumber'></span></div>")

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.goto("file:///" + os.path.join(HERE, "manual.html").replace("\\", "/"))
    pg.wait_for_load_state("networkidle")
    pg.pdf(path=OUT, format="A5", print_background=True, display_header_footer=True,
           header_template="<div></div>", footer_template=FOOT,
           margin={"top": "16mm", "bottom": "18mm", "left": "14mm", "right": "14mm"})
    b.close()
print("wrote", os.path.abspath(OUT))
