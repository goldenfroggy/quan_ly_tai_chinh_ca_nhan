from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.budget import Budget
from app.models.enums import BudgetPeriod
from app.models.transaction import Transaction


def period_key(budget: Budget, now: date | None = None) -> str:
    now = now or date.today()
    if budget.period == BudgetPeriod.yearly:
        return f"year-{now.year}"
    return f"month-{now.year:04d}-{now.month:02d}"


def current_period_range(budget: Budget, now: date | None = None) -> tuple[date, date] | None:
    now = now or date.today()
    if budget.end_date and budget.end_date < now:
        return None
    if budget.start_date > now:
        return None

    if budget.period == BudgetPeriod.yearly:
        start = date(now.year, 1, 1)
        end = date(now.year, 12, 31)
    else:
        start = date(now.year, now.month, 1)
        end = (
            date(now.year + 1, 1, 1) - timedelta(days=1)
            if now.month == 12
            else date(now.year, now.month + 1, 1) - timedelta(days=1)
        )

    if budget.start_date > start:
        start = budget.start_date
    if budget.end_date and budget.end_date < end:
        end = budget.end_date
    if start > end:
        return None
    return start, end


def budget_spending(db: Session, budget: Budget, start: date, end: date) -> float:
    query = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.type == "expense",
        Transaction.transaction_date >= start,
        Transaction.transaction_date <= end,
    )
    if budget.category_id is not None:
        query = query.filter(Transaction.category_id == budget.category_id)
    return float(query.scalar())


def enrich_budget(db: Session, budget: Budget) -> dict:
    from app.schemas.budget import BudgetOut

    data = BudgetOut.model_validate(budget).model_dump()
    period_range = current_period_range(budget)
    if period_range is None or not budget.is_active:
        data["spent"] = 0.0
        data["percentage"] = 0.0
        data["remaining"] = float(budget.amount)
        return data

    start, end = period_range
    spent = budget_spending(db, budget, start, end)
    amount = float(budget.amount)
    data["spent"] = round(spent, 2)
    data["percentage"] = round(spent / amount * 100, 2) if amount else 0.0
    data["remaining"] = round(amount - spent, 2)
    data["period_key"] = period_key(budget)
    return data
