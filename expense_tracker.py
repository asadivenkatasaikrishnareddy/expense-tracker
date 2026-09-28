"""
Personal Expense Tracker
Python + SQLite (built-in sqlite3 module, no installs needed)

Features
  1. Add, view, update, delete and search expense records
  2. Total spending and category-wise totals using SQL queries
  3. Monthly spending summary
  4. Input validation and error handling
"""

import os
import sqlite3
from datetime import datetime

# Keep the database file next to this script, wherever it is run from
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expenses.db")


# ---------------------------------------------------------------- database
def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    """Create the expenses table if it does not exist yet."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                amount      REAL    NOT NULL CHECK (amount > 0),
                category    TEXT    NOT NULL,
                date        TEXT    NOT NULL,      -- stored as YYYY-MM-DD
                description TEXT
            )
            """
        )


# ------------------------------------------------------- input validation
def read_amount(prompt="Amount: "):
    """Keep asking until the user types a positive number."""
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
            if value <= 0:
                print("  Amount must be greater than 0.")
                continue
            return round(value, 2)
        except ValueError:
            print("  Please enter a valid number, e.g. 250 or 99.50")


def read_date(prompt="Date (YYYY-MM-DD, Enter = today): "):
    """Validate the date format; blank input means today."""
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return datetime.now().strftime("%Y-%m-%d")
        try:
            return datetime.strptime(raw, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            print("  Invalid date. Use the format YYYY-MM-DD, e.g. 2026-09-28")


def read_text(prompt, required=True):
    while True:
        raw = input(prompt).strip()
        if raw or not required:
            return raw
        print("  This field cannot be empty.")


def read_id(prompt="Expense ID: "):
    while True:
        raw = input(prompt).strip()
        if raw.isdigit():
            return int(raw)
        print("  Please enter a valid numeric ID.")


def expense_exists(conn, expense_id):
    row = conn.execute("SELECT 1 FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    return row is not None


# --------------------------------------------------------------- display
def print_rows(rows):
    if not rows:
        print("  No records found.")
        return
    print(f"\n  {'ID':<5}{'Date':<12}{'Category':<14}{'Amount':>10}  Description")
    print("  " + "-" * 60)
    for row_id, amount, category, date, description in rows:
        print(f"  {row_id:<5}{date:<12}{category:<14}{amount:>10.2f}  {description or ''}")


# ------------------------------------------------------------- operations
def add_expense():
    amount = read_amount()
    category = read_text("Category (Food, Travel, Bills...): ").title()
    date = read_date()
    description = read_text("Description (optional): ", required=False)
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO expenses (amount, category, date, description) VALUES (?, ?, ?, ?)",
            (amount, category, date, description),
        )
    print("  Expense added.")


def view_expenses():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, amount, category, date, description FROM expenses "
            "ORDER BY date DESC, id DESC"
        ).fetchall()
    print_rows(rows)


def update_expense():
    expense_id = read_id("ID of the expense to update: ")
    with get_connection() as conn:
        if not expense_exists(conn, expense_id):
            print("  No expense with that ID.")
            return
        print("  Enter the new values.")
        amount = read_amount()
        category = read_text("Category: ").title()
        date = read_date()
        description = read_text("Description (optional): ", required=False)
        conn.execute(
            "UPDATE expenses SET amount = ?, category = ?, date = ?, description = ? "
            "WHERE id = ?",
            (amount, category, date, description, expense_id),
        )
    print("  Expense updated.")


def delete_expense():
    expense_id = read_id("ID of the expense to delete: ")
    with get_connection() as conn:
        if not expense_exists(conn, expense_id):
            print("  No expense with that ID.")
            return
        confirm = input("  Delete this record? (y/n): ").strip().lower()
        if confirm != "y":
            print("  Cancelled.")
            return
        conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    print("  Expense deleted.")


def search_expenses():
    keyword = read_text("Search by category or description: ")
    pattern = f"%{keyword}%"
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, amount, category, date, description FROM expenses "
            "WHERE category LIKE ? OR description LIKE ? "
            "ORDER BY date DESC",
            (pattern, pattern),
        ).fetchall()
    print_rows(rows)


def total_spending():
    with get_connection() as conn:
        total, count = conn.execute(
            "SELECT COALESCE(SUM(amount), 0), COUNT(*) FROM expenses"
        ).fetchone()
    print(f"\n  Total spending: {total:.2f} across {count} expense(s)")


def category_summary():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT category, SUM(amount), COUNT(*) FROM expenses "
            "GROUP BY category ORDER BY SUM(amount) DESC"
        ).fetchall()
    if not rows:
        print("  No records found.")
        return
    print(f"\n  {'Category':<16}{'Total':>10}{'Count':>8}")
    print("  " + "-" * 34)
    for category, total, count in rows:
        print(f"  {category:<16}{total:>10.2f}{count:>8}")


def monthly_summary():
    month = input("Month (YYYY-MM, Enter = this month): ").strip()
    if month == "":
        month = datetime.now().strftime("%Y-%m")
    else:
        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            print("  Invalid month. Use the format YYYY-MM, e.g. 2026-09")
            return

    with get_connection() as conn:
        total, count = conn.execute(
            "SELECT COALESCE(SUM(amount), 0), COUNT(*) FROM expenses "
            "WHERE strftime('%Y-%m', date) = ?",
            (month,),
        ).fetchone()
        rows = conn.execute(
            "SELECT category, SUM(amount) FROM expenses "
            "WHERE strftime('%Y-%m', date) = ? "
            "GROUP BY category ORDER BY SUM(amount) DESC",
            (month,),
        ).fetchall()

    print(f"\n  Summary for {month}")
    print(f"  Total spent: {total:.2f} ({count} expense(s))")
    for category, amount in rows:
        share = amount / total * 100 if total else 0
        print(f"    {category:<14}{amount:>10.2f}  ({share:.0f}%)")
    if not rows:
        print("  No expenses recorded for this month.")


# ------------------------------------------------------------------- menu
MENU = """
===== Personal Expense Tracker =====
 1. Add expense
 2. View all expenses
 3. Update expense
 4. Delete expense
 5. Search expenses
 6. Total spending
 7. Category-wise spending
 8. Monthly summary
 0. Exit
"""

ACTIONS = {
    "1": add_expense,
    "2": view_expenses,
    "3": update_expense,
    "4": delete_expense,
    "5": search_expenses,
    "6": total_spending,
    "7": category_summary,
    "8": monthly_summary,
}


def main():
    init_db()
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        action = ACTIONS.get(choice)
        if action is None:
            print("  Invalid choice. Enter a number from 0 to 8.")
            continue
        try:
            action()
        except sqlite3.Error as error:
            print(f"  Database error: {error}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nExited.")
