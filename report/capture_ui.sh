#!/usr/bin/env bash
# 用 headless Chrome 截取前端各页面，输出到 figures/ui_*.png
set -euo pipefail

REPORT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="$REPORT_DIR/figures"
CHROME=/usr/bin/google-chrome-stable
BASE=http://localhost:5173
SIZE=1400,900

shot() {
    local path="$1"
    local name="$2"
    local url="$BASE$path"
    "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
        --window-size="$SIZE" \
        --virtual-time-budget=5000 \
        --screenshot="$OUT/ui_$name.png" \
        "$url" 2>/dev/null
    echo "  $name ← $url"
}

# 空状态
shot "/boolean" "boolean_empty"
shot "/phrase" "phrase_empty"
shot "/expanded" "expanded_empty"
shot "/soundex" "soundex_empty"
shot "/index" "index_viewer"

# 带查询的
shot "/boolean?q=aerodynamics%20AND%20wing%20NOT%20flutter" "boolean_result"
shot "/phrase?q=boundary%20layer" "phrase_result"
shot "/expanded?q=heat%20transfer" "expanded_result"
shot "/soundex?q=bounderi%20flo" "soundex_result"

echo "截图完成 → $OUT"
ls -lh "$OUT"/ui_*.png
