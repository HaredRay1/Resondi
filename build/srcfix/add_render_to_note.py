"""Insert the Blender concept render after Figure 1 of final/01, without renumbering.

The 6 Nov note's builder is not in this folder, so this edits the supplied .docx. When
that builder is supplied, add the same figure there instead. Run once.
"""
import copy
import os
import docx
from docx.shared import Inches
from docx.oxml.ns import qn

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
F = os.path.join(ROOT, "final", "01-Resondi-Concept-Note.docx")
PNG = os.path.join(ROOT, "figures", "Resondi-Device-3D.png")

d = docx.Document(F)
ps = d.paragraphs
assert not any("Concept Render" in p.text for p in ps), "already inserted"
i = next(n for n, p in enumerate(ps) if p.text.strip() == "Figure 1")
label, title = ps[i], ps[i + 1]
img = next(p for p in ps[i + 2:i + 4] if p._p.findall(".//" + qn("w:drawing")))


def clone(src, text):
    el = copy.deepcopy(src._p)
    runs = el.findall(qn("w:r"))
    runs[0].find(qn("w:t")).text = text
    for r in runs[1:]:
        el.remove(r)
    return el


lab2 = clone(label, "Figure 1 (continued)")
tit2 = clone(title, "Concept Render of the Enclosure from the Team’s Blender Model")
note = clone(title, "Note. Proportions and colours are illustrative. Table 1 gives the measured "
                    "enclosure, and the front face and assembly above are drawn from the printed parts.")
pic = d.add_paragraph()
pic.alignment = img.alignment
pic.add_run().add_picture(PNG, width=Inches(4.7))
pic_el = pic._p
pic_el.getparent().remove(pic_el)

anchor = img._p
for el in (lab2, tit2, pic_el, note):
    anchor.addnext(el)
    anchor = el
d.save(F)
print("inserted after Figure 1")
