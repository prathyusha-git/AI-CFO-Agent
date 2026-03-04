import os
import pandas as pd


def load_transactions() -> pd.DataFrame:
    data_path = os.getenv("DATA_PATH", "./data/sample_transactions.csv")
    df = pd.read_csv(data_path)
    df["date"] = pd.to_datetime(df["date"])
    # amount: income positive, expense negative already in sample
    return df


def cashflow_summary(df: pd.DataFrame) -> dict:
    df["month"] = df["date"].dt.to_period("M").astype(str)

    # total income/expense per month
    monthly = df.groupby("month")["amount"].sum().sort_index()
    income = df[df["amount"] > 0].groupby("month")["amount"].sum().reindex(monthly.index, fill_value=0)
    expense = df[df["amount"] < 0].groupby("month")["amount"].sum().reindex(monthly.index, fill_value=0)

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

    # simple “runway” proxy: if latest net is negative, how many months until cash=0 (assume starting cash 1 month of expenses)
    latest_expense_abs = abs(expense.loc[latest_month]) if latest_month in expense.index else 0.0
    if latest_expense_abs > 0 and summary["latest_net"] < 0:
        # assume starting cash equal to 1.5x latest monthly expense
        starting_cash = 1.5 * latest_expense_abs
        burn = abs(summary["latest_net"])
        summary["estimated_runway_months"] = round(starting_cash / burn, 2) if burn > 0 else None
    else:
        summary["estimated_runway_months"] = None

    return summary