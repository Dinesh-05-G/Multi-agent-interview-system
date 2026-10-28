from fastapi import APIRouter, HTTPException
from fastapi import Depends

import re
import traceback


from api.auth import get_current_user_id
from database.crud import verify_session_ownership

from api.schemas import (
    InterviewStartRequest,
    AnswerRequest
)

from agents.profile_agent import analyze_profile
from agents.question_agent import generate_question
from database.crud import (
    create_user,
    update_user_profile,
    create_interview_session,
    save_question,
    save_answer,
    save_evaluation,
    update_interview_state,
    update_interview_session,
    save_weak_area,
    get_interview_session,
    get_question,
    get_session_questions,
    get_answer_for_question,
    get_evaluation_for_question,
    get_user_profile,
    get_session_weak_areas,
    get_user_interview_sessions
)

from agents.evaluation_agent import evaluate_answer
from agents.adaptive_agent import get_adaptive_difficulty
from agents.weak_area_agent import analyze_weak_areas
from agents.feedback_agent import generate_feedback_report


router = APIRouter(
    prefix="/api/interview",
    tags=["Interview"]
)


# Temporary in-memory interview state
interview_states = {}

# =========================================================
# INTERVIEW TOPICS AND CONCEPTS
# =========================================================

from workflows.interview_config import get_topics, get_concepts


@router.get("/topics")
def list_interview_topics(
    current_user_id: int = Depends(get_current_user_id),
):
    try:
        return {"topics": get_topics()}
    except Exception:
        import logging
        logging.exception("Failed to load interview topics")
        raise HTTPException(
            status_code=500,
            detail="Failed to load interview topics.",
        )


@router.get("/history")
def get_interview_history(
    current_user_id: int = Depends(get_current_user_id),
):
    try:
        sessions = get_user_interview_sessions(current_user_id)

        completed_sessions = [
            session
            for session in sessions
            if session["status"] == "COMPLETED"
        ]

        scored_sessions = [
            session
            for session in completed_sessions
            if session["average_score"] is not None
        ]

        average_score = (
            round(
                sum(s["average_score"] for s in scored_sessions)
                / len(scored_sessions),
                2,
            )
            if scored_sessions
            else None
        )

        return {
            "sessions": sessions,
            "total_interviews": len(sessions),
            "completed_interviews": len(completed_sessions),
            "average_score": average_score,
        }

    except Exception:
        import logging
        logging.exception("Failed to retrieve interview history")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve interview history.",
        )

@router.get("/concepts")
def list_interview_concepts(
    topic: str,
    current_user_id: int = Depends(get_current_user_id),
):
    topic = topic.strip()

    if not topic:
        raise HTTPException(
            status_code=422,
            detail="Topic is required.",
        )

    try:
        topics = get_topics()

        matched_topic = next(
            (
                available_topic
                for available_topic in topics
                if available_topic.casefold() == topic.casefold()
            ),
            None,
        )

        if matched_topic is None:
            raise HTTPException(
                status_code=404,
                detail="Topic not found.",
            )

        return {
            "topic": matched_topic,
            "concepts": get_concepts(matched_topic),
        }

    except HTTPException:
        raise
    except Exception:
        import logging
        logging.exception("Failed to load interview concepts")
        raise HTTPException(
            status_code=500,
            detail="Failed to load interview concepts.",
        )


