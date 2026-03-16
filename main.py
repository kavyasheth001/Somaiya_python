from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.data_initializer import initialize_sample_data
from database import Base, SessionLocal, engine
from routers.assignments import router as assignments_router
from routers.attendance import router as attendance_router
from routers.auth import router as auth_router
from routers.courses import router as courses_router
from routers.notifications import router as notifications_router
from routers.performance import router as performance_router
from routers.student import router as student_router
from routers.teacher import router as teacher_router


app = FastAPI(title="ClassConnect Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(courses_router)
app.include_router(assignments_router)
app.include_router(attendance_router)
app.include_router(performance_router)
app.include_router(notifications_router)
app.include_router(teacher_router)
app.include_router(student_router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        initialize_sample_data(db)

