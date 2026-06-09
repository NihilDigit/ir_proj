"""倒排索引构建（含位置信息）"""

import pickle
from pathlib import Path

from .parser import Document
from .preprocessor import Preprocessor


class InvertedIndex:
    def __init__(self):
        self.index: dict[str, dict[int, list[int]]] = {}  # term -> {doc_id -> [positions]}
        self.doc_lengths: dict[int, int] = {}
        self.total_docs: int = 0
        self.documents: dict[int, Document] = {}
        self.preprocessor = Preprocessor()

    def build(self, documents: list[Document]):
        self.total_docs = len(documents)
        for doc in documents:
            self.documents[doc.doc_id] = doc
            full_text = doc.title + " " + doc.text
            tokens = self.preprocessor.process(full_text)
            self.doc_lengths[doc.doc_id] = len(tokens)
            for term, pos in tokens:
                if term not in self.index:
                    self.index[term] = {}
                if doc.doc_id not in self.index[term]:
                    self.index[term][doc.doc_id] = []
                self.index[term][doc.doc_id].append(pos)

    def get_postings(self, term: str) -> dict[int, list[int]]:
        stemmed = self.preprocessor.stemmer.stem(term.lower())
        return self.index.get(stemmed, {})

    def get_dictionary(
        self, search: str = "", page: int = 1, size: int = 50, letter: str = ""
    ) -> tuple[list[dict], int]:
        items = []
        normalized_letter = letter.lower()
        for term, postings in sorted(self.index.items()):
            if search and not term.startswith(search.lower()):
                continue
            if not search and normalized_letter and normalized_letter != "all":
                if normalized_letter == "#":
                    if term and term[0].isalpha():
                        continue
                elif not term.startswith(normalized_letter):
                    continue
            df = len(postings)
            tf_total = sum(len(positions) for positions in postings.values())
            items.append({"term": term, "df": df, "total_freq": tf_total})
        total = len(items)
        start = (page - 1) * size
        return items[start : start + size], total

    def save(self, path: Path):
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path: Path) -> "InvertedIndex":
        with open(path, "rb") as f:
            return pickle.load(f)
