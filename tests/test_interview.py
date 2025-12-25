import pytest
import json
from datetime import date, datetime, timedelta, time
from flask import Blueprint
import application.controller.interview.controllers as interview_controllers
from application.data.database import db as _db
from application.data.models import (
    User, Company, HRProfile, JobPosting, ApplicantProfile,
    Role, Application, Interview
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
    test_bp = Blueprint("test_interview_test_bp", __name__)

    test_bp.add_url_rule(
        "/feedback_pending/<int:company_id>",
        endpoint="test_feedback_pending",
        view_func=interview_controllers.get_interview_feedback_pending_count,
        methods=["GET"],
    )

    test_bp.add_url_rule(
        "/sorted_by_date/<int:hr_id>",
        endpoint="test_sorted_by_date",
        view_func=interview_controllers.get_interviews_for_hr_sorted,
        methods=["GET"],
    )

    test_bp.add_url_rule(
        "/schedule/<int:application_id>/<int:hr_id>",
        endpoint="test_schedule",
        view_func=interview_controllers.schedule_interview,
        methods=["POST"],
    )

    test_bp.add_url_rule(
        "/reject/<int:application_id>",
        endpoint="test_reject_candidate",
        view_func=interview_controllers.reject_candidate,
        methods=["POST"],
    )

    test_bp.add_url_rule(
        "/stats/scheduled_month/<int:company_id>",
        endpoint="test_scheduled_month",
        view_func=interview_controllers.scheduled_this_month,
        methods=["GET"],
    )

    test_bp.add_url_rule(
        "/stats/scheduled_week/<int:company_id>",
        endpoint="test_scheduled_week",
        view_func=interview_controllers.scheduled_this_week,
        methods=["GET"],
    )

    test_bp.add_url_rule(
        "/stats/completed/<int:company_id>",
        endpoint="test_completed",
        view_func=interview_controllers.completed_interviews,
        methods=["GET"],
    )

    test_bp.add_url_rule(
        "/stats/pending_feedback/<int:company_id>",
        endpoint="test_pending_feedback",
        view_func=interview_controllers.pending_feedback,
        methods=["GET"],
    )

    test_bp.add_url_rule(
        "/cards/<int:company_id>",
        endpoint="test_cards",
        view_func=interview_controllers.get_interview_cards,
        methods=["GET"],
    )

    test_bp.add_url_rule(
        "/evaluation/<int:interview_id>",
        endpoint="test_evaluation",
        view_func=interview_controllers.get_interview_evaluation,
        methods=["GET"],
    )

    test_bp.add_url_rule(
        "/feedback/<int:interview_id>",
        endpoint="test_feedback",
        view_func=interview_controllers.submit_interview_feedback,
        methods=["POST"],
    )

    test_bp.add_url_rule(
        "/decision/<int:interview_id>",
        endpoint="test_decision",
        view_func=interview_controllers.set_interview_decision,
        methods=["PUT"],
    )

    test_bp.add_url_rule(
        "/applicant/<int:applicant_id>/summary",
        endpoint="test_applicant_summary",
        view_func=interview_controllers.get_interview_summary,
        methods=["GET"],
    )

    test_bp.add_url_rule(
        "/applicant/<int:applicant_id>/list",
        endpoint="test_applicant_list",
        view_func=interview_controllers.get_all_applicant_interviews,
        methods=["GET"],
    )

    test_bp.add_url_rule(
        "/<int:interview_id>/cancel",
        endpoint="test_cancel",
        view_func=interview_controllers.cancel_interview,
        methods=["PUT"],
    )

    app.register_blueprint(test_bp, url_prefix="/_test_interview_ctrl")
    yield

def _feedback_pending(company_id):
    return f"/_test_interview_ctrl/feedback_pending/{company_id}"

def _sorted_by_date(hr_id):
    return f"/_test_interview_ctrl/sorted_by_date/{hr_id}"

def _schedule(application_id, hr_id):
    return f"/_test_interview_ctrl/schedule/{application_id}/{hr_id}"

def _reject(application_id):
    return f"/_test_interview_ctrl/reject/{application_id}"

def _scheduled_month(company_id):
    return f"/_test_interview_ctrl/stats/scheduled_month/{company_id}"

def _scheduled_week(company_id):
    return f"/_test_interview_ctrl/stats/scheduled_week/{company_id}"

def _completed(company_id):
    return f"/_test_interview_ctrl/stats/completed/{company_id}"

def _pending_feedback(company_id):
    return f"/_test_interview_ctrl/stats/pending_feedback/{company_id}"

def _cards(company_id):
    return f"/_test_interview_ctrl/cards/{company_id}"

def _evaluation(interview_id):
    return f"/_test_interview_ctrl/evaluation/{interview_id}"

def _feedback(interview_id):
    return f"/_test_interview_ctrl/feedback/{interview_id}"

def _decision(interview_id):
    return f"/_test_interview_ctrl/decision/{interview_id}"

def _applicant_summary(applicant_id):
    return f"/_test_interview_ctrl/applicant/{applicant_id}/summary"

def _applicant_list(applicant_id):
    return f"/_test_interview_ctrl/applicant/{applicant_id}/list"

def _cancel(interview_id):
    return f"/_test_interview_ctrl/{interview_id}/cancel"

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
        # ensure owner user exists
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

def create_job_id(app, hr_id, company_id, title="Engineer", created_date=None):
    with app.app_context():
        if not Company.query.get(company_id):
            raise RuntimeError(f"create_job_id: company {company_id} not found")
        if not HRProfile.query.get(hr_id):
            create_hr_profile_id(app, hr_id, company_id)
        jd = created_date or datetime.utcnow()
        job = JobPosting(hr_id=hr_id, company_id=company_id, job_title=title, created_date=jd, status="open")
        _db.session.add(job)
        _db.session.commit()
        return job.id

def create_applicant_id(app, user_id, name="Applicant", skills=None, phone=None, years_of_experience=None, current_company=None, notice_period=None):
    with app.app_context():
        if not User.query.get(user_id):
            create_user_id(app, user_id, phone=phone, name=name)
        ap = ApplicantProfile.query.get(user_id)
        if not ap:
            ap = ApplicantProfile(applicant_id=user_id, name=name, skills=skills, years_of_experience=years_of_experience, current_company=current_company, notice_period=notice_period)
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

def create_interview_id(app, application_id, interviewer_id, interview_date=None, status="scheduled", result=None, slot_start_time=None, slot_end_time=None, stage="technical"):
    with app.app_context():
        if not Application.query.get(application_id):
            raise RuntimeError(f"create_interview_id: application {application_id} not found")
        # ensure interviewer user/profile exists
        if not User.query.get(interviewer_id):
            create_user_id(app, interviewer_id)
        if not HRProfile.query.get(interviewer_id):
            create_hr_profile_id(app, interviewer_id, Application.query.get(application_id).job.company_id)
        date_obj = interview_date or date.today()
        # default slot times if not provided
        start = slot_start_time or time(10,0)
        end = slot_end_time or time(11,0)
        intr = Interview(
            application_id=application_id,
            interview_date=date_obj,
            interviewee_id=Application.query.get(application_id).applicant_id,
            interviewer_id=interviewer_id,
            mode="online",
            slot_start_time=start,
            slot_end_time=end,
            duration_minutes=int(((datetime.combine(date.today(), end) - datetime.combine(date.today(), start)).seconds) / 60),
            stage=stage,
            status=status,
            result=result
        )
        _db.session.add(intr)
        _db.session.commit()
        return intr.id

# ---------------- Tests ----------------

def test_feedback_pending_count_and_cards(client, app):
    hr_user = 11001
    cand_pending = 11002
    cand_done = 11003

    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="InterviewKpiCo")
    create_hr_profile_id(app, hr_user, comp)
    job = create_job_id(app, hr_user, comp, title="KpiJob")

    # create applicants and applications
    create_applicant_id(app, cand_pending, name="Pend", years_of_experience=2)
    a_pending = create_application_id(app, job, cand_pending, status="submitted")
    create_interview_id(app, a_pending, hr_user, interview_date=date.today(), status="feedback_pending")

    create_applicant_id(app, cand_done, name="Done", years_of_experience=3)
    a_done = create_application_id(app, job, cand_done, status="submitted")
    create_interview_id(app, a_done, hr_user, interview_date=date.today(), status="completed")

    # feedback_pending count for company
    res = client.get(_feedback_pending(comp))
    assert_response(res, expected_status=200)
    j = res.get_json()
    assert j["pending_interview_feedback_count"] == 1

    # cards endpoint returns list with both interviews (ordered by date desc)
    res2 = client.get(_cards(comp))
    assert_response(res2, expected_status=200)
    arr = res2.get_json()
    assert any(item["application_id"] == a_pending for item in arr)
    assert any(item["application_id"] == a_done for item in arr)

