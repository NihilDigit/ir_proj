"""短语查询引擎 — 基于位置信息的短语匹配"""

from .indexer import InvertedIndex


class PhraseSearchEngine:
    def __init__(self, index: InvertedIndex):
        self.index = index

    def search(self, phrase: str) -> list[int]:
        terms = self.index.preprocessor.process_query(phrase)
        if not terms:
            return []
        if len(terms) == 1:
            return list(self.index.index.get(terms[0], {}).keys())

        postings_list = []
        for term in terms:
            p = self.index.index.get(term, {})
            if not p:
                return []
            postings_list.append(p)

        common_docs = set(postings_list[0].keys())
        for p in postings_list[1:]:
            common_docs &= set(p.keys())

        result = []
        for doc_id in common_docs:
            if self._check_positions(doc_id, postings_list):
                result.append(doc_id)
        return result

    def _check_positions(self, doc_id: int, postings_list: list[dict]) -> bool:
        first_positions = postings_list[0][doc_id]
        position_sets = [set(postings_list[i][doc_id]) for i in range(1, len(postings_list))]
        for start_pos in first_positions:
            match = True
            for i, pos_set in enumerate(position_sets, 1):
                if start_pos + i not in pos_set:
                    match = False
                    break
            if match:
                return True
        return False
