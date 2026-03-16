from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from schemas.schemas import AttendanceRequest, AttendanceResponse
from services.attendance_service import AttendanceService


router = APIRouter(prefix="/api/attendance", tags=["attendance"])


def _attendance_payload(a) -> dict:
    return AttendanceResponse.model_validate(a).model_dump(mode="json", by_alias=True)


@router.post("/mark")
def mark_attendance(request: AttendanceRequest, db: Session = Depends(get_db)):
    try:
        records = [(r.studentId, r.status) for r in request.attendanceRecords]
        saved = AttendanceService(db).mark_attendance(
            course_id=request.courseId,
            lecture_date=request.lectureDate,
            lecture_topic=request.lectureTopic,
            records=records,
        )
        return {"message": "Attendance marked successfully", "records": [_attendance_payload(x) for x in saved]}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@router.get("")
def get_attendance(
    courseId: str | None = Query(default=None),
    studentId: str | None = Query(default=None),
    date: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    try:
        svc = AttendanceService(db)
        if courseId and date:
            items = svc.get_attendance_by_course_and_date(uuid.UUID(courseId), date)
        elif courseId:
            items = svc.get_attendance_by_course(uuid.UUID(courseId))
        elif studentId:
            items = svc.get_attendance_by_student(uuid.UUID(studentId))
        else:
            raise ValueError("Please provide courseId, studentId, or both courseId and date")
        return [_attendance_payload(x) for x in items]
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

