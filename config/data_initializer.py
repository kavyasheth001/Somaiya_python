from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import (
    AssessmentType,
    Assignment,
    AssignmentStatus,
    Attendance,
    AttendanceStatus,
    Course,
    Notification,
    NotificationType,
    PerformanceRecord,
    User,
    UserRole,
)
from services.auth_service import pwd_context


def initialize_sample_data(db: Session) -> None:
    existing = db.scalar(select(User.id).limit(1))
    if existing is not None:
        return

    # Teachers
    teacher1 = User(
        name="Dr. Sharma",
        email="sharma@kjit.edu",
        password=pwd_context.hash("password123"),
        role=UserRole.TEACHER,
        department="Computer Science",
    )
    teacher2 = User(
        name="Prof. Kumar",
        email="kumar@kjit.edu",
        password=pwd_context.hash("password123"),
        role=UserRole.TEACHER,
        department="Computer Science",
    )
    teacher3 = User(
        name="Ms. Patel",
        email="patel@kjit.edu",
        password=pwd_context.hash("password123"),
        role=UserRole.TEACHER,
        department="Computer Science",
    )

    # Students
    student1 = User(
        name="Rahul Mehta",
        email="rahul.mehta@student.kjit.edu",
        password=pwd_context.hash("password123"),
        role=UserRole.STUDENT,
        department="Computer Science",
    )
    student2 = User(
        name="Priya Singh",
        email="priya.singh@student.kjit.edu",
        password=pwd_context.hash("password123"),
        role=UserRole.STUDENT,
        department="Computer Science",
    )
    student3 = User(
        name="Amit Kumar",
        email="amit.kumar@student.kjit.edu",
        password=pwd_context.hash("password123"),
        role=UserRole.STUDENT,
        department="Computer Science",
    )
    student4 = User(
        name="Sneha Patel",
        email="sneha.patel@student.kjit.edu",
        password=pwd_context.hash("password123"),
        role=UserRole.STUDENT,
        department="Computer Science",
    )

    db.add_all([teacher1, teacher2, teacher3, student1, student2, student3, student4])
    db.commit()

    # Courses
    course1 = Course(name="Database Management Systems", subject_code="CS-301", teacher=teacher1)
    course2 = Course(name="Data Structures", subject_code="CS-302", teacher=teacher2)
    course3 = Course(name="Web Development", subject_code="CS-303", teacher=teacher3)
    db.add_all([course1, course2, course3])
    db.commit()

    # Enroll students
    course1.students.extend([student1, student2, student3])
    course2.students.extend([student1, student2, student4])
    course3.students.extend([student2, student3, student4])
    db.commit()

    # Assignments
    assignment1 = Assignment(
        title="Database Design Project",
        description="Design a complete database schema for an e-commerce platform",
        subject="DBMS",
        due_date=date.today() + timedelta(days=10),
        status=AssignmentStatus.ACTIVE,
        teacher=teacher1,
        course=course1,
    )
    assignment2 = Assignment(
        title="Binary Tree Implementation",
        description="Implement various binary tree operations",
        subject="Data Structures",
        due_date=date.today() + timedelta(days=15),
        status=AssignmentStatus.ACTIVE,
        teacher=teacher2,
        course=course2,
    )
    assignment3 = Assignment(
        title="Portfolio Website",
        description="Create a personal portfolio website using React",
        subject="Web Development",
        due_date=date.today() + timedelta(days=5),
        status=AssignmentStatus.ACTIVE,
        teacher=teacher3,
        course=course3,
    )
    db.add_all([assignment1, assignment2, assignment3])
    db.commit()

    # Attendance (sample)
    lecture_day = date.today() - timedelta(days=1)
    db.add_all(
        [
            Attendance(
                course=course1,
                student=student1,
                lecture_date=lecture_day,
                status=AttendanceStatus.PRESENT,
                lecture_topic="ER Diagrams",
            ),
            Attendance(
                course=course1,
                student=student2,
                lecture_date=lecture_day,
                status=AttendanceStatus.PRESENT,
                lecture_topic="ER Diagrams",
            ),
            Attendance(
                course=course1,
                student=student3,
                lecture_date=lecture_day,
                status=AttendanceStatus.ABSENT,
                lecture_topic="ER Diagrams",
            ),
        ]
    )
    db.commit()

    # Performance (sample)
    db.add_all(
        [
            PerformanceRecord(
                student=student1,
                subject="DBMS",
                assessment_type=AssessmentType.MIDTERM,
                marks_obtained=85.0,
                total_marks=100.0,
                percentage=85.0,
                recorded_date=date.today() - timedelta(days=30),
            ),
            PerformanceRecord(
                student=student2,
                subject="DBMS",
                assessment_type=AssessmentType.MIDTERM,
                marks_obtained=92.0,
                total_marks=100.0,
                percentage=92.0,
                recorded_date=date.today() - timedelta(days=30),
            ),
            PerformanceRecord(
                student=student1,
                subject="Data Structures",
                assessment_type=AssessmentType.MIDTERM,
                marks_obtained=78.0,
                total_marks=100.0,
                percentage=78.0,
                recorded_date=date.today() - timedelta(days=25),
            ),
        ]
    )
    db.commit()

    # Notifications (sample)
    db.add_all(
        [
            Notification(
                message=f"New assignment 'Database Design Project' is due on {date.today() + timedelta(days=10)}",
                type=NotificationType.ASSIGNMENT_SUBMISSION,
                recipient=student1,
            ),
            Notification(
                message="Your attendance is below 75% in DBMS",
                type=NotificationType.ATTENDANCE_ALERT,
                recipient=student3,
            ),
        ]
    )
    db.commit()

