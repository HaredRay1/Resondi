"""Proposed subscription tiers. Entry tier is the existing ₱1,500; the ladder goes up.

Everything above Essential is a capability the ₱38,000 mobile-application line in
Table 15 already funds, so the ladder and the funding ask tell the same story.
"""
import pathlib
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(__file__).parent
BG, INK, ROSE, DEEP = "#FFF5F9", "#2A1A22", "#E91E76", "#8E2A52"
MUTED, PALE, LINE = "#9E8892", "#F7D6E4", "#EBD3DE"
P = "&#8369;"
FONT = ("<style>@import url('https://fonts.googleapis.com/css2?"
        "family=Poppins:wght@400;600;700&display=swap');</style>")

TIERS = [
    ("Essential", "1,500", "per facility, per month",
     "One facility, one device. Everything the prototype does today.",
     [f"{P}350 cloud &middot; {P}250 service reserve &middot; <b>{P}900 contribution</b>"],
     "AVAILABLE NOW", False),
    ("Clinical", "2,900", "per facility, per month",
     "For a clinic or RHU that follows patients over time rather than one visit.",
     [f"{P}450 cloud &middot; {P}250 service reserve &middot; <b>{P}2,200 contribution</b>"],
     "BUILT BY THE FUNDING ASK", True),
    ("Network", "4,500", "per facility, per month &middot; minimum 3 facilities",
     "For an LGU cluster where a municipal health officer reviews across facilities.",
     [f"{P}600 cloud &middot; {P}250 reserve &middot; {P}350 review ops &middot; <b>{P}3,300 contribution</b>"],
     "BUILT BY THE FUNDING ASK", False),
]

ROWS = [
    ("Guided capture at seven lung sites and five heart points", 1, 1, 1),
    ("Automated quality check before analysis", 1, 1, 1),
    ("AI sound-pattern classification", 1, 1, 1),
    ("Site-tagged storage and visit history", 1, 1, 1),
    ("Offline capture, store-and-forward on MicroSD", 1, 1, 1),
    ("Practitioner confirms, modifies or rejects every result", 1, 1, 1),
    ("Same-site comparison across visits, once built", 1, 1, 1),
    ("Model updates, cloud backup", 1, 1, 1),
    ("Device replacement reserve", 1, 1, 1),
    ("Devices included per facility", "1", "up to 3", "up to 5"),
    ("User accounts per facility", "2", "8", "unlimited in cluster"),
    ("Support response", "1 business day", "same business day", "same day, named contact"),
    ("SPLIT", "", "", ""),
    ("Rehabilitation module, practitioner-released", 0, 1, 1),
    ("Role-based access with audit logging", 0, 1, 1),
    ("Monthly facility report for the health officer", 0, 1, 1),
    ("SPLIT", "", "", ""),
    ("Cross-facility review routing to a remote clinician", 0, 0, 1),
    ("Cluster dashboard across all facilities", 0, 0, 1),
    ("Data export for DOH and LGU reporting", 0, 0, 1),
    ("Quarterly clinical review with the reviewer network", 0, 0, 1),
    ("Annual on-site refresher training", 0, 0, 1),
]


def mark(v):
    if v == 1:
        return '<span class="yes">&#10003;</span>'
    if v == 0:
        return '<span class="no">&mdash;</span>'
    return f'<span class="txt">{v}</span>'


