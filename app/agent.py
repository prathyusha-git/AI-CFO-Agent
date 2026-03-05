# ==========================================================
# Instructions for running the project
# ==========================================================

# 1. Activate the virtual environment (loads Python packages)
# PowerShell command:
# .\.venv\Scripts\Activate.ps1

# 2. Start the FastAPI server
# uvicorn app.main:app --reload

# 3. Check server health
# http://127.0.0.1:8000/health

# 4. Open interactive API documentation
# http://127.0.0.1:8000/docs

# 5. Test the endpoint
# POST http://localhost:8000/ask
# Body:
# {
#   "question": "What should I do about cashflow?"
# }

# ==========================================================
# app/agent.py
# ==========================================================
# This file contains LLM "reasoning layer" functions.
# These functions take deterministic analytics (numbers)
# and ask GPT to explain + recommend actions.
#
# IMPORTANT:
# - We compute numbers in Python (tools.py)
# - GPT only explains those numbers (prevents hallucination)
# ==========================================================

import os
from openai import OpenAI

from app.tools import load_transactions, cashflow_summary, forecast_summary
from app.memory_local import add_memory, retrieve_memory


CASHFLOW_SYSTEM_PROMPT = """
You are an AI CFO for a small business.

You MUST base your answer on the provided cashflow_summary numbers.
Do NOT invent numbers.

Use the "memories" section as business context (past issues, decisions, constraints).
If memories conflict with the latest numbers, trust the latest numbers.

Be practical, specific, and recommend 3 actions.
If data is insufficient, say what’s missing and ask 1 clarifying question.

Keep it under 180 words.
"""

FORECAST_SYSTEM_PROMPT = """
You are an AI CFO for a small business.

You MUST base your answer on the provided forecast_summary numbers.
Do NOT invent numbers.

Use the "memories" section as business context.

Output format:
1) 1-sentence diagnosis
2) 3 concrete actions for the next 7 days
3) 1 metric to watch daily

Keep it under 180 words.
"""


def _get_client_and_model() -> tuple[OpenAI, str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY. Set it in .env")
    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    return client, model


def answer_question(business_id: str, question: str) -> dict:
    client, model = _get_client_and_model()

    # deterministic metrics
    df = load_transactions()
    summary = cashflow_summary(df)

    # memory retrieval
    memories = retrieve_memory(business_id=business_id, k=5)

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": CASHFLOW_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Business ID: {business_id}\n\n"
                    f"Question: {question}\n\n"
                    f"memories (most relevant first):\n{memories}\n\n"
                    f"cashflow_summary:\n{summary}"
                ),
            },
        ],
        temperature=0.2,
        max_tokens=300,
    )

    answer = resp.choices[0].message.content.strip()

    # store interaction in memory
    add_memory(business_id=business_id, kind="cashflow", question=question, answer=answer)

    return {"answer": answer, "cashflow_summary": summary, "memories_used": memories}


def answer_forecast_question(business_id: str, question: str) -> dict:
    client, model = _get_client_and_model()

    # deterministic forecast
    df = load_transactions()
    f_summary = forecast_summary(df)

    # memory retrieval
    memories = retrieve_memory(business_id=business_id, k=5)

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": FORECAST_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Business ID: {business_id}\n\n"
                    f"Question: {question}\n\n"
                    f"memories (most relevant first):\n{memories}\n\n"
                    f"forecast_summary:\n{f_summary}"
                ),
            },
        ],
        temperature=0.2,
        max_tokens=300,
    )

    answer = resp.choices[0].message.content.strip()

    # store interaction
    add_memory(business_id=business_id, kind="forecast", question=question, answer=answer)

    return {"answer": answer, "forecast_summary": f_summary, "memories_used": memories}