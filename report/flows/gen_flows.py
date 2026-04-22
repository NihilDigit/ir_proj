# /// script
# requires-python = ">=3.11"
# dependencies = ["graphviz"]
# ///
"""Render IR course report flow diagrams with Graphviz.

splines=ortho 机制化保证所有 edge 为直角折线；rank=same 分组实现 zig-zag。
样式沿用 theme_ir.py 的色板（input/process/decision/output/external）。

Run: uv run gen_flows.py                  # 渲染全部
     uv run gen_flows.py preprocessing    # 只渲染 preprocessing_flow
"""
from __future__ import annotations

import sys
from pathlib import Path
from graphviz import Digraph

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"
FONT = "HarmonyOS Sans SC"

STYLES: dict[str, dict] = {
    "input":    dict(shape="hexagon",  fillcolor="#E0E7FF", color="#3730A3",
                     fontcolor="#1E1B4B", style="filled", penwidth="2"),
    "process":  dict(shape="box",      fillcolor="#EFF6FF", color="#2563EB",
                     fontcolor="#1E3A8A", style="filled,rounded", penwidth="2"),
    "decision": dict(shape="diamond",  fillcolor="#FEF3C7", color="#B45309",
                     fontcolor="#78350F", style="filled", penwidth="2"),
    "output":   dict(shape="box",      fillcolor="#2563EB", color="#1E40AF",
                     fontcolor="#FFFFFF", style="filled,rounded,bold", penwidth="2"),
    "external": dict(shape="cylinder", fillcolor="#F5F3FF", color="#7C3AED",
                     fontcolor="#4C1D95", style="filled", penwidth="2"),
}

EDGE_MAIN    = "#2563EB"
EDGE_EXTERN  = "#7C3AED"
EDGE_YES     = "#059669"
EDGE_NO      = "#B91C1C"
EDGE_LOOP    = "#D97706"


def base_graph(name: str, *, rankdir: str = "TB") -> Digraph:
    g = Digraph(name, format="png")
    g.attr(rankdir=rankdir, splines="ortho", bgcolor="white",
           fontname=FONT, dpi="300", pad="0.2",
           nodesep="0.35", ranksep="0.55")
    g.attr("node", fontname=FONT, fontsize="14", margin="0.18,0.12")
    g.attr("edge", fontname=FONT, fontsize="12", color=EDGE_MAIN, penwidth="2",
           arrowsize="0.8")
    return g


def N(g: Digraph, key: str, label: str, kind: str = "process") -> None:
    g.node(key, label=label, **STYLES[kind])


def row(g: Digraph, *keys: str) -> None:
    """强制一组节点在同一 rank（水平行）。"""
    with g.subgraph() as s:
        s.attr(rank="same")
        for k in keys:
            s.node(k)


# ─────────────────────────── 各流程图 ───────────────────────────

def _zigzag_linear(g: Digraph, row1: list[str], row2: list[str],
                   extra_edges=()) -> None:
    """Linear flow rendered as two rows with explicit port hints.

    第一行末尾向下跨到第二行首，起止点固定在节点的 s/n 八向端口。
    """
    row(g, *row1)
    row(g, *row2)
    chain = row1 + row2
    for a, b in zip(chain, chain[1:]):
        if a == row1[-1] and b == row2[0]:
            g.edge(a, b, tailport="s", headport="n")
        else:
            g.edge(a, b, tailport="e", headport="w")
    for e in extra_edges:
        g.edge(*e[:2], **e[2] if len(e) > 2 else {})


def preprocessing_flow() -> Digraph:
    g = base_graph("preprocessing_flow")
    N(g, "raw",   "原始文本",       "input")
    N(g, "lower", "小写化",         "process")
    N(g, "punct", "去标点",         "process")
    N(g, "tok",   "空白分词",       "process")
    N(g, "stop",  "去停用词",       "process")
    N(g, "stem",  "Porter 词干",    "process")
    N(g, "out",   "(term, pos)\n序列", "output")
    N(g, "stopwords", "NLTK\nStopwords", "external")

    _zigzag_linear(g,
                   row1=["raw", "lower", "punct", "tok"],
                   row2=["stop", "stem", "out"])
    g.edge("stopwords", "stop", color=EDGE_EXTERN, tailport="s", headport="n")
    return g


def phrase_search_flow() -> Digraph:
    g = base_graph("phrase_search_flow")
    N(g, "q",     "短语查询",                     "input")
    N(g, "stem",  "逐词词干化",                   "process")
    N(g, "fetch", "取倒排表\n（含位置）",         "process")
    N(g, "inter", "文档集求交",                   "process")
    N(g, "check", "位置连续校验\npos[i+1]=pos[i]+1", "process")
    N(g, "rank",  "TF-IDF 排序",                  "process")
    N(g, "out",   "排序结果",                     "output")

    _zigzag_linear(g,
                   row1=["q", "stem", "fetch", "inter"],
                   row2=["check", "rank", "out"])
    return g


def soundex_flow() -> Digraph:
    g = base_graph("soundex_flow")
    N(g, "q",      "查询词\n(可能拼错)",                          "input")
    N(g, "head",   "保留首字母",                                  "process")
    N(g, "map",    "辅音映射为数字\nBFPV→1  CGJKQSXZ→2\nDT→3  L→4  MN→5  R→6", "process")
    N(g, "skip",   "跳 H/W  去元音\n合并相邻重复",                "process")
    N(g, "pad",    "补至首字母+3 位",                             "process")
    N(g, "lookup", "查同码候选词",                                "process")
    N(g, "out",    "TF-IDF 检索",                                 "output")

    _zigzag_linear(g,
                   row1=["q", "head", "map", "skip"],
                   row2=["pad", "lookup", "out"])
    return g


