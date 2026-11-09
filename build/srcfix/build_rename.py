"""Resondi — checklist for the places the old name remains that only the owner can change.

The Canva deck and the Drive folder are view-only from Claude's account, and the
certificates are signed records, so this lists exact changes instead of making them.
"""
import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor

INK  = RGBColor(0x1A, 0x1A, 0x1A)
ROSE = RGBColor(0xC2, 0x18, 0x5B)
GREY = RGBColor(0x66, 0x66, 0x66)
FONT = "Calibri"

CANVA = [
 ("5, 6, 9, 10, 11", "Text box reading AUSCULTA. It does not show on the slide (page 5 shows only the Resondi logo), so it is probably behind the logo, but it stays in the file's text.",
  "Delete the text box."),
 ("14, SDG 3.4", "Ausculta: earlier, comparable heart and lung checks.", "Resondi: earlier, comparable heart and lung checks."),
 ("14, SDG 3.8", "Ausculta: doctor review for RHUs with no resident doctor.", "Resondi: doctor review for RHUs with no resident doctor."),
 ("14, SDG 3.c", "Ausculta: guided exams that nurses and midwives can repeat.", "Resondi: guided exams that nurses and midwives can repeat."),
 ("31", "recordings from Ausculta hardware matched clinician labels", "recordings from Resondi hardware matched clinician labels"),
 ("42", "Represented AUSCULTA at the DICT Competition", "Represented RESONDI at the DICT Competition"),
 ("19, 20, 31, 33, 34, 35, 36, 40, notes", "Speaker notes say Ausculta in the old script lines.",
  "Clear these notes. They are old revision notes, and page 38's still says ₱300,000 and page 39's mentions seven other members, so clear those too. Use the Pitch Script (03) to speak from."),
]

DRIVE = [
 ("Certification letter: CERTIFICATE, 2, 3, 4 and Certificate of Validation (5 images)",
  "Signed and dated 21 August 2026. The study title reads “Ausculta: A Smart Digital Auscultation…”.",
  "Do not edit. Ask each doctor to sign a new copy with the Resondi title, or attach the note below."),
 ("Survey form and results: Survey Validation - Dr. K Lim.docx",
  "Completed by the validator. Title and description say Ausculta; device name says Resondi.",
  "Do not edit the completed form. Use a Resondi title on any new form, or attach the note below."),
 ("Letters: resondi letters (need signitures).pdf",
  "Already says Resondi.", "No name change needed."),
 ("Letters: Permission Papers (1) and (2).pdf",
  "No product name; they say “a smart stethoscope”.", "No change needed."),
 ("Documentations: 3d casing and 3d model (6 .webp images)",
  "Could not be read as text.", "Look through them for the old name."),
 ("flowchart, Transcriptions, Validation form, Logbook",
  "No files visible from this account.", "Check them yourself."),
]

doc = Document()
st = doc.styles["Normal"]
st.font.name = FONT
st.font.size = Pt(10.5)
st.paragraph_format.space_after = Pt(0)
sec = doc.sections[0]
sec.left_margin = sec.right_margin = Inches(0.8)
sec.top_margin = sec.bottom_margin = Inches(0.75)


def para(text, *, size=10.5, bold=False, italic=False, color=INK, after=6, before=0):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.space_before = Pt(before)
    r = p.add_run(text)
    r.font.name = FONT
    r.font.size = Pt(size)
    r.bold, r.italic = bold, italic
    r.font.color.rgb = color


def table(head, rows, widths):
    t = doc.add_table(rows=len(rows) + 1, cols=len(head))
    t.style = "Table Grid"
    t.autofit = False
    for i, row in enumerate([head] + rows):
        for j, v in enumerate(row):
            p = t.cell(i, j).paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(v)
            r.font.name = FONT
            r.font.size = Pt(9.5)
            r.bold = i == 0 or j == len(head) - 1
            t.cell(i, j).width = widths[j]
    para("", after=4)


para("Resondi · Rename Checklist", size=16, bold=True, color=ROSE, after=2)
para("Where “Ausculta” remains and only you can change it, 6 November 2026", size=10, italic=True,
     color=GREY, after=10)
para("The Canva deck and the Drive folder are view-only from Claude’s account, so neither was "
     "changed. Everything Claude could change in this folder is already renamed.", after=10)

para("1 · Canva deck: RESONDI (FINAL), 43 pages", size=12.5, bold=True, color=ROSE, after=4)
table(("Page", "Now", "Change to"), CANVA, (Inches(1.1), Inches(2.9), Inches(2.9)))

para("2 · Drive folder", size=12.5, bold=True, color=ROSE, after=4, before=6)
table(("File", "What it says", "What to do"), DRIVE, (Inches(2.3), Inches(2.3), Inches(2.3)))
para("Why the certificates stay as they are", size=11, bold=True, color=ROSE, after=3)
para("A doctor signed that exact wording. Changing the name on a signed certificate would make it "
     "say something the doctor did not sign, even though the study is the same. A judge may also "
     "compare it with the original.", after=6)
para("Note to attach if you do not get new copies", size=11, bold=True, color=ROSE, after=3)
para("“These certificates were issued in August 2026 under the study’s earlier working title, "
     "Ausculta. The study and device have since been renamed Resondi. The certificates are "
     "reproduced as signed.”", italic=True, after=6)

para("3 · Live app (Base44)", size=12.5, bold=True, color=ROSE, after=4, before=6)
para("The app’s page tags still point to ausculta.base44.app. Paste this into Base44:", after=4)
para("“Replace every use of the old name Ausculta in the page title, meta description, Open Graph "
     "tags and canonical URL with Resondi, and set the canonical URL to https://resondi.base44.app. "
     "Do not change the word auscultation anywhere.”", italic=True, after=6)

para("4 · Other places", size=12.5, bold=True, color=ROSE, after=4, before=6)
para("83-page research paper: use the rename item in the Paper Revision Pack (07), which covers 65 "
     "occurrences and warns against changing “auscultation”.", after=3)
para("Old drafts named Ausculta in your Downloads folder and Ausculta.apk: not changed. They are "
     "earlier versions, and an app’s installed name has to be changed in the app and rebuilt.", after=3)

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                                    "final", "14-Resondi-Rename-Checklist.docx"))
doc.save(OUT)
print("saved", OUT)
