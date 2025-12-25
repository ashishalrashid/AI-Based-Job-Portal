# tests/test_applicant_dashboard.py
import pytest
import json
from datetime import date, datetime, timedelta
from flask import Blueprint
import application.controller.applicant.dashboard as dashboard_controllers
from application.data.database import db as _db
from application.data.models import (
    User, ApplicantProfile, Company, HRProfile, JobPosting,
    Application, Interview, Role
)
from sqlalchemy import func

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

# -------------- Register test-only route (attach controller function) --------------
@pytest.fixture(scope="session", autouse=True)
def register_test_routes(app):
    test_bp = Blueprint("test_applicant_dashboard_test_bp", __name__)
    test_bp.add_url_rule(
        "/applicant_dashboard/<int:applicant_id>",
        endpoint="test_applicant_dashboard",
        view_func=dashboard_controllers.get_applicant_dashboard,
        methods=["GET"],
    )
    app.register_blueprint(test_bp, url_prefix="/_test_dashboard")
    yield

def _dashboard(applicant_id):
    return f"/_test_dashboard/applicant_dashboard/{applicant_id}"

# -------------- DB helper functions --------------
def ensure_roles(app):
    with app.app_context():
        existing = {r.name for r in Role.query.all()}
        needed = {"applicant", "hr", "admin", "company"}
        for nm in needed - existing:
            _db.session.add(Role(name=nm, description=f"{nm} role"))
        _db.session.commit()

def create_user_id(app, user_id, email=None, name=None, phone=None):
    with app.app_context():
        ensure_roles(app)
        email = email or f"user{user_id}@test.local"
        u = User(id=user_id, name=(name or f"User{user_id}"), email=email, phone=phone, password_hashed="pw-hash")
        _db.session.add(u)
        _db.session.commit()
        return u.id

def create_company_id(app, owner_user_id, company_name="ACME Co"):
    with app.app_context():
        if not User.query.get(owner_user_id):
            create_user_id(app, owner_user_id)
        c = Company(company_name=company_name, user_id=owner_user_id, company_email=f"{company_name.lower()}@test")
        _db.session.add(c)
        _db.session.commit()
        return c.id

def create_hr_profile_id(app, hr_user_id, company_id, first_name="HR", last_name="Person"):
    with app.app_context():
        if not User.query.get(hr_user_id):
            create_user_id(app, hr_user_id)
        hr = HRProfile.query.get(hr_user_id)
        if not hr:
            hr = HRProfile(hr_id=hr_user_id, company_id=company_id, first_name=first_name, last_name=last_name, contact_email=f"hr{hr_user_id}@test")
            _db.session.add(hr)
            _db.session.commit()
        return hr.hr_id

def create_job_id(app, hr_id, company_id, title="Engineer", created_date=None, status="open"):
    with app.app_context():
        if not Company.query.get(company_id):
            raise RuntimeError(f"company {company_id} not found")
        if not HRProfile.query.get(hr_id):
            create_hr_profile_id(app, hr_id, company_id)
        jd = created_date or datetime.utcnow()
        job = JobPosting(hr_id=hr_id, company_id=company_id, job_title=title, created_date=jd, status=status)
        _db.session.add(job)
        _db.session.commit()
        return job.id

def create_applicant_profile(app, user_id, name="Applicant", **kwargs):
    """
    Create an ApplicantProfile if missing. If exists, update optional fields passed in kwargs.
    """
    with app.app_context():
        if not User.query.get(user_id):
            create_user_id(app, user_id)
        ap = ApplicantProfile.query.get(user_id)
        if not ap:
            ap = ApplicantProfile(applicant_id=user_id, name=name)
            for k, v in kwargs.items():
                if hasattr(ap, k) and v is not None:
                    setattr(ap, k, v)
            _db.session.add(ap)
            _db.session.commit()
        else:
            changed = False
            if name and ap.name != name:
                ap.name = name
                changed = True
            for k, v in kwargs.items():
                if v is not None and getattr(ap, k, None) != v:
                    setattr(ap, k, v)
                    changed = True
            if changed:
                _db.session.commit()
        return ap.applicant_id

def create_application_id(app, job_id, applicant_id, status="submitted"):
    with app.app_context():
        if not JobPosting.query.get(job_id):
            raise RuntimeError(f"job {job_id} not found")
        if not ApplicantProfile.query.get(applicant_id):
            raise RuntimeError(f"applicant {applicant_id} not found")
        application = Application(job_id=job_id, applicant_id=applicant_id, status=status)
        _db.session.add(application)
        _db.session.commit()
        return application.id

