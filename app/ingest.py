import uuid
import time
import json

import fitz

from tqdm import tqdm

from sentence_transformers import (
    SentenceTransformer
)

from qdrant_client import (
    QdrantClient
)

from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct
)

from config import *

from utils import (
    clean_text,
    split_into_chunks
)

from bm25_store import build_bm25


# -----------------------------
# START TIMER
# -----------------------------

start_time = time.time()

print("\nLoading embedding model...\n")


# -----------------------------
# LOAD EMBEDDING MODEL
# -----------------------------

embed_model = SentenceTransformer(
    EMBED_MODEL
)

print("Embedding model loaded.\n")


# -----------------------------
# OPEN PDF
# -----------------------------

print("Opening PDF...\n")

doc = fitz.open(PDF_PATH)

print(f"Loaded {len(doc)} pages.\n")


# -----------------------------
# INIT QDRANT
# -----------------------------

print("Initializing Qdrant...\n")

client = QdrantClient(
    path=str(QDRANT_PATH)
)


# -----------------------------
# RESET COLLECTION
# -----------------------------

if client.collection_exists(
    COLLECTION_NAME
):

    print(
        "Existing collection found."
    )

    print(
        "Deleting old collection...\n"
    )

    client.delete_collection(
        COLLECTION_NAME
    )


# -----------------------------
# CREATE COLLECTION
# -----------------------------

client.create_collection(

    collection_name=COLLECTION_NAME,

    vectors_config=VectorParams(
        size=1024,
        distance=Distance.COSINE
    )
)

print("Qdrant collection ready.\n")


# -----------------------------
# STORAGE
# -----------------------------

all_chunks = []

all_texts = []

chunk_id = 0


# -----------------------------
# PROCESS PDF
# -----------------------------

print("Processing PDF pages...\n")

for page_num, page in tqdm(
    enumerate(doc),
    total=len(doc),
    desc="Pages"
):

    text = page.get_text("text")

    text = clean_text(text)

    chunks = split_into_chunks(

        text,

        chunk_size=CHUNK_SIZE,

        overlap=CHUNK_OVERLAP
    )

    for chunk in chunks:

        chunk_data = {

            "page": page_num + 1,

            "section":
                chunk["section"],

            "title":
                chunk["title"],

            "chunk_index":
                chunk_id,

            "text":
                chunk["text"]
        }

        all_chunks.append(
            chunk_data
        )

        all_texts.append(
            chunk["text"]
        )

        chunk_id += 1


# -----------------------------
# SAVE CHUNKS
# -----------------------------

with open(
    "chunks.json",
    "w"
) as f:

    json.dump(
        all_chunks,
        f,
        indent=2
    )

print("\nSaved chunks.json\n")


# -----------------------------
# BUILD BM25
# -----------------------------

build_bm25(all_chunks)


# -----------------------------
# GENERATE EMBEDDINGS
# -----------------------------

print("\nGenerating embeddings...\n")

embeddings = embed_model.encode(

    all_texts,

    batch_size=32,

    show_progress_bar=True
)


# -----------------------------
# BUILD POINTS
# -----------------------------

points = []

for i in tqdm(
    range(len(all_chunks)),
    desc="Building vectors"
):

    chunk = all_chunks[i]

    embedding = embeddings[
        i
    ].tolist()

    point = PointStruct(

        id=str(uuid.uuid4()),

        vector=embedding,

        payload=chunk
    )

    points.append(point)


# -----------------------------
# UPSERT
# -----------------------------

print("\nUploading vectors...\n")

client.upsert(
    collection_name=COLLECTION_NAME,
    points=points
)


# -----------------------------
# FINAL STATS
# -----------------------------

elapsed = (
    time.time() - start_time
)

print("\n")
print("=" * 80)

print(
    f"\nTotal Chunks: "
    f"{len(all_chunks)}"
)

print(
    f"\nCompleted in "
    f"{elapsed:.2f} seconds.\n"
)