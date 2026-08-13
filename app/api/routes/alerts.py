from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.api import deps
from app.models.alert import Alert
from app.schemas.alert import AlertOut
from app.schemas.common import MessageOut
from app.services.alert_service import refresh_all_alerts

router = APIRouter()


def _alert_query(db: Session):
    return db.query(Alert).options(joinedload(Alert.budget))


def _to_out(alert: Alert) -> AlertOut:
    out = AlertOut.model_validate(alert)
    out.budget_name = alert.budget.name if alert.budget else None
    category = alert.budget.category if alert.budget else None
    out.category_name = category.name if category else None
    return out


@router.get("", response_model=list[AlertOut])
def list_alerts(
    unread_only: bool = False,
    db: Session = Depends(deps.get_db),
):
    query = _alert_query(db)
    if unread_only:
        query = query.filter(Alert.is_read.is_(False))
    alerts = query.order_by(Alert.created_at.desc(), Alert.id.desc()).all()
    return [_to_out(a) for a in alerts]


@router.get("/unread-count")
def unread_count(db: Session = Depends(deps.get_db)):
    count = (
        db.query(Alert).filter(Alert.is_read.is_(False)).count()
    )
    return {"count": count}


@router.post("/check", response_model=MessageOut)
def check_alerts(db: Session = Depends(deps.get_db)):
    checked = refresh_all_alerts(db)
    return {"message": f"Đã kiểm tra {checked} hạn mức"}


@router.put("/{alert_id}/read", response_model=AlertOut)
def mark_read(alert_id: int, db: Session = Depends(deps.get_db)):
    alert = db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Không tìm thấy cảnh báo")
    alert.is_read = True
    db.commit()
    db.refresh(alert)
    return _to_out(alert)


@router.put("/read-all", response_model=MessageOut)
def mark_all_read(db: Session = Depends(deps.get_db)):
    updated = (
        db.query(Alert)
        .filter(Alert.is_read.is_(False))
        .update({Alert.is_read: True})
    )
    db.commit()
    return {"message": f"Đã đánh dấu {updated} cảnh báo là đã đọc"}
