"""Step 1 smoke test: confirms your Gemini key and model work."""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()  # automatically uses GEMINI_API_KEY

response = client.models.generate_content(
    model=os.getenv("MODEL", "gemini-2.5-flash-lite"),
    contents="Say hello in one short sentence.",
)

print(response.text)
