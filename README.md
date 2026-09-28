# Personal Expense Tracker

A menu-driven command-line application to record and analyse personal expenses, built with **Python** and **SQLite**.

## Features
- Add, view, update, delete and search expense records
- SQLite database with amount, category, date and description
- SQL queries (`SUM`, `COUNT`, `GROUP BY`, `LIKE`, `strftime`) for total spending, category-wise spending and a monthly summary
- Input validation (positive amounts, valid dates, numeric IDs) and error handling

## Run
```bash
python expense_tracker.py
```
Requires Python 3.8+. No extra packages needed (`sqlite3` ships with Python). The database file `expenses.db` is created automatically on first run.

## Database schema
| Column | Type | Notes |
|---|---|---|
| id | INTEGER | Primary key, auto-increment |
| amount | REAL | Must be greater than 0 |
| category | TEXT | e.g. Food, Travel, Bills |
| date | TEXT | `YYYY-MM-DD` |
| description | TEXT | Optional |

## Possible improvements
- Export records to CSV
- Set a monthly budget and warn when it is exceeded
- Add a simple charts view
