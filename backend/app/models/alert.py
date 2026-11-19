from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(50), default="System", nullable=False)  # "Attendance", "Emotion", "Attention", "Temperature", "System"
    severity = Column(String(20), default="Medium", nullable=False)  # "Low", "Medium", "High", "Critical"
    classroom_id = Column(Integer, ForeignKey("classrooms.id", ondelete="SET NULL"), nullable=True, index=True)
    student_id = Column(String(50), ForeignKey("students.id", ondelete="SET NULL"), nullable=True, index=True)
    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    classroom = relationship("Classroom", back_populates="alerts")
    student = relationship("Student", back_populates="alerts")
