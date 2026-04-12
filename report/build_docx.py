#!/usr/bin/env python3
"""Build report.docx from report.md using python-docx with precise formatting."""

import copy
import os
import re
from pathlib import Path

from docx import Document
from docx.shared import Pt, Cm, Twips
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

REPORT_DIR = Path(__file__).parent
MD_FILE = REPORT_DIR / "report.md"
FIGURES_DIR = REPORT_DIR / "figures"
TEMPLATE_FILE = REPORT_DIR.parent / "课程设计报告模板.docx"
OUTPUT_FILE = REPORT_DIR / "report.docx"

# scienceplots figures use 12cm, everything else 15cm
SCIENCEPLOTS_FIGURES = {
    "zipf_distribution.png",
    "df_distribution.png",
    "doc_length_distribution.png",
    "top20_terms.png",
}


# ── helpers ──────────────────────────────────────────────────────────────────

def _ensure_rPr(element):
    rPr = element.find(qn("w:rPr"))
    if rPr is None:
        rPr = OxmlElement("w:rPr")
        element.insert(0, rPr)
    return rPr


def _set_rFonts(rPr, ascii="Times New Roman", east_asia="宋体"):
    rf = rPr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rPr.insert(0, rf)
    if ascii:
        rf.set(qn("w:ascii"), ascii)
        rf.set(qn("w:hAnsi"), ascii)
    if east_asia:
        rf.set(qn("w:eastAsia"), east_asia)


