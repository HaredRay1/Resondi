"""Build final/20-Resondi-Tech-QA.docx: spoken answers to technical judge questions (rose theme)."""
import os
from docx import Document
from docx.shared import Pt, RGBColor, Cm

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "final", "20-Resondi-Tech-QA.docx")
ROSE, PLUM, GREY = RGBColor(0xE9, 0x1E, 0x76), RGBColor(0x8E, 0x2A, 0x52), RGBColor(0x9E, 0x88, 0x92)

QA = [
 ("The device", [
  ("Walk us through how the device works, end to end.", "Hared",
   "The chest piece carries a digital microphone. It sends the sound straight to an ESP32 microcontroller, which saves a 15-second recording as a WAV file on a memory card. The same chip creates its own Wi-Fi network and serves a web page, so any phone can start a recording and play it back, with no internet and no app."),
  ("Why an ESP32?", "Jarred",
   "It's cheap, low-power, and has Wi-Fi and a digital audio interface built in. One chip does the recording, the storage and the phone connection, which keeps the parts cost at 2,775 pesos."),
  ("Why a MEMS microphone with no preamplifier?", "Hared",
   "The INMP441 converts sound to digital right at the microphone. A digital signal doesn't pick up electrical noise along the wire the way an analogue one does, so we don't need a separate preamplifier."),
  ("Why record at 16 kilohertz?", "Hared",
   "Heart sounds sit mostly below 500 hertz, and the wheezes and crackles we classify fall within the range a 16-kilohertz recording captures, which is up to 8 kilohertz. Going higher would only make files bigger. Each 15-second recording is about 480 kilobytes."),
  ("What if the phone disconnects in the middle of a recording?", "Hared",
   "The device makes and saves the recording itself; the phone only presses start and plays it back. If the Wi-Fi drops, reconnect and refresh, and the file is on the card."),
  ("How long does the battery last?", "Jarred",
   "By our estimate, about 30 hours of use on the 10,000 milliamp-hour battery, which is several clinic days. Measuring the exact figure is part of our device testing."),
  ("Why seven lung sites, always in the same order?", "Hared",
   "Because comparison only works if recording one and recording ten come from the same spot. Research shows multi-site recording also helps the AI: in one study of 2,402 recordings, accuracy rose from about 79 percent at one site to about 92 percent across four."),
  ("How did you measure the 13-decibel signal advantage?", "Hared",
   "In our field test, Resondi picked up 45 decibels against 32 on a conventional stethoscope. That's an indicative margin, not a lab signal-to-noise ratio, because the two weren't measured against a common reference. A controlled comparison is part of validation."),
 ]),
 ("The AI", [
  ("How does the AI actually work?", "Hared",
   "It cuts the recording into one-second windows and turns each into MFCCs, a picture of the sound's frequencies that mimics human hearing. A small neural network scores each window as normal, wheeze, crackle, or wheeze with crackle. We average the windows into one suggestion for the recording, which a practitioner then confirms."),
  ("Does the AI run on the device or in the cloud?", "Hared",
   "In the review platform, not on the device. That keeps the device cheap and lets us update the model for every user at once, without recalling a single unit."),
  ("What data did you train it on?", "Hared",
   "Two public databases. ICBHI 2017: 920 adult recordings from 126 patients, labelled breath by breath, split by patient so test patients were never seen in training. And SPRSound: Asian children's recordings from Shanghai, labelled by eleven paediatric physicians, which we added to training."),
  ("How accurate is it?", "Hared",
   "Tested on all 126 patients, each by a model that never saw them, our best model scores 40 percent balanced accuracy, against 25 percent by chance and 34 percent for our simpler design. That gain is statistically significant. On unseen children it scores about 56 percent. It's a real step forward, but still a starting point, not a product claim."),
  ("Is that best model the one in your app?", "Hared",
   "Not yet. The app runs our earlier model, which scores 33.5 percent. The new fusion model still has to be converted for the app; that's part of the AI development we're funding."),
  ("Why doesn't it work well on your own device?", "Hared",
   "Because it learned from hospital stethoscopes, and our microphone sounds different. When we tested it on our device recordings, its scores were close to random. We checked that it wasn't just loudness: adjusting the volume changed nothing. The fix is to train it on recordings made with Resondi."),
  ("Did you try more advanced models?", "Hared",
   "Yes, fifteen designs in all. Our best is a three-branch fusion network that combines three ways of picturing a sound: MFCC, a spectrogram and a chromagram. On adult data alone it was not clearly better; with the children's data added, it became our best. That told us the biggest gains come from more and more varied data, not from a cleverer network."),
  ("How will you make it better?", "Hared",
   "Four steps: record Filipino patients on our own device at the seven sites; have two clinicians label every breath without seeing the AI's answer; train with added noise so it survives a real ward; and screen out poor recordings before the AI ever sees them."),
  ("Can the AI analyse heart sounds?", "Hared",
   "Not yet. Heart Mode records and stores heart sounds today. The funded work will identify S1 and S2 and detect whether a murmur is present and when it occurs, using the CirCor DigiScope database of 5,282 recordings from 1,568 patients. We won't promise S3 or S4, because no public dataset labels them well enough."),
  ("How does the AI explain its answer?", "Hared",
   "The practitioner always gets the original recording alongside the suggestion, so they listen for themselves. The AI points to what to listen for; the human makes the call."),
  ("Other studies report 95 to 99 percent. Why is yours lower?", "Hared",
   "Because we tested honestly. Those studies usually classify the patient's diagnosis and split recordings at random, so the same patient appears in training and testing. When we kept test patients completely unseen, our best model scored 40 percent. We'd rather build on a true number than a flattering one."),
  ("Your earlier report said 71 to 84 percent. Which is true?", "Hared",
   "The lower one. We found our own mistake: the same patients' audio was in both training and testing, so the model learned who the patient was, not what the sound was. We rebuilt it with patients kept completely separate. We'd rather correct ourselves in front of you than have you find it."),
  ("Your AI only matched 40 percent in the field. Isn't that a failure?", "Hared",
   "It's a starting point, and we chose to show it. It matched the reference on 6 of 15 field recordings, against 25 percent by chance. With only 15 recordings, that could still be luck. Retraining on Filipino patients recorded with Resondi is exactly what this funding buys."),
 ]),
 ("Platform, data and safety", [
  ("How does a recording get from the device to the doctor?", "Hared",
   "Today, on the memory card: a health worker copies the files and uploads them to the patient's record on our platform. That's the one link we haven't automated. Both ends work; the gateway that sends recordings automatically is part of what this round funds."),
  ("What is your platform built on?", "Hared",
   "It's a hosted web app built on Base44. It stores recordings against each patient, runs the classifier, and shows results to a practitioner for confirmation. Building on a hosted platform let three students ship a working system fast; if we outgrow it, the data and the model can move."),
  ("How do you keep patient data safe?", "Hared",
   "Recordings stay on the device until they're uploaded to our own platform, not to a server abroad. Access is by account, and I'm the designated Data Protection Officer under the Data Privacy Act. Encryption at rest and in transit, and role-based access with an audit log, are part of the funded build, and we register with the National Privacy Commission before we hold a thousand patients' data."),
  ("What is the recording-quality check, and why does it take 145 seconds?", "Hared",
   "Before the AI looks at a recording, an automatic check rejects one that's too noisy or too faint. It works, but it's slow, about 145 seconds per recording, which is why a full exam takes about 34 minutes. Making it fast is the first technical milestone we fund."),
  ("What happens in a noisy ward?", "Hared",
   "Honestly, today's model struggles: when we added noise in testing, its accuracy fell to chance. The fix is training with real ward and community noise, plus the quality check rejecting bad recordings before analysis. In our field test, we measured background noise of 24, 35 and 42 decibels across a quiet room, a ward and a community setting."),
  ("How do you stop a wrong AI answer from hurting a patient?", "Hared",
   "Three safeguards. The AI describes a sound pattern, never a disease. A poor recording is screened out before analysis. And no result reaches a patient until a licensed practitioner has listened and confirmed it, on every subscription tier."),
  ("How will you validate it clinically?", "Hared",
   "A prospective study in our partner facilities: practitioners assess the same patients independently, without seeing the AI's answer, and we measure agreement with Cohen's kappa and a confusion matrix, plus recording quality and performance under real noise. Blinding will be recorded this time."),
  ("Was the field test blinded?", "Hared",
   "Blinding wasn't recorded, so we don't claim it. Our validation protocol requires it, and records it."),
  ("How do you update the model once devices are in the field?", "Hared",
   "The AI lives in the platform, so a new model reaches every facility the moment we publish it. No device needs to be returned, and every update is version-tagged so we know which model produced which result."),
 ]),
]

