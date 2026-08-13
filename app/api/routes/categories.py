from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api import deps
from app.models.category import Category
from app.models.enums import TransactionType
from app.models.transaction import Transaction
from app.schemas.category import (
    CategoryCreate,
    CategoryOut,
    CategoryUpdate,
)

router = APIRouter()


@router.get("", response_model=list[CategoryOut])
def list_categories(
    type: TransactionType | None = None,
    db: Session = Depends(deps.get_db),
):
    query = db.query(Category).order_by(Category.type, Category.id)
    if type is not None:
        query = query.filter(Category.type == type.value)
    return query.all()


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(deps.get_db)):
    exists = (
        db.query(Category)
        .filter(Category.name == payload.name, Category.type == payload.type.value)
        .first()
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Danh mục với tên này đã tồn tại",
        )
    category = Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(deps.get_db)):
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Không tìm thấy danh mục")
    return category


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(deps.get_db),
):
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Không tìm thấy danh mục")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(deps.get_db)):
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Không tìm thấy danh mục")
    in_use = (
        db.query(Transaction)
        .filter(Transaction.category_id == category_id)
        .count()
    )
    if in_use:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Danh mục đang được sử dụng bởi giao dịch, không thể xóa",
        )
    db.delete(category)
    db.commit()
    return {"message": "Đã xóa danh mục"}