def html():
    cards = ""
    for name, amt, per, blurb, cost, badge, feat in TIERS:
        cards += f"""<div class="card{' feat' if feat else ''}">
          <div class="badge{' b2' if 'FUNDING' in badge else ''}">{badge}</div>
          <div class="tname">{name}</div>
          <div class="amt">{P}{amt}</div><div class="per">{per}</div>
          <div class="blurb">{blurb}</div>
          <div class="cost">{cost[0]}</div></div>"""
    trs = ""
    for r in ROWS:
        if r[0] == "SPLIT":
            trs += '<tr class="split"><td colspan="4"></td></tr>'
            continue
        label, a, b, c = r
        trs += (f"<tr><td class='lab'>{label}</td><td>{mark(a)}</td>"
                f"<td>{mark(b)}</td><td>{mark(c)}</td></tr>")
    return f"""<!doctype html><meta charset="utf-8">{FONT}<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:{BG};font-family:'Poppins',sans-serif;color:{INK}}}
.wrap{{width:1920px;padding:48px 52px 44px}}
h1{{font-size:44px;font-weight:700;margin-bottom:6px}}
.sub{{font-size:22px;color:{MUTED};margin-bottom:32px}}
.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-bottom:34px}}
.card{{background:#fff;border:2px solid {LINE};border-radius:20px;padding:22px 28px 22px;
      display:flex;flex-direction:column}}
.card.feat{{border:3px solid {ROSE}}}
.badge{{display:inline-block;align-self:flex-start;font-size:14px;font-weight:700;
       letter-spacing:.12em;padding:5px 11px;border-radius:7px;margin-bottom:12px;
       background:{PALE};color:{DEEP}}}
.badge.b2{{background:{ROSE};color:#fff}}
.tname{{font-size:23px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
       color:{DEEP};margin-bottom:6px}}
.amt{{font-size:56px;font-weight:700;color:{ROSE};line-height:1}}
.per{{font-size:19px;color:{MUTED};margin:5px 0 14px}}
.blurb{{font-size:20px;line-height:1.35;margin-bottom:14px}}
.cost{{margin-top:auto;padding-top:12px;border-top:2px solid {LINE};
      font-size:18px;color:{MUTED}}}
.cost b{{color:{DEEP}}}
table{{width:100%;border-collapse:collapse;background:#fff;border:2px solid {LINE};
      border-radius:16px;overflow:hidden}}
th{{font-size:19px;font-weight:700;padding:14px 16px;background:{PALE};color:{DEEP};
   text-align:center;width:180px}}
th.first{{text-align:left;width:auto}}
td{{font-size:20px;padding:11px 16px;border-top:1px solid {LINE};text-align:center}}
td.lab{{text-align:left}}
tr.split td{{padding:0;height:10px;background:{BG};border:none}}
.yes{{color:{ROSE};font-size:26px;font-weight:700}}
.no{{color:#D9C6CE;font-size:24px}}
.txt{{font-size:18px;color:{INK}}}
.foot{{margin-top:26px;font-size:20px;line-height:1.5}}
.foot b{{color:{DEEP}}}
</style><div class="wrap">
<h1>Subscription tiers</h1>
<div class="sub">Per health facility. {P}1,500 stays the entry price, so nothing in the financial
model is re-cut &mdash; the ladder only adds above it. Schools keep the separate
{P}30,000 annual teaching licence.</div>
<div class="cards">{cards}</div>
<table>
<tr><th class="first">What each tier includes</th><th>Essential</th><th>Clinical</th><th>Network</th></tr>
{trs}</table>
<div class="foot">Everything below the first divider, and Essential&rsquo;s visit comparison, is
<b>funded by the {P}38,000 mobile-application line</b> in Table 15: the practitioner dashboard ({P}9,000), role-based access and audit logging
({P}8,000), offline synchronisation ({P}7,000) and longitudinal comparison views ({P}7,000).
The ladder and the funding ask describe the same build.</div>
</div>"""


with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1920, "height": 1000}, device_scale_factor=2)
    (OUT / "Resondi-Subscription-Tiers.html").write_text(html(), encoding="utf-8")
    pg.goto((OUT / "Resondi-Subscription-Tiers.html").as_uri())
    pg.wait_for_timeout(1200)
    el = pg.query_selector(".wrap")
    el.screenshot(path=str(OUT / "Resondi-Subscription-Tiers.png"))
    bb = el.bounding_box()
    print(f"Resondi-Subscription-Tiers.png  {bb['width']:.0f} x {bb['height']:.0f} css px")
    br.close()