AVOID = ["\"Diagnoses\", \"detects disease\", \"replaces the doctor\"",
         "\"Clinically proven\" or \"validated\" for the AI",
         "71, 83 or 84 percent as performance",
         "That the app already runs the 40 percent model",
         "\"No one else does this\" (say \"no vendor we reviewed documents this\")"]

doc = Document()
for s in doc.sections:
    s.left_margin = s.right_margin = Cm(2.2); s.top_margin = s.bottom_margin = Cm(2)
st = doc.styles["Normal"]; st.font.name, st.font.size = "Poppins", Pt(10.5)


def run(p, text, size=None, color=None, bold=False, italic=False):
    r = p.add_run(text); r.bold, r.italic = bold, italic
    if size: r.font.size = Pt(size)
    if color: r.font.color.rgb = color
    return r


run(doc.add_paragraph(), "Resondi: Technical Q&A", 22, PLUM, True)
p = doc.add_paragraph(); run(p, "Spoken answers for judges. Lead with the plain answer; add the technical detail only if they ask for more.", 10, GREY)
n = 0
for sec, items in QA:
    h = doc.add_paragraph(); h.paragraph_format.space_before = Pt(14); run(h, sec.upper(), 11, ROSE, True)
    for q, who, a in items:
        n += 1
        p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(2)
        run(p, f"{n}. {q}", 11, PLUM, True); run(p, f"   {who}", 9, GREY, italic=True)
        p = doc.add_paragraph(); p.paragraph_format.left_indent = Cm(0.6); p.paragraph_format.line_spacing = 1.25
        run(p, f"“{a}”", 10.5)
h = doc.add_paragraph(); h.paragraph_format.space_before = Pt(14); run(h, "NEVER SAY", 11, ROSE, True)
for t in AVOID:
    run(doc.add_paragraph(style="List Bullet"), t, 10)
doc.save(OUT)
print("wrote", OUT, n, "questions")
