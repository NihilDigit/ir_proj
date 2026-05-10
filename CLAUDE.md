# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Cranfield IR search engine — a course project implementing a full-stack information retrieval system on the Cranfield dataset (1,400 aerospace documents, 225 queries, 1,837 relevance judgments). Python FastAPI backend + Vue 3 frontend. Includes a separate report-build pipeline (Markdown → docx → PDF) under `report/`.

## Commands

Dependencies are unified in a single root `pyproject.toml` (backend runtime + report tooling). Run `uv` commands from the project root.

### Backend
```bash
uv sync
uv run python -m uvicorn app.main:app --port 8000 --reload --app-dir backend

# 在 225 条标准查询上跑 MAP / P@k / R-Precision / NDCG@10 评估
cd backend && uv run python -m app.eval
```

NLTK data (stopwords, wordnet) is auto-downloaded on first startup via the FastAPI lifespan handler. The first run also builds `backend/app/data/index.pkl`; subsequent runs load it. Delete the pickle to force a rebuild.

### Frontend (working directory: `frontend/`)
```bash
bun install
bun run dev        # http://localhost:5173, proxies /api → localhost:8000
bun run build      # production build
```

Both servers must run simultaneously. Vite proxies `/api` requests to the backend.

### Report build (working directory: `report/`)

**日常迭代用 `rebuild_keep_cover.py`**, 它会自动:
1. 把当前 `report.docx` 的封面 12 段快照保存为 `.cover_source.docx`
2. 跑 `build_docx.py`, 但封面源指向快照而不是模板

```bash
uv run rebuild_keep_cover.py                      # 推荐: 保留手改的封面 + 完整重建
python3 uno_export_pdf.py report.docx report.pdf  # docx → pdf via LibreOffice UNO (system python)

# 辅助脚本:
uv run python gen_figures.py                      # PlotNine 统计图 → figures/*.png
uv run python flows/gen_flows.py                  # Graphviz 流程图 → figures/*.png
./capture_ui.sh                                   # 抓取前端界面截图
uv run --group report python build_docx.py        # 全量重建（封面用模板, 不保留手改第一页）
uv run patch_docx.py                              # 在已生成 docx 上做局部字符串替换
```

封面页(信息表 + 学生姓名)是手改后的状态, 直接跑 `build_docx.py` 会用模板覆盖。如要回到模板封面: 删除 `report/.cover_source.docx` 后用 `build_docx.py`。

`uno_export_pdf.py` 必须用系统 Python(不是 `uv run`), 因为 LibreOffice UNO 桥不在 venv 里。

### Packaging
```bash
./pack.sh          # → dist/ir-system-<YYYYMMDD>.zip (excludes pkl, node_modules, AI tooling files)
```

## Architecture

```
Data Flow:  Cranfield XML → Parser → Preprocessor → InvertedIndex → SearchEngines → FastAPI → Vue UI

backend/app/
├── engine.py          # Coordinator: loads data, builds/loads index, initializes all engines
├── main.py            # FastAPI lifespan + CORS + route mounting
├── config.py          # Path constants (DATA_DIR, INDEX_CACHE)
├── models.py          # Pydantic request/response schemas
├── eval.py            # MAP / P@k / R-Precision / NDCG@10 evaluation on 225 standard queries
├── core/
│   ├── parser.py          # XML parser for Cranfield docs/queries/relevance
│   ├── preprocessor.py    # Tokenize → lowercase → remove stopwords → Porter stem
│   ├── indexer.py         # Inverted index: term → {doc_id → [positions]}
│   ├── boolean_search.py  # Recursive descent parser for AND/OR/NOT/parens
│   ├── phrase_search.py   # Position-based consecutive term matching
│   ├── tfidf.py           # Log TF-IDF + cosine similarity ranking (idf_cache 共用 IDF)
│   ├── query_expansion.py # WordNet synonym expansion
│   ├── soundex.py         # Soundex phonetic codes + dictionary-based correction
│   └── highlighter.py     # Injects <mark> tags around matching stems
└── routers/
    ├── search.py      # POST /api/search/{boolean,phrase,expanded,soundex}
    └── index.py       # GET /api/index/{dictionary,postings/{term},documents/{id}}

frontend/src/components/
├── BooleanSearch.vue   # AND/OR/NOT operator buttons
├── PhraseSearch.vue    # Consecutive phrase query
├── ExpandedSearch.vue  # WordNet synonym expansion
├── SoundexSearch.vue   # Phonetic spelling correction
├── IndexViewer.vue     # Paginated dictionary + postings viewer
└── ResultList.vue      # Shared: ranked results with highlights + detail expand

report/
├── report.md / report.docx / report.pdf
├── rebuild_keep_cover.py # 入口: 快照封面 + 调 build_docx
├── build_docx.py         # Markdown → docx (cover, TOC, styles, code blocks, 三线表, 公式字体注入)
├── patch_docx.py         # Targeted edits to existing docx after md changes
├── uno_export_pdf.py     # docx → pdf via LibreOffice UNO bridge (system python)
├── gen_figures.py        # PlotNine statistical charts → figures/
├── theme_ir.py           # Shared PlotNine theme
├── flows/gen_flows.py    # Graphviz pipeline diagrams → figures/
├── capture_ui.sh         # Headless screenshots of the running frontend
└── demo_script.md        # Demo recording script
```

