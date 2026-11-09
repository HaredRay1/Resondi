# RESONDI — Project Handoff

> **What this is.** The state of the Resondi project as of **2 November 2026**, written so a new Claude Code session can pick the work up cold. It **supersedes** `handoff2/RESONDI-HANDOFF.md` (30 Oct) and `handoff/RESONDI-HANDOFF.md` (27 Oct). Those two stay for provenance; **where this file disagrees with either of them, this file wins.**
>
> **How to use it.** Put this file in the project root as `CLAUDE.md`, unzip the workspace next to it, then say: *"Read CLAUDE.md, then continue from the Open Work list."*
>
> **Read Part A and §C0 before changing anything.** §C0 lists the four traps that have each cost a session's work once already.

---

# PART A — WHAT IS TRUE NOW

## A1. The project in one paragraph

**Resondi** is an AI-assisted smart stethoscope and mobile monitoring platform. An ESP32-based digital stethoscope records lung and heart sounds at guided, standardized chest sites. A mobile-first app (built on Base44) tags each recording by site, stores it, and runs a CNN that sorts lung sounds into four patterns. A rule layer turns the pattern across chest zones into a literature-backed *possibility*, never a diagnosis, and a practitioner confirms, modifies or rejects every result. Longitudinal comparison at the same site across visits supports rehabilitation tracking. The team is **Team Wheezards**, from **Puerto Princesa City National Science High School (PPCNSHS)**, Palawan. They **won the DICT Philippine Startup Challenge XI regional round on 26 October 2026**; **nationals are next and are what every deliverable is being prepared for.** It is also a school research paper.

**The user is Ahnycca Krish N. Malimban**, Managing Director. She works on **Windows** — write PowerShell, not bash (§C0.3).

## A2. Names

| Era | Name |
|---|---|
| Earliest research | SmartSteth (the Edge Impulse project is still called "SmartStethoscope") |
| 8–25 Oct 2026 | Ausculta |
| 26–27 Oct 2026 | Auscora (short-lived) |
| **Now** | **RESONDI** |

When renaming, replace only the product name. **Never** touch *auscultation* / *auscultatory* / *auscultate*. Safe pattern:

```python
PAT = re.compile(r"\b(AUSCULTA|Ausculta|ausculta|AUSCORA|Auscora|auscora)\b")
def sub(m):
    w = m.group(1)
    return "RESONDI" if w.isupper() else ("Resondi" if w[0].isupper() else "resondi")
```

Still carrying the old name: the Base44 app's meta tags (canonical domain still reads `ausculta.base44.app` though the site serves at `resondi.base44.app`), the Edge Impulse project, and the 83-page research paper PDF.

## A3. People

PSC rules allow **3 students + 1 mentor**.

