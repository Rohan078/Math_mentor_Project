"""Build RAG vector index from knowledge_base. Run once before first use (or use sidebar button in app)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.rag import build_index

if __name__ == "__main__":
    print("Building RAG index from knowledge_base/ ...")
    coll = build_index(force_rebuild=True)
    print(f"Done. Collection has {coll.count()} chunks.")
