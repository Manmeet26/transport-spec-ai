from pathlib import Path


# -----------------------------
# PATHS
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

PDF_PATH = BASE_DIR / "data" / "specs.pdf"
CHUNKS_PATH = BASE_DIR / "data" / "chunks.json"
BM25_PATH = BASE_DIR / "data" / "bm25.pkl"
QDRANT_PATH = BASE_DIR / "qdrant_storage"


# -----------------------------
# COLLECTION
# -----------------------------

COLLECTION_NAME = "transport_specs"


# -----------------------------
# MODELS
# -----------------------------

EMBED_MODEL = "BAAI/bge-large-en-v1.5"

RERANK_MODEL = "BAAI/bge-reranker-large"

LLM_MODEL = "llama3.1:8b"

# later:
# LLM_MODEL = "mixtral:8x7b"


# -----------------------------
# RETRIEVAL
# -----------------------------

TOP_K = 20

FINAL_TOP_K = 6

MIN_RERANK_SCORE = 0.15


# -----------------------------
# CHUNKING
# -----------------------------

CHUNK_SIZE = 350

CHUNK_OVERLAP = 75