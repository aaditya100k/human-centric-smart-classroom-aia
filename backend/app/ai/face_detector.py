import os
import logging
import cv2
import numpy as np
from typing import Dict, Any, List, Tuple

logger = logging.getLogger("smart_classroom.ai.face_detector")

CASCADE_PATH = os.path.join(
    os.path.dirname(__file__),
    "cascades",
    "haarcascade_frontalface_default.xml"
)


class FaceDetector:
    """
    OpenCV Haar Cascade Face Detector module.
    Detects faces in image frames without performing face recognition or identity mapping.
    """

    def __init__(self, cascade_path: str = CASCADE_PATH):
        if not os.path.exists(cascade_path):
            if hasattr(cv2, "data") and hasattr(cv2.data, "haarcascades"):
                alt_path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
                if os.path.exists(alt_path):
                    cascade_path = alt_path

        self.cascade_path = cascade_path
        self.classifier = cv2.CascadeClassifier(self.cascade_path)
        if self.classifier.empty():
            logger.error(f"Failed to load Haar Cascade classifier from {self.cascade_path}")
        else:
            logger.info(f"Loaded FaceDetector Haar Cascade successfully from {self.cascade_path}")

    def is_loaded(self) -> bool:
        return not self.classifier.empty()

    def detect_faces_in_frame(
        self,
        frame: np.ndarray,
        scale_factor: float = 1.1,
        min_neighbors: int = 5,
        min_size: Tuple[int, int] = (30, 30)
    ) -> Dict[str, Any]:
        """
        Detect faces in a numpy BGR OpenCV frame.
        Returns bounding boxes and count.
        """
        if self.classifier.empty() or frame is None or frame.size == 0:
            return {"faces_detected": 0, "faces": []}

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        faces = self.classifier.detectMultiScale(
            gray,
            scaleFactor=scale_factor,
            minNeighbors=min_neighbors,
            minSize=min_size,
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        face_list: List[Dict[str, int]] = []
        for (x, y, w, h) in faces:
            face_list.append({
                "x": int(x),
                "y": int(y),
                "width": int(w),
                "height": int(h)
            })

        return {
            "faces_detected": len(face_list),
            "faces": face_list
        }

    def detect_faces_in_bytes(
        self,
        image_bytes: bytes,
        scale_factor: float = 1.1,
        min_neighbors: int = 5
    ) -> Dict[str, Any]:
        """
        Detect faces from raw image bytes (e.g., JPEG / PNG / WebP decoded from Base64).
        """
        if not image_bytes:
            return {"faces_detected": 0, "faces": []}

        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            return {"faces_detected": 0, "faces": []}

        return self.detect_faces_in_frame(frame, scale_factor=scale_factor, min_neighbors=min_neighbors)
