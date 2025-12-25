import pytest
import json
from flask import Blueprint
from datetime import date, datetime

from application.data.database import db as _db
from application.data.models import (
    User, ApplicantProfile, PreviousExperience, PreviousEducation,
    Certification, Role
)

import application.controller.applicant.profile as applicant_profile_controller


# ---------------- Debug helpers ----------------
def show_debug(expected_status=None, expected_message=None, res=None):
    print("\n================ DEBUG OUTPUT ================")
    if expected_status is not None:
        print(f"EXPECTED STATUS: {expected_status}")
    if expected_message:
        print(f"EXPECTED MESSAGE SUBSTRING: {expected_message}")
    print(f"ACTUAL STATUS:   {res.status_code}")
    print("\n----- RAW RESPONSE BODY -----")
    print(res.get_data(as_text=True))
    print("\n----- PARSED JSON (if any) -----")
    parsed = res.get_json(silent=True)
    if parsed is None:
        print("<no json>")
    else:
        print(json.dumps(parsed, indent=2))
    print("==============================================\n")


def assert_response(res, expected_status=None, expected_message=None):
    if expected_status is not None:
        if res.status_code != expected_status:
            show_debug(expected_status, expected_message, res)
        assert res.status_code == expected_status

    if expected_message:
        parsed = res.get_json(silent=True)
        body = json.dumps(parsed).lower() if parsed else res.get_data(as_text=True).lower()
        if expected_message.lower() not in body:
            show_debug(expected_status, expected_message, res)
        assert expected_message.lower() in body


# ---------------- Register Test Routes ----------------
@pytest.fixture(scope="session", autouse=True)
def register_test_routes(app):
    bp = Blueprint("test_applicant_profile_bp", __name__)
    bp.add_url_rule(
        "/profile/<int:applicant_id>",
        view_func=applicant_profile_controller.get_full_profile,
        methods=["GET"]
    )
    app.register_blueprint(bp, url_prefix="/_test_applicant_profile")
    yield


def _url(applicant_id):
    return f"/_test_applicant_profile/profile/{applicant_id}"


# ---------------- DB Helpers ----------------
def ensure_roles(app):
    with app.app_context():
        existing = {r.name for r in Role.query.all()}
        needed = {"applicant", "hr", "admin", "company"}
        for nm in needed - existing:
            _db.session.add(Role(name=nm))
        _db.session.commit()


def create_user(app, user_id, name=None, email=None, phone=None):
    with app.app_context():
        ensure_roles(app)
        if User.query.get(user_id):
            return user_id

        u = User(
            id=user_id,
            name=name or f"User{user_id}",
            email=email or f"user{user_id}@test.local",
            phone=phone,
            password_hashed="pw"
        )
        _db.session.add(u)
        _db.session.commit()
        return u.id


def create_applicant_profile(app, user_id, **fields):
    with app.app_context():
        if not User.query.get(user_id):
            create_user(app, user_id)

        ap = ApplicantProfile.query.get(user_id)
        if not ap:
            ap = ApplicantProfile(applicant_id=user_id, name=f"Applicant{user_id}")
            _db.session.add(ap)
            _db.session.commit()

        changed = False
        for k, v in fields.items():
            if hasattr(ap, k) and v is not None:
                setattr(ap, k, v)
                changed = True

        if changed:
            _db.session.commit()

        return ap.applicant_id


# ---------------- Tests ----------------

def test_applicant_full_profile_success(client, app, tmp_path):
    user_id = 8001

    # Create applicant and profile
    create_user(app, user_id, name="John Doe", email="john@test.com", phone="12345")

    resume_path = tmp_path / "resume_test.pdf"
    resume_path.write_text("dummy resume")

    cover_path = tmp_path / "cover_test.pdf"
    cover_path.write_text("dummy cover letter")

    create_applicant_profile(
        app,
        user_id,
        name="John Doe",
        bio="Test Bio",
        skills="Python, SQL",
        location="Remote",
        resume_filename="resume_test.pdf",
        resume_file_path=str(resume_path),
        cover_letter_filename="cover_test.pdf",
        cover_letter_file_path=str(cover_path),
    )

    # Add experience, education, certification
    with app.app_context():
        exp = PreviousExperience(
            applicant_id=user_id,
            company="ACME",
            position="Developer",
            start_date=date(2022, 1, 1),
            end_date=date(2023, 1, 1),
            description="Did important work."
        )
        edu = PreviousEducation(
            applicant_id=user_id,
            university="UniTest",
            degree="BSc",
            field="CS",
            grade="A",
            grade_out_of="4.0",
            start_date=date(2018, 1, 1),
            end_date=date(2021, 1, 1)
        )
        cert = Certification(
            applicant_id=user_id,
            certificate_name="Cert1",
            issuing_organization="OrgX",
            issue_date=date(2022, 6, 1),
            expiry_date=None,
            credential_id="CRED123",
            credential_url="http://example.com"
        )
        _db.session.add_all([exp, edu, cert])
        _db.session.commit()

    # Call API
    res = client.get(_url(user_id))
    assert_response(res, expected_status=200)
    j = res.get_json()

    assert j["personal_info"]["name"] == "John Doe"
    assert j["personal_info"]["email"] == "john@test.com"
    assert j["personal_info"]["phone"] == "12345"

    assert j["skills"] == ["Python", "SQL"]

    assert j["resume"]["filename"] == "resume_test.pdf"
    assert "resume_test.pdf" in j["resume"]["path"]

    assert len(j["work_experience"]) == 1
    assert j["work_experience"][0]["company"] == "ACME"

    assert len(j["education"]) == 1
    assert j["education"][0]["university"] == "UniTest"

    assert len(j["certifications"]) == 1
    assert j["certifications"][0]["certificate_name"] == "Cert1"


def test_get_full_profile_404(client, app):
    non_existent = 999999
    res = client.get(_url(non_existent))
    assert res.status_code == 404
