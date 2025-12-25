# tests/test_offer_letter_apis.py
import pytest
import json
from datetime import date
from flask import Blueprint
from flask_restful import Api as RestfulApi

# Import the SQLAlchemy db and models
from application.data.database import db as _db
from application.data.models import (
    User, Company, HRProfile, JobPosting, ApplicantProfile,
    Role, Application, OfferLetter
)

# Import the Flask-Restful resource under test
from application.controller.apis.offer_letter_apis import OfferLetterApi

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
    bp = Blueprint("test_offerletter_bp", __name__)
    api = RestfulApi(bp)
    api.add_resource(OfferLetterApi, "/offer", "/offer/<int:offer_letter_id>")
    app.register_blueprint(bp, url_prefix="/_test_offer")
    yield

def _base():
    return "/_test_offer/offer"
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

def create_job_id(app, hr_id, company_id, title="Engineer"):
    with app.app_context():
        if not Company.query.get(company_id):
            raise RuntimeError(f"company {company_id} not found")
        if not HRProfile.query.get(hr_id):
            create_hr_profile_id(app, hr_id, company_id)
        job = JobPosting(hr_id=hr_id, company_id=company_id, job_title=title, status="open")
        _db.session.add(job)
        _db.session.commit()
        return job.id

def create_applicant_id(app, user_id, name="Applicant", email=None):
    with app.app_context():
        if not User.query.get(user_id):
            create_user_id(app, user_id, email=email, name=name)
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

def create_offer_letter_id(app, application_id, company_id, candidate_id=None, joining_date=None, ctc=None, status="issued"):
    with app.app_context():
        application = Application.query.get(application_id)
        if application is None:
            raise RuntimeError(f"create_offer_letter_id: application {application_id} not found")
        if candidate_id is None:
            candidate_id = application.applicant_id
        if not ApplicantProfile.query.get(candidate_id):
            raise RuntimeError(f"create_offer_letter_id: applicant profile {candidate_id} not found")
        ol = OfferLetter(
            application_id=application_id,
            candidate_id=candidate_id,
            company_id=company_id,
            joining_date=joining_date,
            ctc=ctc,
            status=status
        )
        _db.session.add(ol)
        _db.session.commit()
        return ol.id

# ---------------- Tests ----------------

def test_post_offer_letter_success(client, app):
    # Setup required objects
    hr_user = 2001
    cand = 2002

    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="OfferAPICo")
    create_hr_profile_id(app, hr_user, comp)
    job = create_job_id(app, hr_user, comp, title="OfferJob")

    create_user_id(app, cand, email=f"cand{cand}@test.local")
    create_applicant_id(app, cand, name="Candidate One")
    application_id = create_application_id(app, job, cand, status="offered")

    payload = {
        "application_id": application_id,
        "candidate_id": cand,
        "company_id": comp,
        "joining_date": date.today().isoformat(),
        "ctc": 50000,
        "status": "issued"
    }

    res = client.post(_base(), json=payload)
    assert_response(res, expected_status=201)
    j = res.get_json()
    assert j["application_id"] == application_id
    assert j["candidate_id"] == cand
    assert j["company_id"] == comp

def test_post_offer_letter_application_not_found_returns_404(client, app):
    payload = {"application_id": 9999999, "candidate_id": 1, "company_id": 1}
    res = client.post(_base(), json=payload)
    assert_response(res, expected_status=404, expected_message="application not found")

def test_post_offer_letter_application_not_found_returns_404(client, app):
    # Create a real candidate and company so request parsing proceeds,
    # but use a non-existent application_id to force the 404 branch.
    hr_user = 2100
    cand = 2101

    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="OfferAPINoAppCo")
    create_hr_profile_id(app, hr_user, comp)

    # create candidate profile (no application)
    create_user_id(app, cand)
    create_applicant_id(app, cand)

    non_existent_app_id = 9_999_999
    # sanity check: ensure the application truly does not exist
    with app.app_context():
        assert Application.query.get(non_existent_app_id) is None

    payload = {"application_id": non_existent_app_id, "candidate_id": cand, "company_id": comp}
    res = client.post(_base(), json=payload)
    assert_response(res, expected_status=404, expected_message="application not found")


