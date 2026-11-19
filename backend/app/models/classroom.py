from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, index=True, nullable=False)  # e.g., "Room 101"
    department = Column(String(100), nullable=False)  # e.g., "Science", "Engineering"
    capacity = Column(Integer, default=30, nullable=False)
    status = Column(String(20), default="Active", nullable=False)  # "Active", "Inactive"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    students = relationship("Student", back_populates="classroom")
    attendance_records = relationship("Attendance", back_populates="classroom", cascade="all, delete-orphan")
    emotion_records = relationship("EmotionRecord", back_populates="classroom", cascade="all, delete-orphan")
    attention_records = relationship("AttentionRecord", back_populates="classroom", cascade="all, delete-orphan")
    temperature_records = relationship("TemperatureRecord", back_populates="classroom", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="classroom", cascade="all, delete-orphan")
