
from database.connection import get_connection


def migrate():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS password_hash TEXT;
        """)

        connection.commit()
        print("Authentication migration completed.")
        print("Existing users and interview sessions were preserved.")

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    migrate()
