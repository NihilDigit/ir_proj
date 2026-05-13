#!/usr/bin/env bash
# 打包代码，供课程提交。
#
# 输出：dist/ir-system-YYYYMMDD.zip
#   · backend/           —— 后端源码
#   · frontend/          —— 前端源码（不含 node_modules / dist）
#   · data/              —— Cranfield 原始数据
#   · pyproject.toml / uv.lock / README.md / .gitignore / pack.sh
#
# 排除：report, __pycache__, .venv, node_modules, *.pkl, .git, dist, 一切 AI 相关
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATE="$(date +%Y%m%d)"
OUT_DIR="$ROOT/dist"
ZIP_NAME="ir-system-$DATE.zip"
ZIP_PATH="$OUT_DIR/$ZIP_NAME"

mkdir -p "$OUT_DIR"
rm -f "$ZIP_PATH"

cd "$ROOT"

zip -r "$ZIP_PATH" \
  backend/ \
  frontend/ \
  data/ \
  pyproject.toml uv.lock \
  README.md \
  .gitignore pack.sh \
  -x '*/__pycache__/*' \
  -x '*/__pycache__' \
  -x '*.pyc' \
  -x '*/.venv/*' \
  -x '.venv/*' \
  -x '*/node_modules/*' \
  -x 'frontend/dist/*' \
  -x 'backend/app/data/*.pkl' \
  -x '*/.git/*' \
  -x '.git/*' \
  -x 'dist/*' \
  -x 'report/*' \
  -x '.DS_Store' \
  -x 'CLAUDE.md' '*/CLAUDE.md' \
  -x '.claude/*' '*/.claude/*' '*/.claude' \
  -x '.impeccable.md' '*/.impeccable.md' \
  -x '.cursor*' '*/.cursor*' \
  -x '.aider*' '*/.aider*' \
  -x '.continue*' '*/.continue*' \
  -x '.copilot*' '*/.copilot*' \
  -x '.github/copilot*' \
  > /dev/null

SIZE=$(du -h "$ZIP_PATH" | cut -f1)
SHA=$(sha256sum "$ZIP_PATH" | cut -d' ' -f1)

echo "✓ $ZIP_PATH"
echo "  size: $SIZE"
echo "  sha256: $SHA"
