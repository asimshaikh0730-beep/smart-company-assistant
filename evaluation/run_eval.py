"""Run the test questions through the agent and report a score.

Run:  python -m evaluation.run_eval

Checks:
 - normal questions: the answer must contain the expected facts
 - must_refuse questions: the bot must say it does not know / will not help
 - must_clarify questions: the bot must ask the user for more detail
This is a simple keyword-based eval. Later you can add an LLM-as-judge.
It sleeps between questions to respect free-tier rate limits.
"""
import json
import time
from pathlib import Path

from src.agent import ask

QUESTIONS = Path(__file__).parent / "questions.json"

REFUSAL_HINTS = ["could not find", "couldn't find", "don't have", "do not have",
                 "cannot", "can't", "unable", "not mentioned", "no information",
                 "only help", "not covered", "outside"]

CLARIFY_HINTS = ["could you", "can you", "please specify", "please clarify",
                 "what kind", "what type", "which limit", "which policy",
                 "more detail", "more specific", "clarify"]

SLEEP_SECONDS = 5


def check(case: dict, answer: str) -> bool:
    text = answer.lower()
    if case.get("must_clarify"):
        return any(h in text for h in CLARIFY_HINTS)
    if case.get("must_refuse"):
        return any(h in text for h in REFUSAL_HINTS)
    if "must_include_all" in case:
        return all(s.lower() in text for s in case["must_include_all"])
    if "must_include_any" in case:
        return any(s.lower() in text for s in case["must_include_any"])
    return False


def main() -> None:
    cases = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    passed = 0
    for i, case in enumerate(cases, 1):
        try:
            answer = ask(case["question"], "E101")
        except Exception as e:
            answer = f"[ERROR] {e!r}"
        ok = check(case, answer)
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'}  Q{i}: {case['question']}")
        if not ok:
            print(f"      answer: {answer[:300]}")
        time.sleep(SLEEP_SECONDS)
    print(f"\nScore: {passed}/{len(cases)} = {passed / len(cases):.0%}")


if __name__ == "__main__":
    main()