from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from models.models import Attendance, AttendanceStatus, Course, Notification, NotificationType, User, UserRole


class AttendanceService:
    def __init__(self, db: Session):
        self.db = db

    def mark_attendance(
        self,
        *,
        course_id: uuid.UUID,
        lecture_date: date,
        lecture_topic: str | None,
        records: list[tuple[uuid.UUID, AttendanceStatus]],
    ) -> list[Attendance]:
        course = self.db.get(Course, course_id)
        if course is None:
            raise ValueError("Course not found")

        saved: list[Attendance] = []
        for student_id, status in records:
            student = self.db.get(User, student_id)
            if student is None or student.role != UserRole.STUDENT:
                raise ValueError("Student not found")

            existing = self.db.scalar(
                select(Attendance).where(
                    Attendance.course_id == course_id,
                    Attendance.student_id == student_id,
                    Attendance.lecture_date == lecture_date,
                )
            )
            if existing:
                existing.status = status
                attendance = existing
            else:
                attendance = Attendance(
                    course=course,
                    student=student,
                    lecture_date=lecture_date,
                    status=status,
                    lecture_topic=lecture_topic,
                )
                self.db.add(attendance)
            self.db.commit()
            self.db.refresh(attendance)
            saved.append(attendance)

        return saved

    def get_attendance_by_course(self, course_id: uuid.UUID) -> list[Attendance]:
        course = self.db.get(Course, course_id)
        if course is None:
            raise ValueError("Course not found")
        q = (
            select(Attendance)
            .where(Attendance.course_id == course_id)
            .options(joinedload(Attendance.course).joinedload(Course.teacher), joinedload(Attendance.student), joinedload(Attendance.course).joinedload(Course.students))
            .order_by(Attendance.lecture_date.desc(), Attendance.created_at.desc())
        )
        return list(self.db.scalars(q).unique())

    def get_attendance_by_student(self, student_id: uuid.UUID) -> list[Attendance]:
        student = self.db.get(User, student_id)
        if student is None:
            raise ValueError("Student not found")
        q = (
            select(Attendance)
            .where(Attendance.student_id == student_id)
            .options(joinedload(Attendance.course).joinedload(Course.teacher), joinedload(Attendance.student), joinedload(Attendance.course).joinedload(Course.students))
            .order_by(Attendance.lecture_date.desc(), Attendance.created_at.desc())
        )
        return list(self.db.scalars(q).unique())

    def get_attendance_by_course_and_date(self, course_id: uuid.UUID, lecture_date: date) -> list[Attendance]:
        course = self.db.get(Course, course_id)
        if course is None:
            raise ValueError("Course not found")
        q = (
            select(Attendance)
            .where(Attendance.course_id == course_id, Attendance.lecture_date == lecture_date)
            .options(joinedload(Attendance.course).joinedload(Course.teacher), joinedload(Attendance.student), joinedload(Attendance.course).joinedload(Course.students))
            .order_by(Attendance.created_at.desc())
        )
        return list(self.db.scalars(q).unique())

    def get_attendance_by_student_and_course(self, student_id: uuid.UUID, course_id: uuid.UUID) -> list[Attendance]:
        student = self.db.get(User, student_id)
        if student is None:
            raise ValueError("Student not found")
        course = self.db.get(Course, course_id)
        if course is None:
            raise ValueError("Course not found")
        q = (
            select(Attendance)
            .where(Attendance.student_id == student_id, Attendance.course_id == course_id)
            .options(joinedload(Attendance.course).joinedload(Course.teacher), joinedload(Attendance.student), joinedload(Attendance.course).joinedload(Course.students))
            .order_by(Attendance.lecture_date.desc(), Attendance.created_at.desc())
        )
        return list(self.db.scalars(q).unique())

    def calculate_attendance_percentage(self, student_id: uuid.UUID, course_id: uuid.UUID) -> float:
        student = self.db.get(User, student_id)
        if student is None:
            raise ValueError("Student not found")
        course = self.db.get(Course, course_id)
        if course is None:
            raise ValueError("Course not found")

        total = self.db.scalar(
            select(func.count()).select_from(Attendance).where(Attendance.student_id == student_id, Attendance.course_id == course_id)
        )
        present = self.db.scalar(
            select(func.count()).select_from(Attendance).where(
                Attendance.student_id == student_id,
                Attendance.course_id == course_id,
                Attendance.status == AttendanceStatus.PRESENT,
            )
        )
        total_n = int(total or 0)
        present_n = int(present or 0)
        percentage = (present_n / total_n) * 100.0 if total_n > 0 else 0.0

        if percentage < 75.0 and total_n > 0:
            msg = f"Parent notified: {student.name} – Attendance {percentage:.1f}%"
            self.db.add(Notification(message=msg, type=NotificationType.ATTENDANCE_ALERT, recipient=student))
            self.db.commit()

        return percentage

