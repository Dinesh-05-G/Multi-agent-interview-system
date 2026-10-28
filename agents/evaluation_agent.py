from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.gemini_agent import ask_gemini


def evaluate_answer(
    question: str,
    answer: str,
    topic: str,
    difficulty: str = "Medium"
):

    print("[1] Sending answer to Gemini evaluation agent...")

    prompt = f"""
You are an expert technical interviewer.

Evaluate the candidate's answer to the interview question.

Topic: {topic}
Difficulty: {difficulty}

================ QUESTION ================

{question}

================ CANDIDATE ANSWER ================

{answer}

====================================================

Evaluate the answer based on:

1. Correctness
2. Relevance
3. Technical depth
4. Clarity
5. Missing concepts

Give a score from 0 to 10.

Return EXACTLY this format:

Score: <number>/10
Correctness: <short explanation>
Relevance: <short explanation>
Technical Depth: <short explanation>
Clarity: <short explanation>
Missing Concepts: <short explanation>
Overall Feedback: <short explanation>

IMPORTANT:
- Return the complete evaluation.
- Do not return only internal reasoning.
- Do not leave the response empty.
- Do not ask another question.
- Do not provide unnecessary text.
"""

    result = ask_gemini(prompt)

    print("[2] Evaluation received.")

    if not result:
        print("[ERROR] Empty evaluation returned.")
        return ""

    print("[3] Gemini evaluation received successfully.")

    return result.strip()