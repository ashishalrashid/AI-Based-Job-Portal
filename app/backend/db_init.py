# create_big_test_db.py

from main import app
from application.data.database import db
from application.data.models import (
    Role, User, Company, ApplicantProfile, HRProfile, JobPosting,
    Application, Interview, OfferLetter, Onboarding
)
from werkzeug.security import generate_password_hash
import datetime as dt
import random
import string


# ---------------------------------------------
# Helpers
# ---------------------------------------------

def pwd_hash():
    return generate_password_hash("password123")

def randstr(n=8):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(n))


def create_user(name, email, role_name):
    user = User(
        name=name,
        email=email,
        password_hashed=pwd_hash(),
        role=role_name
    )
    db.session.add(user)
    db.session.commit()

    # Assign actual Role model (many-to-many)
    role = Role.query.filter_by(name=role_name).first()
    if role:
        user.add_role(role)
        db.session.commit()
    return user


# ---------------------------------------------
# Main Seeding Logic
# ---------------------------------------------

with app.app_context():

    print("🗑 Dropping & recreating database…")
    db.drop_all()
    db.create_all()

    print("🔧 Creating roles…")
    for r in ["admin", "hr", "applicant", "company"]:
        db.session.add(Role(name=r))
    db.session.commit()

    print("👑 Creating SUPER ADMIN…")
    super_admin = create_user("Super Admin", "admin@system.com", "admin")

    # ------------------------------
    # Create Companies
    # ------------------------------

    print("🏢 Creating companies + HRs…")

    companies = []
    hrs = []

    for i in range(5):
        company_name = f"TechCorp{i+1} Pvt Ltd"

        company_owner = create_user(f"Owner{i+1}", f"owner{i+1}@test.com", "company")

        company = Company(
            user_id=company_owner.id,
            company_name=company_name,
            company_email=f"contact{i+1}@techcorp.com",
            location=random.choice(["Bengaluru", "Mumbai", "Chennai", "Delhi", "Pune"]),
            technology="Python, Flask, React",
            company_size=random.choice(["50-100", "100-200", "200-500", "500+"]),
            description="Sample seed company"
        )
        db.session.add(company)
        db.session.commit()

        # HR for the company
        hr_user = create_user(f"HR_{i+1}", f"hr{i+1}@test.com", "hr")

        hrp = HRProfile(
            hr_id=hr_user.id,
            company_id=company.id,
            first_name=f"HR{i+1}",
            last_name="Manager",
            username=f"hr_user_{i+1}",
            password="password123",
            gender="Other",
            contact_email=f"hr{i+1}@test.com",
            staff_id=f"STAFF{i+1}"
        )
        db.session.add(hrp)
        db.session.commit()

        companies.append(company)
        hrs.append(hr_user)

    # ------------------------------
    # Create Applicants (20)
    # ------------------------------

    print("🧑‍💼 Creating applicant users + profiles…")

    applicants = []
    for i in range(20):
        user = create_user(
            f"Applicant{i+1}",
            f"applicant{i+1}@test.com",
            "applicant"
        )

        ap = ApplicantProfile(
            applicant_id=user.id,
            name=f"Applicant{i+1}",
            highest_qualification=random.choice(["B.Tech", "M.Tech", "B.Sc", "MCA"]),
            institution_name="ABC University",
            graduation_year=random.randint(2018, 2024),
            skills=random.choice([
                "Python, SQL, Flask",
                "React, Node.js, JS",
                "Java, Spring Boot",
                "C++, DS Algo",
                "Machine Learning, Python"
            ]),
            years_of_experience=random.randint(0, 4),
            preferred_location=random.choice(["Remote", "Bengaluru", "Hyderabad"]),
        )
        db.session.add(ap)
        db.session.commit()
        applicants.append(user)

    # ------------------------------
    # Create Job Postings (50+)
    # ------------------------------

    print("💼 Creating job postings…")

    jobs = []
    for i in range(50):
        comp = random.choice(companies)
        hr_user = HRProfile.query.filter_by(company_id=comp.id).first()

        job = JobPosting(
            hr_id=hr_user.hr_id,
            company_id=comp.id,
            job_title=random.choice([
                "Software Engineer",
                "Data Scientist",
                "Backend Developer",
                "Frontend Engineer",
                "ML Engineer",
                "DevOps Engineer"
            ]),
            level=random.choice(["Junior", "Mid", "Senior"]),
            basic_salary=random.randint(6, 25) * 100000,
            required_skills="Python, SQL, Git",
            job_description="Auto-generated seed job",
            required_experience="0-5 years",
            created_date=dt.datetime.utcnow(),
            status="open"
        )

        db.session.add(job)
        db.session.commit()
        jobs.append(job)

    # ------------------------------
    # Create Applications
    # ------------------------------

    print("📝 Creating job applications…")
    applications = []

    for applicant in applicants:
        app_profile = ApplicantProfile.query.get(applicant.id)

        for _ in range(random.randint(2, 4)):  # each applies to 2–4 jobs
            job = random.choice(jobs)
            application = Application(
                job_id=job.id,
                applicant_id=app_profile.applicant_id,
                applied_date=dt.datetime.utcnow(),
                status=random.choice(["submitted", "in review", "shortlisted"])
            )
            db.session.add(application)
            db.session.commit()
            applications.append(application)

    # ------------------------------
    # Add Interviews + Offer Letters
    # ------------------------------

    print("🎤 Scheduling interviews + offers…")

    for application in random.sample(applications, 20):  # 20 interviews
        job = JobPosting.query.get(application.job_id)
        hr = HRProfile.query.filter_by(company_id=job.company_id).first()

        # Randomly make some interviews completed and selected for offer letter testing
        interview_status = random.choice(["scheduled", "completed"])
        interview_result = "selected" if interview_status == "completed" else None

        interview = Interview(
            application_id=application.id,
            interview_date=dt.date.today() + dt.timedelta(days=random.randint(1, 10)),
            interviewer_id=hr.hr_id,
            mode="Online",
            stage="Round 1",
            slot_start_time=dt.time(10),
            slot_end_time=dt.time(11),
            status=interview_status,
            result=interview_result
        )
        db.session.add(interview)

    db.session.commit()

    # Offer letters for some
    for application in random.sample(applications, 10):
        job = JobPosting.query.get(application.job_id)
        offer = OfferLetter(
            application_id=application.id,
            candidate_id=application.applicant_id,
            company_id=job.company_id,
            joining_date=dt.datetime.utcnow() + dt.timedelta(days=30),
            ctc=random.randint(8, 20) * 100000,
            status="issued"
        )
        db.session.add(offer)

        onboarding = Onboarding(
            application_id=application.id,
            contact_email="hr@company.com",
            status="pending",
            joining_date=dt.date.today() + dt.timedelta(days=30)
        )
        db.session.add(onboarding)

    db.session.commit()

    print("\n🎉 DATABASE SEEDED SUCCESSFULLY!")
    print("="*80)
    print("🔥 LOGIN CREDENTIALS (ALL USERS)")
    print("="*80)
    print("PASSWORD FOR EVERY USER = password123\n")

    print("Admin:")
    print("  admin@system.com / password123\n")

    print("HR Users:")
    for i in range(5):
        print(f"  hr{i+1}@test.com / password123")

    print("\nCompany Owners:")
    for i in range(5):
        print(f"  owner{i+1}@test.com / password123")

    print("\nApplicants:")
    for i in range(20):
        print(f"  applicant{i+1}@test.com / password123")

    print("\n🎯 SEED COMPLETE. You now have:")
    print(" - 40 total users")
    print(" - 5 companies")
    print(" - 5 HR profiles")
    print(" - 20 applicant profiles")
    print(" - 50+ job postings")
    print(" - 60–80 job applications")
    print(" - 20 interviews")
    print(" - 10 offer letters + onboarding")
    print("="*80)