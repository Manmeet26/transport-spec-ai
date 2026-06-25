from rag_utils import (
    reciprocal_rank_fusion,
    filter_reranked_chunks,
    build_citations,
)


SAMPLE_CHUNKS = [
    {
        "chunk_index": 0,
        "section": "90-1.02C",
        "title": "Concrete Requirements",
        "page": 12,
        "text": "Concrete shall cure for at least seven days under normal weather.",
    },
    {
        "chunk_index": 1,
        "section": "90-1.03A",
        "title": "Cold Weather",
        "page": 14,
        "text": "Cold weather curing requires insulated blankets and temperature monitoring.",
    },
    {
        "chunk_index": 2,
        "section": "87-1.01",
        "title": "Pull Boxes",
        "page": 88,
        "text": "Pull boxes must be installed per manufacturer requirements and anchored.",
    },
]


def test_reciprocal_rank_fusion_prefers_chunks_in_both_lists():
    vector_results = [SAMPLE_CHUNKS[0], SAMPLE_CHUNKS[2]]
    bm25_results = [SAMPLE_CHUNKS[0], SAMPLE_CHUNKS[1]]

    fused = reciprocal_rank_fusion(
        vector_results,
        bm25_results,
        SAMPLE_CHUNKS,
    )

    assert fused[0]["chunk_index"] == 0


def test_filter_reranked_chunks_applies_threshold_and_limit():
    reranked = [
        (SAMPLE_CHUNKS[0], 0.42),
        (SAMPLE_CHUNKS[1], 0.18),
        (SAMPLE_CHUNKS[2], 0.05),
    ]

    final = filter_reranked_chunks(reranked, min_score=0.15, final_top_k=2)

    assert len(final) == 2
    assert final[0]["section"] == "90-1.02C"
    assert final[1]["section"] == "90-1.03A"


def test_build_citations_includes_metadata_and_snippet():
    citations = build_citations([SAMPLE_CHUNKS[0], SAMPLE_CHUNKS[1]])

    assert citations[0]["section"] == "90-1.02C"
    assert citations[0]["page"] == 12
    assert "Concrete shall cure" in citations[0]["snippet"]
    assert citations[1]["title"] == "Cold Weather"
