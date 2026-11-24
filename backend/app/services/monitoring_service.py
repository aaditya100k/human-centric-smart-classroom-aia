import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from fastapi import WebSocket

from app.ai.face_detector import FaceDetector

logger = logging.getLogger("smart_classroom.monitoring")


class MonitoringService:
    """
    Monitoring Service orchestrates live classroom camera feeds,
    AI detection pipelines, and real-time face detection.

    Architecture prepared for plug-and-play integrations:
    - OpenCV VideoCapture & WebSocket frame process loop
    - Face Detection (OpenCV Haar Cascade)
    - Face Recognition (Future module - dlib / MTCNN / InsightFace)
    - Emotion Classification (Future module - FER models / ONNX / PyTorch)
    - Attention & Head Pose Estimation (Future module - MediaPipe Face Mesh)
    - ESP32 Temperature Ingest (MQTT / HTTP webhooks)
    - WebSocket real-time broadcast to connected frontend clients
    """

    _is_active: bool = False
    _camera_active: bool = False
    _classroom_id: Optional[int] = None
    _camera_index: int = 0
    _fps: int = 30
    _started_at: Optional[datetime] = None
    _last_update: datetime = datetime.now(timezone.utc)
    _students_detected: int = 0
    _attendance_processed: int = 0
    _websocket_connections: List[WebSocket] = []
    _attendance_cooldown: Dict[Any, float] = {}
    _cooldown_seconds: float = 60.0

    _face_detector: Optional[FaceDetector] = None
    _face_recognizer: Optional[Any] = None

    @classmethod
    def get_face_detector(cls) -> FaceDetector:
        if cls._face_detector is None:
            cls._face_detector = FaceDetector()
        return cls._face_detector

    @classmethod
    def get_face_recognizer(cls):
        if cls._face_recognizer is None:
            from app.ai.face_recognizer import FaceRecognizer
            cls._face_recognizer = FaceRecognizer()
        return cls._face_recognizer

    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        uptime_seconds = 0
        now = datetime.now(timezone.utc)
        if cls._is_active and cls._started_at:
            uptime_seconds = int((now - cls._started_at).total_seconds())

        detector = cls.get_face_detector()
        recognizer = cls.get_face_recognizer()

        return {
            "active": cls._is_active,
            "is_active": cls._is_active,
            "camera": cls._camera_active,
            "classroom_id": cls._classroom_id,
            "camera_index": cls._camera_index,
            "fps": cls._fps,
            "started_at": cls._started_at.isoformat() if cls._started_at else None,
            "uptime_seconds": uptime_seconds,
            "students_detected": cls._students_detected,
            "attendance_processed": cls._attendance_processed,
            "last_update": cls._last_update.isoformat(),
            "status_message": "Monitoring Active" if cls._is_active else "Monitoring Stopped",
            "modules": {
                "opencv_capture": "ready",
                "face_detection": "active" if detector.is_loaded() else "unavailable",
                "face_recognition": "active" if recognizer.is_loaded() else "ready",
                "auto_attendance": "active" if (cls._is_active and cls._classroom_id is not None) else "ready",
                "emotion_detection": "not_implemented",
                "attention_monitoring": "not_implemented",
                "esp32_sensor": "disconnected",
                "websocket_stream": "ready",
            },
        }

    @classmethod
    async def start_monitoring(
        cls,
        classroom_id: Optional[int] = None,
        camera_index: int = 0,
        fps: int = 30,
        camera_active: bool = True
    ) -> Dict[str, Any]:
        cls._is_active = True
        cls._camera_active = camera_active
        cls._classroom_id = classroom_id
        cls._camera_index = camera_index
        cls._fps = fps
        cls._started_at = datetime.now(timezone.utc)
        cls._last_update = datetime.now(timezone.utc)

        logger.info(
            f"Monitoring session started for Classroom {classroom_id} "
            f"on Camera {camera_index} at {fps} FPS."
        )

        status_data = cls.get_status()
        await cls.broadcast_ws_message({"event": "monitoring_started", "data": status_data})

        return {
            "success": True,
            "message": f"Monitoring successfully started for Classroom {classroom_id}",
            "status": status_data,
        }

    @classmethod
    async def stop_monitoring(cls) -> Dict[str, Any]:
        cls._is_active = False
        cls._camera_active = False
        previous_classroom = cls._classroom_id
        cls._classroom_id = None
        cls._started_at = None
        cls._last_update = datetime.now(timezone.utc)
        cls._students_detected = 0

        logger.info(f"Monitoring session stopped for Classroom {previous_classroom}.")

        status_data = cls.get_status()
        await cls.broadcast_ws_message({"event": "monitoring_stopped", "data": status_data})

        return {
            "success": True,
            "message": f"Monitoring stopped for Classroom {previous_classroom}",
            "status": status_data,
        }

    @classmethod
    def set_camera_state(cls, camera_active: bool):
        cls._camera_active = camera_active
        cls._last_update = datetime.now(timezone.utc)

    @classmethod
    def process_frame(cls, image_bytes: bytes, db: Optional[Any] = None) -> Dict[str, Any]:
        """
        Process incoming webcam frame bytes via OpenCV FaceDetector & FaceRecognizer.
        Performs automatic Face AI attendance marking when face is recognized and classroom session is active.
        No raw images or frames are saved permanently.
        """
        import time
        import cv2
        import numpy as np
        from app.database import SessionLocal
        from app.services.face_recognition_service import FaceRecognitionService
        from app.services.attendance_service import AttendanceService

        now_iso = datetime.now(timezone.utc).isoformat()
        if not image_bytes:
            return {"type": "face_recognition", "faces_detected": 0, "faces": [], "timestamp": now_iso}

        detector = cls.get_face_detector()
        recognizer = cls.get_face_recognizer()

        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            return {"type": "face_recognition", "faces_detected": 0, "faces": [], "timestamp": now_iso}

        detection = detector.detect_faces_in_frame(frame)
        face_boxes = detection.get("faces", [])

        db_created = False
        if db is None:
            try:
                db = SessionLocal()
                db_created = True
            except Exception as db_err:
                logger.warning(f"Could not open DB session for face recognition matching: {db_err}")
                db = None

        recognized_faces = []
        for bbox in face_boxes:
            face_item = {
                "x": bbox["x"],
                "y": bbox["y"],
                "width": bbox["width"],
                "height": bbox["height"],
                "recognized": False,
                "student_id": None,
                "name": "Unknown",
                "similarity": 0.0,
                "attendance": {
                    "status": "not_marked"
                }
            }

            if recognizer.is_loaded() and db is not None:
                try:
                    emb = recognizer.extract_embedding(frame, bbox=bbox)
                    if emb:
                        match_res = FaceRecognitionService.match_face(emb, db)
                        face_item["recognized"] = match_res["recognized"]
                        face_item["student_id"] = match_res["student_id"]
                        face_item["name"] = match_res["name"]
                        face_item["similarity"] = match_res["similarity"]

                        # Phase 4 Automatic Face Attendance Trigger
                        if match_res["recognized"] and match_res["student_id"]:
                            student_id = match_res["student_id"]
                            active_room = cls._classroom_id

                            # Privacy Enforcement: Check emotion inference consent
                            from app.services.privacy_service import PrivacyService
                            if not PrivacyService.has_emotion_consent(db, student_id):
                                face_item["emotion"] = {
                                    "status": "withheld",
                                    "reason": "Emotion inference consent absent or revoked"
                                }
                            else:
                                face_item["emotion"] = {
                                    "status": "not_implemented",
                                    "detail": "Emotion Analysis: Not Implemented"
                                }

                            if active_room is not None:
                                cache_key = (student_id, active_room)
                                now_ts = time.time()
                                last_ts = cls._attendance_cooldown.get(cache_key, 0.0)

                                if (now_ts - last_ts) < cls._cooldown_seconds:
                                    face_item["attendance"] = {
                                        "status": "already_marked",
                                        "verification_method": "Face AI"
                                    }
                                else:
                                    # Perform DB verification and attendance marking
                                    att_res = AttendanceService.record_face_attendance(
                                        db=db,
                                        student_id=student_id,
                                        classroom_id=active_room,
                                        confidence=match_res["similarity"]
                                    )
                                    cls._attendance_cooldown[cache_key] = now_ts

                                    if att_res.get("status") == "marked":
                                        cls._attendance_processed += 1

                                    face_item["attendance"] = {
                                        "status": att_res.get("status", "marked"),
                                        "verification_method": "Face AI"
                                    }
                            else:
                                face_item["attendance"] = {
                                    "status": "not_marked",
                                    "reason": "No active classroom selected"
                                }
                except Exception as match_err:
                    logger.warning(f"Face matching / attendance error: {match_err}")

            recognized_faces.append(face_item)

        if db_created and db:
            db.close()

        recognized_count = sum(1 for f in recognized_faces if f.get("recognized"))
        unknown_count = len(recognized_faces) - recognized_count
        cls._students_detected = len(recognized_faces)
        cls._last_update = datetime.now(timezone.utc)

        return {
            "type": "face_recognition",
            "faces_detected": len(recognized_faces),
            "recognized_count": recognized_count,
            "unknown_count": unknown_count,
            "faces": recognized_faces,
            "timestamp": now_iso
        }

    # =========================================================================
    # WEBSOCKET REAL-TIME BROADCAST MANAGER
    # =========================================================================

    @classmethod
    async def connect_ws(cls, websocket: WebSocket):
        await websocket.accept()
        if websocket not in cls._websocket_connections:
            cls._websocket_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total connections: {len(cls._websocket_connections)}")
        try:
            await websocket.send_json({"event": "connection_established", "data": cls.get_status()})
        except Exception as e:
            logger.error(f"Error sending initial WS message: {e}")

    @classmethod
    def disconnect_ws(cls, websocket: WebSocket):
        if websocket in cls._websocket_connections:
            cls._websocket_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Remaining connections: {len(cls._websocket_connections)}")

    @classmethod
    async def broadcast_ws_message(cls, message: Dict[str, Any]):
        disconnected = []
        for ws in cls._websocket_connections:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            cls.disconnect_ws(ws)
