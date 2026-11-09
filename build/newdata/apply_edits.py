"""Apply the UTAUT rewrite and the 30 -> 27 correction across all build sources."""
import pathlib

EDITS = []


def E(path, old, new, label):
    EDITS.append((path, old, new, label))


# ── 1. CONCEPT NOTE ─────────────────────────────────────────────────────
E("cn2/build.js", """  + 'capture, is what makes noise reduction the first development priority. End-user acceptance was assessed with '
  + '30 participants across Puerto Princesa City, together with three patients at a private '
  + 'hospital under the supervision of an attending physician who reviewed and consented to the '
  + 'procedure; the acceptance findings are reported in '),
  T('[insert the weighted means for user-friendliness, usability, durability, '
  + 'functionality and community impact]', { color: 'C00000', bold: true }),
  T('.')]));""", """  + 'capture, is what makes noise reduction the first development priority. End-user acceptance '
  + 'was assessed with 27 respondents across Puerto Princesa City using an instrument adapted '
  + 'from the Unified Theory of Acceptance and Use of Technology, together with three patients '
  + 'at a private hospital under the supervision of an attending physician who reviewed and '
  + 'consented to the procedure. Across twelve five-point Likert items overall acceptance was '
  + '3.95, interpreted as Agree on the study\\u2019s acceptance scale. Performance expectancy '
  + 'and effort expectancy each returned a weighted mean of 4.09, regulatory assurance 3.84, '
  + 'and social influence 3.63. Twenty-one of twenty-seven respondents reported that peers '
  + 'encourage use of the device and twenty of twenty-seven that their institution would '
  + 'provide the resources to run it; access to training and technical support drew the least '
  + 'certain response, with eight answering yes, twelve unsure and seven no.')]));""",
  "concept note: acceptance passage -> UTAUT, 30 -> 27, placeholder resolved")

# ── 2. SCRIPT ───────────────────────────────────────────────────────────
E("script5/revised_long.txt",
  "J: Acceptance was tested with thirty participants across Puerto Princesa City, and three patients at a private hospital under a supervising physician.",
  "J: Acceptance was tested with twenty-seven respondents across Puerto Princesa City, and three patients at a private hospital. Overall acceptance came back at three point nine five out of five.",
  "script: 30 -> 27 and the acceptance score added")

# ── 3. JUDGE Q&A ────────────────────────────────────────────────────────
E("qa/part5.py", "“How were your thirty acceptance participants selected?”",
  "“How were your twenty-seven acceptance respondents selected?”",
  "Q&A: question wording 30 -> 27")

# ── 4. SLIDES ───────────────────────────────────────────────────────────
E("slides/build_results.py",
  "<span>Acceptance tested with <b>30 participants</b></span>",
  "<span>Acceptance <b>3.95/5</b> across 27 respondents</span>",
  "slides: participant count and the score")

# ── 5. IMRaD — methodology ──────────────────────────────────────────────
E("imrad/build_imrad.py", '''p = para("End-user acceptance. Acceptance was assessed with thirty participants across "
         "Puerto Princesa City, together with three patients at a private hospital under "
         "the supervision of an attending physician who reviewed and consented to the "
         "procedure.", first=0, after=6, spacing=1.6)
FILL(p, "sampling method and inclusion criteria for the thirty participants. The "
        "instrument is documented; how participants were selected is not")''',
  '''p = para("End-user acceptance. Acceptance was assessed with 27 respondents across Puerto "
         "Princesa City using a questionnaire adapted from the Unified Theory of Acceptance "
         "and Use of Technology (Venkatesh, Morris, Davis, & Davis, 2003), together with "
         "three patients at a private hospital under the supervision of an attending "
         "physician who reviewed and consented to the procedure. Items were rated on a "
         "five-point Likert scale and grouped into four constructs \\u2014 performance "
         "expectancy, effort expectancy, social influence and facilitating conditions "
         "\\u2014 together with a fifth group assessing the degree to which conformity with "
         "recognised medical-device standards (ISO 13485, ISO 14971, ISO/IEC 62304, ISO/IEC "
         "27001 and ISO 14155) influenced confidence in the device, reported here as "
         "regulatory assurance. Weighted mean, standard deviation and Cronbach\\u2019s alpha "
         "were computed for each construct and interpreted against the five-point "
         "acceptance scale. Three items used a dichotomous response format and are reported "
         "as frequencies rather than means. Three behavioural-intention items and all "
         "open-ended items returned no responses and are not reported.",
         first=0, after=6, spacing=1.6)
FILL(p, "sampling method and inclusion criteria for the 27 respondents. The instrument is "
        "documented; how respondents were recruited is not")''',
  "IMRaD: methodology rewritten around UTAUT")

