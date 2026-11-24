import os
import logging
import cv2
import numpy as np
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.ai.face_detector import FaceDetector
from app.ai.face_recognizer import FaceRecognizer
from app.models.student import Student
from app.models.student_face_embedding import StudentFaceEmbedding

logger = logging.getLogger("smart_classroom.services.face_recognition")


class FaceRecognitionService:
    """
    Service layer handling student face enrollment, feature vector storage,
    and cosine similarity matching for live monitoring.
    Raw images and video frames are NEVER stored permanently.
    """

    _recognizer: Optional[FaceRecognizer] = None
    _detector: Optional[FaceDetector] = None

    @classmethod
    def get_recognizer(cls) -> FaceRecognizer:
        if cls._recognizer is None:
            cls._recognizer = FaceRecognizer()
        return cls._recognizer

    @classmethod
    def get_detector(cls) -> FaceDetector:
        if cls._detector is None:
            cls._detector = FaceDetector()
        return cls._detector

    @classmethod
    def enroll_student_face(
        cls,
        db: Session,
        student_id: str,
        image_bytes: bytes
    ) -> Dict[str, Any]:
        """
        Enroll a student's face embedding from an uploaded image.
        Validates that EXACTLY ONE face is present in the image.
        """
        if not image_bytes:
            return {
                "success": False,
                "message": "Invalid or empty image data provided.",
                "faces_detected": 0
            }

        # Check if student exists
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID '{student_id}' does not exist."
            )

        # Check student consent
        from app.models.student_consent import StudentConsent
        consent = db.query(StudentConsent).filter(StudentConsent.student_id == student_id).first()
        if consent and (consent.status == "Revoked" or not consent.camera_processing or not consent.face_recognition):
            return {
                "success": False,
                "message": f"Face enrollment rejected: Student '{student_id}' has not granted required camera and face recognition consent (Status: {consent.status}).",
                "faces_detected": 0
            }

        # Decode image
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            return {
                "success": False,
                "message": "Failed to decode image data.",
                "faces_detected": 0
            }

        detector = cls.get_detector()
        detection = detector.detect_faces_in_frame(frame)
        face_count = detection.get("faces_detected", 0)

        if face_count == 0:
            return {
                "success": False,
                "message": "No face detected in the image. Please provide a clear facial photo.",
                "faces_detected": 0
            }
        elif face_count > 1:
            return {
                "success": False,
                "message": f"Multiple faces ({face_count}) detected. Image must contain exactly one student face.",
                "faces_detected": face_count
            }

        # Extract 128-D face embedding vector
        bbox = detection["faces"][0]
        recognizer = cls.get_recognizer()
        embedding = recognizer.extract_embedding(frame, bbox=bbox)

        if not embedding or len(embedding) != 128:
            return {
                "success": False,
                "message": "Failed to extract face feature vector from image.",
                "faces_detected": 1
            }

        # Save embedding record in database
        existing = db.query(StudentFaceEmbedding).filter(StudentFaceEmbedding.student_id == student_id).first()
        if existing:
            existing.embedding = embedding
        else:
            new_emb = StudentFaceEmbedding(student_id=student_id, embedding=embedding)
            db.add(new_emb)

        db.commit()

        logger.info(f"Successfully enrolled face embedding for student {student_id} ({student.name}).")

        return {
            "success": True,
            "message": f"Face enrollment completed successfully for {student.name}.",
            "student_id": student_id,
            "student_name": student.name,
            "faces_detected": 1,
            "embedding_dimensions": len(embedding)
        }

    @classmethod
    def get_enrollment_status(cls, db: Session, student_id: str) -> Dict[str, Any]:
        """Check if a student has an enrolled face embedding in the database."""
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID '{student_id}' does not exist."
            )

        count = db.query(StudentFaceEmbedding).filter(StudentFaceEmbedding.student_id == student_id).count()

        return {
            "student_id": student_id,
            "student_name": student.name,
            "enrolled": count > 0,
            "count": count
        }

    @classmethod
    def delete_enrollment(cls, db: Session, student_id: str) -> Dict[str, Any]:
        """Delete enrolled face embeddings for a student."""
        embeddings = db.query(StudentFaceEmbedding).filter(StudentFaceEmbedding.student_id == student_id).all()
        if not embeddings:
            return {
                "success": False,
                "message": f"No face enrollment records found for student {student_id}.",
                "deleted_count": 0
            }

        count = len(embeddings)
        for emb in embeddings:
            db.delete(emb)
        db.commit()

        logger.info(f"Deleted {count} face enrollment records for student {student_id}.")

        return {
            "success": True,
            "message": f"Deleted face enrollment for student {student_id}.",
            "deleted_count": count
        }

    @classmethod
    def match_face(
        cls,
        candidate_embedding: List[float],
        db: Session,
        threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Compare a candidate face embedding against all enrolled student embeddings in database.
        Returns recognized student identity if cosine similarity >= threshold, else Unknown.
        """
        if not candidate_embedding or len(candidate_embedding) != 128:
            return {
                "recognized": False,
                "student_id": None,
                "name": "Unknown",
                "similarity": 0.0
            }

        recognizer = cls.get_recognizer()
        match_threshold = threshold if threshold is not None else recognizer.threshold

        # Fetch all enrolled embeddings with student info
        enrolled_records = db.query(StudentFaceEmbedding).all()
        if not enrolled_records:
            return {
                "recognized": False,
                "student_id": None,
                "name": "Unknown",
                "similarity": 0.0
            }

        best_match_student = None
        best_similarity = -1.0

        for record in enrolled_records:
            enrolled_emb = record.embedding
            if enrolled_emb and len(enrolled_emb) == 128:
                sim = recognizer.compute_similarity(candidate_embedding, enrolled_emb)
                if sim > best_similarity:
                    best_similarity = sim
                    best_match_student = record.student

        best_similarity_rounded = round(max(0.0, best_similarity), 2)

        if best_match_student and best_similarity >= match_threshold:
            return {
                "recognized": True,
                "student_id": best_match_student.id,
                "name": best_match_student.name,
                "similarity": best_similarity_rounded
            }
        else:
            return {
                "recognized": False,
                "student_id": None,
                "name": "Unknown",
                "similarity": best_similarity_rounded
            }
