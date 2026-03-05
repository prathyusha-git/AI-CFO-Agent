import os
import pandas as pd


def load_transactions() -> pd.DataFrame:
    """
    Loads transactions from a CSV path set in .env as DATA_PATH.
    Default: ./data/sample_transactions.csv
    """
    data_path = os.getenv("DATA_PATH", "./data/sample_transactions.csv")
    df = pd.read_csv(data_path)
    df["date"] = pd.to_datetime(df["date"])
    return df


def cashflow_summary(df: pd.DataFrame) -> dict:
    """
    Deterministic monthly cashflow summary:
    - monthly income
    - monthly expense
    - monthly net cashflow
    - simple runway estimate
    """
    df = df.copy()
    df["month"] = df["date"].dt.to_period("M").astype(str)

    # Monthly totals
    monthly = df.groupby("month")["amount"].sum().sort_index()
    income = (
        df[df["amount"] > 0]
        .groupby("month")["amount"]
        .sum()
        .reindex(monthly.index, fill_value=0)
    )
    expense = (
        df[df["amount"] < 0]
        .groupby("month")["amount"]
        .sum()
        .reindex(monthly.index, fill_value=0)
    )

    latest_month = monthly.index[-1]
    prev_month = monthly.index[-2] if len(monthly.index) >= 2 else latest_month

    summary = {
        "months": list(monthly.index),
        "monthly_net_cashflow": {m: float(v) for m, v in monthly.items()},
        "monthly_income": {m: float(v) for m, v in income.items()},
        "monthly_expense": {m: float(v) for m, v in expense.items()},
        "latest_month": latest_month,
        "latest_net": float(monthly.loc[latest_month]),
        "prev_month": prev_month,
        "prev_net": float(monthly.loc[prev_month]),
    }

    # Runway estimate:
    # If latest net is negative, estimate months of runway assuming starting cash = 1.5x latest monthly expense.
    latest_expense_abs = abs(float(expense.loc[latest_month])) if latest_month in expense.index else 0.0
    if latest_expense_abs > 0 and summary["latest_net"] < 0:
        starting_cash = 1.5 * latest_expense_abs
        burn = abs(summary["latest_net"])
        summary["estimated_runway_months"] = round(starting_cash / burn, 2) if burn > 0 else None
    else:
        summary["estimated_runway_months"] = None

    return summary


def forecast_summary(df: pd.DataFrame) -> dict:
    """
    Deterministic, explainable forecast:
    - Uses last up to 3 months
    - Forecasts next month income/expense using a simple linear trend
    - Provides runway and risk level
    """
    df = df.copy()
    df["month"] = df["date"].dt.to_period("M").astype(str)

    # Monthly aggregates
    monthly_net = df.groupby("month")["amount"].sum().sort_index()
    monthly_income = (
        df[df["amount"] > 0]
        .groupby("month")["amount"]
        .sum()
        .reindex(monthly_net.index, fill_value=0)
    )
    monthly_expense = (
        df[df["amount"] < 0]
        .groupby("month")["amount"]
        .sum()
        .reindex(monthly_net.index, fill_value=0)
    )

    months = list(monthly_net.index)
    n = len(months)

    latest_month = months[-1]
    prev_month = months[-2] if n >= 2 else latest_month

    # Helper: percent change (safe)
    def pct_change(curr: float, prev: float):
        if prev == 0:
            return None
        return round(((curr - prev) / abs(prev)) * 100, 2)

    income_latest = float(monthly_income.loc[latest_month])
    income_prev = float(monthly_income.loc[prev_month])

    expense_latest = float(monthly_expense.loc[latest_month])  # negative
    expense_prev = float(monthly_expense.loc[prev_month])      # negative

    revenue_trend_pct = pct_change(income_latest, income_prev)
    expense_trend_pct = pct_change(expense_latest, expense_prev)

    # Use last up to 3 points for a simple linear trend forecast
    use_k = min(3, n)
    recent_months = months[-use_k:]

    y_income = [float(monthly_income.loc[m]) for m in recent_months]
    y_expense = [float(monthly_expense.loc[m]) for m in recent_months]

    # linear forecast: y_next = y_last + slope
    def linear_next(y):
        if len(y) == 1:
            return y[0]
        slope = (y[-1] - y[0]) / (len(y) - 1)
        return y[-1] + slope

    forecast_income_next = round(linear_next(y_income), 2)
    forecast_expense_next = round(linear_next(y_expense), 2)  # negative
    forecast_net_next = round(forecast_income_next + forecast_expense_next, 2)

    # Runway estimate based on latest month burn
    latest_expense_abs = abs(expense_latest)
    latest_net = float(monthly_net.loc[latest_month])

    runway_months = None
    if latest_expense_abs > 0 and latest_net < 0:
        starting_cash = 1.5 * latest_expense_abs
        burn = abs(latest_net)
        runway_months = round(starting_cash / burn, 2) if burn > 0 else None

    # Risk label + reasons (explainable rules)
    risk = "low"
    reasons = []

    if latest_net < 0:
        reasons.append(f"Latest month net cashflow is negative ({latest_net}).")

    if revenue_trend_pct is not None and revenue_trend_pct < -15:
        risk = "high"
        reasons.append(f"Revenue dropped sharply ({revenue_trend_pct}%).")
    elif revenue_trend_pct is not None and revenue_trend_pct < 0:
        risk = "medium"
        reasons.append(f"Revenue is down ({revenue_trend_pct}%).")

    if runway_months is not None and runway_months < 2:
        risk = "high"
        reasons.append(f"Estimated runway is short ({runway_months} months).")
    elif runway_months is not None and runway_months < 3 and risk != "high":
        risk = "medium"
        reasons.append(f"Estimated runway is limited ({runway_months} months).")

    if forecast_net_next < 0 and risk == "low":
        risk = "medium"
        reasons.append(f"Next month forecast net is negative ({forecast_net_next}).")

    return {
        "months_used": recent_months,
        "latest_month": latest_month,
        "latest_income": income_latest,
        "latest_expense": expense_latest,
        "latest_net": latest_net,
        "revenue_trend_pct": revenue_trend_pct,
        "expense_trend_pct": expense_trend_pct,
        "forecast_next_month": {
            "income": forecast_income_next,
            "expense": forecast_expense_next,
            "net": forecast_net_next,
        },
        "estimated_runway_months": runway_months,
        "risk_level": risk,
        "risk_reasons": reasons,
    }