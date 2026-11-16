"""Final text corrections applied to a built paper just before it is saved (review of 16 Nov 2026).

Many sentences in the papers come from the author's original documents rather than from the builders' own
strings, so these fixes are applied to the finished document. Each (old, new, count) must match exactly `count`
times across body paragraphs and table cells, or the build stops: a fix that silently misses is worse than none.
Formatting is kept: the replacement takes the formatting of the run where the old text starts.
"""
import copy


def _paragraphs(doc):
    for p in doc.paragraphs:
        yield p
    for t in doc.tables:
        for row in t.rows:
            seen = set()
            for c in row.cells:
                if id(c._tc) in seen:
                    continue
                seen.add(id(c._tc))
                for p in c.paragraphs:
                    yield p


def _replace_once(p, old, new):
    runs = p.runs
    text = "".join(r.text for r in runs)
    i = text.find(old)
    if i < 0:
        return False
    j = i + len(old)
    pos = 0
    first = None
    for r in runs:
        a, b = pos, pos + len(r.text)
        pos = b
        if b <= i or a >= j:
            continue
        s, e = max(i, a) - a, min(j, b) - a
        if first is None:
            first = r
            r.text = r.text[:s] + new + r.text[e:]
        else:
            r.text = r.text[:s] + r.text[e:]
    return True


def apply(doc, fixes):
    done = []
    for old, new, count in fixes:
        n = 0
        for p in _paragraphs(doc):
            while old in "".join(r.text for r in p.runs):
                _replace_once(p, old, new)
                n += 1
                if old in new:
                    break
        if n != count:
            raise SystemExit(f"review fix matched {n} times, expected {count}: {old[:70]!r}")
        done.append(n)
    return f"{len(done)} fixes, {sum(done)} replacements"


def insert_after(doc, anchor_text, next_text, model_text):
    """Insert a copy of the first paragraph whose text is model_text after the paragraph anchor_text, when the
    paragraph after it is next_text (used for a missing arrow in the plan's Procedures flowchart)."""
    ps = doc.paragraphs
    # An empty paragraph standing where the arrow belongs is replaced by the arrow.
    gaps = [k for k in range(len(ps) - 2)
            if ps[k].text.strip() == anchor_text and not ps[k + 1].text.strip() and ps[k + 2].text.strip() == next_text]
    if len(gaps) == 1:
        model = next(p for p in ps if p.text.strip() == model_text)
        ps[gaps[0] + 1]._p.addprevious(copy.deepcopy(model._p))
        ps[gaps[0] + 1]._p.getparent().remove(ps[gaps[0] + 1]._p)
        # The step after the gap takes the anchor step's paragraph and run formatting (centred, bold).
        anchor, nxt = ps[gaps[0]], ps[gaps[0] + 2]
        if anchor._p.pPr is not None:
            if nxt._p.pPr is not None:
                nxt._p.remove(nxt._p.pPr)
            nxt._p.insert(0, copy.deepcopy(anchor._p.pPr))
        rpr = anchor.runs[0]._r.rPr if anchor.runs else None
        for r in nxt.runs:
            if r._r.rPr is not None:
                r._r.remove(r._r.rPr)
            if rpr is not None:
                r._r.insert(0, copy.deepcopy(rpr))
        return "1 empty paragraph replaced, last step formatted like the others"
    hits = [k for k in range(len(ps) - 1)
            if ps[k].text.strip() == anchor_text and ps[k + 1].text.strip() == next_text]
    if len(hits) == 1:
        model = next(p for p in ps if p.text.strip() == model_text)
        ps[hits[0]]._p.addnext(copy.deepcopy(model._p))
        return "1 paragraph inserted"
    # The same check on single-column table rows (the plan's flowchart is a table).
    rows = []
    for t in doc.tables:
        rs = list(t.rows)
        for k in range(len(rs) - 1):
            if rs[k].cells[0].text.strip() == anchor_text and rs[k + 1].cells[0].text.strip() == next_text:
                model = next(r for r in rs if r.cells[0].text.strip() == model_text)
                rows.append((rs[k], model))
    if len(rows) != 1 or hits:
        raise SystemExit(f"insert_after matched {len(hits)} paragraphs and {len(rows)} rows: {anchor_text!r}")
    rows[0][0]._tr.addnext(copy.deepcopy(rows[0][1]._tr))
    return "1 table row inserted"
