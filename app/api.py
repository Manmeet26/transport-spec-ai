from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from query import ask_question

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {"status": "running"}


@app.post("/query")
def query_doc(req: QueryRequest):

    result = ask_question(
        req.question
    )

    return result