def create_interview_id(app, application_id, interviewer_id, interview_date=None, status="scheduled", slot_start_time=None):
    with app.app_context():
        if not Application.query.get(application_id):
            raise RuntimeError(f"application {application_id} not found")
        # ensure interviewer profile
        if not User.query.get(interviewer_id):
            create_user_id(app, interviewer_id)
        if not HRProfile.query.get(interviewer_id):
            create_hr_profile_id(app, interviewer_id, Application.query.get(application_id).job.company_id)
        date_obj = interview_date or date.today()
        # default slot time
        from datetime import time
        start = slot_start_time or time(10, 0)
        intr = Interview(
            application_id=application_id,
            interview_date=date_obj,
            interviewee_id=Application.query.get(application_id).applicant_id,
            interviewer_id=interviewer_id,
            slot_start_time=start,
            slot_end_time=None,
            mode="online",
            duration_minutes=60,
            stage="technical",
            status=status
        )
        _db.session.add(intr)
        _db.session.commit()
        return intr.id

# -------------- Tests --------------

def test_recent_applications_and_status_counts_and_profile_completion(client, app):
    hr = 5001
    cand = 5002

    create_user_id(app, hr)
    comp = create_company_id(app, hr, company_name="DashCo")
    create_hr_profile_id(app, hr, comp)

    # create job and applicant
    job1 = create_job_id(app, hr, comp, title="J1")
    job2 = create_job_id(app, hr, comp, title="J2")
    create_applicant_profile(app, cand, name="Dash Applicant", skills="py,sql", linkedin_url="lnk", github_url=None, resume_filename="r.pdf")

    # create multiple applications with different statuses and dates
    a1 = create_application_id(app, job1, cand, status="submitted")
    a2 = create_application_id(app, job2, cand, status="shortlisted")
    # older application
    with app.app_context():
        older = Application(job_id=job1, applicant_id=cand, status="offered")
        _db.session.add(older)
        _db.session.commit()
        older_id = older.id
        # adjust applied_date to be earlier
        older.applied_date = datetime.utcnow() - timedelta(days=30)
        _db.session.commit()

    # ping dashboard
    res = client.get(_dashboard(cand))
    assert_response(res, expected_status=200)
    j = res.get_json()
    assert "applicant_name" in j and j["applicant_name"] == "Dash Applicant"
    assert "recent_applications" in j and isinstance(j["recent_applications"], list)
    # ensure the returned list contains our application ids
    ids = {it["application_id"] for it in j["recent_applications"]}
    assert a1 in ids or a2 in ids or older_id in ids

    # check status counts mapping keys exist
    counts = j.get("application_status_counts", {})
    assert set(["Applied", "Shortlisted", "Interview", "Offer", "Rejected"]).issubset(set(counts.keys()))
    # verify numeric counts are integers
    for v in counts.values():
        assert isinstance(v, int)

    # profile completion (we set some fields; compute expected)
    # in our create_applicant_profile we provided name, skills, linkedin_url and resume_filename
    # profile_completion should be integer between 0 and 100
    assert isinstance(j.get("profile_completion"), int)
    assert 0 <= j.get("profile_completion") <= 100

def test_upcoming_interviews_listed_and_ordered(client, app):
    hr = 5010
    cand = 5011

    create_user_id(app, hr)
    comp = create_company_id(app, hr, company_name="InterviewDashCo")
    create_hr_profile_id(app, hr, comp)

    # job and applicant
    job = create_job_id(app, hr, comp, title="IntJob")
    create_applicant_profile(app, cand, name="Interview Candidate")

    # create applications and interviews: one in future, one in past
    app_future = create_application_id(app, job, cand)
    app_past = create_application_id(app, job, cand)

    future_date = date.today() + timedelta(days=3)
    past_date = date.today() - timedelta(days=3)

    intr_future = create_interview_id(app, app_future, hr, interview_date=future_date, status="scheduled")
    intr_past = create_interview_id(app, app_past, hr, interview_date=past_date, status="scheduled")

    res = client.get(_dashboard(cand))
    assert_response(res, expected_status=200)
    j = res.get_json()
    upcoming = j.get("upcoming_interviews", [])
    # only future interview should be present
    ids = {it["interview_id"] for it in upcoming}
    assert intr_future in ids
    assert intr_past not in ids
    # ensure ordering by date ascending (first item date <= next item date)
    if len(upcoming) >= 2:
        dates = [datetime.strptime(it["date"], "%Y-%m-%d").date() for it in upcoming]
        assert dates == sorted(dates)

def test_404_if_applicant_not_found(client, app):
    non_existent = 9_999_991
    # sanity check no profile
    with app.app_context():
        assert ApplicantProfile.query.get(non_existent) is None
    res = client.get(_dashboard(non_existent))
    assert res.status_code == 404
