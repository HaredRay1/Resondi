"""Resondi price structure revision — workbook."""
import os as _os
_BUILD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))).replace(chr(92), '/')
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.comments import Comment

F = "Arial"
BLUE = Font(name=F, size=11, color="0000FF")          # hardcoded input
BLACK = Font(name=F, size=11)                          # formula
BOLD = Font(name=F, size=11, bold=True)
H1 = Font(name=F, size=15, bold=True, color="8E2A52")
H2 = Font(name=F, size=12, bold=True, color="8E2A52")
MUTED = Font(name=F, size=10, color="707070")
HDRF = Font(name=F, size=11, bold=True, color="FFFFFF")
HDR = PatternFill("solid", fgColor="8E2A52")
YEL = PatternFill("solid", fgColor="FFFF00")
BAND = PatternFill("solid", fgColor="F2F2F2")
PESO = '₱#,##0;(₱#,##0);-'
PCT = '0.0%'
thin = Side(style="thin", color="BFBFBF")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
TOPLINE = Border(top=Side(style="medium", color="8E2A52"))

wb = Workbook()


def header(ws, row, cols, widths):
    for i, (c, w) in enumerate(zip(cols, widths), start=1):
        cell = ws.cell(row=row, column=i, value=c)
        cell.font = HDRF
        cell.fill = HDR
        cell.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[row].height = 30


def title(ws, text, sub=None):
    ws["A1"] = text
    ws["A1"].font = H1
    if sub:
        ws["A2"] = sub
        ws["A2"].font = MUTED
    ws.freeze_panes = "A5"


# ═══════════════════════════════════════════════ 1. UNIT COST MODEL
ws = wb.active
ws.title = "Unit Cost Model"
title(ws, "Resondi — unit cost and margin",
      "Blue cells are inputs: change them and everything below recalculates. "
      "Black cells are formulas.")

ws["A4"] = "INPUTS"
ws["A4"].font = H2
rows = [
    ("Bill of materials, one unit", 2775, "6 Nov 2026 handoff: 20 × 4 LCD and 32 GB card, both "
     "repriced; PLA casing. The BOM file on this PC still reads ₱2,875 with PETG."),
    ("Battery protection and charging circuit", 300, "Excluded from the bill of materials "
     "by its own technical note. CONFIRM THIS FIGURE with a supplier quote."),
    ("Production allowance", 325, "Connectors, strain relief, finished enclosure and spares "
     "a saleable unit needs beyond a bench prototype."),
    ("Assembly, calibration, test, packaging", 600, "Per unit, once the design is frozen."),
    ("Selling price to a facility", 8000, "Concept note, business model section."),
]
r = 5
for label, val, note in rows:
    ws.cell(row=r, column=1, value=label).font = BLACK
    c = ws.cell(row=r, column=2, value=val)
    c.font = BLUE
    c.number_format = PESO
    if "CONFIRM" in note:
        c.fill = YEL
    ws.cell(row=r, column=3, value=note).font = MUTED
    ws.cell(row=r, column=3).alignment = Alignment(wrap_text=True, vertical="top")
    r += 1

ws["A11"] = "BUILD-UP"
ws["A11"].font = H2
build = [
    ("Bill of materials", "=B5", False),
    ("Battery protection and charging", "=B6", False),
    ("Production allowance", "=B7", False),
    ("Components, production unit", "=B12+B13+B14", True),
    ("Assembly, calibration, test, packaging", "=B8", False),
    ("Fully loaded unit cost", "=B15+B16", True),
]
r = 12
for label, f, bold in build:
    ws.cell(row=r, column=1, value=label).font = BOLD if bold else BLACK
    c = ws.cell(row=r, column=2, value=f)
    c.font = BOLD if bold else BLACK
    c.number_format = PESO
    if bold:
        ws.cell(row=r, column=1).border = TOPLINE
        c.border = TOPLINE
    r += 1

ws["A19"] = "MARGIN"
ws["A19"].font = H2
marg = [
    ("Selling price", "=B9"),
    ("Fully loaded unit cost", "=B17"),
    ("Device margin per unit", "=B20-B21"),
    ("Gross margin", "=IFERROR(B22/B20,0)"),
]
r = 20
for label, f in marg:
    ws.cell(row=r, column=1, value=label).font = BLACK
    c = ws.cell(row=r, column=2, value=f)
    c.font = BOLD if r >= 22 else BLACK
    c.number_format = PCT if r == 23 else PESO
    r += 1
