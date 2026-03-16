from __future__ import annotations

import uuid

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import User, UserRole


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(
        self,
        *,
        name: str,
        email: str,
        password: str,
        role: UserRole,
        department: str | None,
    ) -> User:
        existing = self.db.scalar(select(User).where(User.email == email))
        if existing is not None:
            raise ValueError(f"User with email {email} already exists")

        user = User(
            name=name,
            email=email,
            password=pwd_context.hash(password),
            role=role,
            department=department,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def login(self, *, email: str, password: str) -> User:
        user = self.db.scalar(select(User).where(User.email == email))
        if user is None or not pwd_context.verify(password, user.password):
            raise ValueError("Invalid email or password")
        return user

    def get_user_by_id(self, user_id: uuid.UUID) -> User:
        user = self.db.get(User, user_id)
        if user is None:
            raise ValueError("User not found")
        return user

    def get_all_users(self) -> list[User]:
        return list(self.db.scalars(select(User).order_by(User.created_at.asc())))

    def get_all_users_by_role(self, role: UserRole) -> list[User]:
        return list(self.db.scalars(select(User).where(User.role == role).order_by(User.created_at.asc())))

