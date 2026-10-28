# =========================================================
# AI INTERVIEW SYSTEM
# workflows/interview_workflow.py
# =========================================================

from pathlib import Path
import sys
import re
from typing import TypedDict, List


# =========================================================
# PROJECT PATH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


# =========================================================
# LANGGRAPH
# =========================================================

from langgraph.graph import StateGraph, END


# =========================================================
# WORKFLOW CONFIGURATION
# =========================================================

from workflows.interview_config import get_interview_configuration


# =========================================================
# AGENTS
# =========================================================

from agents.profile_agent import analyze_profile
from agents.question_agent import generate_question
from agents.evaluation_agent import evaluate_answer
from agents.adaptive_agent import get_adaptive_difficulty
from agents.weak_area_agent import analyze_weak_areas
from agents.feedback_agent import generate_feedback_report


# =========================================================
# DATABASE
# =========================================================

from database.crud import (
    create_user,
    update_user_profile,
    create_interview_session,
    save_question,
    save_answer,
    save_evaluation,
    update_interview_session,
    save_weak_area,
)


# =========================================================
# INTERVIEW STATE
# =========================================================

class InterviewState(TypedDict):

    # -----------------------------------------------------
    # Candidate Profile
    # -----------------------------------------------------

    profile: dict
    profile_analysis: str

    # -----------------------------------------------------
    # Interview Configuration
    # -----------------------------------------------------

    topic: str
    selected_concepts: list
    question_type: str

    # -----------------------------------------------------
    # Difficulty
    # -----------------------------------------------------

    difficulty: str
    starting_difficulty: str
    next_difficulty: str

    # -----------------------------------------------------
    # Question Control
    # -----------------------------------------------------

    question_count: int
    max_questions: int

    # -----------------------------------------------------
    # Current Question
    # -----------------------------------------------------

    current_question: str
    current_question_id: int | None
    current_question_difficulty: str
    current_concept: str
    current_question_type: str

    # -----------------------------------------------------
    # Current Answer / Evaluation
    # -----------------------------------------------------

    current_answer: str
    current_evaluation: str
    current_score: int

    # -----------------------------------------------------
    # Interview History
    # -----------------------------------------------------

    asked_concepts: list
    history: list

    # -----------------------------------------------------
    # Analysis
    # -----------------------------------------------------

    weak_areas: list
    feedback_report: str

    # -----------------------------------------------------
    # Database IDs
    # -----------------------------------------------------

    user_id: int | None
    session_id: int | None


# =========================================================
# NODE 1 — PROFILE AGENT
# =========================================================

def profile_agent_node(state: InterviewState):

    print("\n")
    print("=" * 70)
    print("PROFILE AGENT")
    print("=" * 70)

    profile = state["profile"]

    profile_analysis = analyze_profile(
        name=profile["name"],
        education=profile["education"],
        skills=profile["skills"],
        projects=profile["projects"],
        experience=profile["experience"],
        target_role=profile["target_role"]
    )

    if not profile_analysis:
        raise RuntimeError(
            "Profile Agent failed to generate profile analysis."
        )

    print("\n")
    print("=" * 70)
    print("PROFILE ANALYSIS")
    print("=" * 70)
    print(profile_analysis)

    return {
        "profile_analysis": profile_analysis
    }


# =========================================================
# NODE 2 — CREATE INTERVIEW SESSION
# =========================================================

def create_session_node(state: InterviewState):

    print("\n")
    print("=" * 70)
    print("CREATING INTERVIEW SESSION")
    print("=" * 70)

    profile = state["profile"]

    # -----------------------------------------------------
    # Create / Get User
    # -----------------------------------------------------

    user_id = create_user(
        name=profile["name"],
        email=profile["email"]
    )

    # -----------------------------------------------------
    # Update Candidate Profile
    # -----------------------------------------------------

    update_user_profile(
        user_id=user_id,
        education=profile["education"],
        skills=profile["skills"],
        projects=profile["projects"],
        experience=profile["experience"],
        target_role=profile["target_role"]
    )

    # -----------------------------------------------------
    # Create Interview Session
    # -----------------------------------------------------

    session_id = create_interview_session(
        user_id=user_id,
        topic=state["topic"],
        starting_difficulty=state["starting_difficulty"]
    )

    print(
        f"[SESSION] User ID: {user_id}"
    )

    print(
        "[SESSION] Candidate profile saved."
    )

    print(
        f"[SESSION] Session ID: {session_id}"
    )

    print("=" * 70)

    return {
        "user_id": user_id,
        "session_id": session_id,

        "question_count": 0,

        "asked_concepts": [],
        "history": [],
        "weak_areas": [],

        "feedback_report": ""
    }


