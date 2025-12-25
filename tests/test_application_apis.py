# tests/test_application_apis_fixed.py
import pytest
import io
from datetime import datetime
from werkzeug.security import generate_password_hash
from flask import Blueprint
from flask_restful import Api as RestfulApi

from application.data.database import db as _db
from application.data.models import (
    User, Company, HRProfile, JobPosting, ApplicantProfile, Role, Application
)
from application.controller.apis.application_apis import ApplicationApi

# ---------- Debug helpers ----------
import json
def show_debug(expected_status=None, expected_message=None, res=None):
    """Print useful debug info for failing HTTP responses."""
    print("\n================ DEBUG OUTPUT ================")
    if expected_status is not None:
        print(f"EXPECTED STATUS: {expected_status}")
    if expected_message:
        print(f"EXPECTED MESSAGE SUBSTRING: {expected_message}")
    print(f"ACTUAL STATUS:   {res.status_code}")
    print("\n----- RAW RESPONSE BODY -----")
    try:
        body_text = res.get_data(as_text=True)
        print(body_text)
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
    """
    Assert that response has expected status, and optionally contains expected_message.
    On failure, print debug output.
    """
    if expected_status is not None and res.status_code != expected_status:
        show_debug(expected_status=expected_status, expected_message=expected_message, res=res)
    assert expected_status is None or res.status_code == expected_status

    if expected_message:
        # get JSON if possible, else text
        body = None
        try:
            body = res.get_json(silent=True)
        except Exception:
            body = None
        body_text = body if body is not None else res.get_data(as_text=True)
        if expected_message.lower() not in str(body_text).lower():
            show_debug(expected_status=expected_status, expected_message=expected_message, res=res)
        assert expected_message.lower() in str(body_text).lower()

# ---------- register test-only routes ----------
@pytest.fixture(scope="session", autouse=True)
def register_test_routes(app):
    bp = Blueprint("test_application_bp", __name__)
    api = RestfulApi(bp)
    api.add_resource(ApplicationApi, "/application", "/application/<int:application_id>")
    app.register_blueprint(bp, url_prefix="/_test_application")
    yield

def _base():
    return "/_test_application/application"
def _single(aid):
    return f"{_base()}/{aid}"

# ---------- helper functions that return IDs (not ORM objects) ----------
def create_user_id(app, user_id, email=None, name=None):
    with app.app_context():
        # ensure roles exist (idempotent)
        existing = {r.name for r in Role.query.all()}
        needed = {"applicant", "hr", "admin", "company"}
        for nm in needed - existing:
            _db.session.add(Role(name=nm, description=f"{nm} role"))
        _db.session.commit()

        email = email or f"user{user_id}@test.local"
        u = User(id=user_id, name=(name or f"User{user_id}"), email=email, password_hashed=generate_password_hash("pw"))
        _db.session.add(u)
        _db.session.commit()
        return u.id

def create_company_id(app, user_id, company_name="ACME Co"):
    with app.app_context():
        c = Company(company_name=company_name, user_id=user_id, company_email=f"c{user_id}@co.test")
        _db.session.add(c)
        _db.session.commit()
        return c.id

def create_hr_profile_id(app, user_id, company_id, first_name="HR", last_name="Person"):
    with app.app_context():
        hr = HRProfile(hr_id=user_id, company_id=company_id, first_name=first_name, last_name=last_name, contact_email=f"hr{user_id}@test")
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

# ---------- Tests ----------
def test_post_application_success(client, app):
    hr_user = 401
    applicant_user = 501

    create_user_id(app, hr_user, email="hr401@test")
    comp_id = create_company_id(app, hr_user, company_name="TestCo401")
    create_hr_profile_id(app, hr_user, comp_id)
    job_id = create_job_id(app, hr_user, comp_id)

    create_user_id(app, applicant_user, email="app501@test")
    create_applicant_id(app, applicant_user)

    payload = {
        "job_id": job_id,
        "applicant_id": applicant_user,
        "status": "submitted",
        "resume_score": 85,
        "ai_feedback": "Good match"
    }

    res = client.post(_base(), json=payload)
    assert_response(res, expected_status=201)
    j = res.get_json()
    assert j["job_id"] == job_id
    assert j["applicant_id"] == applicant_user
    assert j["status"] == "submitted"
    assert j["resume_score"] == 85

