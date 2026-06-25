# query.py

import json
from rank_bm25 import BM25Okapi
import ollama

from config import (
    CHUNKS_PATH,
    COLLECTION_NAME,
    EMBED_MODEL,
    RERANK_MODEL,
    LLM_MODEL,
    TOP_K,
    FINAL_TOP_K,
    MIN_RERANK_SCORE,
    QDRANT_PATH,
)

from prompts import (
    QUERY_REWRITE_PROMPT,
    GROUNDING_PROMPT
)

from conversation import conversation_history
from rag_utils import (
    reciprocal_rank_fusion,
    filter_reranked_chunks,
    build_citations,
)

_resources = {}


def _load_resources():
    if _resources:
        return _resources

    from sentence_transformers import SentenceTransformer, CrossEncoder
    from qdrant_client import QdrantClient

    with open(CHUNKS_PATH, "r") as f:
        chunks = json.load(f)

    tokenized_chunks = [chunk["text"].split() for chunk in chunks]

    _resources["chunks"] = chunks
    _resources["bm25"] = BM25Okapi(tokenized_chunks)
    _resources["embed_model"] = SentenceTransformer(EMBED_MODEL)
    _resources["reranker"] = CrossEncoder(RERANK_MODEL)
    _resources["qdrant"] = QdrantClient(path=str(QDRANT_PATH))

    return _resources


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
        model=LLM_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"].strip()


def retrieve_chunks(query):
    import numpy as np

    resources = _load_resources()
    chunks = resources["chunks"]
    bm25 = resources["bm25"]
    embed_model = resources["embed_model"]
    reranker = resources["reranker"]
    qdrant = resources["qdrant"]

    query_embedding = embed_model.encode(query).tolist()

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

    tokenized_query = query.split()
    bm25_scores = bm25.get_scores(tokenized_query)
    bm25_top_indices = np.argsort(bm25_scores)[::-1][:TOP_K]
    bm25_results = [chunks[idx] for idx in bm25_top_indices]

    fused_chunks = reciprocal_rank_fusion(
        vector_chunks,
        bm25_results,
        chunks,
    )

    rerank_pairs = [(query, chunk["text"]) for chunk in fused_chunks]
    rerank_scores = reranker.predict(rerank_pairs)

    reranked = sorted(
        zip(fused_chunks, rerank_scores),
        key=lambda x: x[1],
        reverse=True
    )

    return filter_reranked_chunks(
        reranked,
        MIN_RERANK_SCORE,
        FINAL_TOP_K,
    )


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
    context = build_context(retrieved_chunks)
    conversation_context = get_recent_history()

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
        token = chunk["message"]["content"]
        print(token, end="", flush=True)
        full_answer += token

    print("\n")

    return full_answer


def ask_question(question):
    conversation_history.append({
        "role": "user",
        "content": question
    })

    rewritten_query = rewrite_query(question)

    print(f"\nRewritten Query: {rewritten_query}")

    retrieved_chunks = retrieve_chunks(rewritten_query)
    answer = generate_answer(question, retrieved_chunks)

    conversation_history.append({
        "role": "assistant",
        "content": answer
    })

    return {
        "answer": answer,
        "rewritten_query": rewritten_query,
        "citations": build_citations(retrieved_chunks),
    }