# =========================================================
# NODE 3 — QUESTION AGENT
# =========================================================

def question_agent_node(state: InterviewState):

    print("\n")
    print("=" * 70)
    print("QUESTION AGENT")
    print("=" * 70)

    # -----------------------------------------------------
    # Existing Asked Concepts
    # -----------------------------------------------------

    asked_concepts = state.get(
        "asked_concepts",
        []
    ).copy()

    # -----------------------------------------------------
    # Current Difficulty
    # -----------------------------------------------------

    difficulty = state["difficulty"]

    # -----------------------------------------------------
    # Generate Question
    # -----------------------------------------------------

    result = generate_question(
        topic=state["topic"],
        selected_concepts=state["selected_concepts"],
        difficulty=difficulty,
        question_type=state["question_type"],
        profile_analysis=state["profile_analysis"],
        asked_concepts=asked_concepts
    )

    question = result["question"]
    concept = result["concept"]
    question_type = result["question_type"]

    # IMPORTANT:
    # This is the difficulty of the question actually generated.
    question_difficulty = result["difficulty"]

    # -----------------------------------------------------
    # Update Asked Concepts
    # -----------------------------------------------------

    if concept not in asked_concepts:
        asked_concepts.append(concept)

    # -----------------------------------------------------
    # Question Number
    # -----------------------------------------------------

    question_number = state["question_count"] + 1

    # -----------------------------------------------------
    # Display
    # -----------------------------------------------------

    print(
        f"\nQuestion Number : {question_number}"
    )

    print(
        f"Concept         : {concept}"
    )

    print(
        f"Type            : {question_type}"
    )

    print(
        f"Difficulty      : {question_difficulty}"
    )

    print("\nQuestion:")
    print(question)

    # -----------------------------------------------------
    # Save Question
    # -----------------------------------------------------

    question_id = save_question(
        session_id=state["session_id"],
        question_number=question_number,
        concept=concept,
        difficulty=question_difficulty,
        question=question,
        question_type=question_type
    )

    print(
        f"\n[QUESTION AGENT] "
        f"Question saved. ID: {question_id}"
    )

    # -----------------------------------------------------
    # Update State
    # -----------------------------------------------------

    return {
        "current_question": question,

        "current_question_id": question_id,

        "current_concept": concept,

        "current_question_type": question_type,

        # IMPORTANT FIX
        "current_question_difficulty": question_difficulty,

        "current_score": 0,

        "current_evaluation": "",

        "current_answer": "",

        "question_count": question_number,

        "asked_concepts": asked_concepts
    }


# =========================================================
# NODE 4 — CANDIDATE ANSWER
# =========================================================

def candidate_answer_node(state: InterviewState):

    print("\n")
    print("=" * 70)
    print("CANDIDATE ANSWER")
    print("=" * 70)

    # -----------------------------------------------------
    # Current Question
    # -----------------------------------------------------

    question = state["current_question"]

    print("\nQuestion:")
    print(question)

    print("\n" + "-" * 70)

    # -----------------------------------------------------
    # Coding Question
    # -----------------------------------------------------

    if state["current_question_type"].lower() == "coding":

        print("Enter your code below.")
        print("Type END on a new line when finished.")
        print()

        answer_lines = []

        while True:

            line = input()

            if line.strip().upper() == "END":
                break

            answer_lines.append(line)

        answer = "\n".join(
            answer_lines
        ).strip()

    # -----------------------------------------------------
    # Conceptual Question
    # -----------------------------------------------------

    else:

        print("Enter your answer:")

        answer = input("\n> ").strip()

    # -----------------------------------------------------
    # Validate Answer
    # -----------------------------------------------------

    if not answer:

        raise ValueError(
            "Candidate answer cannot be empty."
        )

    # -----------------------------------------------------
    # Save Answer
    # -----------------------------------------------------

    answer_id = save_answer(
        question_id=state["current_question_id"],
        answer=answer
    )

    print(
        f"\n[CANDIDATE ANSWER] "
        f"Answer saved. ID: {answer_id}"
    )

    return {
        "current_answer": answer
    }


