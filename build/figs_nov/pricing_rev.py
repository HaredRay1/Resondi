"""Revised pricing structure: what a buyer pays, and what a unit costs to build.

The cost column is the part that changed. It now traces to the 30 Oct bill of
materials (₱2,735) instead of stopping at an unexplained ₱3,400 component line.
"""
import pathlib
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(__file__).parent
BG, INK, ROSE, DEEP = "#FFF5F9", "#2A1A22", "#E91E76", "#8E2A52"
MUTED, PALE, LINE = "#9E8892", "#F7D6E4", "#EBD3DE"
P = "&#8369;"
FONT = ("<style>@import url('https://fonts.googleapis.com/css2?"
        "family=Poppins:wght@400;600;700&display=swap');</style>")

BUILD = [
    ("Bill of materials, one unit \u2014 confirmed", "2,735", "ESP32, MEMS microphone, OLED, MicroSD and card, "
     "battery, PCB, PLA enclosure, chest piece, switches and fixings", False, "bom"),
    ("Battery protection, charging, and production allowance", "665",
     "Excluded from the bill of materials by its own note, plus the connectors, strain relief, "
     "enclosure finish and spares a saleable unit needs beyond a prototype", False, "add"),
    ("Components, production unit", "3,400", "Once the design is frozen", True, "sub"),
    ("Assembly, calibration, functional test, packaging", "600", "", False, "add"),
    ("Fully loaded unit cost", "4,000", "What the ₱8,000 price is set against", True, "tot"),
]
VOL = [("1 unit", "4,000"), ("100 units", "3,000"), ("500 units", "2,500")]


def html():
    rows = ""
    for label, amt, note, bold, kind in BUILD:
        cls = {"sub": "sub", "tot": "tot", "bom": "bom", "add": ""}[kind]
        sign = "" if kind in ("bom", "sub", "tot") else '<span class="plus">+</span>'
        rows += (f'<tr class="{cls}"><td class="lab">{sign}{label}'
                 f'{f"<span class=n>{note}</span>" if note else ""}</td>'
                 f'<td class="amt">{P}{amt}</td></tr>')
    vols = "".join(f'<div class="v"><b>{P}{a}</b><span>{q}</span></div>' for q, a in VOL)
    return f"""<!doctype html><meta charset="utf-8">{FONT}<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:{BG};font-family:'Poppins',sans-serif;color:{INK}}}
.wrap{{width:1920px;padding:50px 56px 44px}}
h1{{font-size:46px;font-weight:700;margin-bottom:8px}}
.sub0{{font-size:22px;color:{MUTED};margin-bottom:34px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:30px}}
.panel{{background:#fff;border:2px solid {LINE};border-radius:22px;padding:30px 34px 26px}}
h2{{font-size:27px;font-weight:700;margin-bottom:4px}}
.lead{{font-size:19px;color:{MUTED};margin-bottom:20px}}
table{{width:100%;border-collapse:collapse}}
td{{padding:11px 0;font-size:21px;vertical-align:top}}
td.amt{{text-align:right;font-weight:600;white-space:nowrap;padding-left:18px}}
.n{{display:block;font-size:17px;color:{MUTED};line-height:1.3;margin-top:3px}}
tr.bom td{{border-top:none}}
tr.sub td{{border-top:2px solid {LINE};font-weight:700;color:{DEEP};padding-top:14px}}
tr.tot td{{border-top:3px solid {DEEP};font-weight:700;color:{ROSE};font-size:26px;padding-top:16px}}
.plus{{color:{MUTED};margin-right:8px}}
.price{{display:flex;gap:26px;margin-bottom:22px}}
.pc{{flex:1;background:{BG};border-radius:16px;padding:18px 20px}}
.pc b{{display:block;font-size:40px;font-weight:700;color:{ROSE};line-height:1.05}}
.pc span{{font-size:18px;color:{MUTED}}}
.vols{{display:flex;gap:16px;margin-top:20px}}
.v{{flex:1;background:{BG};border-radius:14px;padding:14px 16px;text-align:center}}
.v b{{display:block;font-size:28px;font-weight:700;color:{DEEP}}}
.v span{{font-size:17px;color:{MUTED}}}
.foot{{margin-top:28px;font-size:20px;line-height:1.5}}
.foot b{{color:{DEEP}}}
.flag{{margin-top:14px;padding:16px 20px;background:#fff;border-left:6px solid {ROSE};
      border-radius:10px;font-size:19px;line-height:1.45}}
</style><div class="wrap">
<h1>Price and unit cost</h1>
<div class="sub0">The cost build-up now traces to the 30 October bill of materials.
Prices and margins are unchanged.</div>

<div class="grid">
  <div class="panel">
    <h2>What a buyer pays</h2>
    <div class="lead">Per health facility</div>
    <div class="price">
      <div class="pc"><b>{P}8,000</b><span>per device, one time</span></div>
      <div class="pc"><b>{P}1,500</b><span>per facility, per month</span></div>
    </div>
    <table>
      <tr><td class="lab">Device margin on the first unit<span class="n">{P}8,000 price less {P}4,000 fully loaded cost</span></td><td class="amt">{P}4,000</td></tr>
      <tr><td class="lab">Monthly contribution<span class="n">{P}1,500 less {P}350 cloud and {P}250 service reserve</span></td><td class="amt">{P}900</td></tr>
      <tr class="sub"><td class="lab">First-year value of one facility</td><td class="amt">{P}14,800</td></tr>
    </table>
    <div class="vols">{vols}</div>
    <div class="lead" style="margin:12px 0 0;text-align:center">Fully loaded cost at volume</div>
  </div>

  <div class="panel">
    <h2>What a unit costs to build</h2>
    <div class="lead">Production unit, once the design is frozen</div>
    <table>{rows}</table>
  </div>
</div>

<div class="flag"><b>Why the bridge line exists.</b> {P}2,735 is the confirmed cost of the parts in the prototype. The bill of materials states that the battery protection and charging circuit are not included in that total, and a unit built to sell also needs connectors, strain relief, a finished enclosure and a spares allowance. Those sit in the {P}665 line. Confirm the battery protection and charging portion: if it is materially above {P}300, the {P}4,000 fully loaded figure needs revisiting before the {P}8,000 price does.</div>

<div class="foot">Schools pay a separate <b>{P}30,000 annual teaching licence</b>, {P}25,800 after
platform cost. The device is profitable from the first production unit, so the subscription is a
second margin stream rather than cover for a hardware loss.</div>
</div>"""


with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1920, "height": 1100}, device_scale_factor=2)
    (OUT / "Resondi-Price-And-Unit-Cost.html").write_text(html(), encoding="utf-8")
    pg.goto((OUT / "Resondi-Price-And-Unit-Cost.html").as_uri())
    pg.wait_for_timeout(1200)
    el = pg.query_selector(".wrap")
    el.screenshot(path=str(OUT / "Resondi-Price-And-Unit-Cost.png"))
    bb = el.bounding_box()
    print(f"{bb['width']:.0f} x {bb['height']:.0f} css px")
    br.close()
