"""Concept-note Figures 8, 11 and 12 in the pitch-deck style.

Same tokens as slides/theme.py (Poppins, app background, app pink), rendered
from HTML with Playwright like the slides. Each figure is laid out at the CSS
width that maps to its print width, so type sizes survive placement:
  Figures 11, 12: 1600 CSS px -> 6.0 in   (1 px = 0.27 pt; 28 px = 7.6 pt)
  Figure 8      : 2400 CSS px -> 9.0 in   (landscape page; 25 px = 6.8 pt)
"""
import sys, pathlib, html
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "finpack"))
from model import ROWS as _ALL_ROWS, Y1, Y2, CUM24, X500, OFFSET
# The model now runs to month 36 for the Year 3 projection, but this figure answers
# "when is the seed recovered" and its caption and stat row are two-year. Clip to 24.
ROWS = _ALL_ROWS[:24]
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(__file__).parent
BG, INK, ROSE, DEEP = "#FFF5F9", "#2A1A22", "#E91E76", "#8E2A52"
MUTED, PALE, LINE = "#9E8892", "#F7D6E4", "#EBD3DE"
P = "&#8369;"

BASE = f"""<!doctype html><meta charset="utf-8"><style>
* {{ margin:0; padding:0; box-sizing:border-box }}
body {{ font-family:'Poppins',sans-serif; background:{BG}; color:{INK};
       -webkit-font-smoothing:antialiased }}
.fig {{ padding:56px 64px 44px; background:{BG} }}
.eyebrow {{ font-size:24px; font-weight:600; letter-spacing:.2em; text-transform:uppercase;
           color:{MUTED} }}
.head {{ font-size:50px; font-weight:700; line-height:1.15; margin:10px 0 34px;
        letter-spacing:-.01em }}
.head em {{ font-style:normal; color:{ROSE} }}
.stats {{ display:flex; gap:64px; border-top:2px solid {LINE}; padding-top:26px; margin-top:26px }}
.stat .k {{ font-size:20px; font-weight:600; letter-spacing:.16em; text-transform:uppercase;
           color:{MUTED} }}
.stat .v {{ font-size:44px; font-weight:700; color:{DEEP}; margin-top:2px }}
.stat .v.hot {{ color:{ROSE} }}
.foot {{ display:flex; justify-content:space-between; align-items:flex-end; margin-top:22px;
        font-size:20px; color:{MUTED}; line-height:1.45 }}
.mark {{ font-size:20px; font-weight:600; letter-spacing:.16em; color:{PALE}; white-space:nowrap;
        padding-left:40px }}
svg text {{ font-family:'Poppins',sans-serif }}
</style>"""

def money(v): return f"{P}{v:,}"

