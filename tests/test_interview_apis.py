# tests/test_interview_apis.py
import pytest
import json
from datetime import date, time, datetime
from werkzeug.security import generate_password_hash
from flask import Blueprint
from flask_restful import Api as RestfulApi

from application.data.database import db as _db
from application.data.models import (
    User, Company, HRProfile, JobPosting, ApplicantProfile,
    Role, Application, Interview
)

# Resource under test
from application.controller.apis.interview_apis import InterviewApi

# ---------------- Debug helpers ----------------
def show_debug(expected_status=None, expected_message=None, res=None):
    print("\n================ DEBUG OUTPUT ================")
    if expected_status is not None:
        print(f"EXPECTED STATUS: {expected_status}")
    if expected_message:
        print(f"EXPECTED MESSAGE SUBSTRING: {expected_message}")
    print(f"ACTUAL STATUS:   {res.status_code}")
    print("\n----- RAW RESPONSE BODY -----")
    try:
        print(res.get_data(as_text=True))
    except Exception as e:
        print(f"<could not read body: {e}>")
    print("\n----- PARSED JSON (if any) -----")
    try:
        parsed = res.get_json(silent=True)
        if parsed is None:
            print("<no json>")
        else:
            print(json.dumps(parsed, indent=2, default=str))
    except Exception as e:
        print(f"<json parse error: {e}>")
    print("==============================================\n")

def assert_response(res, expected_status=None, expected_message=None):
    if expected_status is not None and res.status_code != expected_status:
        show_debug(expected_status=expected_status, expected_message=expected_message, res=res)
    assert expected_status is None or res.status_code == expected_status

    if expected_message:
        parsed = res.get_json(silent=True)
        body_text = json.dumps(parsed, indent=2) if parsed is not None else res.get_data(as_text=True)
        if expected_message.lower() not in str(body_text).lower():
            show_debug(expected_status=expected_status, expected_message=expected_message, res=res)
        assert expected_message.lower() in str(body_text).lower()

# -------------- Register test-only routes --------------
@pytest.fixture(scope="session", autouse=True)
def register_test_routes(app):
    bp = Blueprint("test_interview_bp", __name__)
    api = RestfulApi(bp)
    api.add_resource(InterviewApi, "/interview", "/interview/<int:interview_id>")
    app.register_blueprint(bp, url_prefix="/_test_interview")
    yield

def _base():
    return "/_test_interview/interview"
def _single(iid):
    return f"{_base()}/{iid}"

# -------------- DB helper functions (return IDs only) --------------
def ensure_roles(app):
    with app.app_context():
        existing = {r.name for r in Role.query.all()}
        needed = {"applicant", "hr", "admin", "company"}
        for nm in needed - existing:
            _db.session.add(Role(name=nm, description=f"{nm} role"))
        _db.session.commit()

def create_user_id(app, user_id, email=None, name=None):
    with app.app_context():
        ensure_roles(app)
        email = email or f"user{user_id}@test.local"
        u = User(id=user_id, name=(name or f"User{user_id}"), email=email, password_hashed=generate_password_hash("pw"))
        _db.session.add(u)
        _db.session.commit()
        return u.id

def create_company_id(app, owner_user_id, company_name="ACME Co"):
    with app.app_context():
        c = Company(company_name=company_name, user_id=owner_user_id, company_email=f"{company_name.lower()}@test")
        _db.session.add(c)
        _db.session.commit()
        return c.id

def create_hr_profile_id(app, hr_user_id, company_id, first_name="HR", last_name="Person"):
    with app.app_context():
        hr = HRProfile(hr_id=hr_user_id, company_id=company_id, first_name=first_name, last_name=last_name, contact_email=f"hr{hr_user_id}@test")
        _db.session.add(hr)
        _db.session.commit()
        return hr.hr_id

def create_job_id(app, hr_id, company_id, title="Engineer"):
    with app.app_context():
        job = JobPosting(hr_id=hr_id, company_id=company_id, job_title=title)
        _db.session.add(job)
        _db.session.commit()
        return job.id

def create_applicant_id(app, user_id, name="Applicant"):
    with app.app_context():
        ap = ApplicantProfile(applicant_id=user_id, name=name)
        _db.session.add(ap)
        _db.session.commit()
        return ap.applicant_id

def create_application_id(app, job_id, applicant_id):
    with app.app_context():
        application = Application(job_id=job_id, applicant_id=applicant_id, status="submitted")
        _db.session.add(application)
        _db.session.commit()
        return application.id

# ---------------- Tests ----------------

