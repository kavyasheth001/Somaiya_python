from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from schemas.schemas import PerformanceRequest, PerformanceResponse
from services.performance_service import PerformanceService


router = APIRouter(prefix="/api/performance", tags=["performance"])


def _perf_payload(r) -> dict:
    return PerformanceResponse.model_validate(r).model_dump(mode="json", by_alias=True)


@router.post("")
def create_performance(request: PerformanceRequest, db: Session = Depends(get_db)):
    try:
        record = PerformanceService(db).create_performance_record(
            student_id=request.studentId,
            subject=request.subject,
            assessment_type=request.assessmentType,
            marks_obtained=request.marksObtained,
            total_marks=request.totalMarks,
            recorded_date=request.recordedDate,
        )
        return {"message": "Performance record created successfully", "record": _perf_payload(record)}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@router.get("")
def get_performance(studentId: str | None = Query(default=None), subject: str | None = Query(default=None), db: Session = Depends(get_db)):
    try:
        svc = PerformanceService(db)
        if studentId:
            records = svc.get_by_student(uuid.UUID(studentId))
        elif subject:
            records = svc.get_by_subject(subject)
        else:
            records = svc.get_all_records()
        return [_perf_payload(r) for r in records]
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

