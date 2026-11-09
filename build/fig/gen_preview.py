"""Overlay the exported coordinates back onto the plates.

This is the check: if a marker lands off its landmark here, the percentages
in resondi-sites.json are wrong, because this page positions them exactly
the way the app will.
"""
import os as _os
_BUILD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))).replace(chr(92), '/')
import json
import pathlib

OUT = pathlib.Path(_BUILD + "/app-assets")
D = json.loads((OUT / "resondi-sites.json").read_text(encoding="utf-8"))
T = D["theme"]

ACTIVE = {"heart": 4, "lungAnterior": 3, "lungPosterior": 7}   # by order


def panel(key, title):
    v = D["views"][key]
    act = ACTIVE[key]
    dots, pts = [], []
    for s in v["sites"]:
        state = ("active" if s["order"] == act
                 else "done" if s["order"] < act else "todo")
        opt = " opt" if s.get("optional") else ""
        dots.append(
            f'<button class="site {state}{opt}" '
            f'style="left:{s["left"]}%;top:{s["top"]}%" '
            f'data-order="{s["order"]}">{s["tag"]}</button>')
        pts.append((s["left"], s["top"]))
    poly = " ".join(f"{x},{y}" for x, y in pts)
    return f"""
  <figure>
    <figcaption>{title}</figcaption>
    <div class="plate">
      <img src="{v['plate']}@3x.png" alt="">
      <svg class="path" viewBox="0 0 100 100" preserveAspectRatio="none">
        <polyline points="{poly}" />
      </svg>
      {''.join(dots)}
    </div>
  </figure>"""


html = f"""<!doctype html>
<meta charset="utf-8">
<title>Resondi guide - coordinate check</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box }}
  body {{
    width:1920px; height:1080px; background:{T['surface']};
    font-family:'Poppins',sans-serif; color:#2A1A22; padding:46px 54px;
  }}
  h1 {{ font-size:34px; font-weight:700 }}
  p.sub {{ font-size:21px; color:#AE99A1; margin-top:6px }}
  .row {{ display:flex; gap:40px; margin-top:26px; align-items:flex-start }}
  figure {{ flex:1 }}
  figcaption {{
    font-size:19px; font-weight:600; letter-spacing:.16em;
    text-transform:uppercase; color:#8E2A52; margin-bottom:12px;
  }}
  .plate {{ position:relative; aspect-ratio:{D['plate']['aspectRatio']} }}
  .plate img {{ width:100%; display:block }}
  .path {{ position:absolute; inset:0; width:100%; height:100% }}
  .path polyline {{
    fill:none; stroke:{T['done']}; stroke-width:.5; stroke-dasharray:1.6 1.3;
    vector-effect:non-scaling-stroke; opacity:.75;
  }}
  .site {{
    position:absolute; transform:translate(-50%,-50%);
    width:42px; height:42px; border-radius:50%; border:3px solid #fff;
    font:700 17px/1 'Poppins',sans-serif; color:#fff; cursor:pointer;
    display:grid; place-items:center; font-family:'Poppins',sans-serif;
    box-shadow:0 2px 8px rgba(42,26,34,.22);
  }}
  .site.todo {{ background:{T['marker']} }}
  .site.todo.opt {{ background:{T['markerOptional']} }}
  .site.done {{ background:{T['done']} }}
  .site.active {{
    background:{T['active']}; width:58px; height:58px; font-size:22px;
    box-shadow:0 0 0 10px rgba(233,30,118,.20), 0 4px 14px rgba(42,26,34,.3);
  }}
  .key {{ display:flex; gap:34px; margin-top:20px; font-size:19px;
         color:#AE99A1; align-items:center }}
  .key i {{ width:19px; height:19px; border-radius:50%; display:inline-block;
           margin-right:9px; vertical-align:-3px }}
</style>
<body>
  <h1>Auscultation guide &mdash; coordinate check</h1>
  <p class="sub">Markers positioned from resondi-sites.json only. Nothing
    here is drawn into the plate.</p>
  <div class="row">
    {panel('heart', 'Heart mode &middot; anterior')}
    {panel('lungAnterior', 'Lung mode &middot; anterior')}
    {panel('lungPosterior', 'Lung mode &middot; posterior')}
  </div>
  <div class="key">
    <span><i style="background:{T['done']}"></i>recorded</span>
    <span><i style="background:{T['active']}"></i>current site</span>
    <span><i style="background:{T['marker']}"></i>still to record</span>
    <span><i style="background:{T['markerOptional']}"></i>optional</span>
  </div>
</body>
"""
(OUT / "preview.html").write_text(html, encoding="utf-8")
print("wrote preview.html")
