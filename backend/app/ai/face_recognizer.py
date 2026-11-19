import os
import logging
import urllib.request
import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("smart_classroom.ai.face_recognizer")

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "face_recognition_sface_2021dec.onnx")
MODEL_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx"

DEFAULT_RECOGNITION_THRESHOLD = float(os.getenv("FACE_RECOGNITION_THRESHOLD", "0.60"))


class FaceRecognizer:
    """
    OpenCV SFace 128-dimensional Deep Face Recognition module.
    Extracts L2-normalized feature vectors and computes cosine similarity.
    Does NOT store raw images or video frames.
    """

    def __init__(self, model_path: str = MODEL_PATH, threshold: float = DEFAULT_RECOGNITION_THRESHOLD):
        self.model_path = model_path
        self.threshold = threshold
        self.recognizer = None

        self._ensure_model_loaded()

    def _ensure_model_loaded(self):
        if not os.path.exists(self.model_path):
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            logger.info(f"Downloading SFace recognition model to {self.model_path}...")
            try:
                urllib.request.urlretrieve(MODEL_URL, self.model_path)
                logger.info("SFace model downloaded successfully.")
            except Exception as err:
                logger.error(f"Failed to download SFace model: {err}")

        if os.path.exists(self.model_path) and hasattr(cv2, "FaceRecognizerSF"):
            try:
                self.recognizer = cv2.FaceRecognizerSF.create(self.model_path, "")
                logger.info(f"FaceRecognizer initialized successfully with model {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to load FaceRecognizerSF from {self.model_path}: {e}")

    def is_loaded(self) -> bool:
        return self.recognizer is not None

    def extract_embedding(
        self,
        frame: np.ndarray,
        bbox: Optional[Dict[str, int]] = None
    ) -> Optional[List[float]]:
        """
        Extract a 128-dimensional floating-point feature embedding vector from a face.
        """
        if frame is None or frame.size == 0 or not self.is_loaded():
            return None

        h_img, w_img = frame.shape[:2]

        if bbox:
            x = max(0, int(bbox.get("x", 0)))
            y = max(0, int(bbox.get("y", 0)))
            w = max(1, int(bbox.get("width", w_img)))
            h = max(1, int(bbox.get("height", h_img)))

            # Clip bounding box within image boundaries
            x_end = min(w_img, x + w)
            y_end = min(h_img, y + h)

            cropped = frame[y:y_end, x:x_end]
        else:
            cropped = frame

        if cropped is None or cropped.size == 0:
            return None

        try:
            # Resize cropped face to standard 112x112 for SFace feature extraction
            face_resized = cv2.resize(cropped, (112, 112), interpolation=cv2.INTER_AREA)
            feat = self.recognizer.feature(face_resized)
            if feat is not None and feat.size > 0:
                feat_vec = feat.flatten()
                # Normalize vector to unit L2 length
                norm = np.linalg.norm(feat_vec)
                if norm > 0:
                    feat_vec = feat_vec / norm
                return [float(v) for v in feat_vec]
        except Exception as err:
            logger.error(f"Error extracting face embedding: {err}")

        return None

    def extract_embedding_from_bytes(
        self,
        image_bytes: bytes,
        bbox: Optional[Dict[str, int]] = None
    ) -> Optional[List[float]]:
        """
        Extract embedding vector directly from raw image bytes.
        """
        if not image_bytes:
            return None
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            return None
        return self.extract_embedding(frame, bbox=bbox)

    @staticmethod
    def compute_similarity(emb1: List[float], emb2: List[float]) -> float:
        """
        Compute Cosine Similarity between two 128-dimensional embedding vectors.
        similarity = (A · B) / (||A|| × ||B||)
        Returns a float score between -1.0 and 1.0 (typically 0.0 to 1.0 for normalized faces).
        """
        if not emb1 or not emb2 or len(emb1) != len(emb2):
            return 0.0

        vec1 = np.array(emb1, dtype=np.float32)
        vec2 = np.array(emb2, dtype=np.float32)

        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = float(np.dot(vec1, vec2) / (norm1 * norm2))
        return max(-1.0, min(1.0, similarity))
