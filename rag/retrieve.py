import pickle
from pathlib import Path

import faiss
import numpy as np

from rag.create_embeddings import create_embedding


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Vector store
VECTOR_DIR = BASE_DIR / "data" / "vector_store"

INDEX_FILE = VECTOR_DIR / "interview_knowledge.index"
DOCUMENTS_FILE = VECTOR_DIR / "documents.pkl"


def load_vector_store():
    """Load FAISS index and documents."""

    if not INDEX_FILE.exists():
        raise FileNotFoundError(
            f"FAISS index not found:\n{INDEX_FILE}\n"
            "Run build_vector_store.py first."
        )

    if not DOCUMENTS_FILE.exists():
        raise FileNotFoundError(
            f"Documents file not found:\n{DOCUMENTS_FILE}"
        )

    index = faiss.read_index(str(INDEX_FILE))

    with open(DOCUMENTS_FILE, "rb") as file:
        documents = pickle.load(file)

    return index, documents


def retrieve(query: str, top_k: int = 3):
    """
    Search the FAISS vector database.

    Returns the most relevant knowledge records.
    """

    index, documents = load_vector_store()

    # Convert query into Gemini embedding
    query_embedding = create_embedding(query)

    # Convert to NumPy
    query_vector = np.array(
        [query_embedding],
        dtype="float32"
    )

    # Search FAISS
    distances, indices = index.search(
        query_vector,
        top_k
    )

    results = []

    for distance, index_id in zip(
        distances[0],
        indices[0]
    ):
        if index_id == -1:
            continue

        document = documents[index_id]

        results.append({
            "score": float(distance),
            "document": document
        })

    return results


if __name__ == "__main__":

    query = "Python decorators and higher order functions"

    print("FAISS Semantic Search")
    print("=" * 60)

    print(f"Query: {query}")
    print()

    results = retrieve(query, top_k=3)

    for i, result in enumerate(results, start=1):

        document = result["document"]

        print(f"Result {i}")
        print("-" * 60)

        print(f"Similarity distance: {result['score']:.4f}")
        print(f"Topic: {document['topic']}")
        print(f"Difficulty: {document['difficulty']}")
        print(f"Concept: {document['concept']}")
        print(f"Knowledge: {document['knowledge']}")

        print()