import os
import requests
import json
from datetime import date, timedelta
from tracker import calculate_spending
from budget_management import budgets
from anomaly_detection import SpendingAnomalyDetector, build_daily_features

# ── Configuration ─────────────────────────────────────────────────────────────
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "YOUR-KEY-HERE")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
MODEL_NAME = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# ── Utility: date string for `days` ago ─────────────────────────────────────────
def _days_ago_string(days):
    return (date.today() - timedelta(days=days)).isoformat()

def _first_day_of_month():
    """Get the first day of the current month."""
    today = date.today()
    return today.replace(day=1)

def _last_day_of_month():
    """Get the last day of the current month."""
    today = date.today()
    next_month = today.replace(day=28) + timedelta(days=4)  # this will never fail
    return next_month - timedelta(days=next_month.day)

# ── Summarize Spending as structured JSON ────────────────────────────────────────
def summarize_spending(records, period_type="week"):
    """
    Build a structured summary of spending data:
      - transactions list filtered by date
      - monthly budgets
      - spending totals per category

    period_type: either 'week' or 'month'
    Returns a dict ready for JSON serialization.
    """
    if period_type == "week":
        cutoff = _days_ago_string(7)  # Last 7 days
        period_label = "last 7 days"
    elif period_type == "month":
        start_date = _first_day_of_month()
        end_date = _last_day_of_month()
        cutoff = start_date.isoformat()
        period_label = f"from {start_date} to {end_date}"
    else:
        raise ValueError("Invalid period type. Use 'week' or 'month'.")

    # Filter records for the selected period
    recent = [r for r in records if r.get("date", "") >= cutoff]

    spending_totals = calculate_spending(recent)

    summary = {
        "period": period_label,
        "transactions": recent,
        "budgets": budgets,
        "spending": spending_totals
    }

    # Optionally, include anomaly detection results
    daily_feats = build_daily_features(recent)
    detector = SpendingAnomalyDetector()
    if not daily_feats.empty:
        try:
            detector.train(daily_feats)
            anomaly_results = detector.predict(daily_feats)
            # Extract dates flagged as anomalies
            anomalies = anomaly_results[anomaly_results['anomaly']].index.strftime("%Y-%m-%d").tolist()
            summary["anomalies"] = anomalies
        except Exception as e:
            summary["anomaly_detection_error"] = str(e)

    return summary

# ── Analyze with DeepSeek Chat API ────────────────────────────────────────────────
def analyze_spending_deepseek(summary: dict):
    """
    Send structured summary to DeepSeek Chat API with enhanced, detailed prompts.
    """
    system_prompt = (
        "You are a data-driven financial advisor. "
        "Analyze the user's transaction data, monthly budgets, spending trends, "
        "and highlight any anomalies in spending patterns. "
        "Budgets represent the maximum allowed expenses per category per month. "
        "Provide a brief numeric overview, detect anomalies, and give one clear actionable tip."
    )

    user_content = (
        "Here is the user's financial data as JSON:\n```"
        + json.dumps(summary, indent=2)
        + "\n```\n"
        "Please provide your analysis in a structured but easy-to-read way."
    )

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
    }

    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return "[Error] Unexpected response format from DeepSeek."
