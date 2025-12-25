# tests/test_offer_apis.py
import pytest
import json
from datetime import date
from flask import Blueprint
import application.controller.offer_letter.controllers as offer_controllers
from application.data.database import db as _db
from application.data.models import (
    User, Company, HRProfile, JobPosting, ApplicantProfile,
    Role, Application, Interview, OfferLetter
)

# ---------------- Debug helpers (same style as other tests) ----------------
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

# -------------- Register test-only routes (attach controller functions to a unique blueprint) --------------
@pytest.fixture(scope="session", autouse=True)
def register_test_routes(app):
    test_bp = Blueprint("test_offer_test_bp", __name__)

    test_bp.add_url_rule(
        "/acceptance_rate/<int:company_id>",
        endpoint="test_offer_acceptance_rate",
        view_func=offer_controllers.get_acceptance_rate,
        methods=["GET"],
    )

    test_bp.add_url_rule(
        "/eligible/<int:company_id>",
        endpoint="test_offer_eligible",
        view_func=offer_controllers.get_eligible_candidates,
        methods=["GET"],
    )

    test_bp.add_url_rule(
        "/send_offer/<int:application_id>",
        endpoint="test_offer_send",
        view_func=offer_controllers.send_offer,
        methods=["POST"],
    )

    app.register_blueprint(test_bp, url_prefix="/_test_offer")
    yield

def _acceptance(company_id):
    return f"/_test_offer/acceptance_rate/{company_id}"

def _eligible(company_id, qs=""):
    return f"/_test_offer/eligible/{company_id}{qs}"

def _send_offer(application_id):
    return f"/_test_offer/send_offer/{application_id}"

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

def create_hr_profile_if_missing(app, hr_user_id, company_id):
    with app.app_context():
        # ensure User exists
        if not User.query.get(hr_user_id):
            _db.session.add(User(id=hr_user_id, name=f"HR{hr_user_id}", email=f"hr{hr_user_id}@test", password_hashed="pw"))
            _db.session.commit()
        hr = HRProfile.query.get(hr_user_id)
        if not hr:
            hr = HRProfile(hr_id=hr_user_id, company_id=company_id, first_name="HR", last_name=str(hr_user_id), contact_email=f"hr{hr_user_id}@test")
            _db.session.add(hr)
            _db.session.commit()
        return hr.hr_id

def create_job_id(app, hr_id, company_id, title="Engineer"):
    """
    Ensure HRProfile exists (often JobPosting.hr_id references HRProfile.hr_id).
    """
    with app.app_context():
        # ensure company exists
        if not Company.query.get(company_id):
            raise RuntimeError(f"Company {company_id} not found")
        # ensure HRProfile exists
        create_hr_profile_if_missing(app, hr_id, company_id)
        job = JobPosting(hr_id=hr_id, company_id=company_id, job_title=title)
        _db.session.add(job)
        _db.session.commit()
        return job.id

def create_applicant_id(app, user_id, name="Applicant", gender="male"):
    with app.app_context():
        # ensure User exists
        if not User.query.get(user_id):
            create_user_id(app, user_id, name=name)
        ap = ApplicantProfile(applicant_id=user_id, name=name, gender=gender)
        _db.session.add(ap)
        _db.session.commit()
        return ap.applicant_id

def create_application_id(app, job_id, applicant_id, status="submitted"):
    with app.app_context():
        # ensure job/applicant exist
        if not JobPosting.query.get(job_id):
            raise RuntimeError(f"create_application_id: job {job_id} not found")
        if not ApplicantProfile.query.get(applicant_id):
            raise RuntimeError(f"create_application_id: applicant {applicant_id} not found")
        application = Application(job_id=job_id, applicant_id=applicant_id, status=status)
        _db.session.add(application)
        _db.session.commit()
        return application.id

def create_interview_id(app, application_id, status="completed", result="selected"):
    with app.app_context():
        # ensure application exists
        if not Application.query.get(application_id):
            raise RuntimeError(f"create_interview_id: application {application_id} not found")
        intr = Interview(application_id=application_id, status=status, result=result)
        _db.session.add(intr)
        _db.session.commit()
        return intr.id

def create_offer_letter_id(app, application_id, company_id, status="sent", candidate_id=None):
    """
    Ensure OfferLetter has non-null candidate id and required fields.
    If candidate_id is None, resolve from Application.applicant_id.
    """
    with app.app_context():
        application = Application.query.get(application_id)
        if application is None:
            raise RuntimeError(f"create_offer_letter_id: application {application_id} not found")
        if candidate_id is None:
            candidate_id = application.applicant_id
        # ensure applicant profile exists
        if not ApplicantProfile.query.get(candidate_id):
            raise RuntimeError(f"create_offer_letter_id: applicant profile {candidate_id} not found")
        ol = OfferLetter(application_id=application_id, company_id=company_id, status=status, candidate_id=candidate_id)
        _db.session.add(ol)
        _db.session.commit()
        return ol.id

