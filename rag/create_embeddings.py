import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in .env")

client = genai.Client(api_key=api_key)


def create_embedding(text: str):
    """Create a Gemini embedding for the given text."""

    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text,
    )

    return response.embeddings[0].values


if __name__ == "__main__":
    print("Testing Gemini Embeddings...")
    print("-" * 50)

    text = """
    Python functions are reusable blocks of code.
    Decorators can modify the behavior of functions.
    """

    embedding = create_embedding(text)

    print("Embedding created successfully!")
    print(f"Vector dimensions: {len(embedding)}")
    print(f"First 10 values: {embedding[:10]}")