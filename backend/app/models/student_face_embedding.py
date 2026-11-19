from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class StudentFaceEmbedding(Base):
    """
    SQLAlchemy model storing 128-dimensional face feature vectors (embeddings)
    associated with registered students for real-time face recognition.
    Raw images and video frames are NEVER stored permanently.
    """
    __tablename__ = "student_face_embeddings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(50), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    embedding = Column(JSON, nullable=False)  # Serialized 128-dimensional float list
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship back to Student model
    student = relationship("Student", back_populates="face_embeddings")
