from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_answer(context: str, question: str):

    prompt = f"""
You are a helpful school tutor.

Answer the question using the provided context only.
If content is not in NCERT say "Out of Syllabus".
Context:
{context}

Question:
{question}

Provide a clear and concise answer.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text