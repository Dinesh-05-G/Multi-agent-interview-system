from database.connection import get_connection


def create_user(name: str, email: str):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO users (name, email)
        VALUES (%s, %s)
        ON CONFLICT (email)
        DO UPDATE SET name = EXCLUDED.name
        RETURNING id;
        """,
        (name, email)
    )

    user_id = cursor.fetchone()[0]

    connection.commit()
    cursor.close()
    connection.close()

    return user_id


def create_interview_session(
    user_id: int,
    topic: str,
    starting_difficulty: str,
    selected_concepts: list,
    question_type: str,
    max_questions: int
):
    connection = get_connection()
    cursor = connection.cursor()

    concepts_text = ", ".join(selected_concepts)

    cursor.execute(
        """
        INSERT INTO interview_sessions
        (
            user_id,
            topic,
            selected_concepts,
            question_type,
            starting_difficulty,
            current_difficulty,
            question_count,
            max_questions,
            status
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id;
        """,
        (
            user_id,
            topic,
            concepts_text,
            question_type,
            starting_difficulty,
            starting_difficulty,
            0,
            max_questions,
            "IN_PROGRESS"
        )
    )

    session_id = cursor.fetchone()[0]

    connection.commit()

    cursor.close()
    connection.close()

    return session_id


def save_question(
    session_id: int,
    question_number: int,
    concept: str,
    difficulty: str,
    question: str,
    question_type: str
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO questions
        (
            session_id,
            question_number,
            concept,
            difficulty,
            question,
            question_type
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
        """,
        (
            session_id,
            question_number,
            concept,
            difficulty,
            question,
            question_type
        )
    )

    question_id = cursor.fetchone()[0]

    connection.commit()

    cursor.close()
    connection.close()

    return question_id

def update_interview_state(
    session_id: int,
    current_difficulty: str,
    current_question_id: int,
    question_count: int
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE interview_sessions
        SET
            current_difficulty = %s,
            current_question_id = %s,
            question_count = %s
        WHERE id = %s;
        """,
        (
            current_difficulty,
            current_question_id,
            question_count,
            session_id
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

def save_answer(question_id: int, answer: str):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO answers
        (
            question_id,
            answer
        )
        VALUES (%s, %s)
        RETURNING id;
        """,
        (
            question_id,
            answer
        )
    )

    answer_id = cursor.fetchone()[0]

    connection.commit()
    cursor.close()
    connection.close()

    return answer_id


