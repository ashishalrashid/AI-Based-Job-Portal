# tests/test_job_apis.py
import io
import json
import os
import re
import pytest
from werkzeug.security import generate_password_hash
from flask import Blueprint
from flask_restful import Api as RestfulApi

from application.data.database import db as _db
from application.data.models import User, Company, HRProfile, Role, JobPosting

# Resource under test
from application.controller.apis.job_apis import JobAPI

# ---------------- debug helpers ----------------
def show_debug(expected_status=None, expected_message=None, res=None):
    print("\n================ DEBUG OUTPUT ================")
    if expected_status is not None:
        print(f"EXPECTED STATUS: {expected_status}")
    if expected_message:
        print(f"EXPECTED MESSAGE SUBSTRING: {expected_message}")
    if res is None:
        print("<no response object>")
        return
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

# -------------- register resource under a test blueprint --------------
@pytest.fixture(scope="session", autouse=True)
def register_test_routes(app):
    bp = Blueprint("test_job_bp", __name__)
    api = RestfulApi(bp)
    api.add_resource(JobAPI, "/job", "/job/<int:job_id>")
    app.register_blueprint(bp, url_prefix="/_test_job")
    yield

def _base():
    return "/_test_job/job"
def _single(jid):
    return f"{_base()}/{jid}"

# -------------- DB helper functions (create primitives, not ORM objects) --------------
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
        u = User(id=user_id, name=(name or f"User{user_id}"), email=email, password_hashed=generate_password_hash("pw"))
        _db.session.add(u)
        _db.session.commit()
        return u.id

def create_company_id(app, owner_user_id, company_name="ACME Co"):
    with app.app_context():
        c = Company(company_name=company_name, user_id=owner_user_id, company_email=f"{company_name.lower().replace(' ','')}@test")
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

# ---------------- Tests ----------------

def test_post_job_requires_hr_id_and_job_title_and_company_id(client, app):
    # Missing hr_id
    res = client.post(_base(), json={"job_title": "Eng"})
    assert_response(res, expected_status=400, expected_message="hr_id is required")

    # Missing job_title
    res = client.post(_base(), json={"hr_id": 1})
    assert_response(res, expected_status=400, expected_message="job_title is required")

    # Missing company_id
    res = client.post(_base(), json={"hr_id": 1, "job_title": "Eng"})
    assert_response(res, expected_status=400, expected_message="company id is required")

def test_post_job_gdrive_attachment_validation(client, app):
    owner = 4101
    create_user_id(app, owner, email="owner4101@test")
    comp_id = create_company_id(app, owner, "GDriveCo4101")
    # create hr user
    hr = 4102
    create_user_id(app, hr, email="hr4102@test")
    create_hr_profile_id(app, hr, comp_id)

    # invalid URL
    payload = {"hr_id": hr, "company_id": comp_id, "job_title": "GDrive role", "attachment_type": "gdrive", "attachment_url": "http://notdrive.example.com/foo"}
    res = client.post(_base(), json=payload)
    assert_response(res, expected_status=400, expected_message="attachment_url must be a Google Drive link")

    # missing url
    payload = {"hr_id": hr, "company_id": comp_id, "job_title": "GDrive role", "attachment_type": "gdrive"}
    res = client.post(_base(), json=payload)
    assert_response(res, expected_status=400, expected_message="attachment_url is required when attachment_type=gdrive")

    # valid gdrive url (should create)
    payload = {"hr_id": hr, "company_id": comp_id, "job_title": "GDrive role", "attachment_type": "gdrive", "attachment_url": "https://drive.google.com/file/d/12345/view"}
    res = client.post(_base(), json=payload)
    assert_response(res, expected_status=201)
    j = res.get_json()
    assert j["job_title"] == "GDrive role"
    assert j["attachment_type"] == "gdrive"
    assert j["attachment_url"].startswith("https://drive.google.com")

