from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.orm import Session, joinedload

from models.models import (
    Assignment,
    AssignmentStatus,
    AssignmentSubmission,
    Course,
    Notification,
    NotificationType,
    User,
    UserRole,
)


class AssignmentService:
    def __init__(self, db: Session):
        self.db = db

    def create_assignment(
        self,
        *,
        title: str,
        description: str | None,
        subject: str,
        due_date,
        status: AssignmentStatus,
        teacher_id: uuid.UUID,
        course_id: uuid.UUID,
    ) -> Assignment:
        teacher = self.db.get(User, teacher_id)
        if teacher is None or teacher.role != UserRole.TEACHER:
            raise ValueError("Teacher not found")

        course = self.db.get(Course, course_id)
        if course is None:
            raise ValueError("Course not found")

        assignment = Assignment(
            title=title,
            description=description,
            subject=subject,
            due_date=due_date,
            status=status,
            teacher=teacher,
            course=course,
        )
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)

        # create notifications for all students in the course
        for student in course.students:
            msg = f"New assignment '{assignment.title}' is due on {assignment.due_date}"
            n = Notification(message=msg, type=NotificationType.ASSIGNMENT_SUBMISSION, recipient=student)
            self.db.add(n)
        self.db.commit()

        return assignment

    def get_all_assignments(self) -> list[Assignment]:
        q = (
            select(Assignment)
            .options(
                joinedload(Assignment.teacher),
                joinedload(Assignment.course).joinedload(Course.teacher),
                joinedload(Assignment.course).joinedload(Course.students),
            )
            .order_by(Assignment.created_at.desc())
        )
        return list(self.db.scalars(q).unique())

    def get_assignments_by_teacher(self, teacher_id: uuid.UUID) -> list[Assignment]:
        teacher = self.db.get(User, teacher_id)
        if teacher is None:
            raise ValueError("Teacher not found")
        q = (
            select(Assignment)
            .where(Assignment.teacher_id == teacher_id)
            .options(
                joinedload(Assignment.teacher),
                joinedload(Assignment.course).joinedload(Course.teacher),
                joinedload(Assignment.course).joinedload(Course.students),
            )
            .order_by(Assignment.created_at.desc())
        )
        return list(self.db.scalars(q).unique())

    def get_assignments_by_course(self, course_id: uuid.UUID) -> list[Assignment]:
        course = self.db.get(Course, course_id)
        if course is None:
            raise ValueError("Course not found")
        q = (
            select(Assignment)
            .where(Assignment.course_id == course_id)
            .options(
                joinedload(Assignment.teacher),
                joinedload(Assignment.course).joinedload(Course.teacher),
                joinedload(Assignment.course).joinedload(Course.students),
            )
            .order_by(Assignment.created_at.desc())
        )
        return list(self.db.scalars(q).unique())

    def get_active_assignments_for_student(self, student_id: uuid.UUID) -> list[Assignment]:
        student = self.db.get(User, student_id)
        if student is None:
            raise ValueError("Student not found")
        q = (
            select(Assignment)
            .join(Assignment.course)
            .join(Course.students)
            .where(and_(User.id == student_id, Assignment.status == AssignmentStatus.ACTIVE))
            .options(
                joinedload(Assignment.teacher),
                joinedload(Assignment.course).joinedload(Course.teacher),
                joinedload(Assignment.course).joinedload(Course.students),
            )
            .order_by(Assignment.created_at.desc())
        )
        return list(self.db.scalars(q).unique())

    def get_assignment_by_id(self, assignment_id: uuid.UUID) -> Assignment:
        q = (
            select(Assignment)
            .where(Assignment.id == assignment_id)
            .options(
                joinedload(Assignment.teacher),
                joinedload(Assignment.course).joinedload(Course.teacher),
                joinedload(Assignment.course).joinedload(Course.students),
            )
        )
        assignment = self.db.scalar(q)
        if assignment is None:
            raise ValueError("Assignment not found")
        return assignment

    def update_assignment(self, assignment_id: uuid.UUID, **fields) -> Assignment:
        assignment = self.get_assignment_by_id(assignment_id)
        for k, v in fields.items():
            setattr(assignment, k, v)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def delete_assignment(self, assignment_id: uuid.UUID) -> None:
        assignment = self.db.get(Assignment, assignment_id)
        if assignment is None:
            raise ValueError("Assignment not found")
        self.db.delete(assignment)
        self.db.commit()

    def submit_assignment(self, assignment_id: uuid.UUID, student_id: uuid.UUID, file_url: str) -> AssignmentSubmission:
        assignment = self.db.get(Assignment, assignment_id)
        if assignment is None:
            raise ValueError("Assignment not found")
        student = self.db.get(User, student_id)
        if student is None:
            raise ValueError("Student not found")

        existing = self.db.scalar(
            select(AssignmentSubmission).where(
                AssignmentSubmission.student_id == student_id,
                AssignmentSubmission.assignment_id == assignment_id,
            )
        )
        if existing:
            existing.file_url = file_url
            existing.submission_date = datetime.utcnow()
            submission = existing
        else:
            submission = AssignmentSubmission(
                student=student,
                assignment=assignment,
                file_url=file_url,
                submission_date=datetime.utcnow(),
            )
            self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)

        # notify teacher
        teacher = assignment.teacher
        msg = f"Student {student.name} submitted assignment '{assignment.title}'"
        self.db.add(Notification(message=msg, type=NotificationType.ASSIGNMENT_SUBMISSION, recipient=teacher))
        self.db.commit()

        return submission

    def grade_submission(self, submission_id: uuid.UUID, grade: float, feedback: str | None) -> AssignmentSubmission:
        submission = self.db.get(AssignmentSubmission, submission_id)
        if submission is None:
            raise ValueError("Submission not found")
        submission.grade = grade
        submission.feedback = feedback
        self.db.commit()
        self.db.refresh(submission)

        # notify student
        msg = f"Assignment '{submission.assignment.title}' has been graded. Score: {grade:.1f}"
        self.db.add(Notification(message=msg, type=NotificationType.ASSIGNMENT_GRADED, recipient=submission.student))
        self.db.commit()
        return submission

