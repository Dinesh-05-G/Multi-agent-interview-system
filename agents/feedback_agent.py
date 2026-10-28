from pathlib import Path
import sys

# ---------------------------------------------------------
# Project Root
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


# ---------------------------------------------------------
# Gemini Agent
# ---------------------------------------------------------

from agents.gemini_agent import ask_gemini


# =========================================================
# FEEDBACK / REPORT AGENT
# =========================================================

def generate_feedback_report(
    topic: str,
    starting_difficulty: str,
    final_difficulty: str,
    history: list,
    weak_areas: list
):
    """
    Generate the final interview performance report.
    """

    if not history:
        return ""

    # -----------------------------------------------------
    # Build Interview History
    # -----------------------------------------------------

    history_text = ""

    for item in history:

        history_text += f"""
Question {item["question_number"]}

Concept:
{item["concept"]}

Question Type:
{item["question_type"]}

Difficulty:
{item["difficulty"]}

Question:
{item["question"]}

Candidate Answer:
{item["answer"]}

Score:
{item["score"]}/10

Evaluation:
{item["evaluation"]}

--------------------------------------------------
"""

    # -----------------------------------------------------
    # Build Weak Area Information
    # -----------------------------------------------------

    if weak_areas:

        weak_area_text = ""

        for area in weak_areas:

            weak_area_text += (
                f"- {area['concept']} | "
                f"Average Score: "
                f"{area['average_score']}/10 | "
                f"Severity: "
                f"{area['severity']}\n"
            )

    else:

        weak_area_text = "No significant weak areas detected."

    # -----------------------------------------------------
    # Gemini Prompt
    # -----------------------------------------------------

    prompt = f"""
You are an expert technical interview feedback analyst.

Generate a professional final interview performance report
based ONLY on the information provided below.

================ INTERVIEW INFORMATION ================

Topic:
{topic}

Starting Difficulty:
{starting_difficulty}

Final Difficulty:
{final_difficulty}

================ INTERVIEW HISTORY ================

{history_text}

================ WEAK AREAS ================

{weak_area_text}

========================================================

Generate the report using EXACTLY this structure:

Overall Performance:
<summary of the candidate's overall performance>

Strengths:
- <strength 1>
- <strength 2>
- <strength 3>

Weak Areas:
- <weak area 1>
- <weak area 2>

Technical Assessment:
<assessment of technical understanding>

Difficulty Progression:
<explain how the interview difficulty changed based on performance>

Improvement Recommendations:
1. <recommendation 1>
2. <recommendation 2>
3. <recommendation 3>

Final Feedback:
<short professional feedback for the candidate>

IMPORTANT:
- Use only the supplied interview information.
- Do not invent scores or facts.
- Do not ask another question.
- Do not include internal reasoning.
- Return only the final report.
"""

    # -----------------------------------------------------
    # Call Gemini
    # -----------------------------------------------------

    print("\n[FEEDBACK AGENT] Generating final report...")

    result = ask_gemini(prompt)

    if not result:

        print(
            "[FEEDBACK AGENT] "
            "Failed to generate report."
        )

        return ""

    print(
        "[FEEDBACK AGENT] "
        "Final report generated successfully."
    )

    return result.strip()


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    test_history = [
        {
            "question_number": 1,
            "concept": "Lists",
            "question_type": "Conceptual",
            "difficulty": "Easy",
            "question": "What is a Python list?",
            "answer": "A list is a mutable collection of elements.",
            "score": 8,
            "evaluation": (
                "Good understanding of Python lists."
            )
        },
        {
            "question_number": 2,
            "concept": "Tuples",
            "question_type": "Conceptual",
            "difficulty": "Medium",
            "question": "What is the difference between a list and tuple?",
            "answer": "Lists can be changed while tuples cannot.",
            "score": 5,
            "evaluation": (
                "Basic understanding but lacks technical depth."
            )
        }
    ]

    test_weak_areas = [
        {
            "concept": "Tuples",
            "average_score": 5.0,
            "severity": "MEDIUM"
        }
    ]

    report = generate_feedback_report(
        topic="Python",
        starting_difficulty="Easy",
        final_difficulty="Medium",
        history=test_history,
        weak_areas=test_weak_areas
    )

    print("\n")
    print("=" * 70)
    print("FINAL INTERVIEW REPORT")
    print("=" * 70)
    print(report)