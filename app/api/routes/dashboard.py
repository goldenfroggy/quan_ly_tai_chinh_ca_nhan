from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.api import deps
from app.models.alert import Alert
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.schemas.alert import AlertOut
from app.services.budget_service import enrich_budget

router = APIRouter()


@router.get("/summary")
def summary(db: Session = Depends(deps.get_db)):
    today = date.today()
    month_start = today.replace(day=1)

    def _total(start: date, end: date, txn_type: str) -> float:
        value = (
            db.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.type == txn_type,
                Transaction.transaction_date >= start,
                Transaction.transaction_date <= end,
            )
            .scalar()
        )
        return round(float(value), 2)

    month_income = _total(month_start, today, "income")
    month_expense = _total(month_start, today, "expense")

    budgets = [
        enrich_budget(db, b)
        for b in db.query(Budget)
        .options(joinedload(Budget.category))
        .filter(Budget.is_active.is_(True))
        .order_by(Budget.id)
        .all()
    ]

    recent_transactions = (
        db.query(Transaction)
        .options(joinedload(Transaction.category))
        .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
        .limit(5)
        .all()
    )

    recent_alerts = (
        db.query(Alert)
        .options(joinedload(Alert.budget))
        .order_by(Alert.created_at.desc(), Alert.id.desc())
        .limit(5)
        .all()
    )
    unread_alerts = db.query(Alert).filter(Alert.is_read.is_(False)).count()

    return {
        "month": f"{today.year:04d}-{today.month:02d}",
        "income": month_income,
        "expense": month_expense,
        "balance": round(month_income - month_expense, 2),
        "budgets": budgets,
        "recent_transactions": recent_transactions,
        "recent_alerts": [AlertOut.model_validate(a) for a in recent_alerts],
        "unread_alerts": unread_alerts,
    }
