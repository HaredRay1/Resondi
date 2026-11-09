"""Bundles and onboarding offers.

One discipline governs every discount: nothing comes out of the P600 per facility
per month that pays cloud operation and the replacement reserve. On Essential,
where contribution is exactly the P900 the projections assume, the discount comes
out of device margin alone.
"""
import pathlib
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(__file__).parent
BG, INK, ROSE, DEEP = "#FFF5F9", "#2A1A22", "#E91E76", "#8E2A52"
MUTED, PALE, LINE = "#9E8892", "#F7D6E4", "#EBD3DE"
P = "&#8369;"
FONT = ("<style>@import url('https://fonts.googleapis.com/css2?"
        "family=Poppins:wght@400;600;700&display=swap');</style>")

# name, tier, contents, list price, bundle price, save, discount source, contribution
BUNDLES = [
    ("Starter", "ESSENTIAL", "1 device<br>Essential, 12 months prepaid",
     "26,000", "24,500", "1,500",
     f"{P}1,500 off the device.<br>Subscription charged in full.",
     f"<b>{P}900</b> per month retained<br>Device margin {P}2,500 (38%)", False),
    ("Clinic", "CLINICAL", "3 devices<br>Clinical, 12 months prepaid",
     "58,800", "52,000", "6,800",
     f"{P}3,000 off the devices,<br>{P}3,800 off the subscription.",
     f"<b>{P}1,883</b> per month retained<br>Floor cleared twice over", True),
    ("Cluster", "NETWORK", "3 facilities, 1 device each<br>Network, 12 months prepaid",
     "186,000", "168,000", "18,000",
     f"{P}4,500 off the devices,<br>{P}13,500 off the subscription.",
     f"<b>{P}2,925</b> per facility per month<br>Cluster entity required", False),
    ("Teaching", "SCHOOLS", "Institutional licence<br>2 devices, 12 months",
     "46,000", "42,000", "4,000",
     f"{P}4,000 off the devices.<br>Licence charged in full.",
     f"Licence intact at <b>{P}30,000</b><br>Separate from the tier ladder", False),
]

OFFERS = [
    ("Limited trial", "New facility, full Essential capability",
     "Fourteen days or twenty-five guided examinations, whichever comes first, with no payment "
     f"details taken. <b>About {P}750 per facility.</b> A free month would cost {P}1,500: the "
     f"{P}900 of contribution plus the {P}600 of cloud and reserve still consumed."),
    ("Feature trial", "Sixty days of Clinical features while paying Essential",
     f"Costs the {P}100 monthly difference in cloud allowance, twice. "
     f"<b>{P}200 per facility, once.</b> Gives away capability, not revenue. It cannot be "
     f"offered until the {P}38,000 mobile-application line has built those features."),
]


def html():
    cards = ""
    for name, tier, contents, lst, price, save, src, contrib, feat in BUNDLES:
        cards += f"""<div class="card{' feat' if feat else ''}">
          <div class="badge">{tier}</div>
          <div class="tname">{name}</div>
          <div class="contents">{contents}</div>
          <div class="prices">
            <span class="was">{P}{lst}</span>
            <span class="now">{P}{price}</span>
          </div>
          <div class="save">Saves {P}{save}</div>
          <div class="src">{src}</div>
          <div class="contrib">{contrib}</div></div>"""
    offers = ""
    for title, who, body in OFFERS:
        offers += f"""<div class="offer">
          <div class="otitle">{title}</div>
          <div class="owho">{who}</div>
          <div class="obody">{body}</div></div>"""
    return f"""<!doctype html><meta charset="utf-8">{FONT}<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:{BG};font-family:'Poppins',sans-serif;color:{INK}}}
.wrap{{width:1920px;padding:48px 52px 44px}}
h1{{font-size:44px;font-weight:700;margin-bottom:6px}}
.sub{{font-size:22px;color:{MUTED};margin-bottom:30px;max-width:1500px;line-height:1.4}}
.sub b{{color:{DEEP}}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:22px;margin-bottom:34px}}
.card{{background:#fff;border:2px solid {LINE};border-radius:20px;padding:22px 26px;
      display:flex;flex-direction:column}}
.card.feat{{border:3px solid {ROSE}}}
.badge{{display:inline-block;align-self:flex-start;font-size:13px;font-weight:700;
       letter-spacing:.12em;padding:5px 11px;border-radius:7px;margin-bottom:12px;
       background:{PALE};color:{DEEP}}}
.tname{{font-size:30px;font-weight:700;color:{DEEP};margin-bottom:10px}}
.contents{{font-size:19px;line-height:1.4;margin-bottom:16px}}
.prices{{display:flex;align-items:baseline;gap:14px}}
.was{{font-size:24px;color:{MUTED};text-decoration:line-through}}
.now{{font-size:44px;font-weight:700;color:{ROSE};line-height:1}}
.save{{font-size:18px;font-weight:600;color:{DEEP};margin:6px 0 14px}}
.src{{font-size:18px;line-height:1.4;color:{MUTED};padding-top:12px;
     border-top:2px solid {LINE}}}
.contrib{{margin-top:auto;padding-top:12px;font-size:18px;line-height:1.4}}
.contrib b{{color:{DEEP}}}
.offers{{display:grid;grid-template-columns:repeat(2,1fr);gap:22px}}
.offer{{background:#fff;border:2px solid {LINE};border-left:10px solid {ROSE};
       border-radius:16px;padding:22px 28px}}
.otitle{{font-size:28px;font-weight:700;color:{DEEP}}}
.owho{{font-size:18px;color:{MUTED};margin:2px 0 12px}}
.obody{{font-size:20px;line-height:1.45}}
.obody b{{color:{DEEP}}}
.foot{{margin-top:28px;font-size:20px;line-height:1.5}}
.foot b{{color:{DEEP}}}
</style><div class="wrap">
<h1>Bundles and onboarding offers</h1>
<div class="sub">A facility buying a device and a subscription in the same procurement is making
one decision, not two, and an LGU budget line is easier to defend as a single annual figure.
<b>One rule governs every discount: nothing comes out of what pays cloud operation and the
device replacement reserve: {P}600 a month on Essential, {P}700 on Clinical, {P}1,200 on Network.</b></div>
<div class="cards">{cards}</div>
<div class="offers">{offers}</div>
<div class="foot"><b>Offers do not stack, and no trial turns into a charge:</b> when one ends, the facility
chooses a tier. Every price here is a
<b>proposal, not a validated price</b> &mdash; no buyer has yet agreed to {P}2,900, and
willingness to pay is one of the questions the pre-launch budget-holder interviews exist to
answer.</div>
</div>"""


with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1920, "height": 1000}, device_scale_factor=2)
    f = OUT / "Resondi-Bundles-And-Offers.html"
    f.write_text(html(), encoding="utf-8")
    pg.goto(f.as_uri()); pg.wait_for_timeout(1400)
    el = pg.query_selector(".wrap")
    el.screenshot(path=str(OUT / "Resondi-Bundles-And-Offers.png"))
    bb = el.bounding_box()
    print(f"Resondi-Bundles-And-Offers.png  {bb['width']:.0f} x {bb['height']:.0f} css px")
    br.close()
