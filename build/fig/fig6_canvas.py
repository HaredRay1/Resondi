import os as _os
"""Figure 6 — Business Model Canvas, rebuilt against the corrected financials.

The original raster still carried the pre-restructure seven-category seed
split and the ₱795,000 Year 2 figure, both of which now contradict Table 8
and the business model section. Every monetary figure here is taken from the
concept note as it currently stands.
"""
import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Resondi rose theme (shared with the IMRaD figures and Figures 11-12)
NAVY, RULE, TEXT, GREY = "#8E2A52", "#B5537E", "#3A2730", "#8A7480"
DEEP, PALE, EDGE = "#5E1636", "#FBE9F0", "#C98EA9"
FONT = "Inter"
W, H = 20.40, 15.65          # inches at 100 dpi -> 2040 x 1565

BLOCKS = {
    "Key Partners": [
        "CLINICAL: partner hospital and Provincial Health Office; ethics committee; "
        "pulmonologists and cardiologists for labelling and content approval",
        "ACADEMIC: PPCNSHS research programme; nursing and medical schools as validation "
        "and teaching partners",
        "INDUSTRY: medical device distributors for channel reach; component suppliers, PCB "
        "fabricator, contract assembler for volume production",
        "GOVERNMENT: LGUs and rural health units as pilot sites; DOH, DOST-PCHRD, DICT",
    ],
    "Key Activities": [
        "R&D PRIORITY: build automated recording-quality assessment and noise reduction — "
        "the main gap between prototype and deployable product",
        "R&D: CNN retraining on a patient-wise split; recording collection and clinical "
        "labelling; platform development",
        "PRODUCTION: device assembly, calibration, quality testing; freezing the design and "
        "driving the fully loaded unit cost from ~₱4,000 toward ~₱3,000 at volume",
        "COMPLIANCE: clinical validation and FDA registration",
        "COMMERCIAL: customer acquisition in the school and RHU channels; demonstrations and "
        "expo presence; onboarding and training; distributor partnerships; scaling to "
        "contract assembly",
    ],
    "Key Resources": [
        "DEFENSIBLE: consented, locally labelled cardiopulmonary recordings — grows with "
        "every deployment, cannot be copied",
        "TECHNICAL: three-tier IoT stack — ESP32 edge firmware, mobile gateway, cloud "
        "platform; trained CNN model; clinician-approved interpretation and rehabilitation "
        "content library",
        "HUMAN: three founders — CEO (data and model operations, regulatory, sales), "
        "CTO (platform, security, designated Data Protection Officer), COO (production, "
        "field service, clinical validation, finance)",
        "EXTERNAL: PPCNSHS advisers; three consulting pulmonologists and one pediatrician; "
        "electronics engineer; practitioner reviewer network",
        "IP: firmware, platform, model weights, and content library — ownership to be "
        "formalized with the school before commercial agreements",
    ],
    "Value Propositions": [
        "ONE-LINER: Resondi makes every heartbeat and breath a record that can be tracked, "
        "compared, and reviewed",
        "Guided acquisition at standardized sites — placement directed, lung and heart "
        "separated, every recording tagged by location and mode",
        "Longitudinal comparison at the level of the individual auscultation site",
        "AI-assisted analysis a practitioner confirms, modifies, or rejects — never "
        "overwrites",
        "Separate Lung and Heart modes, rehabilitation support released under practitioner "
        "supervision",
        "Works where the network does not — store-and-forward capture on MicroSD, "
        "synchronised when the gateway next reaches a connection; connectivity is a "
        "convenience, not a precondition",
        "Reachable by a rural health unit at ₱8,000 per device against roughly ₱22,000 for "
        "an imported electronic stethoscope",
        "SLOW, NOT ABSENT: automated quality screening runs before analysis but takes about "
        "145 seconds against ~4 seconds for classification; reducing that latency is the first "
        "funded priority. Active noise reduction is not yet implemented",
    ],
    "Customer Relationships": [
        "On-site training at deployment",
        "Remote platform support, escalation for device faults",
        "Practitioner review workflow as the ongoing touchpoint — and, for now, the quality "
        "safeguard",
        "Model updates delivered through the subscription",
        "COMMUNITY: practitioner user group reviewing classifications and content; in-app "
        "feedback on every AI result; annual user forum; patient engagement through "
        "supervised rehabilitation tracking",
    ],
    "Channels": [
        "INSTITUTIONAL: LGU and DOH procurement; direct sale to private clinics and "
        "hospitals; institutional sale to nursing and medical schools",
        "PARTNER: medical equipment distributors (commercial Year 2 onward); donor-funded "
        "deployment programmes",
        "DIGITAL: product website with specification sheets and request-a-demo; online "
        "demonstrations for remote facilities; social and professional channels targeting "
        "health workers",
        "VISIBILITY: Philippine Startup Challenge; health-tech expos; medical and nursing "
        "conferences",
    ],
    "Customer Segments": [
        "EARLY ADOPTERS (commercial Year 1): nursing and medical schools (B2B) — lighter "
        "regulation, fastest sale; rural health units and municipal health centres (B2B)",
        "GROWTH (commercial Year 2–3): private clinics and secondary hospitals (B2B); LGU "
        "cluster deployments (B2B)",
        "FUNDED: NGOs and development agencies (B2B)",
        "Users: midwives, nurses, rural health physicians",
        "BENEFICIARIES (B2C, indirect): patients in geographically isolated barangays, "
        "reached through institutional deployment under practitioner supervision",
    ],
    "Cost Structure": [
        "ONE-TIME (₱500,000 seed): clinical validation ₱120,000 · AI development ₱102,000 · "
        "contingency ₱50,000 · cloud infrastructure and operation ₱48,000 · hardware "
        "refinement ₱42,000 · production working capital ₱40,000 · mobile application "
        "₱38,000 · IP and registration ₱25,000 · documentation and compliance ₱20,000 · "
        "deployment and marketing ₱15,000",
        "MARGINAL COST PER UNIT: ~₱4,000 fully loaded once the design is frozen — ₱3,400 of "
        "components (ESP32, MEMS mic and preamp, MicroSD, display, battery circuit, chest "
        "piece, casing) plus assembly, calibration and packaging",
        "DESIGN-ITERATION COST: ~₱14,000 per unit (₱42,000 ÷ 3 units) — absorbs retail "
        "pricing, failed prints and board revisions; not the cost of goods sold",
        "PRODUCTION WORKING CAPITAL: ₱40,000 builds the first batch of ten saleable units "
        "at ~₱4,000 each; later batches are built against confirmed orders",
        "COST REDUCTION: → ~₱3,000 at 100 units (silicone vacuum-cast enclosures, batch "
        "PCB, ~15% bulk discount); → ~₱2,500 at 500 units via contract assembly",
        "RECURRING: cloud, storage and backup carried at ₱350 per facility per month at "
        "pilot scale; funded for the first 12 months of commercial service by the ₱18,000 "
        "cloud operation line, and falling per facility as the base grows",
    ],
    "Revenue Streams": [
        "Device sale — ₱8,000 per unit against a ~₱4,000 fully loaded unit cost: ~50% gross "
        "margin from the first unit",
        "Platform subscription — ₱1,500 per facility per month = ₱350 platform cost + ₱250 "
        "support and replacement reserve + ₱900 contribution (primary engine)",
        "Institutional licence — ₱30,000 per school per year (earliest revenue, lightest "
        "regulatory burden)",
        "Donor-funded deployment — per-programme grant covering devices, training, "
        "first-year access",
        "PROJECTION (run-rate): commercial Year 1 ≈ ₱225,400 contribution (10 facilities, "
        "3 schools); Year 2 ≈ ₱510,600, of which ₱450,600 is recurring. In CASH, after the "
        "acquisition ramp: Year 1 ≈ ₱175,900, Year 2 ≈ ₱426,900",
        "INVESTOR RETURN: 40% of net earnings until the ₱500,000 is repaid. The business "
        "recovers the seed at month 35 from funding (month 21 of commercial operation); a "
        "40% share needs ₱1,250,000 of cumulative net, which falls in commercial Year 3 — "
        "beyond the projected horizon. Plus an agreed equity stake",
    ],
}

