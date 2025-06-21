# tracker.py
# Handles loading, saving, filtering, analyzing, and plotting financial transaction data

import csv
import os
from collections import defaultdict
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import List, Dict

from budget_management import BUDGET_CATEGORIES, budgets, calculate_spending

RECORDS_CSV = "records.csv"


def load_records(filename=RECORDS_CSV) -> List[Dict]:
    records = []
    if not os.path.exists(filename):
        return records
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Validate required fields existence
                if not all(k in row for k in ('amount', 'category', 'type', 'date')):
                    print(f"⚠️ Skipping incomplete record: {row}")
                    continue

                amount = float(row.get('amount', 0))
                category = row.get('category', '').strip()
                ttype = row.get('type', '').strip()
                date = row.get('date', '').strip()

                if not category or not ttype or not date:
                    print(f"⚠️ Skipping record with empty fields: {row}")
                    continue

                rec = {
                    'amount': amount,
                    'category': category,
                    'type': ttype,
                    'date': date,
                }
                records.append(rec)
            except ValueError as e:
                print(f"⚠️ Skipping record with invalid amount: {row} — Reason: {e}")
                continue
    return records


def save_records(records_list: List[Dict], filename=RECORDS_CSV):
    """
    Save a list of transaction records to a CSV file.
    """
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['amount', 'category', 'type', 'date']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records_list:
            writer.writerow(r)


def add_record(records_list: List[Dict], new_record: Dict):
    """
    Append a new transaction record to the list and save immediately.
    """
    records_list.append(new_record)
    save_records(records_list)


def filter_records_by_period(records_list: List[Dict], period: str) -> List[Dict]:
    """
    Filter records based on a string period:
    - '7d' = last 7 days (including today)
    - '30d' = last 30 days
    - 'this_month' = records in current calendar month
    - 'last_month' = records in previous calendar month
    - 'all' = no filtering (default)
    """
    now = datetime.now()

    if period == 'all':
        return records_list

    filtered = []
    for r in records_list:
        try:
            dt = datetime.strptime(r.get('date', ''), "%Y-%m-%d")
        except Exception:
            continue

        if period == '7d':
            if dt >= now - timedelta(days=6):  # last 7 days including today
                filtered.append(r)
        elif period == '30d':
            if dt >= now - timedelta(days=29):  # last 30 days including today
                filtered.append(r)
        elif period == 'this_month':
            if dt.year == now.year and dt.month == now.month:
                filtered.append(r)
        elif period == 'last_month':
            last_month = (now.replace(day=1) - timedelta(days=1))
            if dt.year == last_month.year and dt.month == last_month.month:
                filtered.append(r)

    return filtered


def show_spending_breakdown(records_list: List[Dict], period='this_month'):
    filtered_records = filter_records_by_period(records_list, period)
    if not filtered_records:
        print("No transactions to display for this period.")
        return

    spending = calculate_spending(filtered_records)
    total = sum(spending.values())
    if total == 0:
        print("No expenses recorded yet in this period.")
        return

    print(f"Spending Breakdown ({period}):")
    for cat in BUDGET_CATEGORIES:
        amt = spending.get(cat, 0)
        pct = (amt / total * 100) if total else 0
        print(f"- {cat}: ¥{amt:.2f} ({pct:.1f}%)")


def show_remaining_budget(records_list: List[Dict], period='this_month'):
    filtered_records = filter_records_by_period(records_list, period)
    if not filtered_records:
        print("No transactions to calculate remaining budgets for this period.")
        return

    spending = calculate_spending(filtered_records)
    print(f"Remaining Monthly Budget (¥) - Period: {period}")
    for cat in BUDGET_CATEGORIES:
        spent = spending.get(cat, 0)
        if cat in budgets:
            left = budgets[cat] - spent
            print(f"- {cat}: ¥{left:.2f} left of ¥{budgets[cat]:.2f}")


def budget_status_summary(records_list: List[Dict], period='this_month'):
    filtered_records = filter_records_by_period(records_list, period)
    if not filtered_records:
        print("No transactions to calculate budget status for this period.")
        return

    spending = calculate_spending(filtered_records)
    print(f"Monthly Budget Status Summary - Period: {period}")
    for cat in BUDGET_CATEGORIES:
        spent = spending.get(cat, 0)
        limit = budgets.get(cat, 0)
        if spent > limit:
            status = "Exceeded"
        elif spent == limit:
            status = "At Limit"
        else:
            status = "Within Budget"
        print(f"- {cat}: {status} (¥{spent:.2f}/¥{limit:.2f})")


def plot_daily_spending(records_list: List[Dict], period='this_month'):
    filtered_records = filter_records_by_period(records_list, period)
    if not filtered_records:
        print("No transactions to plot for this period.")
        return

    daily = defaultdict(float)
    for r in filtered_records:
        try:
            if r.get('type') == 'expense':
                date_key = r.get('date')
                amount = float(r.get('amount', 0))
                if not date_key:
                    raise ValueError("Missing date")
                daily[date_key] += amount
        except Exception as e:
            print(f"⚠️  Skipping invalid record: {r} — Reason: {e}")

    if not daily:
        print("No valid expense data to plot.")
        return

    dates = sorted(daily.keys())
    values = [daily[d] for d in dates]

    plt.figure(figsize=(8, 4))
    plt.plot(dates, values, marker='o')
    plt.title(f"Daily Spending Trend ({period})")
    plt.xlabel("Date")
    plt.ylabel("Amount Spent (¥)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(True)
    plt.show()