- **Founders (the registered startup team):** Ahnycca Krish N. Malimban (Chief Executive Officer; data and model operations), Hared Ray Cabrera (Chief Technology Officer; platform operations and security), Jarred Paul Llacuna (Chief Operating Officer; production and supply chain). These three are marked `Founder ·` in Figure 10 and are the pitch presenters (A / H / J in the script).
- **Mentor:** the research adviser from the PPCNSHS research programme. **Name still a placeholder in the deck.**
- **Seven contributing members**, shown in Figure 10 without the Founder marker, described as positions staffed as the business grows: David James Segay (application development), Arvin Rogel Coronado (product and AI), Paul Brent Gabayan (device maintenance and field service), Andee Marie Biaco (clinical affairs), Chesca Jomaicha Trajano (regulatory, compliance, Data Protection Officer), Angela Naverra (sales and customer success), Jared Zai Elli (finance and administration).
- **"Advisory Board"**, never "Board of Regents" (that is a state university's governing body).

> **Open:** nobody has confirmed with DICT MIMAROPA whether contributors beyond the three founders are permitted. The wording is safe either way, but the user should confirm.

## A4. Standing instructions from the user

1. **"do not edit directly, provide the revised part here."** Applies to the user's own Google Docs and the 83-page paper. Give pasteable text; never write to their documents. Documents *Claude built* (concept note, script, Q&A, IMRaD) are edited and rebuilt directly.
2. **Code in Python and Rust.**
3. **Keep the Resondi rose theme.** Poppins / `#FFF5F9` background / `#E91E76` app pink / `#8E2A52` deep rose / `#9E8892` muted / `#F7D6E4` pale / `#EBD3DE` line. Older matplotlib figures use DejaVu Serif with `#8E2A52` primary, `#B5537E` secondary, `#C27396` light.
4. **Two deliberate exceptions to the rose theme:** the **business model canvas** and **all tables inside the concept note** are monotone (black / grey / white) for legibility. Do not "fix" them back to pink. Standalone figures (tiers, bundles, device comparison) *are* rose.
5. **IMRaD paper is lung-only.** The concept note covers both Lung and Heart modes.
6. **Keep three-branch fusion and the nine-site protocol as PLANNED**, never present tense. The deployed model is MFCC + CNN over seven sites.
7. **"40% means classifier accuracy"** — 6 of 15 recordings agreed with reference labels. Not device equivalence.
8. Keep the concept note, script, slides and paper agreeing with each other. They have drifted repeatedly.

## A5. Verified facts — use these, not the older handoffs'

| Fact | Value | Note |
|---|---|---|
| Signal strength | **45 dB** vs **32 dB** conventional | 13 dB gap ≈ **4.5× amplitude**. "32.49 vs 7.89 dB, 4× stronger" is wrong twice: wrong figures *and* dB can't be divided. |
| Ambient noise | quiet room **24**, ward **35**, community area **42** dB | Headroom against a 45 dB signal: 21 / 10 / **3** dB |
| Recording quality | **68% good, 25% acceptable, 7% poor** | **Denominator unknown.** Report proportions without a count. |
| Response times | connection **4.55 s**, recording **15.00 s**, quality assessment **144.68 s**, preprocessing **20.91 s**, classification **3.97 s** | **Table 5 of the paper is authoritative.** Figure 4.4 of the same paper contradicts it and is wrong. |
| Field agreement | **6 of 15 = 40%**, Wilson 95% CI **19.8–64.3%**, exact binomial vs 25% chance **p = 0.148** | 8 of 15 would have been needed for significance |
| Chance level | **25%** (four classes) | A review claiming 33% / three classes is wrong |
| Acceptance survey | **n = 27** (13 patients, 13 general, 1 practitioner) | **Not 30.** See A7. |
| Bill of materials | **₱2,735.00** | Confirmed by the user 2 Nov. Excludes battery protection/BMS and charging by its own note. |
| Fully loaded unit cost | **≈ ₱4,000** | The bridge is in A6 — know it before touching any money figure |
| Device price | **₱8,000** | ≈ 50% gross margin from the first unit |
| Seed requested | **₱500,000** | Not ₱300,000 — that appears only as a deliberate comparison |
| Revenue (cash) | Y1 **₱175,900** · Y2 **₱426,900** · Y3 **₱885,700** · cum36 **₱1,488,500** | Run-rate equivalents: Y1 ₱225,400, Y2 ₱510,600 |
| Seed recovery | **commercial month 21** = **month 35 from funding** | Investor 40% share resolves later, in commercial Year 3 |
| Auscultation sites | **SEVEN**: Tc, Al, Ar, Pl, Pr, Ll, Lr | Six lung fields + tracheal reference. Nine sites is the *planned* protocol. |
| PSA mortality | IHD **134,074**, pneumonia **47,260**, total deaths **701,884** | Older decks use 133,373 / 46,718 — stale |
| ICBHI corpus | 920 recordings, 126 patients, 6,898 cycles | Cycle-level: Healthy **52.8%**, Crackle **27.0%**, Wheeze **12.8%**, Both **7.3%** |
| Demonstration materials | **₱5,000** | **NOT ₱15,000.** ₱15,000 is the whole *Deployment and Marketing* category, of which demonstration materials is one line. Claude got this wrong once; don't repeat it. |

## A6. The ₱2,735 → ₱4,000 bridge — memorize this

The user asked whether the pricing structure was up to date with the new BOM, then confirmed **₱2,735** is correct, then said **"keep it as ~4000."** Both are right, and the note now explains why:

```
₱2,735   bill of materials (Malimban, 2026) — excludes battery protection and charging by its own note
+ ₱665   battery protection, charging circuit, connectors, strain relief,
         finished enclosure, spares allowance
= ₱3,400 components, production unit
+ ₱600   assembly, calibration, functional test, packaging
= ₱4,000 fully loaded unit cost, design frozen
```

**₱4,000 is load-bearing.** `finpack/model.py` uses `DEV = 4_000` as the device margin received on acquisition, and every cash figure, Figure 11, Figure 12 and Table 16 descend from it. Changing ₱4,000 means regenerating all of them. The ₱14,000 design-iteration figure is a *third*, separate number — it is the ₱42,000 hardware refinement allocation across three units, absorbing single-quantity retail pricing, failed prints and board revisions. Keep all three apart.

## A7. The device — REWRITTEN 2 NOV, this is the biggest change in this file

The user supplied four STL files and `RESONDI_Product_Specifications.docx` for **enclosure version 2.0**. The concept note had been describing a different machine. Five conflicts were found and all five are now resolved in the note:

| The note used to say | VER 2.0 actually is |
|---|---|
| Bluetooth Low Energy, "advertises over BLE" (3 mentions) | **2.4 GHz Wi-Fi access point**, SSID `RESONDI_WIFI`, device-served web app at `http://192.168.4.1`. **No BLE anywhere in the build.** |
| 3D-printed **PLA** casing (2 mentions) | **PETG**, FDM |
| "MEMS microphone **and preamplifier**", "the preamplified acoustic signal" | **INMP441 digital MEMS on I²S** — there is no analogue preamp stage |
| Cloud tier written in the present tense | Spec sheet: *"Cloud access, remote internet access, and external network integration are not included in the current configuration."* |
| Twenty seconds per lung site | Firmware records a **fixed 15 s** in both modes |

**Full VER 2.0 specification** (now Table 1 of the concept note):

| Item | Specification |
|---|---|
| Main controller | ESP32, 32-bit dual-core Xtensa LX6, up to 240 MHz |
| Audio sensor | INMP441 digital omnidirectional MEMS microphone, I²S |
| Microphone output | 24-bit digital; firmware records at 16-bit |
| Recording format | WAV, uncompressed PCM, 16 kHz, 16-bit, mono, 256 kbps |
| Recording duration | 15 seconds per capture |
| File size | ≈ 480 kB per recording |
| Storage | 32 GB MicroSD; separate Heart and Lungs groups, sequential filenames |
| Display | 20 × 4 character LCD, I²C |
| Controls | Heart and Lungs buttons, two status LEDs, power rocker switch |
| Wireless | 2.4 GHz Wi-Fi 802.11 b/g/n, device-hosted access point |
| Local interface | Resondi web app served by the ESP32 at `http://192.168.4.1` |
| Power | 10,000 mAh rechargeable battery |
| Enclosure | PETG, FDM, **173 × 80 × 70 mm** assembled |

**How the IoT story is now told, and why it must stay this way.** The note no longer claims three working tiers. The **edge tier exists and works today**. The **mobile gateway** is what the ₱38,000 mobile-application line builds, and the **cloud platform** is what the ₱48,000 cloud line builds. This is the same built-vs-planned discipline the rest of the document already follows, and it turns a contradiction a judge would find into a funding argument. **Do not let any future edit put the cloud tier back into the present tense.**

**The recording interval** is handled the same way: the protocol calls for 20 s lung / 15 s heart, the firmware currently does a fixed 15 s, so a lung site is taken as two consecutive recordings until the interval is made selectable — a firmware revision with no component cost.

> ### ⚠ OPEN CONFLICT — the user must decide
> **The BOM says PLA. The specification sheet says PETG.** The concept note currently follows the spec sheet (PETG). If the BOM is the correct one, the note needs flipping back — **and check whether ₱2,735 was priced on PLA filament**, because PETG costs more per spool and the BOM total may move. This was raised with the user on 2 Nov and is unanswered.

**Device figure.** `dev2/device_fig.py` renders `Resondi-Device-Components.png` (3520 × 1130) from the STLs — two panels, because one view cannot do both jobs: a face-on cover where every leader lands exactly, and a small exploded assembly. Feature coordinates are **not guessed** — they come from rasterising the cover's top face with barycentric point-in-triangle tests (`trimesh` ray-casting fails here: `rtree` is not installed). Measured: LCD window 39.9 × 97.6 mm at (0, 24.1); buttons Ø 27.7 mm at (±18.7, −59.8); LEDs Ø 5 mm at (±9.4, −35.4); eight M3 brass inserts. Lighting is **two-sided** (`0.46 + 0.48·max(d,0) + 0.22·max(−d,0)`) or the interiors render black.

## A8. Subscription tiers, bundles and onboarding — ADDED 2 NOV

The user said: *"for the tiered plans, make some up, starts at 1500. then ill implement it in the app"*, then later *"add bundles, free 1 month new user stuff etc."* Everything below is **invented to a sensible shape and is explicitly labelled a proposal, not a validated price**, in every artefact. Keep that label.

**Tiers** (concept note Table 6; figure `figs_nov/Resondi-Subscription-Tiers.png`):

| | Essential | Clinical | Network |
|---|---|---|---|
| Per facility per month | **₱1,500** | **₱2,900** | **₱4,500** |
| Minimum facilities | 1 | 1 | 3 (cluster) |
| Cloud allowance | ₱350 | ₱450 | ₱600 |
| Service and replacement reserve | ₱250 | ₱250 | ₱250 |
| Review operations | — | — | ₱350 |
| **Contribution** | **₱900** | **₱2,200** | **₱3,300** |
| Available | now | after the funded build | after the funded build |

**Bundles** (Table 7; figure `figs_nov/Resondi-Bundles-And-Offers.png`):

| Bundle | Contents | Separately | Bundle | Discount from | Contribution kept |
|---|---|---|---|---|---|
| Starter | 1 device, Essential, 12 mo prepaid | ₱26,000 | **₱24,500** | ₱1,500 device only | ₱900/mo; device margin ₱2,500 (38%) |
| Clinic | 3 devices, Clinical, 12 mo prepaid | ₱58,800 | **₱52,000** | ₱3,000 device + ₱3,800 subscription | ₱1,883/mo |
| Cluster | 3 facilities × 1 device, Network, 12 mo prepaid | ₱186,000 | **₱168,000** | ₱4,500 device + ₱13,500 subscription | ₱2,925/facility/mo |
| Teaching | Institutional licence + 2 devices | ₱46,000 | **₱42,000** | ₱4,000 device only | Licence intact at ₱30,000 |

> **The one rule that holds the whole structure up:** *no bundle discount comes out of the ₱600 per facility per month that pays cloud operation and the replacement reserve.* Essential's contribution is **exactly** the ₱900 the projections assume, so it has **zero headroom** — an Essential discount must come out of device margin and the subscription is charged in full. Clinical and Network have room, so part of their discount can come from the subscription. **If you change any bundle price, re-run the floor check before anything else.**

**Onboarding offers:**

- **First month free**, new facility on Essential, month to month. **Costs the model nothing.** `finpack/model.py` already starts the contribution in the month *after* acquisition (`billing = acquired`, counted before the current month), so the acquisition month was never billed — the free month is already inside the ₱175,900 Year 1 figure. The ₱4,000 device margin is still received on acquisition.
- **Clinical free for 60 days** on a new deployment. Costs the ₱100/month cloud-allowance difference twice: **₱200 per facility, once.**
- **Offers do not stack.** Free first month *or* a prepaid bundle, never both.

**The projections still model every facility at Essential at the full ₱1,500.** That is deliberate and conservative: the ladder can only raise contribution above ₱900. **Nothing in `finpack/model.py` changed, and no figure that imports it needs regenerating.**

App-side config (`BUNDLES`, `OFFERS`, the floor-check function) is in `figs_nov/subscription-tiers-spec.md`. One line in it is not negotiable: `onExpiry: 'prompt_tier_choice'` — a trial that silently rolls into a paid tier is the fastest way to lose a rural health unit's trust.

## A9. Asian datasets — the gap is smaller than the note used to admit

The user flagged, urgently, that Asian corpora already exist. They were right, and their own IMRaD already cited one while the concept note was silent.

| Corpus | What it is |
|---|---|
| **HF_Lung_V1** (Hsu et al., 2021) | **9,765** fifteen-second recordings, ~**279** subjects, **Taiwan**, **CC BY 4.0**, `github.com/techsupportHF/HF_Lung_V1`. ~10× ICBHI's recording count, East Asian rather than European. The strongest free option. |
| Formosa Archive of Breath Sound (FABS) | Taiwanese breath-sound archive |
| Indian Pulmonary Sound dataset | South Asian |
| ZCHSound | Chinese **heart** sound corpus — relevant to Heart Mode, which has no model at all yet |

The concept note now carries a paragraph on this, ending on the line that should survive any rewrite: ***"Asian representation is therefore not absent from the plan; Filipino representation is what remains to be bought."*** That converts "we have no Asian data" from a weakness a judge finds into a step already taken, and keeps the ₱46,000 local-recording line justified.

**The merge tooling is written:** `hflung/merge_corpora.py` plus `hflung/ADD-HF-LUNG-GUIDE.md`. Three rules it enforces, all of which matter:

1. **Patients are partitioned before any audio is opened.**
2. **The test partition is ICBHI patients only and never changes** — the ablation compares runs trained on different corpora, so if the test set grows with the training set no two runs are comparable.
3. **HF_Lung goes entirely into training except a 20% `hf_holdout`** of its own patients, reported separately as East Asian external validation. Patient IDs are namespaced `icbhi_…` / `hf_…` because both corpora number from their own 1 and would silently collide.

`CAS_POLICY = "drop"` (default) or `"wheeze"` decides what happens to stridor and rhonchi, which have no slot in the four-class scheme. **State the choice in the paper either way** — a reviewer who knows HF_Lung_V1 will ask.

**Do not add HF_Lung before the patient-wise re-split has a baseline number (A10).** Adding a second corpus on top of a leaking split makes the leak worse *and* makes the result unreadable.

## A10. THE LEAKAGE FINDING — still the most important thing in this file

The model's reported scores are **inflated and must not be quoted as evidence of field performance.**

**What happened.** ICBHI audio was cut into 19,246 five-second samples at a ~1-second stride (4.86× expansion over ~19,800 s of source audio). Consecutive samples share four of their five seconds. Those overlapping samples were then split train/validation/test **at random over individual samples**, with Edge Impulse's "split train/validation set on metadata key" field left **empty**. Near-identical audio sits on both sides of every split.

**Three errors, in order of severity:**

1. **Windowing before splitting.** Patients must be partitioned *first*; windowing happens inside each partition.
2. **No grouping key on either split.** The metadata key governs only train/validation; the train/test split is a separate operation and does not honour it.
3. **Label granularity.** The model was trained on *patient-level diagnosis labels* (Asthma / Bronchiolitis / Pneumonia / Healthy) applied to every window of that patient's audio. A pneumonia patient does not have crackles in every second. The only signal consistent across all of one patient's windows is **that patient's acoustic fingerprint** — so the model learned *who*, not *what*.

**Affected: 71.1% (test), 83.4% (validation), 83.7% (int8).** All three. **The 40% field agreement is the only unleaked estimate.**

**Expect accuracy to fall to roughly 45–60% after the fix. That is the correct outcome.** The majority-class baseline is **53%** (Healthy), not 25% — report the confusion matrix and per-class recall, not accuracy alone.

If class names change to Healthy / Crackle / Wheeze / Both, the app's `DISPLAY` dict and the rule layer both key off the old disease names:

```javascript
const DISPLAY = {
  Wheeze:  'High Pitched Wheezing',
  Both:    'Wheezing With Crackles',
  Crackle: 'Crackles',
  Healthy: 'Healthy (Soft)',
};
```

## A11. The acceptance survey

The Google Forms export did **not** measure what the paper said. The paper described five dimensions (user-friendliness, usability, durability, functionality, community impact); the actual instrument is a **UTAUT** questionnaire with no durability item and no community-impact item anywhere in it. **Decision taken (user approved):** rewrite the methodology around UTAUT (Venkatesh et al., 2003) rather than force-map the items.

| Construct | Items | n | Mean | SD | Verbal | α |
|---|---|---|---|---|---|---|
| Performance expectancy | 3 | 27 | 4.09 | 0.59 | Agree | 0.51 |
| Effort expectancy | 3 | 27 | 4.09 | 0.60 | Agree | 0.76 |
| Regulatory assurance | 5 | 27 | 3.84 | 0.61 | Agree | 0.59 |
| Social influence | 1 | 27 | 3.63 | 1.21 | Agree | — |
| **Overall (12 Likert items)** | 12 | 27 | **3.95** | — | **Agree** | — |

Dichotomous items (frequencies, never means): peers encourage use 21/27 (78%); institution provides resources 20/27 (74%); access to training — maybe 12 (44%), yes 8 (30%), no 7 (26%); prior device experience 11/27 (41%).

**Disclosed weaknesses:** three behavioural-intention items and all open-ended items returned **zero responses**; four items are Yes/No and cannot be averaged; the option list contains a typo (`Stongly Agree`, 9 occurrences); only one practitioner responded; five of twelve Likert items ask about ISO conformity the device has **not** achieved.

Rerun with `newdata/analyse_acceptance.py`. It never reads the name, e-mail or timestamp columns.

## A12. Privacy rules — carry these forward

- The acceptance CSV contains **respondent names and e-mail addresses**. Never put them in a deliverable; never print them in output.
- Earlier app screenshots contained **a named minor patient with medical history**, a **PRC number**, phone numbers and e-mails. All excluded. App screenshots are masked to "Hello, Patient" / "Welcome, Doctor".
- The user once screenshotted a **live Kaggle API token**. It was redacted and they were told to revoke it. Never reproduce it.
- **Never enter credentials into any login form.** This blocked reading Edge Impulse directly; the workaround is to ask the user for screenshots.

## A13. Competitive position (researched 30 Oct 2026, still current)

**Four findings that carry the argument:**

1. **No vendor reviewed documents same-site longitudinal comparison.** Not Eko, Littmann, Thinklabs, HD Steth or StethoMe. Say *"not documented by any vendor reviewed"*, never *"does not exist"*.
2. **Eko's AI is not sold in the Philippines.** Eko+ supported countries: US, Canada, 20 European countries, Australia, New Zealand. No ASEAN member. A Philippine facility can import the hardware but cannot license the analysis.
3. **Eko stores all cloud recordings in the United States.** Relevant to any Data Privacy Act discussion.
4. **Guided placement exists only as a paid four-point cardiac exam.** No reviewed device guides a non-expert through a lung field sequence.

**The finding that cuts against Resondi — do not hide it.** The **Eko CORE 300** launched **22 October 2026** at **USD 199–249** (FDA K261694, cleared 23 Jul 2026) — the first cleared murmur-AI device priced near Resondi's ₱8,000. It detects one cardiac finding, has no lung AI, no guided lung placement, no longitudinal comparison, and its analysis is unavailable here, so the position holds. But **price alone is no longer a defensible differentiator**, and the note says so. Expect a judge to raise it.

**Reference prices (USD list, Oct 2026):** Eko CORE 500 $449 · CORE 300 $199–249 · 3M Littmann CORE $379 · Thinklabs One $499 (no AI) · HD Steth $499 bundle (2021 price) · Littmann Classic III ~$100 · basic acoustic ~$15–26.

**Philippine benchmark:** DOST-PCHRD reports electronic stethoscopes here cost **at least ₱30,000–₱40,000**, in its write-up of **E-Steth** (UP College of Medicine, DOST-PCHRD funded) — local, acoustic-electronic, no AI, TRL 5, not commercialised. Cite it as evidence of recognised domestic need, not as a competitor.

**Flagged source problems** (hedged in the note): CORE 300 price differs between Eko's store ($249) and the launch announcement ($199); Eko DUO is discontinued at retail but still listed as app-compatible; Thinklabs' regulatory page was last modified March 2021 with no K number; HD Steth markets AI cardiac evaluation while its 510(k) states it "is not intended to be used as a diagnostic device"; Littmann CORE amplification is given as both 40× and 140× on one page. **No PH distributor or peso price was found for any imported device.**

---

# PART B — FILES, BUILDS, AND THE DOCUMENT INDEX

## B1. Where the current work actually lives

> **The concept note builder has two copies and only one is current.**
>
> | Path | Date | Status |
> |---|---|---|
> | **`proj/build/cn2/build.js`** | **2 Nov, 131,865 B** | ✅ **CURRENT.** All VER 2.0, tier and bundle work is here. Has the CEO/CTO/COO team. |
> | `cn2/build.js` | 30 Oct, 120,483 B | ❌ **STALE.** Diverged. Building from it silently produces the 30 Oct document. |
>
> `proj/build/cn2/build.js.bak` is the pre-2-Nov snapshot, kept for diffing.

```bash
cd proj/build/cn2 && node build.js
# → proj/deliverables/Resondi-Concept-Note-FINAL.docx
```

**The `docx` library version matters.** `proj/build/cn2/package.json` pins `^9.15.0`. A container default of 9.7.1 produces **three stray blank paragraphs**. If the output diff is dirty for no reason, run `npm install docx@^9.15.0` first.

## B2. Concept note — current state and the full index

**323 paragraphs · 16 tables · 12 figures · 0 red placeholders · ~88,100 characters.** Two landscape pages: Figure 8 (canvas) and Table 9 (device comparison).

| # | Table | | # | Figure |
|---|---|---|---|---|
| 1 | Technical Specification, Enclosure Version 2.0 **(new 2 Nov)** | | 1 | Resondi Enclosure VER 2.0, Front Face and Exploded Assembly **(new 2 Nov)** |
| 2 | Lung Mode Auscultation Sites | | 2 | Hardware Block Diagram |
| 3 | Heart Mode Auscultation Sites | | 3 | Six-Stage Recording and Review Workflow |
| 4 | Revenue Streams and Payment Basis | | 4 | The Workflow as Rendered in the Application |
| 5 | Unit Economics and Pricing Derivation | | 5 | Auscultation Sites and Recording Protocol |
| 6 | Subscription Tiers **(new 2 Nov)** | | 6 | Planned CNN Feature-Fusion Architecture |
| 7 | Bundles, Prepaid Twelve Months **(new 2 Nov)** | | 7 | Value Proposition Against Existing Alternatives |
| 8 | Competitive Landscape | | 8 | Business Model Canvas *(monotone)* |
| 9 | Device Feature Comparison | | 9 | Addressable, Serviceable, Obtainable Market |
| 10 | PESTLE Analysis | | 10 | Organizational Structure |
| 11 | Risk Register and Mitigation | | 11 | Allocation of the ₱500,000 Requirement |
| 12 | Six-Phase Implementation Plan | | 12 | Cumulative Cash Contribution |
| 13 | Operating Functions, Owners, Service Commitments | | | |
| 14 | Allocation of the ₱500,000 Financial Requirement | | | |
| 15 | Detailed Line-Item Breakdown | | | |
| 16 | Investor Repayment Against Operating Overhead | | | |

### ⚠ Table numbers shifted on 2 Nov — other documents may still quote the old ones

Three tables were inserted. Everything downstream moved:

| 30 Oct | → | 2 Nov | | 30 Oct | → | 2 Nov |
|---|---|---|---|---|---|---|
| — | | **1** Technical Specification | | 7 | → | **10** PESTLE |
| 1 Lung sites | → | 2 | | 8 | → | **11** Risk register |
| 2 Heart sites | → | 3 | | 9 | → | **12** Implementation plan |
| 3 Revenue streams | → | 4 | | 10 | → | **13** Operating functions |
| 4 Unit economics | → | 5 | | 11 | → | **14** ₱500,000 allocation |
| — | | **6** Subscription tiers | | 12 | → | **15** Line-item breakdown |
| — | | **7** Bundles | | 13 | → | **16** Investor repayment |
| 5 Competitive landscape | → | 8 | | | | |
| 6 Device comparison | → | 9 | | | | |

Figure numbers are unchanged (12 either way): the old Figure 1 block diagram became Figure 2, and the old Figure 2 (`fig_device_3d.png`) was **dropped** in favour of the new STL-rendered Figure 1.

**Grep the script, Q&A, IMRaD and deck for stale "Table N" references before the next submission.** In-document references were all verified: zero dangling.

**Renumbering recipe that worked**, if a table is ever inserted again — protect the new captions with placeholders, then substitute **descending** with a negative lookahead so `Table 1` never eats `Table 11`:

```python
for n in range(HIGHEST, 0, -1):
    s = re.sub(rf"Table {n}(?![0-9])", f"Table {n+SHIFT}", s)
    s = re.sub(rf"TCAP\({n},",         f"TCAP({n+SHIFT},", s)
```

## B3. Other deliverables and how to rebuild them

**Never hand-edit a `.docx` — edit the builder and rebuild.**

| Deliverable | Builder | Rebuild | State |
|---|---|---|---|
| `proj/deliverables/Resondi-Concept-Note-FINAL.docx` | `proj/build/cn2/build.js` | `cd proj/build/cn2 && node build.js` | **Current. Submittable.** |
| `script6/Resondi-Pitch-Script.docx` | `script6/build_script.py` from `script5/revised_long.txt` | `cd script6 && python build_script.py` | 1,177 spoken words, **7:50** at 150 wpm. **Not yet checked against the VER 2.0 device.** |
| `qa/Resondi-Judge-QA.docx` | `qa/build_qa.py` + `qa/part5.py` | `cd qa && python build_qa.py` | **111 questions, 34 flagged DECIDE.** Needs tier/bundle and VER 2.0 questions added. |
| `imrad/Resondi-IMRaD-Lung-Only.docx` | `imrad/build_imrad.py` | `cd imrad && python build_imrad.py` | 6,852 words, **16 TO FILL markers**, 3 tables |
| `accept/Resondi-Acceptance-Survey-jamovi-Guide.docx` | `accept/build_guide.py` | `cd accept && python build_guide.py` | 8 pp, click-by-click |
| `finpack/Resondi-Financial-Revision-Pack.docx` | `finpack/build_pack.py` | `cd finpack && python build_pack.py` | 17 pp paste-ready |
| `sheet/Resondi-Price-Structure.xlsx` | `sheet/build_xlsx.py` | `cd sheet && python build_xlsx.py` | BOM bridge and pricing, **new 2 Nov** |
| `stats/*.docx`, `cue/*.docx` | built inline, scripts not retained | — | Statistics summary, jamovi guide, spoken answers |

**Figure scripts:**

| Script | Produces |
|---|---|
| `finpack/model.py` | **Single source of truth for every money figure.** Import it; never retype a number. |
| `dev2/device_fig.py` | **Figure 1** — `Resondi-Device-Components.png` from the STLs *(new 2 Nov)* |
| `dev2/render.py` | STL probe renders (`iso` / `front` / `top` / `side`) for checking geometry |
| `figs_nov/tiers.py` | `Resondi-Subscription-Tiers.png` *(new)* |
| `figs_nov/bundles.py` | `Resondi-Bundles-And-Offers.png` *(new 2 Nov)* |
| `figs_nov/tiers_slide.py` | Slide-shaped tier figure *(new)* |
| `figs_nov/build.py`, `figs_nov/pricing_rev.py` | Device comparison, price-and-unit-cost figures *(new)* |
| `deckfigs/build.py` | Figures 8 (canvas, **monotone**), 11, 12 |
| `fig/fig1.py`, `fig/fig2.py`, `fig/diagrams.py` | Figures 7, 9, 2, 3, 6 — rose palette |
| `fig/fig9_org.py` | Figure 10, org chart |
| `imradfig/results.py` | IMRaD result figures; response times use Table 5 with SDs |
| `slides/*.py` + `slides/capture.py` | Pitch slides, 3840×2160 PNG |
| `newdata/rebuild_dataset.py` | **The leakage fix.** Patient-disjoint ICBHI rebuild. |
| `hflung/merge_corpora.py` | ICBHI + HF_Lung_V1 merge *(new)* |
| `newdata/analyse_acceptance.py` | UTAUT analysis of the survey CSV |

Concept-note figures are read from `proj/figures/`. A new figure must be copied there before `node build.js`.

**Build environment:** Node with `docx@^9.15`; Python with `python-docx`, `python-pptx`, `openpyxl`, `matplotlib`, `trimesh`, `numpy`, `playwright` (Chromium preinstalled), `scipy`, `soundfile`, `pypdf`, `Pillow`. LibreOffice (`soffice --headless --convert-to pdf`) for render checks. **Do not run project builds with `python -I`** — isolated mode drops the script directory from `sys.path` and local imports like `part5` fail.

## B4. The Edge Impulse runbook (interactive)

Published artifact: **`https://claude.ai/artifact/DQMmsN4Pu4TK4JzrMQ43vJ`** (Version 3), source `runbook/runbook.html`, capabilities `{db:{}, user:{}}`. **34 steps across 4 phases**, each badged with the app it happens in (Edge Impulse 14, PowerShell 12, others). Progress persists in the artifact database, so the user can close it and come back.

It exists because generic instructions were not enough — the user asked twice for more specificity: *"make it interactable"*, then *"make it more specific, like which apps I use, what buttons I press."* **Keep that register.** Name the app, name the button, give the exact command.

The upload pattern it teaches (PowerShell, because `edge-impulse-uploader` does not expand `*.wav` on Windows):

```powershell
foreach ($cat in "training","testing") {
  foreach ($lab in "Healthy","Crackle","Wheeze","Both") {
    $f = (Get-ChildItem "$cat\$lab" -Filter *.wav).FullName
    edge-impulse-uploader --category $cat --label $lab @f
  }
}
```

Impulse settings: window size **5000 ms**, window increase **5000 ms** (equal — anything smaller recreates overlap inside a clip), frequency **16000 Hz**. **Never press "Perform train/test split"** afterwards: it reshuffles at clip level and destroys every partition.

## B5. Source material

| File | What it is |
|---|---|
| `RIM-FULLPAPER-2026-9_1.pdf` | The 83-page research paper. Figure 4.5 p.12 is the source of 68/25/7; Table 5 pp.13–14 is the authoritative response-time table. |
| `dev2/specs.docx` | `RESONDI_Product_Specifications.docx` — the VER 2.0 spec sheet (A7) |
| STL files | `RESONDI_BASE_VER2.0.stl`, `RESONDI_COVER_VER2.0.stl`, `STETH_MOUNT.stl`, `STETH_COVER.stl` |
| `newdata/dataset920.csv` | The user's own 920-recording ICBHI index with the `patient` grouping column — lets you plan and verify a split **without touching any audio** |
| `Resondi_Bill_of_Materials.docx` | ₱2,735.00 |
| `Ausculta_Survey_Questionnaire__Responses_` | Acceptance survey export — **contains PII** |
| `Ausculta_Respiratory_Rules_Evidence_Citations.pdf` | The rule layer with citations — the Figure 7 evidence base, keep it |
| `Hypothesis_2_design_and_analysis.md` | Paired playback study design, not yet run |
| `handoff2/RESONDI-HANDOFF.md` | 30 Oct handoff — provenance only, its device section and table numbers are now wrong |
| `handoff/RESONDI-HANDOFF.md` | 27 Oct handoff — provenance only |

The user's own copies live on Windows at `C:\Users\Hared\Downloads\Resondi`.

---

# PART C — HOW TO WORK ON THIS

## C0. Four traps, each of which has cost a session once

1. **The stale builder.** `cn2/build.js` is 30 Oct; `proj/build/cn2/build.js` is current. Check the date before you edit (B1).
2. **Renumbering tables.** Inserting one table moves every number after it *and* every prose reference. Substitute descending with a lookahead, verify captions come out `1..N` in order, and check for dangling references (B2).
3. **The user is on Windows.** Bash loops, `*.wav` glob expansion and `&&` chains do not work in PowerShell. She has also hit the execution-policy wall — `npm.ps1 cannot be loaded because running scripts is disabled`. The fix is `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, with `npm.cmd` as a fallback and "skip the CLI, use the Studio uploader" as a third option. Offer all three.
4. **Grep false positives.** `BLE` matches inside `PROBLEM`. `PLA` matches inside `PLAN` and `PLATFORM`. `OLED` matches inside `pooled`. `Elli` matches inside `intelligence`. `signed` matches `designed`. **Read the context of every hit before reporting a finding.** More than one "conflict" has evaporated on inspection.

## C1. Open work, in priority order

### 1. Re-split and retrain — the only item that changes a number a judge will ask about
Run `newdata/rebuild_dataset.py`, upload with explicit categories (B4), retrain. **Expect 45–60%.** Record Run A's accuracy, confusion matrix and per-class recall — without that baseline nothing after it is measurable. Then update: concept note model paragraph, `stats/Resondi-Model-Statistics-Summary.docx`, IMRaD results, slide 11, and the `DISPLAY` dict if class names change.

### 2. Then — and only then — add HF_Lung_V1 (A9)
`hflung/merge_corpora.py --inspect` first, to confirm the label format against the real files. Then the four-run ablation on one fixed ICBHI test partition: **A** ICBHI/MFCC+CNN · **B** ICBHI/fusion · **C** ICBHI+HF_Lung · **D** +local Filipino. **C is free and can be run now; D is what the ₱46,000 recording line buys.** That contrast is the funding argument. McNemar is correct here — same fixed test set, paired predictions.

### 3. Resolve PETG vs PLA (A7) and confirm whether ₱2,735 moves

### 4. Correct the 83-page paper (`RIM-FULLPAPER-2026-9_1.pdf`)
**User's document — provide pasteable text, do not edit.** Needs: McNemar removed; the three paired t-tests removed; signal 32.49/7.89 → 45/32; ambient noise → 24/35/42; **Figure 4.4 corrected to match Table 5**; six locations → seven; the Data Analysis section reworded (it describes a device comparison, not a classifier test); the leakage disclosure added; Section G ("End-User Preference Evaluation") either reported or deleted — it has no results anywhere.

### 5. Bring the deck and script up to the 2 Nov concept note
The deck still needs: name → Resondi throughout; PSA **134,074 / 47,260**; **seven** sites not nine; **45 vs 32 dB ≈ 4.5×**; **25%, four classes** plus the leakage disclosure; **commercial month 21 = month 35**; Y1 **₱175,900**; ask **₱500,000**; acceptance **3.95/5, n = 27**. Now also: **VER 2.0 device and the Wi-Fi/no-cloud honesty**, and the **tier ladder and bundles**. Delete the yellow "WHAT CHANGED" annotations, export flat PDF, keep under 10 MB.

### 6. Deck placeholders the user owes
Founder achievements, mentor name, letter of intent, clean logo on transparent background plus a one-colour version and a 32 px app icon.

### 7. The 16 IMRaD TO FILL markers
Load-bearing ones: **#2** microphone part — **now resolved, it is the INMP441** (documentation had cited both INMP441 and MAX4466; the VER 2.0 spec sheet settles it); **#5** the rule layer operates on four zones while recording uses seven sites — state the mapping; **#7** signal measurement unit, reference level, comparator stethoscope make and model; **#8** how many professionals rated clarity and whether inter-rater agreement was assessed; **#9** whether the pulmonologists were blinded; **#10** sampling method for the 27 respondents; **#12** ethics approval versus physician supervision; **#13** whether the 3 hospital patients overlap the 13 self-identified patients in the survey.

### 8. Smaller, still open
- **Blinding was not recorded** for the 15-recording agreement study. The note states the gap and the prospective fix rather than asserting blinding. **Do not let a later edit claim it.**
- **Clarity denominator** — 68/25/7 of how many? Not in the paper; 170 values between 28 and 300 fit after rounding, so it cannot be derived.
- **The live app still guides nine lung sites.** The documents say seven. The fix was drafted in an earlier session but **the file is not in this workspace** — redraft it.
- **`final/README.md` is stale** — still says "three founders plus seven contributors" in the old phrasing.
- **Base44 app meta tags** still say `ausculta.base44.app`.
- **IP ownership** written as "to be formalized with the school" — unresolved commitment.
- **Confirm the live Google Sheet** still has 27 rows, not more.
- **Hypothesis 2** (`Hypothesis_2_design_and_analysis.md`) designed but never run: 20 paired reference-vs-device playback recordings. McNemar is correct for that design. Run it *after* the re-split, or §8.3 applies — a near-chance classifier in both conditions produces no detectable difference for reasons unrelated to hardware.
- **A third agreement study** exists as an empty template (`agreement_analysis_TEMPLATE.csv`, 30 rows, six interpretation-layer categories). Never run.
- **Willingness to pay has no evidence anywhere.** The tier ladder is cheap to test: when the five to ten budget-holder interviews happen, add *"At ₱1,500 you get capture, AI and review. For ₱2,900 you also get comparison against the last visit, the rehabilitation module and a monthly report. Which would your facility choose, and why?"* Ten answers turn the proposal into a priced product.

## C2. Statistics — what is correct and what is circular

- **McNemar** is correct for *classifier versus classifier on a fixed test set*, with paired predictions. It is **wrong** for agreement against reference labels. The IMRaD Discussion explains the distinction; three correct McNemar references were deliberately kept.
- **The jamovi Kruskal-Wallis is circular as run.** It compares `abnormal_sound_percent` across the four sound categories (χ² = 633, p < .001), but **Healthy recordings are 0.0 with SD 0.00 by definition** — a recording is *called* Healthy when it has no abnormal cycles. Three of six pairwise comparisons are tautological. **Rerun without Healthy and the finding survives: H = 32.53, df = 2, p < .001**, all three pairwise comparisons surviving Bonferroni. Wheezing with Crackles (84.7%) > Crackles alone (70.6%) > Wheezing alone (64.7%). Report that, with one line on why Healthy was excluded.
- **Wilson score intervals** for proportions; **exact binomial** against the 25% chance level. Not normal approximations at n = 15.

## C3. The editorial standard this project is held to

Every deliverable distinguishes **what exists** from **what the funding builds**, in the present and future tense respectively, and never blurs the two. That discipline is why the device section survived contact with the real spec sheet, and it is the single most valuable property of these documents. When a new fact arrives that contradicts a claim, the move is to **state the gap and what closes it** — never to quietly soften the claim.

Three worked examples of that move, all in the current note:

- *"Asian representation is therefore not absent from the plan; Filipino representation is what remains to be bought."*
- The IoT section: edge tier in the present tense, gateway and cloud tied to the ₱38,000 and ₱48,000 lines.
- The agreement study: blinding was not recorded, so the note says so and describes the prospective fix.
