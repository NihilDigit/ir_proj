import nltk
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .engine import SearchEngine
from .routers import search, index


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 确保 NLTK 数据已下载
    for res in ["stopwords", "wordnet"]:
        nltk.download(res, quiet=True)
    # 初始化搜索引擎
    app.state.engine = SearchEngine()
    yield


app = FastAPI(title="Cranfield IR System", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api")
app.include_router(index.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok", "doc_count": app.state.engine.index.total_docs}
