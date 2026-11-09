"""Blinded CirCor heart-sound set for a cardiologist to label.

Source: CirCor DigiScope Phonocardiogram Dataset 1.0.3 (Oliveira et al., 2022), PhysioNet,
Open Data Commons Attribution License v1.0. Reads the downloaded zip; writes:
  heart-validation/           share this: recordings S01..S25, answer sheet, instructions
  ../Resondi-private/heart-validation-key/   keep private: which dataset label each sample carries
                              (outside the project folder, so Drive sync never uploads it)
The cardiologist labels the recordings without seeing the dataset's labels, so their answers
are an independent check of those labels. Run: python build_validation_set.py <path to zip>
"""
import csv
import io
import os
import random
import sys
import wave
import zipfile

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SHARE = os.path.join(ROOT, "heart-validation")
# The answer key lives beside the project, not in it: the project folder is synced to
# Google Drive, and the reviewer must never be able to see the key.
KEY = os.path.join(os.path.dirname(ROOT), "Resondi-private", "heart-validation-key")
PER_CLASS = 5
SEED = 20261109
CITE = ("Oliveira, J., Renna, F., Costa, P. D., Nogueira, M., Oliveira, C., Ferreira, C., Jorge, A., Mattos, S., "
        "Hatem, T., Tavares, T., Elola, A., Rad, A. B., Sameni, R., Clifford, G. D., & Coimbra, M. T. (2022). The CirCor "
        "DigiScope dataset: From murmur detection to murmur classification. IEEE Journal of Biomedical and Health "
        "Informatics, 26(6), 2524–2535. https://doi.org/10.1109/JBHI.2021.3137048")
# Classes match the planned Heart Mode output (CLAUDE.md §6): murmur present or absent, and its timing.
CLASSES = [
    ("No murmur", lambda r: r["Murmur"] == "Absent"),
    ("Holosystolic murmur", lambda r: r["Murmur"] == "Present" and r["Systolic murmur timing"] == "Holosystolic"
     and r["Diastolic murmur timing"] == "nan"),
    ("Early-systolic murmur", lambda r: r["Murmur"] == "Present" and r["Systolic murmur timing"] == "Early-systolic"
     and r["Diastolic murmur timing"] == "nan"),
    ("Mid-systolic murmur", lambda r: r["Murmur"] == "Present" and r["Systolic murmur timing"] == "Mid-systolic"
     and r["Diastolic murmur timing"] == "nan"),
    ("Diastolic murmur (most also systolic)", lambda r: r["Murmur"] == "Present" and r["Diastolic murmur timing"] == "Early-diastolic"),
]


