from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BudgetPeriod
from app.schemas.category import CategoryOut


class BudgetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category_id: int | None = None
    amount: float = Field(..., gt=0)
    period: BudgetPeriod = BudgetPeriod.monthly
    alert_threshold: int = Field(80, ge=1, le=100)
    start_date: date = Field(default_factory=date.today)
    end_date: date | None = None
    is_active: bool = True


class BudgetUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    category_id: int | None = None
    amount: float | None = Field(None, gt=0)
    period: BudgetPeriod | None = None
    alert_threshold: int | None = Field(None, ge=1, le=100)
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None


class BudgetOut(BaseModel):
    id: int
    name: str
    category_id: int | None
    amount: float
    period: BudgetPeriod
    alert_threshold: int
    start_date: date
    end_date: date | None
    is_active: bool
    created_at: datetime
    spent: float = 0.0
    percentage: float = 0.0
    remaining: float = 0.0
    period_key: str | None = None
    category: CategoryOut | None = None

    model_config = ConfigDict(from_attributes=True)
