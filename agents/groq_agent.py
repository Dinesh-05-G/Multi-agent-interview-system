import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# PROJECT ROOT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# ============================================================
# GROQ CONFIGURATION
# ============================================================

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY is not set in .env"
    )

client = Groq(api_key=api_key)

MODEL_NAME = "openai/gpt-oss-20b"


# ============================================================
# ASK GROQ
# ============================================================

def ask_groq(prompt: str) -> str:

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert technical interviewer. "
                        "Follow the user's instructions exactly. "
                        "When asked for a question, return only the question."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],

            temperature=0.2,

            # Increased because GPT-OSS may use
            # completion tokens for reasoning
            max_completion_tokens=1500,
        )

        print("[GROQ DEBUG] Response received.")
        print(
            f"[GROQ DEBUG] Choices: "
            f"{len(response.choices)}"
        )

        if not response.choices:
            print("[GROQ ERROR] No choices returned.")
            return ""

        message = response.choices[0].message

        print(
            f"[GROQ DEBUG] Content: "
            f"{repr(message.content)}"
        )

        print(
            f"[GROQ DEBUG] Reasoning length: "
            f"{len(message.reasoning) if message.reasoning else 0}"
        )

        if message.content and message.content.strip():

            return message.content.strip()

        print(
            "[GROQ WARNING] Model returned empty content."
        )

        return ""

    except Exception as e:

        print(
            f"[GROQ ERROR] "
            f"{type(e).__name__}: {e}"
        )

        return ""

    except Exception as e:

        print(
            f"[GROQ ERROR] "
            f"{type(e).__name__}: {e}"
        )

        return ""


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("Testing Groq API...")
    print(f"Model: {MODEL_NAME}")
    print("-" * 50)

    test_prompt = """
Generate ONE Python technical interview question.

Topic: Python decorators.

Return ONLY the question.
Do not provide the answer.
Do not provide explanation.
"""

    answer = ask_groq(test_prompt)

    print()
    print("Groq Response:")
    print("-" * 50)
    print(answer)
    print("-" * 50)