def main(zpath):
    z = zipfile.ZipFile(zpath)
    names = z.namelist()
    base = next(n for n in names if n.endswith("training_data.csv")).rsplit("training_data.csv", 1)[0]
    rows = list(csv.DictReader(io.TextIOWrapper(z.open(base + "training_data.csv"), encoding="utf-8")))
    have = set(names)
    rng = random.Random(SEED)
    picks, used = [], set()
    for label, test in CLASSES:
        pool = [r for r in rows if test(r) and r["Patient ID"] not in used]
        rng.shuffle(pool)
        n = 0
        for r in pool:
            if r["Murmur"] == "Present":
                site = r["Most audible location"]
            else:
                site = rng.choice(r["Recording locations:"].split("+"))
            wav = f"{base}training_data/{r['Patient ID']}_{site}.wav"
            if wav not in have:  # some patients have several takes at a site (_AV_1 ...): skip them
                continue
            picks.append((label, r, site, wav))
            used.add(r["Patient ID"])
            n += 1
            if n == PER_CLASS:
                break
        assert n == PER_CLASS or label.startswith("Diastolic"), (label, n)
    rng.shuffle(picks)

    os.makedirs(os.path.join(SHARE, "recordings"), exist_ok=True)
    os.makedirs(KEY, exist_ok=True)
    key_rows, sheet_rows = [], []
    for i, (label, r, site, wav) in enumerate(picks, 1):
        sid = f"S{i:02d}"
        data = z.read(wav)
        open(os.path.join(SHARE, "recordings", sid + ".wav"), "wb").write(data)
        with wave.open(io.BytesIO(data)) as w:
            secs = w.getnframes() / w.getframerate()
        age = r["Age"] if r["Age"] != "nan" else "Not recorded"
        sheet_rows.append((sid, site, age, round(secs, 1)))
        key_rows.append({"Sample": sid, "Class in this set": label, "Patient ID": r["Patient ID"], "Site": site,
                         "Murmur": r["Murmur"], "Murmur locations": r["Murmur locations"],
                         "Most audible": r["Most audible location"],
                         "Systolic timing": r["Systolic murmur timing"], "Systolic grade": r["Systolic murmur grading"],
                         "Systolic shape": r["Systolic murmur shape"], "Diastolic timing": r["Diastolic murmur timing"],
                         "Diastolic grade": r["Diastolic murmur grading"], "Outcome": r["Outcome"],
                         "Source file": wav.rsplit("/", 1)[1], "Seconds": round(secs, 1)})
    with open(os.path.join(KEY, "answer-key.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(key_rows[0]))
        w.writeheader()
        w.writerows(key_rows)
    answer_sheet(sheet_rows)
    instructions(len(picks))
    from collections import Counter
    print(len(picks), "samples", Counter(k["Class in this set"] for k in key_rows))


HEAD = ["Sample", "Site", "Age group", "Seconds", "Recording usable?", "Murmur heard?", "Timing", "Grade (I–VI)",
        "Confidence", "Comments"]


def answer_sheet(rows):
    wb = Workbook()
    ws = wb.active
    ws.title = "Answers"
    ws.append(HEAD)
    for r in rows:
        ws.append(list(r) + [""] * 6)
    widths = [9, 7, 13, 9, 17, 16, 20, 13, 13, 40]
    thin = Side(style="thin", color="BFBFBF")
    for j, w in enumerate(widths, 1):
        ws.column_dimensions[chr(64 + j)].width = w
        c = ws.cell(row=1, column=j)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="8E2A52")
        c.alignment = Alignment(wrap_text=True, vertical="center")
    for row in ws.iter_rows(min_row=1, max_row=len(rows) + 1):
        for c in row:
            c.border = Border(left=thin, right=thin, top=thin, bottom=thin)
    n = len(rows) + 1
    for col, choices in (("E", "Yes,No"), ("F", "Present,Absent,Cannot tell"),
                         ("G", "Holosystolic,Early-systolic,Mid-systolic,Late-systolic,Diastolic,Systolic and diastolic,Other,Not applicable"),
                         ("H", "I,II,III,IV,V,VI,Not applicable"), ("I", "High,Medium,Low")):
        dv = DataValidation(type="list", formula1=f'"{choices}"', allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"{col}2:{col}{n}")
    ws.freeze_panes = "B2"
    wb.save(os.path.join(SHARE, "Answer-Sheet.xlsx"))
    with open(os.path.join(SHARE, "Answer-Sheet.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(HEAD)
        for r in rows:
            w.writerow(list(r) + [""] * 6)


INSTR = [
    ("h", "Heart Sound Label Review: Instructions for the Reviewing Cardiologist"),
    ("p", "Thank you for helping the Resondi team, Puerto Princesa City National Science High School. We are building a "
          "smart stethoscope that will, in a later version, flag whether a heart murmur is present and when it occurs. "
          "Before training it, we want a cardiologist to check the labels in the public dataset we plan to use."),
    ("h2", "What is in this folder"),
    ("p", "recordings: {n} heart sound recordings, named S01 to S{n:02d}, from the CirCor DigiScope Phonocardiogram "
          "Dataset (Oliveira et al., 2022). They come from children and adolescents in Brazil, recorded with an electronic "
          "stethoscope at the aortic (AV), pulmonic (PV), tricuspid (TV) or mitral (MV) area. Each is between 7 and 32 seconds"
          " long."),
    ("p", "Answer-Sheet.xlsx (also as a Google Sheet): one row per recording, with its site and age group."),
    ("h2", "What we ask"),
    ("p", "Please listen to each recording, ideally with good headphones, and fill in the answer sheet: whether the recording "
          "is usable, whether you hear a murmur, its timing, its grade if you would give one, and how confident you are. Use "
          "the comments for anything else. It should take about 30 to 40 minutes."),
    ("p", "The recordings are deliberately in mixed order and the dataset's own labels are not shown, so that your answers "
          "are an independent check. Please do not look the recordings up in the dataset."),
    ("h2", "What your answers are used for"),
    ("p", "We will compare your labels with the dataset's labels and report how often they agree. This checks the labels we "
          "intend to train on. It is not a test of you, and it does not validate any device or software as a diagnostic tool."),
    ("h2", "About the data"),
    ("p", "The dataset is publicly available on PhysioNet under the Open Data Commons Attribution License v1.0 and contains no "
          "names or other direct identifiers."),
    ("p", "Reference: " + CITE),
]


def instructions(n):
    d = Document()
    d.styles["Normal"].font.name = "Calibri"
    d.styles["Normal"].font.size = Pt(11)
    for kind, text in INSTR:
        text = text.format(n=n)
        p = d.add_paragraph()
        r = p.add_run(text)
        if kind == "h":
            r.bold, r.font.size = True, Pt(15)
            r.font.color.rgb = RGBColor(0x8E, 0x2A, 0x52)
        elif kind == "h2":
            r.bold, r.font.size = True, Pt(12)
            r.font.color.rgb = RGBColor(0x8E, 0x2A, 0x52)
            p.paragraph_format.space_before = Pt(8)
    d.save(os.path.join(SHARE, "Instructions.docx"))
    with open(os.path.join(SHARE, "Instructions.txt"), "w", encoding="utf-8") as f:
        f.write("\n\n".join(t.format(n=n) for _, t in INSTR))


if __name__ == "__main__":
    main(sys.argv[1])
