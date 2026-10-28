from pathlib import Path
from sentence_transformers import CrossEncoder


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

print("Loading reranker model...")
reranker_model = CrossEncoder(MODEL_NAME)
print("Reranker model loaded successfully.")


# ============================================================
# DOCUMENT TEXT
# ============================================================

def create_document_text(document: dict) -> str:

    return f"""
Topic: {document["topic"]}

Difficulty: {document["difficulty"]}

Concept: {document["concept"]}

Knowledge:
{document["knowledge"]}

Interview Focus:
{", ".join(document["interview_focus"])}
""".strip()


# ============================================================
# RERANK
# ============================================================

def rerank(query: str, results: list, top_k: int = 3):

    if not results:
        return []

    documents = [
        result["document"]
        for result in results
    ]

    document_texts = [
        create_document_text(document)
        for document in documents
    ]

    # Create query-document pairs
    pairs = [
        [query, document_text]
        for document_text in document_texts
    ]

    # Cross-encoder scores
    scores = reranker_model.predict(pairs)

    reranked_results = []

    for result, score in zip(results, scores):

        reranked_results.append({
            "document": result["document"],
            "hybrid_score": result.get("hybrid_score", 0.0),
            "rerank_score": float(score)
        })

    # Highest reranker score first
    reranked_results.sort(
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    return reranked_results[:top_k]


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    from rag.hybrid_retriever import hybrid_search

    query = "Python decorators and functions"

    print()
    print("=" * 70)
    print("HYBRID RAG + RERANKER TEST")
    print("=" * 70)

    print(f"\nQuery: {query}")

    # --------------------------------------------------------
    # Hybrid Retrieval
    # --------------------------------------------------------

    print("\n[1] Running Hybrid Search...")

    results = hybrid_search(
        query=query,
        top_k=5,
        alpha=0.5
    )

    print(f"[2] Retrieved {len(results)} documents.")

    # --------------------------------------------------------
    # Reranking
    # --------------------------------------------------------

    print("\n[3] Running Cross-Encoder Reranker...")

    reranked = rerank(
        query=query,
        results=results,
        top_k=3
    )

    print("[4] Reranking completed.")

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("RERANKED RESULTS")
    print("=" * 70)

    for i, result in enumerate(reranked, start=1):

        document = result["document"]

        print(f"\nResult {i}")
        print("-" * 70)

        print(f"Concept      : {document['concept']}")
        print(f"Topic        : {document['topic']}")
        print(f"Difficulty   : {document['difficulty']}")
        print(f"Hybrid Score : {result['hybrid_score']:.4f}")
        print(f"Rerank Score : {result['rerank_score']:.4f}")