@router.post("/start")
def start_interview(
    request: InterviewStartRequest,
    current_user_id: int = Depends(get_current_user_id)
):

    try:

        
        # -------------------------------------------------
        # 1. Get Authenticated Candidate Profile
        # -------------------------------------------------

        authenticated_profile = get_user_profile(current_user_id)

        if authenticated_profile is None:
            raise HTTPException(
                status_code=401,
                detail="Authenticated user account not found."
            )

        profile = {
            "name": authenticated_profile["name"],
            "email": authenticated_profile["email"],
            "education": request.education,
            "skills": request.skills,
            "projects": request.projects,
            "experience": request.experience,
            "target_role": request.target_role
        }


        # -------------------------------------------------
        # 2. Profile Agent
        # -------------------------------------------------

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
                "Profile Agent failed."
            )

        
        # -------------------------------------------------
        # 3. Update Existing User Profile
        # -------------------------------------------------

        user_id = current_user_id

        update_user_profile(
            user_id=user_id,
            education=profile.get("education"),
            skills=profile.get("skills", []),
            projects=profile.get("projects", []),
            experience=profile.get("experience"),
            target_role=profile.get("target_role")
        )

        # -------------------------------------------------
        # 4. Create Interview Session
        # -------------------------------------------------

        session_id = create_interview_session(
            user_id=user_id,
            topic=request.topic,
            starting_difficulty=request.starting_difficulty,
            selected_concepts=request.selected_concepts,
            question_type=request.question_type,
            max_questions=request.max_questions
        )
        # -------------------------------------------------
        # 5. Generate First Question
        # -------------------------------------------------

        result = generate_question(
            topic=request.topic,
            selected_concepts=request.selected_concepts,
            difficulty=request.starting_difficulty,
            question_type=request.question_type,
            profile_analysis=profile_analysis,
            asked_concepts=[]
        )

        question = result["question"]
        concept = result["concept"]
        question_type = result["question_type"]
        difficulty = result["difficulty"]

        # -------------------------------------------------
        # 6. Save Question
        # -------------------------------------------------

        question_id = save_question(
            session_id=session_id,
            question_number=1,
            concept=concept,
            difficulty=difficulty,
            question=question,
            question_type=question_type
        )

        update_interview_state(
            session_id=session_id,
            current_difficulty=difficulty,
            current_question_id=question_id,
            question_count=1
        )

        # -------------------------------------------------
        # 7. Store Interview State
        # -------------------------------------------------

        interview_states[session_id] = {

            "profile": profile,

            "profile_analysis":
                profile_analysis,

            "user_id":
                user_id,

            "session_id":
                session_id,

            "topic":
                request.topic,

            "selected_concepts":
                request.selected_concepts,

            "question_type":
                request.question_type,

            "starting_difficulty":
                request.starting_difficulty,

            "difficulty":
                difficulty,

            "current_question":
                question,

            "current_question_id":
                question_id,

            "current_concept":
                concept,

            "current_question_type":
                question_type,

            "current_question_difficulty":
                difficulty,

            "question_count":
                1,

            "max_questions":
                request.max_questions,

            "asked_concepts":
                [concept],

            "history":
                [],

            "weak_areas":
                [],

            "feedback_report":
                ""
        }

        # -------------------------------------------------
        # 8. Return First Question
        # -------------------------------------------------

        return {
            "session_id": session_id,
            "question_id": question_id,
            "question_number": 1,
            "question": question,
            "concept": concept,
            "question_type": question_type,
            "difficulty": difficulty
        }

    
    except HTTPException:
        raise

    except Exception:
        import logging
        logging.exception("Failed to start interview")
        raise HTTPException(
            status_code=500,
            detail="Failed to start interview. Check the server logs."
        )


# =========================================================
# SUBMIT ANSWER
# =========================================================


