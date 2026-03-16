from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from schemas.schemas import AssignmentRequest, AssignmentResponse
from services.assignment_service import AssignmentService


router = APIRouter(prefix="/api/assignments", tags=["assignments"])


def _assignment_payload(a) -> dict:
    return AssignmentResponse.model_validate(a).model_dump(mode="json", by_alias=True)


@router.post("")
def create_assignment(request: AssignmentRequest, db: Session = Depends(get_db)):
    try:
        assignment = AssignmentService(db).create_assignment(
            title=request.title,
            description=request.description,
            subject=request.subject,
            due_date=request.dueDate,
            status=request.status,
            teacher_id=request.teacherId,
            course_id=request.courseId,
        )
        return {"message": "Assignment created successfully", "assignment": _assignment_payload(assignment)}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@router.get("")
def get_assignments(
    teacherId: str | None = Query(default=None),
    courseId: str | None = Query(default=None),
    studentId: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    try:
        svc = AssignmentService(db)
        if teacherId:
            assignments = svc.get_assignments_by_teacher(uuid.UUID(teacherId))
        elif courseId:
            assignments = svc.get_assignments_by_course(uuid.UUID(courseId))
        elif studentId:
            assignments = svc.get_active_assignments_for_student(uuid.UUID(studentId))
        else:
            assignments = svc.get_all_assignments()
        return [_assignment_payload(a) for a in assignments]
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

