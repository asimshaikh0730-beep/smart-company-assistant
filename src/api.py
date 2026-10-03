"""FastAPI web service.   Run:  uvicorn src.api:app --reload"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src import vector_store
from src.agent import ask
from src.guardrails import looks_like_injection, mask_pii, too_long
from src.ingest import build_index


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Build the search index on first start if it does not exist yet.
    if vector_store.count() == 0:
        build_index()
    yield


app = FastAPI(title="Smart Company Assistant", lifespan=lifespan)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3)
    employee_id: str = Field("E101", max_length=20)


class AskResponse(BaseModel):
    answer: str


@app.get("/health")
def health():
    return {"status": "ok", "indexed_chunks": vector_store.count()}


@app.post("/ask", response_model=AskResponse)
def ask_endpoint(req: AskRequest):
    if too_long(req.question):
        raise HTTPException(status_code=400, detail="Question is too long.")
    if looks_like_injection(req.question):
        raise HTTPException(status_code=400, detail="I can only help with company policy questions.")

    safe_question = mask_pii(req.question)
    try:
        return AskResponse(answer=ask(safe_question, req.employee_id))
    except Exception as e:  # e.g. rate limit after retries
        print(f"[api] error: {e!r}")
        raise HTTPException(status_code=503, detail="The AI service is busy. Please try again in a minute.")
