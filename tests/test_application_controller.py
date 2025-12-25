# tests/test_applications.py
import pytest
import json
from datetime import datetime, timedelta
from flask import Blueprint
import application.controller.applications.controllers as applications_controllers
from application.data.database import db as _db
from application.data.models import (
    User, Company, HRProfile, JobPosting, ApplicantProfile,
    Application, Role
)

# ---------------- Debug helpers ----------------
def show_debug(expected_status=None, expected_message=None, res=None):
    print("\n================ DEBUG OUTPUT ================")
    if expected_status is not None:
        print(f"EXPECTED STATUS: {expected_status}")
    if expected_message:
        print(f"EXPECTED MESSAGE SUBSTRING: {expected_message}")
    if res is not None:
        print(f"ACTUAL STATUS:   {res.status_code}")
    print("\n----- RAW RESPONSE BODY -----")
    try:
        if res is not None:
            print(res.get_data(as_text=True))
    except Exception as e:
        print(f"<could not read body: {e}>")
    print("\n----- PARSED JSON (if any) -----")
    try:
        if res is not None:
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
        body_text = json.dumps(parsed, indent=2) if parsed is not None else (res.get_data(as_text=True) if res is not None else "")
        if expected_message.lower() not in str(body_text).lower():
            show_debug(expected_status=expected_status, expected_message=expected_message, res=res)
        assert expected_message.lower() in str(body_text).lower()

# ---------------- Register test-only routes ----------------
@pytest.fixture(scope="session", autouse=True)
def register_test_routes(app):
    bp = Blueprint("test_applications_bp", __name__)

    # candidates list
    bp.add_url_rule("/<int:company_id>/candidates", view_func=applications_controllers.get_candidates, methods=["GET"])
    bp.add_url_rule("/<int:company_id>/count", view_func=applications_controllers.get_candidate_count, methods=["GET"])
    bp.add_url_rule("/<int:company_id>/roles", view_func=applications_controllers.get_roles, methods=["GET"])
    bp.add_url_rule("/apply", view_func=applications_controllers.apply_for_job, methods=["POST"])
    bp.add_url_rule("/applicant/<int:applicant_id>", view_func=applications_controllers.get_applications_for_applicant, methods=["GET"])

    app.register_blueprint(bp, url_prefix="/_test_applications")
    yield

def _candidates(company_id, **qs):
    q = "?" + "&".join(f"{k}={v}" for k,v in qs.items()) if qs else ""
    return f"/_test_applications/{company_id}/candidates{q}"

def _count(company_id):
    return f"/_test_applications/{company_id}/count"

def _roles(company_id):
    return f"/_test_applications/{company_id}/roles"

def _apply():
    return "/_test_applications/apply"

def _applicant(applicant_id, **qs):
    q = "?" + "&".join(f"{k}={v}" for k,v in qs.items()) if qs else ""
    return f"/_test_applications/applicant/{applicant_id}{q}"

# ---------------- DB helpers ----------------
def ensure_roles(app):
    with app.app_context():
        existing = {r.name for r in Role.query.all()}
        needed = {"applicant", "hr", "admin", "company"}
        for nm in needed - existing:
            _db.session.add(Role(name=nm, description=f"{nm} role"))
        _db.session.commit()

def create_user(app, user_id, email=None, name=None):
    with app.app_context():
        ensure_roles(app)
        if User.query.get(user_id):
            return user_id
        u = User(id=user_id, name=(name or f"User{user_id}"), email=email or f"user{user_id}@test.local", password_hashed="pw")
        _db.session.add(u)
        _db.session.commit()
        return u.id

def create_company(app, owner_user_id, company_name="ACME Co"):
    with app.app_context():
        if not User.query.get(owner_user_id):
            create_user(app, owner_user_id)
        c = Company(company_name=company_name, user_id=owner_user_id, company_email=f"{company_name.lower()}@test")
        _db.session.add(c)
        _db.session.commit()
        return c.id

def create_hr_profile(app, hr_user_id, company_id):
    with app.app_context():
        if not User.query.get(hr_user_id):
            create_user(app, hr_user_id)
        hr = HRProfile.query.get(hr_user_id)
        if not hr:
            hr = HRProfile(hr_id=hr_user_id, company_id=company_id, first_name="HR", last_name="Person", contact_email=f"hr{hr_user_id}@test")
            _db.session.add(hr)
            _db.session.commit()
        return hr.hr_id

def create_job(app, hr_id, company_id, title="Engineer", num_positions=None, required_skills=None):
    with app.app_context():
        if not HRProfile.query.get(hr_id):
            create_hr_profile(app, hr_id, company_id)
        job = JobPosting(hr_id=hr_id, company_id=company_id, job_title=title, num_positions=num_positions, required_skills=required_skills, status="open")
        _db.session.add(job)
        _db.session.commit()
        return job.id

def create_applicant_profile(app, user_id, name="Applicant"):
    with app.app_context():
        if not User.query.get(user_id):
            create_user(app, user_id)
        ap = ApplicantProfile.query.get(user_id)
        if not ap:
            ap = ApplicantProfile(applicant_id=user_id, name=name)
            _db.session.add(ap)
            _db.session.commit()
        return ap.applicant_id

