# File: budget_management.py
# Manages budgets persistence and provides core budget-check logic.

import csv
import os

BUDGETS_CSV = "budgets.csv"
BUDGET_CATEGORIES = ["food", "transport", "entertainment", "shopping", "others"]
budgets = {}


def load_budgets(filename=BUDGETS_CSV):
    """
    Load budgets from CSV into global `budgets` dict.
    If file doesn't exist, initializes all categories with zero.
    """
    global budgets
    budgets = {}

    if not os.path.exists(filename):
        budgets = {cat: 0.0 for cat in BUDGET_CATEGORIES}
        save_budgets(filename)
        return budgets

    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cat = row.get("category", "").strip()
            if not cat:
                print(f"⚠️ Skipping budget row with missing category: {row}")
                continue
            try:
                val = float(row.get("budget", 0))
            except ValueError:
                print(f"⚠️ Skipping budget row with invalid amount: {row}")
                val = 0.0
            if cat in BUDGET_CATEGORIES:
                budgets[cat] = val

    # Ensure all categories are present
    for cat in BUDGET_CATEGORIES:
        budgets.setdefault(cat, 0.0)

    return budgets


def save_budgets(filename=BUDGETS_CSV):
    """
    Save the global `budgets` dict to a CSV file.
    """
    global budgets
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["category", "budget"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for cat in BUDGET_CATEGORIES:
            writer.writerow({"category": cat, "budget": budgets.get(cat, 0.0)})


def calculate_spending(records_list):
    """
    Calculate total expense per category from transaction records.
    Only considers type == "expense".
    Returns: {category: total_spent}
    """
    spending = {cat: 0.0 for cat in BUDGET_CATEGORIES}
    for r in records_list:
        if r.get("type") == "expense":
            cat = r.get("category")
            if cat in spending:
                try:
                    amt = float(r.get("amount", 0))
                    spending[cat] += amt
                except (ValueError, TypeError):
                    continue
    return spending


def edit_budget(category, new_value):
    """
    Update the budget for a given category.
    Returns True if successful, False otherwise.
    """
    global budgets
    if category not in BUDGET_CATEGORIES:
        print(f"❌ Invalid category '{category}'.")
        return False
    try:
        val = float(new_value)
        if val < 0:
            print("❌ Budget cannot be negative.")
            return False
    except ValueError:
        print("❌ Invalid budget amount.")
        return False

    budgets[category] = val
    save_budgets()
    print(f"✅ Budget for '{category}' set to ¥{val:.2f}.")
    return True


def check_budget(spending, budgets_dict):
    """
    Return list of warning messages for overspending categories.
    """
    alerts = []
    for cat, spent in spending.items():
        limit = budgets_dict.get(cat, 0.0)
        if spent > limit:
            alerts.append(f"⚠️  Warning: '{cat}' exceeded budget (¥{spent:.2f} > ¥{limit:.2f})")
    return alerts


# Autoload budgets at import
load_budgets()
