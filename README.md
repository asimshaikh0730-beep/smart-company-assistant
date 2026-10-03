# Smart Company Assistant (free-stack GenAI project)

An HR assistant for a fictional company ("Acme Tech"). It answers policy questions
using **RAG** (retrieval from policy documents) and can **call tools** (check leave
balance, apply for leave). It includes guardrails, an evaluation script, a FastAPI
service and a Dockerfile.

Everything runs on free tools: Gemini API free tier, local embeddings, Chroma, FastAPI, Docker.
Use only fake documents - free-tier requests may be used by Google to improve its products.

## Architecture

```
Question -> guardrails (PII mask, injection check)
         -> agent (Gemini + tools)
              |-- search_policies -> embed query -> Chroma -> top chunks
              |-- check_leave_balance
              '-- apply_leave
         -> grounded answer with source file names
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell   (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env             # Mac/Linux: cp .env.example .env   -> then put your key in .env
python src/hello_llm.py            # smoke test
```

## Run it, phase by phase

| Phase | Command | What you learn |
|---|---|---|
| 1. Build the index | `python -m src.ingest` | loading, chunking, embeddings, vector DB |
| 2. Plain RAG | `python -m src.rag "How many annual leave days do I get?"` | retrieval + grounded prompt |
| 3. Agent + tools | `python -m src.agent "Apply 2 days casual leave from next Monday"` | tool calling |
| 4. Evaluate | `python -m evaluation.run_eval` | test set, hallucination check |
| 5. API | `uvicorn src.api:app --reload` then open http://127.0.0.1:8000/docs | FastAPI |
| 6. Docker | `docker build -t smart-assistant .` then `docker run -p 8000:8000 --env-file .env smart-assistant` | containers |

Fast offline tests (no key needed): `pip install -r requirements-dev.txt` then `pytest`

## Tuning knobs (src/config.py)

`CHUNK_SIZE`, `CHUNK_OVERLAP`, `TOP_K`, `MAX_DISTANCE`. Change one, re-run
`python -m src.ingest`, then `python -m evaluation.run_eval` and compare scores.
That experiment loop is what interviewers want to hear about.

## Ideas to extend

LLM-as-judge faithfulness score, hybrid (keyword + vector) search, reranking,
a Streamlit/React front end, logging/tracing, response caching, switching to LangChain/LangGraph.
