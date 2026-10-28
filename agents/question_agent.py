from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.groq_agent import ask_groq
from rag.retrieve import retrieve
from rag.bm25_retriever import search_bm25
from rag.reranker import rerank


def generate_question(
    topic: str,
    selected_concepts: list,
    difficulty: str,
    question_type: str,
    profile_analysis: str = "",
    asked_concepts: list = None
):
    """
    Generate an interview question using:

    1. Candidate-selected topic
    2. Candidate-selected concepts
    3. Candidate-selected question type
    4. Current adaptive difficulty
    5. Candidate profile analysis
    6. Hybrid RAG
    7. Cross-encoder reranking
    """

    if not selected_concepts:
        raise ValueError(
            "At least one concept must be selected."
        )

    if asked_concepts is None:
        asked_concepts = []

    # ========================================================
    # SELECT CONCEPT
    # ========================================================

    # Prefer concepts that have not been asked yet.
    available_concepts = [
        concept
        for concept in selected_concepts
        if concept not in asked_concepts
    ]

    # If every selected concept has been used,
    # allow reuse as a fallback.
    if available_concepts:
        concept = available_concepts[0]
    else:
        concept = selected_concepts[
            len(asked_concepts) % len(selected_concepts)
        ]

    # ========================================================
    # RAG QUERY
    # ========================================================

    rag_query = f"""
Topic: {topic}

Concept: {concept}

Difficulty: {difficulty}

Question Type: {question_type}
""".strip()

    print("\n[QUESTION AGENT] Searching knowledge...")

    # --------------------------------------------------------
    # FAISS semantic search
    # --------------------------------------------------------

    faiss_results = retrieve(
        rag_query,
        top_k=3
    )

    print(
        f"[QUESTION AGENT] FAISS results: "
        f"{len(faiss_results)}"
    )

    # --------------------------------------------------------
    # BM25 keyword search
    # --------------------------------------------------------

    bm25_results = search_bm25(
        rag_query,
        top_k=3
    )

    print(
        f"[QUESTION AGENT] BM25 results: "
        f"{len(bm25_results)}"
    )

    # ========================================================
    # COMBINE RESULTS
    # ========================================================

    combined_results = []

    seen = set()

    for result in faiss_results + bm25_results:

        document = result["document"]

        key = (
            document["topic"],
            document["concept"],
            document["difficulty"]
        )

        if key in seen:
            continue

        seen.add(key)

        combined_results.append(result)

    print(
        f"[QUESTION AGENT] Combined results: "
        f"{len(combined_results)}"
    )

    # ========================================================
    # RERANK
    # ========================================================

    reranked_results = rerank(
        query=rag_query,
        results=combined_results,
        top_k=3
    )

    print(
        f"[QUESTION AGENT] Reranked results: "
        f"{len(reranked_results)}"
    )

    # ========================================================
    # BUILD KNOWLEDGE CONTEXT
    # ========================================================

    knowledge_context = ""

    for index, result in enumerate(
        reranked_results,
        start=1
    ):

        document = result["document"]

        knowledge_context += f"""

Knowledge Result {index}

Topic:
{document["topic"]}

Difficulty:
{document["difficulty"]}

Concept:
{document["concept"]}

Knowledge:
{document["knowledge"]}

Interview Focus:
{", ".join(document["interview_focus"])}

----------------------------------------
"""

    # ========================================================
    # PROFILE CONTEXT
    # ========================================================

    if profile_analysis:

        profile_context = f"""
Candidate Profile Analysis:

{profile_analysis}
"""

    else:

        profile_context = """
No candidate profile analysis is available.
"""

    # ========================================================
    # PREVIOUS CONCEPTS
    # ========================================================

    if asked_concepts:

        asked_concepts_text = ", ".join(
            asked_concepts
        )

    else:

        asked_concepts_text = "None"

    # ========================================================
    # FINAL LLM PROMPT
    # ========================================================

    prompt = f"""
You are an expert technical interviewer.

Generate ONE interview question.

================ INTERVIEW CONSTRAINTS ================

Topic:
{topic}

Selected Concept:
{concept}

Question Type:
{question_type}

Current Difficulty:
{difficulty}

Previously Asked Concepts:
{asked_concepts_text}

================ CANDIDATE PROFILE ================

{profile_context}

================ RAG KNOWLEDGE ================

{knowledge_context}

=======================================================

IMPORTANT RULES:

1. The question MUST be about the selected concept:
   {concept}

2. The question MUST belong to the topic:
   {topic}

3. The question MUST be a:
   {question_type}
   question.

4. The question MUST match:
   {difficulty}
   difficulty.

5. Do NOT change the selected topic.

6. Do NOT change the selected concept.

7. Do NOT change the selected question type.

8. Do NOT ask about a different concept.

9. Use the candidate profile only to personalize
   the context or scenario of the question.

10. Use the RAG knowledge to ground the question.

11. Do not provide the answer.

12. Do not provide explanations.

13. Return ONLY the interview question.

14. Make the question different from questions
    that may have already been asked.

=======================================================

Generate the question now.
"""

    print(
        "\n[QUESTION AGENT] Generating personalized question..."
    )

    question = ask_groq(prompt)

    if not question:

        raise RuntimeError(
            "Question Agent failed to generate a question."
        )

    return {
        "question": question.strip(),
        "concept": concept,
        "question_type": question_type,
        "difficulty": difficulty
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    result = generate_question(
        topic="Python",
        selected_concepts=[
            "Decorators",
            "Functions"
        ],
        difficulty="Medium",
        question_type="Conceptual",
        profile_analysis="""
Candidate Profile:
Python developer fresher with backend interests.

Technical Skills:
- Python
- FastAPI
- SQL

Primary Areas:
- Python Programming
- Backend Development

Project Experience:
- AI Interview System
- FastAPI project

Target Role:
Python Developer

Interview Focus Areas:
- Python fundamentals
- Decorators
- Backend development

Potential Weak Areas:
- Advanced Python concepts
""",
        asked_concepts=[]
    )

    print("\n")
    print("=" * 70)
    print("GENERATED QUESTION")
    print("=" * 70)

    print(result["question"])
    print(f"\nConcept: {result['concept']}")
    print(f"Type: {result['question_type']}")
    print(f"Difficulty: {result['difficulty']}")