# =========================================================
# NODE 5 — EVALUATION AGENT
# =========================================================

def evaluation_agent_node(state: InterviewState):

    print("\n")
    print("=" * 70)
    print("EVALUATION AGENT")
    print("=" * 70)

    # -----------------------------------------------------
    # Current Question
    # -----------------------------------------------------

    question = state["current_question"]

    # -----------------------------------------------------
    # Current Answer
    # -----------------------------------------------------

    answer = state["current_answer"]

    # -----------------------------------------------------
    # Difficulty OF CURRENT QUESTION
    # -----------------------------------------------------

    difficulty = state[
        "current_question_difficulty"
    ]

    # -----------------------------------------------------
    # Evaluate
    # -----------------------------------------------------

    evaluation = evaluate_answer(
        question=question,
        answer=answer,
        topic=state["topic"],
        difficulty=difficulty
    )

    # -----------------------------------------------------
    # API Failure
    # -----------------------------------------------------

    if not evaluation:

        raise RuntimeError(
            "Evaluation Agent returned an empty evaluation. "
            "This may be an API failure."
        )

    print("\n")
    print("=" * 70)
    print("EVALUATION RESULT")
    print("=" * 70)

    print(evaluation)

    # =====================================================
    # EXTRACT SCORE
    # =====================================================

    score_match = re.search(
        r"Score:\s*(\d+(?:\.\d+)?)\s*/\s*10",
        evaluation,
        re.IGNORECASE
    )

    if not score_match:

        raise ValueError(
            "Could not extract score from evaluation."
        )

    score = float(
        score_match.group(1)
    )

    # -----------------------------------------------------
    # Convert Score
    # -----------------------------------------------------

    if score.is_integer():

        score = int(score)

    else:

        score = round(score)

    # -----------------------------------------------------
    # Keep Score Between 0 and 10
    # -----------------------------------------------------

    score = max(
        0,
        min(10, int(score))
    )

    # =====================================================
    # EXTRACT EVALUATION SECTIONS
    # =====================================================

    def extract_section(
        text: str,
        section_name: str,
        next_sections: List[str]
    ):

        # -------------------------------------------------
        # Build Lookahead
        # -------------------------------------------------

        if next_sections:

            next_section_pattern = "|".join(
                map(
                    re.escape,
                    next_sections
                )
            )

            pattern = (
                rf"{re.escape(section_name)}:\s*(.*?)"
                rf"(?=\n(?:{next_section_pattern}):|\Z)"
            )

        else:

            pattern = (
                rf"{re.escape(section_name)}:\s*(.*?)\Z"
            )

        # -------------------------------------------------
        # Search
        # -------------------------------------------------

        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.DOTALL
        )

        if match:

            return match.group(1).strip()

        return ""

    # -----------------------------------------------------
    # Correctness
    # -----------------------------------------------------

    correctness = extract_section(
        evaluation,
        "Correctness",
        [
            "Relevance",
            "Technical Depth",
            "Clarity",
            "Missing Concepts",
            "Overall Feedback"
        ]
    )

    # -----------------------------------------------------
    # Relevance
    # -----------------------------------------------------

    relevance = extract_section(
        evaluation,
        "Relevance",
        [
            "Technical Depth",
            "Clarity",
            "Missing Concepts",
            "Overall Feedback"
        ]
    )

    # -----------------------------------------------------
    # Technical Depth
    # -----------------------------------------------------

    technical_depth = extract_section(
        evaluation,
        "Technical Depth",
        [
            "Clarity",
            "Missing Concepts",
            "Overall Feedback"
        ]
    )

    # -----------------------------------------------------
    # Clarity
    # -----------------------------------------------------

    clarity = extract_section(
        evaluation,
        "Clarity",
        [
            "Missing Concepts",
            "Overall Feedback"
        ]
    )

    # -----------------------------------------------------
    # Missing Concepts
    # -----------------------------------------------------

    missing_concepts = extract_section(
        evaluation,
        "Missing Concepts",
        [
            "Overall Feedback"
        ]
    )

    # -----------------------------------------------------
    # Overall Feedback
    # -----------------------------------------------------

    overall_feedback = extract_section(
        evaluation,
        "Overall Feedback",
        []
    )

    # =====================================================
    # SAVE EVALUATION
    # =====================================================

    evaluation_id = save_evaluation(
        question_id=state["current_question_id"],

        score=score,

        correctness=correctness,

        relevance=relevance,

        technical_depth=technical_depth,

        clarity=clarity,

        missing_concepts=missing_concepts,

        overall_feedback=overall_feedback
    )

    print(
        f"\nEvaluation saved with ID: "
        f"{evaluation_id}"
    )

    print(
        f"Score: {score}/10"
    )

    # -----------------------------------------------------
    # Update State
    # -----------------------------------------------------

    return {
        "current_evaluation": evaluation,

        "current_score": score
    }


