"""New certificates under the Resondi title, for the doctors to sign themselves.

The signed originals are never edited. Wording follows the signed certificate word for word,
with only the study name changed and one sentence saying so. Signature, date and licence
details stay blank for each doctor to fill in.
"""
import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

ROSE = RGBColor(0x8E, 0x2A, 0x52)
DOCTORS = [("Dr. Sonia Ulanday", "Pulmonologist / Medical Doctor"),
           ("Dr. Kenneth Wilson O. Lim", "Pulmonologist"),
           ("Dr. Riza Cornelle de la Bajan", "Pediatrics / Medical Doctor")]

d = Document()
st = d.styles["Normal"]
st.font.name = "Times New Roman"
st.font.size = Pt(11)
sec = d.sections[0]
sec.left_margin = sec.right_margin = Inches(1)
sec.top_margin = sec.bottom_margin = Inches(0.7)


def P(text="", bold=False, italic=False, size=10.5, after=5, center=False, color=None, font=None):
    p = d.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.0
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.bold, r.italic, r.font.size = bold, italic, Pt(size)
    if color:
        r.font.color.rgb = color
    if font:
        r.font.name = font
    return p


P("Certificates to Re-sign: How to Use This File", True, size=15, color=ROSE, after=4, font="Calibri")
P("Your signed certificates say “Ausculta” and should stay exactly as signed. These are new copies under the Resondi "
  "name, for each doctor to read and sign. Only a doctor should fill in the blanks on their own page.", font="Calibri")
P("Before you send them", True, color=ROSE, after=3, font="Calibri")
for t in ("Check each doctor's name, title and hospital against their signed certificate. Dr. de la Bajan's middle initial was unclear on the scan, so it is left out.",
          "Your Drive folder has five signed certificates from three doctors. This file has one per doctor. Print a second copy if a doctor reviewed two separate sets.",
          "Add your school or the doctor's letterhead if the originals had one. I did not copy any organization's letterhead.",
          "Keep the signed originals. If a doctor cannot re-sign in time, submit the original with this note: “This certificate was issued in August 2026 under the study's earlier working title, Ausculta. The study and device have since been renamed Resondi. The certificate is reproduced as signed.”"):
    P("•  " + t, after=3, font="Calibri")
P("", after=4)
P("Message you can send", True, color=ROSE, after=3, font="Calibri")
P("Good day, Doctor. We are the Resondi team from Puerto Princesa City National Science High School. You kindly reviewed our "
  "respiratory sound samples in August 2026 and signed a certificate for our study, then titled “Ausculta.” The study and device "
  "have since been renamed Resondi, and the samples you reviewed have not changed. We are preparing for the Philippine "
  "Startup Challenge XI nationals. May we ask if you would be willing to sign the attached copy under the new name? Please feel free "
  "to change anything in it. Thank you very much for your help.", italic=True, font="Calibri")

for name, title in DOCTORS:
    d.add_page_break()
    P("CERTIFICATION", True, size=14, center=True, after=3)
    P("CERTIFICATE OF CLINICAL REVIEW, VALIDATION, AND APPROVAL OF RESPIRATORY SOUND SAMPLES", True, center=True, after=12)
    P("To Whom It May Concern:")
    P("This is to certify that the undersigned medical practitioner has reviewed and clinically evaluated the respiratory sound "
      "samples utilized in the research study entitled “Resondi: A Smart Digital Auscultation and Respiratory Sound Analysis "
      "Platform for Respiratory Health Assessment and Rehabilitation Support.” The study was previously titled “Ausculta”; this "
      "certificate is issued under its current name.")
    P("The respiratory sound samples presented for review were evaluated with reference to the ICBHI 2017 Respiratory Sound Database "
      "(International Conference on Biomedical and Health Informatics 2017 Respiratory Sound Classification Challenge) and its "
      "established respiratory sound categories, including normal respiratory sounds, crackles, wheezes, and combined crackles and "
      "wheezes. The ICBHI 2017 database contains respiratory recordings that were annotated by respiratory experts and is widely used "
      "as a benchmark for respiratory sound classification research. After review, the undersigned certifies that the respiratory "
      "sound samples, their corresponding classifications/labels, and the associated descriptions presented by the researchers have been:")
    for t in ("Reviewed for clinical appropriateness and consistency with recognized respiratory sound characteristics,",
              "Validated against the established respiratory sound classifications and clinical interpretation of the undersigned,",
              "Found to be true and correct, to the best of the undersigned's professional knowledge and clinical judgment, with respect to the characteristics and classifications presented,",
              "Approved for use in the researchers' academic/research validation process, subject to the limitations of the available recordings and the intended scope of the study."):
        p = P(t, after=3)
        p.paragraph_format.left_indent = Inches(0.3)
    P("", after=2)
    P("This certification specifically pertains to the clinical review and validation of the respiratory sound samples and their "
      "corresponding classifications. It does not constitute approval, certification, or authorization of the research device, "
      "software, artificial intelligence model, or platform as a medical diagnostic device, nor does it establish that the system can "
      "independently diagnose respiratory diseases.")
    P("This certification is issued upon the request of the researchers for documentation of expert clinical review and validation of "
      "the respiratory sound samples used in the study.", after=12)
    P("Certified by:", after=18)
    P("______________________________ (signature)", after=2)
    P(name, True, after=2)
    P(title, after=2)
    P("PRC License No.: ____________________", after=2)
    P("Specialization: ____________________", after=2)
    P("Institution/Hospital: ____________________", after=10)
    P("Issued this ____ day of ______________, 2026, at Puerto Princesa City, Palawan, Philippines.", after=10)
    P("Reference: Rocha, B. M., et al. (2019). An open access database for the evaluation of respiratory sound classification "
      "algorithms. Physiological Measurement, 40, 035001.", size=9.5, after=2)

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "final",
                                    "17-Resondi-Certificates-to-Re-sign.docx"))
d.save(OUT)
print("saved", OUT)