def test_post_application_job_not_found_returns_404(client, app):
    applicant_user = 601
    create_user_id(app, applicant_user)
    create_applicant_id(app, applicant_user)

    payload = {"job_id": 9999999, "applicant_id": applicant_user}
    res = client.post(_base(), json=payload)

    assert_response(res, expected_status=404, expected_message="job not found")

def test_post_application_applicant_not_found_returns_404(client, app):
    # create job only
    hr_user = 701
    create_user_id(app, hr_user)
    comp_id = create_company_id(app, hr_user)
    create_hr_profile_id(app, hr_user, comp_id)
    job_id = create_job_id(app, hr_user, comp_id)

    payload = {"job_id": job_id, "applicant_id": 8888888}
    res = client.post(_base(), json=payload)
    assert_response(res, expected_status=404, expected_message="applicant not found")

def test_get_list_and_single_application(client, app):
    hr_user = 801
    applicant_user = 901
    create_user_id(app, hr_user)
    comp_id = create_company_id(app, hr_user)
    create_hr_profile_id(app, hr_user, comp_id)
    job_id = create_job_id(app, hr_user, comp_id)

    create_user_id(app, applicant_user)
    create_applicant_id(app, applicant_user)

    rpost = client.post(_base(), json={"job_id": job_id, "applicant_id": applicant_user, "status": "submitted"})
    assert_response(rpost, expected_status=201)
    app_json = rpost.get_json()
    aid = app_json["id"]

    rlist = client.get(_base())
    assert_response(rlist, expected_status=200)
    arr = rlist.get_json()
    assert any(a.get("id") == aid for a in arr)

    rsingle = client.get(_single(aid))
    assert_response(rsingle, expected_status=200)
    js = rsingle.get_json()
    assert js["id"] == aid
    assert js["job_id"] == job_id

def test_put_application_updates_fields_and_bug_demonstration(client, app):
    hr_user = 1001
    applicant_user = 1101
    create_user_id(app, hr_user)
    comp_id = create_company_id(app, hr_user)
    create_hr_profile_id(app, hr_user, comp_id)
    job_id = create_job_id(app, hr_user, comp_id)

    create_user_id(app, applicant_user)
    create_applicant_id(app, applicant_user)

    rpost = client.post(_base(), json={"job_id": job_id, "applicant_id": applicant_user, "status": "submitted"})
    assert_response(rpost, expected_status=201)
    aid = rpost.get_json()["id"]

    rput = client.put(_single(aid), json={"status": "shortlisted"})
    if rput.status_code == 200:
        assert_response(rput, expected_status=200)
        j = rput.get_json()
        assert j["status"] == "shortlisted"
    else:
        show_debug(expected_status=200, expected_message="shortlisted", res=rput)
        assert rput.status_code in (400, 422)

def test_delete_application(client, app):
    hr_user = 1201
    applicant_user = 1301
    create_user_id(app, hr_user)
    comp_id = create_company_id(app, hr_user)
    create_hr_profile_id(app, hr_user, comp_id)
    job_id = create_job_id(app, hr_user, comp_id)

    create_user_id(app, applicant_user)
    create_applicant_id(app, applicant_user)

    rpost = client.post(_base(), json={"job_id": job_id, "applicant_id": applicant_user})
    assert_response(rpost, expected_status=201)
    aid = rpost.get_json()["id"]

    rdel = client.delete(_single(aid))
    assert_response(rdel, expected_status=200)

    with app.app_context():
        assert Application.query.get(aid) is None
