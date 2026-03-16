from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, joinedload

from models.models import Notification, NotificationType, User


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def get_notifications_by_user(self, user_id: uuid.UUID) -> list[Notification]:
        user = self.db.get(User, user_id)
        if user is None:
            raise ValueError("User not found")
        q = (
            select(Notification)
            .where(Notification.recipient_id == user_id)
            .options(joinedload(Notification.recipient))
            .order_by(Notification.created_at.desc())
        )
        return list(self.db.scalars(q).unique())

    def get_unread_notifications_by_user(self, user_id: uuid.UUID) -> list[Notification]:
        user = self.db.get(User, user_id)
        if user is None:
            raise ValueError("User not found")
        q = (
            select(Notification)
            .where(Notification.recipient_id == user_id, Notification.is_read.is_(False))
            .options(joinedload(Notification.recipient))
            .order_by(Notification.created_at.desc())
        )
        return list(self.db.scalars(q).unique())

    def get_notifications_by_type(self, user_id: uuid.UUID, ntype: NotificationType) -> list[Notification]:
        user = self.db.get(User, user_id)
        if user is None:
            raise ValueError("User not found")
        q = (
            select(Notification)
            .where(Notification.recipient_id == user_id, Notification.type == ntype)
            .options(joinedload(Notification.recipient))
            .order_by(Notification.created_at.desc())
        )
        return list(self.db.scalars(q).unique())

    def get_unread_notification_count(self, user_id: uuid.UUID) -> int:
        user = self.db.get(User, user_id)
        if user is None:
            raise ValueError("User not found")
        count = self.db.scalar(
            select(func.count()).select_from(Notification).where(Notification.recipient_id == user_id, Notification.is_read.is_(False))
        )
        return int(count or 0)

    def mark_as_read(self, notification_id: uuid.UUID) -> Notification:
        n = self.db.get(Notification, notification_id)
        if n is None:
            raise ValueError("Notification not found")
        n.is_read = True
        self.db.commit()
        self.db.refresh(n)
        return n

    def mark_all_as_read(self, user_id: uuid.UUID) -> None:
        user = self.db.get(User, user_id)
        if user is None:
            raise ValueError("User not found")
        self.db.execute(
            update(Notification)
            .where(Notification.recipient_id == user_id, Notification.is_read.is_(False))
            .values(is_read=True)
        )
        self.db.commit()

    def get_notifications_since(self, user_id: uuid.UUID, since: datetime) -> list[Notification]:
        user = self.db.get(User, user_id)
        if user is None:
            raise ValueError("User not found")
        q = (
            select(Notification)
            .where(Notification.recipient_id == user_id, Notification.created_at > since)
            .options(joinedload(Notification.recipient))
            .order_by(Notification.created_at.desc())
        )
        return list(self.db.scalars(q).unique())