def save_evaluation(
    question_id: int,
    score: int,
    correctness: str,
    relevance: str,
    technical_depth: str,
    clarity: str,
    missing_concepts: str,
    overall_feedback: str
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO evaluations
        (
            question_id,
            score,
            correctness,
            relevance,
            technical_depth,
            clarity,
            missing_concepts,
            overall_feedback
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """,
        (
            question_id,
            score,
            correctness,
            relevance,
            technical_depth,
            clarity,
            missing_concepts,
            overall_feedback
        )
    )

    evaluation_id = cursor.fetchone()[0]

    connection.commit()
    cursor.close()
    connection.close()

    return evaluation_id


def update_interview_session(
    session_id: int,
    final_difficulty: str,
    total_questions: int,
    total_score: int,
    average_score: float
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE interview_sessions
        SET
            final_difficulty = %s,
            total_questions = %s,
            total_score = %s,
            average_score = %s,
            status = %s,
            completed_at = CURRENT_TIMESTAMP
        WHERE id = %s;
        """,
        (
            final_difficulty,
            total_questions,
            total_score,
            average_score,
            "COMPLETED",
            session_id
        )
    )

    connection.commit()

    cursor.close()
    connection.close()


def save_weak_area(
    session_id: int,
    concept: str,
    average_score: float,
    severity: str
):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO weak_areas
            (
                session_id,
                concept,
                average_score,
                severity
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (session_id, concept)
            DO UPDATE SET
                average_score = EXCLUDED.average_score,
                severity = EXCLUDED.severity;
            """,
            (
                session_id,
                concept,
                average_score,
                severity
            )
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def update_user_profile(
    user_id: int,
    education: str,
    skills: list,
    projects: list,
    experience: str,
    target_role: str
):
    connection = get_connection()
    cursor = connection.cursor()

    skills_text = ", ".join(skills)
    projects_text = ", ".join(projects)

    cursor.execute(
        """
        UPDATE users
        SET
            education = %s,
            skills = %s,
            projects = %s,
            experience = %s,
            target_role = %s
        WHERE id = %s;
        """,
        (
            education,
            skills_text,
            projects_text,
            experience,
            target_role,
            user_id
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

if __name__ == "__main__":

    from database.connection import get_connection

    user_id = create_user(
        name="Dinesh",
        email="dinesh@example.com"
    )

    update_user_profile(
        user_id=user_id,
        education="B.E. Computer Science",
        skills=[
            "Python",
            "Machine Learning",
            "SQL",
            "FastAPI",
            "LangChain"
        ],
        projects=[
            "AI Interview System",
            "Medical VR Training System"
        ],
        experience="Fresher",
        target_role="Python Developer"
    )

    print("Profile updated successfully.")

    # =========================================================
# GET INTERVIEW SESSION
# =========================================================

def get_interview_session(session_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            user_id,
            topic,
            selected_concepts,
            question_type,
            starting_difficulty,
            current_difficulty,
            current_question_id,
            question_count,
            max_questions,
            final_difficulty,
            total_questions,
            total_score,
            average_score,
            status,
            started_at,
            completed_at
        FROM interview_sessions
        WHERE id = %s;
        """,
        (session_id,)
    )

    row = cursor.fetchone()

    cursor.close()
    connection.close()

    if not row:
        return None

    return {
        "id": row[0],
        "user_id": row[1],
        "topic": row[2],
        "selected_concepts": (
            row[3].split(", ")
            if row[3]
            else []
        ),
        "question_type": row[4],
        "starting_difficulty": row[5],
        "current_difficulty": row[6],
        "current_question_id": row[7],
        "question_count": row[8],
        "max_questions": row[9],
        "final_difficulty": row[10],
        "total_questions": row[11],
        "total_score": row[12],
        "average_score": (
            float(row[13])
            if row[13] is not None
            else 0
        ),
        "status": row[14],
        "started_at": row[15],
        "completed_at": row[16]
    }


# =========================================================
# GET QUESTION
# =========================================================

def get_question(question_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            session_id,
            question_number,
            concept,
            difficulty,
            question,
            question_type,
            created_at
        FROM questions
        WHERE id = %s;
        """,
        (question_id,)
    )

    row = cursor.fetchone()

    cursor.close()
    connection.close()

    if not row:
        return None

    return {
        "id": row[0],
        "session_id": row[1],
        "question_number": row[2],
        "concept": row[3],
        "difficulty": row[4],
        "question": row[5],
        "question_type": row[6],
        "created_at": row[7]
    }


# =========================================================
# GET ALL QUESTIONS FOR SESSION
# =========================================================

def get_session_questions(session_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            session_id,
            question_number,
            concept,
            difficulty,
            question,
            question_type,
            created_at
        FROM questions
        WHERE session_id = %s
        ORDER BY question_number ASC;
        """,
        (session_id,)
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return [
        {
            "id": row[0],
            "session_id": row[1],
            "question_number": row[2],
            "concept": row[3],
            "difficulty": row[4],
            "question": row[5],
            "question_type": row[6],
            "created_at": row[7]
        }
        for row in rows
    ]


# =========================================================
# GET ANSWER FOR QUESTION
# =========================================================

def get_answer_for_question(question_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            question_id,
            answer,
            created_at
        FROM answers
        WHERE question_id = %s
        ORDER BY id DESC
        LIMIT 1;
        """,
        (question_id,)
    )

    row = cursor.fetchone()

    cursor.close()
    connection.close()

    if not row:
        return None

    return {
        "id": row[0],
        "question_id": row[1],
        "answer": row[2],
        "created_at": row[3]
    }


# =========================================================
# GET EVALUATION FOR QUESTION
# =========================================================

def get_evaluation_for_question(question_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            question_id,
            score,
            correctness,
            relevance,
            technical_depth,
            clarity,
            missing_concepts,
            overall_feedback,
            created_at
        FROM evaluations
        WHERE question_id = %s
        ORDER BY id DESC
        LIMIT 1;
        """,
        (question_id,)
    )

    row = cursor.fetchone()

    cursor.close()
    connection.close()

    if not row:
        return None

    return {
        "id": row[0],
        "question_id": row[1],
        "score": row[2],
        "correctness": row[3],
        "relevance": row[4],
        "technical_depth": row[5],
        "clarity": row[6],
        "missing_concepts": row[7],
        "overall_feedback": row[8],
        "created_at": row[9]
    }


# =========================================================
# GET WEAK AREAS
# =========================================================


def get_session_weak_areas(session_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                concept,
                AVG(average_score) AS average_score,
                CASE
                    WHEN AVG(average_score) < 4 THEN 'HIGH'
                    WHEN AVG(average_score) < 7 THEN 'MEDIUM'
                    ELSE 'LOW'
                END AS severity
            FROM weak_areas
            WHERE session_id = %s
            GROUP BY concept
            ORDER BY AVG(average_score) ASC;
            """,
            (session_id,)
        )

        rows = cursor.fetchall()

        return [
            {
                "concept": row[0],
                "average_score": round(float(row[1]), 2),
                "severity": row[2]
            }
            for row in rows
        ]

    finally:
        cursor.close()
        connection.close()

# =========================================================
# GET USER PROFILE
# =========================================================

def get_user_profile(user_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            email,
            education,
            skills,
            projects,
            experience,
            target_role
        FROM users
        WHERE id = %s;
        """,
        (user_id,)
    )

    row = cursor.fetchone()

    cursor.close()
    connection.close()

    if not row:
        return None

    return {
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "education": row[3],
        "skills": (
            row[4].split(", ")
            if row[4]
            else []
        ),
        "projects": (
            row[5].split(", ")
            if row[5]
            else []
        ),
        "experience": row[6],
        "target_role": row[7]
    }


def verify_session_ownership(session_id: int, user_id: int) -> bool:
    """Return True only when the session belongs to this user."""
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT 1
            FROM interview_sessions
            WHERE id = %s AND user_id = %s
            """,
            (session_id, user_id),
        )
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        connection.close()


def get_user_interview_sessions(user_id: int):
    """Return interview sessions belonging to one user."""
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                id,
                topic,
                question_type,
                starting_difficulty,
                final_difficulty,
                total_questions,
                total_score,
                average_score,
                status,
                started_at,
                completed_at
            FROM interview_sessions
            WHERE user_id = %s
            ORDER BY started_at DESC, id DESC;
            """,
            (user_id,),
        )

        rows = cursor.fetchall()

        return [
            {
                "session_id": row[0],
                "topic": row[1],
                "question_type": row[2],
                "starting_difficulty": row[3],
                "final_difficulty": row[4],
                "total_questions": row[5] or 0,
                "total_score": row[6] or 0,
                "average_score": (
                    float(row[7]) if row[7] is not None else None
                ),
                "status": row[8],
                "started_at": row[9],
                "completed_at": row[10],
            }
            for row in rows
        ]

    finally:
        cursor.close()
        connection.close()
