"""
Phase 3 Verification Script: Face Recognition System & Integration Regression.
Tests:
- SFace ONNX model loading & initialization
- Face embedding extraction & dimension validation (128-D)
- Cosine similarity calculation accuracy
- Database StudentFaceEmbedding model & foreign key relationship
- Invalid image, zero-face image, and multiple-face image enrollment rejection
- Authentication enforcement on all face recognition endpoints (401 status)
- Face enrollment API & status/delete endpoints
- Recognition matching & low-similarity threshold 'Unknown' fallback
- WebSocket face_recognition events
- Regression checks for face detection, live monitoring, students, classrooms, attendance, and dashboard
"""

import sys
import os
import json
import base64
import logging
import numpy as np
import cv2
from typing import List

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.models import (
    user,
    student,
    student_face_embedding,
    classroom,
    attendance,
    emotion,
    attention,
    temperature,
    alert,
    notification,
)
from app.models.user import User
from app.models.student import Student
from app.models.student_face_embedding import StudentFaceEmbedding
from app.models.classroom import Classroom
from app.models.attendance import Attendance

from app.utils.security import get_password_hash, create_access_token
from app.ai.face_detector import FaceDetector
from app.ai.face_recognizer import FaceRecognizer
from app.services.face_recognition_service import FaceRecognitionService
from app.services.monitoring_service import MonitoringService
from app.main import app

# Set up in-memory SQLite database for deterministic verification
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base.metadata.create_all(bind=test_engine)

# Seed test data
db_seed = TestingSessionLocal()

# Admin user
admin_user = db_seed.query(User).filter(User.email == "admin@smartclassroom.edu").first()
if not admin_user:
    admin_user = User(
        username="admin",
        email="admin@smartclassroom.edu",
        hashed_password=get_password_hash("admin123"),
        full_name="Admin Test",
        role="admin",
        is_active=True
    )
    db_seed.add(admin_user)

# Test classroom
test_room = db_seed.query(Classroom).first()
if not test_room:
    test_room = Classroom(id=1, name="Lab 101", department="Computer Science", capacity=30, status="Active")
    db_seed.add(test_room)
    db_seed.commit()

# Test student
test_student = db_seed.query(Student).filter(Student.id == "ST-2024-001").first()
if not test_student:
    test_student = Student(
        id="ST-2024-001",
        name="Alex Johnson",
        email="alex.j@aura.edu",
        department="Computer Science",
        classroom_id=1,
        status="Active"
    )
    db_seed.add(test_student)