def _set_sz(rPr, half_points):
    """Set font size in half-points (e.g. 24 = 12pt)."""
    for tag in ("w:sz", "w:szCs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = OxmlElement(tag)
            rPr.append(el)
        el.set(qn("w:val"), str(half_points))


def _set_bold(rPr, val=True):
    b = rPr.find(qn("w:b"))
    if val:
        if b is None:
            b = OxmlElement("w:b")
            rPr.append(b)
    else:
        if b is not None:
            rPr.remove(b)


def _set_italic(rPr, val=True):
    i = rPr.find(qn("w:i"))
    if val:
        if i is None:
            i = OxmlElement("w:i")
            rPr.append(i)
    else:
        if i is not None:
            rPr.remove(i)


def _ensure_pPr(para):
    pPr = para._element.find(qn("w:pPr"))
    if pPr is None:
        pPr = OxmlElement("w:pPr")
        para._element.insert(0, pPr)
    return pPr


def _set_spacing(pPr, before=None, after=None, line=None):
    sp = pPr.find(qn("w:spacing"))
    if sp is None:
        sp = OxmlElement("w:spacing")
        pPr.append(sp)
    if before is not None:
        sp.set(qn("w:before"), str(before))
    if after is not None:
        sp.set(qn("w:after"), str(after))
    if line is not None:
        sp.set(qn("w:line"), str(line))
        sp.set(qn("w:lineRule"), "auto")


def _set_jc(pPr, val):
    jc = pPr.find(qn("w:jc"))
    if jc is None:
        jc = OxmlElement("w:jc")
        pPr.append(jc)
    jc.set(qn("w:val"), val)


def _set_indent(pPr, first_line_chars=None, first_line=None):
    ind = pPr.find(qn("w:ind"))
    if ind is None:
        ind = OxmlElement("w:ind")
        pPr.append(ind)
    if first_line_chars is not None:
        ind.set(qn("w:firstLineChars"), str(first_line_chars))
    if first_line is not None:
        ind.set(qn("w:firstLine"), str(first_line))


def _clear_indent(pPr):
    ind = pPr.find(qn("w:ind"))
    if ind is not None:
        pPr.remove(ind)


def make_run(text, ascii="Times New Roman", east_asia="宋体", sz=24,
             bold=False, italic=False):
    """Create a w:r element with formatting."""
    r = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    r.insert(0, rPr)
    _set_rFonts(rPr, ascii=ascii, east_asia=east_asia)
    _set_sz(rPr, sz)
    if bold:
        _set_bold(rPr)
    if italic:
        _set_italic(rPr)
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    r.append(t)
    return r


# ── paragraph builders ───────────────────────────────────────────────────────

def _add_inline_runs(para, text, default_sz=24, default_ascii="Times New Roman",
                     default_east="宋体"):
    """Parse inline markdown (**bold**, `code`, $math$) into runs."""
    pattern = re.compile(r'(\*\*(.+?)\*\*|`([^`]+)`|\$([^$]+)\$)')
    pos = 0
    for m in pattern.finditer(text):
        if m.start() > pos:
            para._element.append(make_run(text[pos:m.start()], sz=default_sz,
                                          ascii=default_ascii, east_asia=default_east))
        if m.group(2):  # bold
            para._element.append(make_run(m.group(2), sz=default_sz, bold=True,
                                          ascii=default_ascii, east_asia=default_east))
        elif m.group(3):  # inline code
            para._element.append(make_run(m.group(3), sz=default_sz,
                                          ascii="Courier New", east_asia=default_east))
        elif m.group(4):  # inline math
            para._element.append(make_run(m.group(4), sz=default_sz, italic=True,
                                          ascii=default_ascii, east_asia=default_east))
        pos = m.end()
    if pos < len(text):
        para._element.append(make_run(text[pos:], sz=default_sz,
                                      ascii=default_ascii, east_asia=default_east))


def add_body_para(doc, text):
    """Normal body paragraph: 12pt, first-line indent 2 chars."""
    p = doc.add_paragraph()
    pPr = _ensure_pPr(p)
    _set_indent(pPr, first_line_chars=200, first_line=480)
    _add_inline_runs(p, text)
    return p


def add_unindented_para(doc, text):
    """Paragraph without indent (list items etc.)."""
    p = doc.add_paragraph()
    pPr = _ensure_pPr(p)
    _clear_indent(pPr)
    _add_inline_runs(p, text)
    return p


def add_heading2(doc, text):
    """H2: sz=32 (16pt), bold, 宋体+TNR, before=260 after=260 line=416, no indent."""
    p = doc.add_paragraph()
    pPr = _ensure_pPr(p)
    _set_spacing(pPr, before=260, after=260, line=416)
    _clear_indent(pPr)
    p._element.append(make_run(text, sz=32, bold=True))
    return p


def add_heading3(doc, text):
    """H3: sz=32 (16pt), bold, before=260 after=260 line=416, no indent."""
    p = doc.add_paragraph()
    pPr = _ensure_pPr(p)
    _set_spacing(pPr, before=260, after=260, line=416)
    _clear_indent(pPr)
    p._element.append(make_run(text, sz=32, bold=True))
    return p


def add_heading4(doc, text):
    """H4: sz=28 (14pt), bold, 宋体+TNR, before=280 after=290 line=376, no indent."""
    p = doc.add_paragraph()
    pPr = _ensure_pPr(p)
    _set_spacing(pPr, before=280, after=290, line=376)
    _clear_indent(pPr)
    p._element.append(make_run(text, sz=28, bold=True))
    return p


def add_abstract_title(doc, text):
    """Abstract title: sz=28 (14pt), bold, 黑体, centered."""
    p = doc.add_paragraph()
    pPr = _ensure_pPr(p)
    _set_jc(pPr, "center")
    _clear_indent(pPr)
    p._element.append(make_run(text, sz=28, bold=True, east_asia="黑体"))
    return p


def add_figure(doc, img_path, caption):
    """Insert image centered + caption below."""
    filename = os.path.basename(img_path)
    width = Cm(12) if filename in SCIENCEPLOTS_FIGURES else Cm(15)

    # Image paragraph
    p = doc.add_paragraph()
    pPr = _ensure_pPr(p)
    _set_jc(pPr, "center")
    _clear_indent(pPr)
    run = p.add_run()
    run.add_picture(str(img_path), width=width)

    # Caption paragraph: sz=21 (10.5pt), centered
    cap = doc.add_paragraph()
    cpPr = _ensure_pPr(cap)
    _set_jc(cpPr, "center")
    _clear_indent(cpPr)
    cap._element.append(make_run(caption, sz=21))
    return p


def add_code_block(doc, lines):
    """Code block: Courier New 9pt (sz=18), no indent, tight spacing."""
    for line in lines:
        p = doc.add_paragraph()
        pPr = _ensure_pPr(p)
        _clear_indent(pPr)
        _set_spacing(pPr, before=0, after=0, line=260)
        p._element.append(make_run(line if line else " ", sz=18,
                                    ascii="Courier New", east_asia="宋体"))


def add_math_block(doc, text):
    """Display math: italic, centered, 12pt."""
    p = doc.add_paragraph()
    pPr = _ensure_pPr(p)
    _set_jc(pPr, "center")
    _clear_indent(pPr)
    p._element.append(make_run(text, sz=24, italic=True))
    return p


def add_page_break(doc):
    p = doc.add_paragraph()
    pPr = _ensure_pPr(p)
    _clear_indent(pPr)
    r = OxmlElement("w:r")
    br = OxmlElement("w:br")
    br.set(qn("w:type"), "page")
    r.append(br)
    p._element.append(r)
    return p


# ── page / style setup ───────────────────────────────────────────────────────

def setup_page(doc):
    s = doc.sections[0]
    s.page_width = Twips(11906)
    s.page_height = Twips(16838)
    s.top_margin = Twips(1701)
    s.bottom_margin = Twips(1418)
    s.left_margin = Twips(1588)
    s.right_margin = Twips(1418)


def setup_normal_style(doc):
    """Normal: 12pt/sz24, 宋体+TNR, line=360/auto, jc=both."""
    style_el = doc.styles["Normal"].element
    # rPr
    rPr = _ensure_rPr(style_el)
    _set_rFonts(rPr, ascii="Times New Roman", east_asia="宋体")
    _set_sz(rPr, 24)
    # pPr
    pPr = style_el.find(qn("w:pPr"))
    if pPr is None:
        pPr = OxmlElement("w:pPr")
        style_el.append(pPr)
    _set_spacing(pPr, line=360)
    _set_jc(pPr, "both")


# ── markdown parser ──────────────────────────────────────────────────────────

def parse_md(text):
    """Return list of (type, content) tuples."""
    lines = text.split("\n")
    elems = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        # blank
        if not line.strip():
            i += 1
            continue

        # hr – skip
        if line.strip() == "---":
            i += 1
            continue

        # page break
        if line.strip() == "\\newpage":
            elems.append(("pagebreak", None))
            i += 1
            continue

        # headings (order matters: check #### before ### before ##)
        if line.startswith("#### "):
            elems.append(("h4", line[5:].strip()))
            i += 1
            continue
        if line.startswith("### "):
            elems.append(("h3", line[4:].strip()))
            i += 1
            continue
        if line.startswith("## "):
            title = line[3:].strip()
            if title.startswith("摘") or title == "Abstract":
                elems.append(("abstract_title", title))
            else:
                elems.append(("h2", title))
            i += 1
            continue

        # figure
        fm = re.match(r'^!\[(图\s*\d+\s+.+?)\]\((.+?)\)$', line)
        if fm:
            elems.append(("figure", (fm.group(1), fm.group(2))))
            i += 1
            continue

        # code block
        if line.strip().startswith("```"):
            code = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            if i < n:
                i += 1  # skip closing ```
            elems.append(("code", code))
            continue

        # display math $$...$$
        if line.strip().startswith("$$"):
            content = line.strip()[2:]
            if content.endswith("$$") and len(content) > 2:
                elems.append(("math", content[:-2].strip()))
                i += 1
                continue
            parts = []
            if content.strip():
                parts.append(content.strip())
            i += 1
            while i < n:
                l = lines[i].strip()
                if l.endswith("$$"):
                    rest = l[:-2].strip()
                    if rest:
                        parts.append(rest)
                    i += 1
                    break
                parts.append(l)
                i += 1
            elems.append(("math", " ".join(parts)))
            continue

        # list item
        if re.match(r'^(\d+\.\s+|- )', line):
            elems.append(("list_item", line.strip()))
            i += 1
            continue

        # normal paragraph – collect consecutive non-special lines
        para_lines = [line]
        i += 1
        while i < n:
            nl = lines[i]
            if not nl.strip():
                break
            if (nl.startswith("#") or nl.startswith("!") or nl.startswith("```") or
                nl.strip().startswith("$$") or nl.strip() == "---" or
                nl.strip() == "\\newpage" or re.match(r'^(\d+\.\s+|- )', nl)):
                break
            para_lines.append(nl)
            i += 1
        elems.append(("paragraph", " ".join(l.strip() for l in para_lines)))

    return elems


# ── cover page from template ─────────────────────────────────────────────────

def insert_cover(doc, template_path):
    """Copy first 14 paragraphs from template into doc, fix title + color, then page break."""
    from docx.opc.part import Part
    from docx.opc.package import OpcPackage
    from docx.opc.packuri import PackURI

    tmpl = Document(str(template_path))

    # Collect template image blobs keyed by rId, create NEW image parts with
    # unique names (prefixed "cover_") to avoid collisions with body images.
    rid_map = {}  # old_rid -> new_rid
    for rid, rel in tmpl.part.rels.items():
        if "image" in rel.reltype:
            blob = rel.target_part.blob
            content_type = rel.target_part.content_type
            # Create a new part with a unique name
            old_name = rel.target_part.partname  # e.g. /word/media/image1.png
            ext = os.path.splitext(str(old_name))[1]
            # Find next free image number in doc
            existing = {str(r.target_part.partname) for r2, r in doc.part.rels.items()
                        if "image" in r.reltype} if doc.part.rels else set()
            num = 100  # start at high number to avoid collisions
            while f"/word/media/image{num}{ext}" in existing:
                num += 1
            new_partname = PackURI(f"/word/media/image{num}{ext}")
            new_part = Part(new_partname, content_type, blob, doc.part.package)
            new_rid = doc.part.relate_to(new_part, rel.reltype)
            rid_map[rid] = new_rid

    body = doc.element.body

    for idx in range(14):
        src = tmpl.paragraphs[idx]
        elem = copy.deepcopy(src._element)

        # Remap image rIds
        for blip in elem.findall(".//" + qn("a:blip")):
            old_rid = blip.get(qn("r:embed"))
            if old_rid and old_rid in rid_map:
                blip.set(qn("r:embed"), rid_map[old_rid])

        # Paragraph 4: replace title placeholder, fix color
        if idx == 4:
            title_set = False
            for r in elem.findall(qn("w:r")):
                for t in r.findall(qn("w:t")):
                    if t.text and ("此处" in t.text or "仿宋" in t.text or "题目" in t.text):
                        if not title_set:
                            t.text = "基于Cranfield数据集的信息检索系统"
                            title_set = True
                        else:
                            t.text = ""
                    elif t.text and t.text.strip() == "" and title_set:
                        t.text = ""
                rPr = r.find(qn("w:rPr"))
                if rPr is not None:
                    col = rPr.find(qn("w:color"))
                    if col is not None and col.get(qn("w:val")) == "FF0000":
                        col.set(qn("w:val"), "000000")

        body.insert(idx, elem)

    # Page break after cover (index 14)
    pb = OxmlElement("w:p")
    pb_r = OxmlElement("w:r")
    pb_br = OxmlElement("w:br")
    pb_br.set(qn("w:type"), "page")
    pb_r.append(pb_br)
    pb.append(pb_r)
    body.insert(14, pb)


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    md = MD_FILE.read_text("utf-8")
    elements = parse_md(md)
    print(f"Parsed {len(elements)} elements from markdown")

    doc = Document()
    setup_page(doc)
    setup_normal_style(doc)

    # Remove default empty paragraph
    if doc.paragraphs:
        doc.element.body.remove(doc.paragraphs[0]._element)

    # Build body
    for etype, content in elements:
        if etype == "pagebreak":
            add_page_break(doc)
        elif etype == "abstract_title":
            add_abstract_title(doc, content)
        elif etype == "h2":
            add_heading2(doc, content)
        elif etype == "h3":
            add_heading3(doc, content)
        elif etype == "h4":
            add_heading4(doc, content)
        elif etype == "figure":
            caption, rel_path = content
            img = REPORT_DIR / rel_path
            if img.exists():
                add_figure(doc, img, caption)
            else:
                print(f"  WARNING: missing image {img}")
        elif etype == "code":
            add_code_block(doc, content)
        elif etype == "math":
            add_math_block(doc, content)
        elif etype == "list_item":
            add_unindented_para(doc, content)
        elif etype == "paragraph":
            add_body_para(doc, content)

    # Insert cover at beginning (after body is built, so Normal style isn't overridden)
    insert_cover(doc, TEMPLATE_FILE)

    doc.save(str(OUTPUT_FILE))
    print(f"Saved → {OUTPUT_FILE}")
    print(f"Size: {OUTPUT_FILE.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
