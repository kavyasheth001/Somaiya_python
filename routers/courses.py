from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from schemas.schemas import CourseRequest, CourseResponse
from services.course_service import CourseService


router = APIRouter(prefix="/api/courses", tags=["courses"])


def _course_payload(course) -> dict:
    return CourseResponse.model_validate(course).model_dump(mode="json", by_alias=True)


@router.get("")
def get_all_courses(db: Session = Depends(get_db)):
    try:
        courses = CourseService(db).get_all_courses()
        return [_course_payload(c) for c in courses]
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@router.post("")
def create_course(request: CourseRequest, db: Session = Depends(get_db)):
    try:
        course = CourseService(db).create_course(
            name=request.name,
            subject_code=request.subjectCode,
            teacher_id=request.teacherId,
            student_ids=request.studentIds,
        )
        return {"message": "Course created successfully", "course": _course_payload(course)}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@router.get("/teacher/{teacherId}")
def get_courses_by_teacher(teacherId: str, db: Session = Depends(get_db)):
    try:
        courses = CourseService(db).get_courses_by_teacher(uuid.UUID(teacherId))
        return [_course_payload(c) for c in courses]
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@router.get("/student/{studentId}")
def get_courses_by_student(studentId: str, db: Session = Depends(get_db)):
    try:
        courses = CourseService(db).get_courses_by_student(uuid.UUID(studentId))
        return [_course_payload(c) for c in courses]
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