def test_post_job_file_upload_creates_file_and_metadata(client, app, tmp_path):
    """
    multipart/form-data POST with attachment_type=file and file part should succeed.
    """
    owner = 4201
    create_user_id(app, owner, email="owner4201@test")
    comp_id = create_company_id(app, owner, "UploadCo4201")

    hr = 4202
    create_user_id(app, hr, email="hr4202@test")
    create_hr_profile_id(app, hr, comp_id)

    # prepare file bytes
    file_bytes = b"%PDF-1.4 test content\n"
    data = {
        "hr_id": str(hr),
        "company_id": str(comp_id),
        "job_title": "File Role",
        "attachment_type": "file"
    }
    file_tuple = (io.BytesIO(file_bytes), "spec.pdf")

    # Flask test client needs data with files as tuples
    res = client.post(_base(), data={**data, "file": file_tuple}, content_type="multipart/form-data")
    if res.status_code != 201:
        print("CREATE FILE JOB FAILED RAW BODY:", res.get_data(as_text=True))
    assert_response(res, expected_status=201)
    j = res.get_json()
    assert j["job_title"] == "File Role"
    # uploaded metadata should be present
    assert j["attachment_filename"] == "spec.pdf"
    assert j["attachment_mimetype"] is not None
    assert isinstance(j["attachment_size"], int) and j["attachment_size"] > 0
    # saved path should be inside app.root_path/uploads
    if j.get("attachment_url"):
        assert "uploads" in j["attachment_url"]

def test_get_list_and_single_job(client, app):
    owner = 4301
    create_user_id(app, owner, email="owner4301@test")
    comp_id = create_company_id(app, owner, "ListCo4301")

    hr = 4302
    create_user_id(app, hr, email="hr4302@test")
    create_hr_profile_id(app, hr, comp_id)

    # create a job
    r = client.post(_base(), json={"hr_id": hr, "company_id": comp_id, "job_title": "ListJob"})
    assert_response(r, expected_status=201)
    jid = r.get_json()["id"]

    rlist = client.get(_base())
    assert_response(rlist, expected_status=200)
    arr = rlist.get_json()
    assert any(item.get("id") == jid for item in arr)

    rsingle = client.get(_single(jid))
    assert_response(rsingle, expected_status=200)
    single = rsingle.get_json()
    assert single["job_title"] == "ListJob"

def test_put_updates_job_and_no_valid_fields_returns_400(client, app):
    owner = 4401
    create_user_id(app, owner, email="owner4401@test")
    comp_id = create_company_id(app, owner, "PutCo4401")

    hr = 4402
    create_user_id(app, hr, email="hr4402@test")
    create_hr_profile_id(app, hr, comp_id)

    r = client.post(_base(), json={"hr_id": hr, "company_id": comp_id, "job_title": "ToUpdate"})
    assert_response(r, expected_status=201)
    jid = r.get_json()["id"]

    # valid update
    rput = client.put(_single(jid), json={"job_title": "UpdatedTitle", "level": "senior"})
    assert_response(rput, expected_status=200)
    upd = rput.get_json()
    assert upd["job_title"] == "UpdatedTitle"
    assert upd["level"] == "senior"

    # send PUT with no updatable fields (all null) -> expected 400
    rput2 = client.put(_single(jid), json={})
    assert_response(rput2, expected_status=400, expected_message="No valid fields to update")

def test_delete_job_removes_record(client, app):
    owner = 4501
    create_user_id(app, owner, email="owner4501@test")
    comp_id = create_company_id(app, owner, "DelCo4501")

    hr = 4502
    create_user_id(app, hr, email="hr4502@test")
    create_hr_profile_id(app, hr, comp_id)

    r = client.post(_base(), json={"hr_id": hr, "company_id": comp_id, "job_title": "ToDelete"})
    assert_response(r, expected_status=201)
    jid = r.get_json()["id"]

    rdel = client.delete(_single(jid))
    assert_response(rdel, expected_status=200)

    with app.app_context():
        assert JobPosting.query.get(jid) is None
