import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api"

def test_authentication_system():
    print("=" * 60)
    print("STARTING AUTHENTICATION & LOGIN END-TO-END VERIFICATION")
    print("=" * 60)

    test_timestamp = int(datetime.now().timestamp())
    test_username = f"testuser_{test_timestamp}"
    test_email = f"user_{test_timestamp}@aura.edu"
    test_password = "SecurePassword123!"

    # 1. Register a test user
    reg_payload = {
        "username": test_username,
        "email": test_email,
        "password": test_password,
        "full_name": "Test Faculty User",
        "role": "teacher"
    }
    r_reg = requests.post(f"{BASE_URL}/auth/register", json=reg_payload)
    print(f"1. [POST /api/auth/register] -> Status: {r_reg.status_code}")
    assert r_reg.status_code == 201, f"Failed to register user: {r_reg.text}"
    reg_data = r_reg.json()
    assert "access_token" in reg_data, "No access token returned in registration!"
    print(f"   Registered user '{test_username}' ({test_email}) successfully.")

    # 2. Login with test user using email
    login_payload_email = {
        "email": test_email,
        "password": test_password
    }
    r_login = requests.post(f"{BASE_URL}/auth/login", json=login_payload_email)
    print(f"2. [POST /api/auth/login (Email)] -> Status: {r_login.status_code}")
    assert r_login.status_code == 200, f"Login failed: {r_login.text}"
    login_data = r_login.json()
    token = login_data["access_token"]
    assert token, "No token in login response!"
    print(f"   JWT token received: {token[:25]}...")

    # 3. Login with default admin demo credentials using username
    login_payload_user = {
        "email": "admin",
        "password": "admin123"
    }
    r_admin = requests.post(f"{BASE_URL}/auth/login", json=login_payload_user)
    print(f"3. [POST /api/auth/login (Username 'admin')] -> Status: {r_admin.status_code}")
    assert r_admin.status_code == 200, f"Admin login failed: {r_admin.text}"

    # 4. GET /api/auth/me (Authenticated user profile)
    headers = {"Authorization": f"Bearer {token}"}
    r_me = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"4. [GET /api/auth/me] -> Status: {r_me.status_code}")
    assert r_me.status_code == 200, f"Failed to fetch profile: {r_me.text}"
    me_data = r_me.json()
    print(f"   Authenticated User: {me_data['full_name']} | Role: {me_data['role']}")
    assert me_data["email"] == test_email

    # 5. Call protected endpoint WITH token (Should succeed: 200 OK)
    r_protected = requests.get(f"{BASE_URL}/students", headers=headers)
    print(f"5. [GET /api/students WITH Token] -> Status: {r_protected.status_code}")
    assert r_protected.status_code == 200, f"Protected route rejected valid token: {r_protected.text}"

    # 6. Call protected endpoint WITHOUT token (Should fail: 401 Unauthorized)
    r_unauth = requests.get(f"{BASE_URL}/students")
    print(f"6. [GET /api/students WITHOUT Token] -> Status: {r_unauth.status_code}")
    assert r_unauth.status_code == 401, f"Expected 401 Unauthorized, got {r_unauth.status_code}: {r_unauth.text}"
    print(f"   Unauthenticated request rejected with: {r_unauth.json().get('detail')}")

    # 7. Public endpoint /api/health (Should succeed without token)
    r_health = requests.get(f"{BASE_URL}/health")
    print(f"7. [GET /api/health (Public)] -> Status: {r_health.status_code}")
    assert r_health.status_code == 200

    # 8. Direct MySQL Check for hashed password
    from app.database import SessionLocal
    from app.models.user import User
    db = SessionLocal()
    db_user = db.query(User).filter(User.email == test_email).first()
    assert db_user is not None
    assert db_user.hashed_password.startswith("$2b$") or db_user.hashed_password.startswith("$2a$"), "Password is not bcrypt hashed!"
    print(f"8. [Direct MySQL Check] User '{db_user.username}' stored in MySQL table 'users' with secure bcrypt hash: {db_user.hashed_password[:20]}...")
    db.close()

    print("=" * 60)
    print("ALL AUTHENTICATION & LOGIN TESTS PASSED! (100% Verified)")
    print("=" * 60)

if __name__ == "__main__":
    test_authentication_system()
