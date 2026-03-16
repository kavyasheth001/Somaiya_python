from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from schemas.schemas import CourseResponse
from services.course_service import CourseService


router = APIRouter(prefix="/api/teacher", tags=["teacher"])


def _course_payload(course) -> dict:
    return CourseResponse.model_validate(course).model_dump(mode="json", by_alias=True)


@router.get("/dashboard")
def get_dashboard(teacherId: str = Query(...), db: Session = Depends(get_db)):
    try:
        classes = CourseService(db).get_courses_by_teacher(uuid.UUID(teacherId))

        classes_managed = len(classes)
        avg_attendance = 87.5
        avg_grade = 82.3

        return {
            "classesManaged": classes_managed,
            "avgAttendance": avg_attendance,
            "avgGrade": avg_grade,
            "classes": [_course_payload(c) for c in classes],
        }
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

