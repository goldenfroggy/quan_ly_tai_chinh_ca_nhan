from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.services.budget_service import (
    budget_spending,
    current_period_range,
    period_key,
)


def _sync_budget_alerts(db: Session, budget: Budget) -> None:
    period_range = current_period_range(budget)
    if period_range is None:
        return

    start, end = period_range
    key = period_key(budget)
    spent = budget_spending(db, budget, start, end)

    db.query(Alert).filter(
        Alert.budget_id == budget.id,
        Alert.period != key,
    ).update({Alert.is_read: True}, synchronize_session=False)
    amount = float(budget.amount)
    pct = spent / amount if amount else 1.0

    desired: list[str] = []
    if pct >= 1.0:
        desired.append("danger")
    elif pct >= budget.alert_threshold / 100:
        desired.append("warning")

    existing = (
        db.query(Alert)
        .filter(Alert.budget_id == budget.id, Alert.period == key)
        .all()
    )

    for alert in existing:
        if alert.level not in desired:
            db.delete(alert)

    for level in desired:
        if not any(a.level == level for a in existing):
            if level == "danger":
                message = (
                    f"Đã vượt hạn mức '{budget.name}': "
                    f"đã chi {spent:,.0f} / {amount:,.0f} VNĐ ({pct * 100:.0f}%)"
                )
            else:
                message = (
                    f"Hạn mức '{budget.name}' sắp đạt ngưỡng: "
                    f"đã chi {spent:,.0f} / {amount:,.0f} VNĐ ({pct * 100:.0f}%)"
                )
            db.add(
                Alert(
                    budget_id=budget.id,
                    period=key,
                    level=level,
                    message=message,
                )
            )


def refresh_alerts_for_transaction(db: Session, txn: Transaction) -> None:
    budgets = (
        db.query(Budget)
        .filter(
            Budget.is_active.is_(True),
            (Budget.category_id == txn.category_id)
            | (Budget.category_id.is_(None)),
        )
        .all()
    )
    for budget in budgets:
        _sync_budget_alerts(db, budget)
    db.commit()


def refresh_all_alerts(db: Session) -> int:
    budgets = db.query(Budget).filter(Budget.is_active.is_(True)).all()
    for budget in budgets:
        _sync_budget_alerts(db, budget)
    db.commit()
    return len(budgets)
