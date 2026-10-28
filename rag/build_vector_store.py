import json
import pickle
from pathlib import Path

import faiss
import numpy as np

from create_embeddings import create_embedding


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Knowledge file
KNOWLEDGE_FILE = BASE_DIR / "data" / "interview_knowledge.json"

# Vector database directory
VECTOR_DIR = BASE_DIR / "data" / "vector_store"

VECTOR_DIR.mkdir(parents=True, exist_ok=True)


def load_knowledge():
    """Load interview knowledge from JSON."""

    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def create_knowledge_text(item):
    """Convert one knowledge record into searchable text."""

    focus = ", ".join(item["interview_focus"])

    return f"""
Topic: {item["topic"]}

Difficulty: {item["difficulty"]}

Concept: {item["concept"]}

Knowledge:
{item["knowledge"]}

Interview Focus:
{focus}
""".strip()


def build_vector_store():

    print("Loading knowledge...")
    knowledge = load_knowledge()

    print(f"Found {len(knowledge)} knowledge records.")

    embeddings = []
    documents = []

    print("\nCreating Gemini embeddings...")
    print("-" * 50)

    for i, item in enumerate(knowledge):

        text = create_knowledge_text(item)

        print(
            f"Embedding {i + 1}/{len(knowledge)}: "
            f"{item['concept']}"
        )

        embedding = create_embedding(text)

        embeddings.append(embedding)
        documents.append(item)

    # Convert embeddings to NumPy array
    embeddings = np.array(
        embeddings,
        dtype="float32"
    )

    print("\nEmbedding matrix shape:")
    print(embeddings.shape)

    # Get vector dimension
    dimension = embeddings.shape[1]

    # Create FAISS index
    index = faiss.IndexFlatL2(dimension)

    # Add vectors
    index.add(embeddings)

    print(f"\nFAISS index created.")
    print(f"Vector dimension: {dimension}")
    print(f"Vectors stored: {index.ntotal}")

    # Save FAISS index
    index_path = VECTOR_DIR / "interview_knowledge.index"

    faiss.write_index(
        index,
        str(index_path)
    )

    # Save original documents
    documents_path = VECTOR_DIR / "documents.pkl"

    with open(documents_path, "wb") as file:
        pickle.dump(documents, file)

    print("\nVector store saved successfully!")

    print(f"FAISS index: {index_path}")
    print(f"Documents:   {documents_path}")


if __name__ == "__main__":
    build_vector_store()