# ---------------- Tests ----------------

def test_acceptance_rate_zero_when_no_offers(client, app):
    hr_user = 9001
    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="OfferCoZero")
    res = client.get(_acceptance(comp))
    assert_response(res, expected_status=200)
    j = res.get_json()
    assert j["acceptance_rate"] == 0

def test_acceptance_rate_calculation(client, app):
    hr_user = 9002
    a1 = 9003
    a2 = 9004

    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="OfferCoCalc")
    create_hr_profile_if_missing(app, hr_user, comp)
    job = create_job_id(app, hr_user, comp, title="OfferEng")

    # applicant 1: accepted
    create_user_id(app, a1)
    create_applicant_id(app, a1, name="Accept One")
    app1 = create_application_id(app, job, a1, status="offered")
    create_offer_letter_id(app, app1, comp, status="accepted", candidate_id=a1)

    # applicant 2: sent (but not accepted)
    create_user_id(app, a2)
    create_applicant_id(app, a2, name="Sent Two")
    app2 = create_application_id(app, job, a2, status="offered")
    create_offer_letter_id(app, app2, comp, status="sent", candidate_id=a2)

    res = client.get(_acceptance(comp))
    assert_response(res, expected_status=200)
    j = res.get_json()
    # accepted 1 / total 2 => 50.0
    assert abs(j["acceptance_rate"] - 50.0) < 0.0001

def test_get_eligible_candidates_returns_selected_after_completed(client, app):
    hr_user = 9010
    cand = 9011

    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="OfferEligibleCo")
    create_hr_profile_if_missing(app, hr_user, comp)
    job = create_job_id(app, hr_user, comp, title="EligibleEng")

    create_user_id(app, cand)
    create_applicant_id(app, cand, name="Selected Candidate")
    application_id = create_application_id(app, job, cand, status="submitted")

    # create interview with completed + selected
    create_interview_id(app, application_id, status="completed", result="selected")

    res = client.get(_eligible(comp))
    assert_response(res, expected_status=200)
    arr = res.get_json()
    assert any(int(x.get("application_id")) == application_id for x in arr)
    # ensure the returned email field exists and matches the user's email
    matched = [x for x in arr if int(x.get("application_id")) == application_id]
    assert matched and matched[0].get("email") == User.query.get(cand).email

def test_send_offer_posts_and_calls_email_and_pdf(monkeypatch, client, app):
    hr_user = 9020
    cand = 9021

    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="OfferSendCo")
    create_hr_profile_if_missing(app, hr_user, comp)
    job = create_job_id(app, hr_user, comp, title="SendEng")

    create_user_id(app, cand, email=f"cand{cand}@test.local")
    create_applicant_id(app, cand, name="Email Candidate")
    application_id = create_application_id(app, job, cand, status="offered")

    # Create interview with completed status and selected result (required for offer eligibility)
    create_interview_id(app, application_id, status="completed", result="selected")

    # Create OfferLetter in DB; controller expects OfferLetter exists for application_id
    ol_id = create_offer_letter_id(app, application_id, comp, status="draft", candidate_id=cand)

    # Monkeypatch the PDF/email utilities to avoid file IO or real email sending
    called = {"pdf": False, "email": False, "pdf_path": None, "email_to": None}

    def fake_generate_offer_letter_pdf(offer, offer_details=None):
        called["pdf"] = True
        # ensure the passed offer id matches
        assert offer.id == ol_id
        called["pdf_path"] = "/tmp/fake_offer.pdf"
        return called["pdf_path"]

    def fake_send_offer_email(email_to, pdf_path):
        called["email"] = True
        called["email_to"] = email_to
        assert pdf_path == called["pdf_path"]

    # patch functions where they are imported in the controller module
    monkeypatch.setattr(offer_controllers, "generate_offer_letter_pdf", fake_generate_offer_letter_pdf)
    monkeypatch.setattr(offer_controllers, "send_offer_email", fake_send_offer_email)

    # Send offer with required JSON data (salary is required)
    offer_data = {
        "salary": "1500000",
        "position": "Software Engineer",
        "start_date": "2025-03-01",
        "department": "Engineering",
        "work_mode": "Hybrid"
    }
    r = client.post(_send_offer(application_id), json=offer_data)
    assert_response(r, expected_status=200, expected_message="offer letter sent")

    # verify that offer status updated to 'sent'
    with app.app_context():
        ol = OfferLetter.query.filter_by(application_id=application_id).first()
        assert ol is not None
        assert ol.status == "sent"
        assert called["pdf"] is True and called["email"] is True
        assert called["email_to"] == User.query.get(cand).email
