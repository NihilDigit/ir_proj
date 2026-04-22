"""搜索引擎：统一管理所有核心模块"""

from .config import DOCS_FILE, QUERY_FILE, QREL_FILE, INDEX_CACHE
from .core.parser import parse_documents, parse_queries, parse_relevance
from .core.indexer import InvertedIndex
from .core.boolean_search import BooleanSearchEngine
from .core.phrase_search import PhraseSearchEngine
from .core.tfidf import TFIDFRanker
from .core.query_expansion import QueryExpander
from .core.soundex import SoundexCorrector


class SearchEngine:
    def __init__(self):
        # 解析数据
        self.docs = parse_documents(str(DOCS_FILE))
        self.queries = parse_queries(str(QUERY_FILE))
        self.relevance = parse_relevance(str(QREL_FILE))

        # 构建或加载索引
        if INDEX_CACHE.exists():
            self.index = InvertedIndex.load(INDEX_CACHE)
        else:
            self.index = InvertedIndex()
            self.index.build(self.docs)
            INDEX_CACHE.parent.mkdir(parents=True, exist_ok=True)
            self.index.save(INDEX_CACHE)

        # 初始化各引擎
        self.boolean_engine = BooleanSearchEngine(self.index)
        self.phrase_engine = PhraseSearchEngine(self.index)
        self.tfidf_ranker = TFIDFRanker(self.index)
        self.expander = QueryExpander(self.index.preprocessor)
        self.soundex_corrector = SoundexCorrector(self.index.index.keys())
