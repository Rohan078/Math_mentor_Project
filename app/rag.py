"""RAG pipeline: chunk knowledge base, embed with Groq, store in Chroma, retrieve top-k."""
from pathlib import Path
from typing import List, Tuple

import chromadb
from chromadb.config import Settings

from app.config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIR,
    KNOWLEDGE_BASE_DIR,
    RAG_CHUNK_OVERLAP,
    RAG_CHUNK_SIZE,
    RAG_TOP_K,
)
from app.embeddings import embed_texts


def _chunk_text(text: str, chunk_size: int = RAG_CHUNK_SIZE, overlap: int = RAG_CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks."""
    text = text.replace("\r\n", "\n").strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if end < len(text):
            last_break = max(chunk.rfind("\n"), chunk.rfind(". "), chunk.rfind(" "))
            if last_break > chunk_size // 2:
                chunk = chunk[: last_break + 1]
                end = start + last_break + 1
        chunk = chunk.strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap if end < len(text) else len(text)
    return chunks


def _load_docs_from_dir(kb_dir: Path) -> List[Tuple[str, str]]:
    """Load all .md and .txt from knowledge_base. Returns list of (source_id, content)."""
    out = []
    for path in sorted(kb_dir.glob("**/*")):
        if path.is_file() and path.suffix.lower() in (".md", ".txt"):
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                source_id = path.name
                out.append((source_id, content))
            except Exception:
                continue
    return out


def build_index(force_rebuild: bool = False) -> chromadb.Collection:
    """Build or load Chroma collection from knowledge_base. Returns collection."""
    client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR), settings=Settings(anonymized_telemetry=False))
    existing = [c.name for c in client.list_collections()]
    if not force_rebuild and CHROMA_COLLECTION_NAME in existing:
        return client.get_collection(name=CHROMA_COLLECTION_NAME)

    if CHROMA_COLLECTION_NAME in existing:
        client.delete_collection(CHROMA_COLLECTION_NAME)
    collection = client.create_collection(name=CHROMA_COLLECTION_NAME, metadata={"description": "math_mentor_kb"})

    docs = _load_docs_from_dir(KNOWLEDGE_BASE_DIR)
    if not docs:
        return collection

    all_chunks = []
    all_metadatas = []
    for source_id, content in docs:
        for i, chunk in enumerate(_chunk_text(content)):
            all_chunks.append(chunk)
            all_metadatas.append({"source": source_id, "chunk_id": i})

    if not all_chunks:
        return collection

    embeddings = embed_texts(all_chunks)
    ids = [f"{i}" for i in range(len(all_chunks))]
    collection.add(ids=ids, embeddings=embeddings, documents=all_chunks, metadatas=all_metadatas)
    return collection


def get_collection() -> chromadb.Collection:
    """Get existing Chroma collection (does not build)."""
    client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR), settings=Settings(anonymized_telemetry=False))
    return client.get_collection(name=CHROMA_COLLECTION_NAME)


def retrieve(query: str, top_k: int = RAG_TOP_K) -> List[dict]:
    """Retrieve top-k chunks. Returns list of dicts with content, source, chunk_id, distance; [] on failure."""
    try:
        collection = get_collection()
    except Exception:
        return []
    if collection.count() == 0:
        return []

    try:
        from app.embeddings import embed_query
        q_emb = embed_query(query)
    except Exception:
        return []

    try:
        results = collection.query(
            query_embeddings=[q_emb],
            n_results=min(top_k, collection.count()),
            include=["documents", "metadatas", "distances"],
        )
    except Exception:
        return []

    out = []
    docs = results.get("documents", [[]])
    metadatas = results.get("metadatas", [[]])
    distances = results.get("distances", [[]])
    for i in range(len(docs[0]) if docs else 0):
        meta = metadatas[0][i] if metadatas and metadatas[0] else {}
        out.append({
            "content": docs[0][i] if docs else "",
            "source": meta.get("source", "unknown"),
            "chunk_id": meta.get("chunk_id", 0),
            "distance": distances[0][i] if distances and distances[0] else None,
        })
    return out
