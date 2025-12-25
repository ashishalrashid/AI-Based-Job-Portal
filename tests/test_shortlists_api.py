# tests/test_shortlists_api.py
import pytest
import json
from flask import Blueprint
import application.controller.shortlist.controllers as shortlist_controllers
from application.data.database import db as _db
from application.data.models import (
    User, Company, HRProfile, JobPosting, ApplicantProfile,
    Role, Application, Interview, OfferLetter
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

# -------------- Register test-only routes (mount the controller view funcs under a unique blueprint) --------------
@pytest.fixture(scope="session", autouse=True)
def register_test_routes(app):
    test_bp = Blueprint("test_shortlist_test_bp", __name__)

    test_bp.add_url_rule(
        "/<int:company_id>/stats",
        endpoint="test_shortlist_stats",
        view_func=shortlist_controllers.get_shortlisted_stats,
        methods=["GET"],
    )

    test_bp.add_url_rule(
        "/<int:company_id>/candidates",
        endpoint="test_shortlist_candidates",
        view_func=shortlist_controllers.get_shortlisted_candidates,
        methods=["GET"],
    )

    test_bp.add_url_rule(
        "/reject/<int:application_id>",
        endpoint="test_shortlist_reject",
        view_func=shortlist_controllers.reject_candidate,
        methods=["PUT"],
    )

    app.register_blueprint(test_bp, url_prefix="/_test_shortlist")
    yield

def _stats(company_id):
    return f"/_test_shortlist/{company_id}/stats"

def _candidates(company_id, qs=""):
    return f"/_test_shortlist/{company_id}/candidates{qs}"

def _reject(app_id):
    return f"/_test_shortlist/reject/{app_id}"

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

def create_applicant_id(app, user_id, name="Applicant", gender="male"):
    with app.app_context():
        ap = ApplicantProfile(applicant_id=user_id, name=name, gender=gender)
        _db.session.add(ap)
        _db.session.commit()
        return ap.applicant_id

def create_application_id(app, job_id, applicant_id, status="submitted", resume_score=0.0):
    with app.app_context():
        application = Application(job_id=job_id, applicant_id=applicant_id, status=status, resume_score=resume_score)
        _db.session.add(application)
        _db.session.commit()
        return application.id

def create_interview_id(app, application_id, status="scheduled"):
    with app.app_context():
        intr = Interview(application_id=application_id, status=status)
        _db.session.add(intr)
        _db.session.commit()
        return intr.id

def create_offer_letter_id(app, application_id, company_id, status="sent", candidate_id=None):
    with app.app_context():
        if candidate_id is None:
            application = Application.query.get(application_id)
            if application is None:
                raise RuntimeError(f"create_offer_letter_id: application {application_id} not found")
            candidate_id = application.applicant_id
        ol = OfferLetter(application_id=application_id, company_id=company_id, status=status, candidate_id=candidate_id)
        _db.session.add(ol)
        _db.session.commit()
        return ol.id

# ---------------- Tests ----------------

def test_get_shortlisted_stats_counts(client, app):
    hr_user = 7001
    applicant1 = 7002
    applicant2 = 7003
    applicant3 = 7004
    create_user_id(app, hr_user)
    comp_id = create_company_id(app, hr_user, company_name="StatsCo")
    create_hr_profile_id(app, hr_user, comp_id)
    job_id = create_job_id(app, hr_user, comp_id)
    create_user_id(app, applicant1)
    create_applicant_id(app, applicant1, name="One", gender="female")
    # This application will have the misspelled 'shorlisted' status and should be excluded from total_shortlisted
    app_shorlisted = create_application_id(app, job_id, applicant1, status="shorlisted", resume_score=10.0)
    create_user_id(app, applicant2)
    create_applicant_id(app, applicant2, name="Two", gender="male")
    # This application will have an interview with status 'pending'
    app_with_pending = create_application_id(app, job_id, applicant2, status="submitted", resume_score=20.0)
    create_interview_id(app, app_with_pending, status="pending")

    create_user_id(app, applicant3)
    create_applicant_id(app, applicant3, name="Three", gender="male")
    # This application will have an offer that is accepted
    app_with_offer = create_application_id(app, job_id, applicant3, status="submitted", resume_score=30.0)
    # IMPORTANT: pass candidate_id (applicant3) OR rely on helper to pick it up from application
    create_offer_letter_id(app, app_with_offer, comp_id, status="accepted", candidate_id=applicant3)
    res = client.get(_stats(comp_id))
    assert_response(res, expected_status=200)
    j = res.get_json()
    assert j["total_shortlisted"] == 2
    assert j["pending_interviews"] == 1
    assert j["offers_sent"] == 1
    assert j["acceptance_rate"] == 100.0

def test_get_shortlisted_candidates_filters(client, app):
    hr_user = 7101
    a_user1 = 7102
    a_user2 = 7103
    a_user3 = 7104

    create_user_id(app, hr_user)
    comp_id = create_company_id(app, hr_user, company_name="FilterCo")
    create_hr_profile_id(app, hr_user, comp_id)
    job_eng = create_job_id(app, hr_user, comp_id, title="Engineer")
    job_mgr = create_job_id(app, hr_user, comp_id, title="Manager")
    # Applicant 1: has scheduled interview (will map to 'pending interview' in UI)
    create_user_id(app, a_user1)
    create_applicant_id(app, a_user1, name="Alice Alpha", gender="female")
    app1 = create_application_id(app, job_eng, a_user1, status="submitted", resume_score=75.5)
    create_interview_id(app, app1, status="scheduled")  # latest_interview.status == 'scheduled' -> 'pending interview'
    # Applicant 2: interview completed -> maps to 'interview done'
    create_user_id(app, a_user2)
    create_applicant_id(app, a_user2, name="Bob Beta", gender="male")
    app2 = create_application_id(app, job_eng, a_user2, status="submitted", resume_score=60.0)
    create_interview_id(app, app2, status="completed")
    # Applicant 3: rejected at application level -> maps to 'rejected'
    create_user_id(app, a_user3)
    create_applicant_id(app, a_user3, name="Carol Gamma", gender="female")
    app3 = create_application_id(app, job_mgr, a_user3, status="rejected", resume_score=50.0)
    # Applicant 4: has an offer sent (not accepted) -> maps to 'offer sent'
    a_user4 = 7105
    create_user_id(app, a_user4)
    create_applicant_id(app, a_user4, name="Dave Delta", gender="male")
    app4 = create_application_id(app, job_mgr, a_user4, status="submitted", resume_score=88.0)
    
    # rely on helper to fetch candidate_id from Application
    create_offer_letter_id(app, app4, comp_id, status="sent")
    # 1) Filter: pending interview
    res_pending = client.get(_candidates(comp_id, "?status=pending%20interview"))
    assert_response(res_pending, expected_status=200)
    arr = res_pending.get_json()
    assert any(int(item.get("application_id")) == app1 for item in arr)
    # 2) Filter: interview done
    res_done = client.get(_candidates(comp_id, "?status=interview%20done"))
    assert_response(res_done, expected_status=200)
    arr = res_done.get_json()
    assert any(int(item.get("application_id")) == app2 for item in arr)
    # 3) Filter: rejected (application-level)
    res_rej = client.get(_candidates(comp_id, "?status=rejected"))
    assert_response(res_rej, expected_status=200)
    arr = res_rej.get_json()
    assert any(int(item.get("application_id")) == app3 for item in arr)
    # 4) Filter: offer sent
    res_offer = client.get(_candidates(comp_id, "?status=offer%20sent"))
    assert_response(res_offer, expected_status=200)
    arr = res_offer.get_json()
    assert any(int(item.get("application_id")) == app4 for item in arr)
    # 5) Filter by role (job_title == 'Engineer')
    res_role = client.get(_candidates(comp_id, "?role=Engineer"))
    assert_response(res_role, expected_status=200)
    arr = res_role.get_json()
    ids = {int(x.get("application_id")) for x in arr}
    assert app1 in ids and app2 in ids
    # 6) Search by name (partial, case-insensitive)
    res_search = client.get(_candidates(comp_id, "?search=alice"))
    assert_response(res_search, expected_status=200)
    arr = res_search.get_json()
    assert any(str(item.get("applicant_id")) == str(a_user1) or item.get("first_name","").lower() == "alice" for item in arr)

def test_reject_candidate_put(client, app):
    hr_user = 7201
    applicant = 7202

    create_user_id(app, hr_user)
    comp_id = create_company_id(app, hr_user, company_name="RejectCo")
    create_hr_profile_id(app, hr_user, comp_id)
    job_id = create_job_id(app, hr_user, comp_id)

    create_user_id(app, applicant)
    create_applicant_id(app, applicant, name="RejectMe", gender="male")
    application_id = create_application_id(app, job_id, applicant, status="submitted")

    # Call reject
    r = client.put(_reject(application_id))
    assert_response(r, expected_status=200, expected_message="candidate rejected successfully")

    with app.app_context():
        a = Application.query.get(application_id)
        assert a is not None
        assert a.status == "rejected"