ws["C22"] = "Flows into finpack/model.py as device margin per facility."
ws["C22"].font = MUTED

ws["A25"] = "SENSITIVITY — what if the battery protection and charging circuit costs more?"
ws["A25"].font = H2
header(ws, 26, ["Battery protection + charging", "Components", "Fully loaded",
                "Device margin", "Gross margin"], [30, 16, 16, 16, 14])
r = 27
for v in (200, 300, 400, 500, 600, 700):
    ws.cell(row=r, column=1, value=v).font = BLUE
    ws.cell(row=r, column=1).number_format = PESO
    ws.cell(row=r, column=2, value=f"=$B$5+A{r}+$B$7").font = BLACK
    ws.cell(row=r, column=3, value=f"=B{r}+$B$8").font = BLACK
    ws.cell(row=r, column=4, value=f"=$B$9-C{r}").font = BLACK
    ws.cell(row=r, column=5, value=f"=IFERROR(D{r}/$B$9,0)").font = BLACK
    for col in range(1, 5):
        ws.cell(row=r, column=col).number_format = PESO
        ws.cell(row=r, column=col).border = BOX
    ws.cell(row=r, column=5).number_format = PCT
    ws.cell(row=r, column=5).border = BOX
    if v == 300:
        for col in range(1, 6):
            ws.cell(row=r, column=col).fill = BAND
    r += 1
ws.cell(row=r, column=1,
        value="Shaded row is the current assumption. Above ₱300 the ₱4,000 fully loaded "
              "figure needs revisiting before the ₱8,000 price does.").font = MUTED

ws["A36"] = "COST AT VOLUME"
ws["A36"].font = H2
header(ws, 37, ["Batch size", "Fully loaded cost", "Device margin", "Basis"], [16, 18, 18, 56])
vols = [(1, "=B17", "=$B$9-B38", "Current build"),
        (100, 3000, "=$B$9-B39", "Silicone vacuum-cast enclosures, batch PCB, bulk pricing"),
        (500, 2500, "=$B$9-B40", "Contract assembly")]
r = 38
for q, cost, marg_f, basis in vols:
    ws.cell(row=r, column=1, value=q).font = BLACK
    c = ws.cell(row=r, column=2, value=cost)
    c.font = BLACK if isinstance(cost, str) else BLUE
    c.number_format = PESO
    ws.cell(row=r, column=3, value=marg_f).font = BLACK
    ws.cell(row=r, column=3).number_format = PESO
    ws.cell(row=r, column=4, value=basis).font = MUTED
    for col in range(1, 5):
        ws.cell(row=r, column=col).border = BOX
    r += 1

ws["B6"].comment = Comment(
    "The bill of materials states battery protection and a compatible charging solution are "
    "not included in its ₱2,775 total. A TP4056-class charger plus a small BMS board should "
    "sit under ₱300 at Philippine retail. Replace this with a supplier quote.", "Claude")

# ═══════════════════════════════════════════════ 2. REVISION ACTIONS
ws = wb.create_sheet("Revision Actions")
title(ws, "Concept note revisions", "Find-and-replace pairs. Full text in "
                                    "price-structure-revision.md.")
header(ws, 4, ["#", "Document", "Section", "What changes", "Status", "Notes"],
       [5, 22, 30, 62, 14, 34])
acts = [
    (1, "Concept note", "Financial requirement — unit cost sentence",
     "The build-up: ₱2,775 bill of materials, plus battery protection, charging and the "
     "production allowance, = ₱3,400 components; + ₱600 assembly = ₱4,000 fully loaded.",
     "Done", "In the 6 Nov note."),
    (2, "Concept note", "Production working capital",
     "Same bridge, one clause: ₱3,400 of components — the ₱2,775 bill of materials plus "
     "battery protection, charging and the production allowance.", "Done", "In the 6 Nov note."),
    (3, "Business model canvas", "Cost structure block",
     "UNIT COST line reads ₱2,775 + ₱625 + ₱600 = ~₱4,000.", "Check",
     "Check Figure 8 in the 6 Nov note."),
    (4, "83-page paper", "Prototype cost",
     "Add the line distinguishing ₱2,094.47 (earlier build) from ₱2,775.00 (current build, "
     "adds PCB, battery and printed enclosure).", "Not started",
     "Paste-ready; add to the paper revision pack."),
]
r = 5
for a in acts:
    for i, v in enumerate(a, start=1):
        c = ws.cell(row=r, column=i, value=v)
        c.font = BLACK
        c.alignment = Alignment(wrap_text=True, vertical="top")
        c.border = BOX
        if i == 5:
            c.fill = YEL
    ws.row_dimensions[r].height = 58
    r += 1
