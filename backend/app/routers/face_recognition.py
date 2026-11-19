import base64
from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile, Request, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.face_recognition_service import FaceRecognitionService
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/face-recognition", tags=["Face Recognition"])


class Base64EnrollRequest(BaseModel):
    image: str


@router.post("/enroll/{student_id}", status_code=status.HTTP_200_OK)
async def enroll_student_face_file(
    student_id: str,
    request: Request,
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Enroll a student's face embedding from an uploaded image file or Base64 string.
    Validates that EXACTLY ONE face is detected in the image.
    Requires JWT authentication.
    """
    image_bytes = None

    if file and file.filename:
        image_bytes = await file.read()
    else:
        try:
            body = await request.json()
            raw_img = body.get("image") if isinstance(body, dict) else None
            if raw_img:
                if "," in raw_img:
                    raw_img = raw_img.split(",", 1)[1]
                image_bytes = base64.b64decode(raw_img)
        except Exception:
            pass

    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image data is required. Provide an uploaded image file or base64 image payload."
        )

    res = FaceRecognitionService.enroll_student_face(db, student_id=student_id, image_bytes=image_bytes)
    if not res.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=res.get("message", "Face enrollment failed.")
        )

    return res


@router.get("/status/{student_id}", status_code=status.HTTP_200_OK)
def get_enrollment_status(
    student_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Get face enrollment status for a student.
    Requires JWT authentication.
    """
    return FaceRecognitionService.get_enrollment_status(db, student_id=student_id)


@router.delete("/enrollment/{student_id}", status_code=status.HTTP_200_OK)
def delete_enrollment(
    student_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Delete face enrollment for a student.
    Requires JWT authentication.
    """
    return FaceRecognitionService.delete_enrollment(db, student_id=student_id)
