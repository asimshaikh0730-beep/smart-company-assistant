"""One place that talks to Gemini, with retry for free-tier rate limits."""
import time
from functools import lru_cache

from google import genai
from google.genai import errors, types

from src import config


@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    return genai.Client()  # reads GEMINI_API_KEY from the environment


def generate(prompt: str, system: str | None = None, tools: list | None = None,
             temperature: float = 0.2) -> str:
    """Send a prompt, return the text answer.

    If `tools` (plain Python functions) are given, the SDK lets the model call
    them automatically and feeds the results back until it has a final answer.
    """
    cfg = types.GenerateContentConfig(
        system_instruction=system, tools=tools, temperature=temperature
    )
    for attempt in range(config.MAX_RETRIES):
        try:
            resp = get_client().models.generate_content(
                model=config.MODEL, contents=prompt, config=cfg
            )
            return (resp.text or "").strip()
        except errors.APIError as e:
            retryable = e.code in (429, 500, 503)
            if retryable and attempt < config.MAX_RETRIES - 1:
                wait = 2 ** (attempt + 1)
                print(f"[llm] error {e.code}, retrying in {wait}s...")
                time.sleep(wait)
                continue
            raise
    return ""
