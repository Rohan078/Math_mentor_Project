"""Configuration for Math Mentor."""
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=True)
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"
DATA_DIR = PROJECT_ROOT / "data"
CHROMA_PERSIST_DIR = DATA_DIR / "chroma"
MEMORY_DB_PATH = DATA_DIR / "memory.jsonl"

DATA_DIR.mkdir(exist_ok=True)
CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)

_raw_key = os.getenv("GROQ_API_KEY", "")
if _raw_key:
    _key = "".join(c for c in _raw_key.strip().strip('"').strip("'") if c.isprintable() or c in "\n\r")
    GROQ_API_KEY = _key.strip()
else:
    GROQ_API_KEY = ""
GROQ_CHAT_MODEL = os.getenv("GROQ_CHAT_MODEL", "llama-3.3-70b-versatile")
GROQ_VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "llama-3.3-70b-versatile")
GROQ_EMBEDDING_MODEL = "nomic-embed-text-v1.5"

RAG_TOP_K = 5
RAG_CHUNK_SIZE = 512
RAG_CHUNK_OVERLAP = 64
OCR_CONFIDENCE_THRESHOLD = 0.6
ASR_CONFIDENCE_THRESHOLD = 0.7
CHROMA_COLLECTION_NAME = "math_mentor_kb"