def test_sorted_by_date_and_schedule_and_reject_flow(client, app):
    hr_user = 11101
    cand = 11102

    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="InterviewSchedCo")
    create_hr_profile_id(app, hr_user, comp)
    job = create_job_id(app, hr_user, comp, title="SchedJob")

    create_applicant_id(app, cand, name="SchedApplicant", phone="12345")
    app_id = create_application_id(app, job, cand, status="submitted")

    # schedule interview via endpoint (POST) using ISO date/time strings
    interview_date = (date.today() + timedelta(days=2)).isoformat()   # "YYYY-MM-DD"
    interview_time = "14:30"
    payload = {"stage": "technical", "interview_date": interview_date, "interview_time": interview_time, "duration": 45}

    r = client.post(_schedule(app_id, hr_user), json=payload)
    assert_response(r, expected_status=201, expected_message="interview scheduled successfully")
    j = r.get_json()
    intr_id = j.get("interview_id")
    assert intr_id is not None

    # scheduled_by_date for HR should return the interview
    res_sorted = client.get(_sorted_by_date(hr_user))
    assert_response(res_sorted, expected_status=200)
    response_data = res_sorted.get_json()
    arr = response_data.get("interviews", []) if isinstance(response_data, dict) else response_data
    assert any(item["id"] == intr_id for item in arr)

    # Now reject candidate via endpoint (POST) — this should set application.status='rejected' and cancel pending interviews
    rrej = client.post(_reject(app_id))
    assert_response(rrej, expected_status=200, expected_message="candidate rejected")
    with app.app_context():
        a = Application.query.get(app_id)
        assert a.status == "rejected"
        # interview status should be updated to 'cancelled'
        intr = Interview.query.get(intr_id)
        assert intr.status == "cancelled"

