# tests/test_hr_api.py
import pytest
from werkzeug.security import generate_password_hash
from flask import Blueprint
from flask_restful import Api as RestfulApi
import json

from application.data.database import db as _db
from application.data.models import User, Company, HRProfile, Role

# Import the resource under test
from application.controller.apis.hr_apis import HRApi

# ---------- Debug helpers (prints useful info on failures) ----------
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
        # Try JSON first, otherwise raw text
        body = res.get_json(silent=True)
        body_text = json.dumps(body, indent=2) if body is not None else res.get_data(as_text=True)
        if expected_message.lower() not in str(body_text).lower():
            show_debug(expected_status=expected_status, expected_message=expected_message, res=res)
        assert expected_message.lower() in str(body_text).lower()

# ---------- register test-only routes ----------
@pytest.fixture(scope="session", autouse=True)
def register_test_routes(app):
    bp = Blueprint("test_hr_bp", __name__)
    api = RestfulApi(bp)
    api.add_resource(HRApi, "/hr", "/hr/<int:hr_id>")
    app.register_blueprint(bp, url_prefix="/_test_hr")
    yield

def _base():
    return "/_test_hr/hr"
def _single(hr_id):
    return f"{_base()}/{hr_id}"

# ---------- helpers that create DB rows and return IDs (no ORM objects returned) ----------
def create_user_id(app, user_id, email=None, name=None):
    with app.app_context():
        # ensure roles exist (idempotent)
        existing = {r.name for r in Role.query.all()}
        needed = {"applicant", "hr", "admin", "company"}
        for nm in needed - existing:
            _db.session.add(Role(name=nm, description=f"{nm} role"))
        _db.session.commit()

        email = email or f"user{user_id}@test.local"
        u = User(id=user_id, name=(name or f"User{user_id}"), email=email, password_hashed=generate_password_hash("pw"))
        _db.session.add(u)
        _db.session.commit()
        return u.id

def create_company_id(app, owner_user_id, company_name="ACME Co"):
    with app.app_context():
        c = Company(company_name=company_name, user_id=owner_user_id, company_email=f"{company_name.lower()}@test")
        _db.session.add(c)
        _db.session.commit()
        return c.id

def create_hr_profile_id(app, hr_user_id, company_id, first_name="HR", last_name="Person", contact_email=None):
    with app.app_context():
        if contact_email is None:
            contact_email = f"hr{hr_user_id}@test"
        hr = HRProfile(hr_id=hr_user_id, company_id=company_id, first_name=first_name, last_name=last_name, contact_email=contact_email)
        _db.session.add(hr)
        _db.session.commit()
        return hr.hr_id

# ---------- Tests ----------

def test_post_create_hr_creates_user_and_hr_profile_for_new_user(client, app):
    owner_user = 2101
    hr_user_id = None
    create_user_id(app, owner_user, email="owner2101@test")
    comp_id = create_company_id(app, owner_user, company_name="OwnerCo2101")

    payload = {
        "company_id": comp_id,
        "first_name": "Henry",
        "last_name": "HR",
        "email": "henry.new@example.com",
        "phone": "1234567890",
        "gender": "male",
        "username": "henry_hr",
        "password": "supersecret",
        "staff_id": "S-1001"
    }

    res = client.post(_base(), json=payload)
    assert_response(res, expected_status=201)
    data = res.get_json()
    assert data.get("contact_email") == payload["email"]
    assert data.get("first_name") == payload["first_name"]
    assert data.get("company_id") == comp_id
    assert isinstance(data.get("hr_id"), int) and data.get("hr_id") > 0

def test_post_create_hr_existing_user_conflict_returns_409(client, app):
    owner_user = 2201
    hr_user = 2202
    create_user_id(app, owner_user, email="owner2201@test")
    comp_id = create_company_id(app, owner_user, company_name="OwnerCo2201")

    create_user_id(app, hr_user, email="duplicate.hr@test", name="Dup HR")
    create_hr_profile_id(app, hr_user, comp_id, first_name="Already", last_name="HR")

    payload = {
        "company_id": comp_id,
        "email": "duplicate.hr@test",
        "password": "irrelevant",  
    }

    res = client.post(_base(), json=payload)
    assert_response(res, expected_status=409, expected_message="User already has an HR profile")

def test_post_create_hr_company_not_found_returns_404(client, app):
    # Ensure no company with ID 9999999
    payload = {
        "company_id": 9999999,
        "email": "no.company@test",
        "password": "pw"
    }
    res = client.post(_base(), json=payload)
    assert_response(res, expected_status=404, expected_message="company not found")

def test_get_list_and_single_hr_returns_data(client, app):
    owner_user = 2301
    hr_user = 2302
    create_user_id(app, owner_user, email="owner2301@test")
    comp_id = create_company_id(app, owner_user, company_name="OwnerCo2301")

    create_user_id(app, hr_user, email="list.hr@test")
    hr_id_created = create_hr_profile_id(app, hr_user, comp_id, first_name="List", last_name="HR", contact_email="list.hr@test")
    
    # Ensure data is committed by flushing
    with app.app_context():
        from application.data.database import db as _db
        _db.session.flush()
        _db.session.commit()

    rlist = client.get(_base())
    assert_response(rlist, expected_status=200)
    arr = rlist.get_json()
    assert isinstance(arr, list), f"Expected list, got {type(arr)}: {arr}"
    # Debug: print what we got
    if not any((item.get("contact_email") or "").lower() == "list.hr@test" for item in arr):
        print(f"DEBUG: HR list response: {arr}")
        print(f"DEBUG: Looking for email: list.hr@test")
        print(f"DEBUG: Found emails: {[item.get('contact_email') for item in arr]}")
    assert any((item.get("contact_email") or "").lower() == "list.hr@test" for item in arr)

    hr_items = [item for item in arr if (item.get("contact_email") or "").lower() == "list.hr@test"]
    assert hr_items, "created HR not found in GET list"
    hr_id = hr_items[0].get("hr_id")
    rsingle = client.get(_single(hr_id))
    assert_response(rsingle, expected_status=200)
    js = rsingle.get_json()
    assert js.get("first_name") == "List"
    assert js.get("contact_email").lower() == "list.hr@test"

def test_put_updates_hr_fields_and_delete_removes_profile(client, app):
    owner_user = 2401
    hr_user = 2402
    create_user_id(app, owner_user, email="owner2401@test")
    comp_id = create_company_id(app, owner_user, company_name="OwnerCo2401")
    create_user_id(app, hr_user, email="put.hr@test")
    create_hr_profile_id(app, hr_user, comp_id, first_name="Before", last_name="Name")
    update_payload = {
        "company_id": comp_id,  
        "first_name": "After",
        "last_name": "Changed",
        "phone": "999888777",
        "gender": "female",
        "username": "put_hr_user",
        "password": "newpw",
        "staff_id": "S-999"
    }
    rput = client.put(_single(hr_user), json=update_payload)
    # The API uses @marshal_with on put and returns the HR object; expect 200
    assert_response(rput, expected_status=200)
    updated = rput.get_json()
    assert updated.get("first_name") == "After"
    assert updated.get("last_name") == "Changed"
    assert str(updated.get("contact_phone")) == update_payload["phone"] or updated.get("contact_phone") == update_payload["phone"]
    rdel = client.delete(_single(hr_user))
    assert_response(rdel, expected_status=200)
    with app.app_context():
        assert HRProfile.query.get(hr_user) is None
