import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not set in .env"
    )


def get_connection():
    return psycopg2.connect(DATABASE_URL)


if __name__ == "__main__":
    print("Testing PostgreSQL connection...")
    print("-" * 60)

    try:
        connection = get_connection()

        print("PostgreSQL connection successful!")

        connection.close()

    except Exception as e:
        print("PostgreSQL connection failed.")
        print(f"{type(e).__name__}: {e}")