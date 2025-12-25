import os
import io
import pytest
from datetime import datetime
from werkzeug.security import generate_password_hash
from tests.utils.require_role import require_role
from application.data.models import ApplicantProfile, User, Role
from application.data.database import db as _db

# ---------- helpers ----------
def _file_tuple(filename="resume.pdf", content=b"PDF-CONTENT"):
    return (io.BytesIO(content), filename)

def _exists(path):
    return bool(path) and os.path.exists(path)

def _cleanup_uploads(app):
    uploads = os.path.join(app.root_path, "uploads")
    if os.path.isdir(uploads):
        for root, dirs, files in os.walk(uploads, topdown=False):
            for f in files:
                try:
                    os.remove(os.path.join(root, f))
                except Exception:
                    pass
            for d in dirs:
                try:
                    os.rmdir(os.path.join(root, d))
                except Exception:
                    pass
        try:
            os.rmdir(uploads)
        except Exception:
            pass

# ---------- Note ----------
# This test file used to register a blueprint test_applicant_bp, which
# caused a duplicate-blueprint error when the suite also registered the
# same blueprint centrally. We removed the per-file registration so the
# centrally-registered routes in tests/conftest.py are used instead.
#
# The central conftest should register ApplicantAPI at:
#   url_prefix="/_test_applicant"
#   routes: "/applicant", "/applicant/<int:applicant_id>"

def _base():
    return "/_test_applicant/applicant"
def _single(aid):
    return f"{_base()}/{aid}"

# ---------- helper to create a minimal User for FK ----------
def create_user_for_id(app, user_id, name=None):

    with app.app_context():
        # ensure roles exist - this is idempotent
        existing = {r.name for r in Role.query.all()}
        needed = {"applicant", "hr", "admin", "company"}
        for nm in needed - existing:
            _db.session.add(Role(name=nm, description=f"{nm} role"))
        _db.session.commit()

        email = f"user{user_id}@example.test"
        # allow explicit id set; SQLAlchemy will accept it for autoincrement PK
        user = User(id=user_id, name=(name or f"User{user_id}"), email=email,
                    password_hashed=generate_password_hash("pw"))
        _db.session.add(user)
        _db.session.commit()
        return user

# ---------- Tests ----------
def test_create_applicant_success(client, app):
    base = _base()
    aid = 201
    try:
        create_user_for_id(app, aid, name="ApplicantUser201")

        data = {
            "applicant_id": str(aid),
            "name": "John Doe",
            "skills": "Python, SQL",
            "resume": _file_tuple("resume.pdf", b"%PDF-sample"),
            "cover_letter": _file_tuple("cover.docx", b"COVER")
        }
        res = client.post(base, data=data, content_type="multipart/form-data")
        if res.status_code != 201:
            print("POST returned:", res.status_code)
            print(res.get_data(as_text=True))
        assert res.status_code == 201, f"Expected 201, got {res.status_code}"
        j = res.get_json()
        assert j["applicant_id"] == aid
        assert j["name"] == "John Doe"
        assert "Python" in j["skills"]
        assert j["resume_filename"].endswith("resume.pdf")
        assert isinstance(j["resume_size"], int) and j["resume_size"] > 0
        assert ("/uploads/resumes" in j["resume_file_path"]) or (os.path.sep + "uploads" + os.path.sep + "resumes" in j["resume_file_path"])
        try:
            datetime.fromisoformat(j["resume_uploaded_at"].replace("Z", "+00:00"))
        except Exception as e:
            pytest.fail(f"resume_uploaded_at not parseable: {j.get('resume_uploaded_at')} ({e})")
    finally:
        _cleanup_uploads(app)

def test_get_list_and_single(client, app):
    base = _base()
    aid = 202
    try:
        create_user_for_id(app, aid, name="ApplicantUser202")
        create = client.post(base, data={
            "applicant_id": str(aid),
            "name": "Jane List",
            "address": "Mumbai",
            "gender": "Female",
            "highest_qualification": "BTech",
            "institution_name": "IIT Bombay",
            "graduation_year": "2024",
            "skills": "Python",
            "resume": _file_tuple("jane.pdf", b"X")
        }, content_type="multipart/form-data")
        if create.status_code != 201:
            print("Create returned:", create.status_code, create.get_data(as_text=True))
        assert create.status_code == 201
        rlist = client.get(base)
        if rlist.status_code != 200:
            print("GET list returned:", rlist.status_code, rlist.get_data(as_text=True))
        assert rlist.status_code == 200
        arr = rlist.get_json()
        assert isinstance(arr, list)
        found = next((it for it in arr if it.get("applicant_id") == aid), None)
        assert found is not None
        assert found.get("address") == "Mumbai"
        rs = client.get(_single(aid))
        if rs.status_code != 200:
            print("GET single returned:", rs.status_code, rs.get_data(as_text=True))
        assert rs.status_code == 200
        j = rs.get_json()
        assert j["applicant_id"] == aid
        assert j["name"] == "Jane List"
    finally:
        _cleanup_uploads(app)

def test_put_update_and_invalid_resume(client, app):
    base = _base()
    aid = 203
    try:
        create_user_for_id(app, aid, name="ApplicantUser203")
        create = client.post(base, data={
            "applicant_id": str(aid),
            "name": "Put User",
            "skills": "Python",
            "resume": _file_tuple("orig.pdf", b"orig")
        }, content_type="multipart/form-data")
        assert create.status_code == 201
        j1 = create.get_json()
        old_path = j1["resume_file_path"]

        upd = client.put(_single(aid), data={
            "name": "Put Updated",
            "skills": "Python, SQL, React",
            "resume": _file_tuple("updated.pdf", b"newpdf")
        }, content_type="multipart/form-data")
        if upd.status_code != 200:
            print("PUT returned:", upd.status_code, upd.get_data(as_text=True))
        assert upd.status_code == 200
        j2 = upd.get_json()
        assert j2["name"] == "Put Updated"
        assert "React" in j2["skills"]
        assert j2["resume_filename"].endswith("updated.pdf")
        try:
            datetime.fromisoformat(j2["resume_uploaded_at"].replace("Z", "+00:00"))
        except Exception as e:
            pytest.fail(f"resume_uploaded_at not parseable: {e}")
        assert not _exists(old_path)

        # invalid resume
        bad = client.put(_single(aid), data={
            "resume": _file_tuple("bad.exe", b"exe")
        }, content_type="multipart/form-data")
        assert bad.status_code == 400
        bj = bad.get_json()
        assert "invalid resume" in bj.get("message", "").lower()
    finally:
        _cleanup_uploads(app)

def test_delete_applicant(client, app):
    base = _base()
    aid = 204
    try:
        create_user_for_id(app, aid, name="ApplicantUser204")
        create = client.post(base, data={
            "applicant_id": str(aid),
            "name": "To Delete",
            "resume": _file_tuple("del.pdf", b"y")
        }, content_type="multipart/form-data")
        assert create.status_code == 201
        j = create.get_json()
        resume_path = j["resume_file_path"]

        rp = client.put(_single(aid), data={"cover_letter": _file_tuple("cover.pdf", b"c")}, content_type="multipart/form-data")
        assert rp.status_code == 200

        rd = client.delete(_single(aid))
        if rd.status_code != 200:
            print("DELETE returned:", rd.status_code, rd.get_data(as_text=True))
        assert rd.status_code == 200

        with app.app_context():
            assert ApplicantProfile.query.get(aid) is None
        assert not _exists(resume_path)
    finally:
        _cleanup_uploads(app)