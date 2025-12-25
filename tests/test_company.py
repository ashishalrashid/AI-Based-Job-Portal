# tests/test_company_dashboard.py
import pytest
import json
from datetime import datetime, date, timedelta
from flask import Blueprint
import application.controller.company.controllers as company_controllers
from application.data.database import db as _db
from application.data.models import (
    User, Company, HRProfile, JobPosting, ApplicantProfile,
    Role, Application, Interview, Onboarding
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

# -------------- Register test-only route --------------
@pytest.fixture(scope="session", autouse=True)
def register_test_routes(app):
    test_bp = Blueprint("test_company_test_bp", __name__)
    test_bp.add_url_rule(
        "/dashboard/<int:company_id>",
        endpoint="test_company_dashboard",
        view_func=company_controllers.get_company_dashboard,
        methods=["GET"],
    )
    app.register_blueprint(test_bp, url_prefix="/_test_company")
    yield

def _dashboard(company_id):
    return f"/_test_company/dashboard/{company_id}"

# -------------- DB helper functions --------------
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
        u = User(id=user_id, name=(name or f"User{user_id}"), email=email, password_hashed="pw-hash")
        _db.session.add(u)
        _db.session.commit()
        return u.id

def create_company_id(app, owner_user_id, company_name="ACME Co"):
    with app.app_context():
        # ensure owner user exists
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
            raise RuntimeError(f"create_job_id: company {company_id} not found")
        if not HRProfile.query.get(hr_id):
            create_hr_profile_id(app, hr_id, company_id)
        jd = created_date or datetime.utcnow()
        job = JobPosting(hr_id=hr_id, company_id=company_id, job_title=title, created_date=jd, status=status)
        _db.session.add(job)
        _db.session.commit()
        return job.id

def create_applicant_id(app, user_id, name="Applicant"):
    with app.app_context():
        if not User.query.get(user_id):
            create_user_id(app, user_id)
        ap = ApplicantProfile.query.get(user_id)
        if not ap:
            ap = ApplicantProfile(applicant_id=user_id, name=name)
            _db.session.add(ap)
            _db.session.commit()
        return ap.applicant_id

def create_application_id(app, job_id, applicant_id, status="submitted"):
    with app.app_context():
        if not JobPosting.query.get(job_id):
            raise RuntimeError(f"create_application_id: job {job_id} not found")
        if not ApplicantProfile.query.get(applicant_id):
            raise RuntimeError(f"create_application_id: applicant {applicant_id} not found")
        application = Application(job_id=job_id, applicant_id=applicant_id, status=status)
        _db.session.add(application)
        _db.session.commit()
        return application.id

def create_interview_id(app, application_id, interviewer_id, interview_date=None, status="scheduled", result=None):
    with app.app_context():
        if not Application.query.get(application_id):
            raise RuntimeError(f"create_interview_id: application {application_id} not found")
        # ensure interviewer user/profile exists
        if not User.query.get(interviewer_id):
            create_user_id(app, interviewer_id)
        if not HRProfile.query.get(interviewer_id):
            create_hr_profile_id(app, interviewer_id, Application.query.get(application_id).job.company_id)
        date_obj = interview_date or date.today()
        intr = Interview(
            application_id=application_id,
            interview_date=date_obj,
            interviewee_id=Application.query.get(application_id).applicant_id,
            interviewer_id=interviewer_id,
            mode="online",
            slot_start_time=None,
            slot_end_time=None,
            duration_minutes=60,
            stage="technical",
            status=status,
            result=result
        )
        _db.session.add(intr)
        _db.session.commit()
        return intr.id

def create_onboarding_id(app, application_id, joining_date=None, offer_accepted=True, status="pending"):
    with app.app_context():
        application = Application.query.get(application_id)
        if application is None:
            raise RuntimeError(f"create_onboarding_id: application {application_id} not found")
        existing = Onboarding.query.filter_by(application_id=application_id).first()
        if existing:
            return existing.id
        jd = joining_date or date.today()
        ob = Onboarding(
            application_id=application_id,
            contact_email=application.applicant.user.email if application.applicant and application.applicant.user else None,
            contact_phone=None,
            offer_accepted=bool(offer_accepted),
            status=status,
            joining_date=jd
        )
        _db.session.add(ob)
        _db.session.commit()
        return ob.id

# ---------------- Tests ----------------

def test_total_employees_and_open_jobs_and_onboarded_last_month(client, app):
    hr_user = 12001
    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="CompanyDashCo")
    # create two HRs for this company
    create_hr_profile_id(app, hr_user, comp)
    second_hr = hr_user + 1
    create_user_id(app, second_hr)
    create_hr_profile_id(app, second_hr, comp)

    # jobs: one open, one closed (different company)
    job_open = create_job_id(app, hr_user, comp, title="OpenJob", status="open", created_date=datetime.utcnow() - timedelta(days=10))
    job_closed = create_job_id(app, hr_user, comp, title="ClosedJob", status="closed", created_date=datetime.utcnow() - timedelta(days=40))
    # create application and onboarding that joined last month
    cand = 12010
    create_user_id(app, cand)
    create_applicant_id(app, cand, name="Joinee")
    app_id = create_application_id(app, job_open, cand, status="offered")

    # joining date in last month window
    now = datetime.utcnow()
    first_of_this_month = datetime(now.year, now.month, 1)
    first_of_last_month = first_of_this_month - timedelta(days=1)
    first_of_last_month = datetime(first_of_last_month.year, first_of_last_month.month, 1)
    last_of_last_month = first_of_this_month - timedelta(seconds=1)
    # pick joining date middle of last month
    join_date = first_of_last_month + timedelta(days=3)
    create_onboarding_id(app, app_id, joining_date=join_date, offer_accepted=True, status="completed")

    res = client.get(_dashboard(comp))
    assert_response(res, expected_status=200)
    j = res.get_json()
    assert j["total_employees"] == 2
    assert j["open_job_openings"] == 1
    assert j["onboarded_last_month"] == 1
    assert "hiring_summary" in j
    # ensure keys exist in summary
    hs = j["hiring_summary"]
    assert "openings" in hs and "onboarded" in hs and "interviewing" in hs

