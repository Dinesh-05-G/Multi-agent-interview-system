from database.connection import get_connection


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    # ---------------------------------------------------------
    # USERS
    # ---------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # ---------------------------------------------------------
    # INTERVIEW SESSIONS
    # ---------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),

            topic VARCHAR(100) NOT NULL,

            selected_concepts TEXT,

            question_type VARCHAR(30),

            starting_difficulty VARCHAR(20) NOT NULL,

            current_difficulty VARCHAR(20),

            current_question_id INTEGER,

            question_count INTEGER DEFAULT 0,

            max_questions INTEGER DEFAULT 0,

            final_difficulty VARCHAR(20),

            total_questions INTEGER DEFAULT 0,

            total_score INTEGER DEFAULT 0,

            average_score NUMERIC(5,2),

            status VARCHAR(20) DEFAULT 'IN_PROGRESS',

            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            completed_at TIMESTAMP
        );
    """)

    # ---------------------------------------------------------
    # QUESTIONS
    # ---------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY,
            session_id INTEGER REFERENCES interview_sessions(id),
            question_number INTEGER NOT NULL,
            concept VARCHAR(150),
            difficulty VARCHAR(20),
            question TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # ---------------------------------------------------------
    # ANSWERS
    # ---------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            id SERIAL PRIMARY KEY,
            question_id INTEGER REFERENCES questions(id),
            answer TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # ---------------------------------------------------------
    # EVALUATIONS
    # ---------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id SERIAL PRIMARY KEY,
            question_id INTEGER REFERENCES questions(id),
            score INTEGER,
            correctness TEXT,
            relevance TEXT,
            technical_depth TEXT,
            clarity TEXT,
            missing_concepts TEXT,
            overall_feedback TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # ---------------------------------------------------------
    # WEAK AREAS
    # ---------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weak_areas (
            id SERIAL PRIMARY KEY,
            session_id INTEGER REFERENCES interview_sessions(id),
            concept VARCHAR(150) NOT NULL,
            average_score NUMERIC(5,2),
            severity VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    connection.commit()

    cursor.close()
    connection.close()

    print("Database tables created successfully!")


if __name__ == "__main__":
    print("Creating AI Interview database tables...")
    print("-" * 60)

    create_tables()

    print("-" * 60)
    print("Schema setup completed.")