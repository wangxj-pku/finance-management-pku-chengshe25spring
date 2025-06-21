"""
Main script for the Personal Finance Management System.
Handles user interaction and ties together budget_management and tracker modules.
"""

from budget_management import budgets, load_budgets, save_budgets, edit_budget, BUDGET_CATEGORIES
from tracker import (
    load_records, save_records, add_record,
    show_spending_breakdown, show_remaining_budget,
    budget_status_summary, plot_daily_spending,
    filter_records_by_period
)
from gpt_analysis import summarize_spending, analyze_spending_deepseek
from budget_recommender import recommend_budgets
from anomaly_detection import SpendingAnomalyDetector
from utils import (
    validate_category,
    get_month_key,
    calculate_category_spent,
    check_budget_alerts
)
from datetime import date as dt_date, datetime


def print_divider():
    print("\n" + "=" * 50 + "\n")


def print_menu():
    print("\n=== Personal Finance Manager ===")
    print("Note: Budgets are monthly limits (¥ per month).")
    print("1. Add new transaction")
    print("2. Show spending breakdown")
    print("3. Show remaining budgets (select month)")
    print("4. Show budget status summary (select month)")
    print("5. Plot daily spending trend (select period)")
    print("6. AI Spending Analysis (select period)")
    print("7. Edit budgets (monthly)")
    print("8. Show recommended budgets")
    print("9. Exit")


def input_transaction():
    try:
        amt = float(input("Amount: ¥"))
        if amt < 0:
            print("Amount cannot be negative.")
            return None
    except ValueError:
        print("Invalid amount.")
        return None

    cat = input("Category: ")
    cat = validate_category(cat)
    if not cat:
        print("Category cannot be empty.")
        return None

    ttype = input("Type (expense/income) [e/i]: ").strip().lower()
    if ttype == "e":
        ttype = "expense"
    elif ttype == "i":
        ttype = "income"
    else:
        print("Invalid type.")
        return None

    today_str = dt_date.today().isoformat()
    date_input = input(f"Date (default {today_str}, or YYYYMMDD): ").strip()
    if not date_input:
        date = today_str
    elif len(date_input) == 8 and date_input.isdigit():
        try:
            datetime.strptime(date_input, "%Y%m%d")
            date = f"{date_input[:4]}-{date_input[4:6]}-{date_input[6:]}"
        except ValueError:
            print("Invalid date format.")
            return None
    else:
        try:
            datetime.strptime(date_input, "%Y-%m-%d")
            date = date_input
        except ValueError:
            print("Invalid date format.")
            return None

    return {"amount": amt, "category": cat, "type": ttype, "date": date}


def input_period():
    print("\nSelect time period:")
    print("1. Last 7 days")
    print("2. Last 30 days")
    print("3. This month")
    print("4. Last month")
    print("5. All time")
    choice = input("Choose (1-5, default 3): ").strip()
    mapping = {
        '1': '7d',
        '2': '30d',
        '3': 'this_month',
        '4': 'last_month',
        '5': 'all'
    }
    return mapping.get(choice, 'this_month')


def input_period_month_only():
    print("\nSelect month for budget analysis:")
    print("1. This month")
    print("2. Last month")
    choice = input("Choose (1-2, default 1): ").strip()
    mapping = {
        '1': 'this_month',
        '2': 'last_month'
    }
    return mapping.get(choice, 'this_month')


def main():
    load_budgets()
    records = load_records()
    detector = SpendingAnomalyDetector()

    while True:
        print_divider()
        print_menu()
        choice = input("Select an option: ").strip()

        if choice == '1':
            while True:
                new = input_transaction()
                if new:
                    add_record(records, new)
                    print("Transaction added.")

                    alerts = check_budget_alerts(records, budgets, new)
                    for alert in alerts:
                        print(alert)

                    if detector.is_anomalous(new, records):
                        print("🚨 Warning: This transaction appears anomalous compared to your recent spending!")

                else:
                    print("Failed to add transaction. Try again.")
                cont = input("Add another transaction? (y/n): ").strip().lower()
                if cont != 'y':
                    break
            input("\nPress Enter to continue...")

        elif choice == '2':
            period = input_period()
            show_spending_breakdown(records, period)
            input("\nPress Enter to continue...")

        elif choice == '3':
            period = input_period_month_only()
            print("Note: Budgets are monthly limits, so analysis is for the selected month only.")
            show_remaining_budget(records, period)
            input("\nPress Enter to continue...")

        elif choice == '4':
            period = input_period_month_only()
            print("Note: Budgets are monthly limits, so analysis is for the selected month only.")
            budget_status_summary(records, period)
            input("\nPress Enter to continue...")

        elif choice == '5':
            period = input_period()
            plot_daily_spending(records, period)
            input("\nPress Enter to continue...")

        elif choice == '6':
            period = input_period()
            filtered = filter_records_by_period(records, period)

            # Correct mapping for AI model expectation
            if period in ["7d", "30d"]:
                period_type = "week"
            elif period in ["this_month", "last_month"]:
                period_type = "month"
            else:
                period_type = "month"  # fallback

            summary = summarize_spending(filtered, period_type=period_type)

            print("\nSummary Data:")
            print(summary)
            print("\nAI Feedback:")
            feedback = analyze_spending_deepseek(summary)
            print(feedback)
            input("\nPress Enter to continue...")

        elif choice == '7':
            print("\nCurrent Monthly Budgets (¥ per month):")
            for cat in BUDGET_CATEGORIES:
                print(f"- {cat}: ¥{budgets.get(cat, 0)}")
            cat = input("\nEnter category to edit: ").strip()
            amt = input("Enter new monthly budget amount: ").strip()
            if not edit_budget(cat, amt):
                print("Failed to update budget. Please try again.")
            input("\nPress Enter to continue...")

        elif choice == '8':
            print("\nBudget Recommendations Based on Past Spending and Adherence:")
            recs = recommend_budgets(records)
            if not recs:
                print("Not enough data to generate recommendations.")
            else:
                for cat, amt in recs.items():
                    print(f"- {cat}: ¥{amt:.2f}")
            input("\nPress Enter to continue...")

        elif choice == '9':
            print("Goodbye!")
            save_records(records)
            save_budgets()
            break

        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