# =========================================================
# NODE 6 — ADAPTIVE DIFFICULTY AGENT
# =========================================================

def adaptive_agent_node(state: InterviewState):

    print("\n")
    print("=" * 70)
    print("ADAPTIVE DIFFICULTY AGENT")
    print("=" * 70)

    # -----------------------------------------------------
    # Score
    # -----------------------------------------------------

    score = state["current_score"]

    # -----------------------------------------------------
    # Difficulty of Question Just Answered
    # -----------------------------------------------------

    current_difficulty = (
        state["current_question_difficulty"]
    )

    print(
        f"Current Difficulty : "
        f"{current_difficulty}"
    )

    print(
        f"Candidate Score    : "
        f"{score}/10"
    )

    # -----------------------------------------------------
    # Calculate Next Difficulty
    # -----------------------------------------------------

    next_difficulty = get_adaptive_difficulty(
        current_difficulty=current_difficulty,
        score=score
    )

    print(
        f"Next Difficulty    : "
        f"{next_difficulty}"
    )

    # -----------------------------------------------------
    # Update State
    # -----------------------------------------------------

    return {
        "difficulty": next_difficulty,

        "next_difficulty": next_difficulty
    }


# =========================================================
# NODE 7 — SAVE HISTORY
# =========================================================

def save_history_node(state: InterviewState):

    print("\n")
    print("=" * 70)
    print("SAVING INTERVIEW HISTORY")
    print("=" * 70)

    # -----------------------------------------------------
    # Copy Existing History
    # -----------------------------------------------------

    history = state.get(
        "history",
        []
    ).copy()

    # -----------------------------------------------------
    # Add Current Question History
    # -----------------------------------------------------

    history.append({

        "question_number":
            state["question_count"],

        "concept":
            state["current_concept"],

        "question_type":
            state["current_question_type"],

        # IMPORTANT:
        # Actual difficulty of the question asked
        "difficulty":
            state["current_question_difficulty"],

        "question":
            state["current_question"],

        "answer":
            state["current_answer"],

        "score":
            state["current_score"],

        "evaluation":
            state["current_evaluation"]
    })

    print(
        f"[HISTORY] "
        f"Question {state['question_count']} saved."
    )

    print(
        f"[HISTORY] "
        f"Score: {state['current_score']}/10"
    )

    return {
        "history": history
    }


# =========================================================
# NODE 8 — WEAK AREA AGENT
# =========================================================

def weak_area_agent_node(state: InterviewState):

    print("\n")
    print("=" * 70)
    print("WEAK AREA AGENT")
    print("=" * 70)

    history = state["history"]

    weak_areas = analyze_weak_areas(
        history
    )

    if weak_areas:

        print("\nWeak Areas:")

        for area in weak_areas:

            print(
                f"- {area['concept']} | "
                f"Average Score: "
                f"{area['average_score']}/10 | "
                f"Severity: "
                f"{area['severity']}"
            )

    else:

        print(
            "\nNo significant weak areas detected."
        )

    # -----------------------------------------------------
    # Save Weak Areas to PostgreSQL
    # -----------------------------------------------------

    for area in weak_areas:

        save_weak_area(
            session_id=state["session_id"],

            concept=area["concept"],

            average_score=area["average_score"],

            severity=area["severity"]
        )

    return {
        "weak_areas": weak_areas
    }


