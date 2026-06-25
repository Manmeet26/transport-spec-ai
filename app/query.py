# query.py

import json
import numpy as np
from pathlib import Path
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder
from qdrant_client import QdrantClient
from qdrant_client.models import Filter
import ollama

from config import (
    COLLECTION_NAME,
    EMBED_MODEL,
    RERANK_MODEL,
    LLM_MODEL,
    TOP_K,
    FINAL_TOP_K,
    MIN_RERANK_SCORE
)

from prompts import (
    QUERY_REWRITE_PROMPT,
    GROUNDING_PROMPT
)

from conversation import conversation_history


BASE_DIR = Path(__file__).resolve().parent.parent

chunks_file = BASE_DIR / "data" / "chunks.json"

with open(chunks_file, "r") as f:
    chunks = json.load(f)

tokenized_chunks = [
    chunk["text"].split()
    for chunk in chunks
]

bm25 = BM25Okapi(tokenized_chunks)




embed_model = SentenceTransformer(
    EMBED_MODEL
)

reranker = CrossEncoder(
    RERANK_MODEL
)

from config import QDRANT_PATH

qdrant = QdrantClient(

    path=str(QDRANT_PATH)

)


def reciprocal_rank_fusion(
    vector_results,
    bm25_results,
    k=60
):

    scores = {}

    for rank, chunk in enumerate(vector_results):

        chunk_id = chunk["chunk_index"]

        scores[chunk_id] = (
            scores.get(chunk_id, 0)
            + 1 / (k + rank + 1)
        )

    for rank, chunk in enumerate(bm25_results):

        chunk_id = chunk["chunk_index"]

        scores[chunk_id] = (
            scores.get(chunk_id, 0)
            + 1 / (k + rank + 1)
        )

    ranked_ids = sorted(
        scores,
        key=scores.get,
        reverse=True
    )

    fused_chunks = []

    for idx in ranked_ids:

        fused_chunks.append(
            chunks[idx]
        )

    return fused_chunks


def get_recent_history(limit=6):

    recent = conversation_history[-limit:]

    history_text = ""

    for msg in recent:

        role = msg["role"]
        content = msg["content"]

        history_text += f"{role}: {content}\n"

    return history_text


def rewrite_query(question):

    history = get_recent_history()

    prompt = QUERY_REWRITE_PROMPT.format(
        history=history,
        question=question
    )

    response = ollama.chat(
        model="llama3.1:8b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    rewritten_query = (
        response["message"]["content"]
        .strip()
    )

    return rewritten_query


def retrieve_chunks(query):

    # VECTOR SEARCH

    query_embedding = embed_model.encode(
        query
    ).tolist()

    vector_results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=TOP_K
    )

    vector_chunks = []

    for hit in vector_results:

        payload = hit.payload

        vector_chunks.append({
            "text": payload["text"],
            "page": payload["page"],
            "section": payload["section"],
            "title": payload["title"],
            "chunk_index": payload["chunk_index"]
        })


    # BM25 SEARCH

    tokenized_query = query.split()

    bm25_scores = bm25.get_scores(
        tokenized_query
    )

    bm25_top_indices = np.argsort(
        bm25_scores
    )[::-1][:TOP_K]

    bm25_results = []

    for idx in bm25_top_indices:

        bm25_results.append(
            chunks[idx]
        )


    # RRF FUSION

    fused_chunks = reciprocal_rank_fusion(
        vector_chunks,
        bm25_results
    )


    # RERANKING

    rerank_pairs = [
        (query, chunk["text"])
        for chunk in fused_chunks
    ]

    rerank_scores = reranker.predict(
        rerank_pairs
    )

    reranked = sorted(
        zip(fused_chunks, rerank_scores),
        key=lambda x: x[1],
        reverse=True
    )

    final_chunks = []

    for chunk, score in reranked:

        if score >= MIN_RERANK_SCORE:

            final_chunks.append(chunk)

        if len(final_chunks) >= FINAL_TOP_K:

            break

    return final_chunks


def build_context(retrieved_chunks):

    context = ""

    for chunk in retrieved_chunks:

        context += f"""
Section: {chunk['section']}
Page: {chunk['page']}

{chunk['text']}

-------------------
"""

    return context


def generate_answer(question, retrieved_chunks):

    context = build_context(
        retrieved_chunks
    )

    conversation_context = (
        get_recent_history()
    )

    prompt = GROUNDING_PROMPT.format(
        conversation_context=conversation_context,
        context=context,
        question=question
    )

    stream = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        stream=True
    )

    full_answer = ""

    print("\nAnswer:\n")

    for chunk in stream:

        token = (
            chunk["message"]["content"]
        )

        print(token, end="", flush=True)

        full_answer += token

    print("\n")

    return full_answer


def ask_question(question):

    # STORE USER MESSAGE

    conversation_history.append({
        "role": "user",
        "content": question
    })


    # REWRITE QUERY

    rewritten_query = rewrite_query(
        question
    )

    print(
        f"\nRewritten Query: "
        f"{rewritten_query}"
    )


    # RETRIEVE CHUNKS

    retrieved_chunks = retrieve_chunks(
        rewritten_query
    )


    # GENERATE ANSWER

    answer = generate_answer(
        question,
        retrieved_chunks
    )


    # STORE ASSISTANT RESPONSE

    conversation_history.append({
        "role": "assistant",
        "content": answer
    })


    return {
        "answer": answer,
        "rewritten_query": rewritten_query
    }