"""Slide 5 — the 37 / 89 asymmetry.

Carried in the note as prose on p. 8 only. The two numbers are deliberately
not the same size: the argument is the gap between them, and equal weight
would read as "mixed results" instead of "it misses most cases". The rows
beneath are held to fixed heights so the two columns stay in register
despite the different type sizes.
"""
import pathlib
from theme import HEAD, INK, ROSE, DEEP, MUTED, PALE

OUT = pathlib.Path(__file__).parent

html = HEAD + f"""
<style>
  .top {{ position: absolute; left: 110px; top: 88px }}
  .lede {{
    margin-top: 16px; font-size: 40px; font-weight: 400; color: {INK};
    max-width: 1560px; line-height: 1.3;
  }}
  .pair {{
    position: absolute; left: 110px; right: 110px; top: 252px;
    display: flex; gap: 110px;
  }}
  .stat {{ flex: 1; display: flex; flex-direction: column }}
  .numbox {{ height: 226px; display: flex; align-items: flex-end }}
  .num {{ font-weight: 700; letter-spacing: -.04em; line-height: .86 }}
  .lead .num {{ font-size: 226px; color: {ROSE} }}
  .foil .num {{ font-size: 146px; color: {MUTED} }}
  .name {{
    margin-top: 20px; height: 54px;
    font-size: 40px; font-weight: 600; letter-spacing: .02em;
  }}
  .lead .name {{ color: {DEEP} }}
  .foil .name {{ color: {MUTED} }}
  .gloss {{
    height: 108px; font-size: 28px; font-weight: 400; color: {MUTED};
    line-height: 1.42; max-width: 780px;
  }}
  .track {{
    height: 26px; border-radius: 13px; background: {PALE}; overflow: hidden;
  }}
  .foil .track {{ background: #ECE2E6 }}
  .fill {{ height: 100%; border-radius: 13px }}
  .lead .fill {{ width: 37%; background: {ROSE} }}
  .foil .fill {{ width: 89%; background: {MUTED} }}
  .readout {{
    margin-top: 18px; font-size: 27px; font-weight: 500; color: {MUTED};
  }}
  .lead .readout b {{ color: {DEEP}; font-weight: 600 }}
  .kicker {{
    position: absolute; left: 110px; right: 110px; bottom: 142px;
    padding-top: 40px; border-top: 2px solid {PALE};
    display: flex; align-items: baseline; gap: 28px;
  }}
  .kicker .q {{ font-size: 44px; font-weight: 700; color: {DEEP} }}
  .kicker .a {{ font-size: 31px; font-weight: 400; color: {MUTED} }}
</style>
<div class="slide">
  <div class="top">
    <div class="eyebrow">Why the method matters</div>
    <div class="lede">Unaided auscultation, pooled across
      <b>34 studies</b> of pulmonary pathology:</div>
  </div>

  <div class="pair">
    <div class="stat lead">
      <div class="numbox"><div class="num">37%</div></div>
      <div class="name">Sensitivity</div>
      <div class="gloss">Of patients who had the condition, this many were
        found &mdash; 63 in 100 were missed.</div>
      <div class="track"><div class="fill"></div></div>
      <div class="readout">Good at ruling <b>in</b>. Poor at ruling
        <b>out</b>.</div>
    </div>

    <div class="stat foil">
      <div class="numbox"><div class="num">89%</div></div>
      <div class="name">Specificity</div>
      <div class="gloss">Of patients who were well, this many were
        correctly cleared.</div>
      <div class="track"><div class="fill"></div></div>
      <div class="readout">The half that already works.</div>
    </div>
  </div>

  <div class="kicker">
    <div class="q">&ldquo;The same site, the same way, every visit.&rdquo;</div>
    <div class="a">Resondi fixes the method, not the ear.</div>
  </div>

  <div class="src">Arts et al., 2020 &middot; concept note p. 8</div>
  <div class="mark">Resondi</div>
</div>
"""
(OUT / "slide05_method.html").write_text(html, encoding="utf-8")
print("wrote slide05_method.html")
