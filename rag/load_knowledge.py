import json
from pathlib import Path


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# JSON knowledge base
KNOWLEDGE_FILE = BASE_DIR / "data" / "interview_knowledge.json"


def load_knowledge():
    """Load the interview knowledge base."""

    print(f"Loading knowledge from: {KNOWLEDGE_FILE}")

    if not KNOWLEDGE_FILE.exists():
        raise FileNotFoundError(
            f"Knowledge file not found:\n{KNOWLEDGE_FILE}"
        )

    try:
        with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
            knowledge = json.load(file)

    except json.JSONDecodeError as e:
        raise ValueError(
            f"Invalid JSON in {KNOWLEDGE_FILE}\n"
            f"Line: {e.lineno}, Column: {e.colno}\n"
            f"Error: {e.msg}"
        )

    return knowledge


def retrieve_knowledge(topic: str, difficulty: str):
    """Retrieve knowledge matching topic and difficulty."""

    knowledge = load_knowledge()

    results = []

    for item in knowledge:

        if (
            item["topic"].lower() == topic.lower()
            and item["difficulty"].lower() == difficulty.lower()
        ):
            results.append(item)

    return results


if __name__ == "__main__":

    topic = "Python"
    difficulty = "Medium"

    results = retrieve_knowledge(topic, difficulty)

    print()
    print("RAG Knowledge Retrieval")
    print("=" * 50)
    print(f"Topic      : {topic}")
    print(f"Difficulty : {difficulty}")
    print()

    if not results:
        print("No relevant knowledge found.")

    else:

        print(f"Found {len(results)} relevant concepts.")
        print()

        for item in results:

            print(f"Concept: {item['concept']}")
            print(f"Knowledge: {item['knowledge']}")

            print("Interview Focus:")

            for focus in item["interview_focus"]:
                print(f"  - {focus}")

            print("-" * 50)