"""Cranfield 数据集解析器 (XML TREC 格式)"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass


@dataclass
class Document:
    doc_id: int
    title: str
    author: str
    bib: str
    text: str


@dataclass
class Query:
    query_id: int
    text: str


@dataclass
class Relevance:
    query_id: int
    doc_id: int
    relevance: int


def _parse_wrapped(filepath: str) -> ET.Element:
    """解析没有根元素的 XML 文件，自动包裹 <root>"""
    with open(filepath) as f:
        content = f.read()
    # 去掉可能的 XML 声明
    if content.startswith("<?xml"):
        content = content.split("?>", 1)[1]
    return ET.fromstring(f"<root>{content}</root>")


def parse_documents(filepath: str) -> list[Document]:
    root = _parse_wrapped(filepath)
    docs = []
    for doc_elem in root.findall("doc"):
        doc_id = int(doc_elem.findtext("docno", "0").strip())
        title = doc_elem.findtext("title", "").strip()
        author = doc_elem.findtext("author", "").strip()
        bib = doc_elem.findtext("bib", "").strip()
        text = doc_elem.findtext("text", "").strip()
        docs.append(Document(doc_id=doc_id, title=title, author=author, bib=bib, text=text))
    return docs


def parse_queries(filepath: str) -> list[Query]:
    root = _parse_wrapped(filepath)
    queries = []
    for top_elem in root.findall(".//top"):
        query_id = int(top_elem.findtext("num", "0").strip())
        text = top_elem.findtext("title", "").strip()
        queries.append(Query(query_id=query_id, text=text))
    return queries


def parse_relevance(filepath: str) -> list[Relevance]:
    rels = []
    with open(filepath) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 4:
                # TREC format: query_id, iter, doc_id, relevance
                rels.append(Relevance(
                    query_id=int(parts[0]),
                    doc_id=int(parts[2]),
                    relevance=int(parts[3]),
                ))
    return rels