def test_stats_scheduled_month_week_completed_pending_feedback(client, app):
    hr_user = 11201
    cand = 11202

    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="InterviewStatsCo")
    create_hr_profile_id(app, hr_user, comp)
    job = create_job_id(app, hr_user, comp, title="StatsJob")

    # create interviews: one scheduled this month, one scheduled this week, one completed, one feedback_pending
    create_applicant_id(app, cand, name="StatCand")
    app1 = create_application_id(app, job, cand)
    # scheduled today
    create_interview_id(app, app1, hr_user, interview_date=date.today(), status="scheduled")
    # scheduled earlier in month but not this week (ensure it's still in current month)
    app2_user = cand + 1
    create_user_id(app, app2_user)
    create_applicant_id(app, app2_user, name="MonthCand")
    app2 = create_application_id(app, job, app2_user)
    # Use a date that's definitely in the current month (e.g., first day of month or a few days ago)
    today = date.today()
    earlier_this_month = date(today.year, today.month, max(1, today.day - 5))  # 5 days ago or first of month
    create_interview_id(app, app2, hr_user, interview_date=earlier_this_month, status="scheduled")
    # completed interview
    app3_user = cand + 2
    create_user_id(app, app3_user)
    create_applicant_id(app, app3_user, name="CompCand")
    app3 = create_application_id(app, job, app3_user)
    create_interview_id(app, app3, hr_user, interview_date=date.today(), status="completed")
    # feedback pending
    app4_user = cand + 3
    create_user_id(app, app4_user)
    create_applicant_id(app, app4_user, name="FeedCand")
    app4 = create_application_id(app, job, app4_user)
    create_interview_id(app, app4, hr_user, interview_date=date.today(), status="feedback_pending")

    # scheduled_this_month
    r_month = client.get(_scheduled_month(comp))
    assert_response(r_month, expected_status=200)
    jm = r_month.get_json()
    # at least 2 scheduled interviews in the month (app1 and app2)
    assert jm.get("scheduled_this_month", 0) >= 2

    # scheduled_this_week
    r_week = client.get(_scheduled_week(comp))
    assert_response(r_week, expected_status=200)
    jw = r_week.get_json()
    # at least one scheduled this week (app1)
    assert jw.get("scheduled_this_week", 0) >= 1

    # completed_interviews
    r_comp = client.get(_completed(comp))
    assert_response(r_comp, expected_status=200)
    jc = r_comp.get_json()
    assert jc.get("completed_interviews", 0) >= 1

    # pending_feedback count endpoint
    r_pf = client.get(_pending_feedback(comp))
    assert_response(r_pf, expected_status=200)
    jpf = r_pf.get_json()
    assert jpf.get("pending_feedback", 0) >= 1

