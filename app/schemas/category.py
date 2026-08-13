from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TransactionType


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: TransactionType
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, max_length=20)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, max_length=20)


class CategoryOut(CategoryBase):
    id: int
    is_default: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
