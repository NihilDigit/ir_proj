"""布尔检索引擎 — 递归下降解析器，支持 AND/OR/NOT/括号"""

import re

from .indexer import InvertedIndex


class BooleanSearchEngine:
    def __init__(self, index: InvertedIndex):
        self.index = index
        self.all_doc_ids = set(index.documents.keys())

    def search(self, query: str) -> set[int]:
        tokens = self._tokenize(query)
        if not tokens:
            return set()
        result, _ = self._parse_or(tokens, 0)
        return result

    def _tokenize(self, query: str) -> list[str]:
        query = re.sub(r"([()])", r" \1 ", query)
        return query.split()

    def _parse_or(self, tokens: list[str], pos: int) -> tuple[set[int], int]:
        left, pos = self._parse_and(tokens, pos)
        while pos < len(tokens) and tokens[pos].upper() == "OR":
            pos += 1
            right, pos = self._parse_and(tokens, pos)
            left = left | right
        return left, pos

    def _parse_and(self, tokens: list[str], pos: int) -> tuple[set[int], int]:
        left, pos = self._parse_not(tokens, pos)
        while pos < len(tokens) and tokens[pos].upper() == "AND":
            pos += 1
            right, pos = self._parse_not(tokens, pos)
            left = left & right
        return left, pos

    def _parse_not(self, tokens: list[str], pos: int) -> tuple[set[int], int]:
        if pos < len(tokens) and tokens[pos].upper() == "NOT":
            pos += 1
            result, pos = self._parse_not(tokens, pos)
            return self.all_doc_ids - result, pos
        return self._parse_atom(tokens, pos)

    def _parse_atom(self, tokens: list[str], pos: int) -> tuple[set[int], int]:
        if pos >= len(tokens):
            return set(), pos
        if tokens[pos] == "(":
            pos += 1
            result, pos = self._parse_or(tokens, pos)
            if pos < len(tokens) and tokens[pos] == ")":
                pos += 1
            return result, pos
        term = self.index.preprocessor.stemmer.stem(tokens[pos].lower())
        postings = self.index.index.get(term, {})
        return set(postings.keys()), pos + 1

    @staticmethod
    def extract_terms(query: str) -> list[str]:
        """从布尔查询中提取纯词项（去掉 AND/OR/NOT/括号）"""
        tokens = re.sub(r"[()]", " ", query).split()
        return [t for t in tokens if t.upper() not in ("AND", "OR", "NOT")]
