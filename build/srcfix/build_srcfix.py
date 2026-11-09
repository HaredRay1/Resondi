"""Resondi — paste-ready corrections for the user's own source documents.

The spec sheet and the bill of materials are the user's documents ("do not edit
directly, provide the revised part here"), so this builds a sheet of exact
current-text / replacement-text pairs instead of touching them.
"""
import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT

INK  = RGBColor(0x1A, 0x1A, 0x1A)
ROSE = RGBColor(0xC2, 0x18, 0x5B)
GREY = RGBColor(0x66, 0x66, 0x66)
FONT = "Calibri"

SPEC = [
 ("Cover banner, STORAGE box",
  "Up to 32 GB microSD",
  "16 GB microSD"),
 ("Section 4, Storage and Recording Management, last sentence",
  "The stated 32 GB capacity is the target card capacity; usable space depends on card "
  "formatting and filesystem overhead.",
  "The fitted card is 16 GB; usable space depends on card formatting and filesystem "
  "overhead. At about 480 kB per recording, 16 GB holds more than 30,000 recordings."),
 ("Section 2 table, row “Specified storage capacity”",
  "32 GB",
  "16 GB"),
 ("Section 2 table, row “Enclosure”",
  "Custom 3D-printed PETG plastic",
  "Custom 3D-printed PLA plastic"),
 ("Section 4 table, row “Specified capacity”",
  "32 GB",
  "16 GB"),
 ("Section 7 table, row “Enclosure material”",
  "PETG thermoplastic",
  "PLA thermoplastic"),
 ("Section 9, Specification Notes, storage note",
  "The 32 GB storage capacity is the specified microSD capacity. Confirm the exact card "
  "model and filesystem compatibility in the final hardware build.",
  "The 16 GB storage capacity is the fitted microSD card. Confirm the exact card model "
  "and filesystem compatibility in the final hardware build."),
 ("Section 9, Specification Notes — ADD as a new note after the storage note",
  "(nothing)",
  "The PLA enclosure softens at around 60 °C, a temperature the inside of a parked "
  "vehicle can reach in direct sun. It is a prototype enclosure; keep the device out of "
  "parked vehicles and direct sunlight. A heat-resistant enclosure is part of the planned "
  "hardware refinement."),
]

BOM = [
 ("Item 5, Name",
  "1.3-inch OLED Display",
  "20 × 4 Character LCD (I2C)"),
 ("Item 5, Detailed Description and Specifications",
  "128 × 64 pixel monochrome OLED; I2C/SPI interface; commonly available with "
  "SH1106-compatible driver.",
  "20-column × 4-row character LCD with I2C backpack module; backlit."),
 ("Item 9, Detailed Description and Specifications",
  "8 GB microSD memory card; FAT32-compatible.",
  "16 GB microSD memory card; FAT32-compatible."),
 ("Item 11, Function / Purpose in the System",
  "Physical input controls for heart sound and lung sound recording, plus one additional "
  "control.",
  "Physical input controls for heart sound and lung sound recording."),
 ("Technical Notes, “Push buttons” bullet",
  "Push buttons: Three buttons are budgeted for heart recording, lung recording, and one "
  "additional control. The rocker switch is the main power switch.",
  "Push buttons: Two buttons are budgeted, for heart recording and lung recording. The "
  "rocker switch is the main power switch."),
]

doc = Document()
st = doc.styles["Normal"]
st.font.name = FONT
st.font.size = Pt(10.5)
st.paragraph_format.space_after = Pt(0)
sec = doc.sections[0]
sec.left_margin = sec.right_margin = Inches(0.8)
sec.top_margin = sec.bottom_margin = Inches(0.75)


def para(text="", *, size=10.5, bold=False, italic=False, color=INK, after=6, before=0):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.space_before = Pt(before)
    if text:
        r = p.add_run(text)
        r.font.name = FONT
        r.font.size = Pt(size)
        r.bold, r.italic = bold, italic
        r.font.color.rgb = color
    return p


def cell(c, text, *, bold=False, color=INK, size=9.5):
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(text)
    r.font.name = FONT
    r.font.size = Pt(size)
    r.bold = bold
    r.font.color.rgb = color


def table(rows):
    t = doc.add_table(rows=len(rows) + 1, cols=4)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for j, h in enumerate(("#", "Where", "Current text", "Replace with")):
        cell(t.cell(0, j), h, bold=True)
    for i, (where, cur, new) in enumerate(rows, 1):
        cell(t.cell(i, 0), str(i))
        cell(t.cell(i, 1), where)
        cell(t.cell(i, 2), cur, color=GREY)
        cell(t.cell(i, 3), new, bold=True)
    for row in t.rows:
        for j, w in enumerate((Inches(0.3), Inches(1.6), Inches(2.3), Inches(2.7))):
            row.cells[j].width = w
    para(after=4)


para("Resondi · Source Document Corrections", size=16, bold=True, color=ROSE, after=2)
para("Paste-ready fixes for the product specification sheet and the bill of materials, "
     "2 November 2026", size=10, italic=True, color=GREY, after=10)
para("Both are your documents, so nothing here has been changed in them. Each row gives "
     "the exact current text and what to paste in its place. After these changes, the "
     "spec sheet, the BOM, the concept note (Table 1) and the IMRaD all describe the same "
     "device: PLA casing, 16 GB microSD, 20 × 4 character LCD, two recording buttons.",
     after=10)

para("1 · RESONDI_Product_Specifications.docx", size=12.5, bold=True, color=ROSE, after=4)
para("Two facts were wrong in the sheet: the casing is PLA, not PETG (your correction, "
     "2 Nov), and the fitted card is 16 GB, not 32 GB.", size=10, color=GREY, after=6)
table(SPEC)

para("2 · Resondi_Bill_of_Materials.docx", size=12.5, bold=True, color=ROSE, after=4, before=6)
para("The grand total of ₱2,735.00 does not change: these are label and description fixes "
     "only. The device has a 20 × 4 character LCD, which the cover’s 40 × 98 mm window is "
     "sized for, and two recording buttons, which is also what the BOM already counts "
     "(item 11, 2 pcs).", size=10, color=GREY, after=6)
table(BOM)

para("One price to check", size=11, bold=True, color=ROSE, after=3, before=6)
para("The BOM prices the display at ₱210, which was an OLED price. The research paper "
     "priced the same 20 × 4 LCD at ₱239. If you change item 5 to ₱239, the grand total "
     "becomes ₱2,764.00, and the concept note, price workbook and CLAUDE.md must be "
     "updated to match. The fully loaded unit cost stays ₱4,000 either way: the "
     "₱29 comes out of the ₱665 allowance for protection, charging and spares.",
     after=6)

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                                    "deliverables", "Resondi-Source-Document-Corrections.docx"))
doc.save(OUT)
print("saved", OUT, f"\n  {len(SPEC)} spec-sheet items, {len(BOM)} BOM items")
