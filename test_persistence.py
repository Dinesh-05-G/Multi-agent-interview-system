from database.crud import (
    get_session_questions,
    get_answer_for_question,
    get_evaluation_for_question
)

SESSION_ID = 24

questions = get_session_questions(SESSION_ID)

print("=" * 60)
print("ANSWER + EVALUATION CHECK")
print("=" * 60)

for q in questions:
    question_id = q["id"]

    answer = get_answer_for_question(question_id)
    evaluation = get_evaluation_for_question(question_id)

    print(f"\nQuestion ID: {question_id}")
    print(f"Concept: {q['concept']}")
    print("ANSWER:")
    print(answer)
    print("EVALUATION:")
    print(evaluation)