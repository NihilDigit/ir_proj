"""Cranfield 检索效果评估：在 225 条标准查询上跑 TF-IDF，对照 1837 条 qrels 计算 MAP / P@k / R-Precision / NDCG。

运行方式（项目根目录）：
    cd backend && uv run python -m app.eval

输出：
- 终端：每条指标的均值
- backend/app/data/eval_results.json：原始数据，可供 report 引用
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

from .engine import SearchEngine


def _avg(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def precision_at_k(ranked: list[int], relevant: set[int], k: int) -> float:
    if k == 0:
        return 0.0
    top_k = ranked[:k]
    if not top_k:
        return 0.0
    return sum(1 for d in top_k if d in relevant) / k


def average_precision(ranked: list[int], relevant: set[int]) -> float:
    """Average Precision: 命中位置上 P 的平均，未命中位置不计入分母外但需归一到 |R|。"""
    if not relevant:
        return 0.0
    hits = 0
    score = 0.0
    for i, doc_id in enumerate(ranked, start=1):
        if doc_id in relevant:
            hits += 1
            score += hits / i
    return score / len(relevant)


def r_precision(ranked: list[int], relevant: set[int]) -> float:
    """R-Precision: 取 top-|R| 的 precision。"""
    R = len(relevant)
    if R == 0:
        return 0.0
    return precision_at_k(ranked, relevant, R)


def ndcg_at_k(ranked: list[int], rel_grades: dict[int, int], k: int) -> float:
    """NDCG@k，使用 (2^rel - 1) gain 与 log2(i+1) 折扣。"""
    if not rel_grades:
        return 0.0
    dcg = 0.0
    for i, doc_id in enumerate(ranked[:k], start=1):
        g = rel_grades.get(doc_id, 0)
        if g > 0:
            dcg += (2**g - 1) / math.log2(i + 1)
    ideal_grades = sorted(rel_grades.values(), reverse=True)[:k]
    idcg = sum((2**g - 1) / math.log2(i + 1) for i, g in enumerate(ideal_grades, start=1) if g > 0)
    return dcg / idcg if idcg > 0 else 0.0


def main():
    print("加载数据 + 构建/加载索引 ...")
    engine = SearchEngine()
    print(f"  文档数: {len(engine.docs)}, 查询数: {len(engine.queries)}, qrels: {len(engine.relevance)}")

    # qrels 转换：原始格式 query_id, doc_id, relevance（含 rel=0 哑判与极少数 rel=3）
    # 二值集合：rel > 0 视为相关。
    # 分级集合：rel 原值用作 grade（0 不计 gain）。
    rel_binary: dict[int, set[int]] = defaultdict(set)
    rel_graded: dict[int, dict[int, int]] = defaultdict(dict)
    for r in engine.relevance:
        if r.relevance > 0:
            rel_binary[r.query_id].add(r.doc_id)
        rel_graded[r.query_id][r.doc_id] = max(0, r.relevance)

    # XML <num> 字段有跳号（1..365），qrels 用位置序号 1..225。按位置重映射。
    indexed_queries = [(i + 1, q) for i, q in enumerate(engine.queries)]
    queries_with_rel = [(qid, q) for qid, q in indexed_queries if rel_binary.get(qid)]
    print(f"  含相关判断的查询数: {len(queries_with_rel)} / {len(engine.queries)}")

    aps, p5s, p10s, p20s, r_precs, ndcg10s = [], [], [], [], [], []
    per_query = []

    for qid, q in queries_with_rel:
        terms = engine.index.preprocessor.process_query(q.text)
        ranked_pairs = engine.tfidf_ranker.search(terms, top_k=1000)
        ranked_ids = [doc_id for doc_id, _ in ranked_pairs]

        relevant = rel_binary[qid]
        graded = rel_graded[qid]

        ap = average_precision(ranked_ids, relevant)
        p5 = precision_at_k(ranked_ids, relevant, 5)
        p10 = precision_at_k(ranked_ids, relevant, 10)
        p20 = precision_at_k(ranked_ids, relevant, 20)
        rp = r_precision(ranked_ids, relevant)
        nd10 = ndcg_at_k(ranked_ids, graded, 10)

        aps.append(ap); p5s.append(p5); p10s.append(p10); p20s.append(p20)
        r_precs.append(rp); ndcg10s.append(nd10)
        per_query.append({
            "qid": qid, "xml_num": q.query_id, "n_relevant": len(relevant),
            "ap": ap, "p5": p5, "p10": p10, "p20": p20, "rp": rp, "ndcg10": nd10,
        })

    metrics = {
        "n_queries": len(queries_with_rel),
        "MAP": _avg(aps),
        "P@5": _avg(p5s),
        "P@10": _avg(p10s),
        "P@20": _avg(p20s),
        "R-Precision": _avg(r_precs),
        "NDCG@10": _avg(ndcg10s),
    }

    print("\n=== 评估结果（TF-IDF + 余弦相似度，全文档检索）===")
    print(f"  评估查询数: {metrics['n_queries']}")
    print(f"  MAP        : {metrics['MAP']:.4f}")
    print(f"  P@5        : {metrics['P@5']:.4f}")
    print(f"  P@10       : {metrics['P@10']:.4f}")
    print(f"  P@20       : {metrics['P@20']:.4f}")
    print(f"  R-Precision: {metrics['R-Precision']:.4f}")
    print(f"  NDCG@10    : {metrics['NDCG@10']:.4f}")

    out_path = Path(__file__).parent / "data" / "eval_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"summary": metrics, "per_query": per_query}, indent=2))
    print(f"\n详细结果已写入: {out_path}")


if __name__ == "__main__":
    main()
