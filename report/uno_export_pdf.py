#!/usr/bin/env python3
"""通过 LibreOffice UNO 加载 docx，更新 TOC 和所有字段，导出 PDF。"""
import os
import socket
import subprocess
import sys
import time
import zipfile


PORT = 2202


def _repair_cover_layout(docx_abs: str) -> None:
    """Restore cover paragraph twip indents stripped by LibreOffice DOCX save."""
    from lxml import etree

    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(docx_abs, "r") as zin:
        entries = {name: zin.read(name) for name in zin.namelist()}

    root = etree.fromstring(entries["word/document.xml"])
    body = root.find("w:body", ns)
    if body is None:
        return
    paras = [el for el in body if el.tag == f"{{{ns['w']}}}p"]
    w_ns = ns["w"]

    def q(local):
        return f"{{{w_ns}}}{local}"

    def ensure_ind(p):
        p_pr = p.find("w:pPr", ns)
        if p_pr is None:
            p_pr = etree.Element(q("pPr"))
            p.insert(0, p_pr)
        ind = p_pr.find("w:ind", ns)
        if ind is None:
            ind = etree.Element(q("ind"))
            p_pr.append(ind)
        return ind

    for idx, p in enumerate(paras[:12]):
        ind = ensure_ind(p)
        if idx == 0:
            ind.set(q("firstLineChars"), "600")
            ind.set(q("firstLine"), "1687")
        elif idx in (5, 6):
            ind.set(q("firstLineChars"), "448")
            ind.set(q("firstLine"), "1259")
        elif idx in (7, 8, 9):
            ind.set(q("firstLineChars"), "300")
            ind.set(q("firstLine"), "843")
            ind.set(q("rightChars"), "189")
            ind.set(q("right"), "397")
        elif idx in (10, 11):
            ind.set(q("firstLineChars"), "300")
            ind.set(q("firstLine"), "843")

    entries["word/document.xml"] = etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone=True
    )

    tmp_abs = docx_abs + ".coverfix"
    with zipfile.ZipFile(tmp_abs, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in entries.items():
            zout.writestr(name, data)
    os.replace(tmp_abs, docx_abs)


def _wait_port(host, port, timeout=30):
    end = time.time() + timeout
    while time.time() < end:
        try:
            s = socket.socket()
            s.settimeout(0.5)
            s.connect((host, port))
            s.close()
            return True
        except Exception:
            time.sleep(0.2)
    return False


def convert(docx_path: str, pdf_path: str) -> None:
    docx_abs = os.path.abspath(docx_path)
    pdf_abs = os.path.abspath(pdf_path)
    updated_docx_abs = docx_abs + ".updated.docx"

    # 启动 soffice 监听
    env = os.environ.copy()
    env.setdefault("HOME", os.path.expanduser("~"))
    proc = subprocess.Popen(
        [
            "soffice",
            "--headless",
            "--norestore",
            "--nolockcheck",
            "--nologo",
            "--nodefault",
            f"--accept=socket,host=127.0.0.1,port={PORT};urp;",
        ],
        env=env,
    )
    if not _wait_port("127.0.0.1", PORT):
        proc.terminate()
        raise RuntimeError("soffice listener timeout")

    try:
        import uno
        from com.sun.star.beans import PropertyValue  # type: ignore

        local_ctx = uno.getComponentContext()
        resolver = local_ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", local_ctx
        )
        remote_ctx = resolver.resolve(
            f"uno:socket,host=127.0.0.1,port={PORT};urp;StarOffice.ComponentContext"
        )
        smgr = remote_ctx.ServiceManager
        desktop = smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", remote_ctx
        )

        load_props = (PropertyValue("Hidden", 0, True, 0),)
        doc = desktop.loadComponentFromURL(
            "file://" + docx_abs, "_blank", 0, load_props
        )

        # 更新 TOC、字段、交叉引用、链接
        try:
            doc.refresh()
        except Exception as e:
            print("refresh:", e)
        try:
            for i in range(doc.DocumentIndexes.Count):
                doc.DocumentIndexes.getByIndex(i).update()
        except Exception as e:
            print("index update:", e)
        try:
            doc.TextFields.refresh()
        except Exception as e:
            print("fields refresh:", e)

        # 是否把更新后的 TOC 保存回 docx（命令行加 --save-docx 才保存，
        # 避免用户在 docx 里手动编辑后被覆盖）
        save_updated_docx = "--save-docx" in sys.argv
        if save_updated_docx:
            if os.path.exists(updated_docx_abs):
                os.unlink(updated_docx_abs)
            docx_save_props = (
                PropertyValue("FilterName", 0, "MS Word 2007 XML", 0),
                PropertyValue("Overwrite", 0, True, 0),
            )
            doc.storeToURL("file://" + updated_docx_abs, docx_save_props)

        save_props = (PropertyValue("FilterName", 0, "writer_pdf_Export", 0),)
        doc.storeToURL("file://" + pdf_abs, save_props)
        try:
            doc.close(True)
        except Exception:
            pass
        if save_updated_docx:
            os.replace(updated_docx_abs, docx_abs)
            _repair_cover_layout(docx_abs)
    finally:
        if os.path.exists(updated_docx_abs):
            os.unlink(updated_docx_abs)
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    positional = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(positional) != 2:
        print("usage: uno_export_pdf.py input.docx output.pdf [--save-docx]",
              file=sys.stderr)
        sys.exit(1)
    convert(positional[0], positional[1])
    print(f"exported: {positional[1]}")
