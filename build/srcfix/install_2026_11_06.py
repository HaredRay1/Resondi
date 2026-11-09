"""Install the 6 Nov document set into this folder and rename Ausculta -> Resondi.

Everything replaced is kept in history/final-2026-11-02/ first. Run once.
"""
import os
import re
import shutil
import zipfile

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DL = os.path.dirname(ROOT)
OLD = os.path.join(ROOT, "history", "final-2026-11-02")
os.makedirs(OLD, exist_ok=True)

PAT = re.compile(r"\b(AUSCULTA|Ausculta|ausculta|AUSCORA|Auscora|auscora)\b")


def sub(m):
    w = m.group(1)
    return "RESONDI" if w.isupper() else ("Resondi" if w[0].isupper() else "resondi")


def keep(rel):
    src = os.path.join(ROOT, rel)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(OLD, rel.replace("/", "__")))


def install(name, rel):
    src, dst = os.path.join(DL, name), os.path.join(ROOT, rel)
    keep(rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print("installed", rel)


for rel in ("final/01-Resondi-Concept-Note.pdf", "final/03-Resondi-Pitch-Script.pdf",
            "final/14-Resondi-Source-Document-Corrections.docx",
            "final/14-Resondi-Source-Document-Corrections.pdf"):
    keep(rel)
for rel in ("final/14-Resondi-Source-Document-Corrections.docx",
            "final/14-Resondi-Source-Document-Corrections.pdf"):
    os.remove(os.path.join(ROOT, rel))  # superseded; copy kept above

install("Resondi-Concept-Note-FINAL.docx", "final/01-Resondi-Concept-Note.docx")
install("Resondi-Pitch-Script-REVISED.docx", "final/03-Resondi-Pitch-Script.docx")
install("Resondi-Pitch-and-QA-Brief.docx", "final/15-Resondi-Pitch-and-QA-Brief.docx")
install("Resondi-QA-Answer-Bank.docx", "final/16-Resondi-QA-Answer-Bank.docx")
install("Resondi_Concept_Note_PSC_XI_Assessment.docx", "assess/Resondi_Concept_Note_PSC_XI_Assessment.docx")
install("RESONDI_Product_Specifications.docx", "source-material/RESONDI_Product_Specifications.docx")
install("Resondi_Bill_of_Materials_VER2.0.docx", "source-material/Resondi_Bill_of_Materials_VER2.0.docx")
install("subscription-tiers-spec.md", "pricing/subscription-tiers-spec.md")
install("UPDATE-2026-11-03.md", "history/UPDATE-2026-11-03.md")

# Plain-text and Office sources that still carried the product name
md = "source-material/Hypothesis_2_design_and_analysis.md"
keep(md)
p = os.path.join(ROOT, md)
s, n = PAT.subn(sub, open(p, encoding="utf-8").read())
open(p, "w", encoding="utf-8").write(s)
print("renamed", n, md)

for rel in ("source-material/PSC_XI_Compliance_Review.docx",
            "source-material/Pitch-Deck-Revised-Annotated.pptx"):
    keep(rel)
    p = os.path.join(ROOT, rel)
    tmp, total = p + ".tmp", 0
    with zipfile.ZipFile(p) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.endswith((".xml", ".rels")):
                text, k = PAT.subn(sub, data.decode("utf-8"))
                total += k
                data = text.encode("utf-8")
            zout.writestr(item, data)
    os.replace(tmp, p)
    print("renamed", total, rel)

# Handoff: the 6 Nov file wins; keep the 2 Nov one, and say how this folder differs
keep("CLAUDE.md")
note = """# RESONDI — Project Handoff

> **This folder (added 6 Nov).** The handoff below uses cloud paths: `proj/build/...` is this folder's `build/...`. `final/01`, `03`, `15`, `16` are the 6 Nov documents **as supplied**. **Their builders are not in this folder:** `build/cn2/build.js`, `build/script6/` and `build/qa/` here are the 2 Nov versions, so rebuilding from them brings back old facts (₱2,735, cloud not built, free first month). Edit those four documents only after the 6 Nov builders are supplied. `final/02`, `04`, `05`, `06`, `07`, `08`, `13` were built on 2 Nov and predate this handoff. The 2 Nov handoff and replaced files are in `history/final-2026-11-02/`. Windows build setup and PDF export: see that handoff's section B3.

"""
s = open(os.path.join(DL, "CLAUDE.md"), encoding="utf-8").read()
head = "# RESONDI — Project Handoff\n\n"
assert s.replace("\r\n", "\n").startswith(head)
open(os.path.join(ROOT, "CLAUDE.md"), "w", encoding="utf-8").write(note + s.replace("\r\n", "\n")[len(head):])
print("CLAUDE.md written")
