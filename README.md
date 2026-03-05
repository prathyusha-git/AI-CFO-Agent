# CashFlow CFO Agent

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-green)
![OpenAI](https://img.shields.io/badge/OpenAI-LLM-orange)
![License](https://img.shields.io/badge/license-MIT-lightgrey)
![Status](https://img.shields.io/badge/status-prototype-success)
# AI-CFO-Agent
CashFlowGPT — An AI CFO Agent for SMBs....... This will 
1) Connect to mock QuickBooks data  
2)Analyze cash flow trends  
3)Predict burn risk  
4)Recommend actions  
5)Store long-term memory  
6)Use RAG  
7)Expose a FastAPI endpoint  
8)Show real reasoning workflow

## Demo

This backend provides financial monitoring and AI advisory capabilities.

Key endpoints demonstrated:

- `/dashboard` → Business health overview
- `/alerts` → Financial risk monitoring
- `/ask_forecast` → AI CFO recommendations

Example financial alerts detected by the system:

- Revenue dropped 62.5% month-over-month
- Latest month net cashflow is negative
- Estimated runway ~2.3 months
- Next month forecast is negative
  
AI-CFO-Agent
│
├── app
│ ├── main.py # FastAPI server
│ ├── agent.py # AI CFO reasoning layer
│ ├── tools.py # Financial analytics engine
│ ├── memory.py # Conversation memory
│
├── data
│ └── sample_transactions.csv
│
├── requirements.txt
└── README.md

## Demo Video

Loom walkthrough:
# CashFlow CFO Agent

An AI-powered financial monitoring and advisory backend built with **FastAPI, Python, and OpenAI**.  
The system analyzes business transactions, forecasts financial trends, detects financial risks, and provides CFO-style recommendations.

It combines **deterministic financial analytics** with **LLM reasoning and contextual memory** to simulate an **AI CFO assistant for small businesses**.

---

# Features

## Financial Analytics
- Monthly income, expenses, and net cashflow analysis
- Revenue and expense trend detection
- Burn rate and runway estimation

## Forecasting
- Predict next month's income, expenses, and net cashflow
- Detect financial risk signals early

## AI CFO Advisor
- Ask financial questions in natural language
- Receive structured financial recommendations
- Context-aware responses using stored conversation memory

## Financial Monitoring
- Revenue drop alerts
- Expense spike alerts
- Cash runway warnings
- Negative forecast detection

---

# System Architecture


The system separates **deterministic financial computation** from **AI reasoning**, improving reliability, explainability, and performance.

---

# API Endpoints

## Health Check
GET /health

Checks whether the API server is running.

---

## Financial Analytics

### Cashflow Summary
**GET /health**

Checks whether the API server is running.

---

## Financial Analytics

### Cashflow Summary

**GET /summary**
Returns monthly:
- income
- expenses
- net cashflow

---
**GET /forecast**
Predicts next month's:

- income
- expenses
- net cashflow
- revenue trend
- expense trend

---
**GET /dashboard**
Provides a **complete financial health overview** including:

- cashflow summary
- forecast summary
- runway estimate
- risk level
- recommended actions

Example response:

```json
{
  "risk_level": "high",
  "estimated_runway_months": 2.28,
  "recommended_actions": [
    "Reduce discretionary expenses immediately",
    "Secure short-term financing or increase revenue"
  ]
}



**Financial Risk Alerts**
GET /alerts
Detects financial warning signals such as:
revenue collapse
expense spikes
negative cashflow
runway danger
negative forecast

Example response:
{
  "risk_level": "high",
  "alerts": [
    "Revenue dropped 62.5% month-over-month",
    "Latest month net cashflow is negative (-5800)",
    "Runway is high risk: ~2.28 months remaining",
    "Next month forecast is negative (projected net -7615)"
  ]
}
**AI CFO Advisor
Ask Financial Questions**
POST /ask

{
  "question": "How can I improve my cashflow?"
}

**Ask Forecast-Based Questions**
POST /ask_forecast

Example request:

{
  "business_id": "demo",
  "question": "Given the forecast, what should I fix this week?"
}

This endpoint combines:
transaction analytics
financial forecasting
conversation memory
LLM reasoning

to produce **context-aware financial recommendations.**

**How to Run**
**Install dependencies**
pip install -r requirements.txt
**Activate virtual environment (Windows)**
.\.venv\Scripts\Activate.ps1
**Set OpenAI API key**
Create a .env file:
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o
**Start the API server**
uvicorn app.main:app --reload
**Open API documentation**
http://127.0.0.1:8000/docs
Swagger UI allows you to test all endpoints interactively.

**Example Workflow**
Load business transactions
Generate financial analytics
Detect financial risks
Ask the AI CFO for recommendations

**Example:**

POST /ask_forecast
{
  "business_id": "demo",
  "question": "Why is my cashflow declining?"
}

The system combines: transaction analytics, forecasting, monitoring alerts, conversational memory, AI reasoning to provide structured financial advice.

**Tech Stack**

**Backend**
FastAPI
Python

**AI**
OpenAI GPT models

**Data Processing**
Pandas

**Financial Logic**
Custom analytics engine

**Monitoring**
Deterministic financial rule engine

**Future Improvements**
Possible production enhancements:
Integration with QuickBooks or Plaid APIs
Real-time financial monitoring
Slack / email alert notifications
ML-based anomaly detection
Automated cost optimization recommendations
