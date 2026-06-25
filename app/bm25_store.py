import pickle

from rank_bm25 import BM25Okapi


# -----------------------------
# BUILD BM25 INDEX
# -----------------------------

def build_bm25(chunks):

    tokenized_chunks = [

        c["text"].split()

        for c in chunks
    ]

    bm25 = BM25Okapi(
        tokenized_chunks
    )

    with open(
        "bm25.pkl",
        "wb"
    ) as f:

        pickle.dump(
            bm25,
            f
        )

    print("\nBM25 index saved.\n")