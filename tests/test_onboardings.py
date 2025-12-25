# tests/test_onboarding_api.py
import pytest
import json
from flask import Blueprint
import application.controller.onboarding.controllers as onboarding_controllers
from application.data.database import db as _db
from application.data.models import (
    User, Company, HRProfile, JobPosting, ApplicantProfile,
    Role, Application, Onboarding
)

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

# -------------- Register test-only routes (mount controller view func under unique blueprint) --------------
@pytest.fixture(scope="session", autouse=True)
def register_test_routes(app):
    test_bp = Blueprint("test_onboarding_test_bp", __name__)

    test_bp.add_url_rule(
        "/pending_count/<int:company_id>",
        endpoint="test_onboarding_pending_count",
        view_func=onboarding_controllers.get_onboarding_pending_count,
        methods=["GET"],
    )

    app.register_blueprint(test_bp, url_prefix="/_test_onboarding")
    yield

def _pending_count(company_id):
    return f"/_test_onboarding/pending_count/{company_id}"

# -------------- DB helper functions (create objects and return ids) --------------
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
        c = Company(company_name=company_name, user_id=owner_user_id, company_email=f"{company_name.lower()}@test")
        _db.session.add(c)
        _db.session.commit()
        return c.id

def create_job_id(app, hr_id, company_id, title="Engineer"):
    with app.app_context():
        # Ensure the company exists
        comp = Company.query.get(company_id)
        if comp is None:
            raise RuntimeError(f"create_job_id: company {company_id} does not exist")

        hr = HRProfile.query.get(hr_id)
        if not hr:
            user = User.query.get(hr_id)
            if not user:
                u = User(id=hr_id, name=f"HR{hr_id}", email=f"hr{hr_id}@test", password_hashed="pw-hash")
                _db.session.add(u)
                _db.session.commit()
            hr = HRProfile(hr_id=hr_id, company_id=company_id, first_name="HR", last_name=str(hr_id), contact_email=f"hr{hr_id}@test")
            _db.session.add(hr)
            _db.session.commit()

        job = JobPosting(hr_id=hr_id, company_id=company_id, job_title=title)
        _db.session.add(job)
        _db.session.commit()
        return job.id


def create_applicant_and_profile(app, user_id, name="Applicant"):
    with app.app_context():
        # ensure a User exists
        u = User.query.get(user_id)
        if not u:
            create_user_id(app, user_id, name=name)
        ap = ApplicantProfile(applicant_id=user_id, name=name)
        _db.session.add(ap)
        _db.session.commit()
        return ap.applicant_id

def create_application_id(app, job_id, applicant_id, status="submitted"):
    with app.app_context():
        application = Application(job_id=job_id, applicant_id=applicant_id, status=status)
        _db.session.add(application)
        _db.session.commit()
        return application.id

def create_onboarding_id(app, application_id, status="pending", offer_accepted=False, contact_email=None, contact_phone=None, joining_date=None):
    with app.app_context():
        # Ensure the application exists
        application = Application.query.get(application_id)
        if application is None:
            raise RuntimeError(f"create_onboarding_id: application {application_id} not found")

        existing = Onboarding.query.filter_by(application_id=application_id).first()
        if existing:
            return existing.id

        ob = Onboarding(
            application_id=application_id,
            status=status if status is not None else "pending",
            offer_accepted=bool(offer_accepted),
            contact_email=contact_email,
            contact_phone=contact_phone,
            joining_date=joining_date
        )
        _db.session.add(ob)
        _db.session.commit()
        return ob.id


# ---------------- Tests ----------------

def test_pending_count_zero_when_none(client, app):
    hr_user = 8001
    create_user_id(app, hr_user)
    comp_id = create_company_id(app, hr_user, company_name="OnboardCo0")
    # no applications / onboardings created
    res = client.get(_pending_count(comp_id))
    assert_response(res, expected_status=200)
    j = res.get_json()
    assert j["pending_onboarding_count"] == 0

def test_pending_count_counts_only_pending_for_company(client, app):
    hr_user_a = 8002
    hr_user_b = 8003
    create_user_id(app, hr_user_a)
    create_user_id(app, hr_user_b)

    comp_a = create_company_id(app, hr_user_a, company_name="OnboardCoA")
    comp_b = create_company_id(app, hr_user_b, company_name="OnboardCoB")

    # create job for company A and B
    job_a = create_job_id(app, hr_user_a, comp_a, title="EngA")
    job_b = create_job_id(app, hr_user_b, comp_b, title="EngB")

    # applicants and applications
    applicant1 = 8010
    applicant2 = 8011
    applicant3 = 8012

    create_applicant_and_profile(app, applicant1, name="Alice")
    create_applicant_and_profile(app, applicant2, name="Bob")
    create_applicant_and_profile(app, applicant3, name="Charlie")

    # Application A1 -> onboarding pending
    app_a1 = create_application_id(app, job_a, applicant1, status="offered")
    create_onboarding_id(app, app_a1, status="pending")

    # Application A2 -> onboarding completed
    app_a2 = create_application_id(app, job_a, applicant2, status="offered")
    create_onboarding_id(app, app_a2, status="completed")

    # Application B1 -> onboarding pending (different company)
    app_b1 = create_application_id(app, job_b, applicant3, status="offered")
    create_onboarding_id(app, app_b1, status="pending")

    # Query company A
    res_a = client.get(_pending_count(comp_a))
    assert_response(res_a, expected_status=200)
    j_a = res_a.get_json()
    assert j_a["pending_onboarding_count"] == 1

    # Query company B
    res_b = client.get(_pending_count(comp_b))
    assert_response(res_b, expected_status=200)
    j_b = res_b.get_json()
    assert j_b["pending_onboarding_count"] == 1
