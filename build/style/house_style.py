"""House style for the papers in Ahnyccas papers (user, 14 Nov 2026): Times New Roman 11 pt, justified, consistent
indentation. Called by each builder just before it saves, so a rebuild keeps the format.

    import house_style; house_style.apply(doc)

What it does, outside tables:
  body text        justified, first line indented 0.5", no left indent; a paragraph that continues a sentence
                   (starts in lower case) and a "Keywords" line are not first-line indented
  headings         (Heading/Title styles, or every run bold and short) flush left, or centred if centred already;
                   a numbered heading hangs its number in 0.5"
  captions, notes  (every run italic, or "Note." first) no indent; caption titles flush left, notes justified
  lists            ("1. ", "a) ", "•" first, or Word numbering) left 0.5", the marker hanging 0.25" with a tab
                   after it so wrapped lines align with the text
  references       (after the References heading, or any hanging paragraph) flush left, hanging 0.5"
  centred lines    (title page, figures, figure captions, the plan's flowchart) stay centred, indents cleared
Inside tables: font and size only; cell paragraphs lose first-line and left indents, alignment is kept (justified
text in narrow columns opens wide gaps). Headers and footers: font and size only.
Fonts: every run, style, list number and the document defaults become Times New Roman 11 pt; symbol fonts (bullet
glyphs) are kept.
Line spacing (only when apply(doc, line_spacing=2.0) is asked for; the papers ask, user 14 Nov): every paragraph with
text outside tables gets that spacing. Body text, lists, references, captions and notes lose their extra space
before and after, the usual double-spaced layout, since the doubled line already separates them; headings and centred
lines (title page) keep theirs. Table cells, paragraphs holding a picture, and a text flowchart (centred lines
with arrow lines such as "▼" between them, the plan's Procedures chart) stay as they are: Word multiplies the
height of a line with an inline picture, and a doubled flowchart no longer fits on one page.
"""
import copy
import re

from docx.oxml import OxmlElement
from docx.oxml.ns import qn

FONT = "Times New Roman"
HALF_PTS = "22"  # 11 pt
TW = 1440        # twips per inch
KEEP_FONTS = {"Symbol", "Wingdings", "Wingdings 2", "Wingdings 3", "Cambria Math", "Segoe UI Symbol",
              "Segoe UI Emoji", "Courier New"}

RPR_ORDER = ["ins", "del", "moveFrom", "moveTo", "rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps",
             "strike", "dstrike", "outline", "shadow", "emboss", "imprint", "noProof", "snapToGrid", "vanish",
             "webHidden", "color", "spacing", "w", "kern", "position", "sz", "szCs", "highlight", "u", "effect",
             "bdr", "shd", "fitText", "vertAlign", "rtl", "cs", "em", "lang", "eastAsianLayout", "specVanish",
             "oMath"]
PPR_ORDER = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr",
             "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap",
             "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd", "snapToGrid",
             "spacing", "ind", "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc", "textDirection",
             "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr", "pPrChange"]
LIST_RE = re.compile(r"^(\d{1,2}[.)]|[a-z][.)]|\([a-z0-9]{1,3}\)|[•▪◦‣–-])(\s+)")
REF_HEADS = {"references", "reference list", "works cited", "bibliography", "literature cited"}


def child(parent, tag, order, create=True):
    """The parent's child <w:tag>, created in schema order if missing."""
    el = parent.find(qn("w:" + tag))
    if el is not None or not create:
        return el
    el = OxmlElement("w:" + tag)
    pos = order.index(tag)
    for i, c in enumerate(parent):
        name = c.tag.split("}")[1]
        if name in order and order.index(name) > pos:
            parent.insert(i, el)
            return el
    parent.append(el)
    return el


def set_font(rpr):
    f = child(rpr, "rFonts", RPR_ORDER)
    if f.get(qn("w:ascii")) in KEEP_FONTS:
        return
    for a in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
        f.attrib.pop(qn("w:" + a), None)
    for a in ("ascii", "hAnsi", "eastAsia", "cs"):
        f.set(qn("w:" + a), FONT)
    for tag in ("sz", "szCs"):
        child(rpr, tag, RPR_ORDER).set(qn("w:val"), HALF_PTS)


def run_rpr(r):
    rpr = r.find(qn("w:rPr"))
    if rpr is None:
        rpr = OxmlElement("w:rPr")
        r.insert(0, rpr)
    return rpr


