"""Shared look for the Resondi pitch slides.

Colours are the ones the app itself uses, so a slide dropped into the deck
sits beside a screenshot without a seam.
"""

BG = "#FFF5F9"        # app background
INK = "#2A1A22"       # app text
ROSE = "#E91E76"      # app accent
DEEP = "#8E2A52"      # deep rose, matches the concept-note figures
MUTED = "#AE99A1"     # app secondary text
PALE = "#F7D6E4"      # tint for empty bar track
TEAL = "#0F7B76"      # reserved for the favourable half of a statistic
DARK = "#241318"      # inverted slide background

W, H = 1920, 1080

HEAD = f"""<!doctype html>
<meta charset="utf-8">
<style>
  @page {{ margin: 0 }}
  * {{ margin: 0; padding: 0; box-sizing: border-box }}
  html, body {{ width: {W}px; height: {H}px; overflow: hidden }}
  body {{
    font-family: 'Poppins', 'Inter', sans-serif;
    background: {BG};
    color: {INK};
    -webkit-font-smoothing: antialiased;
  }}
  .slide {{ width: {W}px; height: {H}px; position: relative }}
  .eyebrow {{
    font-size: 26px; font-weight: 600; letter-spacing: .20em;
    text-transform: uppercase; color: {MUTED};
  }}
  .src {{
    position: absolute; left: 110px; bottom: 58px;
    font-size: 24px; font-weight: 400; color: {MUTED};
  }}
  .mark {{
    position: absolute; right: 110px; bottom: 58px;
    font-size: 24px; font-weight: 600; letter-spacing: .14em;
    text-transform: uppercase; color: {PALE};
  }}
  .rule {{ height: 5px; background: {ROSE}; border-radius: 3px }}
</style>
"""
