import csv
import random
from datetime import datetime, timedelta

RECORDS_CSV = "records.csv"

# Known categories and typical daily spending ranges (expenses)
CATEGORIES = {
    "food": (5, 50),
    "transport": (2, 20),
    "entertainment": (0, 40),
    "shopping": (0, 100),
    "others": (0, 30)
}

# Income categories and typical monthly salary or random small incomes
INCOME_CATEGORIES = ["salary", "bonus", "gift"]

def random_date(start_date, end_date):
    """Generate a random date between start_date and end_date."""
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

def generate_record(date):
    """Generate one transaction record for a given date."""
    # Decide type: 85% chance expense, 15% income
    ttype = "expense" if random.random() < 0.85 else "income"

    if ttype == "expense":
        category = random.choices(
            population=list(CATEGORIES.keys()),
            weights=[0.4, 0.25, 0.1, 0.15, 0.1],
            k=1
        )[0]
        low, high = CATEGORIES[category]
        # Random amount in realistic range, rounded to 2 decimals
        amount = round(random.uniform(low, high), 2)
        # Occasionally create bigger expenses (5% chance)
        if random.random() < 0.05:
            amount *= random.uniform(2, 5)
            amount = round(amount, 2)
    else:
        # Income
        category = random.choice(INCOME_CATEGORIES)
        # Income amount: mostly salary (fixed), small bonuses or gifts (random)
        if category == "salary":
            amount = 3000  # fixed monthly salary
        elif category == "bonus":
            amount = round(random.uniform(100, 500), 2)
        else:  # gift
            amount = round(random.uniform(20, 200), 2)

    return {
        "amount": amount,
        "category": category,
        "type": ttype,
        "date": date.strftime("%Y-%m-%d")
    }

def generate_data(start_date, end_date, min_records_per_day=0, max_records_per_day=3):
    """Generate a list of transaction records over date range."""
    records = []
    current_date = start_date
    while current_date <= end_date:
        num_records = random.randint(min_records_per_day, max_records_per_day)
        for _ in range(num_records):
            rec = generate_record(current_date)
            records.append(rec)
        current_date += timedelta(days=1)
    return records

def save_records(records, filename=RECORDS_CSV):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["amount", "category", "type", "date"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow(r)

if __name__ == "__main__":
    today = datetime.today()
    start = today - timedelta(days=60)  # 2 months ago
    data = generate_data(start, today, min_records_per_day=1, max_records_per_day=3)
    save_records(data)
    print(f"Generated {len(data)} transactions from {start.date()} to {today.date()} in {RECORDS_CSV}")
