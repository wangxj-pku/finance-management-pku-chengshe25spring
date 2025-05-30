import json
from datetime import datetime

DATA_FILE = "transactions.json"

class Transaction:
    # 收入支出记录
    def __init__(self, amount, date, category, notes):
        self.amount = amount
        self.date = date  # string 'YYYY-MM-DD'
        self.category = category
        self.notes = notes

    def to_dict(self):
        return {
            "amount": self.amount,
            "date": self.date,
            "category": self.category,
            "notes": self.notes
        }

    @staticmethod
    def from_dict(data):
        return Transaction(data['amount'], data['date'], data['category'], data['notes'])

class FinanceManager:
    # 管理交易记录列表和数据存储
    def __init__(self):
        self.transactions = []
        self.load_data()

    def add_transaction(self, amount, date, category, notes):
        t = Transaction(amount, date, category, notes)
        self.transactions.append(t)
        self.save_data()

    def save_data(self):
        try:
            with open(DATA_FILE, "w") as f:
                json.dump([t.to_dict() for t in self.transactions], f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")

    def load_data(self):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                self.transactions = [Transaction.from_dict(item) for item in data]
        except FileNotFoundError:
            self.transactions = []
        except Exception as e:
            print(f"Error loading data: {e}")
            self.transactions = []

    def show_transactions(self):
        if not self.transactions:
            print("No transactions recorded yet.")
            return
        print("\nDate       | Category   | Amount   | Notes")
        print("--------------------------------------------")
        for t in self.transactions:
            print(f"{t.date:<10} | {t.category:<10} | {t.amount:<8.2f} | {t.notes}")

def input_date(prompt="Enter date (YYYY-MM-DD): "):
    while True:
        date_str = input(prompt)
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("Invalid date format. Please enter as YYYY-MM-DD.")

def main():
    fm = FinanceManager()

    while True:
        print("\n--- Personal Finance Manager ---")
        print("1. Add transaction")
        print("2. Show all transactions")
        print("3. Exit")
        choice = input("Select option: ")

        if choice == "1":
            try:
                amount = float(input("Amount: "))
                date = input_date()
                category = input("Category: ")
                notes = input("Notes (optional): ")
                fm.add_transaction(amount, date, category, notes)
                print("Transaction added successfully.")
            except ValueError:
                print("Invalid input for amount.")
        elif choice == "2":
            fm.show_transactions()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1, 2 or 3.")

if __name__ == "__main__":
    main()