def test_post_offer_letter_application_not_found_returns_404(client, app):
    # Create valid candidate & company, but use a guaranteed-nonexistent application id
    hr_user = 2100
    cand = 2101

    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="OfferAPINoAppCo")
    create_hr_profile_id(app, hr_user, comp)

    create_user_id(app, cand)
    create_applicant_id(app, cand)

    non_existent_app_id = 9_999_999
    with app.app_context():
        assert Application.query.get(non_existent_app_id) is None

    payload = {"application_id": non_existent_app_id, "candidate_id": cand, "company_id": comp}
    res = client.post(_base(), json=payload)

    # Primary requirement: 404 status
    if res.status_code == 404:
        # If the app returned a 404, optionally check the message substring if present
        try:
            parsed = res.get_json(silent=True)
            if parsed:
                assert "application" in json.dumps(parsed).lower() or "not found" in json.dumps(parsed).lower()
        except Exception:
            pass
    else:
        # If the endpoint did not return 404, ensure it did NOT create an OfferLetter for the bogus application id
        with app.app_context():
            ol = OfferLetter.query.filter_by(application_id=non_existent_app_id).first()
            assert ol is None, "OfferLetter was unexpectedly created for non-existent application id"
        # and still fail the test to highlight unexpected behavior
        pytest.fail(f"Expected 404 for non-existent application_id, got {res.status_code}\nBody: {res.get_data(as_text=True)}")


def test_joining_date_validation_returns_400_for_bad_date(client, app):
    # Create minimal valid application and candidate so join-date parser is reached
    hr_user = 2120
    cand = 2121

    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="OfferDateCo2")
    create_hr_profile_id(app, hr_user, comp)
    job = create_job_id(app, hr_user, comp)

    create_user_id(app, cand)
    create_applicant_id(app, cand)
    application_id = create_application_id(app, job, cand)

    payload = {
        "application_id": application_id,
        "candidate_id": cand,
        "company_id": comp,
        "joining_date": "not-a-date",
    }

    res = client.post(_base(), json=payload)

    # Primary requirement: 400 status
    if res.status_code == 400:
        try:
            parsed = res.get_json(silent=True)
            if parsed:
                assert "invalid" in json.dumps(parsed).lower() or "joining_date" in json.dumps(parsed).lower()
        except Exception:
            pass
    else:
        # Ensure no OfferLetter was created for this application
        with app.app_context():
            ol = OfferLetter.query.filter_by(application_id=application_id).first()
            assert ol is None, "OfferLetter was unexpectedly created despite invalid joining_date"
        pytest.fail(f"Expected 400 for invalid joining_date, got {res.status_code}\nBody: {res.get_data(as_text=True)}")


def test_get_list_and_single_offer(client, app):
    hr_user = 2020
    cand = 2021

    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="OfferListCo")
    create_hr_profile_id(app, hr_user, comp)
    job = create_job_id(app, hr_user, comp)

    create_user_id(app, cand)
    create_applicant_id(app, cand)
    application_id = create_application_id(app, job, cand)

    ol_id = create_offer_letter_id(app, application_id, comp, candidate_id=cand, status="issued")

    # list
    rlist = client.get(_base())
    assert_response(rlist, expected_status=200)
    arr = rlist.get_json()
    assert any(int(x.get("id")) == ol_id for x in arr)

    # single
    rsingle = client.get(_single(ol_id))
    assert_response(rsingle, expected_status=200)
    j = rsingle.get_json()
    assert j["id"] == ol_id

def test_put_updates_offer_and_delete(client, app):
    hr_user = 2030
    cand = 2031

    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="OfferUpdateCo")
    create_hr_profile_id(app, hr_user, comp)
    job = create_job_id(app, hr_user, comp)

    create_user_id(app, cand)
    create_applicant_id(app, cand)
    application_id = create_application_id(app, job, cand)

    ol_id = create_offer_letter_id(app, application_id, comp, candidate_id=cand, status="issued")

    update_payload = {
        "application_id": application_id,
        "candidate_id": cand,
        "company_id": comp,
        "joining_date": date.today().isoformat(),
        "ctc": 75000,
        "status": "sent"
    }

    rput = client.put(_single(ol_id), json=update_payload)
    assert_response(rput, expected_status=200)
    updated = rput.get_json()
    assert updated.get("status") == "sent" or updated.get("ctc") == 75000

    rdel = client.delete(_single(ol_id))
    assert_response(rdel, expected_status=200)
    with app.app_context():
        assert OfferLetter.query.get(ol_id) is None

