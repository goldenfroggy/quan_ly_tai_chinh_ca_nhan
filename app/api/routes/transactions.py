from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api import deps
from app.models.category import Category
from app.models.enums import TransactionType
from app.models.transaction import Transaction
from app.schemas.common import MessageOut, Page
from app.schemas.transaction import (
    TransactionCreate,
    TransactionOut,
    TransactionUpdate,
)
from app.services.alert_service import refresh_all_alerts

router = APIRouter()


def _get_transaction_or_404(db: Session, txn_id: int) -> Transaction:
    txn = (
        db.query(Transaction)
        .options(joinedload(Transaction.category))
        .filter(Transaction.id == txn_id)
        .first()
    )
    if not txn:
        raise HTTPException(status_code=404, detail="Không tìm thấy giao dịch")
    return txn


def _validate_category(db: Session, category_id: int) -> None:
    if not db.get(Category, category_id):
        raise HTTPException(status_code=400, detail="Danh mục không tồn tại")


@router.get("", response_model=Page[TransactionOut])
def list_transactions(
    type: TransactionType | None = None,
    category_id: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(deps.get_db),
):
    query = db.query(Transaction).options(joinedload(Transaction.category))
    if type is not None:
        query = query.filter(Transaction.type == type.value)
    if category_id is not None:
        query = query.filter(Transaction.category_id == category_id)
    if date_from:
        query = query.filter(Transaction.transaction_date >= date_from)
    if date_to:
        query = query.filter(Transaction.transaction_date <= date_to)

    total = query.count()
    items = (
        query.order_by(
            Transaction.transaction_date.desc(), Transaction.id.desc()
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    pages = (total + page_size - 1) // page_size if total else 0
    return Page(
        items=items, total=total, page=page, page_size=page_size, pages=pages
    )


@router.post("", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate, db: Session = Depends(deps.get_db)
):
    _validate_category(db, payload.category_id)
    txn = Transaction(**payload.model_dump())
    db.add(txn)
    db.commit()
    db.refresh(txn)
    refresh_all_alerts(db)
    return _get_transaction_or_404(db, txn.id)


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(transaction_id: int, db: Session = Depends(deps.get_db)):
    return _get_transaction_or_404(db, transaction_id)


@router.put("/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    db: Session = Depends(deps.get_db),
):
    txn = _get_transaction_or_404(db, transaction_id)
    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data:
        _validate_category(db, data["category_id"])
    for field, value in data.items():
        setattr(txn, field, value)
    db.commit()
    db.refresh(txn)
    refresh_all_alerts(db)
    return _get_transaction_or_404(db, txn.id)


@router.delete("/{transaction_id}", response_model=MessageOut)
def delete_transaction(transaction_id: int, db: Session = Depends(deps.get_db)):
    txn = _get_transaction_or_404(db, transaction_id)
    db.delete(txn)
    db.commit()
    refresh_all_alerts(db)
    return {"message": "Đã xóa giao dịch"}
