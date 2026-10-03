"""Plain RAG: retrieve relevant chunks, then answer ONLY from them."""
from src import config, vector_store
from src.llm import generate

RAG_SYSTEM_PROMPT = """You are an HR policy assistant for Acme Tech Pvt Ltd.
Answer ONLY using the CONTEXT provided. Rules:
1. If the context does not contain the answer, say exactly: "I could not find this in the company policies."
2. Never guess or use outside knowledge about company rules.
3. Keep answers short and clear. Mention the source file name in brackets, e.g. [leave_policy.txt].
"""


def retrieve(query: str, k: int = config.TOP_K) -> list[dict]:
    """Search the index and drop chunks that are too far from the question."""
    results = vector_store.search(query, k)
    return [r for r in results if r["distance"] <= config.MAX_DISTANCE]


def format_context(results: list[dict]) -> str:
    return "\n\n".join(f"[{r['source']}]\n{r['text']}" for r in results)


def rag_answer(question: str) -> str:
    results = retrieve(question)
    if not results:
        return "I could not find this in the company policies."
    prompt = f"CONTEXT:\n{format_context(results)}\n\nQUESTION: {question}"
    return generate(prompt, system=RAG_SYSTEM_PROMPT)


if __name__ == "__main__":
    import sys

    q = " ".join(sys.argv[1:]) or "How many annual leave days do I get?"
    print(rag_answer(q))
