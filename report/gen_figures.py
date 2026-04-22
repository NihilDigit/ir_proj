"""Generate all statistical figures for the IR course report.

All figures use the shared theme_ir (plotnine + theme_classic base).
No in-figure titles — captions live in the report.

Run from the `report/` directory:
    uv run --project ../backend python gen_figures.py
"""

from __future__ import annotations
import sys
from pathlib import Path

REPORT_DIR = Path(__file__).parent
sys.path.insert(0, str(REPORT_DIR.parent / "backend"))

import numpy as np
import pandas as pd
from plotnine import (
    ggplot,
    aes,
    geom_line,
    geom_histogram,
    geom_col,
    geom_vline,
    geom_text,
    annotate,
    scale_x_log10,
    scale_y_log10,
    scale_y_continuous,
    expand_limits,
    coord_flip,
    labs,
)

from theme_ir import theme_ir, TOKENS, y_top_label
from app.core.parser import parse_documents
from app.core.preprocessor import Preprocessor
from app.core.indexer import InvertedIndex

DATA_DIR = REPORT_DIR.parent / "data"
FIG_DIR = REPORT_DIR / "figures"
FIG_DIR.mkdir(exist_ok=True)

FIG_W, FIG_H = 2.6, 1.8  # inches; matches 6.5 cm half-page width


def save(plot, name: str, h: float = FIG_H):
    out = FIG_DIR / name
    # bbox_inches="tight" lets matplotlib expand the output past figure_size to
    # include the horizontal y-axis title (needed for CJK rotation=0 labels
    # that stick out to the left of the canvas).
    plot.save(
        out, width=FIG_W, height=h, units="in", dpi=300,
        verbose=False, bbox_inches="tight",
    )
    print(f"wrote {out}")


def main():
    docs = parse_documents(str(DATA_DIR / "cran.all.1400.xml"))
    pp = Preprocessor()
    idx = InvertedIndex()
    idx.build(docs)

    # ── Zipf ─────────────────────────────────────────────────────
    # Pair rank vs total term frequency. Add an ideal Zipf reference
    # (slope -1 in log-log space) anchored at the top-ranked term so the
    # reader can see deviation from the pure 1/rank law visually.
    freqs = sorted(
        (sum(len(p) for p in postings.values()) for postings in idx.index.values()),
        reverse=True,
    )
    zipf_df = pd.DataFrame({"rank": range(1, len(freqs) + 1), "freq": freqs})
    ref = pd.DataFrame({
        "rank": [1, len(freqs)],
        "freq": [freqs[0], freqs[0] / len(freqs)],
    })
    save(
        ggplot(zipf_df, aes(x="rank", y="freq"))
        + geom_line(
            ref, aes(x="rank", y="freq"),
            color=TOKENS["ink"], size=0.5, linetype="dashed",
        )
        + geom_line(color=TOKENS["accent"], size=0.8)
        + annotate(
            "text",
            x=60, y=3,
            label="理想 Zipf（斜率 −1）",
            color=TOKENS["ink"], size=7, ha="left",
        )
        + scale_x_log10()
        + scale_y_log10()
        + labs(x="词项排名")
        + y_top_label("总频数")
        + theme_ir(grid=True),
        "zipf_distribution.png",
    )

    # ── Document frequency distribution ──────────────────────────
    # Linear-x / log-y histogram. A median reference line anchors the
    # "中位数 DF = 2" sentence in §3.3.4 — very low median despite a
    # 730-max heavy tail.
    dfs = [len(postings) for postings in idx.index.values()]
    median_df = int(np.median(dfs))
    df_df = pd.DataFrame({"df": dfs})
    save(
        ggplot(df_df, aes(x="df"))
        + geom_histogram(
            bins=50,
            fill=TOKENS["accent"],
            color=TOKENS["paper"],
            size=0.2,
        )
        + geom_vline(
            xintercept=median_df,
            color=TOKENS["ink"], size=0.5, linetype="dashed",
        )
        + annotate(
            "text",
            x=median_df + 20, y=2000,
            label=f"中位数 = {median_df}",
            color=TOKENS["ink"], size=7, ha="left",
        )
        + scale_y_log10()
        + labs(x="文档频数 DF")
        + y_top_label("词项数（对数刻度）")
        + theme_ir(grid=True),
        "df_distribution.png",
    )

    # ── Document length distribution ─────────────────────────────
    doc_lengths = [len(pp.process(d.title + " " + d.text)) for d in docs]
    mean_len = float(np.mean(doc_lengths))
    median_len = float(np.median(doc_lengths))
    len_df = pd.DataFrame({"length": doc_lengths})
    save(
        ggplot(len_df, aes(x="length"))
        + geom_histogram(
            bins=40,
            fill=TOKENS["accent"],
            color=TOKENS["paper"],
            size=0.2,
        )
        + geom_vline(
            xintercept=mean_len,
            color=TOKENS["ink"], size=0.5, linetype="dashed",
        )
        + annotate(
            "text",
            x=mean_len + 6, y=130,
            label=f"均值 = {mean_len:.1f}",
            color=TOKENS["ink"], size=7, ha="left",
        )
        + labs(x="每文档词项数（预处理后）")
        + y_top_label("文档数")
        + theme_ir(grid=True),
        "doc_length_distribution.png",
    )

    # ── Top-20 most frequent terms ───────────────────────────────
    # Horizontal bars with value labels pinned to the right of each bar,
    # so the figure can double as a table without cross-referencing ticks.
    pairs = sorted(
        (
            (term, sum(len(p) for p in postings.values()))
            for term, postings in idx.index.items()
        ),
        key=lambda x: x[1],
        reverse=True,
    )[:20]
    top = pd.DataFrame(pairs, columns=["term", "freq"])
    top["term"] = pd.Categorical(top["term"], categories=top["term"][::-1], ordered=True)
    save(
        ggplot(top, aes(x="term", y="freq"))
        + geom_col(fill=TOKENS["accent"], width=0.7)
        + geom_text(
            aes(label="freq"),
            ha="left", nudge_y=40, size=7, color=TOKENS["ink"],
        )
        # leave headroom on the right so the largest label isn't clipped
        + expand_limits(y=top["freq"].max() * 1.15)
        + coord_flip()
        + labs(x="", y="总频数（Porter 词干后）")
        + theme_ir(grid=True),
        "top20_terms.png",
        h=2.6,
    )

    # ── Stats summary ────────────────────────────────────────────
    stats = {
        "Documents": len(docs),
        "Unique terms": len(idx.index),
        "Avg doc length": f"{mean_len:.1f}",
        "Median doc length": int(median_len),
        "Max DF": max(dfs),
        "Min DF": min(dfs),
        "Median DF": median_df,
    }
    print("\n=== Index statistics ===")
    for k, v in stats.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