def test_post_interview_success(client, app):
    hr_user = 3001
    app_user = 3002
    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="InterviewCo3001")
    create_hr_profile_id(app, hr_user, comp)
    job = create_job_id(app, hr_user, comp)

    create_user_id(app, app_user)
    create_applicant_id(app, app_user)

    application_id = create_application_id(app, job, app_user)

    payload = {
        "application_id": application_id,
        "interview_date": "2025-02-20",
        "mode": "online",
        "stage": "technical",
        "duration_minutes": 45,
        "slot_start_time": "10:00:00",
        "slot_end_time": "10:45:00",
        "interviewer_id": hr_user,
        "interviewee_id": app_user,
        "interview_recording_url": None,
        "status": "scheduled",
        "result": None
    }

    res = client.post(_base(), json=payload)
    assert_response(res, expected_status=201)
    j = res.get_json()
    assert j["application_id"] == application_id
    assert j["mode"] == "online"
    assert j["stage"] == "technical"
    assert "interview_date" in j
    assert "slot_start_time" in j

def test_post_interview_application_not_found_returns_404(client, app):
    payload = {"application_id": 9999999}
    res = client.post(_base(), json=payload)
    assert_response(res, expected_status=404, expected_message="application not found")

def test_post_interview_interviewer_not_found_returns_404(client, app):
    hr_user = 3101
    app_user = 3102
    create_user_id(app, hr_user)  
    comp = create_company_id(app, hr_user, company_name="Comp3101")
    job_owner = 3110
    create_user_id(app, job_owner)
    comp2 = create_company_id(app, job_owner, company_name="Comp3110")
    create_hr_profile_id(app, job_owner, comp2)
    job = create_job_id(app, job_owner, comp2)

    create_user_id(app, app_user)
    create_applicant_id(app, app_user)

    application_id = create_application_id(app, job, app_user)

    payload = {"application_id": application_id, "interviewer_id": 9999999}
    res = client.post(_base(), json=payload)
    assert_response(res, expected_status=404, expected_message="interviewer not found")

def test_post_interview_interviewee_not_found_returns_404(client, app):
    hr_user = 3201
    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="Comp3201")
    create_hr_profile_id(app, hr_user, comp)
    job = create_job_id(app, hr_user, comp)

    real_applicant = 3202
    create_user_id(app, real_applicant)
    create_applicant_id(app, real_applicant)
    application_id = create_application_id(app, job, real_applicant)

    payload = {"application_id": application_id, "interviewee_id": 9999999}
    res = client.post(_base(), json=payload)
    assert_response(res, expected_status=404, expected_message="interviewee not found")

def test_get_list_and_single_interview(client, app):
    hr_user = 3301
    applicant_user = 3302
    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="Comp3301")
    create_hr_profile_id(app, hr_user, comp)
    job = create_job_id(app, hr_user, comp)

    create_user_id(app, applicant_user)
    create_applicant_id(app, applicant_user)

    app_id = create_application_id(app, job, applicant_user)

    rpost = client.post(_base(), json={"application_id": app_id, "interviewer_id": hr_user, "interviewee_id": applicant_user})
    assert_response(rpost, expected_status=201)
    created = rpost.get_json()
    iid = created["id"]

    rlist = client.get(_base())
    assert_response(rlist, expected_status=200)
    arr = rlist.get_json()
    assert any(item.get("id") == iid for item in arr)

    rsingle = client.get(_single(iid))
    assert_response(rsingle, expected_status=200)
    js = rsingle.get_json()
    assert js["id"] == iid
    assert js["application_id"] == app_id

def test_put_updates_interview_and_delete(client, app):
    hr_user = 3401
    applicant_user = 3402
    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="Comp3401")
    create_hr_profile_id(app, hr_user, comp)
    job = create_job_id(app, hr_user, comp)

    create_user_id(app, applicant_user)
    create_applicant_id(app, applicant_user)

    app_id = create_application_id(app, job, applicant_user)

    rpost = client.post(_base(), json={"application_id": app_id, "interviewer_id": hr_user, "interviewee_id": applicant_user})
    assert_response(rpost, expected_status=201)
    iid = rpost.get_json()["id"]

    update_payload = {
        "application_id": app_id,  
        "mode": "in-person",
        "stage": "final",
        "duration_minutes": 60,
        "slot_start_time": "15:00:00",
        "slot_end_time": "16:00:00",
        "status": "completed",
        "result": "passed"
    }
    rput = client.put(_single(iid), json=update_payload)
    assert_response(rput, expected_status=200)
    updated = rput.get_json()
    assert updated.get("mode") == "in-person" or updated.get("stage") == "final" or updated.get("status") == "completed"
    rdel = client.delete(_single(iid))
    assert_response(rdel, expected_status=200)
    with app.app_context():
        assert Interview.query.get(iid) is None
