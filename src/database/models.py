from sqlalchemy import (
    Column, Integer, String, Float, Text, Boolean,
    DateTime, ForeignKey, Enum, JSON, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db_manager import Base

import enum


class UserRole(enum.Enum):
    STUDENT = "student"
    ADMIN = "admin"
    PLACEMENT_OFFICER = "placement_officer"


class PlacementStatus(enum.Enum):
    NOT_PLACED = "not_placed"
    PLACED = "placed"
    IN_PROCESS = "in_process"
    OFFER_RECEIVED = "offer_received"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)
    resume = relationship("Resume", back_populates="user", uselist=False)
    predictions = relationship("PredictionHistory", back_populates="user")


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String(200), nullable=False)
    roll_number = Column(String(50), unique=True, nullable=False, index=True)
    department = Column(String(100), nullable=False)
    year_of_study = Column(Integer, nullable=False)
    cgpa = Column(Float, nullable=False)
    tenth_percentage = Column(Float)
    twelfth_percentage = Column(Float)
    backlogs = Column(Integer, default=0)
    gender = Column(String(20))
    date_of_birth = Column(String(20))
    phone = Column(String(20))
    address = Column(Text)
    programming_languages = Column(JSON)
    technical_skills = Column(JSON)
    soft_skills = Column(JSON)
    certifications = Column(JSON)
    projects = Column(JSON)
    internships = Column(Integer, default=0)
    github_url = Column(String(500))
    linkedin_url = Column(String(500))
    placement_status = Column(
        Enum(PlacementStatus), default=PlacementStatus.NOT_PLACED
    )
    target_salary_lpa = Column(Float, default=4.0)
    preferred_location = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="student_profile")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    file_path = Column(String(500), nullable=False)
    original_filename = Column(String(255))
    parsed_text = Column(Text)
    extracted_skills = Column(JSON)
    ats_score = Column(Float)
    experience_years = Column(Float, default=0)
    education_details = Column(JSON)
    projects_extracted = Column(JSON)
    certifications_extracted = Column(JSON)
    raw_sections = Column(JSON)
    upload_date = Column(DateTime, server_default=func.now())
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="resume")


class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(200), nullable=False, index=True)
    job_title = Column(String(200), nullable=False)
    description = Column(Text)
    required_skills = Column(JSON)
    min_cgpa = Column(Float, default=6.0)
    min_salary_lpa = Column(Float)
    max_salary_lpa = Column(Float)
    location = Column(String(100))
    job_type = Column(String(50), default="Full-Time")
    experience_required = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
    application_deadline = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    applications = relationship("JobApplication", back_populates="job")


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    match_score = Column(Float)
    status = Column(String(50), default="applied")
    applied_at = Column(DateTime, server_default=func.now())

    student = relationship("StudentProfile")
    job = relationship("JobPosting", back_populates="applications")


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    prediction_type = Column(String(50), nullable=False)
    input_features = Column(JSON)
    prediction_result = Column(JSON)
    confidence_score = Column(Float)
    model_version = Column(String(50))
    predicted_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="predictions")


class LearningRecommendation(Base):
    __tablename__ = "learning_recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    skill_gap = Column(String(100), nullable=False)
    course_name = Column(String(300), nullable=False)
    course_url = Column(String(500))
    platform = Column(String(100))
    difficulty_level = Column(String(50))
    estimated_hours = Column(Integer)
    description = Column(Text)
    relevance_score = Column(Float, default=0.0)


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipient_email = Column(String(255), nullable=False)
    subject = Column(String(300), nullable=False)
    body = Column(Text)
    email_type = Column(String(50))
    sent_at = Column(DateTime, server_default=func.now())
    status = Column(String(20), default="sent")


class AnalyticsLog(Base):
    __tablename__ = "analytics_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(100), nullable=False)
    event_data = Column(JSON)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, server_default=func.now())