ws.cell(row=r + 1, column=1,
        value="Status: set each to Done as you apply it. Yellow cells are yours to edit.").font = MUTED

# ═══════════════════════════════════════════════ 3. LOCKED FIGURES
ws = wb.create_sheet("Locked Figures")
title(ws, "Figures that must not move",
      "This revision makes ₱4,000 traceable. It does not change it. Everything here is "
      "unchanged and is referenced across the documents.")
header(ws, 4, ["Figure", "Value", "Where it is used"], [36, 16, 78])
locked = [
    ("Selling price per device", "='Unit Cost Model'!B9",
     "Concept note business model; canvas; deck slide 12; Table 6"),
    ("Fully loaded unit cost", "='Unit Cost Model'!B17",
     "Concept note; canvas; production working capital; deck slide 12"),
    ("Device margin per facility", "='Unit Cost Model'!B22",
     "finpack/model.py — drives every revenue figure"),
    ("Platform subscription per facility per month", 1500,
     "Concept note Table 5; canvas; deck slide 12; tier ladder entry price"),
    ("Monthly contribution per facility", 900,
     "₱1,500 less ₱350 cloud and ₱250 service reserve. finpack/model.py"),
    ("First-year value of one facility", "=B7+B9*12",
     "Device margin ₱4,000 plus twelve months at ₱900"),
    ("Production working capital", 40000,
     "Buys the first batch of ten units at ₱4,000 each. Concept note Table 15"),
    ("School licence per year", 30000, "Institutional teaching licence; separate from the tiers"),
    ("School licence net of platform cost", 25800, "₱30,000 less ₱4,200 annual platform cost"),
]
r = 5
for label, val, where in locked:
    ws.cell(row=r, column=1, value=label).font = BLACK
    c = ws.cell(row=r, column=2, value=val)
    c.font = BLACK if isinstance(val, str) else BLUE
    c.number_format = PESO
    ws.cell(row=r, column=3, value=where).font = MUTED
    for col in range(1, 4):
        ws.cell(row=r, column=col).border = BOX
        ws.cell(row=r, column=col).alignment = Alignment(wrap_text=True, vertical="top")
    r += 1

# ═══════════════════════════════════════════════ 4. OPEN ITEMS
ws = wb.create_sheet("Open Items")
title(ws, "Still yours to resolve", None)
header(ws, 4, ["#", "Item", "Why it matters", "What to do", "Status"],
       [5, 36, 56, 56, 14])
opens = [
    (1, "Battery protection and charging cost",
     "It is the only input that could push the ₱4,000 fully loaded figure up. The bill of "
     "materials excludes it by its own note.",
     "Get a supplier quote for a BMS board and a charging module. Enter it in "
     "'Unit Cost Model'!B6 and read the margin.", "Open"),
    (2, "₱2,094.47 in the 83-page paper",
     "The paper and the concept note currently state different prototype costs with no "
     "explanation. A reviewer comparing them finds a contradiction.",
     "Add the paste-ready line distinguishing the earlier build from the current one to the "
     "paper revision pack.", "Open"),
]
r = 5
for o in opens:
    for i, v in enumerate(o, start=1):
        c = ws.cell(row=r, column=i, value=v)
        c.font = BLACK
        c.alignment = Alignment(wrap_text=True, vertical="top")
        c.border = BOX
        if i == 5:
            c.fill = YEL
    ws.row_dimensions[r].height = 72
    r += 1

out = _BUILD + "/sheet/Resondi-Price-Structure.xlsx"
wb.save(out)
print("saved", out)
