"""Tools the AI agent may call. Plain Python functions with clear docstrings.

The model reads each function's name, type hints and docstring to decide
when to call it - so write them carefully.

NOTE: employee data lives in memory (loaded from data/employees.json), so
changes reset when the app restarts. That is fine for a demo; a real system
would use a database.
"""
import json
from datetime import date, datetime, timedelta

from src import config
from src.rag import format_context, retrieve

LEAVE_TYPES = ("annual", "sick", "casual")
_employees: dict | None = None


def _db() -> dict:
    global _employees
    if _employees is None:
        _employees = json.loads(config.EMPLOYEES_FILE.read_text(encoding="utf-8"))
    return _employees


def reset_state() -> None:
    """Reload employee data from disk (used by tests)."""
    global _employees
    _employees = None


def count_weekdays(start: date, end: date) -> int:
    days, d = 0, start
    while d <= end:
        if d.weekday() < 5:  # Mon-Fri
            days += 1
        d += timedelta(days=1)
    return days


def search_policies(query: str) -> str:
    """Search the company policy documents (leave, work from home, expenses,
    IT security, holidays, general HR). Use this for ANY question about
    company rules. Returns policy excerpts with their source file names.

    Args:
        query: Short search query describing what to look up.
    """
    results = retrieve(query)
    if not results:
        return "NO_RELEVANT_POLICY_FOUND"
    return format_context(results)


def check_leave_balance(employee_id: str) -> dict:
    """Get the remaining leave days (annual, sick, casual) for an employee.

    Args:
        employee_id: The employee ID, for example E101.
    """
    emp = _db().get(employee_id.strip().upper())
    if not emp:
        return {"status": "error", "message": f"Employee {employee_id} not found."}
    return {"status": "ok", "name": emp["name"], "balance_days": emp["leave_balance"]}


def apply_leave(employee_id: str, leave_type: str, start_date: str,
                end_date: str, reason: str) -> dict:
    """Submit a leave request. Only call this after the employee has clearly
    given the leave type and dates.

    Args:
        employee_id: The employee ID, for example E101.
        leave_type: One of 'annual', 'sick' or 'casual'.
        start_date: First day of leave, format YYYY-MM-DD.
        end_date: Last day of leave, format YYYY-MM-DD.
        reason: Short reason for the leave.
    """
    emp = _db().get(employee_id.strip().upper())
    if not emp:
        return {"status": "error", "message": f"Employee {employee_id} not found."}

    leave_type = leave_type.strip().lower()
    if leave_type not in LEAVE_TYPES:
        return {"status": "error", "message": f"leave_type must be one of {LEAVE_TYPES}."}

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return {"status": "error", "message": "Dates must be in YYYY-MM-DD format."}

    if end < start:
        return {"status": "error", "message": "end_date cannot be before start_date."}
    if start < date.today() and leave_type != "sick":
        return {"status": "error", "message": "Only sick leave can be applied for past dates."}

    days = count_weekdays(start, end)
    if days == 0:
        return {"status": "error", "message": "Those dates have no working days."}

    available = emp["leave_balance"][leave_type]
    if days > available:
        return {"status": "error",
                "message": f"Not enough {leave_type} leave: need {days}, have {available}."}

    emp["leave_balance"][leave_type] = available - days
    return {
        "status": "submitted",
        "days": days,
        "leave_type": leave_type,
        "from": start_date,
        "to": end_date,
        "reason": reason,
        "remaining_balance": emp["leave_balance"][leave_type],
        "note": "Pending manager approval (usually within 2 working days).",
    }