def test_evaluation_and_decision_and_applicant_endpoints(client, app):
    hr_user = 11301
    cand = 11302

    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="InterviewEvalCo")
    create_hr_profile_id(app, hr_user, comp)
    job = create_job_id(app, hr_user, comp, title="EvalJob")

    create_user_id(app, cand, email=f"cand{cand}@test.local")
    create_applicant_id(app, cand, name="EvalCandidate", phone="99999", years_of_experience=5, current_company="X")
    application_id = create_application_id(app, job, cand, status="submitted")

    # schedule and then complete interview
    intr_id = create_interview_id(app, application_id, hr_user, interview_date=date.today(), status="completed", result="approved")

    # evaluation endpoint
    reval = client.get(_evaluation(intr_id))
    assert_response(reval, expected_status=200)
    je = reval.get_json()
    assert je["interview"]["interview_id"] == intr_id
    assert "candidate" in je and "interview" in je

    # decision endpoint: change to rejected
    rdec = client.put(_decision(intr_id), json={"decision": "rejected"})
    assert_response(rdec, expected_status=200)
    jd = rdec.get_json()
    assert jd.get("interview_result") == "rejected"
    with app.app_context():
        inter = Interview.query.get(intr_id)
        assert inter.result == "rejected"
        assert inter.application.status == "rejected"

    # applicant summary & list endpoints (no exceptions)
    rsumm = client.get(_applicant_summary(cand))
    assert_response(rsumm, expected_status=200)
    rlist = client.get(_applicant_list(cand))
    assert_response(rlist, expected_status=200)

def test_submit_interview_feedback(client, app):
    """Test POST /interview/feedback/<interview_id> endpoint"""
    hr_user = 11501
    cand = 11502

    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="FeedbackCo")
    create_hr_profile_id(app, hr_user, comp)
    job = create_job_id(app, hr_user, comp, title="FeedbackJob")

    create_user_id(app, cand, email=f"cand{cand}@test.local")
    create_applicant_id(app, cand, name="FeedbackCandidate")
    application_id = create_application_id(app, job, cand, status="submitted")

    # Create interview with feedback_pending status
    intr_id = create_interview_id(app, application_id, hr_user, interview_date=date.today(), status="feedback_pending")

    # Submit feedback
    rfeedback = client.post(_feedback(intr_id), json={"notes": "Good candidate, strong technical skills"})
    assert_response(rfeedback, expected_status=200)
    jf = rfeedback.get_json()
    assert jf["message"] == "Feedback submitted successfully"
    assert jf["interview_status"] == "completed"

    # Verify interview status was updated
    with app.app_context():
        inter = Interview.query.get(intr_id)
        assert inter.status == "completed"

def test_cancel_interview_endpoint(client, app):
    hr_user = 11401
    cand = 11402

    create_user_id(app, hr_user)
    comp = create_company_id(app, hr_user, company_name="InterviewCancelCo")
    create_hr_profile_id(app, hr_user, comp)
    job = create_job_id(app, hr_user, comp, title="CancelJob")

    create_applicant_id(app, cand, name="CancelCandidate")
    application_id = create_application_id(app, job, cand)
    intr_id = create_interview_id(app, application_id, hr_user, interview_date=date.today(), status="scheduled")

    r = client.put(_cancel(intr_id))
    assert_response(r, expected_status=200, expected_message="interview cancelled")
    with app.app_context():
        inter = Interview.query.get(intr_id)
        assert inter.status == "cancelled"