# ── 6. IMRaD — results ──────────────────────────────────────────────────
E("imrad/build_imrad.py", '''p = para("Acceptance was assessed with thirty participants across Puerto Princesa City "
         "together with three patients at a private hospital.", first=0)
FILL(p, "report the actual acceptance findings — scores, proportions, or themes. The "
        "current material records that the assessment was conducted but not what it "
        "found")''',
  '''para("Twenty-seven respondents completed the acceptance questionnaire: 13 patients, "
     "13 general respondents and one health practitioner. Across the twelve five-point "
     "Likert items, overall acceptance was 3.95, interpreted as Agree.", first=0)

para("Performance expectancy and effort expectancy each returned a weighted mean of "
     "4.09 (SD = 0.59 and 0.60 respectively), both interpreted as Agree. Regulatory "
     "assurance returned 3.84 (SD = 0.61) and social influence 3.63 (SD = 1.21), "
     "likewise interpreted as Agree.")

para("Internal consistency varied across constructs. Effort expectancy reached "
     "acceptable reliability (\\u03b1 = 0.76). Regulatory assurance (\\u03b1 = 0.59) and "
     "performance expectancy (\\u03b1 = 0.51) fell below the conventional 0.70 "
     "threshold. With three to five items per construct and 27 respondents these "
     "values are reported as provisional, and the constructs are presented "
     "descriptively rather than as validated scales. Social influence is represented "
     "by a single item, for which no alpha is computed.")

p = para("Dichotomous items are reported as frequencies. Twenty-one of 27 respondents "
         "(78 percent) indicated that peers or colleagues encourage use of the device, "
         "and 20 of 27 (74 percent) reported that their institution provides resources "
         "to use it effectively. Access to training and technical support was the least "
         "certain response: 12 respondents (44 percent) answered \\u2018maybe\\u2019, 8 "
         "(30 percent) \\u2018yes\\u2019 and 7 (26 percent) \\u2018no\\u2019. Eleven "
         "respondents (41 percent) reported prior experience with medical devices or "
         "health applications.")
FILL(p, "confirm whether the three patients recorded at the private hospital are "
        "distinct from the 13 respondents who identified themselves as patients in the "
        "acceptance questionnaire. The two groups are currently described separately")''',
  "IMRaD: acceptance results written, FILL marker resolved")

# ── apply ───────────────────────────────────────────────────────────────
ok, miss = [], []
by_file = {}
for path, old, new, label in EDITS:
    by_file.setdefault(path, []).append((old, new, label))

for path, items in by_file.items():
    p = pathlib.Path(__file__).resolve().parent.parent / path
    s = p.read_text()
    for old, new, label in items:
        n = s.count(old)
        if n == 1:
            s = s.replace(old, new)
            ok.append(label)
        else:
            miss.append(f"{label}  (found {n} times)")
    if not miss:
        p.write_text(s)

print("APPLIED:")
for o in ok:
    print("  +", o)
if miss:
    print("\nFAILED - nothing written for those files:")
    for m in miss:
        print("  -", m)
