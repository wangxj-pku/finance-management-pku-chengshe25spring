# File: budget_recommender.py
# Suggests budget amounts based on past monthly spending patterns using clustering

import os
import json
import numpy as np
from sklearn.cluster import KMeans

from budget_management import BUDGET_CATEGORIES, budgets
from tracker import calculate_spending

# Paths
DATA_PATH = "data"
MONTHLY_SPENDING_FILE = os.path.join(DATA_PATH, "monthly_spending.json")
RECOMMENDATION_FILE = os.path.join(DATA_PATH, "budget_recommendations.json")

# Config
N_CLUSTERS = 3


def load_monthly_spending():
    if not os.path.exists(MONTHLY_SPENDING_FILE):
        return []
    with open(MONTHLY_SPENDING_FILE, "r") as f:
        return json.load(f)


def save_monthly_spending(data):
    os.makedirs(DATA_PATH, exist_ok=True)
    with open(MONTHLY_SPENDING_FILE, "w") as f:
        json.dump(data, f, indent=2)


def save_recommendations(recs):
    os.makedirs(DATA_PATH, exist_ok=True)
    with open(RECOMMENDATION_FILE, "w") as f:
        json.dump(recs, f, indent=2)


def load_recommendations():
    if not os.path.exists(RECOMMENDATION_FILE):
        return {}
    with open(RECOMMENDATION_FILE, "r") as f:
        return json.load(f)


def aggregate_monthly_spending(records):
    """
    Aggregates total spending per category for each month in records.
    Returns: List[ { "month": "YYYY-MM", "spending": {cat: amt, ...} } ]
    """
    monthly_data = {}

    for rec in records:
        date_str = rec.get("date", "")
        if len(date_str) < 7:
            continue
        month = date_str[:7]  # YYYY-MM
        cat = rec.get("category")
        amt = rec.get("amount", 0)
        ttype = rec.get("type")
        if ttype != "expense":
            continue

        if month not in monthly_data:
            monthly_data[month] = {c: 0.0 for c in BUDGET_CATEGORIES}
        if cat in monthly_data[month]:
            try:
                monthly_data[month][cat] += float(amt)
            except (ValueError, TypeError):
                continue

    result = []
    for month in sorted(monthly_data.keys()):
        result.append({"month": month, "spending": monthly_data[month]})
    return result


def build_feature_matrix(monthly_spending):
    """
    Converts monthly spending into an array of budget adherence ratios.
    Each row = month; each column = spending ratio (spent / budget).
    """
    features = []
    for month_data in monthly_spending:
        month_spending = month_data["spending"]
        row = []
        for cat in BUDGET_CATEGORIES:
            budget_amt = budgets.get(cat, 1)  # avoid divide-by-zero
            if budget_amt <= 0:
                ratio = 1.0
            else:
                ratio = month_spending.get(cat, 0) / budget_amt
            row.append(ratio)
        features.append(row)
    return np.array(features)


def fit_clusters(features):
    if len(features) < N_CLUSTERS:
        return None
    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42)
    kmeans.fit(features)
    return kmeans


def recommend_budgets(records):
    """
    Generate budget recommendations based on past behavior using clustering.
    Returns: {category: new_budget}
    """
    monthly_spending = aggregate_monthly_spending(records)
    if not monthly_spending:
        return {}

    features = build_feature_matrix(monthly_spending)
    kmeans = fit_clusters(features)
    if kmeans is None:
        return budgets.copy()

    last_month_features = features[-1].reshape(1, -1)
    cluster_idx = kmeans.predict(last_month_features)[0]
    cluster_center = kmeans.cluster_centers_[cluster_idx]

    recommended = {}
    for i, cat in enumerate(BUDGET_CATEGORIES):
        current_budget = budgets.get(cat, 0)
        suggested = cluster_center[i] * current_budget
        blended = 0.7 * current_budget + 0.3 * suggested
        recommended[cat] = round(max(blended, 100), 2)

    save_monthly_spending(monthly_spending)
    save_recommendations(recommended)

    return recommended
