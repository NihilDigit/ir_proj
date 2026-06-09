from fastapi import APIRouter, Request

from ..models import (
    DictionaryResponse,
    PostingsResponse,
    PostingsEntry,
    PostingContext,
    DocumentResponse,
)
from ..core.highlighter import highlight_text

router = APIRouter()


@router.get("/index/dictionary", response_model=DictionaryResponse)
async def get_dictionary(
    request: Request,
    page: int = 1,
    size: int = 50,
    search: str = "",
    letter: str = "",
    sort_by: str = "term",
    sort_order: str = "asc",
):
    engine = request.app.state.engine
    terms, total = engine.index.get_dictionary(
        search=search,
        page=page,
        size=size,
        letter=letter,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return DictionaryResponse(total=total, page=page, size=size, terms=terms)


def _posting_contexts(engine, doc, stemmed_term: str, positions: list[int], window: int = 4):
    tokens = engine.index.preprocessor.tokenize(doc.title + " " + doc.text)
    contexts = []
    for pos in positions:
        if pos < 0 or pos >= len(tokens):
            continue
        start = max(0, pos - window)
        end = min(len(tokens), pos + window + 1)
        parts = []
        for i in range(start, end):
            if i == pos:
                parts.append(f"<mark>{stemmed_term}[{pos}]</mark>")
            else:
                parts.append(tokens[i])
        contexts.append(PostingContext(position=pos, html=" ".join(parts)))
    return contexts


@router.get("/index/postings/{term}", response_model=PostingsResponse)
async def get_postings(term: str, request: Request):
    engine = request.app.state.engine
    normalized = term.lower()
    stemmed = (
        normalized
        if normalized in engine.index.index
        else engine.index.preprocessor.stemmer.stem(normalized)
    )
    raw_postings = engine.index.index.get(stemmed, {})
    postings = [
        PostingsEntry(
            doc_id=doc_id,
            title=engine.index.documents[doc_id].title,
            author=engine.index.documents[doc_id].author,
            bib=engine.index.documents[doc_id].bib,
            tf=len(positions),
            positions=positions,
            contexts=_posting_contexts(
                engine, engine.index.documents[doc_id], stemmed, positions
            ),
        )
        for doc_id, positions in sorted(
            raw_postings.items(), key=lambda item: (-len(item[1]), item[0])
        )
    ]
    return PostingsResponse(
        term=term, stemmed_term=stemmed, df=len(postings), postings=postings
    )


@router.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: int, request: Request, highlight_terms: str = ""):
    engine = request.app.state.engine
    doc = engine.index.documents[doc_id]
    stemmer = engine.index.preprocessor.stemmer
    terms = highlight_terms.split(",") if highlight_terms else []
    return DocumentResponse(
        doc_id=doc.doc_id,
        title=doc.title,
        author=doc.author,
        bib=doc.bib,
        text=doc.text,
        highlighted_title=highlight_text(doc.title, terms, stemmer) if terms else doc.title,
        highlighted_text=highlight_text(doc.text, terms, stemmer) if terms else doc.text,
    )


@router.get("/queries")
async def get_queries(request: Request):
    engine = request.app.state.engine
    return [{"query_id": q.query_id, "text": q.text} for q in engine.queries]