# ── layout, in pixels on a 2040 x 1565 canvas ───────────────────────────
PX, PY = 2040, 1565
L, R, TOPY, BOTY = 24, 2016, 1565 - 96, 24
COLW = (R - L) / 5
BAND = 450                  # top of the cost / revenue band
SPLIT = 950                 # where columns 2 and 4 divide
DIV = L + (R - L) * 0.475   # cost / revenue divider

col = lambda i: (L + i * COLW, L + (i + 1) * COLW)

LAYOUT = [
    ("Key Partners",           *col(0), TOPY, BAND + 20),
    ("Key Activities",         *col(1), TOPY, SPLIT),
    ("Key Resources",          *col(1), SPLIT, BAND + 20),
    ("Value Propositions",     *col(2), TOPY, BAND + 20),
    ("Customer Relationships", *col(3), TOPY, SPLIT),
    ("Channels",               *col(3), SPLIT, BAND + 20),
    ("Customer Segments",      *col(4), TOPY, BAND + 20),
    ("Cost Structure",         L, DIV, BAND, BOTY),
    ("Revenue Streams",        DIV, R, BAND, BOTY),
]

FS, STEP, GAP, PAD = 10.2, 20, 7, 38

fig = plt.figure(figsize=(PX / 100, PY / 100), dpi=100)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, PX); ax.set_ylim(0, PY); ax.axis("off")
ax.add_patch(Rectangle((0, 0), PX, PY, facecolor="white", zorder=0))

ax.text(L, PY - 26, "Business Model Canvas — Resondi", fontsize=19,
        fontweight="bold", family=FONT, color=DEEP, va="top")
ax.text(L, PY - 58, "All monetary figures derive from the ₱500,000 financial "
        "requirement.", fontsize=11.5, family=FONT, color=GREY, va="top")

for name, x0, x1, ytop, ybot in LAYOUT:
    ax.add_patch(Rectangle((x0, ybot), x1 - x0, ytop - ybot, facecolor="white",
                           edgecolor=EDGE, linewidth=1.4, zorder=1))
    ax.add_patch(Rectangle((x0, ytop - 42), x1 - x0, 42, facecolor=PALE,
                           edgecolor=EDGE, linewidth=1.4, zorder=1.5))
    ax.text(x0 + 14, ytop - 14, name, fontsize=14.5, fontweight="bold",
            family=FONT, color=NAVY, va="top", zorder=2)

    cpl = int((x1 - x0 - PAD) / 7.25) - (3 if name == "Key Partners" else 0)
    y = ytop - 52
    for item in BLOCKS[name]:
        ax.text(x0 + 16, y + 2, "▪", fontsize=7.5, family=FONT, color=NAVY,
                va="top", zorder=2)
        for ln in textwrap.wrap(item, cpl):
            ax.text(x0 + 28, y, ln, fontsize=FS, family=FONT, color=TEXT,
                    va="top", zorder=2)
            y -= STEP
        y -= GAP
    if y < ybot + 6:
        print(f"  OVERFLOW in {name}: {ybot + 6 - y:.0f}px")

fig.savefig(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "fig_business_model_canvas.png"),
            facecolor="white")
plt.close(fig)
print("fig_business_model_canvas.png rebuilt")
