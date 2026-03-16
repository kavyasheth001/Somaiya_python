from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from models.models import NotificationType
from schemas.schemas import NotificationResponse
from services.notification_service import NotificationService


router = APIRouter(prefix="/api/notifications", tags=["notifications"])


def _notif_payload(n) -> dict:
    return NotificationResponse.model_validate(n).model_dump(mode="json", by_alias=True)


@router.get("")
def get_notifications(
    userId: str = Query(...),
    type: str | None = Query(default=None),
    unreadOnly: bool | None = Query(default=None),
    db: Session = Depends(get_db),
):
    try:
        svc = NotificationService(db)
        uid = uuid.UUID(userId)
        if unreadOnly:
            notes = svc.get_unread_notifications_by_user(uid)
        elif type:
            notes = svc.get_notifications_by_type(uid, NotificationType(type))
        else:
            notes = svc.get_notifications_by_user(uid)
        return [_notif_payload(n) for n in notes]
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@router.put("/{id}/read")
def mark_read(id: str, db: Session = Depends(get_db)):
    try:
        n = NotificationService(db).mark_as_read(uuid.UUID(id))
        return {"message": "Notification marked as read", "notification": _notif_payload(n)}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

