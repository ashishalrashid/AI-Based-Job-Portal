# tests/test_job_apis.py
import os
import tempfile
import pytest
import json
from datetime import datetime, date, timedelta
from flask import Blueprint
import application.controller.job.controllers as job_controllers
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

# -------------- Register test-only routes (attach controller functions to a unique blueprint) --------------
@pytest.fixture(scope="session", autouse=True)
def register_test_routes(app):
    test_bp = Blueprint("test_job_test_bp", __name__)

    test_bp.add_url_rule(
        "/stats/<int:company_id>",
        endpoint="test_job_stats",
        view_func=job_controllers.get_job_stats,
        methods=["GET"],
    )

    test_bp.add_url_rule(
        "/opportunities/<int:applicant_id>",
        endpoint="test_job_opportunities",
        view_func=job_controllers.get_job_opportunities,
        methods=["GET"],
    )

    test_bp.add_url_rule(
        "/detail/<int:job_id>/<int:applicant_id>",
        endpoint="test_job_detail",
        view_func=job_controllers.get_job_details,
        methods=["GET"],
    )

    test_bp.add_url_rule(
        "/download_jd/<int:job_id>",
        endpoint="test_job_download_jd",
        view_func=job_controllers.download_jd,
        methods=["GET"],
    )

    app.register_blueprint(test_bp, url_prefix="/_test_jobs")
    yield

def _stats(company_id):
    return f"/_test_jobs/stats/{company_id}"

def _opportunities(applicant_id, qs=""):
    return f"/_test_jobs/opportunities/{applicant_id}{qs}"

def _detail(job_id, applicant_id):
    return f"/_test_jobs/detail/{job_id}/{applicant_id}"

def _download_jd(job_id):
    return f"/_test_jobs/download_jd/{job_id}"

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
        # ensure user exists
        if not User.query.get(owner_user_id):
            create_user_id(app, owner_user_id)
        c = Company(company_name=company_name, user_id=owner_user_id, company_email=f"{company_name.lower()}@test")
        _db.session.add(c)
        _db.session.commit()
        return c.id

def create_hr_profile_id(app, hr_user_id, company_id, first_name="HR", last_name="Person"):
    with app.app_context():
        # ensure user exists
        if not User.query.get(hr_user_id):
            create_user_id(app, hr_user_id)
        hr = HRProfile.query.get(hr_user_id)
        if not hr:
            hr = HRProfile(hr_id=hr_user_id, company_id=company_id, first_name=first_name, last_name=last_name, contact_email=f"hr{hr_user_id}@test")
            _db.session.add(hr)
            _db.session.commit()
        return hr.hr_id

def create_job_id(app, hr_id, company_id, title="Engineer", created_date=None, num_positions=None, required_skills=None, attachment_url=None):
    """
    Create a JobPosting, ensuring HRProfile exists (some schemas FK to HRProfile.hr_id).
    Populate minimal fields so controller code can run.
    """
    with app.app_context():
        # ensure company exists
        if not Company.query.get(company_id):
            raise RuntimeError(f"create_job_id: company {company_id} not found")
        # ensure HRProfile exists
        if not HRProfile.query.get(hr_id):
            create_hr_profile_id(app, hr_id, company_id)
        jd = created_date or datetime.utcnow()
        job = JobPosting(
            hr_id=hr_id,
            company_id=company_id,
            job_title=title,
            created_date=jd,
            status="open",
            num_positions=num_positions,
            required_skills=required_skills,
            attachment_url=attachment_url
        )
        _db.session.add(job)
        _db.session.commit()
        return job.id

def create_applicant_id(app, user_id, name="Applicant", skills=None):
    with app.app_context():
        if not User.query.get(user_id):
            create_user_id(app, user_id, name=name)
        ap = ApplicantProfile.query.get(user_id)
        if not ap:
            ap = ApplicantProfile(applicant_id=user_id, name=name, skills=skills)
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

# ---------------- Tests ----------------