def fonts_in(el):
    for r in el.iter(qn("w:r")):
        set_font(run_rpr(r))
    for ppr in el.iter(qn("w:pPr")):
        rpr = ppr.find(qn("w:rPr"))
        if rpr is not None:
            set_font(rpr)


def on(rpr, tag):
    x = None if rpr is None else rpr.find(qn("w:" + tag))
    return x is not None and x.get(qn("w:val")) not in ("0", "false", "none")


def set_ind(p, left=0.0, first=0.0):
    ppr = p.find(qn("w:pPr"))
    if ppr is None:
        ppr = OxmlElement("w:pPr")
        p.insert(0, ppr)
    ind = child(ppr, "ind", PPR_ORDER)
    ind.attrib.clear()
    ind.set(qn("w:left"), str(round(left * TW)))
    ind.set(qn("w:right"), "0")
    if first < 0:
        ind.set(qn("w:hanging"), str(round(-first * TW)))
    else:
        ind.set(qn("w:firstLine"), str(round(first * TW)))


def set_spacing(p, line=None, before=None, after=None):
    """Line spacing as a multiple (2.0 = double) and space before/after in twips; None leaves a value alone."""
    ppr = p.find(qn("w:pPr"))
    if ppr is None:
        ppr = OxmlElement("w:pPr")
        p.insert(0, ppr)
    sp = child(ppr, "spacing", PPR_ORDER)
    if line is not None:
        sp.set(qn("w:line"), str(round(240 * line)))
        sp.set(qn("w:lineRule"), "auto")
    for side, v in (("before", before), ("after", after)):
        if v is not None:
            sp.set(qn("w:" + side), str(v))
            for a in (side + "Lines", side + "Autospacing"):  # these override before/after in Word
                sp.attrib.pop(qn("w:" + a), None)


TIGHT = {"body", "list", "list_cont", "list2", "reference", "note", "caption"}
ARROWS = set("▼↓⬇▽⇩")


def flowchart(seq, styles):
    """Centred paragraphs that are arrow lines, or sit next to one, in the order of (p, text) pairs given."""
    flow = set()
    for i, (p, t) in enumerate(seq):
        if t and set(t.replace(" ", "")) <= ARROWS:
            for j in (i - 1, i, i + 1):
                if 0 <= j < len(seq) and get_jc(seq[j][0], styles) == "center":
                    flow.add(j)
    return flow


def get_jc(p, styles):
    ppr = p.find(qn("w:pPr"))
    jc = None if ppr is None else ppr.find(qn("w:jc"))
    if jc is not None:
        return jc.get(qn("w:val"))
    return styles.get(style_id(p), {}).get("jc")


def set_jc(p, val):
    ppr = p.find(qn("w:pPr"))
    if ppr is None:
        ppr = OxmlElement("w:pPr")
        p.insert(0, ppr)
    child(ppr, "jc", PPR_ORDER).set(qn("w:val"), val)


def style_id(p):
    ppr = p.find(qn("w:pPr"))
    s = None if ppr is None else ppr.find(qn("w:pStyle"))
    return None if s is None else s.get(qn("w:val"))


def text_runs(p):
    out = []
    for r in p.iter(qn("w:r")):
        t = "".join(x.text or "" for x in r.iter(qn("w:t")))
        if t.strip():
            out.append((r, t))
    return out


