"""Personal Expense Tracker (v2)
Run with:  py expense_tracker.py
"""
import os
from datetime import date

import matplotlib.pyplot as plt
import pandas as pd

FILE = "expenses.csv"
BUDGET_FILE = "budget.txt"
CATEGORIES = ["Food", "Travel", "Shopping", "Bills", "Other"]


# ---------- Budget ----------
def load_budget():
    """Return the saved monthly budget, or None if not set."""
    if not os.path.exists(BUDGET_FILE):
        return None
    try:
        with open(BUDGET_FILE) as f:
            return float(f.read().strip())
    except ValueError:
        return None


def set_budget():
    current = load_budget()
    if current:
        print(f"Current monthly budget: Rs {current:.2f}")
    try:
        budget = float(input("Enter your monthly budget (Rs): "))
    except ValueError:
        print("Please enter a valid number.\n")
        return
    if budget <= 0:
        print("Budget must be greater than 0.\n")
        return
    with open(BUDGET_FILE, "w") as f:
        f.write(str(budget))
    print(f"Monthly budget set to Rs {budget:.2f}\n")


# ---------- Adding expenses ----------
def add_expense():
    try:
        amount = float(input("Amount (Rs): "))
    except ValueError:
        print("Please enter a valid number.\n")
        return
    if amount <= 0:
        print("Amount must be greater than 0.\n")
        return

    for number, name in enumerate(CATEGORIES, start=1):
        print(f"  {number}. {name}")
    choice = input("Choose category number: ")
    if not choice.isdigit() or not 1 <= int(choice) <= len(CATEGORIES):
        print("Invalid category.\n")
        return

    category = CATEGORIES[int(choice) - 1]
    note = input("Note (optional): ")

    row = pd.DataFrame(
        [[date.today(), amount, category, note]],
        columns=["date", "amount", "category", "note"],
    )
    row.to_csv(FILE, mode="a", header=not os.path.exists(FILE), index=False)
    print("Expense saved!\n")


# ---------- Loading and choosing a month ----------
def load_data():
    """Load all expenses. Returns None if there is no data."""
    if not os.path.exists(FILE):
        print("No expenses yet. Add one first.\n")
        return None
    df = pd.read_csv(FILE, parse_dates=["date"])
    if df.empty:
        print("No expenses yet. Add one first.\n")
        return None
    df["month"] = df["date"].dt.strftime("%Y-%m")
    return df


def pick_month(df):
    """Show the months that have data and let the user choose one.
    Returns (month, list_of_all_months) or (None, None)."""
    months = sorted(df["month"].unique(), reverse=True)  # newest first
    print("\nMonths with expenses:")
    for number, m in enumerate(months, start=1):
        print(f"  {number}. {m}")

    choice = input("Choose a number (press Enter for the latest): ").strip()
    if choice == "":
        return months[0], months
    if choice.isdigit() and 1 <= int(choice) <= len(months):
        return months[int(choice) - 1], months
    print("Invalid choice.\n")
    return None, None


# ---------- Report ----------
def monthly_report():
    df = load_data()
    if df is None:
        return
    month, months = pick_month(df)
    if month is None:
        return

    month_df = df[df["month"] == month]
    total = month_df["amount"].sum()
    by_category = month_df.groupby("category")["amount"].sum().sort_values(ascending=False)

    print(f"\n--- Report for {month} ---")
    print(f"Total spent: Rs {total:.2f}")

    # Budget status
    budget = load_budget()
    if budget is None:
        print("Budget: not set (use option 5 to set one)")
    elif total > budget:
        print(f"Budget: Rs {budget:.2f}  -> OVER by Rs {total - budget:.2f}!")
    else:
        print(f"Budget: Rs {budget:.2f}  -> Remaining Rs {budget - total:.2f}")

    # Comparison with the previous month that has data
    position = months.index(month)
    if position + 1 < len(months):
        prev_month = months[position + 1]
        prev_total = df[df["month"] == prev_month]["amount"].sum()
        change = total - prev_total
        direction = "more" if change > 0 else "less"
        print(f"Previous month ({prev_month}): Rs {prev_total:.2f}  "
              f"-> you spent Rs {abs(change):.2f} {direction} this month")

    print("\nSpending by category:")
    print(by_category.to_string())
    print(f"\nHighest spending category: {by_category.index[0]} (Rs {by_category.iloc[0]:.2f})\n")


# ---------- View all expenses of a month ----------
def view_expenses():
    df = load_data()
    if df is None:
        return
    month, _ = pick_month(df)
    if month is None:
        return

    month_df = df[df["month"] == month].sort_values("date")
    view = month_df[["date", "amount", "category", "note"]].copy()
    view["date"] = view["date"].dt.strftime("%Y-%m-%d")

    print(f"\n--- All expenses in {month} ---")
    print(view.to_string(index=False))
    print(f"\nTotal: Rs {month_df['amount'].sum():.2f}  ({len(month_df)} expenses)\n")


# ---------- Charts ----------
def show_charts():
    df = load_data()
    if df is None:
        return
    month, _ = pick_month(df)
    if month is None:
        return

    by_category = df[df["month"] == month].groupby("category")["amount"].sum()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
    ax1.pie(by_category.values, labels=by_category.index, autopct="%1.1f%%")
    ax1.set_title(f"Spending share - {month}")

    ax2.bar(by_category.index, by_category.values, color="steelblue")
    ax2.set_title("Total per category")
    ax2.set_ylabel("Amount (Rs)")

    plt.tight_layout()
    plt.show()


# ---------- Menu ----------
def main():
    while True:
        print("1. Add expense")
        print("2. Monthly report")
        print("3. Show charts")
        print("4. View expenses of a month")
        print("5. Set monthly budget")
        print("6. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            monthly_report()
        elif choice == "3":
            show_charts()
        elif choice == "4":
            view_expenses()
        elif choice == "5":
            set_budget()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Please choose 1-6.\n")


if __name__ == "__main__":
    main()