def test_stats_counts_and_positions_left(client, app):
    # Setup company, hr, job, applications, offers
    hr_user = 10001
    cand1 = 10002
    cand2 = 10003

    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="JobStatsCo")
    create_hr_profile_id(app, hr_user, comp)
    # job has 2 positions
    job_id = create_job_id(app, hr_user, comp, title="StatsEng", num_positions=2, created_date=datetime.utcnow() - timedelta(days=5))

    # create two applicants and applications
    create_applicant_id(app, cand1, name="Alpha")
    a1 = create_application_id(app, job_id, cand1, status="submitted")
    create_applicant_id(app, cand2, name="Beta")
    a2 = create_application_id(app, job_id, cand2, status="submitted")

    # create one interview (counts as interviewed)
    with app.app_context():
        intr = Interview(application_id=a1, status="completed", result="selected")
        _db.session.add(intr)
        _db.session.commit()

    # create one offer (counts toward offered_count)
    with app.app_context():
        ol = OfferLetter(application_id=a2, company_id=comp, status="sent", candidate_id=cand2)
        _db.session.add(ol)
        _db.session.commit()

    res = client.get(_stats(comp))
    assert_response(res, expected_status=200)
    arr = res.get_json()
    # Should have at least one job entry and counts reflect our data
    assert any(j["job_id"] == job_id for j in arr)
    job_entry = next(j for j in arr if j["job_id"] == job_id)
    assert job_entry["applications_count"] == 2
    assert job_entry["interviewed_count"] == 1
    assert job_entry["offered_count"] == 1
    # positions_left = num_positions - offered_count (2 - 1 = 1)
    assert job_entry["positions_left"] == 1
    # days_ago_posted approx 5
    assert abs(job_entry["days_ago_posted"] - 5) <= 1

def test_opportunities_role_search_and_pagination(client, app):
    hr_user = 10101
    cand = 10102

    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="JobsListCo")
    create_hr_profile_id(app, hr_user, comp)

    # job titles and skills
    create_job_id(app, hr_user, comp, title="Backend Engineer", required_skills="python,sql,aws")
    create_job_id(app, hr_user, comp, title="Frontend Engineer", required_skills="javascript,react,css")
    create_job_id(app, hr_user, comp, title="Product Manager", required_skills="communication,planning")

    # create applicant with some skills
    create_user_id(app, cand)
    create_applicant_id(app, cand, name="JobSeeker", skills="python,css")

    # role filter (match Backend)
    res_role = client.get(_opportunities(cand, "?role=Backend"))
    assert_response(res_role, expected_status=200)
    j = res_role.get_json()
    assert j["total_jobs"] >= 1
    assert any("Backend" in job["position"] for job in j["jobs"])

    # search filter (company name or job title)
    res_search = client.get(_opportunities(cand, "?search=frontend"))
    assert_response(res_search, expected_status=200)
    j = res_search.get_json()
    assert any("Frontend" in job["position"] for job in j["jobs"])

    # pagination: per_page small should create multiple pages if enough jobs exist
    res_page = client.get(_opportunities(cand, "?page=1&per_page=1"))
    assert_response(res_page, expected_status=200)
    j = res_page.get_json()
    assert j["per_page"] == 1
    assert isinstance(j["total_jobs"], int)

def test_job_detail_skills_match_and_company_info(client, app):
    hr_user = 10201
    cand = 10202

    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="JobDetailCo")
    create_hr_profile_id(app, hr_user, comp)

    # job with required skills and some metadata
    job_id = create_job_id(app, hr_user, comp, title="DetailEngineer", required_skills="python,sql")

    create_user_id(app, cand)
    create_applicant_id(app, cand, name="DetailCandidate", skills="python,go")

    # create a couple of applications to ensure application_count populated
    # create a couple of applications to ensure application_count populated
    create_application_id(app, job_id, cand)

    # create a second applicant and application so the count is > 1
    second_cand = cand + 1
    create_user_id(app, second_cand)
    create_applicant_id(app, second_cand, name="SecondCandidate")
    create_application_id(app, job_id, second_cand)

    res = client.get(_detail(job_id, cand))
    assert_response(res, expected_status=200)
    j = res.get_json()
    assert j["job_id"] == job_id
    assert "job_title" in j
    assert "company_info" in j
    assert "skills_match" in j
    assert "total_applicants" in j

def test_download_jd_google_drive_redirect_and_local_file(client, app, tmp_path):
    hr_user = 10301
    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="JobDownloadCo")
    create_hr_profile_id(app, hr_user, comp)

    # Create job with Google Drive link
    gdrive_link = "https://drive.google.com/file/d/ABC123DEF/view?usp=sharing"
    job_g = create_job_id(app, hr_user, comp, title="DriveJD", attachment_url=gdrive_link)

    res = client.get(_download_jd(job_g))
    # expecting redirect (302) to a direct download URL
    assert_response(res, expected_status=302)

    # Create a local temp file and set job.attachment_url to it
    tmp_file = tmp_path / "jd_test.pdf"
    tmp_file.write_text("dummy content")

    with app.app_context():
        job = JobPosting.query.get(job_g)
        job.attachment_url = str(tmp_file)
        _db.session.commit()

    res2 = client.get(_download_jd(job_g))
    # send_file usually returns 200 with file content; framework may stream; check status
    assert_response(res2, expected_status=200)

