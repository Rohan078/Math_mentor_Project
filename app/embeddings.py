"""Embeddings using Groq (nomic-embed-text) with fallback to sentence-transformers."""
from typing import List
from app.config import GROQ_API_KEY, GROQ_EMBEDDING_MODEL

_GROQ_CLIENT = None
_FALLBACK_MODEL = None


def _get_groq():
    global _GROQ_CLIENT
    if _GROQ_CLIENT is None and GROQ_API_KEY:
        from groq import Groq
        _GROQ_CLIENT = Groq(api_key=GROQ_API_KEY)
    return _GROQ_CLIENT


def _get_fallback():
    global _FALLBACK_MODEL
    if _FALLBACK_MODEL is None:
        from sentence_transformers import SentenceTransformer
        _FALLBACK_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _FALLBACK_MODEL


def embed_texts(texts: List[str]) -> List[List[float]]:
    client = _get_groq()
    if client:
        for model_id in ["nomic-embed-text-v1.5", "nomic-embed-text-v1_5", GROQ_EMBEDDING_MODEL]:
            try:
                resp = client.embeddings.create(input=texts, model=model_id)
                return [d.embedding for d in resp.data]
            except Exception:
                continue
    model = _get_fallback()
    return model.encode(texts, convert_to_numpy=True).tolist()


def embed_query(query: str) -> List[float]:
    return embed_texts([query])[0]
