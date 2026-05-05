"""TF-IDF 与余弦相似度排序"""

import math

from .indexer import InvertedIndex


class TFIDFRanker:
    def __init__(self, index: InvertedIndex):
        self.index = index
        self.N = index.total_docs
        self.doc_norms: dict[int, float] = {}
        self._precompute_norms()

    def _precompute_norms(self):
        doc_weights: dict[int, float] = {}
        for term, postings in self.index.index.items():
            idf = math.log10(self.N / len(postings)) if len(postings) > 0 else 0
            for doc_id, positions in postings.items():
                tf = 1 + math.log10(len(positions))
                w = tf * idf
                doc_weights[doc_id] = doc_weights.get(doc_id, 0) + w * w
        for doc_id, sum_sq in doc_weights.items():
            self.doc_norms[doc_id] = math.sqrt(sum_sq)

    def search(self, query_terms: list[str], top_k: int = 50) -> list[tuple[int, float]]:
        """全文档 TF-IDF 检索，返回 [(doc_id, cosine_similarity)]"""
        return self._rank(query_terms, None, top_k)

    def rank_subset(self, query_terms: list[str], doc_ids: set[int], top_k: int = 50) -> list[tuple[int, float]]:
        """对指定文档子集排序"""
        return self._rank(query_terms, doc_ids, top_k)

    def _rank(self, query_terms: list[str], doc_ids: set[int] | None, top_k: int) -> list[tuple[int, float]]:
        # 单次计算每个查询词的 IDF，复用于查询权重与文档权重，避免重复 log 计算
        query_weights: dict[str, float] = {}
        idf_cache: dict[str, float] = {}
        for term in set(query_terms):
            if term in self.index.index:
                idf = math.log10(self.N / len(self.index.index[term]))
                tf = 1 + math.log10(query_terms.count(term))
                idf_cache[term] = idf
                query_weights[term] = tf * idf

        query_norm = math.sqrt(sum(w * w for w in query_weights.values()))
        if query_norm == 0:
            return []

        scores: dict[int, float] = {}
        for term, q_weight in query_weights.items():
            idf = idf_cache[term]
            postings = self.index.index[term]
            for doc_id, positions in postings.items():
                if doc_ids is not None and doc_id not in doc_ids:
                    continue
                tf = 1 + math.log10(len(positions))
                d_weight = tf * idf
                scores[doc_id] = scores.get(doc_id, 0) + q_weight * d_weight

        results = []
        for doc_id, dot_product in scores.items():
            doc_norm = self.doc_norms.get(doc_id, 1)
            cosine = dot_product / (query_norm * doc_norm) if doc_norm > 0 else 0
            results.append((doc_id, round(cosine, 6)))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