`build_docx.py` 的几个非显然处理:
- `style_three_line_tables()` — 把 pandoc 默认的方格表改为三线表(顶/底 1.5pt、表头 0.5pt、单元格水平居中、整表居中)
- `keep_tables_together()` — caption 段落 `<w:keepNext/>`、表格行 `<w:cantSplit/>`, 防止 caption 与表身被分页割裂
- `insert_cover()` — 从 `TEMPLATE_FILE` 复制前 12 段作为封面; `rebuild_keep_cover.py` 把这个常量指向 `.cover_source.docx`(用户手改过的封面)而不是模板, 实现"重建保留封面"
- `apply_math_font()` — 给 OMML 公式注入 Cambria Math 字体声明: `settings.xml` 加全局 `<m:mathPr>`, 每个 `<m:r>` 加 `<w:rPr><w:rFonts ascii=hAnsi="Cambria Math"/></w:rPr>`; pandoc 输出的 OMML 不带任何字体声明, Word 桌面版有 fallback 但其它渲染器没有, 不补就会回退到段落字体导致下标错位

## Key Design Decisions

- **Position-aware index**: stopwords are removed but original token positions are preserved (not reindexed), so phrase queries like `"boundary layer"` match correctly.
- **Stemming consistency**: indexing and querying share the same `PorterStemmer` instance. Double-stemming is safe (idempotent on already-stemmed tokens).
- **Index caching**: first build pickles to `backend/app/data/index.pkl`; subsequent starts load from cache. Delete the pickle to force rebuild.
- **Server-side highlighting**: backend returns HTML with `<mark>` tags; frontend renders via `v-html`. Safe because Cranfield data is static and trusted.
- **All search modes rank results**: boolean and phrase searches filter documents first, then rank the filtered set using TF-IDF cosine similarity.
- **Soundex uses top-1 candidate only for retrieval**: each query term's other phonetic candidates are returned for UI display but not fed into TF-IDF. Stuffing all candidates into ranking would let phonetically similar but semantically unrelated words (e.g. `fail`/`fall` for `flow`) dominate scores. Candidates are ranked by longest common prefix, then length difference, then alphabet.
- **Unified dependencies**: a single root `pyproject.toml` covers backend runtime, figure generation, and the report toolchain. The `report` dependency group (currently `python-docx`) is opt-in via `uv sync --group report` or `uv run --group report ...`.
- **eval qid 重映射**: `cran.qry.xml` 的 `<num>` 字段是 1–365 的非连续值(有跳号), 但 `cranqrel.txt` 用位置序号 1–225。直接拿 `query.query_id` 匹配 qrels 会错位, 导致 MAP 假性偏低到 0.012。`eval.py` 按出现顺序重新编号后, MAP 回到合理基线 0.276。
- **公式全部走 OMML + Cambria Math 字体注入**: pandoc 把 `$$...$$` 和 `$...$` 都转为 OMML(`<m:oMath>` / `<m:oMathPara>`), 但不带字体声明; settings.xml 也没有全局 `<m:mathPr>`。Word 桌面版默认 fallback 到 Cambria Math 所以表面正常, LibreOffice 等其它渲染器没 fallback, 会回退到段落字体(Times New Roman / 宋体), 这两个字体没有 OpenType MATH 表, 下标位置和操作符间距全乱。`build_docx.apply_math_font()` 后处理一次性注入字体, 让 docx 在 Word 和 LO 里都正确渲染。
