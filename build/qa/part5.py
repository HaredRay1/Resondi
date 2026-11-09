PART5 = [
 ("HARDWARE AND ENGINEERING CHOICES", [
  ("“Why the ESP32? Why not a Raspberry Pi or something more capable?”",
   "Because the edge tier does not need to be capable — it samples the microphone, writes "
   "to MicroSD and serves its own Wi-Fi web page. The classifier runs in the Resondi "
   "application, not on the device. The ESP32 has Wi-Fi built in, reads the INMP441 "
   "microphone digitally over I²S, runs from the unit's 10,000 mAh battery, and is "
   "available from local suppliers at a price that keeps the unit at about ₱4,000 fully "
   "loaded. A Pi costs more, draws far more power, and buys us nothing we use.", None),

  ("“Why a MEMS microphone rather than an electret?”",
   "Unit-to-unit consistency. Our entire premise is that a recording taken today can be "
   "compared against the same site months later, possibly on a different device. Electret "
   "capsules vary noticeably between units, which would put drift into exactly the "
   "comparison we are selling. MEMS parts hold a far tighter response spread, and they "
   "interface cleanly with the microcontroller.", None),

  ("“Why Wi-Fi rather than Bluetooth?”",
   "Because the device is its own access point. It raises a Wi-Fi network and serves the "
   "Resondi web page itself, so any phone, tablet or laptop with a browser can start a "
   "recording and play it back without installing anything, without pairing, and without "
   "a router or internet. That matters in a barangay health station that has neither. "
   "Bluetooth would have forced a native app onto every phone before anyone heard a "
   "recording. The cost is power, which is why the unit carries a 10,000 mAh battery.", None),

  ("“A 3D-printed case, in a tropical climate?”",
   "It is printed in PLA, and I will not pretend that is a field material. PLA softens "
   "around sixty degrees, which a vehicle parked in the sun here can reach. It is the "
   "right material for iterating quickly on a prototype, and I would not ship it. A "
   "heat-resistant enclosure is one of the reasons hardware refinement is ₱42,000 of the ask, and why "
   "the volume plan moves to silicone vacuum casting — which also takes the unit cost from "
   "about ₱4,000 toward ₱3,000.", None),

  ("“Philippine mains is sixty hertz. Heart sounds run from twenty to two hundred hertz. "
   "How do you keep hum out of the cardiac band?”",
   "Two ways. The device runs on battery with no mains connection during capture, which "
   "removes the commonest coupling path. And interference that still appears is handled "
   "in filtering before classification.",
   "Confirm what your firmware actually does here — a notch filter at 60 Hz, a "
   "high-pass, or nothing. This question comes from an electronics judge and a vague "
   "answer is worse than “we high-pass at X hertz.”"),

  ("“What sample rate and bit depth do you record at, and why?”",
   "State the figure and tie it to the content: lung sounds carry useful information to "
   "roughly one kilohertz and heart sounds much lower, so the rate must comfortably "
   "exceed twice that.",
   "Your note never states the sample rate or bit depth. Fill it in — it also drives "
   "the storage arithmetic behind your ₱350 platform cost and the MicroSD capacity "
   "question."),

  ("“What happens if the device fails partway through an examination?”",
   "Each site is written to MicroSD as it completes, so a failure costs the site in "
   "progress rather than the session. The user re-records that one site.",
   "Confirm whether the firmware has a watchdog and whether a partial file is "
   "recoverable. “It just works” is not an answer to a hardware judge."),
 ]),

 ("RESEARCH METHOD AND STATISTICS", [
  ("“Forty percent agreement on a two-class problem is worse than flipping a coin. "
   "Explain that.”",
   "If the comparison were binary you would be right, and I would not defend it. The "
   "more important point is that fifteen samples cannot establish a rate in either "
   "direction. The ninety-five percent confidence interval on six out of fifteen runs "
   "from about twenty percent to sixty-four percent — forty-four points wide. That "
   "interval contains chance and it contains a usable classifier, which is exactly why we "
   "are not claiming a performance figure and are asking you to fund the study that "
   "produces one.",
   "You must know how many classes were compared before you answer this. Binary "
   "gives a kappa of −0.20, three classes +0.10, four classes +0.20. This is the single "
   "most dangerous question in the set and the answer changes completely with that "
   "number. Find it in your raw results tonight."),

  ("“Why report raw agreement rather than Cohen’s kappa?”",
   "Because raw agreement is the honest headline for a sample this small, and kappa on "
   "fifteen paired observations is not a stable statistic. The planned validation reports "
   "kappa alongside sensitivity and specificity on a patient-wise split, and uses "
   "McNemar’s test for the comparison against the baseline.", None),

  ("“What is your research design?”",
   "Developmental, with a descriptive evaluation component: we built an instrument and "
   "then characterised it — signal acquisition against a conventional stethoscope, "
   "recording clarity across three ambient conditions, end-user acceptance, and "
   "classification agreement against reference labels.", None),

  ("“How were your twenty-seven acceptance respondents selected?”",
   "State the sampling method and the inclusion criteria. The composition was 13 "
   "patients, 13 general respondents and one health practitioner.",
   "Your note gives the number but not the method. Purposive or convenience sampling "
   "is perfectly acceptable at this stage — being unable to name which is not. Be "
   "ready for the follow-up: only one practitioner responded, so the instrument's "
   "questions about institutional resources and professional practice were largely "
   "answered by people those questions do not apply to. Volunteer that before it is "
   "found."),

  ("“Your questionnaire has no results for intention to use. Why?”",
   "Three behavioural-intention items and all the open-ended questions returned no "
   "responses — respondents did not reach that page of the form. We report the four "
   "constructs that have data and we do not report intention to adopt.",
   "This is a real gap and it is the most interesting part of an acceptance study. "
   "Do not improvise a number. Say it was lost to a form-design fault, and that it is "
   "the first thing the next round fixes."),

  ("“Why UTAUT rather than the dimensions in your earlier draft?”",
   "The instrument we actually administered is adapted from the Unified Theory of "
   "Acceptance and Use of Technology, so we report it against that framework rather "
   "than against labels the questionnaire never measured.",
   "An earlier draft described five dimensions — user-friendliness, usability, "
   "durability, functionality, community impact — that no item in the questionnaire "
   "asks about. Correcting it to the instrument you ran is the honest move and a "
   "stronger one: UTAUT is an established, citable framework."),

  ("“Several of your items ask about ISO compliance. Is the device certified?”",
   "No. Those items measure how much regulatory conformity would influence a user's "
   "confidence, not conformity we have achieved. The device is pre-certification, and "
   "FDA registration is funded in the requested budget.",
   "This is the sharpest question in the acceptance set. Five of the twelve Likert "
   "items reference ISO standards the device does not yet meet. Frame them as "
   "willingness-to-adopt drivers, never as evidence of compliance."),

  ("“Under what ethical approval did you record three patients at a private hospital?”",
   "The note says an attending physician reviewed the procedure and consented to it, "
   "which is clinical supervision.",
   "Clinical supervision is not the same as ethics committee approval, and a research "
   "judge knows the difference. Establish exactly what approval existed, in writing, "
   "and be precise about it. If it was supervision only, say so and point to the ethics "
   "review funded in the validation line."),

  ("“What are the limitations of your study?”",
   "Four, and I would rather list them than be asked. Fifteen paired recordings is too "
   "few to establish classification performance. The model has not been evaluated on a "
   "patient-wise split. The training data is European and American, not Filipino. And the "
   "system cannot yet reject a poor recording before analysis, so quality control rests "
   "with the reviewing practitioner.", None),
 ]),

 ("LIABILITY AND HARM", [
  ("“A patient is harmed after Resondi returns a normal result. Who is liable?”",
   "Clinical responsibility stays with the licensed practitioner, because the diagnosis "
   "is theirs — our software produces a flag on a recording and never a finding to a "
   "patient. What would sit with us is product liability if the device itself were "
   "defective: a microphone that failed silently, or a recording attributed to the wrong "
   "site.",
   "You carry no product liability insurance and there is no written limitation of "
   "liability in any customer agreement, because there is no customer agreement. Both "
   "belong in Phase 1 alongside incorporation."),

  ("“Is a device that gives false reassurance worse than no device at all?”",
   "It would be, and that is the risk we have designed the whole workflow around. No "
   "result reaches a patient unreviewed, and the review is by a licensed practitioner who "
   "sees the waveform and hears the audio rather than only a label. If we ever shipped a "
   "version that returned a result directly to a patient, your question would become "
   "unanswerable — which is why we will not.", None),

  ("“Should high school students be handling patient health data at all?”",
   "Not unsupervised, and we are not. The facility is the personal information "
   "controller and holds the relationship with the patient; we are the processor. Our "
   "research adviser and the Advisory Board sit above the student team, a Data "
   "Protection Officer is designated, and incorporation in Phase 1 moves this into an "
   "entity with accountable officers rather than a group of minors.", None),

  ("“Your app’s dashboard currently describes the model in terms your results do not "
   "support. Why?”",
   "Because the wording was written before we had our own measurement and it has not "
   "been corrected. It overstates validation and it is being changed. I would rather tell "
   "you that than have you find it in the build.",
   "Fix the dashboard disclaimer before anyone opens the app. A judge who downloads "
   "it and finds a validation claim you disowned on stage is the worst version of this."),
 ]),

 ("FINANCIAL DEPTH", [
  ("“What is your customer acquisition cost?”",
   "In cash, about ₱1,150 per customer in commercial Year 1: the ₱15,000 deployment and "
   "marketing line across ten facilities and three schools. That excludes our own time, "
   "because we are unpaid, and costed at any fair rate our time would be the larger part. "
   "The number that matters is payback: a facility returns ₱14,800 of contribution in its "
   "first year, so even at ten times that acquisition cost it pays for itself within the year.",
   "DRAFTED 30 Oct from finpack/model.py. Confirm the figures and the wording, and agree "
   "as a team that you are comfortable saying your time is unpaid."),

  ("“What churn rate have you assumed?”",
   "The base case assumes every Year 1 facility renews, and we say so. We tested it: if "
   "one in ten Year 1 facilities leaves at renewal, Year 2 contribution falls by ₱10,800; "
   "if one in five leaves, by ₱21,600. In both cases the seed is still recovered in the "
   "twenty-first commercial month, because the school licences and new facilities carry "
   "Year 2. Churn would bite in Year 3, which is why practitioner review is built in as the "
   "reason to stay.",
   "DRAFTED 30 Oct from finpack/model.py (renewal churn applied at commercial month 13). "
   "Confirm before pitch day; the 0% base case is still the one in the concept note."),

  ("“What equity stake are you offering for the ₱500,000?”",
   "Alongside forty percent of net earnings until the ₱500,000 is returned, an agreed "
   "equity stake.",
   "“An agreed equity stake” is not a term, it is a placeholder, and it is the "
   "question any investor asks first. Decide a number or a range before you present."),

  ("“Why forty percent of net earnings, and not thirty or fifty?”",
   "Because it returns the seed without starving the business of the working capital it "
   "needs for the next batch. The business recovers ₱500,000 from operations by "
   "commercial month 21. The investor’s forty percent share returns it during the third "
   "commercial year: month 33 if overhead is nil, month 36 at fifteen percent. Above that, "
   "forty percent does not return it within three years, and we would rather say so and "
   "discuss a larger share or a priced equity stake than claim a date the model does not "
   "produce.", None),

  ("“What happens to your unit cost if component prices rise or a part goes "
   "end-of-life?”",
   "The design deliberately uses widely available parts rather than anything "
   "single-sourced, which is why we chose the ESP32 and a common MEMS part over something "
   "more specialised. A price rise compresses the fifty percent margin rather than "
   "breaking the model, and the ₱40,000 of production working capital lets us buy a batch "
   "ahead when a part looks unstable.", None),

  ("“What is your monthly burn, and what is your runway?”",
   "Through the eighteen-month programme the team is unpaid and the spend is the "
   "₱500,000 itself, so burn is programme spend rather than payroll. The first salaried "
   "hires are triggered after commercial operation begins.",
   "DRAFTED 30 Oct. Say it as: about ₱27,800 a month on average across eighteen months, "
   "heaviest from month 4 to month 16 when AI development, the pilot and clinical "
   "validation overlap. ₱50,000 is contingency that is only released against a documented "
   "overrun, and ₱18,000 of cloud is spent in the first commercial year, after the "
   "programme. Runway is the programme itself: funds are released phase by phase."),
 ]),

 ("THE TEAM UNDER STRESS", [
  ("“There are three of you. Who decides when you disagree?”",
   "The CEO decides, and the founder who owns the area makes the call inside it. Where it touches clinical content or ethics, it goes to the Advisory Board. "
   "We would rather name a decision-maker than claim we always agree.", None),

  ("“What happens if one of you leaves?”",
   "Every function has a named owner in Table 14, and with three founders each of us "
   "holds several, so the other two can cover any one role for a time. The one "
   "genuine single point of failure is model and data operations, which sits with me.",
   "Decide who your backup is on the model side, and say the name."),

  ("“How many hours a week can students actually give this?”",
   "Be specific and do not inflate it.",
   "Settle a real figure as a team. An inflated number is caught instantly by anyone "
   "who has supervised students, and an honest small number paired with the "
   "incorporation plan is far more convincing."),

  ("“What happens when you all go to different universities?”",
   "Incorporation is the answer rather than good intentions. Once the company exists it "
   "holds the asset, the Advisory Board does not graduate, and roles can be filled by "
   "hire rather than by whoever is still enrolled.", None),
 ]),

 ("IMPACT", [
  ("“How many lives will this save?”",
   "I cannot answer that and I will not estimate it. No device saves lives on its own — "
   "it changes whether a finding is detected, recorded and acted on, and the clinical "
   "outcome depends on what happens after that. Claiming a mortality figure from fifteen "
   "recordings would be the least credible thing I could say today.", None),

  ("“Then what will you actually measure?”",
   "Four things, all of them countable: recordings captured per facility per week, which "
   "tells us whether the device is used or in a drawer; proportion of abnormal flags "
   "reviewed by a practitioner, and how quickly; proportion of patients with a second "
   "recording at the same site, which is the rehabilitation loop working; and "
   "classification agreement against clinician labels on a proper split.", None),

  ("“Will this reach the poorest patients, or only facilities that can afford it?”",
   "Patients pay nothing — the facility carries the cost, which is the whole reason we "
   "price to a rural health unit budget rather than to a private clinic’s. Where even "
   "that is out of reach, the donor-funded deployment stream exists to place devices "
   "through NGOs and development agencies. I would not claim it reaches everyone. It "
   "reaches whoever the public health system already reaches, with better instruments.", None),
 ]),
]
