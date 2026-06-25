import pickle

from rank_bm25 import BM25Okapi

from config import BM25_PATH


def build_bm25(chunks):
    tokenized_chunks = [c["text"].split() for c in chunks]
    bm25 = BM25Okapi(tokenized_chunks)

    BM25_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(BM25_PATH, "wb") as f:
        pickle.dump(bm25, f)

    print(f"\nBM25 index saved to {BM25_PATH}.\n")