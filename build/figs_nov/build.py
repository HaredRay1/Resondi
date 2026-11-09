"""Two standalone figures: the named device comparison and the pricing structure.

Rendered from HTML with Playwright at 2x, like the deck figures.
  - Device comparison is a TABLE -> monotone, per the standing instruction.
  - Pricing structure is a DIAGRAM -> Resondi rose.
"""
import pathlib
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(__file__).parent
BG, INK, ROSE, DEEP = "#FFF5F9", "#2A1A22", "#E91E76", "#8E2A52"
MUTED, PALE, LINE = "#9E8892", "#F7D6E4", "#EBD3DE"
P = "&#8369;"

FONT = ("<style>@import url('https://fonts.googleapis.com/css2?"
        "family=Poppins:wght@400;600;700&display=swap');</style>")

# ─────────────────────────────────────────────── 1. DEVICE COMPARISON
ROWS = [
    ("Resondi", f"{P}8,000 + {P}1,500/mo",
     "Yes &mdash; four lung sound patterns",
     "Yes &mdash; seven lung sites", "Yes &mdash; by site",
     "Yes &mdash; MicroSD", "Designed for it", True),
    ("Eko CORE 500", "USD 449", "No &mdash; cardiac only", "Cardiac only, paid tier",
     "Not documented", "No", "Hardware only; AI not sold in PH", False),
    ("Eko CORE 300<span class='n'>released 22 Oct 2026</span>", "USD 199&ndash;249",
     "No &mdash; murmur only", "No", "Not documented",
     "Acoustic mode only", "US at launch; AI not sold in PH", False),
    ("3M Littmann CORE", "USD 379", "No &mdash; murmur only", "Cardiac only, paid tier",
     "Not documented", "No", "Hardware only; AI not sold in PH", False),
    ("Thinklabs One", "USD 499", "None", "Position tagging only", "Not documented",
     "Yes &mdash; no storage", "Import only", False),
    ("HD Medical HD Steth", "USD 499 <span class='n'>2021 price</span>",
     "Claimed; clearance says not for diagnosis", "No", "Not documented",
     "Not documented", "Not found", False),
    ("StethoMe", "Not published", "Yes &mdash; wheeze, home use", "No", "Not documented",
     "Not documented", "CE marked, Europe", False),
    ("E-Steth <span class='n'>UP &middot; DOST-PCHRD</span>", "Not sold", "None", "No", "No",
     "Yes", "Philippine, not purchasable", False),
    ("Acoustic stethoscope", f"{P}500 &ndash; {P}3,000", "None", "No", "No", "Yes",
     "Universal", False),
]
HEAD = ["Device", "List price", "AI on lung sounds", "Guided placement",
        "Same-site comparison", "Works offline", "Available in the Philippines"]


def device_html():
    th = "".join(f"<th>{h}</th>" for h in HEAD)
    tr = ""
    for name, price, ai, guide, longi, off, ph, ours in ROWS:
        cls = ' class="ours"' if ours else ""
        tr += (f"<tr{cls}><td class='dev'>{name}</td><td>{price}</td><td>{ai}</td>"
               f"<td>{guide}</td><td>{longi}</td><td>{off}</td><td>{ph}</td></tr>")
    return f"""<!doctype html><meta charset="utf-8">{FONT}<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#fff;font-family:'Poppins',sans-serif;color:#262626}}
.wrap{{width:1920px;padding:44px 48px 40px;background:#fff}}
h1{{font-size:40px;font-weight:700;color:#111;margin-bottom:6px}}
.sub{{font-size:21px;color:#555;margin-bottom:26px}}
table{{border-collapse:collapse;width:100%;border:2.5px solid #111}}
th{{background:#E8E8E8;font-size:20px;font-weight:700;text-align:left;
   padding:14px 14px;border:1.2px solid #9E9E9E;color:#111}}
td{{font-size:20px;padding:13px 14px;border:1.2px solid #BDBDBD;vertical-align:top;
   line-height:1.3}}
td.dev{{font-weight:600;color:#111}}
tr.ours td{{background:#F2F2F2;font-weight:600}}
tr.ours td.dev{{border-left:6px solid #111}}
.n{{display:block;font-size:16px;color:#6B6B6B;font-weight:400;margin-top:3px}}
.note{{margin-top:18px;font-size:17px;color:#555;line-height:1.5}}
</style><div class="wrap">
<h1>Device Feature Comparison</h1>
<div class="sub">Resondi against the named alternatives &middot; list prices as published October 2026,
excluding shipping, duties and local margin</div>
{f'<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'}
<div class="note"><b>Not documented</b> means no vendor publishes the feature, not that it cannot exist.
No device reviewed documents comparison against an earlier recording from the same anatomical site.
Eko&rsquo;s analysis is delivered through the Eko+ subscription, which is sold in the United States,
Canada, twenty European countries, Australia and New Zealand &mdash; not in the Philippines or anywhere in ASEAN.
DOST-PCHRD reports electronic stethoscopes in the Philippines cost at least {P}30,000 to {P}40,000.</div>
</div>"""


