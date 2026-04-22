"""Soundex 发音编码与基于发音的拼写/查询矫正"""

from collections import defaultdict


_CODE_MAP = {
    **dict.fromkeys("bfpv", "1"),
    **dict.fromkeys("cgjkqsxz", "2"),
    **dict.fromkeys("dt", "3"),
    "l": "4",
    **dict.fromkeys("mn", "5"),
    "r": "6",
}


def soundex(word: str) -> str:
    """标准 Soundex 编码：首字母 + 3 位数字。"""
    if not word:
        return ""
    word = word.lower()
    first = word[0].upper()
    digits: list[str] = []
    prev = _CODE_MAP.get(word[0], "")
    for ch in word[1:]:
        if ch in "hw":
            continue
        d = _CODE_MAP.get(ch, "")
        if d:
            if d != prev:
                digits.append(d)
            prev = d
        else:
            prev = ""
    return (first + "".join(digits) + "000")[:4]


class SoundexCorrector:
    """基于词典的 Soundex 发音矫正：把查询词映射到发音相近的词典词。"""

    def __init__(self, dictionary_terms):
        self.code_to_terms: dict[str, set[str]] = defaultdict(set)
        for term in dictionary_terms:
            if not term:
                continue
            self.code_to_terms[soundex(term)].add(term)

    def suggest(self, word: str, limit: int = 10) -> tuple[str, list[str]]:
        code = soundex(word)
        w = word.lower()
        raw = self.code_to_terms.get(code, set()) - {w}

        def _rank(cand: str) -> tuple:
            # 优先：公共前缀最长 > 长度差最小 > 字母序
            prefix = 0
            for a, b in zip(w, cand):
                if a == b:
                    prefix += 1
                else:
                    break
            return (-prefix, abs(len(cand) - len(w)), cand)

        candidates = sorted(raw, key=_rank)
        return code, candidates[:limit]

    def expand(self, query_terms: list[str], limit_per_term: int = 5) -> dict:
        """为每个查询词提供 Soundex 候选词；检索只用 top-1 候选，其余候选仅供 UI 展示。

        把 5 个候选全塞进 TF-IDF 会让拼写相近但语义无关的词（如 fail/fall 对 flow）
        主导排序。只用 top-1 最像的候选，检索结果更聚焦。
        """
        suggestion_map: dict[str, dict] = {}
        search_terms: set[str] = set(t.lower() for t in query_terms)
        for term in query_terms:
            code, candidates = self.suggest(term, limit_per_term)
            suggestion_map[term] = {"code": code, "candidates": candidates}
            if candidates:
                search_terms.add(candidates[0])
        return {
            "original_terms": query_terms,
            "suggestion_map": suggestion_map,
            "expanded_terms": sorted(search_terms),
        }
