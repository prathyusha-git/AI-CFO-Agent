from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    business_id: str = Field(default="demo", min_length=1, max_length=64)
    question: str = Field(..., min_length=3, max_length=500)


class AskResponse(BaseModel):
    answer: str
    cashflow_summary: dict
    memories_used: list[str]


class AskForecastRequest(BaseModel):
    business_id: str = Field(default="demo", min_length=1, max_length=64)
    question: str = Field(..., min_length=3, max_length=500)


class AskForecastResponse(BaseModel):
    answer: str
    forecast_summary: dict
    memories_used: list[str]