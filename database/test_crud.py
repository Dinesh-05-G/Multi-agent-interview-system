from database.crud import (
    create_user,
    create_interview_session,
    save_question,
    save_answer,
    save_evaluation,
    save_weak_area,
    update_interview_session
)


print("=" * 70)
print("DATABASE CRUD TEST")
print("=" * 70)


# --------------------------------------------------
# 1. CREATE USER
# --------------------------------------------------

print("\n[1] Creating user...")

user_id = create_user(
    name="Test Candidate",
    email="testcandidate@example.com"
)

print(f"User created/found. ID: {user_id}")


# --------------------------------------------------
# 2. CREATE INTERVIEW SESSION
# --------------------------------------------------

print("\n[2] Creating interview session...")

session_id = create_interview_session(
    user_id=user_id,
    topic="Python",
    starting_difficulty="Medium"
)

print(f"Interview session created. ID: {session_id}")


# --------------------------------------------------
# 3. SAVE QUESTION
# --------------------------------------------------

print("\n[3] Saving question...")

question_id = save_question(
    session_id=session_id,
    question_number=1,
    concept="Decorators",
    difficulty="Medium",
    question="What are decorators in Python and how are they implemented?"
)

print(f"Question saved. ID: {question_id}")


# --------------------------------------------------
# 4. SAVE ANSWER
# --------------------------------------------------

print("\n[4] Saving answer...")

answer_id = save_answer(
    question_id=question_id,
    answer=(
        "A decorator is a function that modifies or extends "
        "the behavior of another function without changing its source code."
    )
)

print(f"Answer saved. ID: {answer_id}")


# --------------------------------------------------
# 5. SAVE EVALUATION
# --------------------------------------------------

print("\n[5] Saving evaluation...")

evaluation_id = save_evaluation(
    question_id=question_id,
    score=8,
    correctness="The answer correctly explains the purpose of decorators.",
    relevance="The answer is relevant to the question.",
    technical_depth="Good basic understanding but implementation details are missing.",
    clarity="The answer is clear and concise.",
    missing_concepts="Function wrappers and @decorator syntax.",
    overall_feedback="Good answer. Add implementation details for a stronger response."
)

print(f"Evaluation saved. ID: {evaluation_id}")


# --------------------------------------------------
# 6. SAVE WEAK AREA
# --------------------------------------------------

print("\n[6] Saving weak area...")

save_weak_area(
    session_id=session_id,
    concept="Decorators",
    average_score=8.0,
    severity="LOW"
)

print("Weak area saved.")


# --------------------------------------------------
# 7. UPDATE SESSION
# --------------------------------------------------

print("\n[7] Updating interview session...")

update_interview_session(
    session_id=session_id,
    final_difficulty="Hard",
    total_questions=1,
    total_score=8,
    average_score=8.0
)

print("Interview session updated.")


print("\n" + "=" * 70)
print("DATABASE CRUD TEST COMPLETED SUCCESSFULLY")
print("=" * 70)