def query_expansion_flow() -> Digraph:
    g = base_graph("query_expansion_flow")
    N(g, "q",      "原始查询词",        "input")
    N(g, "synset", "查 Synset",         "process")
    N(g, "lemma",  "抽 lemma\n过滤同词干", "process")
    N(g, "limit",  "取前 N 个\nmax_synonyms", "process")
    N(g, "merge",  "合并\n原词 + 扩展词", "process")
    N(g, "out",    "TF-IDF 检索",        "output")
    N(g, "wn",     "WordNet\n(NLTK)",    "external")

    _zigzag_linear(g,
                   row1=["q", "synset", "lemma", "limit"],
                   row2=["merge", "out"])
    g.edge("wn", "synset", color=EDGE_EXTERN, tailport="s", headport="n")
    g.edge("q", "merge", color=EDGE_YES, constraint="false",
           tailport="s", headport="w")
    return g


def index_construction_flow() -> Digraph:
    """纯线性：循环在节点标签里暗示，不画决策分支和回边。"""
    g = base_graph("index_construction_flow")
    N(g, "docs",   "文档集合",                                "input")
    N(g, "loop",   "遍历\n文档 × 词项",                        "process")
    N(g, "prep",   "拼接标题+正文\n预处理",                    "process")
    N(g, "append", "追加到倒排表\n(若不存在则新建 entry)\nindex[term][doc].append(pos)", "process")
    N(g, "pickle", "序列化\npickle 缓存",                     "output")

    _zigzag_linear(g,
                   row1=["docs", "loop", "prep"],
                   row2=["append", "pickle"])
    return g


def boolean_search_flow() -> Digraph:
    g = base_graph("boolean_search_flow")
    N(g, "q",      "布尔查询",                               "input")
    N(g, "tok",    "词法分析\nAND / OR / NOT / ()",          "process")
    N(g, "parser", "递归下降解析器\nparse_or → parse_and\n→ parse_not → parse_atom", "process")
    N(g, "setop",  "集合运算\n∪ (OR)  ∩ (AND)  ∖ (NOT)",    "process")
    N(g, "rank",   "TF-IDF 排序",                            "process")
    N(g, "out",    "排序结果",                               "output")

    _zigzag_linear(g,
                   row1=["q", "tok", "parser"],
                   row2=["setop", "rank", "out"])
    return g


def system_architecture() -> Digraph:
    """Pipeline：每节点配 SVG 图标撑起垂直高度，让横排比例协调。"""
    g = base_graph("system_architecture", rankdir="LR")
    g.attr(nodesep="0.35", ranksep="0.45",
           imagepath=str((FIGURES_DIR / "icons").resolve()))

    def node(key, icon, title, subtitle, fill="#EFF6FF",
             stroke="#2563EB", fontcolor="#1E3A8A"):
        html = (
            '<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3">'
            f'<TR><TD><IMG SRC="{icon}"/></TD></TR>'
            f'<TR><TD><FONT POINT-SIZE="14" COLOR="{fontcolor}"><B>{title}</B></FONT></TD></TR>'
            f'<TR><TD><FONT POINT-SIZE="11" COLOR="{fontcolor}">{subtitle}</FONT></TD></TR>'
            '</TABLE>>'
        )
        g.node(key, label=html, shape="box", style="filled,rounded",
               fillcolor=fill, color=stroke, penwidth="2", margin="0.12,0.12")

    PROC = ("#EFF6FF", "#2563EB", "#1E3A8A")
    OUT  = ("#DBEAFE", "#1E40AF", "#1E3A8A")
    IN   = ("#E0E7FF", "#3730A3", "#1E1B4B")
    node("ui",     "ui.png",     "Web UI",       "Vue 3 单页应用",                *OUT)
    node("api",    "api.png",    "FastAPI 后端", "/api/search · /api/index",      *PROC)
    node("engine", "engine.png", "四路检索引擎", "布尔 · 短语 · 扩展 · Soundex",  *PROC)
    node("rank",   "rank.png",   "TF-IDF 排序",  "余弦相似度 · 预算模长",          *PROC)
    node("index",  "index.png",  "倒排索引",     "词典 + 位置表（pickle）",        *PROC)
    node("prep",   "prep.png",   "文本预处理",   "分词 · 停用词 · Porter",        *PROC)
    node("docs",   "docs.png",   "Cranfield",    "1400 文档 / 225 查询",          *IN)

    chain = ["ui", "api", "engine", "rank", "index", "prep", "docs"]
    for a, b in zip(chain, chain[1:]):
        g.edge(a, b, color="#374151", penwidth="2.5", arrowsize="1.0",
               tailport="e", headport="w")
    return g


# ─────────────────────────── Build entry ───────────────────────────

ALL_GRAPHS = {
    "preprocessing":       preprocessing_flow,
    "phrase_search":       phrase_search_flow,
    "soundex":             soundex_flow,
    "query_expansion":     query_expansion_flow,
    "index_construction":  index_construction_flow,
    "boolean_search":      boolean_search_flow,
    "system_architecture": system_architecture,
}


def render(name: str) -> Path:
    g = ALL_GRAPHS[name]()
    FIGURES_DIR.mkdir(exist_ok=True)
    out = FIGURES_DIR / g.name
    rendered = g.render(filename=out.as_posix(), format="png", cleanup=True)
    return Path(rendered)


def main() -> None:
    targets = sys.argv[1:] or list(ALL_GRAPHS.keys())
    for t in targets:
        if t not in ALL_GRAPHS:
            print(f"unknown: {t}; choices={list(ALL_GRAPHS)}", file=sys.stderr)
            continue
        p = render(t)
        print(f"✓ {p}")


if __name__ == "__main__":
    main()
