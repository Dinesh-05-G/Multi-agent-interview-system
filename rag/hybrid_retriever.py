from rag.retrieve import retrieve
from rag.bm25_retriever import search_bm25

def normalize_scores(results, lower_is_better=False):
    """
    Normalize scores between 0 and 1.

    For FAISS:
        Lower distance = better result.

    For BM25:
        Higher score = better result.
    """

    if not results:
        return results

    scores = [result["score"] for result in results]

    min_score = min(scores)
    max_score = max(scores)

    # Avoid division by zero
    if max_score == min_score:
        for result in results:
            result["normalized_score"] = 1.0

        return results

    for result in results:

        if lower_is_better:
            # FAISS L2 distance:
            # lower distance means more similar
            result["normalized_score"] = (
                (max_score - result["score"])
                / (max_score - min_score)
            )

        else:
            # BM25:
            # higher score means better match
            result["normalized_score"] = (
                (result["score"] - min_score)
                / (max_score - min_score)
            )

    return results


def hybrid_search(
    query: str,
    top_k: int = 3,
    alpha: float = 0.5
):
    """
    Combine FAISS semantic search and BM25 keyword search.

    alpha:
        Weight given to FAISS.

        0.5 = FAISS 50% + BM25 50%
        0.7 = FAISS 70% + BM25 30%
        0.3 = FAISS 30% + BM25 70%
    """

    # --------------------------------------------------
    # 1. FAISS Semantic Search
    # --------------------------------------------------

    faiss_results = retrieve(
        query,
        top_k=top_k
    )

    # --------------------------------------------------
    # 2. BM25 Keyword Search
    # --------------------------------------------------

    bm25_results = search_bm25(
        query,
        top_k=top_k
    )

    # --------------------------------------------------
    # 3. Normalize FAISS Scores
    # --------------------------------------------------

    faiss_results = normalize_scores(
        faiss_results,
        lower_is_better=True
    )

    # --------------------------------------------------
    # 4. Normalize BM25 Scores
    # --------------------------------------------------

    bm25_results = normalize_scores(
        bm25_results,
        lower_is_better=False
    )

    # --------------------------------------------------
    # 5. Combine Results
    # --------------------------------------------------

    combined = {}

    # Add FAISS results
    for result in faiss_results:

        document = result["document"]

        # Use concept as document identifier
        key = document["concept"]

        combined[key] = {
            "document": document,
            "faiss_score": result["normalized_score"],
            "bm25_score": 0.0
        }

    # Add BM25 results
    for result in bm25_results:

        document = result["document"]

        key = document["concept"]

        if key not in combined:

            combined[key] = {
                "document": document,
                "faiss_score": 0.0,
                "bm25_score": 0.0
            }

        combined[key]["bm25_score"] = (
            result["normalized_score"]
        )

    # --------------------------------------------------
    # 6. Calculate Hybrid Score
    # --------------------------------------------------

    results = []

    for item in combined.values():

        hybrid_score = (
            alpha * item["faiss_score"]
            +
            (1 - alpha) * item["bm25_score"]
        )

        results.append({
            "document": item["document"],
            "faiss_score": item["faiss_score"],
            "bm25_score": item["bm25_score"],
            "hybrid_score": hybrid_score
        })

    # --------------------------------------------------
    # 7. Sort by Hybrid Score
    # --------------------------------------------------

    results.sort(
        key=lambda x: x["hybrid_score"],
        reverse=True
    )

    return results[:top_k]


# ------------------------------------------------------
# TEST
# ------------------------------------------------------

if __name__ == "__main__":

    query = "Python decorators functions"

    print("HYBRID RAG SEARCH")
    print("=" * 70)

    print(f"Query: {query}")
    print()

    results = hybrid_search(
        query=query,
        top_k=3,
        alpha=0.5
    )

    for i, result in enumerate(
        results,
        start=1
    ):

        document = result["document"]

        print(f"Result {i}")
        print("-" * 70)

        print(
            f"FAISS Score : "
            f"{result['faiss_score']:.4f}"
        )

        print(
            f"BM25 Score  : "
            f"{result['bm25_score']:.4f}"
        )

        print(
            f"Hybrid Score: "
            f"{result['hybrid_score']:.4f}"
        )

        print(
            f"Concept     : "
            f"{document['concept']}"
        )

        print(
            f"Topic       : "
            f"{document['topic']}"
        )

        print(
            f"Difficulty  : "
            f"{document['difficulty']}"
        )

        print(
            f"Knowledge   : "
            f"{document['knowledge']}"
        )

        print()