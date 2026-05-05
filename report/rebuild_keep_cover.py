# /// script
# requires-python = ">=3.12"
# dependencies = ["python-docx>=1.1"]
# ///
"""保留封面页（第一页）的前提下重建 report.docx。

背景：
build_docx.py 每次重建都会把封面 12 段从「课程设计报告模板.docx」拷过来覆盖；
而项目第一页是信息表，由不稳定表格 + 手填字段（作者、学号、时间）构成，
重建后必须重新手填。本脚本通过把 build_docx.TEMPLATE_FILE 临时指向当前
report.docx，让 insert_cover() 从已手改过的版本而不是模板里复制封面。

用法（report/ 目录下）：
    uv run rebuild_keep_cover.py

首次使用前提：
- report.docx 已经存在
- 第一页已经按你的需要调整过

之后每次修改 report.md，都跑本脚本而不是 build_docx.py，封面就不会丢。
目录是 Word 字段，重建后自动刷新（无需保留）。

如果想回到模板封面（重新手改一遍）：删除 .cover_source.docx 之后跑 build_docx.py。
"""

import shutil
import subprocess
import sys
from pathlib import Path

REPORT_DIR = Path(__file__).resolve().parent
REPORT_DOCX = REPORT_DIR / "report.docx"
COVER_SNAPSHOT = REPORT_DIR / ".cover_source.docx"
RENDERED_MD = REPORT_DIR / "_math_rendered.md"

sys.path.insert(0, str(REPORT_DIR))
import build_docx  # noqa: E402


def main():
    if REPORT_DOCX.exists():
        shutil.copy(REPORT_DOCX, COVER_SNAPSHOT)
        print(f"  封面快照已更新 → {COVER_SNAPSHOT.name}")
    elif COVER_SNAPSHOT.exists():
        print(f"  report.docx 不存在，使用现有快照 {COVER_SNAPSHOT.name}")
    else:
        sys.exit(
            "× 找不到 report.docx，也没有 .cover_source.docx 快照。\n"
            "  首次使用：先跑一次 build_docx.py，手动改好第一页，再运行本脚本。"
        )

    # 块级公式预渲染：用 LaTeX 把 $$...$$ 转 PNG，绕开 LibreOffice OMML 渲染问题
    print("  渲染块级数学公式 …")
    subprocess.run(["uv", "run", str(REPORT_DIR / "render_math.py")], check=True, cwd=REPORT_DIR)
    if not RENDERED_MD.exists():
        sys.exit("× render_math.py 没有产出 _math_rendered.md")

    # 让 insert_cover() 从快照读封面，而不是从「课程设计报告模板.docx」
    build_docx.TEMPLATE_FILE = COVER_SNAPSHOT
    # 让 build_docx 读渲染后的 md 而不是源 md
    build_docx.MD_FILE = RENDERED_MD
    build_docx.main()


if __name__ == "__main__":
    main()
