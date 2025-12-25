import pytest
from application.data.models import Role, User, Company
from application.data.database import db

AUTH_BASE = "/auth"


@pytest.fixture(autouse=True)
def ensure_roles(app, db):
    with app.app_context():
        needed = {"applicant", "hr", "admin", "company"}
        existing = {r.name for r in Role.query.all()}
        missing = needed - existing
        for name in missing:
            db.session.add(Role(name=name, description=f"{name} role"))
        if missing:
            db.session.commit()
    yield


# ---------------------------
# 1) Register as admin — company created
# ---------------------------
def test_register_admin_creates_company(client, app):
    payload = {
        "name": "Ann Admin",
        "email": "ann.admin@company.com",
        "password": "adminpw",
        "role": "admin",
        "company_name": "AnnCo"
    }

    res = client.post(f"{AUTH_BASE}/register", json=payload)
    assert res.status_code in (200, 201), f"Unexpected status {res.status_code}: {res.get_data(as_text=True)}"

    with app.app_context():
        user = User.query.filter_by(email=payload["email"].lower()).first()
        assert user is not None, "Admin user should be created"
        assert user.role == "admin" or any(r.name == "admin" for r in user.roles), "User role not set to admin"

        company = Company.query.filter_by(user_id=user.id).first()
        assert company is not None, "Company record should be created for admin"
        assert company.company_name == payload["company_name"]
        assert company.company_email == payload["email"].lower()


# ---------------------------
# 2) Register as HR with @hr.com — NOT ALLOWED
# ---------------------------
def test_register_hr_domain_disallowed(client):
    payload = {"name": "Bad HR", "email": "someone@hr.com", "password": "pw"}
    res = client.post(f"{AUTH_BASE}/register", json=payload)
    assert res.status_code == 400, f"Expected 400 for @hr.com but got {res.status_code}: {res.get_data(as_text=True)}"
    data = res.get_json() or {}
    assert "not allowed" in (data.get("message", "")).lower()


# ---------------------------
# 3) Login as candidate/applicant (register then login)
# ---------------------------
def test_login_as_candidate_sets_cookies(client, app):
    register_payload = {
        "name": "Candidate One",
        "email": "candidate@example.com",
        "password": "candidatepw"
    }
    r = client.post(f"{AUTH_BASE}/register", json=register_payload)
    assert r.status_code in (200, 201), f"Register failed: {r.status_code} {r.get_data(as_text=True)}"

    login_payload = {"email": register_payload["email"], "password": register_payload["password"]}
    res = client.post(f"{AUTH_BASE}/login", json=login_payload)
    assert res.status_code == 200, f"Login failed: {res.status_code} {res.get_data(as_text=True)}"

    data = res.get_json()
    assert "role" in data
    assert "applicant_id" in data
    assert "successful" in data.get("message", "").lower()

    assert "Set-Cookie" in res.headers or any(k.lower().startswith("set-cookie") for k in res.headers.keys())