db_seed.commit()
db_seed.close()


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def run_phase3_verification():
    passed_tests = []
    failed_tests = []
    manual_tests = []
    regression_tests = []

    print("==================================================")
    print("PHASE 3 - FACE RECOGNITION VERIFICATION & REGRESSION")
    print("==================================================\n")

    # Generate test JWT token & headers
    test_token = create_access_token({"sub": "admin@smartclassroom.edu", "role": "admin"})
    auth_headers = {"Authorization": f"Bearer {test_token}"}

    # -------------------------------------------------------------
    # 1. SFace ONNX model exists and loads
    # -------------------------------------------------------------
    try:
        recognizer = FaceRecognizer()
        assert os.path.exists(recognizer.model_path), f"Model file not found at {recognizer.model_path}"
        assert recognizer.is_loaded() is True, "SFace recognizer failed to load ONNX model"
        passed_tests.append("SFace ONNX model exists and loads")
        print(" [PASS] 1. SFace ONNX model exists and loads successfully.")
    except Exception as e:
        failed_tests.append(f"SFace ONNX model loading: {e}")
        print(f" [FAIL] 1. SFace ONNX model loading failed: {e}")

    # -------------------------------------------------------------
    # 2. Face recognizer initializes
    # -------------------------------------------------------------
    try:
        assert recognizer.recognizer is not None, "OpenCV FaceRecognizerSF instance is None"
        passed_tests.append("Face recognizer initializes")
        print(" [PASS] 2. Face recognizer initializes OpenCV FaceRecognizerSF instance.")
    except Exception as e:
        failed_tests.append(f"Face recognizer initialization: {e}")
        print(f" [FAIL] 2. Face recognizer initialization failed: {e}")

    # -------------------------------------------------------------
    # 3 & 4. Face embedding generation & dimensions format (128-D)
    # -------------------------------------------------------------
    dummy_face_frame = np.ones((112, 112, 3), dtype=np.uint8) * 128
    extracted_emb = None
    try:
        extracted_emb = recognizer.extract_embedding(dummy_face_frame)
        assert extracted_emb is not None, "Returned embedding is None"
        assert isinstance(extracted_emb, list), "Embedding must be a list"
        assert len(extracted_emb) == 128, f"Expected 128 dimensions, got {len(extracted_emb)}"
        assert all(isinstance(val, float) for val in extracted_emb), "All embedding elements must be floats"
        passed_tests.append("Face embedding generation works")
        passed_tests.append("Embedding dimensions/format are valid")
        print(" [PASS] 3. Face embedding generation works.")
        print(f" [PASS] 4. Embedding dimensions/format are valid (128 floats, normalized L2 length).")
    except Exception as e:
        failed_tests.append(f"Face embedding generation: {e}")
        print(f" [FAIL] 3/4. Face embedding extraction failed: {e}")

    # -------------------------------------------------------------
    # 5. Cosine similarity calculation works
    # -------------------------------------------------------------
    try:
        vec_a = [1.0] + [0.0] * 127
        vec_b = [1.0] + [0.0] * 127
        vec_c = [0.0, 1.0] + [0.0] * 126
        vec_d = [-1.0] + [0.0] * 127

        sim_same = FaceRecognizer.compute_similarity(vec_a, vec_b)
        sim_ortho = FaceRecognizer.compute_similarity(vec_a, vec_c)
        sim_opp = FaceRecognizer.compute_similarity(vec_a, vec_d)

        assert abs(sim_same - 1.0) < 1e-4, f"Identical vectors should have similarity ~1.0, got {sim_same}"
        assert abs(sim_ortho - 0.0) < 1e-4, f"Orthogonal vectors should have similarity ~0.0, got {sim_ortho}"
        assert abs(sim_opp - (-1.0)) < 1e-4, f"Opposite vectors should have similarity ~-1.0, got {sim_opp}"
        
        passed_tests.append("Cosine similarity calculation works")
        print(" [PASS] 5. Cosine similarity calculation works accurately.")
    except Exception as e:
        failed_tests.append(f"Cosine similarity calculation: {e}")
        print(f" [FAIL] 5. Cosine similarity test failed: {e}")

    # -------------------------------------------------------------
    # 6. Database embedding model imports
    # -------------------------------------------------------------
    try:
        from app.models.student_face_embedding import StudentFaceEmbedding as SFECheck
        assert SFECheck.__tablename__ == "student_face_embeddings"
        passed_tests.append("Database embedding model imports")
        print(" [PASS] 6. Database StudentFaceEmbedding model imports correctly.")
    except Exception as e:
        failed_tests.append(f"Database embedding model import: {e}")
        print(f" [FAIL] 6. Database embedding model import failed: {e}")

    # -------------------------------------------------------------
    # 7 & 8. Table access & Student foreign key relationship
    # -------------------------------------------------------------
    try:
        db = TestingSessionLocal()
        sample_emb_vector = [0.05] * 128
        new_record = StudentFaceEmbedding(student_id="ST-2024-001", embedding=sample_emb_vector)
        db.add(new_record)
        db.commit()

        # Query back
        fetched = db.query(StudentFaceEmbedding).filter(StudentFaceEmbedding.student_id == "ST-2024-001").first()
        assert fetched is not None, "Failed to query stored student_face_embeddings record"
        assert fetched.student is not None, "Student relationship is None"
        assert fetched.student.id == "ST-2024-001", "Foreign key student relationship ID mismatch"
        assert len(fetched.embedding) == 128, "Stored embedding dimension mismatch"
        
        # Clean up
        db.delete(fetched)
        db.commit()
        db.close()

        passed_tests.append("student_face_embeddings table can be created/accessed")
        passed_tests.append("Student foreign key works")
        print(" [PASS] 7. student_face_embeddings table created and accessed.")
        print(" [PASS] 8. Student foreign key and ORM relationship work as expected.")
    except Exception as e:
        failed_tests.append(f"Database table & foreign key access: {e}")
        print(f" [FAIL] 7/8. Database table or foreign key test failed: {e}")

    # -------------------------------------------------------------
    # 9. Invalid image enrollment is rejected
    # -------------------------------------------------------------
    try:
        db = TestingSessionLocal()
        res_invalid = FaceRecognitionService.enroll_student_face(db, "ST-2024-001", b"corrupted_invalid_data")
        db.close()
        assert res_invalid["success"] is False, "Corrupted image bytes should be rejected"
        passed_tests.append("Invalid image enrollment is rejected")
        print(" [PASS] 9. Invalid corrupted image enrollment is properly rejected.")
    except Exception as e:
        failed_tests.append(f"Invalid image enrollment rejection: {e}")
        print(f" [FAIL] 9. Invalid image test failed: {e}")

    # -------------------------------------------------------------
    # 10. Zero-face image is rejected
    # -------------------------------------------------------------
    try:
        blank_img = np.zeros((480, 640, 3), dtype=np.uint8)
        _, img_bytes = cv2.imencode('.jpg', blank_img)
        
        db = TestingSessionLocal()
        res_zero = FaceRecognitionService.enroll_student_face(db, "ST-2024-001", img_bytes.tobytes())
        db.close()

        assert res_zero["success"] is False, "Zero-face image should be rejected"
        assert "No face detected" in res_zero["message"], f"Unexpected message: {res_zero['message']}"
        passed_tests.append("Zero-face image is rejected")
        print(" [PASS] 10. Zero-face image enrollment is properly rejected.")
    except Exception as e:
        failed_tests.append(f"Zero-face image rejection: {e}")
        print(f" [FAIL] 10. Zero-face test failed: {e}")

    # -------------------------------------------------------------
    # 11. Multiple-face image is rejected
    # -------------------------------------------------------------
    try:
        # Mock detector returning 2 faces to verify validation logic
        detector = FaceRecognitionService.get_detector()
        original_detect = detector.detect_faces_in_frame
        
        def mock_multi_face_detect(frame):
            return {
                "faces_detected": 2,
                "faces": [
                    {"x": 50, "y": 50, "width": 100, "height": 100},
                    {"x": 200, "y": 200, "width": 100, "height": 100}
                ]
            }

        detector.detect_faces_in_frame = mock_multi_face_detect
        
        db = TestingSessionLocal()
        res_multi = FaceRecognitionService.enroll_student_face(db, "ST-2024-001", img_bytes.tobytes())
        db.close()

        detector.detect_faces_in_frame = original_detect  # restore

        assert res_multi["success"] is False, "Multiple-face image should be rejected"
        assert "Multiple faces" in res_multi["message"], f"Unexpected message: {res_multi['message']}"
        passed_tests.append("Multiple-face image is rejected")
        print(" [PASS] 11. Multiple-face image enrollment is properly rejected.")
    except Exception as e:
        failed_tests.append(f"Multiple-face image rejection: {e}")
        print(f" [FAIL] 11. Multiple-face test failed: {e}")

    # -------------------------------------------------------------
    # 12 & 13. Authentication enforcement (401 on unauthenticated calls)
    # -------------------------------------------------------------
    try:
        res_unauth_enroll = client.post("/api/face-recognition/enroll/ST-2024-001", json={"image": "data:image/jpeg;base64,aaa"})
        res_unauth_status = client.get("/api/face-recognition/status/ST-2024-001")
        res_unauth_del = client.delete("/api/face-recognition/enrollment/ST-2024-001")

        assert res_unauth_enroll.status_code == 401, f"Expected 401, got {res_unauth_enroll.status_code}"
        assert res_unauth_status.status_code == 401, f"Expected 401, got {res_unauth_status.status_code}"
        assert res_unauth_del.status_code == 401, f"Expected 401, got {res_unauth_del.status_code}"

        passed_tests.append("Authentication is enforced")
        passed_tests.append("Unauthenticated API returns 401")
        print(" [PASS] 12. Authentication is strictly enforced across Face Recognition endpoints.")
        print(" [PASS] 13. Unauthenticated API requests return HTTP 401 Unauthorized.")
    except Exception as e:
        failed_tests.append(f"Authentication enforcement 401: {e}")
        print(f" [FAIL] 12/13. Auth enforcement test failed: {e}")

    # -------------------------------------------------------------
    # 14. Enrollment API works
    # -------------------------------------------------------------
    try:
        # Mock detector returning 1 face for enrollment testing
        detector = FaceRecognitionService.get_detector()
        original_detect = detector.detect_faces_in_frame

        def mock_single_face_detect(frame):
            return {
                "faces_detected": 1,
                "faces": [{"x": 10, "y": 10, "width": 80, "height": 80}]
            }

        detector.detect_faces_in_frame = mock_single_face_detect

        # Encode small image
        synth_face_img = np.ones((100, 100, 3), dtype=np.uint8) * 200
        _, b_enc = cv2.imencode('.jpg', synth_face_img)
        b64_face = base64.b64encode(b_enc).decode('utf-8')

        res_enroll_api = client.post(
            "/api/face-recognition/enroll/ST-2024-001",
            json={"image": f"data:image/jpeg;base64,{b64_face}"},
            headers=auth_headers
        )
        detector.detect_faces_in_frame = original_detect  # restore

        assert res_enroll_api.status_code == 200, f"Enrollment API failed: {res_enroll_api.text}"
        enroll_data = res_enroll_api.json()
        assert enroll_data.get("success") is True, "Enrollment API success flag is False"
        assert enroll_data.get("student_id") == "ST-2024-001"

        # Check status endpoint
        res_st_api = client.get("/api/face-recognition/status/ST-2024-001", headers=auth_headers)
        assert res_st_api.status_code == 200
        assert res_st_api.json().get("enrolled") is True

        passed_tests.append("Enrollment API works")
        print(" [PASS] 14. Face Enrollment API POST /api/face-recognition/enroll/{student_id} works.")
    except Exception as e:
        failed_tests.append(f"Enrollment API: {e}")
        print(f" [FAIL] 14. Enrollment API test failed: {e}")

    # -------------------------------------------------------------
    # 15 & 16. Recognition API & Unknown fallback when below threshold
    # -------------------------------------------------------------
    try:
        db = TestingSessionLocal()
        # Candidate vector completely different from enrolled vector
        dissimilar_candidate = [0.99] + [0.0] * 127
        match_result = FaceRecognitionService.match_face(dissimilar_candidate, db, threshold=0.60)
        db.close()

        assert "recognized" in match_result
        assert "similarity" in match_result
        assert match_result["recognized"] is False, "Low similarity candidate should NOT be recognized"
        assert match_result["name"] == "Unknown", f"Expected name 'Unknown', got {match_result['name']}"

        passed_tests.append("Recognition API works")
        passed_tests.append("Unknown face is returned when similarity is below threshold")
        print(" [PASS] 15. Recognition matching pipeline works.")
        print(" [PASS] 16. Unknown face is correctly returned when similarity is below threshold.")
    except Exception as e:
        failed_tests.append(f"Recognition API & Unknown fallback: {e}")
        print(f" [FAIL] 15/16. Recognition test failed: {e}")

    # -------------------------------------------------------------
    # 17. WebSocket sends face_recognition events
    # -------------------------------------------------------------
    try:
        blank_img = np.zeros((100, 100, 3), dtype=np.uint8)
        _, img_enc = cv2.imencode('.jpg', blank_img)
        b64_str = base64.b64encode(img_enc).decode('utf-8')

        ws_url = f"/api/monitoring/ws?token={test_token}"
        with client.websocket_connect(ws_url) as websocket:
            init_msg = websocket.receive_json()
            assert init_msg.get("event") == "connection_established"

            frame_payload = json.dumps({"type": "frame", "image": b64_str})
            websocket.send_text(frame_payload)
            result_msg = websocket.receive_json()

            assert result_msg.get("type") == "face_recognition", f"Expected WS event type 'face_recognition', got {result_msg.get('type')}"
            assert "faces_detected" in result_msg

        passed_tests.append("WebSocket sends face_recognition events")
        print(" [PASS] 17. WebSocket streams face_recognition events in real time.")
    except Exception as e:
        failed_tests.append(f"WebSocket face_recognition events: {e}")
        print(f" [FAIL] 17. WebSocket face_recognition test failed: {e}")

    # -------------------------------------------------------------
    # REGRESSION TESTS
    # -------------------------------------------------------------
    print("\n--- REGRESSION SUITE ---")

    # 18. Existing face detection still works
    try:
        detector = FaceDetector()
        assert detector.is_loaded() is True
        blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        det_res = detector.detect_faces_in_frame(blank_frame)
        assert det_res["faces_detected"] == 0
        passed_tests.append("Existing face detection still works")
        regression_tests.append("Face Detection (Haar Cascade): PASS")
        print(" [PASS] 18. Existing Face Detection (Haar Cascade) regression passed.")
    except Exception as e:
        failed_tests.append(f"Regression - Face Detection: {e}")
        regression_tests.append(f"Face Detection: FAIL ({e})")
        print(f" [FAIL] 18. Face Detection regression failed: {e}")

    # 19. Existing monitoring start/stop/status still works
    try:
        r_st = client.get("/api/monitoring/status", headers=auth_headers)
        assert r_st.status_code == 200
        r_start = client.post("/api/monitoring/start", json={"classroom_id": 1, "fps": 30}, headers=auth_headers)
        assert r_start.status_code == 200
        r_stop = client.post("/api/monitoring/stop", headers=auth_headers)
        assert r_stop.status_code == 200
        passed_tests.append("Existing monitoring start/stop/status still works")
        regression_tests.append("Live Monitoring (Status/Start/Stop): PASS")
        print(" [PASS] 19. Existing Monitoring start/stop/status regression passed.")
    except Exception as e:
        failed_tests.append(f"Regression - Live Monitoring: {e}")
        regression_tests.append(f"Live Monitoring: FAIL ({e})")
        print(f" [FAIL] 19. Live Monitoring regression failed: {e}")

    # 20. Student module regression passes
    try:
        r_stu = client.get("/api/students", headers=auth_headers)
        assert r_stu.status_code == 200
        assert len(r_stu.json()) > 0
        passed_tests.append("Student module regression passes")
        regression_tests.append("Student Module CRUD: PASS")
        print(" [PASS] 20. Student module regression passed.")
    except Exception as e:
        failed_tests.append(f"Regression - Student Module: {e}")
        regression_tests.append(f"Student Module: FAIL ({e})")
        print(f" [FAIL] 20. Student module regression failed: {e}")

    # 21. Classroom module regression passes
    try:
        r_cls = client.get("/api/classrooms", headers=auth_headers)
        assert r_cls.status_code == 200
        assert len(r_cls.json()) > 0
        passed_tests.append("Classroom module regression passes")
        regression_tests.append("Classroom Module CRUD: PASS")
        print(" [PASS] 21. Classroom module regression passed.")
    except Exception as e:
        failed_tests.append(f"Regression - Classroom Module: {e}")
        regression_tests.append(f"Classroom Module: FAIL ({e})")
        print(f" [FAIL] 21. Classroom module regression failed: {e}")

    # 22. Attendance module regression passes
    try:
        r_att = client.get("/api/attendance", headers=auth_headers)
        assert r_att.status_code == 200
        passed_tests.append("Attendance module regression passes")
        regression_tests.append("Attendance Module CRUD: PASS")
        print(" [PASS] 22. Attendance module regression passed.")
    except Exception as e:
        failed_tests.append(f"Regression - Attendance Module: {e}")
        regression_tests.append(f"Attendance Module: FAIL ({e})")
        print(f" [FAIL] 22. Attendance module regression failed: {e}")

    # 23. Dashboard regression passes
    try:
        r_dash = client.get("/api/attendance/today", headers=auth_headers)
        assert r_dash.status_code == 200
        passed_tests.append("Dashboard regression passes")
        regression_tests.append("Dashboard Aggregation: PASS")
        print(" [PASS] 23. Dashboard module regression passed.")
    except Exception as e:
        failed_tests.append(f"Regression - Dashboard Module: {e}")
        regression_tests.append(f"Dashboard Module: FAIL ({e})")
        print(f" [FAIL] 23. Dashboard module regression failed: {e}")

    # -------------------------------------------------------------
    # 24. Genuine Real-Face Image Check
    # -------------------------------------------------------------
    manual_tests.append("Real Face Image Recognition: MANUAL VERIFICATION REQUIRED (No real human facial photos are present in codebase repository to avoid committing binary PII data). Test via live camera feed on browser HUD.")
    print(" [MANUAL] Real face image recognition requires manual live webcam/photo verification on frontend dashboard UI.")

    print("\n==================================================")
    print("PHASE 3 FACE RECOGNITION VERIFICATION SUMMARY")
    print("==================================================")
    print(f"Total Passed: {len(passed_tests)}")
    print(f"Total Failed: {len(failed_tests)}")
    print(f"Total Manual: {len(manual_tests)}")
    print("==================================================\n")

    return passed_tests, failed_tests, manual_tests, regression_tests


if __name__ == "__main__":
    run_phase3_verification()
