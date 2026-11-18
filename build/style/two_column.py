"""Two-column journal layout for the IMRaD (user, 18 Nov 2026: copy the format of the RSTF team paper "AlagaVax",
which sets its body in two columns with full-width figures and tables).

    import two_column
    two_column.apply(doc, title_end, wide_blocks)

title_end    the last paragraph of the one-column title block (title, credits, abstract, keywords)
wide_blocks  (first, last) element pairs, each a figure or table with its caption and note, set across the full
             page width; everything else after the title block flows in two columns.

Word defines a section by the section properties at its END: a paragraph whose pPr holds a sectPr closes the
section above it. So the one-column title block is closed by a continuous one-column break, each run of body text
before a wide block by a continuous two-column break, each wide block by a continuous one-column break, and the
body's final sectPr is made two-column.
"""
import copy

from docx.oxml import OxmlElement
from docx.oxml.ns import qn

GAP_TWIPS = 360   # 0.25 inch between the columns


def _sect(template, cols):
    s = copy.deepcopy(template)
    for el in list(s):
        if el.tag in (qn("w:type"), qn("w:cols"), qn("w:titlePg")):
            s.remove(el)
    t = OxmlElement("w:type")
    t.set(qn("w:val"), "continuous")
    s.find(qn("w:pgSz")).addprevious(t)          # schema order: references, type, pgSz, pgMar, ..., cols, docGrid
    c = OxmlElement("w:cols")
    c.set(qn("w:num"), str(cols))
    c.set(qn("w:space"), str(GAP_TWIPS))
    # w:cols must come before w:docGrid / after w:pgNumType etc.; placing it before docGrid keeps schema order
    grid = s.find(qn("w:docGrid"))
    if grid is not None:
        grid.addprevious(c)
    else:
        s.append(c)
    return s


def _break_after(el, sect):
    """Insert an empty paragraph after el that closes a section with the given properties."""
    p = OxmlElement("w:p")
    ppr = OxmlElement("w:pPr")
    sp = OxmlElement("w:spacing")
    sp.set(qn("w:before"), "0"); sp.set(qn("w:after"), "0"); sp.set(qn("w:line"), "20"); sp.set(qn("w:lineRule"), "exact")
    ppr.append(sp)
    ppr.append(sect)
    p.append(ppr)
    el.addnext(p)
    return p


def apply(doc, title_end, wide_blocks):
    body = doc.element.body
    final = body.find(qn("w:sectPr"))
    template = copy.deepcopy(final)
    # 1. the title block: one column
    _break_after(title_end, _sect(template, 1))
    # 2. each wide block: close the two-column text above it, then close the block itself as one column.
    # Blocks that follow each other with nothing but empty paragraphs between share one one-column section.
    children = list(body)
    pos = {id(el): i for i, el in enumerate(children)}
    blocks = sorted(wide_blocks, key=lambda b: pos[id(b[0])])
    merged = []
    for first, last in blocks:
        if merged:
            a = pos[id(merged[-1][1])]
            between = children[a + 1:pos[id(first)]]
            if all(el.tag == qn("w:p") and not "".join(t.text or "" for t in el.iter(qn("w:t"))).strip()
                   and el.find(".//" + qn("w:drawing")) is None for el in between):
                merged[-1] = (merged[-1][0], last)
                continue
        merged.append((first, last))
    for first, last in merged:
        prev = first.getprevious()
        _break_after(prev, _sect(template, 2))
        _break_after(last, _sect(template, 1))
    # 3. the body's own (last) section: two columns
    for el in list(final):
        if el.tag in (qn("w:cols"), qn("w:type")):
            final.remove(el)
    c = OxmlElement("w:cols")
    c.set(qn("w:num"), "2")
    c.set(qn("w:space"), str(GAP_TWIPS))
    grid = final.find(qn("w:docGrid"))
    if grid is not None:
        grid.addprevious(c)
    else:
        final.append(c)
    t = OxmlElement("w:type"); t.set(qn("w:val"), "continuous")
    final.find(qn("w:pgSz")).addprevious(t)
    return f"{len(merged)} full-width blocks"
