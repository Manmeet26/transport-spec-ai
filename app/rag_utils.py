"""Pure retrieval helpers used by query.py and tests."""


def reciprocal_rank_fusion(vector_results, bm25_results, chunks, k=60):
    scores = {}

    for rank, chunk in enumerate(vector_results):
        chunk_id = chunk["chunk_index"]
        scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (k + rank + 1)

    for rank, chunk in enumerate(bm25_results):
        chunk_id = chunk["chunk_index"]
        scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (k + rank + 1)

    ranked_ids = sorted(scores, key=scores.get, reverse=True)
    return [chunks[idx] for idx in ranked_ids]


def filter_reranked_chunks(reranked_pairs, min_score, final_top_k):
    final_chunks = []

    for chunk, score in reranked_pairs:
        if score >= min_score:
            final_chunks.append(chunk)

        if len(final_chunks) >= final_top_k:
            break

    return final_chunks


def build_citations(retrieved_chunks):
    citations = []

    for chunk in retrieved_chunks:
        section = chunk.get("section") or "Unknown"
        title = chunk.get("title") or ""
        page = chunk.get("page")
        snippet = chunk.get("text", "")[:240].strip()

        if len(chunk.get("text", "")) > 240:
            snippet += "..."

        citations.append(
            {
                "section": section,
                "title": title,
                "page": page,
                "snippet": snippet,
            }
        )

    return citations
