from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import relationship
from app.database import Base


class EmotionRecord(Base):
    __tablename__ = "emotion_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(50), ForeignKey("students.id", ondelete="SET NULL"), nullable=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    dominant_emotion = Column(String(50), default="Neutral", nullable=False)  # "Happy", "Neutral", "Focused", "Stressed", "Bored", "Sad"
    confidence = Column(Float, default=0.85, nullable=False)
    engagement_level = Column(Float, default=80.0, nullable=False)  # 0 to 100 percentage
    raw_scores = Column(Text, nullable=True)  # JSON-encoded raw emotion probabilities

    # Relationships
    student = relationship("Student", back_populates="emotion_records")
    classroom = relationship("Classroom", back_populates="emotion_records")