# ── Figure 12: recovery ──────────────────────────────────────────────────
def fig12():
    W, H = 1472, 540                     # svg box inside the 1600 px figure
    X0, X1, Y0, YT = 118, 1340, 500, 20
    TOP = 650_000
    px = lambda m: X0 + (m - 1) * (X1 - X0) / 23
    py = lambda v: Y0 - v / TOP * (Y0 - YT)
    pts = [(px(r["m"]), py(r["cum"])) for r in ROWS]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"{X0},{Y0} {line} {X1},{Y0}"
    g = []
    g.append(f'<rect x="{X0}" y="{YT}" width="{px(12.5)-X0:.1f}" height="{Y0-YT}" fill="{PALE}" opacity=".35"/>')
    for v in range(0, 600_001, 100_000):
        y = py(v)
        g.append(f'<line x1="{X0}" y1="{y:.1f}" x2="{X1}" y2="{y:.1f}" stroke="{LINE}" stroke-width="2"/>')
        lab = f"{P}0" if v == 0 else f"{P}{v//1000}k"
        g.append(f'<text x="{X0-18}" y="{y+8:.1f}" text-anchor="end" font-size="24" fill="{MUTED}">{lab}</text>')
    for m in (1, 6, 12, 18, 24):
        g.append(f'<text x="{px(m):.1f}" y="{Y0+38}" text-anchor="middle" font-size="24" fill="{MUTED}">{m}</text>')
    g.append(f'<text x="{px(6.5):.1f}" y="{Y0-22}" text-anchor="middle" font-size="22" font-weight="600" '
             f'letter-spacing="5" fill="{MUTED}">YEAR 1</text>')
    g.append(f'<text x="{px(16):.1f}" y="{Y0-22}" text-anchor="middle" font-size="22" font-weight="600" '
             f'letter-spacing="5" fill="{MUTED}">YEAR 2</text>')
    g.append(f'<defs><linearGradient id="gr" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{ROSE}" stop-opacity=".28"/>'
             f'<stop offset="1" stop-color="{ROSE}" stop-opacity=".03"/></linearGradient></defs>')
    g.append(f'<polygon points="{area}" fill="url(#gr)"/>')
    ys = py(500_000)
    g.append(f'<line x1="{X0}" y1="{ys:.1f}" x2="{X1}" y2="{ys:.1f}" stroke="{DEEP}" stroke-width="3" stroke-dasharray="14 10"/>')
    g.append(f'<text x="{X0+16}" y="{ys-16:.1f}" font-size="24" font-weight="700" letter-spacing="2" fill="{DEEP}">{P}500,000 SEED</text>')
    g.append(f'<polyline points="{line}" fill="none" stroke="{ROSE}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>')
    r = ROWS[X500 - 1]; cx, cy = px(X500), py(r["cum"])
    g.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx:.1f}" y2="{Y0}" stroke="{DEEP}" stroke-width="2.5" stroke-dasharray="3 7" opacity=".7"/>')
    g.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="13" fill="{DEEP}" stroke="{BG}" stroke-width="5"/>')
    g.append(f'<text x="{cx-24:.1f}" y="{cy-56:.1f}" text-anchor="end" font-size="26" font-weight="700" letter-spacing="2" fill="{DEEP}">MONTH {X500}</text>')
    g.append(f'<text x="{cx-24:.1f}" y="{cy-22:.1f}" text-anchor="end" font-size="25" fill="{MUTED}">{money(r["cum"])} recovered</text>')
    ex, ey = px(24), py(CUM24)
    g.append(f'<text x="{ex+16:.1f}" y="{ey+9:.1f}" font-size="24" font-weight="700" fill="{INK}">{money(CUM24)}</text>')
    g.append(f'<text x="{(X0+X1)/2:.0f}" y="{Y0+78}" text-anchor="middle" font-size="20" font-weight="600" '
             f'letter-spacing="5" fill="{MUTED}">MONTH OF COMMERCIAL OPERATION</text>')
    svg = f'<svg width="{W}" height="{H+52}" viewBox="0 0 {W} {H+52}">{"".join(g)}</svg>'
    return f"""{BASE}<div class="fig" style="width:1600px">
<div class="eyebrow">Return on the requirement</div>
<div class="head">The seed is recovered in <em>commercial month {X500}</em>.</div>
{svg}
<div class="stats">
 <div class="stat"><div class="k">End of Year 1</div><div class="v">{money(Y1)}</div></div>
 <div class="stat"><div class="k">Crosses {P}500,000</div><div class="v hot">Month {X500}</div></div>
 <div class="stat"><div class="k">End of Year 2</div><div class="v">{money(CUM24)}</div></div>
 <div class="stat"><div class="k">From funding</div><div class="v">Month {X500+OFFSET}</div></div>
</div>
<div class="foot"><div>Cumulative cash contribution, not revenue. {P}4,000 device margin on acquisition; {P}900 per facility
per month from the month after installation; school licence {P}25,800 a year, paid in advance.<br>
Commercial month 1 is month 15 from funding.</div><div class="mark">RESONDI</div></div>
</div>"""

# ── Figure 11: allocation ────────────────────────────────────────────────
def fig11():
    rows = [("Clinical validation",120_000,1),("AI development",102_000,1),("Contingency",50_000,0),
            ("Cloud infrastructure and operation",48_000,0),("Hardware refinement",42_000,0),
            ("Production working capital",40_000,0),("Mobile application",38_000,0),
            ("Intellectual property and registration",25_000,0),("Documentation and compliance",20_000,0),
            ("Deployment and marketing",15_000,0)]
    total = sum(r[1] for r in rows); assert total == 500_000
    mx = rows[0][1]
    bars = []
    for name, amt, hot in rows:
        w = amt / mx * 100
        bars.append(f"""<div class="row"><div class="lab">{name}</div>
<div class="track"><div class="bar" style="width:{w:.2f}%;background:{ROSE if hot else DEEP}"></div></div>
<div class="val"><b>{money(amt)}</b><span>{amt/total*100:.1f}%</span></div></div>""")
    drv = sum(r[1] for r in rows if r[2])
    css = f"""<style>
.row {{ display:grid; grid-template-columns:520px 1fr 250px; align-items:center; gap:22px; height:52px }}
.lab {{ font-size:27px; text-align:right; color:{INK} }}
.track {{ height:28px; background:{PALE}; border-radius:14px; overflow:hidden }}
.bar {{ height:100%; border-radius:14px }}
.val b {{ font-size:27px; font-weight:700; color:{INK} }}
.val span {{ font-size:25px; color:{MUTED}; margin-left:14px }}
.key {{ display:flex; gap:40px; margin:6px 0 4px 542px; font-size:22px; color:{MUTED} }}
.key i {{ display:inline-block; width:22px; height:22px; border-radius:11px; vertical-align:-3px; margin-right:10px }}
</style>"""
    return f"""{BASE}{css}<div class="fig" style="width:1600px">
<div class="eyebrow">Financial requirement</div>
<div class="head"><em>44%</em> of the {P}500,000 buys the evidence and the model.</div>
<div class="key"><span><i style="background:{ROSE}"></i>The two commitments that drive the ask</span>
<span><i style="background:{DEEP}"></i>Everything else</span></div>
{''.join(bars)}
<div class="stats">
 <div class="stat"><div class="k">Total requirement</div><div class="v">{P}500,000</div></div>
 <div class="stat"><div class="k">Evidence and model</div><div class="v hot">{money(drv)}</div></div>
 <div class="stat"><div class="k">Contingency held</div><div class="v">{P}50,000</div></div>
 <div class="stat"><div class="k">Categories</div><div class="v">10</div></div>
</div>
<div class="foot"><div>Category totals from Table 9; line items in Table 10. Cash costs only: no salary or stipend is drawn
against the requirement.</div><div class="mark">RESONDI</div></div>
</div>"""