def tab_after_marker(p):
    """'1. Text' -> '1.' + tab + 'Text', so a hanging indent lines the wrapped lines up with the text."""
    runs = text_runs(p)
    if not runs:
        return
    r, t = runs[0]
    m = LIST_RE.match(t.lstrip())
    if not m or r.find(qn("w:tab")) is not None:
        return
    ts = r.findall(qn("w:t"))
    if len(ts) != 1:
        return
    lead = len(t) - len(t.lstrip())
    rest = t[lead + m.end():]
    ts[0].text = rest
    if rest != rest.strip():
        ts[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    mark = copy.deepcopy(r)
    for c in list(mark):
        if c.tag != qn("w:rPr"):
            mark.remove(c)
    t_el = OxmlElement("w:t")
    t_el.text = m.group(1)
    mark.append(t_el)
    mark.append(OxmlElement("w:tab"))
    r.addprevious(mark)


BULLETS = "•▪◦‣"


def split_bullet_breaks(p):
    """A paragraph whose lines after each manual line break start with a bullet ('question:' + '• a;' + '• b?')
    becomes one paragraph per line, so each bullet can take a list indent; justified lines that end in a manual
    break would otherwise be stretched across the page. Returns the number of paragraphs added."""
    brs = [b for b in p.iter(qn("w:br")) if b.get(qn("w:type")) in (None, "textWrapping")]
    if not brs or any(c.tag not in (qn("w:pPr"), qn("w:r")) for c in p):
        return 0
    segments = [[]]
    for r in [c for c in p if c.tag == qn("w:r")]:
        rpr, cur = r.find(qn("w:rPr")), None
        for c in list(r):
            if c.tag == qn("w:rPr"):
                continue
            if c.tag == qn("w:br") and c.get(qn("w:type")) in (None, "textWrapping"):
                segments.append([])
                cur = None
                continue
            if cur is None:
                cur = OxmlElement("w:r")
                if rpr is not None:
                    cur.append(copy.deepcopy(rpr))
                segments[-1].append(cur)
            cur.append(copy.deepcopy(c))
    texts = ["".join(x.text or "" for r in seg for x in r.iter(qn("w:t"))).strip() for seg in segments]
    if not all(t[:1] in BULLETS for t in texts[1:]):
        return 0
    ppr = p.find(qn("w:pPr"))
    for c in [c for c in p if c.tag != qn("w:pPr")]:
        p.remove(c)
    for r in segments[0]:
        p.append(r)
    paras, last = [p], p
    for seg in segments[1:]:
        q = OxmlElement("w:p")
        if ppr is not None:
            q.append(copy.deepcopy(ppr))
        for r in seg:
            q.append(r)
        last.addnext(q)
        paras.append(q)
        last = q
    for q in paras[:-1]:  # the lines of one item sit together; the space after stays on the last line
        qp = q.find(qn("w:pPr"))
        if qp is None:
            qp = OxmlElement("w:pPr")
            q.insert(0, qp)
        child(qp, "spacing", PPR_ORDER).set(qn("w:after"), "0")
    return len(paras) - 1


def classify(p, text, styles, in_refs):
    sid = style_id(p) or ""
    sname = styles.get(sid, {}).get("name", "")
    runs = text_runs(p)
    rprs = [r.find(qn("w:rPr")) for r, _ in runs]
    sty_bold = styles.get(sid, {}).get("bold", False)
    all_bold = bool(runs) and all(on(x, "b") or sty_bold for x in rprs)
    all_italic = bool(runs) and all(on(x, "i") for x in rprs)
    ppr = p.find(qn("w:pPr"))
    numbered = ppr is not None and ppr.find(qn("w:numPr")) is not None
    ind = None if ppr is None else ppr.find(qn("w:ind"))
    hanging = ind is not None and ind.get(qn("w:hanging")) not in (None, "0")
    if sname.lower().startswith(("heading", "title", "subtitle")) or (all_bold and len(text) < 200):
        return "heading_num" if numbered else "heading"
    if text.startswith("Note.") or (all_italic and len(text) >= 200) or (all_italic and text.endswith(".")):
        return "note"
    if all_italic:
        return "caption"
    if in_refs:
        return "reference"
    if numbered or LIST_RE.match(text):
        return "list"
    if hanging:
        return "reference"
    return "body"


def apply(doc, line_spacing=None):
    styles = {}
    for s in doc.styles.element.findall(qn("w:style")):
        sid = s.get(qn("w:styleId"))
        name = s.find(qn("w:name"))
        ppr, rpr = s.find(qn("w:pPr")), s.find(qn("w:rPr"))
        jc = None if ppr is None else ppr.find(qn("w:jc"))
        styles[sid] = {"name": "" if name is None else name.get(qn("w:val")),
                       "jc": None if jc is None else jc.get(qn("w:val")), "bold": on(rpr, "b")}
        if s.get(qn("w:type")) in ("paragraph", "character", "table"):
            if rpr is None:
                rpr = OxmlElement("w:rPr")
                s.append(rpr)
            set_font(rpr)
    dd = doc.styles.element.find(qn("w:docDefaults"))
    if dd is not None:
        rd = dd.find(qn("w:rPrDefault"))
        if rd is None:
            rd = OxmlElement("w:rPrDefault")
            dd.insert(0, rd)
        rpr = rd.find(qn("w:rPr"))
        if rpr is None:
            rpr = OxmlElement("w:rPr")
            rd.append(rpr)
        set_font(rpr)
    try:
        for lvl_rpr in doc.part.numbering_part.element.iter(qn("w:rPr")):
            set_font(lvl_rpr)
    except NotImplementedError:
        pass
    for sec in doc.sections:
        for hf in (sec.header, sec.footer, sec.first_page_header, sec.first_page_footer, sec.even_page_header,
                   sec.even_page_footer):
            if not hf.is_linked_to_previous:
                fonts_in(hf._element)

    body = doc.element.body
    fonts_in(body)
    counts = {"split": 0}
    for p in list(body.iter(qn("w:p"))):
        if not {qn("w:tc"), qn("w:txbxContent")} & {a.tag for a in p.iterancestors()}:
            counts["split"] += split_bullet_breaks(p)
    in_refs = False
    prev = None
    numbered_parent = False
    seq = []
    for p in body.iter(qn("w:p")):
        if not {qn("w:tc"), qn("w:txbxContent")} & {a.tag for a in p.iterancestors()}:
            t = "".join(x.text or "" for x in p.iter(qn("w:t"))).strip()
            if t:
                seq.append((p, t))
    flow_ps = [seq[i][0] for i in flowchart(seq, styles)]
    for p in list(body.iter(qn("w:p"))):
        anc = {a.tag for a in p.iterancestors()}
        if qn("w:txbxContent") in anc:
            continue
        text = "".join(x.text or "" for x in p.iter(qn("w:t"))).strip()
        if qn("w:tc") in anc:
            if text:
                set_ind(p, 0, 0)
            continue
        if not text:
            continue
        jc = get_jc(p, styles)
        kind = classify(p, text, styles, in_refs)
        ppr = p.find(qn("w:pPr"))
        ind = None if ppr is None else ppr.find(qn("w:ind"))
        cur_left = float((ind.get(qn("w:left")) or ind.get(qn("w:start")) or 0) if ind is not None else 0) / TW
        if kind in ("body", "note") and prev in ("list", "list_cont") and cur_left >= 0.59:
            kind = "list_cont"  # a description under a list item (the IMRaD's objectives)
        if kind == "list":
            if text[:1] in BULLETS and numbered_parent and prev in ("list", "list2"):
                kind = "list2"  # a bullet under a numbered item (the plan's research questions)
            else:
                numbered_parent = text[:1].isdigit()
        elif kind != "list_cont":
            numbered_parent = False
        if kind in ("heading", "heading_num"):
            in_refs = text.strip().rstrip(":").lower() in REF_HEADS
        if kind == "heading":
            set_ind(p, 0, 0)
            set_jc(p, "center" if jc == "center" else "left")
        elif kind == "heading_num":
            set_ind(p, 0.5, -0.5)
            set_jc(p, "center" if jc == "center" else "left")
        elif jc in ("center", "right"):
            kind = "centred"
            set_ind(p, 0, 0)
        elif kind == "caption":
            set_ind(p, 0, 0)
            set_jc(p, "left")
        elif kind == "note":
            set_ind(p, 0, 0)
            set_jc(p, "both")
        elif kind == "reference":  # hanging 0.5", flush left (user, 14 Nov: long web addresses stretch justified lines)
            set_ind(p, 0.5, -0.5)
            set_jc(p, "left")
        elif kind == "list":
            set_ind(p, 0.5, -0.25)
            set_jc(p, "both")
            if not (p.find(qn("w:pPr")) is not None and p.find(qn("w:pPr")).find(qn("w:numPr")) is not None):
                tab_after_marker(p)
        elif kind == "list_cont":
            set_ind(p, 0.5, 0)
            set_jc(p, "both")
        elif kind == "list2":
            set_ind(p, 0.75, -0.25)
            set_jc(p, "left")
            tab_after_marker(p)
        else:
            no_indent = text[:1].islower() or text.lower().startswith(("keywords", "key words"))
            set_ind(p, 0, 0 if no_indent else 0.5)
            set_jc(p, "both")
        if kind in ("heading", "heading_num", "caption"):  # never strand a heading or caption at a page foot
            child(p.find(qn("w:pPr")), "keepNext", PPR_ORDER)
        if any(p is q for q in flow_ps):
            counts["flowchart"] = counts.get("flowchart", 0) + 1
        elif line_spacing and p.find(".//" + qn("w:drawing")) is None and p.find(".//" + qn("w:pict")) is None:
            if kind in TIGHT:
                set_spacing(p, line_spacing, 0, 0)
            else:
                set_spacing(p, line_spacing)
            counts["spaced"] = counts.get("spaced", 0) + 1
        counts[kind] = counts.get(kind, 0) + 1
        prev = kind
    return counts
