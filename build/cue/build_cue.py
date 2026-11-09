"""Resondi — spoken answers for live Q&A.

Each answer is written to be said, not read: the first sentence is the answer
and everything after it is support. Target is 55-80 spoken words, which at
pitch pace is 22-32 seconds — long enough to be substantive, short enough
that the judge is still listening at the end.
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

INK   = RGBColor(0x1A, 0x1A, 0x1A)
ROSE  = RGBColor(0xC2, 0x18, 0x5B)
GREY  = RGBColor(0x66, 0x66, 0x66)
SLATE = RGBColor(0x1F, 0x4E, 0x79)
FONT  = "Calibri"
WPM   = 150

SPEAKER = {"A": "Ahnycca", "H": "Hared", "J": "Jarred"}

CUES = [
 ("OPEN", "A", "“Tell us about Resondi.”",
  "A stethoscope lets you hear a patient once. Resondi guides you to seven lung sites "
  "and five cardiac points, saves what it hears at each one, flags what sounds abnormal, "
  "and sends it to a practitioner to confirm or reject. Next visit, you compare the same "
  "site against itself. Eight thousand pesos, works without a network, built in Palawan."),

 ("1", "A", "“Forty percent agreement. What stops Resondi missing the disease?”",
  "Resondi never gives a patient a diagnosis. The classification is a flag on a "
  "recording, held as Pending Review until a practitioner acts on it. Nobody is sent home "
  "on the model’s word, because the model’s word never leaves the queue. And forty "
  "percent is six agreements out of fifteen recordings — too few to be a rate. It is the "
  "number we are funding ourselves to beat."),

 ("2", "A", "“Have you consulted the FDA, the DOH, or an ethics board?”",
  "Not the FDA yet, and I will say that plainly. We have our research adviser for ethics "
  "endorsement, four consulting clinicians for labelling and reference assessment, and "
  "ethics committee review funded inside the fifty-one thousand peso validation line. "
  "What we have not done is file. Our Regulatory lead owns that filing and it is a phase "
  "milestone. May I ask what you would want in place before a pilot?"),

 ("3", "J", "“Who buys it, who maintains it, and how does it scale?”",
  "Rural health units and municipal health offices through their equipment budget, "
  "private clinics, and nursing schools. Eight thousand pesos a device against four "
  "thousand to build — fifty percent margin from the first unit. Fifteen hundred a month "
  "per facility covers the platform and field service, which is a named role on our chart, "
  "not a promise. And we scale municipality by municipality, because one health office "
  "covers several barangay stations at once."),

 ("4", "J", "“How are you different from Eko Health?”",
  "Eko is a better device and I will not pretend otherwise. But their AI is cleared in "
  "the United States, not here — a Palawan health unit cannot buy it at any price. Their "
  "hardware lands near twenty-two thousand pesos before the subscription. Their cleared "
  "algorithms are cardiac, while pneumonia is our fourth-leading cause of death. And Eko "
  "hands a cardiologist a better chest piece. We guide a midwife to the right site."),

 ("5", "A", "“Existing AI tools can already do what you described.”",
  "A general AI cannot hear. Our input is a twenty-second acoustic signal below three "
  "hundred hertz — under what a phone microphone passes, and what its own processing "
  "actively suppresses. There is no general-purpose tool you can hold against a patient’s "
  "chest. It has no sensor, no placement protocol, and no training on labelled crackles "
  "and murmurs."),

 ("6", "H", "“Health workers will just go back to doing it manually.”",
  "That is the risk I worry about most, because what we compete with is the stethoscope "
  "already around their neck. The difference is that Resondi has almost no data entry. "
  "Capture is one button, and the site tag is automatic because the app already guided "
  "them there. Nothing to type, nothing to forget to type. And it works offline, so the "
  "network dropping never stops them."),

 ("7", "H", "“These patients never consented to be in your system.”",
  "Health recordings are sensitive personal information under the Data Privacy Act, and "
  "we treat them that way. The facility is the controller and takes consent at capture; "
  "we are the processor. There are two separate consents — one to record for care, and a "
  "revocable one to train the model, and declining the second changes nothing about their "
  "care. Access is role-scoped, every view is logged, and we have a designated Data "
  "Protection Officer."),

 ("8", "A", "“Detecting a problem is easy. Getting the patient treated is hard.”",
  "Partly we only display, and I would rather say that than claim a referral system we "
  "have not built. What we do: the flag enters a named practitioner’s queue, so every "
  "finding has an owner and a decision comes back to the facility. On approval, "
  "rehabilitation is released. What we do not do is refer, book, or treat. We close "
  "hearing to recording, and recording to review. Not review to treatment."),

 ("9", "H", "“What does the AI actually cost you per facility per month?”",
  "Three hundred fifty pesos, and it is derived in Table 6. Our model is a convolutional "
  "network, not a language model — nineteen recordings in an exam is about a minute and a quarter of "
  "processor time. At twenty patients a day that is about one processor-hour a month. "
  "What actually scales is storage, which is why we need a retention schedule. The "
  "Privacy Act requires one anyway."),

 ("10", "A", "“Is it ninety-seven percent or forty percent?”",
  "Both, measuring different things. Ninety-seven belongs to the published study behind "
  "the architecture we adopted, on a public dataset. Forty is ours — six agreements out "
  "of fifteen recordings, on our own hardware, with no patient-wise split yet. The first "
  "is why we chose this architecture. The second is why we are asking for money."),

 ("11", "A", "“Who runs this after you graduate?”",
  "Three founders: I am CEO, Hared is CTO, and Jarred Paul is COO — that is Figure 10, "
  "and every function has a named owner in Table 14. Our Advisory Board is the continuity mechanism: our research adviser, the consulting clinicians, an "
  "electronics engineer, and the reviewer network. They do not graduate with us. And "
  "incorporation with the SEC is the first activity in Phase 1."),

 ("12", "J", "“Why thirty thousand a year for schools but fifteen hundred a month for "
  "facilities?”",
  "Different units of value. A facility is one exam room; a school is a cohort. At forty "
  "nursing students, thirty thousand a year is seven hundred fifty pesos per student — "
  "against twenty-two thousand for one imported stethoscope that teaches one student at a "
  "time. Schools also budget annually, so it is one purchase order instead of twelve "
  "invoices. And it is the earliest cash we can collect."),

 ("CLOSE", "A", "“If we fund only one team, why yours?”",
  "Because we brought you a number we are not proud of. Most of what you heard today is "
  "projection. Forty percent is not a projection — it is what our device actually did, on "
  "our own hardware, measured by us. We are not asking you to fund an idea. We are asking "
  "you to fund the work of beating it."),
]

RULES = [
 ("The first sentence is the answer.",
  "Never warm up. “That’s a great question” costs four seconds and buys nothing."),
 ("Stop when you have answered.",
  "Silence after a complete answer reads as confidence. Filling it reads as doubt, and "
  "every extra sentence opens a new line of attack."),
 ("One person answers.",
  "Decide the handoff beforehand and say it out loud: “Hared handles the platform side.” "
  "Three people piling onto one question looks like nobody owns it."),
 ("If you do not know, say so and say who would.",
  "“I don’t have that number — it sits with our Regulatory lead and I can follow up” "
  "beats a guess every time. A wrong number is the only answer you cannot take back."),
 ("Never contradict the note from memory.",
  "If a figure sounds wrong, say “the note has that in Table 6, let me not misquote it.” "
  "Being caught contradicting your own document is worse than not recalling it."),
 ("Lead with the weakness when the answer contains one.",
  "A judge who extracts a limitation has learned you conceal. A judge handed it has "
  "learned you measure."),
]

doc = Document()
st = doc.styles["Normal"]
st.font.name, st.font.size = FONT, Pt(11)
st.paragraph_format.space_after = Pt(0)
sec = doc.sections[0]
sec.left_margin = sec.right_margin = Inches(0.9)
sec.top_margin = sec.bottom_margin = Inches(0.7)


def p(after=6, before=0, indent=0.0):
    par = doc.add_paragraph()
    par.paragraph_format.space_after = Pt(after)
    par.paragraph_format.space_before = Pt(before)
    par.paragraph_format.left_indent = Inches(indent)
    par.paragraph_format.line_spacing = 1.14
    par.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return par


def run(par, t, *, size=11, bold=False, italic=False, color=None):
    r = par.add_run(t)
    r.bold, r.italic = bold, italic
    r.font.size, r.font.name = Pt(size), FONT
    if color:
        r.font.color.rgb = color
    return r


run(p(after=2), "Resondi — Spoken Answers", size=20, bold=True, color=INK)
run(p(after=2), "Team Wheezards · Philippine Startup Challenge XI",
    size=11, bold=True, color=GREY)
run(p(after=11), "Say these, do not read them. Each is written for the ear, not the page: "
    "the first sentence answers the question and everything after it is support, so if you "
    "are interrupted after one sentence you have still answered. Timings assume pitch pace, "
    "about 150 words a minute.", size=10, color=GREY)

run(p(after=5), "RULES FOR THE ROOM", size=12, bold=True, color=ROSE)
for head, body in RULES:
    r = p(after=4, indent=0.16)
    run(r, head + "  ", size=10, bold=True, color=SLATE)
    run(r, body, size=10, color=INK)

doc.add_page_break()
run(p(after=9), "THE ANSWERS", size=13.5, bold=True, color=ROSE)

report = []
for tag, who, q, a in CUES:
    words = len(a.split())
    secs = round(words / WPM * 60)
    report.append((tag, words, secs))

    h = p(after=3, before=11)
    run(h, f"{tag}   ", size=10, bold=True, color=ROSE)
    run(h, q, size=11, bold=True, color=SLATE)

    m = p(after=3, indent=0.16)
    run(m, f"{SPEAKER[who]}  ·  {words} words  ·  {secs}s", size=9, bold=True, color=GREY)

    run(p(after=4, indent=0.16), a, size=11, color=INK)

import os
doc.save(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "deliverables", "Resondi-Spoken-Answers.docx")))

bad = [(t, w, s) for t, w, s in report if not (50 <= w <= 85)]
print(f"saved  ·  {len(CUES)} answers")
print(f"  words  {min(w for _, w, _ in report)}–{max(w for _, w, _ in report)}")
print(f"  timing {min(s for *_, s in report)}–{max(s for *_, s in report)}s")
print(f"  total if every one were asked: {sum(s for *_, s in report)}s")
print("  OUT OF RANGE:", bad if bad else "none")