def test_hiring_summary_monthly_aggregates(client, app):
    hr_user = 12101
    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="HiringSummaryCo")
    create_hr_profile_id(app, hr_user, comp)

    # create jobs over 3 months (this month, last month, two months ago)
    today = datetime.utcnow()
    this_month = datetime(today.year, today.month, 5)
    last_month = (this_month - timedelta(days=30))
    two_months = (this_month - timedelta(days=60))

    # jobs created on different months
    create_job_id(app, hr_user, comp, title="JobNow", created_date=this_month)
    create_job_id(app, hr_user, comp, title="JobLast", created_date=last_month)
    create_job_id(app, hr_user, comp, title="JobTwo", created_date=two_months)

    # onboarding rows across months (ensure offer_accepted True)
    # create applicants/applications for each
    cand_base = 12200
    for i, jd in enumerate([this_month.date(), last_month.date(), two_months.date()]):
        uid = cand_base + i
        create_user_id(app, uid)
        create_applicant_id(app, uid, name=f"Cand{i}")
        job = create_job_id(app, hr_user, comp, title=f"JobForCand{i}", created_date=jd)
        app_id = create_application_id(app, job, uid, status="offered")
        create_onboarding_id(app, app_id, joining_date=jd, offer_accepted=True, status="completed")

    # interviewing data: create interviews tied to job created dates
    # create an interview in last month
    cand_i = cand_base + 10
    create_user_id(app, cand_i)
    create_applicant_id(app, cand_i, name="IntCand")
    job_x = create_job_id(app, hr_user, comp, title="InterviewJob", created_date=last_month)
    app_x = create_application_id(app, job_x, cand_i)
    create_interview_id(app, app_x, hr_user, interview_date=last_month.date(), status="completed")

    res = client.get(_dashboard(comp))
    assert_response(res, expected_status=200)
    j = res.get_json()
    hs = j.get("hiring_summary", {})
    # keys should look like "YYYY-MM"
    assert any(k.count("-") == 1 for k in hs.get("openings", {}).keys())
    # onboarded should include last_month and two_months (counts >= 1)
    onboarded = hs.get("onboarded", {})
    # Convert month keys to ints in case DB returns floats
    assert any(v >= 1 for v in onboarded.values())
    interviewing = hs.get("interviewing", {})
    assert any(v >= 1 for v in interviewing.values())
