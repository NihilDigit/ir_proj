from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    top_k: int = 50


class ExpandedSearchRequest(BaseModel):
    query: str
    top_k: int = 50
    max_synonyms: int = 1


class SearchResultItem(BaseModel):
    doc_id: int
    title: str
    author: str
    snippet: str
    score: float | None = None
    highlighted_title: str
    highlighted_snippet: str


class SearchResponse(BaseModel):
    query: str
    result_count: int
    results: list[SearchResultItem]


class ExpandedSearchResponse(BaseModel):
    query: str
    expansion_map: dict[str, list[str]]
    expanded_query_terms: list[str]
    result_count: int
    results: list[SearchResultItem]


class SoundexSearchRequest(BaseModel):
    query: str
    top_k: int = 50
    limit_per_term: int = 5


class SoundexSuggestion(BaseModel):
    code: str
    candidates: list[str]


class SoundexSearchResponse(BaseModel):
    query: str
    suggestion_map: dict[str, SoundexSuggestion]
    expanded_query_terms: list[str]
    result_count: int
    results: list[SearchResultItem]


class PostingContext(BaseModel):
    position: int
    html: str


class PostingsEntry(BaseModel):
    doc_id: int
    title: str
    author: str
    bib: str
    tf: int
    positions: list[int]
    contexts: list[PostingContext]


class PostingsResponse(BaseModel):
    term: str
    stemmed_term: str
    df: int
    postings: list[PostingsEntry]


class DictionaryResponse(BaseModel):
    total: int
    page: int
    size: int
    terms: list[dict]


class DocumentResponse(BaseModel):
    doc_id: int
    title: str
    author: str
    bib: str
    text: str
    highlighted_title: str
    highlighted_text: str
