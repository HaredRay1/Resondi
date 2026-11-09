import re
CUTS = {
 "problem_padding": "So respiratory disease is not simply a hospital problem. It's a monitoring problem. "
                    "A rehabilitation problem. And a contact problem.",
 "dashboard_long":  "But Resondi isn't only for the person holding the device. It has a dual dashboard. "
                    "One for the health professional... and one for the patient. The practitioner has "
                    "the last word: confirm, modify, or repeat.",
 "rehab_long":      "The patient follows the exercise... completes sessions... and builds a "
                    "rehabilitation record.",
 "fusion_line":     "A fusion model reads it three ways: spectrogram, MFCC, and chromagram. Three "
                    "opinions, one verdict.",
 "pvalue_line":     "Agreement with the reference was 6 out of 15 recordings, or 40%, with a p-value "
                    "of 1.000.",
 "response_line":   "Connecting took 4.55 seconds, recording 15, preprocessing 21, and classification "
                    "under 4. Quality assessment took the longest, at 145 seconds.",
 "signal_line":     "Resondi reached 32.49 dB, compared to 7.89 dB from a conventional stethoscope.",
 "pulmo_line":      "This system was developed with clinical input from a pulmonologist.",
}
ADDS = {
 "problem_padding": "Respiratory disease is not only a hospital problem. It is a monitoring problem.",
 "dashboard_long":  "Resondi isn't only for the person holding it. Practitioners get one dashboard, "
                    "patients another — and the practitioner has the last word: confirm, modify, or repeat.",
 "rehab_long":      "The patient follows the exercise and builds a rehabilitation record.",
 "fusion_line":     "The spectrogram goes into a convolutional network trained on ICBHI 2017 — "
                    "920 recordings from 126 patients.",
 "pvalue_line":     "Six of fifteen recordings agreed with the reference. Forty percent. And fifteen "
                    "is far too few to call that a rate.",
 "response_line":   "Classification takes about four seconds. Quality assessment is our bottleneck, "
                    "and fixing it is first on the list.",
 "signal_line":     "Resondi produced a measurably stronger signal than a conventional stethoscope "
                    "under the same conditions.",
 "pulmo_line":      "Reference recordings were reviewed by three pulmonologists, one of them also a "
                    "pediatrician.",
}
NEW = {
 "quality_gate": "Before anything is analyzed, the recording is graded — good, acceptable, poor, or "
                 "invalid. Poor ones get repeated, not classified.",
 "ci_line":      "On fifteen samples the interval runs from twenty to sixty-four percent. That is why "
                 "we are not claiming a number yet.",
 "sdg4":         "and SDG 4, Quality Education.",
}
w = lambda s: len(s.split())
base = 618
cut = sum(w(v) for v in CUTS.values())
add = sum(w(v) for v in ADDS.values())
new = sum(w(v) for v in NEW.values())
total = base - cut + add + new
print(f"original spoken words : {base}")
print(f"  removed             : -{cut}")
print(f"  replacements        : +{add}")
print(f"  new lines           : +{new}")
print(f"revised spoken words  : {total}")
print(f"speech at 150 wpm     : {total/150*60:.0f}s = {total//150}m{int(total/150*60%60):02d}s")
print(f"room left in 5:00     : {300-total/150*60:.0f}s for 40 cues, the demo and pauses")
