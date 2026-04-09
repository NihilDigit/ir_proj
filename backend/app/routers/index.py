from fastapi import APIRouter, Request

from ..models import DictionaryResponse, PostingsResponse, PostingsEntry, DocumentResponse
from ..core.highlighter import highlight_text

router = APIRouter()


@router.get("/index/dictionary", response_model=DictionaryResponse)
async def get_dictionary(
    request: Request, page: int = 1, size: int = 50, search: str = ""
):
    engine = request.app.state.engine
    terms, total = engine.index.get_dictionary(search=search, page=page, size=size)
    return DictionaryResponse(total=total, page=page, size=size, terms=terms)


@router.get("/index/postings/{term}", response_model=PostingsResponse)
async def get_postings(term: str, request: Request):
    engine = request.app.state.engine
    stemmed = engine.index.preprocessor.stemmer.stem(term.lower())
    raw_postings = engine.index.index.get(stemmed, {})
    postings = [
        PostingsEntry(doc_id=doc_id, tf=len(positions), positions=positions)
        for doc_id, positions in sorted(raw_postings.items())
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
