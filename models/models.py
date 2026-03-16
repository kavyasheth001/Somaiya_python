from __future__ import annotations

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class UserRole(str, enum.Enum):
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"


class AssignmentStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"


class AssessmentType(str, enum.Enum):
    MIDTERM = "MIDTERM"
    FINAL = "FINAL"
    INTERNAL = "INTERNAL"
    ASSIGNMENT = "ASSIGNMENT"
    QUIZ = "QUIZ"


class NotificationType(str, enum.Enum):
    ATTENDANCE_ALERT = "ATTENDANCE_ALERT"
    ASSIGNMENT_SUBMISSION = "ASSIGNMENT_SUBMISSION"
    ASSIGNMENT_GRADED = "ASSIGNMENT_GRADED"
    ASSIGNMENT_DUE = "ASSIGNMENT_DUE"
    GENERAL = "GENERAL"
    SYSTEM_UPDATE = "SYSTEM_UPDATE"


course_students = Table(
    "course_students",
    Base.metadata,
    Column("course_id", UUID(as_uuid=True), ForeignKey("courses.id"), primary_key=True),
    Column("student_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    taught_courses: Mapped[list["Course"]] = relationship(back_populates="teacher", cascade="all, delete-orphan")
    enrolled_courses: Mapped[list["Course"]] = relationship(
        secondary=course_students,
        back_populates="students",
    )
    attendance_records: Mapped[list["Attendance"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    created_assignments: Mapped[list["Assignment"]] = relationship(back_populates="teacher", cascade="all, delete-orphan")
    submissions: Mapped[list["AssignmentSubmission"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    performance_records: Mapped[list["PerformanceRecord"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    notifications: Mapped[list["Notification"]] = relationship(back_populates="recipient", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    subject_code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    teacher_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    teacher: Mapped[User] = relationship(back_populates="taught_courses")
    students: Mapped[list[User]] = relationship(secondary=course_students, back_populates="enrolled_courses")

    attendance_records: Mapped[list["Attendance"]] = relationship(back_populates="course", cascade="all, delete-orphan")
    assignments: Mapped[list["Assignment"]] = relationship(back_populates="course", cascade="all, delete-orphan")


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    subject: Mapped[str] = mapped_column(String(100), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[AssignmentStatus] = mapped_column(Enum(AssignmentStatus, name="assignment_status"), nullable=False)
    teacher_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    course_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    teacher: Mapped[User] = relationship(back_populates="created_assignments")
    course: Mapped[Course] = relationship(back_populates="assignments")
    submissions: Mapped[list["AssignmentSubmission"]] = relationship(
        back_populates="assignment", cascade="all, delete-orphan"
    )


class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"
    __table_args__ = (UniqueConstraint("student_id", "assignment_id", name="uq_submission_student_assignment"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    assignment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assignments.id"), nullable=False, index=True
    )
    file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    submission_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    grade: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    student: Mapped[User] = relationship(back_populates="submissions")
    assignment: Mapped[Assignment] = relationship(back_populates="submissions")


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (UniqueConstraint("course_id", "student_id", "lecture_date", name="uq_attendance_unique"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False, index=True)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    lecture_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[AttendanceStatus] = mapped_column(Enum(AttendanceStatus, name="attendance_status"), nullable=False)
    lecture_topic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    course: Mapped[Course] = relationship(back_populates="attendance_records")
    student: Mapped[User] = relationship(back_populates="attendance_records")


class PerformanceRecord(Base):
    __tablename__ = "performance_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    assessment_type: Mapped[AssessmentType] = mapped_column(
        Enum(AssessmentType, name="assessment_type"), nullable=False
    )
    marks_obtained: Mapped[float] = mapped_column(Float, nullable=False)
    total_marks: Mapped[float] = mapped_column(Float, nullable=False)
    percentage: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    student: Mapped[User] = relationship(back_populates="performance_records")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType, name="notification_type"), nullable=False)
    recipient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    recipient: Mapped[User] = relationship(back_populates="notifications")

