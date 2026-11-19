from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class AttentionRecord(Base):
    __tablename__ = "attention_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(50), ForeignKey("students.id", ondelete="SET NULL"), nullable=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    attention_score = Column(Float, default=85.0, nullable=False)  # 0 to 100
    status = Column(String(50), default="Focused", nullable=False)  # "Focused", "Distracted", "Drowsy"
    gaze_direction = Column(String(50), nullable=True)  # "Forward", "Left", "Right", "Down"
    head_pose = Column(String(50), nullable=True)  # "Upright", "Tilted", "Down"

    # Relationships
    student = relationship("Student", back_populates="attention_records")
    classroom = relationship("Classroom", back_populates="attention_records")
