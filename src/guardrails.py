"""Simple safety checks before text reaches the LLM.

These are basic first-layer defences, not a complete security solution.
"""
import re

from src import config

_PATTERNS = [
    (re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"), "[ID_NUMBER]"),                   # Aadhaar-like
    (re.compile(r"(?:\+91[\s-]?)?[6-9]\d{9}\b"), "[PHONE]"),                      # Indian mobile
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[EMAIL]"),                         # email
]

_INJECTION_HINTS = (
    "ignore previous instructions",
    "ignore all previous",
    "ignore the above",
    "reveal your system prompt",
    "show your system prompt",
    "disregard your instructions",
)


def mask_pii(text: str) -> str:
    for pattern, replacement in _PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def looks_like_injection(text: str) -> bool:
    lowered = text.lower()
    return any(hint in lowered for hint in _INJECTION_HINTS)


def too_long(text: str) -> bool:
    return len(text) > config.MAX_QUESTION_CHARS
