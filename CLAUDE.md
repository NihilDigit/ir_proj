# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Cranfield IR search engine — a course project implementing a full-stack information retrieval system on the Cranfield dataset (1,400 aerospace documents, 225 queries, 1,837 relevance judgments). Python FastAPI backend + Vue 3 frontend.

## Commands

### Backend (working directory: `backend/`)
```bash
uv sync                                          # install dependencies
uv run python -m uvicorn app.main:app --port 8000 --reload  # start dev server
uv run python -c "from app.core.parser import parse_documents; ..."  # test modules
```

NLTK data (stopwords, wordnet) is auto-downloaded on first startup via the FastAPI lifespan handler.

### Frontend (working directory: `frontend/`)
```bash
bun install        # install dependencies
bun run dev        # start dev server (proxies /api → localhost:8000)
bun run build      # production build
```

Both servers must run simultaneously. Vite proxies `/api` requests to the backend.

## Architecture

```
Data Flow:  Cranfield XML → Parser → Preprocessor → InvertedIndex → SearchEngines → FastAPI → Vue UI

backend/app/
├── engine.py          # Coordinator: loads data, builds index, initializes all engines
├── main.py            # FastAPI lifespan + CORS + route mounting
├── config.py          # Path constants (DATA_DIR, INDEX_CACHE)
├── models.py          # Pydantic request/response schemas
├── core/
│   ├── parser.py          # XML parser for Cranfield docs/queries/relevance
│   ├── preprocessor.py    # Tokenize → lowercase → remove stopwords → Porter stem
│   ├── indexer.py         # Inverted index: term → {doc_id → [positions]}
│   ├── boolean_search.py  # Recursive descent parser for AND/OR/NOT/parens
│   ├── phrase_search.py   # Position-based consecutive term matching
│   ├── tfidf.py           # Log TF-IDF + cosine similarity ranking
│   ├── query_expansion.py # WordNet synonym expansion
│   └── highlighter.py     # Injects <mark> tags around matching stems
└── routers/
    ├── search.py      # POST /api/search/{boolean,phrase,expanded}
    └── index.py       # GET /api/index/dictionary, /postings/{term}, /documents/{id}

frontend/src/
├── api.js             # Axios wrapper for all backend endpoints
├── components/
│   ├── BooleanSearch.vue   # AND/OR/NOT operator buttons + search
│   ├── PhraseSearch.vue    # Consecutive phrase query
│   ├── ExpandedSearch.vue  # WordNet synonyms + search
│   ├── IndexViewer.vue     # Paginated dictionary + postings viewer
│   └── ResultList.vue      # Shared: ranked results with highlights + detail expand
```

## Key Design Decisions

- **Position-aware index**: Stopwords are removed but original token positions are preserved (not reindexed), enabling correct phrase queries like "boundary layer".
- **Stemming consistency**: Both indexing and querying use the same `PorterStemmer` instance. Double-stemming is safe (already-stemmed terms pass through unchanged).
- **Index caching**: First build pickles to `backend/app/data/index.pkl`; subsequent starts load from cache. Delete the pickle to force rebuild.
- **Server-side highlighting**: Backend returns HTML with `<mark>` tags; frontend renders via `v-html`. Safe because Cranfield data is static/trusted.
- **All search modes rank results**: Boolean and phrase searches filter documents first, then rank the filtered set using TF-IDF cosine similarity.
