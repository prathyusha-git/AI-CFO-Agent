from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from app.tools import dashboard_summary
from fastapi.responses import Response
import json
from app.tools import alerts_summary

from app.schemas import (
    AskRequest,
    AskResponse,
    AskForecastRequest,
    AskForecastResponse,
)
from app.agent import answer_question, answer_forecast_question
from app.tools import load_transactions, cashflow_summary, forecast_summary

load_dotenv()

app = FastAPI(title="CashFlow CFO Agent", version="0.3.0")


@app.get("/health")
def health():
    return {"status": "ok"}


# Deterministic: no GPT
@app.get("/summary")
def summary():
    df = load_transactions()
    return cashflow_summary(df)


# Deterministic: no GPT
@app.get("/forecast")
def forecast():
    df = load_transactions()
    return forecast_summary(df)

@app.get("/dashboard", tags=["dashboard"])
def dashboard():
    df = load_transactions()
    data = dashboard_summary(df)

    pretty = json.dumps(data, indent=2)
    return Response(content=pretty, media_type="application/json")

@app.get("/alerts", tags=["monitoring"])
def alerts():
    df = load_transactions()
    return alerts_summary(df)

@app.get("/", tags=["meta"])
def root():
    return {
        "name": "CashFlow CFO Agent",
        "docs": "/docs",
        "health": "/health",
        "summary": "/summary",
        "forecast": "/forecast",
        "dashboard": "/dashboard",
        "alerts": "/alerts",
        "ask": "/ask",
        "ask_forecast": "/ask_forecast",
    }

# GPT + Memory over cashflow_summary
@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    try:
        return answer_question(req.business_id, req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# GPT + Memory over forecast_summary
@app.post("/ask_forecast", response_model=AskForecastResponse)
def ask_forecast(req: AskForecastRequest):
    try:
        return answer_forecast_question(req.business_id, req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

