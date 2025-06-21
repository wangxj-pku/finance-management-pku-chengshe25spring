# Personal Finance Manager

A simple command-line Personal Finance Management System in Python that helps you:

* Track your income and expenses
* Manage monthly budgets per category
* View spending breakdowns and budget status
* Plot daily spending trends
* Get AI-based spending analysis and budget recommendations

---

## Features

* Add new transactions with amount, category, type (expense/income), and date
* Show spending breakdown by category and period
* Show remaining budgets for a selected month
* Show budget status summary with alerts if budgets exceeded
* Plot daily spending trends with Matplotlib
* AI spending analysis (summary and feedback) 
* Edit monthly budgets and save persistently
* Recommend budgets based on historical spending
* Anomaly detection for suspicious transactions

---

## Setup

1. Ensure you have Python 3.7+ installed.
2. Install dependencies:

```bash
pip install matplotlib
```

3. Run the program:

```bash
python main.py
```

4. For AI access features 
* Please remember to input your own API key in `gpt_analysis.py` **("YOUR-KEY-HERE")**.
---

## File Structure

* `main.py`: Main user interface and application logic
* `tracker.py`: Core tracking functions (loading/saving records, filtering, reporting)
* `budget_management.py`: Handles budgets loading, saving, and editing
* `gpt_analysis.py`: AI spending analysis (external API integration or mock)
* `budget_recommender.py`: Budget recommendation logic
* `anomaly_detection.py`: Spending anomaly detection
* `utils.py`: Helper functions and validation utilities
* `records.csv`: CSV file storing transaction records
* `budgets.csv`: CSV file storing monthly budgets by category

---

## Important Notes and Known Issues

### Budget Data Synchronization Issue

* **Current behavior:**
  When you update a budget category using option 7 (Edit budgets), the change is saved to `budgets.csv`. However, the budget values displayed by other functions such as "Show remaining budgets" or "Budget status summary" may still show outdated values until the program reloads the budgets from file.

* **Reason:**
  The `budgets` dictionary used inside `tracker.py` and other modules is loaded once at import time and cached in memory. It is not automatically refreshed after editing budgets.

* **Workaround:**
  After editing budgets, restart the program to ensure all modules load the latest budget data, or manually reload budgets inside the functions before accessing them.

* **Planned fix:**
  Modify `tracker.py` and related modules to reload budgets from the CSV file before calculations or pass updated budgets explicitly from `main.py`.

---

## How to Update Budgets Properly

To update budgets and see the latest values reflected everywhere without restarting:

1. Use option 7 in the menu to edit budgets.
2. Immediately after editing, budgets are saved but in-memory data in some parts of the program may not be updated.
3. Restart the program or modify the code to reload budgets dynamically (see **Planned fix** above).

---

## Future Improvements

* Implement automatic reloading of budget data across modules after edits.
* Enhance AI spending analysis with real API integration.
* Provide export and backup features for data.
* Add GUI for more user-friendly interaction.

## Authors

* Current version is made by 王希杰
