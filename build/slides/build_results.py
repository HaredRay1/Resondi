"""Results slide — what the prototype has actually done.

Every figure is from Malimban (2026), the team's own RIM full paper. The
agreement result is weak and is presented as weak: a judge who reads the
paper will find it either way, and finding it after the pitch is worse.
"""
import pathlib
from theme import HEAD, INK, ROSE, DEEP, MUTED, PALE, TEAL

OUT = pathlib.Path(__file__).parent

STATS = [
    ("45 dB", "Signal strength",
     "against 32 dB from a conventional stethoscope &mdash; a 13 dB gap, "
     "<b>~4.5&times; the amplitude</b>"),
    ("68%", "Recordings rated Good",
     "by qualified healthcare professionals; 25% acceptable, 7% poor"),
    ("3 of 3", "Environments recorded in",
     "quiet room 24 dB, hospital ward 35 dB, community area 42 dB &mdash; "
     "only ~3 dB of headroom in the noisiest"),
]

cells = "".join(
    f"""<div class="stat">
          <div class="big">{big}</div>
          <div class="name">{name}</div>
          <div class="gloss">{gloss}</div>
        </div>""" for big, name, gloss in STATS)

html = HEAD + f"""
<style>
  .top {{ position: absolute; left: 110px; top: 74px }}
  .head {{
    margin-top: 12px; font-size: 50px; font-weight: 700; color: {INK};
    letter-spacing: -.01em;
  }}
  .row {{
    position: absolute; left: 110px; right: 110px; top: 252px;
    display: flex; gap: 64px;
  }}
  .stat {{ flex: 1 }}
  .big {{
    font-size: 92px; font-weight: 700; color: {ROSE}; line-height: 1;
    letter-spacing: -.03em;
  }}
  .name {{
    margin-top: 16px; font-size: 30px; font-weight: 600; color: {DEEP};
  }}
  .gloss {{
    margin-top: 10px; font-size: 24px; font-weight: 400; color: {MUTED};
    line-height: 1.45;
  }}
  .gloss b {{ color: {DEEP}; font-weight: 600 }}

  .band {{
    position: absolute; left: 110px; right: 110px; top: 566px;
    display: flex; gap: 54px; align-items: stretch;
  }}
  .agree {{
    flex: 1.15; background: #FBE6EE; border-radius: 18px;
    padding: 32px 36px;
  }}
  .limit {{
    flex: 1; border-left: 7px solid {DEEP}; padding: 6px 0 6px 30px;
    display: flex; flex-direction: column; justify-content: center;
  }}
  .k {{
    font-size: 21px; font-weight: 600; letter-spacing: .15em;
    text-transform: uppercase; color: {MUTED};
  }}
  .agree .v {{
    margin-top: 10px; font-size: 42px; font-weight: 700; color: {DEEP};
  }}
  .agree .d {{
    margin-top: 12px; font-size: 24px; color: {INK}; line-height: 1.5;
  }}
  .agree .d b {{ color: {DEEP} }}
  .limit .t {{
    margin-top: 10px; font-size: 27px; line-height: 1.5; color: {INK};
  }}
  .limit .t b {{ color: {ROSE} }}
  .foot {{
    position: absolute; left: 110px; right: 110px; bottom: 124px;
    padding-top: 26px; border-top: 2px solid {PALE};
    display: flex; gap: 60px; font-size: 23px; color: {MUTED};
  }}
  .foot b {{ color: {DEEP}; font-weight: 600 }}
</style>
<div class="slide">
  <div class="top">
    <div class="eyebrow">What the prototype has already done</div>
    <div class="head">Built, tested in the field, and measured.</div>
  </div>

  <div class="row">{cells}</div>

  <div class="band">
    <div class="agree">
      <div class="k">Against reference labels</div>
      <div class="v">6 of 15 &middot; 40% agreement</div>
      <div class="d">95% CI <b>19.8&ndash;64.3%</b> &mdash; the interval contains
        chance and it contains a working classifier. Fifteen recordings is far
        too few to conclude anything, and we report a baseline, not a rate.</div>
    </div>
    <div class="limit">
      <div class="k">Which is the point</div>
      <div class="t">That number is <b>why we are asking</b>. Clinical
        validation is &#8369;120,000 of the &#8369;500,000 &mdash; the largest line.</div>
    </div>
  </div>

  <div class="foot">
    <span>Classifies <b>4 patterns</b> &mdash; normal, wheeze, crackle,
      both</span>
    <span>Acceptance <b>3.95/5</b> across 27 respondents</span>
    <span><b>3 patients</b> at a private hospital, under the
      attending physician</span>
  </div>
  <div class="src">Malimban, 2026 &middot; Resondi full paper</div>
  <div class="mark">Resondi</div>
</div>
"""
(OUT / "slide_results.html").write_text(html, encoding="utf-8")
print("wrote slide_results.html")
