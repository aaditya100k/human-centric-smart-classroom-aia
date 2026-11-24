from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(String(50), primary_key=True, index=True)  # e.g. "ST-2024-001"
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    department = Column(String(100), nullable=False)
    classroom_id = Column(Integer, ForeignKey("classrooms.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(20), default="Active", nullable=False)  # "Active", "Inactive"
    profile_photo_path = Column(String(500), nullable=True)  # Relative path to uploaded profile photo
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    classroom = relationship("Classroom", back_populates="students")
    attendance_records = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
    emotion_records = relationship("EmotionRecord", back_populates="student", cascade="all, delete-orphan")
    attention_records = relationship("AttentionRecord", back_populates="student", cascade="all, delete-orphan")
    temperature_records = relationship("TemperatureRecord", back_populates="student", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="student", cascade="all, delete-orphan")
    face_embeddings = relationship("StudentFaceEmbedding", back_populates="student", cascade="all, delete-orphan")
    consent = relationship("StudentConsent", back_populates="student", uselist=False, cascade="all, delete-orphan")
