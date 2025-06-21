# File: utils.py
# Common utility functions for category validation, budget alerts, and date handling

import difflib
from datetime import datetime

# Defined global categories — must match BUDGET_CATEGORIES in other modules
KNOWN_CATEGORIES = ["food", "transport", "entertainment", "shopping", "others"]


def validate_category(cat: str) -> str:
    """
    Check if input category is in known categories.
    If not, suggest the closest match.
    """
    cat = cat.strip().lower()
    if cat in KNOWN_CATEGORIES:
        return cat

    suggestion = difflib.get_close_matches(cat, KNOWN_CATEGORIES, n=1)
    if suggestion:
        print(f"Unknown category '{cat}'. Did you mean: '{suggestion[0]}'?")
        return suggestion[0]
    else:
        print(f"Unknown category '{cat}'. Please use one of: {', '.join(KNOWN_CATEGORIES)}")
        return cat


def get_month_key(date_str):
    """
    Extract "YYYY-MM" from a date string "YYYY-MM-DD".
    """
    return date_str[:7]


def calculate_category_spent(records, category, month_key):
    """
    Calculate total expenses in the given category and month (YYYY-MM).
    """
    total = 0.0
    for r in records:
        try:
            if (
                r["type"] == "expense"
                and r["category"] == category
                and r["date"].startswith(month_key)
            ):
                total += float(r["amount"])
        except (KeyError, ValueError, TypeError):
            continue
    return total


def check_budget_alerts(records, budgets, new_record):
    """
    Check for budget alerts after adding a new record.
    Alerts: overspending, 80/90/100% milestones.
    """
    alerts = []
    if new_record.get("type") != "expense":
        return alerts

    date = new_record.get("date")
    category = new_record.get("category")
    if not date or not category:
        return alerts

    month_key = get_month_key(date)
    budget = budgets.get(category)
    if budget is None:
        return alerts

    spent = calculate_category_spent(records, category, month_key)

    # Overspend check
    if spent > budget:
        alerts.append(f"⚠️ You exceeded the budget for '{category}': ¥{spent:.2f} / ¥{budget:.2f}")

    # Milestone notices
    else:
        for pct in [0.8, 0.9, 1.0]:
            if spent >= budget * pct and (spent - new_record["amount"]) < budget * pct:
                alerts.append(f"🔔 You reached {int(pct * 100)}% of '{category}' budget: ¥{spent:.2f} / ¥{budget:.2f}")
                break

    return alerts
