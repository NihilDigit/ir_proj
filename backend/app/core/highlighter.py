"""文本高亮 — 在匹配词项处插入 <mark> 标签"""

import re

from nltk.stem import PorterStemmer


def highlight_text(text: str, query_terms: list[str], stemmer: PorterStemmer) -> str:
    stem_set = {stemmer.stem(t.lower()) for t in query_terms}

    def _replace(match: re.Match) -> str:
        word = match.group(0)
        if stemmer.stem(word.lower()) in stem_set:
            return f"<mark>{word}</mark>"
        return word

    return re.sub(r"\b\w+\b", _replace, text)
