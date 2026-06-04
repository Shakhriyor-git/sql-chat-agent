import sqlite3
from src.config import DB_PATH


SCHEMA_DESCRIPTION = """
Table: borrowers (149,717 rows of credit risk data)

Columns:
  borrower_id (INTEGER) - unique ID for each borrower
  is_default (INTEGER) - 1 if borrower defaulted within 2 years, 0 otherwise
  credit_utilization (REAL) - ratio of credit used vs available (0 to 1+)
  age (INTEGER) - age of borrower in years
  past_due_30_59 (INTEGER) - number of times 30-59 days past due
  debt_ratio (REAL) - monthly debt payments / monthly income
  monthly_income (REAL) - monthly income in dollars
  open_credit_lines (INTEGER) - number of open loans/credit lines
  past_due_90 (INTEGER) - number of times 90+ days past due
  real_estate_loans (INTEGER) - number of mortgage/real estate loans
  past_due_60_89 (INTEGER) - number of times 60-89 days past due
  num_dependents (INTEGER) - number of dependents
  income_was_missing (INTEGER) - 1 if income data was originally missing, 0 otherwise
"""


def run_query(query: str) -> str:
    """Execute a read-only SELECT query and return results as a string."""
    cleaned = query.strip().lower()

    # Security: only SELECT
    if not cleaned.startswith("select"):
        return "Error: Only SELECT queries are allowed."

    # Security: block dangerous keywords
    forbidden = ["drop", "delete", "update", "insert", "alter", "create"]
    if any(word in cleaned for word in forbidden):
        return "Error: Query contains forbidden keywords."

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        conn.close()

        if len(rows) > 50:
            return f"Columns: {col_names}\nRows (showing 50 of {len(rows)}): {rows[:50]}"
        return f"Columns: {col_names}\nRows: {rows}"

    except Exception as e:
        return f"Error executing query: {str(e)}"