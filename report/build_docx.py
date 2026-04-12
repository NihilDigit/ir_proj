"""
Build the final .docx report by:
1. Using pandoc to convert report.md to docx (inherits template styles)
2. Unpacking both template and pandoc output
3. Merging: template cover/abstract + pandoc body content
4. Repacking into final docx
"""
import subprocess
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

SCRIPTS = Path("/home/spencer/.claude/plugins/marketplaces/anthropic-agent-skills/skills/docx/scripts/office")
REPORT_DIR = Path(__file__).parent
TEMPLATE = REPORT_DIR.parent / "课程设计报告模板.docx"
REPORT_MD = REPORT_DIR / "report.md"
OUTPUT = REPORT_DIR / "report.docx"

TMP = Path("/tmp/docx_build")
TMP_TEMPLATE = TMP / "template"
TMP_PANDOC = TMP / "pandoc"
TMP_MERGED = TMP / "merged"

ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
# Register all namespaces to prevent ns0/ns1 prefixes
NAMESPACES = {
    "wpc": "http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "o": "urn:schemas-microsoft-com:office:office",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "v": "urn:schemas-microsoft-com:vml",
    "wp14": "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "w10": "urn:schemas-microsoft-com:office:word",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
    "wpg": "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "a14": "http://schemas.microsoft.com/office/drawing/2010/main",
}
for prefix, uri in NAMESPACES.items():
    ET.register_namespace(prefix, uri)


def get_para_text(p):
    return "".join(t.text or "" for t in p.findall(".//w:t", ns)).strip()


def run(cmd, **kwargs):
    print(f"  $ {cmd}")
    subprocess.run(cmd, shell=True, check=True, **kwargs)


def main():
    # Clean up
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)

    # Step 1: Generate pandoc docx with template styles
    print("Step 1: pandoc md -> docx")
    pandoc_docx = TMP / "pandoc.docx"
    run(f'pandoc "{REPORT_MD}" -o "{pandoc_docx}" --reference-doc="{TEMPLATE}"')

    # Step 2: Unpack both
    print("Step 2: Unpack template and pandoc output")
    run(f'python "{SCRIPTS}/unpack.py" "{TEMPLATE}" "{TMP_TEMPLATE}"')
    run(f'python "{SCRIPTS}/unpack.py" "{pandoc_docx}" "{TMP_PANDOC}"')

    # Step 3: Merge
    print("Step 3: Merge cover + body")

    # Use pandoc output as base (it has our content with correct styles)
    shutil.copytree(TMP_PANDOC, TMP_MERGED)

    # Copy template's media files (school logo etc.) to merged
    template_media = TMP_TEMPLATE / "word" / "media"
    merged_media = TMP_MERGED / "word" / "media"
    merged_media.mkdir(exist_ok=True)
    if template_media.exists():
        for f in template_media.iterdir():
            dest = merged_media / f.name
            if not dest.exists():
                shutil.copy2(f, dest)
                print(f"  Copied media: {f.name}")

    # Parse template document.xml - extract cover paragraphs (0-13)
    template_tree = ET.parse(TMP_TEMPLATE / "word" / "document.xml")
    template_root = template_tree.getroot()
    template_body = template_root.find(".//w:body", ns)
    template_paras = list(template_body)  # all children (paragraphs + sectPr)

    # Cover = paragraphs 0..13 (before "摘 要")
    cover_paras = []
    for i, elem in enumerate(template_paras):
        if elem.tag.endswith("}p"):
            text = get_para_text(elem)
            if "摘" in text and "要" in text and i > 5:
                break
        cover_paras.append(elem)

    print(f"  Cover paragraphs: {len(cover_paras)}")

    # Modify cover: replace placeholder title
    for p in cover_paras:
        text = get_para_text(p)
        if "此处写自己的题目" in text:
            for t in p.findall(".//w:t", ns):
                if t.text and "此处写自己的题目" in t.text:
                    t.text = "基于Cranfield数据集的信息检索系统"
                if t.text and "仿宋小二加粗" in t.text:
                    t.text = ""
            # Change color from red to black
            for rpr in p.findall(".//w:color", ns):
                rpr.set(f"{{{ns['w']}}}val", "000000")

    # Parse pandoc document.xml
    pandoc_tree = ET.parse(TMP_MERGED / "word" / "document.xml")
    pandoc_root = pandoc_tree.getroot()
    pandoc_body = pandoc_root.find(".//w:body", ns)

    # Get pandoc's sectPr (last element, page settings)
    pandoc_children = list(pandoc_body)
    sect_pr = pandoc_children[-1] if pandoc_children[-1].tag.endswith("}sectPr") else None

    # Clear pandoc body
    for child in list(pandoc_body):
        pandoc_body.remove(child)

    # Add cover paragraphs first
    for p in cover_paras:
        pandoc_body.append(p)

    # Add a page break after cover
    page_break_p = ET.SubElement(pandoc_body, f"{{{ns['w']}}}p")
    page_break_r = ET.SubElement(page_break_p, f"{{{ns['w']}}}r")
    ET.SubElement(page_break_r, f"{{{ns['w']}}}br", {f"{{{ns['w']}}}type": "page"})

    # Add pandoc content (skip the title paragraph which duplicates our cover)
    skip_first_heading = True
    for child in pandoc_children:
        if child.tag.endswith("}sectPr"):
            continue
        text = get_para_text(child) if child.tag.endswith("}p") else ""
        # Skip the first H1 (report title - already on cover)
        if skip_first_heading and "Cranfield" in text:
            skip_first_heading = False
            continue
        pandoc_body.append(child)

    # Add sectPr back (page settings)
    if sect_pr is not None:
        pandoc_body.append(sect_pr)

    # Copy template's relationships for media
    # (merge template rels into pandoc rels)
    template_rels = TMP_TEMPLATE / "word" / "_rels" / "document.xml.rels"
    merged_rels = TMP_MERGED / "word" / "_rels" / "document.xml.rels"
    if template_rels.exists() and merged_rels.exists():
        t_tree = ET.parse(template_rels)
        m_tree = ET.parse(merged_rels)
        t_root = t_tree.getroot()
        m_root = m_tree.getroot()
        existing_ids = {r.get("Id") for r in m_root}
        for rel in t_root:
            if rel.get("Id") not in existing_ids and "media" in (rel.get("Target") or ""):
                m_root.append(rel)
                print(f"  Added rel: {rel.get('Id')} -> {rel.get('Target')}")
        m_tree.write(merged_rels, xml_declaration=True, encoding="UTF-8")

    # Save merged document.xml
    pandoc_tree.write(
        TMP_MERGED / "word" / "document.xml",
        xml_declaration=True,
        encoding="UTF-8",
    )

    # Step 4: Repack using zipfile directly
    print("Step 4: Pack final docx")
    import zipfile
    if OUTPUT.exists():
        OUTPUT.unlink()
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(TMP_MERGED.rglob("*")):
            if file_path.is_file():
                arcname = file_path.relative_to(TMP_MERGED)
                zf.write(file_path, arcname)

    size = OUTPUT.stat().st_size / 1024 / 1024
    print(f"\nDone! {OUTPUT} ({size:.1f} MB)")


if __name__ == "__main__":
    main()
