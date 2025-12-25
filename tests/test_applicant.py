# tests/test_applicant_apis.py
import os
import json
import pytest
from datetime import date
from flask import Blueprint
import application.controller.applicant.controllers as applicant_controllers
from application.data.database import db as _db
from application.data.models import (
    User, ApplicantProfile, Company, HRProfile, JobPosting,
    Application, PreviousExperience, PreviousEducation, Project, Certification, Role
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
    print("----- PARSED JSON (if any) -----")
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

# -------------- Register test-only routes --------------
@pytest.fixture(scope="session", autouse=True)
def register_test_routes(app):
    bp = Blueprint("test_applicant_bp", __name__)

    # Profile
    bp.add_url_rule("/profile/<int:application_id>", endpoint="test_profile", view_func=applicant_controllers.get_candidate_profile, methods=["GET"])

    # Experiences
    bp.add_url_rule("/<int:applicant_id>/experiences", endpoint="test_get_exps", view_func=applicant_controllers.get_experiences, methods=["GET"])
    bp.add_url_rule("/<int:applicant_id>/experiences", endpoint="test_post_exp", view_func=applicant_controllers.add_experience, methods=["POST"])
    bp.add_url_rule("/<int:applicant_id>/experiences", endpoint="test_delete_exps", view_func=applicant_controllers.delete_all_experiences, methods=["DELETE"])

    # Education
    bp.add_url_rule("/<int:applicant_id>/education", endpoint="test_get_edu", view_func=applicant_controllers.get_education, methods=["GET"])
    bp.add_url_rule("/<int:applicant_id>/education", endpoint="test_post_edu", view_func=applicant_controllers.add_education, methods=["POST"])
    bp.add_url_rule("/<int:applicant_id>/education", endpoint="test_delete_edu", view_func=applicant_controllers.delete_all_education, methods=["DELETE"])

    # Projects
    bp.add_url_rule("/<int:applicant_id>/projects", endpoint="test_get_projs", view_func=applicant_controllers.get_projects, methods=["GET"])
    bp.add_url_rule("/<int:applicant_id>/projects", endpoint="test_post_proj", view_func=applicant_controllers.add_project, methods=["POST"])

    # Certifications
    bp.add_url_rule("/<int:applicant_id>/certifications", endpoint="test_get_certs", view_func=applicant_controllers.get_certifications, methods=["GET"])
    bp.add_url_rule("/<int:applicant_id>/certifications", endpoint="test_post_cert", view_func=applicant_controllers.add_certification, methods=["POST"])
    bp.add_url_rule("/<int:applicant_id>/certifications", endpoint="test_delete_certs", view_func=applicant_controllers.delete_all_certifications, methods=["DELETE"])

    # Downloads
    bp.add_url_rule("/<int:applicant_id>/download_resume", endpoint="test_download_resume", view_func=applicant_controllers.download_resume, methods=["GET"])
    bp.add_url_rule("/<int:applicant_id>/download_cover_letter", endpoint="test_download_cover", view_func=applicant_controllers.download_cover_letter, methods=["GET"])

    app.register_blueprint(bp, url_prefix="/_test_applicant")
    yield

def _profile(application_id): return f"/_test_applicant/profile/{application_id}"
def _get_exps(applicant_id): return f"/_test_applicant/{applicant_id}/experiences"
def _get_edu(applicant_id): return f"/_test_applicant/{applicant_id}/education"
def _get_projs(applicant_id): return f"/_test_applicant/{applicant_id}/projects"
def _get_certs(applicant_id): return f"/_test_applicant/{applicant_id}/certifications"
def _download_resume(applicant_id): return f"/_test_applicant/{applicant_id}/download_resume"
def _download_cover(applicant_id): return f"/_test_applicant/{applicant_id}/download_cover_letter"

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
        u = User(id=user_id, name=(name or f"User{user_id}"), email=email, phone=phone, password_hashed="pw")
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

def create_hr_profile_id(app, hr_user_id, company_id):
    with app.app_context():
        if not User.query.get(hr_user_id):
            create_user_id(app, hr_user_id)
        hr = HRProfile.query.get(hr_user_id)
        if not hr:
            hr = HRProfile(hr_id=hr_user_id, company_id=company_id, first_name="HR", last_name="Person", contact_email=f"hr{hr_user_id}@test")
            _db.session.add(hr)
            _db.session.commit()
        return hr.hr_id

def create_job_id(app, hr_id, company_id, title="Engineer"):
    with app.app_context():
        if not Company.query.get(company_id):
            raise RuntimeError("company not found")
        if not HRProfile.query.get(hr_id):
            create_hr_profile_id(app, hr_id, company_id)
        job = JobPosting(hr_id=hr_id, company_id=company_id, job_title=title, status="open")
        _db.session.add(job)
        _db.session.commit()
        return job.id

def create_applicant_profile(app, user_id, name="Applicant", skills=None,
                             resume_path=None, resume_filename=None,
                             cover_path=None, cover_filename=None):
    """
    Create an ApplicantProfile if missing. If it already exists, optionally update
    resume/cover file path and filename when those args are provided.
    """
    with app.app_context():
        if not User.query.get(user_id):
            create_user_id(app, user_id)
        ap = ApplicantProfile.query.get(user_id)
        if not ap:
            ap = ApplicantProfile(applicant_id=user_id, name=name, skills=skills)
            if resume_path:
                ap.resume_file_path = resume_path
                ap.resume_filename = resume_filename or os.path.basename(resume_path)
            if cover_path:
                ap.cover_letter_file_path = cover_path
                ap.cover_letter_filename = cover_filename or os.path.basename(cover_path)
            _db.session.add(ap)
            _db.session.commit()
        else:
            # Update existing profile with any provided optional fields
            changed = False
            if name and ap.name != name:
                ap.name = name
                changed = True
            if skills is not None and ap.skills != skills:
                ap.skills = skills
                changed = True
            if resume_path:
                ap.resume_file_path = resume_path
                ap.resume_filename = resume_filename or os.path.basename(resume_path)
                changed = True
            if cover_path:
                ap.cover_letter_file_path = cover_path
                ap.cover_letter_filename = cover_filename or os.path.basename(cover_path)
                changed = True
            if changed:
                _db.session.commit()
        return ap.applicant_id

def create_application_id(app, job_id, applicant_id, status="submitted"):
    with app.app_context():
        if not JobPosting.query.get(job_id):
            raise RuntimeError("job not found")
        if not ApplicantProfile.query.get(applicant_id):
            raise RuntimeError("applicant not found")
        application = Application(job_id=job_id, applicant_id=applicant_id, status=status)
        _db.session.add(application)
        _db.session.commit()
        return application.id

def clear_files(path_list):
    for p in path_list:
        try:
            if os.path.exists(p):
                os.remove(p)
        except Exception:
            pass

# -------------- Tests --------------

def test_profile_endpoint_returns_full_profile(client, app):
    hr = 4001
    cand = 4002

    create_user_id(app, hr)
    comp = create_company_id(app, hr, company_name="ProfCo")
    create_hr_profile_id(app, hr, comp)
    job = create_job_id(app, hr, comp, title="ProfJob")

    # create user/applicant/profile and application
    create_user_id(app, cand, email=f"cand{cand}@test.local")
    create_applicant_profile(app, cand, name="Full Candidate", skills="python,flask")
    app_id = create_application_id(app, job, cand)

    # add some experience/education/project/cert via helpers (direct DB) so profile has content
    with app.app_context():
        e = PreviousExperience(applicant_id=cand, position="Eng", company="X", start_date=None, end_date=None, description="did stuff")
        _db.session.add(e)
        ed = PreviousEducation(applicant_id=cand, university="U", degree="BSc", field="CS")
        _db.session.add(ed)
        p = Project(applicant_id=cand, title="P", description="d", technologies="py", project_url=None)
        _db.session.add(p)
        c = Certification(applicant_id=cand, certificate_name="Cert", issuing_organization="Org")
        _db.session.add(c)
        _db.session.commit()

    res = client.get(_profile(app_id))
    assert_response(res, expected_status=200)
    j = res.get_json()
    assert j["name"] == "Full Candidate"
    assert "experiences" in j and isinstance(j["experiences"], list)
    assert "educations" in j and isinstance(j["educations"], list)
    assert "projects" in j and isinstance(j["projects"], list)
    assert "certifications" in j and isinstance(j["certifications"], list)

def test_add_and_get_experience_education_project_certification(client, app):
    cand = 4010
    create_user_id(app, cand)
    create_applicant_profile(app, cand, name="AddTest")

    # EXPERIENCE
    payload_e = {"position":"SE","company":"C","start_date":"2020-01-01","end_date":"2021-01-01","description":"ok"}
    rpost_e = client.post(_get_exps(cand), json=payload_e)
    assert_response(rpost_e, expected_status=201)
    rget_e = client.get(_get_exps(cand))
    assert_response(rget_e, expected_status=200)
    arr_e = rget_e.get_json()
    assert any(x["position"] == "SE" for x in arr_e)

    # EDUCATION
    payload_ed = {"university":"U","degree":"BSc","field":"CS","grade":"A","grade_out_of":"4","start_date":"2015-01-01","end_date":"2019-01-01"}
    rpost_ed = client.post(_get_edu(cand), json=payload_ed)
    assert_response(rpost_ed, expected_status=201)
    rget_ed = client.get(_get_edu(cand))
    assert_response(rget_ed, expected_status=200)
    arr_ed = rget_ed.get_json()
    assert any(x["degree"] == "BSc" for x in arr_ed)

def test_projects_and_certifications_and_downloads(client, app, tmp_path):
    cand = 4020
    create_user_id(app, cand)
    create_applicant_profile(app, cand, name="NoFile")
    # project
    payload_p = {"title":"Proj","description":"d","technologies":"py","project_url":"http://"}
    rpost_p = client.post(_get_projs(cand), json=payload_p)
    assert_response(rpost_p, expected_status=201)
    rget_p = client.get(_get_projs(cand))
    assert_response(rget_p, expected_status=200)
    arr_p = rget_p.get_json()
    assert any(x["title"] == "Proj" for x in arr_p)

    # certification
    payload_c = {"certificate_name":"CertX","issuing_organization":"OrgX","issue_date":"2020-01-01","expiry_date":"2022-01-01","credential_id":"ID1","credential_url":"http://"}
    rpost_c = client.post(_get_certs(cand), json=payload_c)
    assert_response(rpost_c, expected_status=201)
    rget_c = client.get(_get_certs(cand))
    assert_response(rget_c, expected_status=200)
    arr_c = rget_c.get_json()
    assert any(x["certificate_name"] == "CertX" for x in arr_c)

def test_delete_experiences_education_certifications(client, app, tmp_path):
    """Test DELETE endpoints for experiences, education, and certifications"""
    cand = 4030
    create_user_id(app, cand)
    create_applicant_profile(app, cand, name="DeleteTest")

    # Add some experiences
    payload_e = {"position": "SE", "company": "C", "start_date": "2020-01-01", "end_date": "2021-01-01", "description": "ok"}
    client.post(_get_exps(cand), json=payload_e)
    client.post(_get_exps(cand), json={"position": "SSE", "company": "C2", "start_date": "2021-01-01", "end_date": "2022-01-01"})
    
    # Verify experiences exist
    rget_e = client.get(_get_exps(cand))
    assert_response(rget_e, expected_status=200)
    arr_e = rget_e.get_json()
    assert len(arr_e) == 2

    # DELETE all experiences
    rdel_e = client.delete(_get_exps(cand))
    assert_response(rdel_e, expected_status=200)
    j = rdel_e.get_json()
    assert j["message"] == "All experiences deleted"
    
    # Verify all deleted
    rget_e2 = client.get(_get_exps(cand))
    assert_response(rget_e2, expected_status=200)
    assert len(rget_e2.get_json()) == 0

    # Add education
    payload_ed = {"university": "U", "degree": "BSc", "field": "CS", "grade": "A", "grade_out_of": "4", "start_date": "2015-01-01", "end_date": "2019-01-01"}
    client.post(_get_edu(cand), json=payload_ed)
    client.post(_get_edu(cand), json={"university": "U2", "degree": "MSc", "field": "CS"})
    
    # Verify education exists
    rget_ed = client.get(_get_edu(cand))
    assert_response(rget_ed, expected_status=200)
    assert len(rget_ed.get_json()) == 2

    # DELETE all education
    rdel_ed = client.delete(_get_edu(cand))
    assert_response(rdel_ed, expected_status=200)
    j = rdel_ed.get_json()
    assert j["message"] == "All education deleted"
    
    # Verify all deleted
    rget_ed2 = client.get(_get_edu(cand))
    assert_response(rget_ed2, expected_status=200)
    assert len(rget_ed2.get_json()) == 0

    # Add certifications
    payload_c = {"certificate_name": "CertX", "issuing_organization": "OrgX", "issue_date": "2020-01-01", "expiry_date": "2022-01-01", "credential_id": "ID1", "credential_url": "http://"}
    client.post(_get_certs(cand), json=payload_c)
    client.post(_get_certs(cand), json={"certificate_name": "CertY", "issuing_organization": "OrgY"})
    
    # Verify certifications exist
    rget_c = client.get(_get_certs(cand))
    assert_response(rget_c, expected_status=200)
    assert len(rget_c.get_json()) == 2

    # DELETE all certifications
    rdel_c = client.delete(_get_certs(cand))
    assert_response(rdel_c, expected_status=200)
    j = rdel_c.get_json()
    assert j["message"] == "All certifications deleted"
    
    # Verify all deleted
    rget_c2 = client.get(_get_certs(cand))
    assert_response(rget_c2, expected_status=200)
    assert len(rget_c2.get_json()) == 0

    # downloads: none -> 404
    res = client.get(_download_resume(cand))
    assert_response(res, expected_status=404)
    res2 = client.get(_download_cover(cand))
    assert_response(res2, expected_status=404)

    # create files and attach to profile
    resume = tmp_path / "resume_test.pdf"
    resume.write_text("resume")
    cover = tmp_path / "cover_test.pdf"
    cover.write_text("cover")

    create_applicant_profile(app, cand, name="NoFile", resume_path=str(resume), resume_filename="resume_test.pdf", cover_path=str(cover), cover_filename="cover_test.pdf")

    res3 = client.get(_download_resume(cand))
    assert_response(res3, expected_status=200)
    res4 = client.get(_download_cover(cand))
    assert_response(res4, expected_status=200)

    # cleanup
    clear_files([str(resume), str(cover)])
