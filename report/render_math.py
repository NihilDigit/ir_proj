# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""把 report.md 里的块级公式（$$...$$）用 LaTeX 预渲染为 PNG。

LibreOffice 渲染 pandoc-OMML 公式时下标会脱节、字符分散。改用 LaTeX 渲染为图片，
docx 里嵌入 PNG，跨平台跨编辑器一致。inline 公式（$...$）保留 OMML 不动，
因为 inline 公式简单、问题不大且可保持文本流。

输出：
- figures/eq_NN.png 每条块级公式
- _math_rendered.md  已替换 $$...$$ 为 ![](figures/eq_NN.png) 的中间稿（build_docx 读它）

依赖：pdflatex + pdftoppm（系统已装）
"""

import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPORT_DIR = Path(__file__).resolve().parent
SRC_MD = REPORT_DIR / "report.md"
OUT_MD = REPORT_DIR / "_math_rendered.md"
FIG_DIR = REPORT_DIR / "figures"

LATEX_TEMPLATE = r"""\documentclass[varwidth,border=4pt,12pt]{standalone}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{bm}
\usepackage{mathtools}
\begin{document}
\(\displaystyle %s\)
\end{document}
"""


def render_one(latex_body: str, out_png: Path) -> bool:
    """用 pdflatex 渲染一条公式到 PNG。返回是否成功。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = Path(tmpdir) / "eq.tex"
        tex_path.write_text(LATEX_TEMPLATE % latex_body, encoding="utf-8")
        try:
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "eq.tex"],
                cwd=tmpdir, check=True, capture_output=True, timeout=20,
            )
        except subprocess.CalledProcessError as e:
            print(f"  ✗ pdflatex failed for: {latex_body[:60]}…", file=sys.stderr)
            print(e.stdout.decode("utf-8", "replace")[-800:], file=sys.stderr)
            return False
        # PDF → PNG (300 dpi, transparent)
        subprocess.run(
            ["pdftoppm", "-png", "-r", "300", "-singlefile",
             str(Path(tmpdir) / "eq.pdf"), str(out_png.with_suffix(""))],
            check=True, capture_output=True,
        )
    return True


def main():
    if not SRC_MD.exists():
        sys.exit(f"× {SRC_MD} not found")
    if not shutil.which("pdflatex") or not shutil.which("pdftoppm"):
        sys.exit("× 需要 pdflatex 与 pdftoppm（poppler-utils）")
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    src = SRC_MD.read_text(encoding="utf-8")

    # 块级公式：$$...$$ 单独成行（首尾 $$）
    pattern = re.compile(r"^\$\$(.+?)\$\$\s*$", re.MULTILINE | re.DOTALL)
    matches = list(pattern.finditer(src))
    print(f"找到 {len(matches)} 条块级公式，逐条渲染中…")

    parts: list[str] = []
    last_end = 0
    eq_idx = 0
    for m in matches:
        parts.append(src[last_end:m.start()])
        body = m.group(1).strip()
        eq_idx += 1
        # 用 hash 命名以便缓存：公式不变就不重复渲染
        digest = hashlib.sha1(body.encode()).hexdigest()[:10]
        png_path = FIG_DIR / f"eq_{eq_idx:02d}_{digest}.png"
        if not png_path.exists():
            ok = render_one(body, png_path)
            if not ok:
                # 渲染失败时回退到原始 LaTeX
                parts.append(m.group(0))
                last_end = m.end()
                continue
            print(f"  [{eq_idx:02d}] → {png_path.name}")
        else:
            print(f"  [{eq_idx:02d}] cached  {png_path.name}")
        # 替换为图片引用，居中显示，宽度按公式视觉重要性给（默认 11cm）
        rel = png_path.relative_to(REPORT_DIR)
        parts.append(f'![]({rel}){{ width=11cm }}')
        last_end = m.end()

    parts.append(src[last_end:])
    out = "".join(parts)
    OUT_MD.write_text(out, encoding="utf-8")
    print(f"\n输出 → {OUT_MD.name} ({len(matches)} 条公式已替换为 PNG)")


if __name__ == "__main__":
    main()
