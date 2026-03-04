import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

from app.schemas import AskRequest, AskResponse
from app.agent import answer_question

load_dotenv()

app = FastAPI(title="CashFlow CFO Agent", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    try:
        result = answer_question(req.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))