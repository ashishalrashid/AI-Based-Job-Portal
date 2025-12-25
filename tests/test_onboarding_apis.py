# tests/test_onboarding_apis.py
import pytest
import json
from datetime import date
from flask import Blueprint
from flask_restful import Api as RestfulApi

# Resource under test
from application.controller.apis.onboarding_apis import OnboardingApi

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

# -------------- Register test-only routes (Flask-Restful resource) --------------
@pytest.fixture(scope="session", autouse=True)
def register_test_routes(app):
    bp = Blueprint("test_onboarding_bp", __name__)
    api = RestfulApi(bp)
    api.add_resource(OnboardingApi, "/onboarding", "/onboarding/<int:onboarding_id>")
    app.register_blueprint(bp, url_prefix="/_test_onboarding")
    yield

def _base():
    return "/_test_onboarding/onboarding"
def _single(oid):
    return f"{_base()}/{oid}"

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

def create_job_id(app, hr_id, company_id, title="Engineer"):
    with app.app_context():
        if not Company.query.get(company_id):
            raise RuntimeError(f"create_job_id: company {company_id} not found")
        if not HRProfile.query.get(hr_id):
            create_hr_profile_id(app, hr_id, company_id)
        job = JobPosting(hr_id=hr_id, company_id=company_id, job_title=title, status="open")
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

def create_onboarding_id(app, application_id, joining_date=None, offer_accepted=True, status="pending"):
    """
    Create or return existing Onboarding for application (application_id unique constraint).
    """
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

def test_post_onboarding_success(client, app):
    hr_user = 3001
    cand = 3002

    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="OnboardCo")
    create_hr_profile_id(app, hr_user, comp)
    job = create_job_id(app, hr_user, comp, title="OnboardJob")

    create_user_id(app, cand)
    create_applicant_id(app, cand, name="OnboardApplicant")
    application_id = create_application_id(app, job, cand, status="offered")

    payload = {
        "application_id": application_id,
        "contact_email": "cand@example.test",
        "contact_phone": "123456",
        "offer_accepted": True,
        "status": "completed",
        "joining_date": date.today().isoformat()
    }

    res = client.post(_base(), json=payload)
    assert_response(res, expected_status=201)
    j = res.get_json()
    assert j["application_id"] == application_id
    assert j["offer_accepted"] is True
    assert "joining_date" in j

def test_post_onboarding_application_not_found_returns_404(client, app):
    hr_user = 3010
    cand = 3011

    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="OnboardNoAppCo")
    create_hr_profile_id(app, hr_user, comp)

    create_user_id(app, cand)
    create_applicant_id(app, cand)

    non_existent_app_id = 9_999_997
    with app.app_context():
        assert Application.query.get(non_existent_app_id) is None

    payload = {"application_id": non_existent_app_id, "contact_email": "a@b.test"}
    res = client.post(_base(), json=payload)

    # Primary check: status code must be 404
    assert res.status_code == 404, f"Expected 404 but got {res.status_code}. Body: {res.get_data(as_text=True)}"

    # Secondary check: ensure no Onboarding row was created for the bogus application id
    with app.app_context():
        ol = Onboarding.query.filter_by(application_id=non_existent_app_id).first()
        assert ol is None, "Onboarding was unexpectedly created for non-existent application id"

    # Optional: if the response JSON contains a message, ensure it mentions 'application' or 'not found'
    try:
        parsed = res.get_json(silent=True)
        if parsed:
            body_text = json.dumps(parsed).lower()
            assert ("application" in body_text) or ("not found" in body_text) or ("error" in body_text)
    except Exception:
        pass

def test_get_list_and_single_onboarding(client, app):
    hr_user = 3020
    cand = 3021

    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="OnboardListCo")
    create_hr_profile_id(app, hr_user, comp)
    job = create_job_id(app, hr_user, comp)

    create_user_id(app, cand)
    create_applicant_id(app, cand)
    application_id = create_application_id(app, job, cand)

    ob_id = create_onboarding_id(app, application_id, offer_accepted=False, status="pending")

    rlist = client.get(_base())
    assert_response(rlist, expected_status=200)
    arr = rlist.get_json()
    assert any(int(x.get("id")) == ob_id for x in arr)

    rsingle = client.get(_single(ob_id))
    assert_response(rsingle, expected_status=200)
    j = rsingle.get_json()
    assert j["id"] == ob_id

def test_put_updates_onboarding_and_delete(client, app):
    hr_user = 3030
    cand = 3031

    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="OnboardUpdateCo")
    create_hr_profile_id(app, hr_user, comp)
    job = create_job_id(app, hr_user, comp)

    create_user_id(app, cand)
    create_applicant_id(app, cand)
    application_id = create_application_id(app, job, cand)

    ob_id = create_onboarding_id(app, application_id, offer_accepted=False, status="pending")

    update_payload = {
        "application_id": application_id,
        "contact_email": "new@example.test",
        "contact_phone": "99999",
        "offer_accepted": True,
        "status": "completed",
        "joining_date": date.today().isoformat()
    }

    rput = client.put(_single(ob_id), json=update_payload)
    assert_response(rput, expected_status=200)
    updated = rput.get_json()
    assert updated.get("status") == "completed" or updated.get("offer_accepted") is True

    rdel = client.delete(_single(ob_id))
    assert_response(rdel, expected_status=200)
    with app.app_context():
        assert Onboarding.query.get(ob_id) is None