# ─────────────────────────────────────────────── 2. PRICING STRUCTURE
def pricing_html():
    return f"""<!doctype html><meta charset="utf-8">{FONT}<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:{BG};font-family:'Poppins',sans-serif;color:{INK}}}
.wrap{{width:1920px;padding:48px 52px 44px}}
h1{{font-size:44px;font-weight:700;margin-bottom:6px}}
.sub{{font-size:22px;color:{MUTED};margin-bottom:34px}}
.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:26px}}
.card{{background:#fff;border:2px solid {LINE};border-radius:20px;padding:28px 30px 24px;
      display:flex;flex-direction:column}}
.who{{font-size:19px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
     color:{DEEP};margin-bottom:14px}}
.amt{{font-size:58px;font-weight:700;color:{ROSE};line-height:1}}
.per{{font-size:21px;color:{MUTED};margin:6px 0 18px}}
ul{{list-style:none;margin-top:auto}}
li{{font-size:20px;line-height:1.35;margin-bottom:9px;padding-left:20px;position:relative}}
li::before{{content:"";position:absolute;left:0;top:10px;width:8px;height:8px;
           border-radius:4px;background:{ROSE}}}
.net{{margin-top:16px;padding-top:14px;border-top:2px solid {LINE};
     font-size:20px;font-weight:600;color:{DEEP}}}
.split{{margin-top:30px;background:#fff;border:2px solid {LINE};border-radius:20px;
       padding:26px 30px}}
.split h2{{font-size:24px;font-weight:700;margin-bottom:6px}}
.split .lead{{font-size:19px;color:{MUTED};margin-bottom:18px}}
.bar{{display:flex;height:74px;border-radius:12px;overflow:hidden;margin-bottom:12px}}
.seg{{display:flex;flex-direction:column;justify-content:center;padding:0 20px;color:#fff}}
.seg b{{font-size:25px;font-weight:700;line-height:1.1}}
.seg span{{font-size:16px;opacity:.93;line-height:1.2}}
.foot{{margin-top:26px;font-size:20px;color:{INK};line-height:1.5}}
.foot b{{color:{DEEP}}}
</style><div class="wrap">
<h1>What a buyer pays</h1>
<div class="sub">One price per buyer type. Every figure derives from the {P}500,000 financial requirement.</div>

<div class="cards">
  <div class="card">
    <div class="who">Rural health unit or clinic</div>
    <div class="amt">{P}8,000</div><div class="per">per device, one time</div>
    <ul>
      <li>Smart stethoscope, calibrated and tested</li>
      <li>On-site training at deployment</li>
      <li>Fully loaded unit cost &asymp; {P}4,000</li>
    </ul>
    <div class="net">{P}4,000 margin on the first unit</div>
  </div>
  <div class="card">
    <div class="who">Platform, per facility</div>
    <div class="amt">{P}1,500</div><div class="per">per facility, per month</div>
    <ul>
      <li>Cloud storage, backup and sync</li>
      <li>Model updates and remote support</li>
      <li>Device replacement reserve</li>
    </ul>
    <div class="net">{P}900 contribution &middot; {P}14,800 per facility in year one</div>
  </div>
  <div class="card">
    <div class="who">Nursing or medical school</div>
    <div class="amt">{P}30,000</div><div class="per">per school, per year</div>
    <ul>
      <li>Institutional licence for classroom use</li>
      <li>Opens first &mdash; lighter regulatory burden</li>
      <li>Hardware billed separately at {P}8,000</li>
    </ul>
    <div class="net">{P}25,800 after {P}4,200 of platform cost</div>
  </div>
</div>

<div class="split">
  <h2>Where the {P}1,500 subscription goes</h2>
  <div class="lead">Each facility, each month</div>
  <div class="bar">
    <div class="seg" style="background:{MUTED};flex:350"><b>{P}350</b><span>Cloud, storage<br>and backup</span></div>
    <div class="seg" style="background:{DEEP};flex:250"><b>{P}250</b><span>Service &amp;<br>replacement reserve</span></div>
    <div class="seg" style="background:{ROSE};flex:900"><b>{P}900</b><span>Contribution</span></div>
  </div>
</div>

<div class="foot">A fourth stream is <b>donor-funded deployment</b>: a per-programme grant covering devices,
training and first-year access, used where neither an LGU nor a school holds the budget.
The {P}900 contribution is a floor rather than a ceiling &mdash; the fixed part of hosting is spread
across the fewest facilities during the pilot, so the per-facility cost falls as the installed base grows.</div>
</div>"""


pages = {"Resondi-Device-Comparison": device_html(),
         "Resondi-Pricing-Structure": pricing_html()}

with sync_playwright() as pw:
    br = pw.chromium.launch()
    for name, doc in pages.items():
        (OUT / f"{name}.html").write_text(doc, encoding="utf-8")
        pg = br.new_page(viewport={"width": 1920, "height": 900}, device_scale_factor=2)
        pg.goto((OUT / f"{name}.html").as_uri())
        pg.wait_for_timeout(1200)
        el = pg.query_selector(".wrap")
        el.screenshot(path=str(OUT / f"{name}.png"))
        bb = el.bounding_box()
        print(f"{name}.png  {bb['width']:.0f} x {bb['height']:.0f} css px")
        pg.close()
    br.close()
