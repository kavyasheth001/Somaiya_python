from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from schemas.schemas import CourseResponse
from services.assignment_service import AssignmentService
from services.attendance_service import AttendanceService
from services.course_service import CourseService
from services.performance_service import PerformanceService


router = APIRouter(prefix="/api/student", tags=["student"])


def _course_payload(course) -> dict:
    return CourseResponse.model_validate(course).model_dump(mode="json", by_alias=True)


@router.get("/dashboard")
def get_dashboard(studentId: str = Query(...), db: Session = Depends(get_db)):
    try:
        sid = uuid.UUID(studentId)
        courses = CourseService(db).get_courses_by_student(sid)
        active_subjects = len(courses)

        overall_attendance = 0.0
        if courses:
            total = 0.0
            count = 0
            att_svc = AttendanceService(db)
            for c in courses:
                try:
                    pct = att_svc.calculate_attendance_percentage(sid, c.id)
                    total += pct
                    count += 1
                except Exception:
                    pass
            overall_attendance = (total / count) if count > 0 else 0.0

        avg_grade = PerformanceService(db).get_average_by_student(sid) or 0.0

        pending_assignments = 0
        try:
            pending_assignments = len(AssignmentService(db).get_active_assignments_for_student(sid))
        except Exception:
            pending_assignments = 0

        def round1(x: float) -> float:
            return round(x * 10.0) / 10.0

        return {
            "activeSubjects": active_subjects,
            "overallAttendance": round1(overall_attendance),
            "avgGrade": round1(avg_grade),
            "pendingAssignments": pending_assignments,
            "courses": [_course_payload(c) for c in courses],
        }
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