# =========================================================
# NODE 9 — FEEDBACK AGENT
# =========================================================

def feedback_agent_node(state: InterviewState):

    print("\n")
    print("=" * 70)
    print("FEEDBACK AGENT")
    print("=" * 70)

    report = generate_feedback_report(

        topic=state["topic"],

        starting_difficulty=
            state["starting_difficulty"],

        final_difficulty=
            state["difficulty"],

        history=
            state["history"],

        weak_areas=
            state["weak_areas"]
    )

    if not report:

        raise RuntimeError(
            "Feedback Agent failed to generate "
            "the final report."
        )

    print("\n")
    print("=" * 70)
    print("FINAL INTERVIEW REPORT")
    print("=" * 70)

    print(report)

    return {
        "feedback_report": report
    }


# =========================================================
# NODE 10 — FINALIZE SESSION
# =========================================================

def finalize_session_node(state: InterviewState):

    print("\n")
    print("=" * 70)
    print("FINALIZING INTERVIEW SESSION")
    print("=" * 70)

    history = state["history"]

    total_questions = len(history)

    total_score = sum(
        item["score"]
        for item in history
    )

    if total_questions > 0:

        average_score = (
            total_score /
            total_questions
        )

    else:

        average_score = 0.0

    final_difficulty = state["difficulty"]

    # -----------------------------------------------------
    # Update PostgreSQL Session
    # -----------------------------------------------------

    update_interview_session(

        session_id=state["session_id"],

        final_difficulty=final_difficulty,

        total_questions=total_questions,

        total_score=total_score,

        average_score=average_score
    )

    # -----------------------------------------------------
    # Display Final Statistics
    # -----------------------------------------------------

    print(
        f"Session ID       : "
        f"{state['session_id']}"
    )

    print(
        f"Total Questions  : "
        f"{total_questions}"
    )

    print(
        f"Total Score      : "
        f"{total_score}"
    )

    print(
        f"Average Score    : "
        f"{average_score:.2f}/10"
    )

    print(
        f"Final Difficulty : "
        f"{final_difficulty}"
    )

    print(
        "\n[SESSION] "
        "Interview completed successfully."
    )

    print("=" * 70)

    return {}


# =========================================================
# ROUTING FUNCTION
# =========================================================

def should_continue(state: InterviewState):

    if state["question_count"] < state["max_questions"]:

        return "continue"

    return "end"


# =========================================================
# BUILD LANGGRAPH WORKFLOW
# =========================================================

def build_interview_graph():

    workflow = StateGraph(
        InterviewState
    )

    # -----------------------------------------------------
    # Add Nodes
    # -----------------------------------------------------

    workflow.add_node(
        "profile_agent",
        profile_agent_node
    )

    workflow.add_node(
        "create_session",
        create_session_node
    )

    workflow.add_node(
        "question_agent",
        question_agent_node
    )

    workflow.add_node(
        "candidate_answer",
        candidate_answer_node
    )

    workflow.add_node(
        "evaluation_agent",
        evaluation_agent_node
    )

    workflow.add_node(
        "adaptive_agent",
        adaptive_agent_node
    )

    workflow.add_node(
        "save_history",
        save_history_node
    )

    workflow.add_node(
        "weak_area_agent",
        weak_area_agent_node
    )

    workflow.add_node(
        "feedback_agent",
        feedback_agent_node
    )

    workflow.add_node(
        "finalize_session",
        finalize_session_node
    )

    # =====================================================
    # GRAPH EDGES
    # =====================================================

    # -----------------------------------------------------
    # Profile → Session
    # -----------------------------------------------------

    workflow.add_edge(
        "profile_agent",
        "create_session"
    )

    # -----------------------------------------------------
    # Session → Question
    # -----------------------------------------------------

    workflow.add_edge(
        "create_session",
        "question_agent"
    )

    # -----------------------------------------------------
    # Question → Candidate Answer
    # -----------------------------------------------------

    workflow.add_edge(
        "question_agent",
        "candidate_answer"
    )

    # -----------------------------------------------------
    # Candidate Answer → Evaluation
    # -----------------------------------------------------

    workflow.add_edge(
        "candidate_answer",
        "evaluation_agent"
    )

    # -----------------------------------------------------
    # Evaluation → Adaptive Difficulty
    # -----------------------------------------------------

    workflow.add_edge(
        "evaluation_agent",
        "adaptive_agent"
    )

    # -----------------------------------------------------
    # Adaptive → History
    # -----------------------------------------------------

    workflow.add_edge(
        "adaptive_agent",
        "save_history"
    )

    # -----------------------------------------------------
    # History → Continue OR End
    # -----------------------------------------------------

    workflow.add_conditional_edges(

        "save_history",

        should_continue,

        {
            "continue":
                "question_agent",

            "end":
                "weak_area_agent"
        }
    )

    # -----------------------------------------------------
    # Weak Areas → Feedback
    # -----------------------------------------------------

    workflow.add_edge(
        "weak_area_agent",
        "feedback_agent"
    )

    # -----------------------------------------------------
    # Feedback → Finalize
    # -----------------------------------------------------

    workflow.add_edge(
        "feedback_agent",
        "finalize_session"
    )

    # -----------------------------------------------------
    # Finalize → END
    # -----------------------------------------------------

    workflow.add_edge(
        "finalize_session",
        END
    )

    # -----------------------------------------------------
    # Entry Point
    # -----------------------------------------------------

    workflow.set_entry_point(
        "profile_agent"
    )

    # -----------------------------------------------------
    # Compile
    # -----------------------------------------------------

    return workflow.compile()


