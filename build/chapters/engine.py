"""Edit operations on a chapter .docx that keep its formatting and log every change.

Every edit goes through Chapter, so the revision log cannot drift from the documents.
Text is set on w:t elements only, so drawings anchored in a run survive.
"""
import copy
import re
import zipfile
import os
import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

PAT = re.compile(r"\b(AUSCULTA|Ausculta|ausculta)\b")


def _sub(m):
    w = m.group(1)
    return "RESONDI" if w.isupper() else ("Resondi" if w[0].isupper() else "resondi")


class Chapter:
    def __init__(self, src, label):
        self.d = docx.Document(src)
        self.label = label
        self.log = []          # (section, action, was, now, why)
        self.section = "Front matter"

    # ---- finding ----
    def paras(self):
        return self.d.paragraphs

    def find(self, prefix, occ=0):
        hits = [p for p in self.paras() if p.text.strip().startswith(prefix)]
        assert len(hits) > occ, (self.label, "not found", prefix[:70])
        return hits[occ]

    # ---- low-level text ----
    @staticmethod
    def _set_text(p, text):
        runs = [r for r in p.runs if r._r.findall(qn("w:t"))]
        assert runs, ("no text runs", text[:50])
        # A bold lead-in ("Problem.", "H₁ (Alternative Hypothesis):") stays bold when the new text keeps it.
        bold = []
        for r in runs:
            if r.bold and r.text:
                bold.append(r)
            elif r.text:
                break
        lead_text = "".join(r.text for r in bold)
        keep = bool(lead_text.strip()) and text.startswith(lead_text.strip()) and len(bold) < len(runs)
        rest = runs[len(bold):] if keep else runs
        body = max(rest, key=lambda r: len(r.text))
        if keep:
            text = text[len(lead_text):] if text.startswith(lead_text) else " " + text[len(lead_text.strip()):].lstrip()
        for r in rest:
            for t in r._r.findall(qn("w:t")):
                t.text = ""
        ts = body._r.findall(qn("w:t"))
        ts[0].text = text
        ts[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        if "[CONFIRM" in text:
            Chapter._highlight(body)

    @staticmethod
    def _highlight(run):
        """Split a run around [CONFIRM ...] markers and highlight those pieces yellow."""
        text = run.text
        parts = re.split(r"(\[CONFIRM[^\]]*\])", text)
        anchor = run._r
        for t in anchor.findall(qn("w:t")):
            t.text = ""
        for part in parts:
            if not part:
                continue
            r = copy.deepcopy(run._r)
            for t in r.findall(qn("w:t")) + r.findall(qn("w:br")):
                r.remove(t)
            t = OxmlElement("w:t")
            t.text = part
            t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            r.append(t)
            if part.startswith("[CONFIRM"):
                rpr = r.find(qn("w:rPr"))
                if rpr is None:
                    rpr = OxmlElement("w:rPr")
                    r.insert(0, rpr)
                h = OxmlElement("w:highlight")
                h.set(qn("w:val"), "yellow")
                rpr.append(h)
            anchor.addnext(r)
            anchor = r

    # ---- operations ----
    def sec(self, name):
        self.section = name

    def rep(self, prefix, new, why, action="Revised", occ=0):
        p = self.find(prefix, occ)
        old = p.text.strip()
        self._set_text(p, new)
        self.log.append((self.section, action, old, new, why))
        return p

    def head_body(self, prefix, head, body, why):
        """A heading run followed by a line break and a body run, in one paragraph."""
        p = self.find(prefix)
        old = p.text.strip()
        runs = [r for r in p.runs if r._r.findall(qn("w:t"))]
        runs[0]._r.findall(qn("w:t"))[0].text = head
        t = runs[1]._r.findall(qn("w:t"))[0]
        t.text = body
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        if "[CONFIRM" in body:
            self._highlight(runs[1])
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT  # justified text stretches a short line ending in a break
        self.log.append((self.section, "Replaced", old, head + ": " + body, why))

    def delete_math(self, why):
        """Remove paragraphs holding an equation."""
        M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath"
        for p in self.paras():
            if p._p.findall(".//" + M):
                p._p.getparent().remove(p._p)
                self.log.append((self.section, "Removed", "Equation", "", why))

    def sub(self, prefix, old, new, why, occ=0):
        p = self.find(prefix, occ)
        full = p.text
        assert full.count(old) >= 1, (self.label, "substring missing", old[:70])
        self._set_text(p, full.replace(old, new))
        self.log.append((self.section, "Revised", old, new, why))

    def add_after(self, para, text, why, like=None):
        el = copy.deepcopy((like or para)._p)
        for bad in list(el.iter(qn("w:drawing"))) + list(el.iter(qn("w:pict"))):
            bad.getparent().remove(bad)
        para._p.addnext(el)
        new = docx.text.paragraph.Paragraph(el, para._parent)
        self._set_text(new, text)
        self.log.append((self.section, "Added", "", text, why))
        return new

    def _text_of(self, plist):
        return " / ".join(p.text.strip() for p in plist if p.text.strip())

    def delete_range(self, start, end_before, why, occ=0, end_occ=0):
        """Delete from the paragraph starting `start` up to, not including, `end_before`."""
        ps = self.paras()
        a = ps.index(self.find(start, occ)) if False else [i for i, p in enumerate(ps) if p._p is self.find(start, occ)._p][0]
        b = [i for i, p in enumerate(ps) if p._p is self.find(end_before, end_occ)._p][0]
        assert b > a, (start, end_before)
        victims = ps[a:b]
        text = self._text_of(victims)
        for p in victims:
            p._p.getparent().remove(p._p)
        self.log.append((self.section, "Removed", text, "", why))

    def delete(self, prefix, why, occ=0):
        p = self.find(prefix, occ)
        self.log.append((self.section, "Removed", p.text.strip(), "", why))
        p._p.getparent().remove(p._p)

    def replace_textbox(self, old, new, why):
        n = 0
        for box in self.d.element.body.iter(qn("w:txbxContent")):
            for t in box.iter(qn("w:t")):
                if t.text and t.text.strip() == old:
                    t.text = new
                    n += 1
        assert n, ("textbox", old)
        self.log.append((self.section, "Revised", old + " (diagram box)", new, why))

    # ---- finish ----
    def save(self, out):
        self.d.save(out)
        tmp, hits = out + ".tmp", 0
        with zipfile.ZipFile(out) as a, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as b:
            for item in a.infolist():
                data = a.read(item.filename)
                if item.filename.endswith((".xml", ".rels")):
                    s, k = PAT.subn(_sub, data.decode("utf-8"))
                    hits += k
                    data = s.encode("utf-8")
                b.writestr(item, data)
        os.replace(tmp, out)
        if hits:
            self.log.append(("Whole chapter", "Revised", "Ausculta", "Resondi",
                             f"Product name changed in {hits} further places. “Auscultation” and related words were left alone."))
        return hits
