import requests

BASE_URL = "http://127.0.0.1:8000/api"

def test_live_monitoring_verification():
    print("=" * 60)
    print("STARTING LIVE MONITORING MODULE VERIFICATION")
    print("=" * 60)

    # 1. GET /api/monitoring/status WITHOUT JWT -> Should return 401
    r_unauth = requests.get(f"{BASE_URL}/monitoring/status")
    print(f"1. [GET /api/monitoring/status WITHOUT Token] -> Status: {r_unauth.status_code}")
    assert r_unauth.status_code == 401, f"Expected 401 Unauthorized, got {r_unauth.status_code}"
    print("   -> Confirmed: Endpoint rejects unauthenticated requests properly.")

    # 2. Login to obtain valid JWT token
    r_auth = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@aura.edu", "password": "admin123"})
    assert r_auth.status_code == 200, f"Login failed: {r_auth.text}"
    token = r_auth.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"\n2. [POST /api/auth/login] -> JWT token obtained successfully.")

    # 3. GET /api/monitoring/status WITH JWT -> Should succeed
    r_status = requests.get(f"{BASE_URL}/monitoring/status", headers=headers)
    assert r_status.status_code == 200, f"Failed status check: {r_status.text}"
    status_data = r_status.json()
    print(f"\n3. [GET /api/monitoring/status WITH Token] -> Status: {r_status.status_code}")
    print(f"   Response Payload: active={status_data.get('active')}, camera={status_data.get('camera')}, students_detected={status_data.get('students_detected')}, last_update={status_data.get('last_update')}")
    assert "active" in status_data
    assert "camera" in status_data
    assert status_data["students_detected"] == 0

    # 4. POST /api/monitoring/start WITH JWT -> State becomes active
    r_start = requests.post(f"{BASE_URL}/monitoring/start", json={"classroom_id": 1, "fps": 30}, headers=headers)
    assert r_start.status_code == 200, f"Failed start: {r_start.text}"
    start_resp = r_start.json()
    print(f"\n4. [POST /api/monitoring/start] -> Response message: '{start_resp.get('message')}'")
    assert start_resp.get("status", {}).get("active") is True

    # 5. GET /api/monitoring/status -> Verify active state
    r_status_active = requests.get(f"{BASE_URL}/monitoring/status", headers=headers)
    assert r_status_active.status_code == 200
    st_active = r_status_active.json()
    print(f"\n5. [GET /api/monitoring/status] -> Verified active state: active={st_active.get('active')}, camera={st_active.get('camera')}")
    assert st_active.get("active") is True
    assert st_active.get("camera") is True

    # 6. POST /api/monitoring/stop WITH JWT -> State becomes inactive
    r_stop = requests.post(f"{BASE_URL}/monitoring/stop", headers=headers)
    assert r_stop.status_code == 200, f"Failed stop: {r_stop.text}"
    stop_resp = r_stop.json()
    print(f"\n6. [POST /api/monitoring/stop] -> Response message: '{stop_resp.get('message')}'")
    assert stop_resp.get("status", {}).get("active") is False

    # Verify state is inactive again
    r_status_inactive = requests.get(f"{BASE_URL}/monitoring/status", headers=headers)
    assert r_status_inactive.json().get("active") is False

    # 7. Verify Student Management still works
    r_students = requests.get(f"{BASE_URL}/students", headers=headers)
    assert r_students.status_code == 200
    print(f"\n7. [Sanity Check] Student Management: {len(r_students.json())} students loaded OK.")

    # 8. Verify Classroom Management still works
    r_classrooms = requests.get(f"{BASE_URL}/classrooms", headers=headers)
    assert r_classrooms.status_code == 200
    print(f"8. [Sanity Check] Classroom Management: {len(r_classrooms.json())} classrooms loaded OK.")

    # 9. Verify Attendance still works
    r_attendance = requests.get(f"{BASE_URL}/attendance", headers=headers)
    assert r_attendance.status_code == 200
    print(f"9. [Sanity Check] Attendance Logs: {len(r_attendance.json())} records loaded OK.")

    # 10. Verify Dashboard summary endpoint still works
    r_today = requests.get(f"{BASE_URL}/attendance/today", headers=headers)
    assert r_today.status_code == 200
    print(f"10. [Sanity Check] Dashboard Summary: Today attendance rate = {r_today.json().get('attendance_rate')}% OK.")

    print("=" * 60)
    print("ALL LIVE MONITORING VERIFICATION TESTS PASSED! (100% Verified)")
    print("=" * 60)

if __name__ == "__main__":
    test_live_monitoring_verification()
