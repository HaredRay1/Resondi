"""The previous year's paper (SmartSteth, 2025), attached after ISEF Form 7 in the compiled submission.

Form 7 (Continuation/Research Progression Projects) must be accompanied by the previous year's abstract and
research plan; the signed Form 7 ticks that attachment, Year 2025. The user supplied the paper on 14 Nov 2026 as
Downloads\\SmartSteth FINAL.docx, kept privately as Downloads\\Resondi-private\\compile-sources\\SmartSteth-FINAL.docx.

Two layout faults are fixed in the compiled copy only (the user's file is not changed); no text is changed:
  1. Both footers hold a 4-by-2.8-inch group photo anchored 17 inches below the footer line, which Word pulls back
     onto the page. It sits over the text of every page of the body, pushes the page numbers out of the footer, and
     hides about 2,200 of the paper's 6,300 words (the Appendix A interview transcripts): the paper prints as 29
     pages instead of 40. That footer image is removed.
  2. Page numbering restarts at 1 in sections 2 and 3, so the footer would read "Page 14 of 40", then "Page 2 of
     40". Numbering now runs 1 to 40.

    python build/compile/prior_project.py
        -> Resondi-private/compile-sources/SmartSteth-FINAL-compile.docx and .pdf (read by compile_rstf.py)
"""
import os
import re
import subprocess
import zipfile

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRC = os.path.normpath(os.path.join(ROOT, "..", "Resondi-private", "compile-sources"))
IN = os.path.join(SRC, "SmartSteth-FINAL.docx")
OUT = os.path.join(SRC, "SmartSteth-FINAL-compile.docx")
PDF = OUT[:-5] + ".pdf"


def strip_footer_photo(xml):
    """Remove the drawing (with its AlternateContent wrapper, if any) whose anchor holds the photo image9.jpg."""
    hits = [m for m in re.finditer(r"<w:drawing>.*?</w:drawing>", xml, re.S) if 'name="image9.jpg"' in m.group(0)]
    assert len(hits) == 1, f"expected one footer photo, found {len(hits)}"
    s, e = hits[0].span()
    ac_s = xml.rfind("<mc:AlternateContent", 0, s)
    if ac_s != -1 and xml.find("</mc:AlternateContent>", ac_s) > e:
        e = xml.find("</mc:AlternateContent>", ac_s) + len("</mc:AlternateContent>")
        s = ac_s
    out = xml[:s] + xml[e:]
    assert "image9" not in out and out.count("<w:p") == xml.count("<w:p")
    return out


def continuous_page_numbers(xml):
    """Sections 2 and 3 restart page numbering at 1, so the footer reads 'Page 14 of 40' then 'Page 2 of 40'.
    Keep the restart on the first section only."""
    sects = list(re.finditer(r"<w:sectPr\b.*?</w:sectPr>", xml, re.S))
    restarts = [m for m in sects if '<w:pgNumType w:start="1"/>' in m.group(0)]
    assert len(restarts) == 3 and restarts[0].start() == sects[0].start(), len(restarts)
    for m in reversed(restarts[1:]):
        xml = xml[:m.start()] + m.group(0).replace('<w:pgNumType w:start="1"/>', "") + xml[m.end():]
    return xml


def main():
    zin = zipfile.ZipFile(IN)
    footers = [n for n in zin.namelist() if re.fullmatch(r"word/footer\d+\.xml", n)]
    changed = 0
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename in footers and b'name="image9.jpg"' in data:
                data = strip_footer_photo(data.decode("utf-8")).encode("utf-8")
                changed += 1
            elif item.filename == "word/document.xml":
                data = continuous_page_numbers(data.decode("utf-8")).encode("utf-8")
            zout.writestr(item, data)
    assert changed == 2, changed
    ps = (f"$w=New-Object -ComObject Word.Application; $w.Visible=$false; "
          f"$d=$w.Documents.Open('{OUT}',$false,$true); $d.ExportAsFixedFormat('{PDF}',17); "
          f"$n=$d.ComputeStatistics(2); $d.Close($false); $w.Quit(); $n")
    pages = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True,
                           check=True).stdout.strip()
    print(f"wrote {PDF}: {pages} pages; footer photo removed from {changed} footers")


if __name__ == "__main__":
    main()
