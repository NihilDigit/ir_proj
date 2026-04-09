"""文本预处理：分词、去停用词、Porter 词干提取"""

import re

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


class Preprocessor:
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words("english"))
        self.punct_re = re.compile(r"[^\w\s]")

    def tokenize(self, text: str) -> list[str]:
        text = text.lower()
        text = self.punct_re.sub(" ", text)
        return text.split()

    def process(self, text: str) -> list[tuple[str, int]]:
        """返回 (词干化词项, 原始位置) 列表，位置基于原始 token 序列"""
        tokens = self.tokenize(text)
        result = []
        for pos, token in enumerate(tokens):
            if token not in self.stop_words and len(token) > 1:
                stemmed = self.stemmer.stem(token)
                result.append((stemmed, pos))
        return result

    def process_query(self, text: str) -> list[str]:
        """处理查询文本，返回词干化词项列表"""
        tokens = self.tokenize(text)
        return [self.stemmer.stem(t) for t in tokens if t not in self.stop_words and len(t) > 1]
