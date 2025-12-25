#!/usr/bin/env python3
"""
Show which users have interviews scheduled
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from application.data.database import db
from application.data.models import User, Interview, Application, ApplicantProfile, HRProfile

def main():
    with app.app_context():
        print("\n" + "="*80)
        print("📋 USERS WITH SCHEDULED INTERVIEWS")
        print("="*80 + "\n")
        
        # Get all scheduled interviews
        interviews = Interview.query.filter_by(status='scheduled').all()
        
        if not interviews:
            print("❌ No scheduled interviews found in database!")
            print("\nRun: python reset_and_seed_db.py")
            return
        
        print(f"Found {len(interviews)} scheduled interviews\n")
        
        # Group by applicant
        applicant_interviews = {}
        hr_interviews = {}
        
        for interview in interviews:
            # Applicant side
            if interview.interviewee_id not in applicant_interviews:
                applicant_interviews[interview.interviewee_id] = []
            applicant_interviews[interview.interviewee_id].append(interview)
            
            # HR side
            if interview.interviewer_id not in hr_interviews:
                hr_interviews[interview.interviewer_id] = []
            hr_interviews[interview.interviewer_id].append(interview)
        
        # Show applicants with interviews
        print("👥 APPLICANTS WITH INTERVIEWS:")
        print("-" * 80)
        for applicant_id, interviews in sorted(applicant_interviews.items()):
            user = User.query.get(applicant_id)
            if user:
                print(f"\n✅ {user.name} ({user.email})")
                print(f"   Password: password123")
                print(f"   Interviews: {len(interviews)} scheduled")
                for interview in interviews[:3]:  # Show first 3
                    print(f"     • {interview.stage} - {interview.interview_date} - Mode: {interview.mode}")
                if len(interviews) > 3:
                    print(f"     ... and {len(interviews) - 3} more")
        
        # Show HR users with interviews
        print("\n\n💼 HR USERS WITH INTERVIEWS TO CONDUCT:")
        print("-" * 80)
        for hr_id, interviews in sorted(hr_interviews.items()):
            user = User.query.get(hr_id)
            if user:
                hr_profile = HRProfile.query.filter_by(hr_id=hr_id).first()
                print(f"\n✅ {user.name} ({user.email})")
                print(f"   Password: password123")
                if hr_profile:
                    print(f"   Company ID: {hr_profile.company_id}")
                print(f"   Interviews: {len(interviews)} scheduled")
                video_count = len([i for i in interviews if i.mode == 'video'])
                regular_count = len(interviews) - video_count
                print(f"     • Video: {video_count}, Regular: {regular_count}")
        
        print("\n" + "="*80)
        print("💡 TIP: Login with any email above and password 'password123'")
        print("="*80 + "\n")

if __name__ == "__main__":
    main()