@router.post("/{session_id}/answer")
def submit_answer(
    session_id: int,
    request: AnswerRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    if not verify_session_ownership(session_id, current_user_id):
        raise HTTPException(
            status_code=404,
            detail="Interview session not found.",
        )
    

    # =====================================================
    # 1. CHECK SESSION IN DATABASE BEFORE CALLING ANY AGENT
    # =====================================================

    session = get_interview_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found."
        )

    if session["status"] == "COMPLETED":
        raise HTTPException(
            status_code=409,
            detail="Interview session is already completed."
        )

    # =====================================================
    # 2. VALIDATE ANSWER
    # =====================================================

    answer = (request.answer or "").strip()

    if not answer:
        raise HTTPException(
            status_code=422,
            detail="Answer cannot be empty."
        )

    # =====================================================
    # 3. RESTORE INTERVIEW STATE
    # =====================================================

    state = get_or_restore_interview_state(session_id)

    if state is None:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found."
        )

    try:
        # =================================================
        # 4. SAVE ANSWER
        # =================================================

        answer_id = save_answer(
            question_id=state["current_question_id"],
            answer=answer
        )

        # =================================================
        # 5. EVALUATE ANSWER
        # =================================================

        evaluation = evaluate_answer(
            question=state["current_question"],
            answer=answer,
            topic=state["topic"],
            difficulty=state["current_question_difficulty"]
        )

        if not evaluation:
            raise RuntimeError(
                "Evaluation Agent failed to return an evaluation."
            )

        # =================================================
        # 6. EXTRACT SCORE
        # =================================================

        score_match = re.search(
            r"Score:\s*(\d+(?:\.\d+)?)\s*/\s*10",
            evaluation,
            re.IGNORECASE
        )

        if not score_match:
            raise ValueError(
                "Could not extract score from evaluation."
            )

        score = round(float(score_match.group(1)))
        score = max(0, min(10, score))

        # =================================================
        # 7. EXTRACT EVALUATION FIELDS
        # =================================================

        def extract_evaluation_field(text, field_name):
            pattern = (
                rf"{re.escape(field_name)}"
                rf"\s*:\s*"
                rf"(.*?)"
                rf"(?=\n[A-Za-z][A-Za-z_ ]*\s*:|$)"
            )

            match = re.search(
                pattern,
                text,
                re.IGNORECASE | re.DOTALL
            )

            return match.group(1).strip() if match else ""

        correctness = extract_evaluation_field(
            evaluation, "Correctness"
        )
        relevance = extract_evaluation_field(
            evaluation, "Relevance"
        )
        technical_depth = extract_evaluation_field(
            evaluation, "Technical Depth"
        )
        clarity = extract_evaluation_field(
            evaluation, "Clarity"
        )
        missing_concepts = extract_evaluation_field(
            evaluation, "Missing Concepts"
        )
        overall_feedback = extract_evaluation_field(
            evaluation, "Overall Feedback"
        )

        # =================================================
        # 8. SAVE EVALUATION
        # =================================================

        save_evaluation(
            question_id=state["current_question_id"],
            score=score,
            correctness=correctness,
            relevance=relevance,
            technical_depth=technical_depth,
            clarity=clarity,
            missing_concepts=missing_concepts,
            overall_feedback=overall_feedback
        )

        # =================================================
        # 9. CALCULATE ADAPTIVE DIFFICULTY
        # =================================================

        current_difficulty = state["current_question_difficulty"]

        next_difficulty = get_adaptive_difficulty(
            current_difficulty=current_difficulty,
            score=score
        )

        # =================================================
        # 10. APPEND INTERVIEW HISTORY
        # =================================================

        state["history"].append({
            "question_number": state["question_count"],
            "concept": state["current_concept"],
            "question_type": state["current_question_type"],
            "difficulty": current_difficulty,
            "question": state["current_question"],
            "answer": answer,
            "score": score,
            "evaluation": evaluation
        })

        # =================================================
        # 11. CHECK COMPLETION
        # =================================================

        interview_finished = (
            state["question_count"] >= state["max_questions"]
        )

        if interview_finished:
            return finish_interview(
                session_id,
                state
            )

        # =================================================
        # 12. GENERATE NEXT QUESTION
        # =================================================

        result = generate_question(
            topic=state["topic"],
            selected_concepts=state["selected_concepts"],
            difficulty=next_difficulty,
            question_type=state["question_type"],
            profile_analysis=state["profile_analysis"],
            asked_concepts=state["asked_concepts"]
        )

        question = result["question"]
        concept = result["concept"]
        question_type = result["question_type"]
        difficulty = result["difficulty"]

        if concept not in state["asked_concepts"]:
            state["asked_concepts"].append(concept)

        question_number = state["question_count"] + 1

        # =================================================
        # 13. SAVE NEXT QUESTION
        # =================================================

        question_id = save_question(
            session_id=session_id,
            question_number=question_number,
            concept=concept,
            difficulty=difficulty,
            question=question,
            question_type=question_type
        )

        # =================================================
        # 14. UPDATE STATE AND DATABASE
        # =================================================

        state["difficulty"] = difficulty
        state["current_question"] = question
        state["current_question_id"] = question_id
        state["current_concept"] = concept
        state["current_question_type"] = question_type
        state["current_question_difficulty"] = difficulty
        state["question_count"] = question_number

        update_interview_state(
            session_id=session_id,
            current_difficulty=difficulty,
            current_question_id=question_id,
            question_count=question_number
        )

        # =================================================
        # 15. RETURN NEXT QUESTION
        # =================================================

        return {
            "session_id": session_id,
            "completed": False,
            "answer_id": answer_id,
            "score": score,
            "evaluation": evaluation,
            "next_difficulty": next_difficulty,
            "question": {
                "question_id": question_id,
                "question_number": question_number,
                "question": question,
                "concept": concept,
                "question_type": question_type,
                "difficulty": difficulty
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        print("=" * 60)
        print("ANSWER SUBMISSION ERROR")
        print("=" * 60)
        print(str(e))
        traceback.print_exc()
        print("=" * 60)

        raise HTTPException(
            status_code=500,
            detail="Failed to process the submitted answer."
        ) from e

# =========================================================
# FINISH INTERVIEW
# =========================================================

def finish_interview(
    session_id,
    state
):

    # =====================================================
    # Rebuild COMPLETE history from PostgreSQL
    # =====================================================

    questions = get_session_questions(
        session_id
    )

    history = []

    for question in questions:

        answer = get_answer_for_question(
            question["id"]
        )

        evaluation = get_evaluation_for_question(
            question["id"]
        )

        if answer and evaluation:

            history.append({

                "question_number":
                    question["question_number"],

                "question_id":
                    question["id"],

                "concept":
                    question["concept"],

                "question_type":
                    question["question_type"],

                "difficulty":
                    question["difficulty"],

                "question":
                    question["question"],

                "answer":
                    answer["answer"],

                "score":
                    evaluation["score"],

                "evaluation":
                    evaluation["overall_feedback"]
                    or ""
            })

    # =====================================================
    # Calculate Weak Areas
    # =====================================================

    weak_areas = analyze_weak_areas(
        history
    )

    # =====================================================
    # Save Weak Areas
    # =====================================================

    for area in weak_areas:

        save_weak_area(
            session_id=session_id,

            concept=area["concept"],

            average_score=
                area["average_score"],

            severity=
                area["severity"]
        )

    # =====================================================
    # Calculate Final Result
    # =====================================================

    final_difficulty = state[
        "difficulty"
    ]

    total_questions = len(
        history
    )

    total_score = sum(
        item["score"]
        for item in history
    )

    average_score = (
        total_score / total_questions
        if total_questions > 0
        else 0
    )

    # =====================================================
    # Generate Feedback
    # =====================================================

    try:

        feedback_report = generate_feedback_report(

            topic=state["topic"],

            starting_difficulty=
                state["starting_difficulty"],

            final_difficulty=
                final_difficulty,

            history=history,

            weak_areas=weak_areas
        )

        if not feedback_report:
            feedback_report = (
                "Feedback report could not be generated."
            )

    except Exception as e:

        print(
            f"[FEEDBACK AGENT] Failed: {e}"
        )

        feedback_report = (
            "Feedback report could not be generated "
            "because the Feedback Agent was unavailable."
        )

    # =====================================================
    # Update PostgreSQL
    # =====================================================

    update_interview_session(

        session_id=session_id,

        final_difficulty=
            final_difficulty,

        total_questions=
            total_questions,

        total_score=
            total_score,

        average_score=
            average_score
    )

    # =====================================================
    # Update Memory
    # =====================================================

    state["history"] = history

    state["weak_areas"] = weak_areas

    state["feedback_report"] = feedback_report

    # =====================================================
    # Return Final Result
    # =====================================================

    return {

        "session_id":
            session_id,

        "completed":
            True,

        "total_questions":
            total_questions,

        "total_score":
            total_score,

        "average_score":
            round(
                average_score,
                2
            ),

        "final_difficulty":
            final_difficulty,

        "weak_areas":
            weak_areas,

        "feedback_report":
            feedback_report
    }
# =========================================================
# GET SESSION
# =========================================================

def get_or_restore_interview_state(session_id: int):
    """
    Get interview state from memory.
    If not available, rebuild it from PostgreSQL.
    """

    if session_id in interview_states:
        return interview_states[session_id]

    state = build_state_from_database(session_id)

    if state is None:
        return None

    interview_states[session_id] = state

    return state

@router.get("/{session_id}")
def get_interview(
    session_id: int,
    current_user_id: int = Depends(get_current_user_id),
):
    if not verify_session_ownership(session_id, current_user_id):
        raise HTTPException(
            status_code=404,
            detail="Interview session not found.",
        )

    state = get_or_restore_interview_state(session_id)

    return {
        "session_id": session_id,
        "topic": state["topic"],
        "selected_concepts": state["selected_concepts"],
        "question_type": state["question_type"],
        "starting_difficulty": state["starting_difficulty"],
        "current_difficulty": state["current_question_difficulty"],
        "question_count": state["question_count"],
        "max_questions": state["max_questions"],
        "current_question": {
            "question_id": state["current_question_id"],
            "question": state["current_question"],
            "concept": state["current_concept"],
            "question_type": state["current_question_type"],
            "difficulty": state["current_question_difficulty"]
        },
        "status": (
            "COMPLETED"
            if state.get("feedback_report")
            else "IN_PROGRESS"
        )
    }

# =========================================================
# GET RESULT
# =========================================================

@router.get("/{session_id}/result")
def get_interview_result(
    session_id: int,
    current_user_id: int = Depends(get_current_user_id),
):
    if not verify_session_ownership(session_id, current_user_id):
        raise HTTPException(
            status_code=404,
            detail="Interview session not found.",
        )

    state = get_or_restore_interview_state(session_id)

    # If state does not contain a final report,
    # check PostgreSQL session status.
    session = get_interview_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found."
        )

    if session["status"] != "COMPLETED":
        return {
            "session_id": session_id,
            "completed": False,
            "message": "Interview is still in progress."
        }

    weak_areas = get_session_weak_areas(session_id)

    return {
        "session_id": session_id,
        "completed": True,
        "total_questions": session["total_questions"],
        "total_score": session["total_score"],
        "average_score": float(
            session["average_score"]
        )
        if session["average_score"] is not None
        else 0,
        "final_difficulty": session["final_difficulty"],
        "weak_areas": weak_areas,
        "feedback_report": state.get(
            "feedback_report",
            ""
        )
    }


# =========================================================
# GET WEAK AREAS
# =========================================================

@router.get("/{session_id}/weak-areas")
def get_weak_areas(
    session_id: int,
    current_user_id: int = Depends(get_current_user_id),
):
    if not verify_session_ownership(session_id, current_user_id):
        raise HTTPException(
            status_code=404,
            detail="Interview session not found.",
        )

    state = get_or_restore_interview_state(session_id)

    weak_areas = get_session_weak_areas(
        session_id
    )

    return {
        "session_id": session_id,
        "weak_areas": weak_areas
    }

# =========================================================
# BUILD INTERVIEW STATE FROM POSTGRESQL
# =========================================================

def build_state_from_database(session_id: int):

    session = get_interview_session(session_id)

    if not session:
        return None

    # -----------------------------------------------------
    # Get candidate profile
    # -----------------------------------------------------

    profile = get_user_profile(
        session["user_id"]
    )

    if not profile:
        return None

    # -----------------------------------------------------
    # Rebuild profile analysis
    # -----------------------------------------------------

    profile_analysis = {}

    try:
        profile_analysis = analyze_profile(
            name=profile["name"],
            education=profile["education"],
            skills=profile["skills"],
            projects=profile["projects"],
            experience=profile["experience"],
            target_role=profile["target_role"]
        )

    except Exception as e:
        print(
            f"[PROFILE RESTORE] Profile Agent unavailable: {e}"
        )

    if not profile_analysis:
        print(
            "[PROFILE RESTORE] Continuing without profile analysis."
        )

    # -----------------------------------------------------
    # Get all questions
    # -----------------------------------------------------

    questions = get_session_questions(
        session_id
    )

    history = []

    for question in questions:

        answer = get_answer_for_question(
            question["id"]
        )

        evaluation = get_evaluation_for_question(
            question["id"]
        )

        # Only completed questions belong in history
        if answer and evaluation:

            history.append({
                "question_number":
                    question["question_number"],

                "question_id":
                    question["id"],

                "concept":
                    question["concept"],

                "question_type":
                    question["question_type"],

                "difficulty":
                    question["difficulty"],

                "question":
                    question["question"],

                "answer":
                    answer["answer"],

                "score":
                    evaluation["score"],

                "evaluation":
                    (
                        evaluation["overall_feedback"]
                        or ""
                    )
            })

    # -----------------------------------------------------
    # Get current question
    # -----------------------------------------------------

    current_question = None

    if session["current_question_id"]:

        current_question = get_question(
            session["current_question_id"]
        )

    # -----------------------------------------------------
    # Asked concepts
    # -----------------------------------------------------

    asked_concepts = []

    for question in questions:

        concept = question["concept"]

        if concept not in asked_concepts:
            asked_concepts.append(concept)

    # -----------------------------------------------------
    # Build state
    # -----------------------------------------------------

    return {

        "profile":
            profile,

        "profile_analysis":
            profile_analysis,

        "user_id":
            session["user_id"],

        "session_id":
            session["id"],

        "topic":
            session["topic"],

        "selected_concepts":
            session["selected_concepts"],

        "question_type":
            session["question_type"],

        "starting_difficulty":
            session["starting_difficulty"],

        "difficulty":
            session["current_difficulty"],

        "current_question":
            (
                current_question["question"]
                if current_question
                else None
            ),

        "current_question_id":
            session["current_question_id"],

        "current_concept":
            (
                current_question["concept"]
                if current_question
                else None
            ),

        "current_question_type":
            (
                current_question["question_type"]
                if current_question
                else session["question_type"]
            ),

        "current_question_difficulty":
            (
                current_question["difficulty"]
                if current_question
                else session["current_difficulty"]
            ),

        "question_count":
            session["question_count"],

        "max_questions":
            session["max_questions"],

        "asked_concepts":
            asked_concepts,

        "history":
            history,

        "weak_areas":
            [],

        "feedback_report":
            ""
    }