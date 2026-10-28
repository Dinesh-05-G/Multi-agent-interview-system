import os
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is not set in the .env file."
    )

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.6-flash"


def ask_gemini(prompt: str) -> str:
    """Send a prompt to Gemini with retry handling."""

    max_retries = 3

    for attempt in range(1, max_retries + 1):

        try:
            print(
                f"[GEMINI] Sending request "
                f"(attempt {attempt}/{max_retries})..."
            )

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )

            if not response:
                print("[GEMINI] Empty response received.")
                return ""

            if response.text:
                print("[GEMINI] Response received successfully.")
                return response.text.strip()

            print("[GEMINI] Response contains no text.")
            return ""

        except Exception as e:

            print(
                f"[GEMINI ERROR] "
                f"{type(e).__name__}: {e}"
            )

            if attempt < max_retries:
                wait_time = attempt * 2

                print(
                    f"[GEMINI] Retrying in "
                    f"{wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:
                print(
                    "[GEMINI] All retry attempts failed."
                )

    return ""


if __name__ == "__main__":

    print("Testing Gemini API...")
    print("-" * 50)

    prompt = """
You are an AI technical interviewer.

Ask me one medium-level Python interview question.
Do not provide the answer.
"""

    answer = ask_gemini(prompt)

    print("Gemini Response:")
    print(answer)