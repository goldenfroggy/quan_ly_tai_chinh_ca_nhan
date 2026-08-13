from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TransactionType
from app.schemas.category import CategoryOut


class TransactionCreate(BaseModel):
    type: TransactionType
    amount: float = Field(..., gt=0)
    category_id: int
    note: str | None = Field(None, max_length=255)
    transaction_date: date = Field(default_factory=date.today)


class TransactionUpdate(BaseModel):
    type: TransactionType | None = None
    amount: float | None = Field(None, gt=0)
    category_id: int | None = None
    note: str | None = Field(None, max_length=255)
    transaction_date: date | None = None


class TransactionOut(BaseModel):
    id: int
    type: TransactionType
    amount: float
    category_id: int
    note: str | None
    transaction_date: date
    created_at: datetime
    category: CategoryOut | None = None

    model_config = ConfigDict(from_attributes=True)
