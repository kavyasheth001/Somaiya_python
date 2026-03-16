from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from models.models import PerformanceRecord, User, UserRole


class PerformanceService:
    def __init__(self, db: Session):
        self.db = db

    def create_performance_record(
        self,
        *,
        student_id: uuid.UUID,
        subject: str,
        assessment_type,
        marks_obtained: float,
        total_marks: float,
        recorded_date: date,
    ) -> PerformanceRecord:
        student = self.db.get(User, student_id)
        if student is None or student.role != UserRole.STUDENT:
            raise ValueError("Student not found")

        percentage = (marks_obtained / total_marks) * 100.0 if total_marks and total_marks > 0 else 0.0
        record = PerformanceRecord(
            student=student,
            subject=subject,
            assessment_type=assessment_type,
            marks_obtained=marks_obtained,
            total_marks=total_marks,
            percentage=percentage,
            recorded_date=recorded_date,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_all_records(self) -> list[PerformanceRecord]:
        q = select(PerformanceRecord).options(joinedload(PerformanceRecord.student)).order_by(PerformanceRecord.created_at.desc())
        return list(self.db.scalars(q).unique())

    def get_by_student(self, student_id: uuid.UUID) -> list[PerformanceRecord]:
        student = self.db.get(User, student_id)
        if student is None:
            raise ValueError("Student not found")
        q = (
            select(PerformanceRecord)
            .where(PerformanceRecord.student_id == student_id)
            .options(joinedload(PerformanceRecord.student))
            .order_by(PerformanceRecord.created_at.desc())
        )
        return list(self.db.scalars(q).unique())

    def get_by_subject(self, subject: str) -> list[PerformanceRecord]:
        q = (
            select(PerformanceRecord)
            .where(PerformanceRecord.subject == subject)
            .options(joinedload(PerformanceRecord.student))
            .order_by(PerformanceRecord.created_at.desc())
        )
        return list(self.db.scalars(q).unique())

    def get_average_by_student(self, student_id: uuid.UUID) -> float | None:
        student = self.db.get(User, student_id)
        if student is None:
            raise ValueError("Student not found")
        avg = self.db.scalar(select(func.avg(PerformanceRecord.percentage)).where(PerformanceRecord.student_id == student_id))
        return float(avg) if avg is not None else None

