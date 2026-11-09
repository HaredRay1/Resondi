"""Slide 2 — the problem, in two parts.

2a  the two mortality figures, which the note carries only as prose (p. 22)
2b  the 2.7 percent rehabilitation-access figure (note p. 1)
"""
import pathlib
from theme import HEAD, BG, INK, ROSE, DEEP, MUTED, PALE, DARK, W, H

OUT = pathlib.Path(__file__).parent

# ── 2a ───────────────────────────────────────────────────────────────────
mortality = HEAD + f"""
<style>
  .top {{ position: absolute; left: 110px; top: 96px }}
  .total {{
    margin-top: 18px; font-size: 40px; font-weight: 400; color: {INK};
  }}
  .total b {{ font-weight: 700; color: {DEEP} }}
  .cols {{
    position: absolute; left: 110px; right: 110px; top: 322px;
    display: flex; gap: 92px;
  }}
  .col {{ flex: 1 }}
  .col .rule {{ width: 148px; margin-bottom: 34px }}
  .big {{
    font-size: 188px; font-weight: 700; line-height: .92;
    letter-spacing: -.035em; color: {ROSE};
  }}
  .cond {{
    margin-top: 26px; font-size: 44px; font-weight: 600; color: {INK};
    line-height: 1.22;
  }}
  .share {{
    margin-top: 16px; font-size: 32px; font-weight: 400; color: {MUTED};
  }}
  .kicker {{
    position: absolute; left: 110px; right: 110px; bottom: 196px;
    font-size: 42px; font-weight: 600; color: {DEEP};
    padding-top: 40px; border-top: 2px solid {PALE};
  }}
</style>
<div class="slide">
  <div class="top">
    <div class="eyebrow">The problem</div>
    <div class="total">Registered deaths in the Philippines, 2024 &mdash;
      <b>701,884</b></div>
  </div>

  <div class="cols">
    <div class="col">
      <div class="rule"></div>
      <div class="big">134,074</div>
      <div class="cond">Ischaemic heart disease</div>
      <div class="share">Leading cause &middot; 19.1% of all deaths</div>
    </div>
    <div class="col">
      <div class="rule"></div>
      <div class="big">47,260</div>
      <div class="cond">Pneumonia</div>
      <div class="share">4th leading cause &middot; 6.7% of all deaths</div>
    </div>
  </div>

  <div class="kicker">Both are assessed by auscultation. Neither is
    assessed once.</div>
  <div class="src">Philippine Statistics Authority, 2025</div>
  <div class="mark">Resondi</div>
</div>
"""
(OUT / "slide02a_mortality.html").write_text(mortality, encoding="utf-8")

# ── 2b ───────────────────────────────────────────────────────────────────
# 100 dots, 3 of them lit: the figure is 2.7 percent, so the third dot is
# drawn at 70 percent opacity rather than rounded up to a whole person.
dots = []
for i in range(100):
    if i < 2:
        cls = "on"
    elif i == 2:
        cls = "on part"
    else:
        cls = "off"
    dots.append(f'<span class="d {cls}"></span>')

rehab = HEAD + f"""
<style>
  body {{ background: {DARK}; color: #FFF5F9 }}
  .slide {{ background: {DARK} }}
  .eyebrow {{ color: #7E616C }}
  .top {{ position: absolute; left: 110px; top: 96px }}
  .big {{
    margin-top: 40px; font-size: 300px; font-weight: 700; line-height: .86;
    letter-spacing: -.045em; color: {ROSE};
  }}
  .say {{
    margin-top: 28px; font-size: 46px; font-weight: 400; line-height: 1.32;
    color: #FFF5F9; max-width: 1000px;
  }}
  .say b {{ font-weight: 600 }}
  .grid {{
    position: absolute; right: 118px; top: 300px;
    width: 520px; display: flex; flex-wrap: wrap; gap: 18px;
  }}
  .d {{ width: 34px; height: 34px; border-radius: 50% }}
  .d.off {{ background: #3E2730 }}
  .d.on {{ background: {ROSE} }}
  .d.part {{ opacity: .7 }}
  .tie {{
    position: absolute; left: 110px; bottom: 196px; width: 1000px;
    padding-top: 40px; border-top: 2px solid #3E2730;
    font-size: 40px; font-weight: 600; color: {ROSE};
  }}
  .cap {{
    position: absolute; right: 118px; top: 836px; width: 520px;
    font-size: 26px; font-weight: 400; color: #9A7D88; text-align: left;
  }}
  .src {{ color: #7E616C }}
  .mark {{ color: #3E2730 }}
</style>
<div class="slide">
  <div class="top">
    <div class="eyebrow">The gap after diagnosis</div>
    <div class="big">2.7%</div>
    <div class="say">of people with <b>COPD</b> worldwide had access to
      pulmonary rehabilitation.</div>
  </div>

  <div class="grid">{''.join(dots)}</div>
  <div class="cap">Each dot is one patient in a hundred.</div>
  <div class="tie">Diagnosis is one visit. Recovery is forty.</div>

  <div class="src">Lahham &amp; Holland, 2021 &middot; figure for 2015</div>
  <div class="mark">Resondi</div>
</div>
"""
(OUT / "slide02b_rehab.html").write_text(rehab, encoding="utf-8")
print("wrote slide02a_mortality.html, slide02b_rehab.html")
