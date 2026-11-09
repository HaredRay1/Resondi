"""Two financial slides the concept note does not carry.

payback   cumulative cash contribution against the P500,000 requirement
backup    the Year 1 -> Year 2 build-up, flagged as a back-up slide because
          it corrects a figure printed on p. 21 of the submitted note

The monthly model: a facility pays P4,000 of device margin on acquisition
and contributes P900 a month thereafter (note Table 4); a school licence
contributes P25,800 a year net of platform cost (note p. 20). Facilities
onboard one a month from month 3, reaching 10 by the end of Year 1 and 25
by the end of Year 2; school licences bill on their own anniversaries.
"""
import os as _os
_BUILD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))).replace(chr(92), '/')
import pathlib
from theme import HEAD, INK, ROSE, DEEP, MUTED, PALE, TEAL

OUT = pathlib.Path(__file__).parent

import sys
sys.path.insert(0, _BUILD + "/finpack")
from model import ROWS as _R, OFFSET            # single source of truth

SEED = 500_000
series = [(r["m"], r["cum"]) for r in _R[:24]]  # the slide is a two-year chart
Y1 = dict(series)[12]
Y2_END = dict(series)[24]
CROSS = next(m for m, c in series if c >= SEED)
FROM_FUNDING = CROSS + OFFSET

# ── plot geometry ────────────────────────────────────────────────────────
X0, X1 = 236, 1788
Y0, Y1P = 528, 44             # y for P0 and for the top of the scale
TOP = 650_000


def px(m):
    return X0 + (m - 1) * (X1 - X0) / 23


def py(v):
    return Y0 - v / TOP * (Y0 - Y1P)


pts = [(px(m), py(c)) for m, c in series]
line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
area = f"{X0},{Y0} " + line + f" {X1},{Y0}"

gridlines, ylabels = [], []
for v in range(0, TOP + 1, 100_000):
    y = py(v)
    gridlines.append(f'<line x1="{X0}" y1="{y:.1f}" x2="{X1}" y2="{y:.1f}" '
                     f'stroke="{PALE}" stroke-width="2"/>')
    lab = "&#8369;0" if v == 0 else f"&#8369;{v // 1000}k"
    ylabels.append(f'<text x="{X0 - 26}" y="{y + 10:.1f}" text-anchor="end" '
                   f'class="ax">{lab}</text>')

xticks = []
for m in range(1, 25):
    if m % 3 == 0 or m == 1:
        xticks.append(f'<text x="{px(m):.1f}" y="{Y0 + 44}" '
                      f'text-anchor="middle" class="ax">{m}</text>')

cx, cy = px(CROSS), py(dict(series)[CROSS])
y300 = py(SEED)

svg = f"""
<svg width="1920" height="640" viewBox="0 0 1920 640">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{ROSE}" stop-opacity=".26"/>
      <stop offset="100%" stop-color="{ROSE}" stop-opacity=".02"/>
    </linearGradient>
  </defs>

  <rect x="{X0}" y="{Y1P}" width="{px(12) - X0:.1f}" height="{Y0 - Y1P}"
        fill="#FBE6EE" opacity=".55"/>
  <text x="{(X0 + px(12)) / 2:.1f}" y="{Y1P + 34}" text-anchor="middle"
        class="band">YEAR 1</text>
  <text x="{(px(12) + X1) / 2:.1f}" y="{Y1P + 34}" text-anchor="middle"
        class="band">YEAR 2</text>

  {''.join(gridlines)}
  {''.join(ylabels)}
  {''.join(xticks)}

  <polygon points="{area}" fill="url(#g)"/>
  <polyline points="{line}" fill="none" stroke="{ROSE}" stroke-width="7"
            stroke-linejoin="round" stroke-linecap="round"/>

  <line x1="{X0}" y1="{y300:.1f}" x2="{X1}" y2="{y300:.1f}"
        stroke="{DEEP}" stroke-width="4" stroke-dasharray="14 11"/>
  <text x="{X0 + 20}" y="{y300 - 20:.1f}" text-anchor="start" class="thr">
    &#8369;500,000 REQUIREMENT</text>

  <line x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx:.1f}" y2="{Y0}"
        stroke="{DEEP}" stroke-width="3" stroke-dasharray="7 8"
        opacity=".55"/>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="19" fill="#FFF5F9"/>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="13" fill="{DEEP}"/>
  <text x="{X0 + 26}" y="{py(385_000):.1f}" class="cross">
    MONTH {CROSS}</text>
  <text x="{X0 + 26}" y="{py(330_000):.1f}" class="crossv">
    &#8369;{dict(series)[CROSS]:,} recovered</text>
</svg>
"""