def create_application(app, job_id, applicant_id, status="submitted", applied_delta_days=0):
    with app.app_context():
        if not JobPosting.query.get(job_id):
            raise RuntimeError("job not found")
        if not ApplicantProfile.query.get(applicant_id):
            raise RuntimeError("applicant not found")
        a = Application(job_id=job_id, applicant_id=applicant_id, status=status)
        if applied_delta_days:
            a.applied_date = datetime.utcnow() - timedelta(days=applied_delta_days)
        _db.session.add(a)
        _db.session.commit()
        return a.id

# ---------------- Tests ----------------

def test_candidates_list_and_filters_and_pagination(client, app):
    # Setup: company with jobs and many applications
    hr = 6001
    owner = hr
    comp = create_company(app, owner, company_name="CandCo")
    create_hr_profile(app, hr, comp)

    # Create two jobs with different titles and applicants
    job_a = create_job(app, hr, comp, title="Engineer")
    job_b = create_job(app, hr, comp, title="Designer")

    # Applicants and applications
    for i in range(5):
        uid = 6100 + i
        create_user(app, uid)
        create_applicant_profile(app, uid, name=f"Candidate {i}")
        create_application(app, job_a if i % 2 == 0 else job_b, uid, status="submitted")

    # Basic list
    res = client.get(_candidates(comp))
    assert_response(res, expected_status=200)
    j = res.get_json()
    assert "candidates" in j and isinstance(j["candidates"], list)
    assert j["total"] >= 5

    # Filter by role (exact job title)
    res2 = client.get(_candidates(comp, role="Engineer"))
    assert_response(res2, expected_status=200)
    j2 = res2.get_json()
    assert all(item["role"].lower().find("engineer") != -1 for item in j2["candidates"])

    # Search by name (case-insensitive)
    some_name = "Candidate 1"
    res3 = client.get(_candidates(comp, search="candidate 1"))
    assert_response(res3, expected_status=200)
    j3 = res3.get_json()
    assert any("candidate 1" in (item["first_name"] + " " + item["last_name"]).lower() for item in j3["candidates"])

    # Pagination: per_page small
    res4 = client.get(_candidates(comp, page=1, per_page=2))
    assert_response(res4, expected_status=200)
    j4 = res4.get_json()
    assert j4["per_page"] == 2

def test_candidate_count_and_roles_endpoints(client, app):
    hr = 6201
    comp = create_company(app, hr, company_name="CountRolesCo")
    create_hr_profile(app, hr, comp)
    job1 = create_job(app, hr, comp, title="A")
    job2 = create_job(app, hr, comp, title="B")
    # create some applications
    create_user(app, 7001); create_applicant_profile(app, 7001); create_application(app, job1, 7001)
    create_user(app, 7002); create_applicant_profile(app, 7002); create_application(app, job2, 7002)
    # count
    rc = client.get(_count(comp))
    assert_response(rc, expected_status=200)
    assert isinstance(rc.get_json().get("count"), int) and rc.get_json().get("count") >= 2
    # roles
    rr = client.get(_roles(comp))
    assert_response(rr, expected_status=200)
    roles_arr = rr.get_json()
    assert "A" in roles_arr and "B" in roles_arr

def test_apply_for_job_success_and_errors(client, app):
    hr = 6301
    comp = create_company(app, hr, company_name="ApplyCo")
    create_hr_profile(app, hr, comp)
    job = create_job(app, hr, comp, title="ApplyJob")

    applicant = 8001
    create_user(app, applicant)
    create_applicant_profile(app, applicant)
    # success
    payload = {"applicant_id": applicant, "job_id": job, "resume_filename": "r.pdf"}
    rpost = client.post(_apply(), json=payload)
    assert_response(rpost, expected_status=201)
    j = rpost.get_json()
    assert "application_id" in j

    # duplicate apply -> 400
    rdup = client.post(_apply(), json=payload)
    assert_response(rdup, expected_status=400)

    # missing fields -> 400
    rmiss = client.post(_apply(), json={"applicant_id": applicant})
    assert_response(rmiss, expected_status=400)

    # invalid applicant -> 404
    rbad = client.post(_apply(), json={"applicant_id": 99999999, "job_id": job, "resume_filename": "x.pdf"})
    assert_response(rbad, expected_status=404)

    # invalid job -> 404
    rbad2 = client.post(_apply(), json={"applicant_id": applicant, "job_id": 99999999, "resume_filename": "x.pdf"})
    assert_response(rbad2, expected_status=404)

def test_get_applications_for_applicant_and_summary(client, app):
    hr = 6401
    comp = create_company(app, hr, company_name="ApplicantAppsCo")
    create_hr_profile(app, hr, comp)
    job = create_job(app, hr, comp, title="SomeJob")

    applicant = 9001
    create_user(app, applicant)
    create_applicant_profile(app, applicant)

    # create multiple applications with different statuses and dates
    id1 = create_application(app, job, applicant, status="submitted")
    id2 = create_application(app, job, applicant, status="shortlisted")
    id3 = create_application(app, job, applicant, status="rejected")

    r = client.get(_applicant(applicant))
    assert_response(r, expected_status=200)
    j = r.get_json()

    assert "summary" in j and "applications" in j
    summary = j["summary"]
    assert summary["total"] >= 3
    assert isinstance(j["applications"], list)
    # ensure returned applications contain our created ids
    app_ids = {a["application_id"] for a in j["applications"]}
    assert id1 in app_ids and id2 in app_ids and id3 in app_ids