# ── Figure 8: business model canvas (monotone, print-legible) ────────────
# Placed at 940 x 640 px (9.8 x 6.7 in) on a landscape page. Laid out at
# CSS_W px so body text prints near 9.5 pt:  pt = css_px * 940 / CSS_W * 0.75
CSS_W = 1760
CANVAS = {
 "Key Partners": [
  "<b>Clinical:</b> partner hospital, Provincial Health Office, ethics committee, consulting pulmonologists",
  "<b>Academic:</b> PPCNSHS; nursing and medical schools",
  "<b>Industry:</b> distributors, component suppliers, PCB fabricator, contract assembler",
  "<b>Government:</b> LGUs and RHUs as pilot sites; DOH, DOST-PCHRD, DICT"],
 "Key Activities": [
  "<b>First priority:</b> faster quality screening and noise reduction",
  "Patient-wise CNN retraining on clinically labelled Filipino recordings",
  "Assembly, calibration and testing",
  "Clinical validation and FDA registration",
  "School and RHU sales, training, distributor partnerships"],
 "Key Resources": [
  "<b>Defensible:</b> consented, locally labelled recordings that grow with every deployment",
  "ESP32 device, mobile app, cloud platform, trained CNN",
  "Three founders: CEO, CTO and COO",
  "Three pulmonologists and one pediatrician as advisers",
  "<b>IP:</b> ownership formalized with the school before any sale"],
 "Value Propositions": [
  "Every heartbeat and breath becomes a record that can be tracked, compared and reviewed",
  "Guided capture at standardized lung and heart sites",
  "Comparison against the same site at earlier visits",
  "AI suggests; the practitioner confirms, modifies or rejects",
  "Works offline: store-and-forward on MicroSD",
  "<b>&#8369;8,000</b> per device against ~&#8369;22,000 imported",
  "Quality check runs before analysis but takes ~145 s: the first fix funded"],
 "Customer Relationships": [
  "On-site training at deployment",
  "Remote support and device-fault escalation",
  "Practitioner review as the ongoing touchpoint",
  "Model updates through the subscription",
  "User group, in-app feedback, annual forum"],
 "Channels": [
  "LGU and DOH procurement",
  "Direct sale to clinics, hospitals and schools",
  "Distributors from Year 2; donor programmes",
  "Website and online demonstrations",
  "Startup Challenge, health-tech expos, conferences"],
 "Customer Segments": [
  "<b>Year 1:</b> nursing and medical schools; RHUs and municipal health centres",
  "<b>Years 2&#8211;3:</b> private clinics, secondary hospitals, LGU clusters",
  "<b>Funded:</b> NGOs and development agencies",
  "<b>Users:</b> midwives, nurses, rural physicians",
  "<b>Beneficiaries:</b> patients in isolated barangays"],
 "Cost Structure": [
  "<b>&#8369;500,000 seed:</b> clinical validation &#8369;120k &middot; AI &#8369;102k &middot; contingency &#8369;50k &middot; cloud &#8369;48k &middot; hardware &#8369;42k &middot; production &#8369;40k &middot; app &#8369;38k &middot; IP &#8369;25k &middot; documentation &#8369;20k &middot; marketing &#8369;15k",
  "<b>Unit cost:</b> ~&#8369;4,000 fully loaded; ~&#8369;3,000 at 100 units; ~&#8369;2,500 at 500",
  "<b>Working capital:</b> &#8369;40,000 builds the first ten units",
  "<b>Recurring:</b> &#8369;350 per facility per month for cloud, storage and backup"],
 "Revenue Streams": [
  "<b>Device:</b> &#8369;8,000 per unit, ~50% gross margin",
  "<b>Subscription:</b> &#8369;1,500 per facility per month (&#8369;900 contribution)",
  "<b>Licence:</b> &#8369;30,000 per school per year &middot; <b>Donor</b> programme grants",
  "<b>Cash:</b> Year 1 &#8369;175,900 &middot; Year 2 &#8369;426,900; seed recovered in month 21 of sales",
  "<b>Investor:</b> 40% of net earnings until repaid, plus an agreed equity stake"],
}