payback = HEAD + f"""
<style>
  .top {{ position: absolute; left: 110px; top: 84px }}
  .head {{
    margin-top: 14px; font-size: 54px; font-weight: 700; color: {INK};
    letter-spacing: -.01em;
  }}
  .head b {{ color: {ROSE} }}
  svg {{ position: absolute; left: 0; top: 190px }}
  text {{ font-family: 'Poppins', sans-serif }}
  .ax {{ font-size: 24px; fill: {MUTED}; font-weight: 400 }}
  .axt {{ font-size: 22px; fill: {MUTED}; font-weight: 600;
         letter-spacing: .18em }}
  .band {{ font-size: 24px; fill: {MUTED}; font-weight: 600;
          letter-spacing: .20em }}
  .thr {{ font-size: 25px; fill: {DEEP}; font-weight: 600;
         letter-spacing: .10em }}
  .cross {{ font-size: 27px; fill: {DEEP}; font-weight: 700;
           letter-spacing: .10em }}
  .crossv {{ font-size: 27px; fill: {MUTED}; font-weight: 500 }}
  .strip {{
    position: absolute; left: 110px; right: 110px; bottom: 148px;
    display: flex; gap: 86px; padding-top: 30px;
    border-top: 2px solid {PALE};
  }}
  .cell .k {{ font-size: 23px; font-weight: 600; letter-spacing: .14em;
             text-transform: uppercase; color: {MUTED} }}
  .cell .v {{ margin-top: 6px; font-size: 40px; font-weight: 700;
             color: {DEEP} }}
  .cell.hi .v {{ color: {ROSE} }}
  .note {{
    position: absolute; left: 110px; bottom: 48px; right: 420px;
    font-size: 22px; font-weight: 400; color: {MUTED}; line-height: 1.4;
  }}
</style>
<div class="slide">
  <div class="top">
    <div class="eyebrow">Return on the requirement</div>
    <div class="head">The seed is recovered in <b>commercial month {CROSS}</b>.</div>
  </div>

  {svg}

  <div class="strip">
    <div class="cell"><div class="k">End of Year 1</div>
      <div class="v">&#8369;{Y1:,}</div></div>
    <div class="cell hi"><div class="k">Crosses &#8369;500,000</div>
      <div class="v">Month {CROSS}</div></div>
    <div class="cell"><div class="k">End of Year 2</div>
      <div class="v">&#8369;{Y2_END:,}</div></div>
    <div class="cell"><div class="k">From funding</div>
      <div class="v">Month {FROM_FUNDING}</div></div>
  </div>

  <div class="note">Months are months of commercial operation. Cumulative contribution, not revenue. Device margin
    &#8369;4,000 per unit and &#8369;900 per facility per month (note Table 4);
    institutional licence &#8369;25,800 per year net of platform cost.
    Facilities onboard one a month; commercial month 1 is month 15 from
    funding. The investor's 40% share returns the seed later, in commercial
    Year 3.</div>
  <div class="mark">Resondi</div>
</div>
"""
(OUT / "slide_payback.html").write_text(payback, encoding="utf-8")

