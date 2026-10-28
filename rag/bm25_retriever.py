import json
import re
from pathlib import Path

from rank_bm25 import BM25Okapi


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

KNOWLEDGE_FILE = BASE_DIR / "data" / "interview_knowledge.json"


def load_knowledge():
    """Load knowledge records."""

    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def tokenize(text: str):
    """Convert text into tokens for BM25."""

    return re.findall(r"\b\w+\b", text.lower())


def create_document_text(item):
    """Convert a knowledge record into searchable text."""

    focus = " ".join(item["interview_focus"])

    return f"""
    {item["topic"]}
    {item["difficulty"]}
    {item["concept"]}
    {item["knowledge"]}
    {focus}
    """


def build_bm25():

    knowledge = load_knowledge()

    documents = [
        create_document_text(item)
        for item in knowledge
    ]

    tokenized_documents = [
        tokenize(document)
        for document in documents
    ]

    bm25 = BM25Okapi(tokenized_documents)

    return bm25, knowledge


def search_bm25(query: str, top_k: int = 3):

    bm25, knowledge = build_bm25()

    query_tokens = tokenize(query)

    scores = bm25.get_scores(query_tokens)

    # Sort indexes by score
    ranked_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )

    results = []

    for index in ranked_indices[:top_k]:

        results.append({
            "score": float(scores[index]),
            "document": knowledge[index]
        })

    return results


if __name__ == "__main__":

    query = "Python decorators functions"

    print("BM25 Keyword Search")
    print("=" * 60)

    print(f"Query: {query}")
    print()

    results = search_bm25(query, top_k=3)

    for i, result in enumerate(results, start=1):

        document = result["document"]

        print(f"Result {i}")
        print("-" * 60)

        print(f"BM25 Score: {result['score']:.4f}")
        print(f"Topic: {document['topic']}")
        print(f"Difficulty: {document['difficulty']}")
        print(f"Concept: {document['concept']}")
        print()