def fig8():
    K, TX, RULE, HEAD, BUL = "#111111", "#262626", "#9E9E9E", "#E6E6E6", "#6B6B6B"
    def block(name, area):
        lis = "".join(f"<li>{it}</li>" for it in CANVAS[name])
        return (f'<section style="grid-area:{area}"><h3>{name}</h3>'
                f'<ul>{lis}</ul></section>')
    css = f"""<style>
* {{ margin:0; padding:0; box-sizing:border-box }}
body {{ background:#fff }}
.bmc {{ width:{CSS_W}px; padding:6px; background:#fff; color:{TX};
        font-family:'Poppins','Helvetica Neue',Arial,sans-serif }}
.top {{ display:flex; justify-content:space-between; align-items:baseline;
        border-bottom:2.5px solid {K}; padding-bottom:8px; margin-bottom:12px }}
.top .t {{ font-size:27px; font-weight:700; color:{K} }}
.top .s {{ font-size:17px; color:#555 }}
.canvas {{ display:grid; gap:0; grid-template-columns:repeat(10,1fr);
  border:2px solid {K};
  grid-template-areas:
   "kp kp ka ka vp vp cr cr cs cs"
   "kp kp kr kr vp vp ch ch cs cs"
   "co co co co co rv rv rv rv rv"; }}
section {{ border:1.2px solid {RULE}; padding:0 0 6px }}
h3 {{ font-size:21px; font-weight:700; letter-spacing:.05em; text-transform:uppercase;
      color:{K}; background:{HEAD}; padding:6px 12px; border-bottom:1.2px solid {RULE};
      margin-bottom:8px }}
ul {{ list-style:none; padding:0 12px }}
li {{ font-size:22px; line-height:1.27; margin-bottom:5px; padding-left:15px;
      position:relative; color:{TX} }}
li::before {{ content:""; position:absolute; left:0; top:11px; width:6px; height:6px;
      background:{BUL} }}
li b {{ font-weight:700; color:{K} }}
</style>"""
    blocks = "".join([block("Key Partners","kp"), block("Key Activities","ka"),
                      block("Key Resources","kr"), block("Value Propositions","vp"),
                      block("Customer Relationships","cr"), block("Channels","ch"),
                      block("Customer Segments","cs"), block("Cost Structure","co"),
                      block("Revenue Streams","rv")])
    return f"""<!doctype html><meta charset="utf-8">{css}<div class="fig bmc">
<div class="canvas">{blocks}</div></div>"""

pages = {"Figure-11-Allocation-500k": (fig11(), 1600),
         "Figure-12-Cumulative-Recovery": (fig12(), 1600),
         "Figure-08-Business-Model-Canvas": (fig8(), CSS_W)}
# Optional argument: render only the figures whose names contain it (e.g. "Canvas").
ONLY = sys.argv[1] if len(sys.argv) > 1 else ""
FIGDIR = OUT.parent.parent / "figures"
# Poppins is loaded from Google Fonts so the render does not depend on a local install.
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Poppins:wght@400;600;700&display=block">')
with sync_playwright() as pw:
    try:
        br = pw.chromium.launch()
    except Exception:
        br = pw.chromium.launch(channel="msedge")   # Windows: use the installed Edge
    for name, (doc, w) in pages.items():
        if ONLY not in name:
            continue
        doc = doc.replace('<meta charset="utf-8">', '<meta charset="utf-8">' + FONTS, 1)
        (OUT / f"{name}.html").write_text(doc, encoding="utf-8")
        pg = br.new_page(viewport={"width": w, "height": 800}, device_scale_factor=3 if 'Canvas' in name else 2)
        pg.goto((OUT / f"{name}.html").as_uri()); pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(500)
        assert pg.evaluate("document.fonts.check('700 22px Poppins')"), "Poppins did not load"
        el = pg.query_selector(".fig")
        el.screenshot(path=str(FIGDIR / f"{name}.png"))
        bb = el.bounding_box()
        print(f"{name}: {bb['width']:.0f} x {bb['height']:.0f} css px  "
              f"(aspect {bb['height']/bb['width']:.3f})")
        pg.close()
    br.close()