# =========================================================
# MAIN
# =========================================================

def main():

    print("\n")
    print("=" * 70)
    print("        AI MULTI-AGENT INTERVIEW SYSTEM")
    print("=" * 70)

    # -----------------------------------------------------
    # Get Interview Configuration
    # -----------------------------------------------------

    configuration = (
        get_interview_configuration()
    )

    # -----------------------------------------------------
    # Build Graph
    # -----------------------------------------------------

    graph = build_interview_graph()

    # -----------------------------------------------------
    # Initial State
    # -----------------------------------------------------

    initial_state: InterviewState = {

        # -------------------------------------------------
        # Profile
        # -------------------------------------------------

        "profile":
            configuration["profile"],

        "profile_analysis":
            "",

        # -------------------------------------------------
        # Interview Configuration
        # -------------------------------------------------

        "topic":
            configuration["topic"],

        "selected_concepts":
            configuration["selected_concepts"],

        "question_type":
            configuration["question_type"],

        # -------------------------------------------------
        # Difficulty
        # -------------------------------------------------

        "difficulty":
            configuration["starting_difficulty"],

        "starting_difficulty":
            configuration["starting_difficulty"],

        "next_difficulty":
            configuration["starting_difficulty"],

        # -------------------------------------------------
        # Question Control
        # -------------------------------------------------

        "question_count":
            0,

        "max_questions":
            configuration["max_questions"],

        # -------------------------------------------------
        # Current Question
        # -------------------------------------------------

        "current_question":
            "",

        "current_question_id":
            None,

        "current_question_difficulty":
            "",

        "current_concept":
            "",

        "current_question_type":
            "",

        # -------------------------------------------------
        # Current Answer / Evaluation
        # -------------------------------------------------

        "current_answer":
            "",

        "current_evaluation":
            "",

        "current_score":
            0,

        # -------------------------------------------------
        # History
        # -------------------------------------------------

        "asked_concepts":
            [],

        "history":
            [],

        # -------------------------------------------------
        # Analysis
        # -------------------------------------------------

        "weak_areas":
            [],

        "feedback_report":
            "",

        # -------------------------------------------------
        # Database
        # -------------------------------------------------

        "user_id":
            None,

        "session_id":
            None
    }

    # -----------------------------------------------------
    # Run Graph
    # -----------------------------------------------------

    final_state = graph.invoke(
        initial_state
    )

    # -----------------------------------------------------
    # Final Output
    # -----------------------------------------------------

    print("\n")
    print("=" * 70)
    print("INTERVIEW COMPLETED")
    print("=" * 70)

    if final_state.get(
        "feedback_report"
    ):

        print(
            final_state[
                "feedback_report"
            ]
        )

    print("\n")
    print("=" * 70)
    print("END OF INTERVIEW")
    print("=" * 70)


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()