# ── back-up slide: the Year 1 -> Year 2 build-up ─────────────────────────
rows = [
    ("Device margin", "&#8369;4,000 &times; new units",
     "&#8369;40,000", "&#8369;60,000"),
    ("Subscription contribution", "&#8369;900 &times; 12 months",
     "&#8369;108,000", "&#8369;270,000"),
    ("Institutional licences", "&#8369;25,800 net, per school",
     "&#8369;77,400", "&#8369;180,600"),
]
body = "".join(
    f'<tr><td class="l">{a}</td><td class="d">{b}</td>'
    f'<td class="n">{c}</td><td class="n">{d}</td></tr>'
    for a, b, c, d in rows)

backup = HEAD + f"""
<style>
  .badge {{
    position: absolute; left: 110px; top: 76px;
    background: {DEEP}; color: #FFF5F9; border-radius: 999px;
    padding: 13px 30px; font-size: 22px; font-weight: 600;
    letter-spacing: .16em; text-transform: uppercase;
  }}
  .head {{
    position: absolute; left: 110px; top: 168px;
    font-size: 56px; font-weight: 700; color: {INK}; letter-spacing: -.01em;
  }}
  table {{
    position: absolute; left: 110px; right: 110px; top: 288px;
    width: 1700px; border-collapse: collapse;
  }}
  th {{
    font-size: 24px; font-weight: 600; letter-spacing: .14em;
    text-transform: uppercase; color: {MUTED}; text-align: left;
    padding: 0 0 20px; border-bottom: 3px solid {DEEP};
  }}
  th.n, td.n {{ text-align: right }}
  td {{ padding: 26px 0; border-bottom: 2px solid {PALE} }}
  td.l {{ font-size: 34px; font-weight: 600; color: {INK} }}
  td.d {{ font-size: 27px; font-weight: 400; color: {MUTED} }}
  td.n {{ font-size: 36px; font-weight: 600; color: {INK};
         font-variant-numeric: tabular-nums }}
  tr.tot td {{ border-bottom: none; padding-top: 32px }}
  tr.tot td.l {{ font-size: 36px; font-weight: 700; color: {DEEP} }}
  tr.tot td.n {{ font-size: 46px; font-weight: 700; color: {DEEP} }}
  tr.tot td.n.bad {{ color: {ROSE} }}
  .flag {{
    position: absolute; left: 110px; right: 110px; bottom: 128px;
    padding: 28px 34px; border-left: 7px solid {ROSE};
    background: #FDEAF2; font-size: 28px; line-height: 1.45; color: {INK};
  }}
  .flag b {{ color: {DEEP} }}
  .scope {{
    position: absolute; left: 110px; bottom: 58px;
    font-size: 22px; color: {MUTED};
  }}
</style>
<div class="slide">
  <div class="badge">Back-up &mdash; show only if asked</div>
  <div class="head">Contribution build-up, Year 1 &rarr; Year 2</div>

  <table>
    <tr><th>Stream</th><th>Basis</th>
      <th class="n">Year 1 &middot; 10 facilities, 3 schools</th>
      <th class="n">Year 2 &middot; 25 facilities, 7 schools</th></tr>
    {body}
    <tr class="tot"><td class="l">Total contribution</td><td></td>
      <td class="n">&#8369;225,400</td>
      <td class="n bad">&#8369;510,600</td></tr>
  </table>

  <div class="flag">Year 1 matches the concept note. <b>Year 2 does
    not</b> &mdash; p.&nbsp;21 states &#8369;795,000, which we have since
    found to be an overstatement. &#8369;510,600 is the figure we stand
    behind, and it is the conservative one.</div>
  <div class="scope">Contribution after platform and support cost, not
    gross revenue.</div>
  <div class="mark">Resondi</div>
</div>
"""
(OUT / "slide_backup_year2.html").write_text(backup, encoding="utf-8")
print(f"Y1 {Y1:,} | crossing month {CROSS} | Y2 end {Y2_END:,}")
print("wrote slide_payback.html, slide_backup_year2.html")
