from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from models.models import (
    AssessmentType,
    AssignmentStatus,
    AttendanceStatus,
    NotificationType,
    UserRole,
)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: str
    role: UserRole
    department: str | None = None
    createdAt: datetime | None = Field(default=None, validation_alias="created_at", serialization_alias="createdAt")


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str = Field(min_length=6)
    role: UserRole
    department: str | None = None


class AuthRequest(BaseModel):
    email: str
    password: str


class CourseRequest(BaseModel):
    name: str
    subjectCode: str
    teacherId: uuid.UUID
    studentIds: list[uuid.UUID] | None = None


class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    subjectCode: str = Field(validation_alias="subject_code", serialization_alias="subjectCode")
    teacher: UserResponse
    students: list[UserResponse]
    createdAt: datetime | None = Field(default=None, validation_alias="created_at", serialization_alias="createdAt")


class AssignmentRequest(BaseModel):
    title: str
    description: str | None = None
    subject: str
    dueDate: date
    status: AssignmentStatus
    teacherId: uuid.UUID
    courseId: uuid.UUID


class AssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None = None
    subject: str
    dueDate: date = Field(validation_alias="due_date", serialization_alias="dueDate")
    status: AssignmentStatus
    teacher: UserResponse
    course: CourseResponse
    createdAt: datetime | None = Field(default=None, validation_alias="created_at", serialization_alias="createdAt")


class AttendanceMarkRecord(BaseModel):
    studentId: uuid.UUID
    status: AttendanceStatus


class AttendanceRequest(BaseModel):
    courseId: uuid.UUID
    lectureDate: date
    lectureTopic: str | None = None
    attendanceRecords: list[AttendanceMarkRecord]


class AttendanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    course: CourseResponse
    student: UserResponse
    lectureDate: date = Field(validation_alias="lecture_date", serialization_alias="lectureDate")
    status: AttendanceStatus
    lectureTopic: str | None = Field(
        default=None, validation_alias="lecture_topic", serialization_alias="lectureTopic"
    )
    createdAt: datetime | None = Field(default=None, validation_alias="created_at", serialization_alias="createdAt")


class PerformanceRequest(BaseModel):
    studentId: uuid.UUID
    subject: str
    assessmentType: AssessmentType
    marksObtained: float
    totalMarks: float
    recordedDate: date


class PerformanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student: UserResponse
    subject: str
    assessmentType: AssessmentType = Field(validation_alias="assessment_type", serialization_alias="assessmentType")
    marksObtained: float = Field(validation_alias="marks_obtained", serialization_alias="marksObtained")
    totalMarks: float = Field(validation_alias="total_marks", serialization_alias="totalMarks")
    percentage: float
    recordedDate: date = Field(validation_alias="recorded_date", serialization_alias="recordedDate")
    createdAt: datetime | None = Field(default=None, validation_alias="created_at", serialization_alias="createdAt")


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    message: str
    type: NotificationType
    recipient: UserResponse
    isRead: bool = Field(validation_alias="is_read", serialization_alias="isRead")
    createdAt: datetime | None = Field(default=None, validation_alias="created_at", serialization_alias="createdAt")


class TeacherDashboardResponse(BaseModel):
    classesManaged: int
    avgAttendance: float
    avgGrade: float
    classes: list[CourseResponse]


class StudentDashboardResponse(BaseModel):
    activeSubjects: int
    overallAttendance: float
    avgGrade: float
    pendingAssignments: int
    courses: list[CourseResponse]

