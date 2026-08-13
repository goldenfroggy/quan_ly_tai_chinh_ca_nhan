from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import AlertLevel


class AlertOut(BaseModel):
    id: int
    budget_id: int
    period: str
    level: AlertLevel
    message: str
    is_read: bool
    created_at: datetime
    budget_name: str | None = None
    category_name: str | None = None

    model_config = ConfigDict(from_attributes=True)
