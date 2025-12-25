#!/usr/bin/env python3
"""
Reset and Seed Database Script
================================
This script will:
1. Backup the current database (if it exists)
2. Drop all tables
3. Create fresh tables with proper schema
4. Seed with test data including:
   - Interview records with proper fields
   - Video and regular interview modes
   - Company, HR, Applicant data
   - Applications and Job Postings

Usage:
    python reset_and_seed_db.py

Requirements:
    - Flask app must be properly configured
    - All models must be imported
"""

import os
import sys
import shutil
from datetime import datetime, date, timedelta
import random
import string

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from application.data.database import db
from application.data.models import (
    Role, User, Company, ApplicantProfile, HRProfile, JobPosting,
    Application, Interview, OfferLetter, Onboarding
)
from werkzeug.security import generate_password_hash


# ========================================
# Helpers
# ========================================

def pwd_hash():
    """Generate password hash"""
    return generate_password_hash("password123")


def randstr(n=8):
    """Generate random string"""
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(n))


def create_user(name, email, role_name):
    """Create a user with a specific role"""
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


# ========================================
# Main Database Reset & Seed
# ========================================

def main():
    with app.app_context():
        db_path = "db_dir/recruitement.db"
        
        print("\n" + "="*80)
        print("🔧 DATABASE RESET & SEED UTILITY")
        print("="*80)
        
        # Backup existing database
        if os.path.exists(db_path):
            backup_name = f"recruitement.db.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = os.path.join("db_dir", backup_name)
            print(f"\n📦 Backing up existing database to: {backup_path}")
            shutil.copy2(db_path, backup_path)
            print("✅ Backup created")
        
        # Drop and recreate tables
        print("\n🗑 Dropping and recreating all tables...")
        db.drop_all()
        db.create_all()
        print("✅ Database schema created")
        
        # Create roles
        print("\n🔐 Creating roles...")
        for r in ["admin", "hr", "applicant", "company"]:
            db.session.add(Role(name=r))
        db.session.commit()
        print("✅ Roles created: admin, hr, applicant, company")
        
        # Create super admin
        print("\n👑 Creating super admin user...")
        super_admin = create_user("Super Admin", "admin@system.com", "admin")
        print(f"✅ Super admin created: admin@system.com")
        
        # Create companies and HR profiles
        print("\n🏢 Creating companies and HR profiles...")
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
            
            # Create HR for company
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
        
        print(f"✅ Created 5 companies with HR profiles")
        
        # Create applicants
        print("\n🧑‍💼 Creating applicant users and profiles...")
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
        
        print(f"✅ Created 20 applicant profiles")
        
        # Create job postings
        print("\n💼 Creating job postings...")
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
                created_date=datetime.utcnow(),
                status="open"
            )
            
            db.session.add(job)
            db.session.commit()
            jobs.append(job)
        
        print(f"✅ Created 50 job postings")
        
        # Create applications
        print("\n📝 Creating job applications...")
        applications = []
        
        for applicant in applicants:
            app_profile = ApplicantProfile.query.get(applicant.id)
            
            for _ in range(random.randint(2, 4)):
                job = random.choice(jobs)
                application = Application(
                    job_id=job.id,
                    applicant_id=app_profile.applicant_id,
                    applied_date=datetime.utcnow(),
                    status=random.choice(["submitted", "in review", "shortlisted"])
                )
                db.session.add(application)
                db.session.commit()
                applications.append(application)
        
        print(f"✅ Created {len(applications)} job applications")
        
        # Create interviews with proper fields
        print("\n🎤 Scheduling interviews...")
        
        interview_count = 0
        video_interview_count = 0
        
        for application in random.sample(applications, min(20, len(applications))):
            job = JobPosting.query.get(application.job_id)
            hr = HRProfile.query.filter_by(company_id=job.company_id).first()
            
            # Mix of regular and video interviews
            interview_mode = random.choice(["online", "video", "online"])  # 67% online, 33% video
            interview_stage = random.choice(["Screening", "Round 1", "Round 2", "Final"])
            
            interview = Interview(
                application_id=application.id,
                interview_date=date.today() + timedelta(days=random.randint(1, 10)),
                interviewee_id=application.applicant_id,
                interviewer_id=hr.hr_id,
                mode=interview_mode,
                stage=interview_stage,
                slot_start_time=datetime.strptime(f"10:{random.randint(0, 59):02d}", "%H:%M").time(),
                slot_end_time=datetime.strptime(f"11:{random.randint(0, 59):02d}", "%H:%M").time(),
                duration_minutes=60,
                status="scheduled"
            )
            db.session.add(interview)
            interview_count += 1
            
            if interview_mode == "video":
                video_interview_count += 1
        
        db.session.commit()
        print(f"✅ Created {interview_count} interviews ({video_interview_count} video, {interview_count - video_interview_count} regular)")
        
        # Create offer letters
        print("\n📜 Creating offer letters and onboarding records...")
        
        for application in random.sample(applications, min(10, len(applications))):
            job = JobPosting.query.get(application.job_id)
            offer = OfferLetter(
                application_id=application.id,
                candidate_id=application.applicant_id,
                company_id=job.company_id,
                joining_date=datetime.utcnow() + timedelta(days=30),
                ctc=random.randint(8, 20) * 100000,
                status="issued"
            )
            db.session.add(offer)
            
            onboarding = Onboarding(
                application_id=application.id,
                contact_email="hr@company.com",
                status="pending",
                joining_date=date.today() + timedelta(days=30)
            )
            db.session.add(onboarding)
        
        db.session.commit()
        print(f"✅ Created offer letters and onboarding records")
        
        # Print summary
        print("\n" + "="*80)
        print("🎉 DATABASE RESET & SEEDING COMPLETE!")
        print("="*80)
        
        print("\n📋 DATABASE SUMMARY:")
        print(f"  ✅ Total Users: 40")
        print(f"  ✅ Companies: 5")
        print(f"  ✅ HR Profiles: 5")
        print(f"  ✅ Applicant Profiles: 20")
        print(f"  ✅ Job Postings: 50+")
        print(f"  ✅ Job Applications: {len(applications)}")
        print(f"  ✅ Interviews: {interview_count} total")
        print(f"     - Video Interviews: {video_interview_count}")
        print(f"     - Regular Interviews: {interview_count - video_interview_count}")
        print(f"  ✅ Offer Letters: 10")
        print(f"  ✅ Onboarding Records: 10")
        
        print("\n🔐 LOGIN CREDENTIALS (password123 for all):")
        print("  Admin: admin@system.com")
        print("  HR Users: hr1@test.com, hr2@test.com, ... hr5@test.com")
        print("  Company Owners: owner1@test.com, owner2@test.com, ... owner5@test.com")
        print("  Applicants: applicant1@test.com, applicant2@test.com, ... applicant20@test.com")
        
        print("\n" + "="*80)
        print("✨ You can now view interviews at: /interviews/cards/<company_id>")
        print("✨ You can now view video interviews at: /interview/video-interviews/<company_id>")
        print("="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
