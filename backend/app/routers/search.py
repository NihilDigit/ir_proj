from fastapi import APIRouter, Request

from ..models import (
    SearchRequest,
    ExpandedSearchRequest,
    SearchResponse,
    ExpandedSearchResponse,
    SearchResultItem,
    SoundexSearchRequest,
    SoundexSearchResponse,
    SoundexSuggestion,
)
from ..core.boolean_search import BooleanSearchEngine
from ..core.highlighter import highlight_text

router = APIRouter()


def _build_results(
    engine, ranked: list[tuple[int, float]], query_terms: list[str]
) -> list[SearchResultItem]:
    stemmer = engine.index.preprocessor.stemmer
    results = []
    for doc_id, score in ranked:
        doc = engine.index.documents[doc_id]
        snippet = doc.text[:300]
        results.append(
            SearchResultItem(
                doc_id=doc_id,
                title=doc.title,
                author=doc.author,
                snippet=snippet,
                score=score,
                highlighted_title=highlight_text(doc.title, query_terms, stemmer),
                highlighted_snippet=highlight_text(snippet, query_terms, stemmer),
            )
        )
    return results


@router.post("/search/boolean", response_model=SearchResponse)
async def boolean_search(req: SearchRequest, request: Request):
    engine = request.app.state.engine
    doc_ids = engine.boolean_engine.search(req.query)
    pure_terms = BooleanSearchEngine.extract_terms(req.query)
    query_terms = engine.index.preprocessor.process_query(" ".join(pure_terms))
    ranked = engine.tfidf_ranker.rank_subset(query_terms, doc_ids, req.top_k)
    results = _build_results(engine, ranked, pure_terms)
    return SearchResponse(query=req.query, result_count=len(doc_ids), results=results)


@router.post("/search/phrase", response_model=SearchResponse)
async def phrase_search(req: SearchRequest, request: Request):
    engine = request.app.state.engine
    doc_ids = engine.phrase_engine.search(req.query)
    query_terms = engine.index.preprocessor.process_query(req.query)
    ranked = engine.tfidf_ranker.rank_subset(query_terms, set(doc_ids), req.top_k)
    # 原始词用于高亮
    raw_terms = req.query.split()
    results = _build_results(engine, ranked, raw_terms)
    return SearchResponse(query=req.query, result_count=len(doc_ids), results=results)


@router.post("/search/expanded", response_model=ExpandedSearchResponse)
async def expanded_search(req: ExpandedSearchRequest, request: Request):
    engine = request.app.state.engine
    original_terms = engine.index.preprocessor.process_query(req.query)
    expansion = engine.expander.expand(
        req.query.lower().split(), req.max_synonyms
    )
    ranked = engine.tfidf_ranker.search(expansion["expanded_stemmed"], req.top_k)
    results = _build_results(engine, ranked, expansion["expanded_terms"])
    return ExpandedSearchResponse(
        query=req.query,
        expansion_map=expansion["expansion_map"],
        expanded_query_terms=expansion["expanded_terms"],
        result_count=len(ranked),
        results=results,
    )


@router.post("/search/soundex", response_model=SoundexSearchResponse)
async def soundex_search(req: SoundexSearchRequest, request: Request):
    engine = request.app.state.engine
    raw_terms = req.query.lower().split()
    expansion = engine.soundex_corrector.expand(raw_terms, req.limit_per_term)
    # 候选词已是 stem 形式（来自倒排索引），直接作为检索词
    stemmer = engine.index.preprocessor.stemmer
    stemmed_terms = list({stemmer.stem(t) for t in expansion["expanded_terms"]})
    ranked = engine.tfidf_ranker.search(stemmed_terms, req.top_k)
    results = _build_results(engine, ranked, expansion["expanded_terms"])
    suggestion_map = {
        term: SoundexSuggestion(code=info["code"], candidates=info["candidates"])
        for term, info in expansion["suggestion_map"].items()
    }
    return SoundexSearchResponse(
        query=req.query,
        suggestion_map=suggestion_map,
        expanded_query_terms=expansion["expanded_terms"],
        result_count=len(ranked),
        results=results,
    )
