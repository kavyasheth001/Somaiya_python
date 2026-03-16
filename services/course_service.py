from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from models.models import Course, User, UserRole


class CourseService:
    def __init__(self, db: Session):
        self.db = db

    def create_course(
        self,
        *,
        name: str,
        subject_code: str,
        teacher_id: uuid.UUID,
        student_ids: list[uuid.UUID] | None,
    ) -> Course:
        teacher = self.db.get(User, teacher_id)
        if teacher is None or teacher.role != UserRole.TEACHER:
            raise ValueError("Teacher not found")

        course = Course(name=name, subject_code=subject_code, teacher=teacher)
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)

        if student_ids:
            students = list(self.db.scalars(select(User).where(User.id.in_(student_ids))))
            for s in students:
                if s.role == UserRole.STUDENT and s not in course.students:
                    course.students.append(s)
            self.db.commit()
            self.db.refresh(course)

        return course

    def get_all_courses(self) -> list[Course]:
        q = select(Course).options(joinedload(Course.teacher), joinedload(Course.students)).order_by(Course.created_at.asc())
        return list(self.db.scalars(q).unique())

    def get_courses_by_teacher(self, teacher_id: uuid.UUID) -> list[Course]:
        q = (
            select(Course)
            .where(Course.teacher_id == teacher_id)
            .options(joinedload(Course.teacher), joinedload(Course.students))
            .order_by(Course.created_at.asc())
        )
        return list(self.db.scalars(q).unique())

    def get_courses_by_student(self, student_id: uuid.UUID) -> list[Course]:
        q = (
            select(Course)
            .join(Course.students)
            .where(User.id == student_id)
            .options(joinedload(Course.teacher), joinedload(Course.students))
            .order_by(Course.created_at.asc())
        )
        return list(self.db.scalars(q).unique())

    def get_course_by_id(self, course_id: uuid.UUID) -> Course:
        q = (
            select(Course)
            .where(Course.id == course_id)
            .options(joinedload(Course.teacher), joinedload(Course.students))
        )
        course = self.db.scalar(q)
        if course is None:
            raise ValueError("Course not found")
        return course

    def add_student_to_course(self, course_id: uuid.UUID, student_id: uuid.UUID) -> Course:
        course = self.get_course_by_id(course_id)
        student = self.db.get(User, student_id)
        if student is None or student.role != UserRole.STUDENT:
            raise ValueError("Student not found")
        if student not in course.students:
            course.students.append(student)
            self.db.commit()
            self.db.refresh(course)
        return course

    def remove_student_from_course(self, course_id: uuid.UUID, student_id: uuid.UUID) -> Course:
        course = self.get_course_by_id(course_id)
        student = self.db.get(User, student_id)
        if student is None:
            raise ValueError("Student not found")
        if student in course.students:
            course.students.remove(student)
            self.db.commit()
            self.db.refresh(course)
        return course

