from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Transport Spec RAG AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


class Citation(BaseModel):
    section: str
    title: str
    page: Optional[int] = None
    snippet: str


class QueryResponse(BaseModel):
    answer: str
    rewritten_query: str
    citations: List[Citation]


@app.get("/")
def home():
    return {"status": "running", "service": "transport-spec-rag-ai"}


@app.post("/query", response_model=QueryResponse)
def query_doc(req: QueryRequest):
    from query import ask_question

    return ask_question(req.question)
