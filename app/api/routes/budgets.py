from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api import deps
from app.models.budget import Budget
from app.models.category import Category
from app.schemas.budget import BudgetCreate, BudgetOut, BudgetUpdate
from app.schemas.common import MessageOut
from app.services.budget_service import enrich_budget
from app.services.alert_service import refresh_all_alerts

router = APIRouter()


def _get_budget_or_404(db: Session, budget_id: int) -> Budget:
    budget = (
        db.query(Budget)
        .options(joinedload(Budget.category))
        .filter(Budget.id == budget_id)
        .first()
    )
    if not budget:
        raise HTTPException(status_code=404, detail="Không tìm thấy hạn mức")
    return budget


def _validate_category(db: Session, category_id: int | None) -> None:
    if category_id is not None and not db.get(Category, category_id):
        raise HTTPException(status_code=400, detail="Danh mục không tồn tại")


@router.get("", response_model=list[BudgetOut])
def list_budgets(
    active_only: bool = False, db: Session = Depends(deps.get_db)
):
    query = db.query(Budget).options(joinedload(Budget.category))
    if active_only:
        query = query.filter(Budget.is_active.is_(True))
    budgets = query.order_by(Budget.id).all()
    return [enrich_budget(db, b) for b in budgets]


@router.post("", response_model=BudgetOut, status_code=status.HTTP_201_CREATED)
def create_budget(payload: BudgetCreate, db: Session = Depends(deps.get_db)):
    _validate_category(db, payload.category_id)
    budget = Budget(**payload.model_dump())
    db.add(budget)
    db.commit()
    db.refresh(budget)
    refresh_all_alerts(db)
    return enrich_budget(db, budget)


@router.get("/{budget_id}", response_model=BudgetOut)
def get_budget(budget_id: int, db: Session = Depends(deps.get_db)):
    _get_budget_or_404(db, budget_id)
    return enrich_budget(db, _get_budget_or_404(db, budget_id))


@router.put("/{budget_id}", response_model=BudgetOut)
def update_budget(
    budget_id: int,
    payload: BudgetUpdate,
    db: Session = Depends(deps.get_db),
):
    budget = _get_budget_or_404(db, budget_id)
    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data:
        _validate_category(db, data["category_id"])
    for field, value in data.items():
        setattr(budget, field, value)
    db.commit()
    db.refresh(budget)
    refresh_all_alerts(db)
    return enrich_budget(db, budget)


@router.delete("/{budget_id}", response_model=MessageOut)
def delete_budget(budget_id: int, db: Session = Depends(deps.get_db)):
    budget = _get_budget_or_404(db, budget_id)
    db.delete(budget)
    db.commit()
    return {"message": "Đã xóa hạn mức"}
