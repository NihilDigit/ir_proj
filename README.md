# Cranfield IR 检索系统

基于 Cranfield 数据集（1400 文档 / 225 查询 / 1837 相关性判断）的全栈信息检索系统。后端 Python FastAPI，前端 Vue 3。

## 功能

- 倒排索引（含位置信息，支持短语匹配）
- 四种检索模式：布尔检索（递归下降解析）、短语查询、WordNet 同义词扩展、Soundex 拼写矫正
- TF-IDF 余弦相似度排序
- 词典 / 倒排记录表浏览 API
- 匹配词项高亮

## 快速启动

**后端**（工作目录 `backend/`，从根目录用 `uv` 管理依赖）：
```bash
uv sync
uv run python -m uvicorn app.main:app --port 8000 --reload --app-dir backend
```
首次启动自动下载 NLTK stopwords / wordnet。

**前端**（工作目录 `frontend/`）：
```bash
bun install
bun run dev       # 代理 /api → localhost:8000
bun run build     # 生产构建
```

两端同时运行。访问 `http://localhost:5173`。

## 项目结构

```
├── backend/
│   └── app/
│       ├── main.py          FastAPI lifespan + CORS
│       ├── engine.py        数据/索引/引擎协调器
│       ├── config.py        路径常量
│       ├── models.py        Pydantic 请求/响应
│       ├── core/
│       │   ├── parser.py          XML 解析器
│       │   ├── preprocessor.py    小写/去标点/Porter 词干
│       │   ├── indexer.py         倒排索引（term → {doc_id → [pos]}）
│       │   ├── boolean_search.py  递归下降解析器
│       │   ├── phrase_search.py   位置连续校验
│       │   ├── tfidf.py           log TF-IDF + 余弦
│       │   ├── query_expansion.py WordNet 同义词
│       │   ├── soundex.py         发音哈希 + 候选查找
│       │   └── highlighter.py     <mark> 注入
│       └── routers/
│           ├── search.py   POST /api/search/{boolean,phrase,expanded,soundex}
│           └── index.py    GET  /api/index/{dictionary,postings/{term},documents/{id}}
├── frontend/
│   └── src/
│       ├── api.js
│       └── components/     四种检索模式 + 索引浏览
├── data/                   Cranfield 原始文件（cranfield.txt / .qry / .rel）
├── report/
│   ├── report.md / .docx / .pdf
│   ├── build_docx.py       Markdown → docx（含封面、目录、样式）
│   ├── uno_export_pdf.py   docx → pdf（LibreOffice UNO）
│   ├── gen_figures.py      PlotNine 统计图
│   ├── theme_ir.py         PlotNine 主题
│   ├── flows/              Graphviz 流程图生成
│   │   └── gen_flows.py
│   └── figures/            产出 PNG（供 report.md 引用）
├── pack.sh                 代码打包脚本
├── pyproject.toml          统一依赖（后端 + 报告）
└── uv.lock
```

## 关键设计

- **位置感知索引**：停用词被移除但 token 位置保留，短语查询 `boundary layer` 可正确命中。
- **词干一致性**：索引与查询共用同一 PorterStemmer 实例，重复 stem 安全（幂等）。
- **索引缓存**：首次构建后 pickle 到 `backend/app/data/index.pkl`，后续启动直接加载。
- **服务端高亮**：后端返回带 `<mark>` 的 HTML，前端 `v-html` 渲染（Cranfield 数据静态可信）。
- **Boolean & Phrase 也排序**：先用语义过滤文档集，再用 TF-IDF 余弦相似度排序。

## 打包分发

```bash
./pack.sh                   # 产出 dist/ir-system-<date>.zip
```

## 报告构建

```bash
cd report
uv run --with python-docx build_docx.py     # → report.docx
python3 uno_export_pdf.py report.docx report.pdf   # → report.pdf
```
