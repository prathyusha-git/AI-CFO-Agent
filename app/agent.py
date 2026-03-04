# .\.venv\Scripts\Activate.ps1   run that in terminal to load env variables from .env file before running the app
#uvicorn app.main:app --reload run that in terminal to start the app
#http://127.0.0.1:8000/health to check health
#http://127.0.0.1:8000/docs to see interactive API docs where you can also test the /ask endpoint with different questions.
# Then you can POST to http://localhost:8000/ask with JSON body {"question": "What should I do about cashflow?"} to get an answer based on the transactions data.
import os
from openai import OpenAI

from app.tools import load_transactions, cashflow_summary

SYSTEM_PROMPT = """You are an AI CFO for a small business.
You MUST base your answer on the provided cashflow_summary numbers.
Be practical, specific, and recommend 3 actions.
If data is insufficient, say what’s missing and ask 1 clarifying question.
Keep it under 180 words.
"""

def answer_question(question: str) -> dict:
    # Create client only when needed (after env is loaded)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY. Set it in .env")

    client = OpenAI(api_key=api_key)

    df = load_transactions()
    summary = cashflow_summary(df)

    model = os.getenv("OPENAI_MODEL", "gpt-4o")

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Question: {question}\n\ncashflow_summary:\n{summary}"},
        ],
        temperature=0.2,
    )

    answer = resp.choices[0].message.content.strip()

    return {"answer": answer, "cashflow_summary": summary}