"""Resondi — judge Q&A preparation sheet.

Answers are written to be spoken in 20-40 seconds and to survive a follow-up.
Where the team has not yet decided something, the entry says so rather than
inventing a specification: an invented number is the one thing that loses a
room permanently.
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

INK   = RGBColor(0x1A, 0x1A, 0x1A)
ROSE  = RGBColor(0xC2, 0x18, 0x5B)
GREY  = RGBColor(0x66, 0x66, 0x66)
SLATE = RGBColor(0x1F, 0x4E, 0x79)
FONT  = "Calibri"

JUDGES = [
 ("Unit economics and scale",
  "Who buys it, at what price, who pays to keep it running, and how it grows past a "
  "handful of sites. Answer with arithmetic, never with adjectives."),
 ("Data ethics and whether the product solves anything",
  "Personal data belonging to people who never signed up, and the harder version: "
  "showing a problem is not the same as fixing it. Expect to be asked what happens "
  "after your software is right."),
 ("Compliance rigour and per-unit AI cost",
  "Lawful basis, notice, restricted access, secure processing — then whether the "
  "subscription survives a heavy user. Have the cost per facility per month ready "
  "as a number you derived, not a number you hope."),
]

# (question, answer, decide) — decide: None, or text the team must settle first
PART1 = [
 ("“Resondi is meant to catch cardiopulmonary disease earlier. But your own test shows "
  "forty percent agreement with reference labels. In a barangay health station with no "
  "doctor, what stops Resondi from becoming the thing that misses the disease?”",
  "Resondi never issues a diagnosis to a patient. The classification is a flag on a "
  "recording, held as Pending Review until a practitioner confirms, modifies or rejects "
  "it. No one is sent home on the model’s word, because the model’s word never leaves "
  "the queue.\n"
  "On the number itself: forty percent is six agreements out of fifteen recordings. "
  "Fifteen is too few to call a rate. We report it because concealing it would be worse, "
  "and because it is the number we are funding ourselves to beat.\n"
  "The failure we fear is the false negative, so clinical validation is powered for "
  "sensitivity rather than overall accuracy, and the reference labels come from clinicians "
  "who never see the model’s output.\n"
  "And the honest gap: the application cannot yet reject a poor recording before analysis. "
  "Until it can, quality control rests with the reviewing practitioner. Closing that is one "
  "of the two things the ₱500,000 buys.", None),

 ("“Have you consulted the Philippine FDA, the Department of Health, or an ethics review "
  "board about deploying this inside public health facilities?”",
  "Not the FDA yet, and I will not pretend otherwise. Here is where we actually stand.\n"
  "Our research adviser at PPCNSHS carries academic supervision and the ethics endorsement "
  "pathway. Four consulting clinicians — three pulmonologists and a pediatrician — do our "
  "labelling, content approval and reference assessment. Ethics committee review is a "
  "funded line inside the ₱120,000 clinical validation, not an afterthought.\n"
  "What we have not done is file with the FDA. Under Administrative Order 2018-0002 a "
  "device is classified A through D on risk, with a notification for the lowest class and "
  "a registration above it. A stethoscope that records sits at the low end; the moment the "
  "software claims to detect disease, the classification rises. That is exactly why the "
  "practitioner holds the diagnosis and the software does not. We are seeking a formal "
  "determination from the CDRRHR rather than assuming our own classification.\n"
  "Our Regulatory and Compliance lead owns that filing and it is a phase milestone with a "
  "name against it. May I ask what you would want to see in place before a pilot?", None),

 ("“Your note gives costs but no revenue. Who buys the units, at what price, who pays for "
  "maintenance after installation, and how does this grow beyond a few barangays?”",
  "Four buyers: rural health units and municipal health offices through their annual "
  "equipment budget, private clinics, and nursing and medical schools.\n"
  "Price: ₱8,000 for the device against a fully loaded unit cost of about ₱4,000. Fifty "
  "percent margin, profitable from the first unit — we are not subsidising hardware out of "
  "subscription. Then ₱1,500 per facility per month for the platform, and ₱30,000 per year "
  "for a school licence.\n"
  "Maintenance is carried by the subscription: platform, support and field service. Device "
  "Maintenance and Field Service is a named role on our organizational chart, not a "
  "promise in a paragraph.\n"
  "On growth — we do not scale barangay by barangay. Procurement is a municipal health "
  "office decision that covers several barangay health stations at once, and one nursing "
  "school puts a cohort of students on the device every term. Commercial Year 1 is ten "
  "facilities and three schools: ₱225,400 in contribution. Year 2 is twenty-five and "
  "seven: ₱510,600, of which ₱450,600 is recurring.", None),

 ("“Existing tools such as Claude or ChatGPT can already do the things you described. "
  "Why does this need to be built?”",
  "Because a general AI cannot hear. Our input is not text — it is a twenty-second "
  "acoustic signal whose diagnostic content sits below three hundred hertz, under the "
  "range a phone microphone is built to pass and actively suppresses. There is no "
  "general-purpose tool you can hold against a patient’s chest.\n"
  "Three layers, none of them substitutable. The chest piece and its acoustic chamber — "
  "a general model has no sensor. The guided placement protocol — that is a clinical "
  "workflow, not a model. And a classifier trained on labelled crackles, wheezes and "
  "murmurs, which a general model has never been trained on and has no clinical labels "
  "for.\n"
  "There is also a regulatory answer. A general assistant is not cleared as a medical "
  "device for this purpose and no practitioner will accept a finding from one. Where a "
  "general model genuinely helps — drafting the plain-language summary a patient reads — "
  "we use it and we do not claim it as our invention.", None),

 ("“Digital maturity is a real barrier. Health workers often go back to doing things "
  "manually because the digital version is too complex. How do you prevent that?”",
  "The reversion risk is the one that worries me most, because what we are competing "
  "with is not a worse app — it is the stethoscope already around their neck, which "
  "takes zero seconds to learn.\n"
  "The structural answer is that Resondi has almost no data entry. Most tools fail in "
  "low-maturity settings because every item must be typed; our capture is one button, "
  "and the site tag is automatic because the application already knows which site it "
  "just guided the user to. There is nothing to key in and nothing to forget to key in.\n"
  "Second, guided placement lowers the skill required rather than adding to it. A health "
  "worker who was unsure where to listen is more capable with the device than without "
  "it, not less.\n"
  "Third, it is offline-first, so the commonest cause of abandonment — the thing stopped "
  "working when the signal dropped — does not occur. Capture never depends on the "
  "network.\n"
  "We would still run an orientation at installation and keep a named person at each "
  "facility as the first point of contact. And we would measure reversion honestly "
  "during the pilot: recordings per facility per week is the number that tells us "
  "whether it is being used or sitting in a drawer.",
  "You have no live-listening path — a user cannot hear through the device the way "
  "they would an ordinary stethoscope. Adding one would be your single strongest "
  "answer to this question, because it makes the device strictly better than what it "
  "replaces. Decide whether it is in scope."),

 ("“These recordings are personal data about patients who never signed up for your "
  "product. What is your consent, access and deletion approach?”",
  "Health recordings are not ordinary personal data — under the Data Privacy Act they "
  "are sensitive personal information, which carries stricter processing conditions and "
  "heavier penalties. We treat them that way.\n"
  "Lawful basis is consent taken at the point of capture by the facility, which is the "
  "personal information controller; we are the processor, operating under a written "
  "agreement. There are two separate consents: one to record as part of care, and a "
  "second, revocable one to let the recording train the model. Declining the second "
  "changes nothing about the care the patient receives.\n"
  "Notice is given verbally at capture and posted at the facility, in the language the "
  "patient actually speaks. Access, correction, erasure and objection are exercised "
  "through the facility, and we supply the mechanism and the turnaround.\n"
  "Access is restricted by role and scoped to the facility — a reviewing practitioner "
  "sees their queue and nothing else — and every view is logged. Recordings are "
  "encrypted in transit and at rest, a Data Protection Officer is designated, which the "
  "Act requires with no size threshold, and registration with the National Privacy "
  "Commission is triggered once we hold the sensitive personal information of a thousand "
  "individuals.",
  "Three things are not yet settled and a judge of this kind will find them: your "
  "retention period, your erasure turnaround in working days, and whether you have a "
  "written data processing agreement a facility could actually sign. Draft the "
  "one-page version before pitch day."),

 ("“Detecting an abnormality is the easy part. Getting the patient treated is the hard "
  "part. Does Resondi help with that, or does it only display the problem?”",
  "Partly it only displays, and I would rather say so than claim a referral system we "
  "have not built.\n"
  "What it does beyond display: a flag is not left in a folder, it enters a named "
  "practitioner’s review queue, so every abnormal finding has an owner and a decision "
  "comes back to the facility. On practitioner approval the platform releases "
  "mode-specific rehabilitation — guided breathing in Lung Mode, and cardiac activity "
  "guidance in Heart Mode once a diagnosis is recorded and the patient cleared. And the "
  "next visit is compared against the same anatomical site, so follow-up has evidence "
  "rather than recollection.\n"
  "What it does not do: refer, book, transport or treat. We have no integration with a "
  "district hospital, no appointment system, and no way to confirm a patient actually "
  "went.\n"
  "So the honest scope is that we close the gap between hearing and recording, and "
  "between recording and review. We do not close the gap between review and treatment. "
  "Referral is the obvious next layer and I would rather name it as a gap than oversell "
  "it.", None),

 ("“Have you calculated your AI processing cost per facility per month? Can ₱1,500 "
  "survive a customer who uses it heavily?”",
  "Yes — ₱350 per facility per month, and it is in Table 5 of the note: "
  "metered cloud, storage and backup at pilot scale, funded for the first twelve months of commercial service by the cloud-operation line in Table 14 and falling as the installed base grows. The other "
  "₱250 is a support and replacement reserve, leaving ₱900 of monthly contribution.\n"
  "The distinction that matters is that our model is a convolutional network, not a "
  "large language model. One full session is twelve recordings — seven lung sites and "
  "five cardiac points. Classifying all twelve is well under a minute of processor "
  "time. At twenty patients a day, which is a busy rural health unit, that is about one "
  "processor-hour per facility per month. Inference is not our cost driver, and heavy "
  "use does not threaten the tier.\n"
  "What does scale is storage, because recordings accumulate and never shrink. The same "
  "facility generates roughly four gigabytes a month; by year five it is holding about a "
  "quarter of a terabyte, and storage alone approaches the whole ₱350.\n"
  "The answer to that is a retention schedule — full-fidelity audio for a defined "
  "window, then compressed or purged except where a practitioner has flagged a recording "
  "for longitudinal comparison. The Data Privacy Act requires a retention limit anyway, "
  "so one policy fixes the cost curve and the compliance obligation at the same time.",
  "Set the retention window, and recompute the storage arithmetic with your real "
  "sample rate and bit depth. The figures above assume 16 kHz, 16-bit mono — if you "
  "record at a higher rate the curve steepens and the ₱350 is reached sooner."),
]

PART2 = [
 ("TECHNICAL AND CLINICAL", [
  ("“How are you different from Eko Health? They already have FDA-cleared cardiac AI.”",
   "Eko is a better device than ours and I will not pretend otherwise — nine FDA "
   "clearances, a three-lead ECG, real capital, the Littmann partnership.\n"
   "Four differences. Their AI comes through the Eko+ subscription, and Eko’s own "
   "supported-country list has no ASEAN member, so a Palawan rural health unit can import "
   "the hardware but cannot license the analysis at any price. Their new CORE 300, launched "
   "on 22 October at USD 199 to 249, is close to our price, so price alone is no longer "
   "our edge and the note says so; but it detects one cardiac finding and has no lung AI. "
   "Their cleared algorithms are cardiac, while pneumonia is the fourth-leading cause of "
   "death in this country. And Eko hands a cardiologist a better chest piece; we guide a "
   "midwife through a lung sequence, which no vendor we reviewed documents.\n"
   "We are not taking Eko’s market. We are serving the facility Eko will never reach.", None),

  ("“Is the ninety-seven percent accuracy figure yours?”",
   "No. That figure belongs to the published study behind the architecture, measured on a "
   "public dataset. Our own model has not been evaluated on a patient-wise split. That "
   "baseline report is the first thing this funding buys.", None),

  ("“Your training data is ICBHI and CirCor — European and American patients. Why would it "
   "work on Filipinos?”",
   "It may not, at first, and that is the point of the design. Those two public datasets "
   "give us an architecture and a starting weight set, not a finished product. What makes "
   "the model ours is the consented, locally labelled Philippine recordings that grow with "
   "every deployment, and a patient-wise split so a single patient never appears in both "
   "training and test.\n"
   "The honest version is that foreign data gets us to a working model and local data gets "
   "us to a trustworthy one. We would rather state that than claim a transfer that has not "
   "been demonstrated.", None),

  ("“You say a stronger signal and sixty-eight percent of recordings rated good. What "
   "about the other thirty-two percent?”",
   "Those are the recordings a practitioner would have to discard — motion, clothing "
   "contact, ambient noise. Today the application cannot detect them before analysis, so "
   "they reach the queue and the reviewing practitioner catches them. That is the single "
   "most important limitation in the whole system, which is why automatic quality "
   "rejection and higher-sensitivity microphones are both funded lines in the ask.", None),

  ("“What if the practitioner just rubber-stamps whatever the AI says?”",
   "That is a real risk and the literature calls it automation bias. Three things work "
   "against it. The practitioner sees the waveform and hears the audio, not only the label. "
   "Confirm, modify and reject are three separate actions rather than one approve button. "
   "And because every review is logged against a reviewer, a pattern of blanket "
   "confirmation is visible to us and to the facility.\n"
   "We have not measured it yet. Measuring reviewer behaviour is part of what the pilot is "
   "for.", None),

  ("“Why hardware at all? Why not just use the phone’s microphone?”",
   "A phone microphone is built to pass human speech, roughly three hundred hertz upward. "
   "Crackles, wheezes and most murmurs live below that, and the phone’s own processing "
   "actively suppresses what we need. A chest piece with an acoustic chamber and a "
   "sensitive element is not a luxury here; without it there is no signal to classify.\n"
   "That is also why we measured about 45 dB against 32 dB for a conventional stethoscope — a 13 dB gap, which is roughly four and a half times the amplitude — "
   "rather than asserting the hardware was necessary.", None),
 ]),

 ("REGULATORY, DATA AND RISK", [
  ("“Where does patient audio live, and who owns it?”",
   "Today recordings sit on the device's MicroSD card, at the facility. Once the funded "
   "platform is built they will also sit in a cloud record tied to the facility, not to us. "
   "The facility is the personal information controller; we are the processor. Patients "
   "consent at the point of capture, and consent for care is separate from consent to let "
   "a recording train the model.\n"
   "We have designated a Data Protection Officer — the Data Privacy Act requires one with "
   "no size threshold — and registration with the National Privacy Commission is triggered "
   "once we hold the sensitive personal information of a thousand individuals. That is a "
   "milestone we have dated rather than discovered.", None),

  ("“Is this a medical device? Will PhilHealth reimburse it?”",
   "On the first: almost certainly yes in the regulatory sense, and we are seeking a "
   "classification determination rather than assuming one. On reimbursement: no, and we "
   "have not built the model on the assumption that it would be. Our revenue comes from the "
   "facility equipment budget and the school licence, both of which exist today. "
   "Reimbursement would be upside, not the plan.",
   "Confirm nobody on the team has told a partner that PhilHealth coverage is coming."),

  ("“What happens when there is no internet?”",
   "The device records to microSD with no phone present at all, and serves its own Wi-Fi, "
   "so a phone or laptop can play recordings back with no internet. The mobile gateway "
   "this funding builds will carry recordings to the platform once it finds a network. "
   "Analysis and practitioner review wait for connectivity, capture does not. That ordering is "
   "deliberate — the places with the worst connectivity are the places with the fewest "
   "doctors.", None),

  ("“What is your actual intellectual property?”",
   "Not the hardware and not the architecture — both are published, and claiming otherwise "
   "would be false. Three things are ours: the consented, locally labelled Philippine "
   "recording set; the guided acquisition protocol with its fixed sites and capture order, "
   "which is what makes recordings comparable between visits and between facilities; and "
   "the review workflow itself.\n"
   "A competitor can buy our bill of materials. They cannot buy four years of Palawan "
   "recordings labelled by the clinicians who took them.",
   "Formalise IP ownership between the three founders and PPCNSHS in writing before "
   "any investor conversation. This is currently unsigned."),
 ]),

 ("TEAM, MONEY AND CONTINUITY", [
  ("“Who runs this after you graduate?”",
   "Three founders: Ahnycca as CEO, over data and model operations, regulatory and "
   "sales; Hared as CTO, over the platform, security and data protection; Jarred Paul as "
   "COO, over production, field service, clinical validation and finance. That is "
   "Figure 10 in the note, and every function in the operations plan has a named owner "
   "in Table 13.\n"
   "The Advisory Board is the continuity mechanism: the research adviser, the consulting "
   "clinicians, an electronics engineer and the practitioner reviewer network sit above the "
   "student team and do not graduate with us. Incorporation with the Securities and "
   "Exchange Commission is the first activity in Phase 1, which moves the asset from a "
   "student project into an entity that can hold it.", None),

  ("“When do we get our money back?”",
   "Commercial Year 1 returns a little over a third of the seed. On a month-by-month "
   "build-up the ₱500,000 is recovered at the twenty-first month of commercial operation — "
   "month 35 from the date of funding, since commercial sale begins at month 15. Investors "
   "take forty percent of net earnings until the ₱500,000 returns, which completes during "
   "the third commercial year, plus an agreed equity stake.\n"
   "We do not claim a twelve-month payback. LGU procurement is annual and subscription "
   "revenue compounds slowly.", None),

  ("“Why is clinical validation ₱120,000?”",
   "Because forty percent agreement is the number we are funding ourselves to beat. "
   "Validation is the largest line in the ask, twenty-four percent, and it covers "
   "prospective evaluation at pilot sites targeting 300 paired recordings, clinician "
   "honoraria for the reference assessment, field transportation across Palawan, and "
   "ethics committee review.", None),

  ("“What stops a bigger company copying this?”",
   "Not the hardware and not the architecture — both are published. The consented, locally "
   "labelled Philippine recordings are, and they grow with every deployment.", None),

  ("“Why ₱1,500 a month for a facility? Where does that number come from?”",
   "It is built from the bottom up, and Table 5 shows the derivation. ₱350 is the "
   "platform operating cost per facility — "
   "metered cloud, storage and backup at pilot scale, funded for the first twelve months of commercial service by the cloud-operation line in Table 14 and falling as the installed base grows. ₱250 is a support and device replacement reserve. "
   "₱900 is contribution. That is a sixty percent contribution margin on a cost base we "
   "can actually name.\n"
   "The ceiling is affordability, not willingness to pay. ₱1,500 a month is ₱18,000 a "
   "year, which sits inside a rural health unit’s maintenance and operating budget and "
   "does not require a special appropriation. Put another way, it is fifty pesos a day — "
   "less than the facility spends on consumables in a morning.\n"
   "And the ₱350 is conservative. It is derived at five facilities; cloud cost is "
   "substantially fixed, so the per-facility figure falls as the installed base grows. "
   "₱900 of contribution is a floor, not a ceiling.", None),

  ("“And why ₱30,000 a year for a school, rather than the same monthly rate?”",
   "Three reasons: the unit of value is different, the budget cycle is different, and "
   "the load is different.\n"
   "A facility is one exam room. A school is a cohort. At forty nursing students a "
   "₱30,000 licence is ₱750 per student per year — against at least ₱30,000 to ₱40,000 "
   "for a single electronic stethoscope in the Philippines, which teaches one student at a time and produces no "
   "record to review in class.\n"
   "Schools budget and procure annually, so an annual licence is one purchase order "
   "rather than twelve invoices fighting the academic cycle. It is also the earliest cash "
   "we can collect, which matters on a ₱500,000 seed.\n"
   "On load: a school at forty students practising twice a week generates about two "
   "gigabytes a month averaged over the year, which is close to a rural health unit "
   "seeing ten patients a day. So the school pays 1.67 times the facility rate for "
   "comparable load and many more users. Contribution is ₱25,800 a year against ₱10,800 "
   "for a facility — which is why schools are the Year 1 priority, alongside the lighter "
   "regulatory burden of a teaching device.",
   "Table 4 states ₱30,000 but nothing in the note derives it the way Table 5 derives "
   "the ₱1,500. Add a short derivation, or this is the first thing an economics judge "
   "pulls on."),

  ("“What does ₱30,000 actually buy a school — how many students, how many campuses?”",
   "One institution, one campus, with the teaching content library and practitioner "
   "review workflow included. Devices are purchased separately at ₱8,000.",
   "This is not settled in your note and it is the obvious follow-up. A university "
   "with three campuses and six hundred nursing students paying ₱30,000 is badly "
   "underpriced. Decide the boundary — per campus, a student cap, or tiers — before "
   "someone signs the first licence.\n"
   "Also worth raising as upside: one device cannot serve forty students. A school "
   "realistically buys three to five units, which is ₱12,000 to ₱20,000 of device "
   "margin per school that your projection deliberately excludes."),

  ("“Why should we fund high school students?”",
   "Because we have built the thing and measured it honestly, including the parts that "
   "came out badly. We are not asking you to fund an idea; we are asking you to fund the "
   "validation of a working system, with a named owner for every function and an "
   "Advisory Board above us who are not students.\n"
   "If the question is really about capability after graduation, the answer is "
   "incorporation in Phase 1 and the Advisory Board.", None),
 ]),
 ("PRICING TIERS AND BUNDLES (backup slides 18–19, Tables 6–7)", [
  ("“You have three tiers. Has anyone agreed to pay ₱2,900 or ₱4,500?”",
   "No, and we say so on the slide: these are proposed prices. Our projections do not "
   "use them. Every facility is modelled at Essential, ₱1,500, so the tiers can only "
   "raise the numbers you have seen, never prop them up. The budget-holder interviews in "
   "Phase 1 include one question built for this: at ₱1,500 you get capture, AI, review "
   "and comparison against the last visit; at ₱2,900 you also get the rehabilitation "
   "module and a monthly report. Which would your facility choose, and why?", None),
  ("“What does Clinical give a facility that Essential does not?”",
   "The rehabilitation module, role-based access with an audit log, and a monthly report "
   "for the health officer. Those are built by the ₱38,000 mobile-application line, so "
   "Clinical and Network exist after the funded build, not today.\n"
   "Comparison of the same chest site across visits is deliberately not on that list. It "
   "is the reason Resondi exists, so it is in Essential, the tier every facility in our "
   "projections is on. It ships with the funded build like the rest.", None),
  ("“You discount the bundles. Where does the discount come from?”",
   "One rule: nothing comes out of the ₱600 per facility per month that pays cloud "
   "operation and the replacement reserve. Essential’s contribution is exactly the ₱900 "
   "our model assumes, so the Starter bundle’s ₱1,500 discount comes out of device "
   "margin only. The device still earns ₱2,500, 38 percent. Clinical and Network have "
   "room above the floor, so part of their discount comes from the subscription.", None),
  ("“A free first month. Isn’t that revenue you lose?”",
   "Not in our numbers. The model already starts a facility’s subscription the month "
   "after it buys the device, so the first month was never counted. The ₱4,000 device "
   "margin is still received on purchase. Offers do not stack: a facility takes the free "
   "month or a prepaid bundle, not both.", None),
  ("“What happens when a free trial ends? Do you bill them automatically?”",
   "No. When the 60-day Clinical trial ends, the facility is asked to choose a tier. "
   "A trial that quietly turns into a charge is the fastest way to lose a rural health "
   "unit’s trust, and for an LGU it would not survive procurement anyway.", None),
  ("“Is ₱4,500 a month realistic for an LGU?”",
   "Network is for a cluster of at least three facilities under one health officer, so "
   "it is a provincial or city budget line, not a single barangay’s. It adds routing to a "
   "remote clinician, a cluster dashboard and DOH and LGU data export. If no cluster buys "
   "it, the plan does not change, because nothing in the projections depends on it.",
   "Know which office in the Provincial Health Office signs a cluster purchase before "
   "you claim this. If you cannot name it, say the tier is untested."),
 ]),
]

FIGS = [
 ("1", "Enclosure VER 2.0, front face and assembly"), ("2", "Hardware block diagram"),
 ("3", "Six-stage workflow"), ("4", "The workflow in the application"),
 ("5", "Auscultation sites and protocol"), ("6", "Planned CNN feature-fusion architecture"),
 ("7", "Value proposition vs alternatives"), ("8", "Business Model Canvas"),
 ("9", "TAM / SAM / SOM"), ("10", "Organizational structure"),
 ("11", "Allocation of the ₱500,000"), ("12", "Cumulative cash contribution"),
]
TABS = [
 ("1", "Technical specification, VER 2.0"), ("2", "Lung Mode sites and landmarks"),
 ("3", "Heart Mode sites and landmarks"), ("4", "Revenue streams and payment basis"),
 ("5", "Unit economics and pricing"), ("6", "Subscription tiers (proposal)"),
 ("7", "Bundles, twelve months prepaid (proposal)"), ("8", "Competitive landscape"),
 ("9", "Device feature comparison"), ("10", "PESTLE analysis"),
 ("11", "Risk register and mitigation"), ("12", "Six-phase implementation plan"),
 ("13", "Operating functions and owners"), ("14", "Allocation of the ₱500,000"),
 ("15", "Detailed line-item breakdown"), ("16", "Investor repayment vs overhead"),
]

PART4 = [
 ("YOUR OWN DOCUMENT — THE TRAPS", [
  ("“Your third objective is to assess recording quality before analysis. Show me.”",
   "It runs today: every capture is graded good, acceptable or poor before it is "
   "classified, and a poor one is repeated. The problem is speed. The check takes about "
   "145 seconds against 4 seconds for the classification, which is fine for a deliberate "
   "review and too slow for every capture in a busy consultation.\n"
   "Cutting that latency, together with noise reduction, is the first deliverable of the "
   "AI development line. Until then, quality control in a busy clinic still rests with the "
   "reviewing practitioner, and we would rather you heard that from us.", None),

  ("“Your note cites ninety-seven percent and your own result is forty percent. Which is "
   "it?”",
   "Both, and they measure different things. Ninety-seven percent belongs to the "
   "published study behind the fusion architecture we plan to adopt, on a public dataset. Forty "
   "percent is ours — six agreements out of fifteen recordings against reference labels, "
   "on our own hardware, with no patient-wise split yet. The first is why we chose this "
   "architecture. The second is why we are asking for money.", None),

  ("“Walk me through the ₱500,000.”",
   "Ten categories. Clinical validation ₱120,000; AI development ₱102,000; contingency "
   "₱50,000; cloud infrastructure and operation ₱48,000; hardware refinement ₱42,000; "
   "production working capital ₱40,000; mobile application ₱38,000; intellectual property "
   "and registration ₱25,000; documentation and compliance ₱20,000; deployment and "
   "marketing ₱15,000. That is Table 14, and Table 15 breaks it to forty-eight line items.\n"
   "The two largest are clinical validation and AI development, which together are "
   "₱222,000 — forty-four percent of the ask — and both exist because of the forty "
   "percent figure.", None),

  ("“Where does ₱225,400 come from?”",
   "Ten facilities and three schools, in commercial Year 1. Each facility gives ₱4,000 of "
   "device margin on acquisition plus ₱900 a month thereafter — ₱14,800 in its first "
   "year, so ₱148,000 across ten. Each school licence gives ₱25,800 after platform cost, "
   "so ₱77,400 across three. ₱148,000 plus ₱77,400 is ₱225,400.\n"
   "School hardware is excluded from that figure, so any school that also buys a device "
   "adds ₱4,000 that is not counted.", None),

  ("“When exactly does the money come back — month 21 or month 35?”",
   "Both, and the distinction matters. Month 21 is the twenty-first month of commercial "
   "operation. Commercial sale begins in month 15 of the implementation plan, so the same "
   "point is month 35 counted from the date of funding. The business recovers the "
   "₱500,000 there; the investor’s forty percent share of net earnings completes "
   "afterwards.\n"
   "If I say month 21 I mean commercial months. If I say month 35 I mean from your "
   "cheque.", None),

  ("“How many sites does the device record, and why that many?”",
   "Seven in Lung Mode — six lung fields plus a tracheal reference at the suprasternal "
   "notch. Five in Heart Mode: aortic, pulmonary, Erb’s point, tricuspid and mitral. "
   "Twelve sites for a full cardiopulmonary session. The protocol calls for twenty "
   "seconds at a lung site and fifteen at a heart point; today's firmware records a fixed "
   "fifteen, so a lung site is taken as two recordings until the interval is made "
   "selectable, a firmware change with no component cost. A nine-site lung protocol, adding an interscapular pair, is "
   "planned but not built.\n"
   "The tracheal reference exists so that a site recording can be compared against the "
   "patient’s own central airway sound rather than an absolute standard.",
   "Checked 31 Oct: the live app still guides nine lung sites (it includes the two "
   "planned interscapular sites), so its counter reads 'of 9' and 'of 14'. Make the change "
   "in app-changes/seven-sites.md before any demo; it then reads 'of 7' and 'of 12', "
   "matching this answer."),

  ("“What is in your note that you would change if you could?”",
   "Three things, and I will name them rather than wait to be asked. Price is no longer "
   "a defensible edge on its own now that the Eko CORE 300 sells at USD 199 to 249; the "
   "note says so in Table 9, but our pitch still leans on price. Our SDG paragraph names "
   "goals without naming targets. And intellectual property ownership between the "
   "founders and the school is described as to be formalized, which means it is not "
   "signed.", None),
 ]),

 ("DEFINE THIS TERM", [
  ("Auscultation", "Listening to the sounds the body makes — heart, lungs, bowel — "
   "usually with a stethoscope, to judge whether an organ is working normally.", None),
  ("Mel-spectrogram", "A picture of how sound energy is distributed across frequency "
   "over time, with the frequency axis warped to the mel scale so that it spaces "
   "frequencies the way human hearing does rather than linearly.", None),
  ("MFCC (mel-frequency cepstral coefficients)",
   "A compact set of numbers describing the shape of a sound’s frequency envelope. It "
   "captures timbre — the character of a sound — in roughly a dozen values instead of a "
   "whole spectrogram.", None),
  ("Chromagram", "A representation that folds all frequencies into pitch classes. It is "
   "borrowed from music analysis and is useful here because murmurs and wheezes carry "
   "pitch structure that a spectrogram alone blurs.", None),
  ("Feature fusion", "Giving the network three different views of the same recording — "
   "mel-spectrogram, MFCC and chromagram — and letting it combine them, rather than "
   "betting the classification on one representation. Three opinions, one verdict. "
   "Planned, not built: the deployed model uses MFCC alone.", None),
  ("Convolutional neural network (CNN)",
   "A model that learns small patterns and builds them into larger ones. Applied here "
   "to a recording’s MFCCs over time, it learns what a crackle or a murmur looks like "
   "in the numbers.", None),
  ("Patient-wise split", "Dividing data so that no single patient appears in both "
   "training and testing. Without it a model can score highly by recognising the patient "
   "rather than the disease, which is the commonest way an audio classifier fools its "
   "own authors.", None),
  ("McNemar’s test", "A statistical test for whether two classifiers differ on the same "
   "set of cases. We use it to show that any improvement over the baseline is real "
   "rather than noise.", None),
  ("Sensitivity vs specificity",
   "Sensitivity is how often the test catches disease that is present — missing it is a "
   "false negative. Specificity is how often it correctly clears someone who is healthy. "
   "Unaided auscultation pools at about thirty-seven percent sensitivity against "
   "eighty-nine percent specificity: it rarely cries wolf, but it misses a great deal.", None),
  ("ICBHI 2017", "A public respiratory sound database — the standard benchmark for lung "
   "sound classification. One of our two training sources.", None),
  ("CirCor DigiScope", "A public phonocardiogram dataset for heart sounds, labelling "
   "murmurs as present, absent or unknown. Our cardiac training source.",
   "Be ready for: “what do you do with the unknown labels?” Decide whether you drop "
   "them, treat them as a third class, or hold them out."),
  ("Crackles and wheezes", "The two abnormal lung sounds we classify. Crackles are "
   "short, discontinuous popping — fluid or collapsed airways reopening. Wheezes are "
   "continuous and musical — air forced through a narrowed airway.", None),
  ("Erb’s point", "The third intercostal space at the left sternal border, where several "
   "heart sounds are audible at once. We record it as a general listening position and "
   "do not classify it to a specific valve.", None),
  ("Store-and-forward", "Capturing data locally and transmitting it later when a network "
   "appears, rather than requiring a live connection. It is why the device records to "
   "MicroSD with no phone present.", None),
  ("Edge, gateway, cloud",
   "The three tiers of our IoT architecture. The edge is the device that senses — the "
   "ESP32 and the microphone — and it is built and working. The gateway is the phone app "
   "that will relay recordings, and the cloud is where storage and the review queue will "
   "live; those two tiers are what this funding builds.", None),
  ("TAM / SAM / SOM", "Total addressable market — everyone who could conceivably buy. "
   "Serviceable available market — those we can actually reach with this product and "
   "these channels. Serviceable obtainable market — what we realistically expect to win "
   "in the period. That is Figure 9.", None),
  ("PESTLE", "A structured scan of the external environment: political, economic, "
   "social, technological, legal and environmental factors. Table 10.", None),
  ("Controller vs processor",
   "Under the Data Privacy Act the personal information controller decides why and how "
   "personal data is processed; the processor acts on the controller’s instructions. The "
   "facility is the controller of its patients’ recordings. We are the processor. The "
   "distinction decides who answers to the patient and who answers to the facility.", None),
  ("Sensitive personal information",
   "A category under the Act that includes health data. It carries stricter processing "
   "conditions and heavier penalties than ordinary personal information. Everything we "
   "record falls inside it.", None),
  ("Gross margin vs contribution",
   "Gross margin is price less the cost of making the thing — ₱4,000 on a ₱8,000 device. "
   "Contribution is what a customer leaves after the ongoing costs of serving them — "
   "₱900 a month after the ₱350 platform cost and the ₱250 reserve.", None),
 ]),

 ("BUSINESS MODEL CANVAS", [
  ("“Give me your value proposition in one sentence.”",
   "Resondi makes every heartbeat and breath a record that can be tracked, compared and "
   "reviewed.", None),
  ("“Who are your customer segments, and which one do you win first?”",
   "Schools first — nursing and medical schools are the earliest revenue and the lightest "
   "regulatory burden, because a teaching device is not making a clinical decision. Then "
   "rural health units and municipal health centres. Growth in commercial Year 2 to 3 is "
   "private clinics, secondary hospitals and LGU cluster deployments, with NGOs and "
   "development agencies as a funded channel.\n"
   "Our users are midwives, nurses and rural health physicians. Patients in isolated "
   "barangays are beneficiaries, reached indirectly through institutional deployment.", None),
  ("“What are your key resources?”",
   "The defensible one is the consented, locally labelled Philippine recording set, which "
   "grows with every deployment and cannot be copied. Technically, the working edge "
   "device and its firmware, the gateway and cloud platform this round builds, plus the trained model and "
   "the clinician-approved content library. Humanly, three founders as CEO, CTO and COO, "
   "our research adviser, three consulting "
   "pulmonologists and a pediatrician, an electronics engineer, and the practitioner "
   "reviewer network.", None),
  ("“Key partners — who actually matters?”",
   "Four groups. Clinical: a partner hospital and the Provincial Health Office, an ethics "
   "committee, and the clinicians who label and approve content. Academic: the PPCNSHS "
   "research programme, and schools as both validation and teaching partners. Industry: "
   "component suppliers, a PCB fabricator and a contract assembler for volume, plus "
   "distributors for reach. Government: LGUs and rural health units as pilot sites, and "
   "the DOH, DOST-PCHRD and DICT.", None),
  ("“Your channels — how does a device actually reach a rural health unit?”",
   "Institutionally first: LGU and DOH procurement, direct sale to clinics, institutional "
   "sale to schools. From commercial Year 2, medical equipment distributors and "
   "donor-funded deployment programmes. Digitally, a product site with specifications and "
   "a request-a-demo path, which matters for facilities we cannot visit. And visibility "
   "through this competition, health-tech expos and nursing conferences.", None),
  ("“What is your cost structure, in one breath?”",
   "One-time: the ₱500,000 seed across ten categories. Marginal: about ₱4,000 fully "
   "loaded per unit once the design is frozen — ₱3,400 of components plus assembly, "
   "calibration and packaging — falling toward ₱3,000 at a hundred units and ₱2,500 at "
   "five hundred through contract assembly. Recurring: ₱48,000 of cloud, covering the "
   "eighteen-month programme and the first twelve months of commercial service, carried at "
   "₱350 per facility and falling as the base grows.", None),
  ("“Which revenue stream is the engine?”",
   "The subscription. Device sale is the entry point and gives fifty percent margin from "
   "the first unit, so hardware never runs at a loss — but it is one-time. The ₱1,500 "
   "monthly platform fee is what compounds, and by commercial Year 2 recurring revenue is "
   "₱450,600 of a ₱510,600 total. The school licence at ₱30,000 a year is the earliest "
   "money through the door.", None),
  ("“What does the canvas admit you cannot do?”",
   "It says so in two places, deliberately. Under value propositions: automated quality "
   "screening runs before analysis but takes about 145 seconds, too slow to use "
   "routinely, so the practitioner is still the main safeguard today. Under "
   "key resources: intellectual property ownership is to be formalized with the school, "
   "which means it is not yet signed. Both are on the canvas because a canvas that hides "
   "them is not a planning document, it is a poster.", None),
 ]),
]

from part5 import PART5

PART3 = [
 ("“What is it, in one sentence?”",
  "A smart stethoscope that guides you to the right spot on the chest, saves what it "
  "hears, flags what sounds abnormal, and sends it to a practitioner to confirm.", None),
 ("“What does it cost?”",
  "₱8,000 for the device, ₱1,500 per month for the facility platform. A school licence is "
  "₱30,000 a year.", None),
 ("“Who holds it — the doctor or the patient?”",
  "Whoever is doing the exam: a nurse, a midwife, a barangay health worker, a student. "
  "That is the whole reason for guided placement. The practitioner comes in afterwards, on "
  "the review side, and may be nowhere near the patient.", None),
 ("“How long does one patient take?”",
  "Seven lung sites, each taken as two fifteen-second recordings in today's firmware, is "
  "three and a half minutes; five cardiac points at fifteen seconds is a minute and a "
  "quarter. Call it five to six minutes including placement — before the quality check, which today adds "
  "about two and a half minutes per recording and is the first thing the AI funding "
  "fixes.", None),
 ("“Does it need internet?”",
  "Not to record. It stores to microSD and serves its own Wi-Fi, so a phone can play "
  "recordings back with no internet at all. Sending them on for practitioner review is "
  "what the funded gateway and platform add.", None),
 ("“Does it replace the doctor?”",
  "No. It cannot and it is not designed to. It gives the doctor something to look at that "
  "did not exist before — the actual sound, from a known site, that they can compare "
  "against the same site next month.", None),
 ("“Do I need training to use it?”",
  "The app walks you to each site and tags it, which is the part that normally needs "
  "training. We would still run a short orientation at installation.",
  "Decide how long orientation takes and who delivers it — Clinical Affairs or Field "
  "Service. A judge may ask what it costs you per facility."),
 ("“How do you clean it between patients?”",
  "The chest piece touches bare skin on every patient, so this matters and we should "
  "answer it precisely.",
  "You have no stated infection-control procedure. Decide the wipe-down protocol and "
  "which disinfectant the housing tolerates before pitch day — a clinician judge will "
  "ask this and it is an easy question to lose."),
 ("“How does it charge, and how long does the battery last?”",
  "State the battery capacity, the charging method and the number of exams per charge.",
  "Fill in your real measured figures. Do not estimate these on stage."),
 ("“Can it get wet? How rugged is it?”",
  "It travels in a bag to barangay health stations, so this is a fair question.",
  "Decide whether you claim any ingress protection. If you have not tested it, say "
  "“not rated, and that is a Phase 2 item” rather than guessing."),
 ("“What happens when it breaks? Who do I call?”",
  "Device Maintenance and Field Service is a named role and the subscription carries "
  "support.",
  "Decide the warranty period and whether it is repair, replace or swap. “The "
  "subscription covers it” will not survive a follow-up without a term."),
 ("“How many recordings can it hold?”",
  "Give the microSD capacity and the resulting number of sessions.",
  "Compute this from your actual sample rate and bit depth, and have the arithmetic "
  "ready."),
 ("“What language is the app in?”",
  "English today.",
  "Decide whether Filipino and Cuyonon or Tagbanua are on the roadmap. In Palawan this "
  "is a real question, not a courtesy."),
 ("“What if the patient is a child, or very large, or has a hairy chest?”",
  "The sites are anatomical landmarks, so they scale with the patient rather than sitting "
  "at fixed distances — and one of our consulting clinicians is a pediatrician, which is "
  "why pediatric sites were reviewed. A hairy chest degrades contact for any stethoscope, "
  "acoustic or electronic; the protocol is firm contact on bare skin.", None),
 ("“Can patients use it at home?”",
  "Not in this version. Everything is designed around a facility and a reviewing "
  "practitioner. Home use would change the regulatory position substantially, so it is "
  "not something we will claim casually.", None),
 ("“How is this different from the stethoscope I already own?”",
  "Yours produces no record. The moment the exam ends, the sound is gone and all that "
  "survives is your memory of it. Ours keeps the sound, knows which site it came from, "
  "and lets you put it next to the same site from last month.", None),
 ("“What if two health workers need it at the same time?”",
  "One device per facility is the Year 1 assumption. A second unit is a second ₱8,000 "
  "purchase. The subscription is per facility, not per device: Essential covers one "
  "device and two users, Clinical three devices and eight users.", None),
]

doc = Document()
st = doc.styles["Normal"]
st.font.name = FONT
st.font.size = Pt(11)
st.paragraph_format.space_after = Pt(0)
sec = doc.sections[0]
sec.left_margin = sec.right_margin = Inches(0.9)
sec.top_margin = sec.bottom_margin = Inches(0.75)


def p(after=6, before=0, indent=0.0):
    par = doc.add_paragraph()
    par.paragraph_format.space_after = Pt(after)
    par.paragraph_format.space_before = Pt(before)
    par.paragraph_format.left_indent = Inches(indent)
    par.paragraph_format.line_spacing = 1.12
    par.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return par


def run(par, text, *, size=11, bold=False, italic=False, color=None):
    r = par.add_run(text)
    r.bold, r.italic = bold, italic
    r.font.size = Pt(size)
    r.font.name = FONT
    if color:
        r.font.color.rgb = color
    return r


def qa(q, a, decide):
    run(p(after=4, before=11), q, size=11, bold=True, color=SLATE)
    for i, block in enumerate(a.split("\n")):
        run(p(after=4, indent=0.16), block, size=10.5, color=INK)
    if decide:
        d = p(after=3, before=2, indent=0.16)
        run(d, "DECIDE BEFORE PITCH DAY.  ", size=9.5, bold=True, color=ROSE)
        run(d, decide, size=9.5, italic=True, color=GREY)


run(p(after=2), "Resondi — Judge Q&A", size=20, bold=True, color=INK)
run(p(after=2), "Team Wheezards · Philippine Startup Challenge XI",
    size=11, bold=True, color=GREY)
hw = p(after=12)
run(hw, "How to use this. ", size=10, bold=True, color=GREY)
run(hw, "Lead with the direct answer, then the reason. Where an answer admits a "
        "weakness, say the weakness first — a judge who extracts it from you has "
        "learned you conceal; a judge who is handed it has learned you measure. Entries "
        "marked in rose are questions you cannot yet answer: settle them before you "
        "walk in, because an invented specification is the one mistake a room does not "
        "forgive.", size=10, color=GREY)

run(p(after=3, before=6), "PART 1 · The questions, in the register the judges are "
    "actually using", size=13.5, bold=True, color=ROSE)
run(p(after=6), "Rewritten from questions this panel put to other teams. Three distinct "
    "lines of attack recur:", size=10, italic=True, color=GREY)
for name, desc in JUDGES:
    jp = p(after=3, indent=0.16)
    run(jp, name + ".  ", size=9.5, bold=True, color=SLATE)
    run(jp, desc, size=9.5, color=GREY)
run(p(after=6), "", size=4)
for q, a, d in PART1:
    qa(q, a, d)

doc.add_page_break()
run(p(after=9), "PART 2 · Hard questions", size=13.5, bold=True, color=ROSE)
for heading, items in PART2:
    run(p(after=4, before=10), heading, size=11, bold=True, color=ROSE)
    for q, a, d in items:
        qa(q, a, d)

doc.add_page_break()
run(p(after=3), "PART 3 · Your own document", size=13.5, bold=True, color=ROSE)
run(p(after=8), "What is in the note, the terms you must be able to define on demand, and "
    "the canvas. The index below is for the night before.", size=10, italic=True,
    color=GREY)

t = doc.add_table(rows=max(len(FIGS), len(TABS)) + 1, cols=4)
t.style = "Table Grid"
t.autofit = False
hdr = ["Fig.", "Shows", "Table", "Shows"]
for j, htxt in enumerate(hdr):
    c = t.cell(0, j).paragraphs[0]
    c.paragraph_format.space_after = Pt(1)
    run(c, htxt, size=9, bold=True, color=INK)
for i in range(max(len(FIGS), len(TABS))):
    vals = (list(FIGS[i]) if i < len(FIGS) else ["", ""]) + \
           (list(TABS[i]) if i < len(TABS) else ["", ""])
    for j, v in enumerate(vals):
        c = t.cell(i + 1, j).paragraphs[0]
        c.paragraph_format.space_after = Pt(1)
        run(c, v, size=9, color=INK)
for row in t.rows:
    for j, w in enumerate((Inches(0.42), Inches(2.5), Inches(0.52), Inches(2.5))):
        row.cells[j].width = w
run(p(after=4, before=2), "", size=4)

for heading, items in PART4:
    run(p(after=4, before=10), heading, size=11, bold=True, color=ROSE)
    for q, a, d in items:
        qa(q, a, d)

doc.add_page_break()
run(p(after=3), "PART 4 · Going deeper", size=13.5, bold=True, color=ROSE)
run(p(after=8), "Engineering choices, research method, liability, financial depth, the team "
    "under pressure, and impact. Most of the unanswered items in this sheet are here.",
    size=10, italic=True, color=GREY)
for heading, items in PART5:
    run(p(after=4, before=10), heading, size=11, bold=True, color=ROSE)
    for q, a, d in items:
        qa(q, a, d)

doc.add_page_break()
run(p(after=3), "PART 5 · Common-sense questions", size=13.5, bold=True, color=ROSE)
run(p(after=9), "Asked by non-technical judges, procurement officers and the clinician "
    "who will actually hold the device. Losing one of these costs more credibility than "
    "losing a technical question.", size=10, italic=True, color=GREY)
for q, a, d in PART3:
    qa(q, a, d)

import os
OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "deliverables", "Resondi-Judge-QA.docx"))
doc.save(OUT)

grouped = PART2 + PART4 + PART5
flagged = [q for q, _, d in PART1 + PART3 if d] + \
          [q for _, items in grouped for q, _, d in items if d]
total = len(PART1) + len(PART3) + sum(len(i) for _, i in grouped)
print(f"saved {OUT}\n  {total} questions, {len(flagged)} flagged DECIDE")
