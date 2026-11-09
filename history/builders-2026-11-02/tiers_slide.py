"""Compact 16:9 subscription-tier figure, for a slide or a concept-note figure.

The tall version (Resondi-Subscription-Tiers.png) carries the full feature matrix;
this one carries only what separates the tiers.
"""
import pathlib
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(__file__).parent
BG, INK, ROSE, DEEP = "#FFF5F9", "#2A1A22", "#E91E76", "#8E2A52"
MUTED, PALE, LINE = "#9E8892", "#F7D6E4", "#EBD3DE"
P = "&#8369;"
FONT = ("<style>@import url('https://fonts.googleapis.com/css2?"
        "family=Poppins:wght@400;600;700&display=swap');</style>")

CARDS = [
    ("Essential", "1,500", "per facility, per month",
     "AVAILABLE NOW", False,
     ["Guided capture at seven lung sites",
      "Quality check before analysis",
      "AI sound-pattern classification",
      "Practitioner review on every result",
      "<b>Same-site comparison</b> across visits, once built",
      "Offline capture; cloud backup once built"],
     "1 device &middot; 2 users", f"{P}900 contribution"),
    ("Clinical", "2,900", "per facility, per month",
     "BUILT BY THE ASK", True,
     ["Everything in Essential, plus:",
      "<b>Rehabilitation module</b>, practitioner-released",
      "<b>Role-based access</b> with audit log",
      "<b>Monthly report</b> for the health officer"],
     "3 devices &middot; 8 users", f"{P}2,200 contribution"),
    ("Network", "4,500", "per facility &middot; minimum 3",
     "BUILT BY THE ASK", False,
     ["Everything in Clinical, plus:",
      "<b>Cross-facility routing</b> to a remote clinician",
      "<b>Cluster dashboard</b> for the health officer",
      "<b>Data export</b> for DOH and LGU reporting",
      "Quarterly clinical review &middot; annual training"],
     "5 devices &middot; unlimited users", f"{P}3,300 contribution"),
]


def html():
    cards = ""
    for name, amt, per, badge, feat, bullets, cap, contrib in CARDS:
        lis = "".join(f"<li>{b}</li>" for b in bullets)
        cards += f"""<div class="card{' feat' if feat else ''}">
          <div class="badge{' b2' if 'ASK' in badge else ''}">{badge}</div>
          <div class="tname">{name}</div>
          <div class="amt">{P}{amt}</div><div class="per">{per}</div>
          <ul>{lis}</ul>
          <div class="cap">{cap}</div>
          <div class="contrib">{contrib}</div></div>"""
    return f"""<!doctype html><meta charset="utf-8">{FONT}<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:{BG};font-family:'Poppins',sans-serif;color:{INK}}}
.wrap{{width:1920px;height:1080px;padding:54px 58px 46px;display:flex;flex-direction:column}}
h1{{font-size:50px;font-weight:700;margin-bottom:8px}}
.sub{{font-size:23px;color:{MUTED};margin-bottom:34px}}
.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;flex:1}}
.card{{background:#fff;border:2px solid {LINE};border-radius:22px;padding:26px 30px 24px;
      display:flex;flex-direction:column}}
.card.feat{{border:3px solid {ROSE};box-shadow:0 8px 28px rgba(233,30,118,.13)}}
.badge{{align-self:flex-start;font-size:15px;font-weight:700;letter-spacing:.12em;
       padding:6px 12px;border-radius:8px;margin-bottom:14px;background:{PALE};color:{DEEP}}}
.badge.b2{{background:{ROSE};color:#fff}}
.tname{{font-size:26px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
       color:{DEEP};margin-bottom:8px}}
.amt{{font-size:68px;font-weight:700;color:{ROSE};line-height:1}}
.per{{font-size:21px;color:{MUTED};margin:6px 0 20px}}
ul{{list-style:none}}
li{{font-size:22px;line-height:1.35;margin-bottom:11px;padding-left:22px;position:relative}}
li::before{{content:"";position:absolute;left:0;top:11px;width:8px;height:8px;
           border-radius:4px;background:{ROSE}}}
li b{{font-weight:600;color:{DEEP}}}
.cap{{margin-top:auto;padding-top:14px;font-size:20px;color:{MUTED}}}
.contrib{{margin-top:8px;padding-top:12px;border-top:2px solid {LINE};
         font-size:22px;font-weight:700;color:{DEEP}}}
.foot{{margin-top:26px;font-size:21px;color:{INK};line-height:1.45}}
.foot b{{color:{DEEP}}}
</style><div class="wrap">
<h1>Subscription tiers</h1>
<div class="sub">Per health facility. {P}1,500 stays the entry price &mdash; the ladder only adds above it.
Schools keep the separate {P}30,000 annual teaching licence. <b style="color:{DEEP}">Proposed prices, not yet validated with buyers.</b></div>
<div class="cards">{cards}</div>
<div class="foot">The upper tiers and Essential&rsquo;s visit comparison are <b>funded by the
{P}38,000 mobile-application line</b>: practitioner dashboard {P}9,000 &middot; role-based access and audit
logging {P}8,000 &middot; offline synchronisation {P}7,000 &middot; longitudinal comparison views {P}7,000.</div>
</div>"""


with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=2)
    (OUT / "Resondi-Subscription-Tiers-Slide.html").write_text(html(), encoding="utf-8")
    pg.goto((OUT / "Resondi-Subscription-Tiers-Slide.html").as_uri())
    pg.wait_for_timeout(1200)
    el = pg.query_selector(".wrap")
    el.screenshot(path=str(OUT / "Resondi-Subscription-Tiers-Slide.png"))
    bb = el.bounding_box()
    print(f"slide figure  {bb['width']:.0f} x {bb['height']:.0f} css px")
    br.close()
