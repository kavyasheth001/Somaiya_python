from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from models.models import UserRole
from schemas.schemas import AuthRequest, RegisterRequest, UserResponse
from services.auth_service import AuthService


router = APIRouter(prefix="/api/auth", tags=["auth"])


def _user_payload(user) -> dict:
    return UserResponse.model_validate(user).model_dump(mode="json", by_alias=True)


@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = AuthService(db).register(
            name=request.name,
            email=request.email,
            password=request.password,
            role=request.role,
            department=request.department,
        )
        return {"message": "User registered successfully", "user": _user_payload(user)}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@router.post("/login")
def login(request: AuthRequest, db: Session = Depends(get_db)):
    try:
        user = AuthService(db).login(email=request.email, password=request.password)
        return {
            "message": "Login successful",
            "user": _user_payload(user),
            "token": f"mock-jwt-token-{user.id}",
        }
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@router.get("/users")
def get_all_users(role: str | None = None, db: Session = Depends(get_db)):
    try:
        svc = AuthService(db)
        if role:
            users = svc.get_all_users_by_role(UserRole(role.upper()))
        else:
            users = svc.get_all_users()
        return [UserResponse.model_validate(u).model_dump(mode="json", by_alias=True) for u in users]
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@router.get("/user/{userId}")
def get_user(userId: str, db: Session = Depends(get_db)):
    try:
        user = AuthService(db).get_user_by_id(uuid.UUID(userId))
        return _user_payload(user)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

