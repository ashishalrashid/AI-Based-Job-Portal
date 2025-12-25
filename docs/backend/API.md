# Backend documentation

## Class Diagram
[Class-Diagram](https://drive.google.com/file/d/1PY9zYjBwsHSZ9kHZm41uIoUKGvXIuc-C/view)

# ER diagram
[ER-Diagram](https://drive.google.com/file/d/1uaieWI7njWXFMnriHEG8-WRkvzKjNwpw/view)

### To add: frontend
- Add phone number field to both applicant and company login
- Decide whether we need "Candidates" and "Onboardings" options on HR dashboard

### API routes
server: `http://127.0.0.1:8085`

#### Auth

1) register: `/auth/register`
- method: POST
- args: name, email, password, phone
- desc: registers a user according to his/her role
- note: @company.com -> role is set to **admin**, @hr.com -> role is set to **hr**, anything else -> role is set to **applicant**
- example:
```
{
    "name": "company",
    "email": "hr@company.com",
    "password": "company345",
    "phone": "1234567890"
}
```

2) login: `/auth/login`
- method: POST
- args: email, password
- desc: logs in a user
- example:
```
{
    "email": "srupat@gmail.com",
    "password": "srupat1234"
}
```
- whenever a company (admin) logs in, we return (company_id, message, role). This will be useful for getting HRs according to company. So store the company_id at the frontend.
- whenever a hr logs in, we return (hr_id, message, role). store at frontend.
- whenever an applicant logs in, we return (applicant_id, message, role). store appropriately at frontend.


3) logout: `/auth/logout`
- method: POST
- desc: unset jwt token
- args: None

#### HR APIs
1) create new hr: `/hr`
- method: POST
- desc: create a new hr by giving all hr info in payload
- example body:
```
{
    "company_id": "1",
    "first_name": "srujan",
    "last_name": "pat",
    "email": "srupat@gmail.com",
    "phone": "1234567890",
    "gender": "Male",
    "username": "srupat",
    "password": "srupat1234",
    "staff_id": "E-AUTO-1762737117527"
}
```
- constraints: make sure company_id exists, keep company_id as the logged in company

2) get single hr: `/hr/<hr_id>`
- method: GET
- desc: get hr by id
- constraints: ensure hr_id exists

3) get all HRs: `/hr`
- method: GET
- desc: get all HRs

4) update HR: `/hr/<hr_id>`
- method: PUT
- desc: update HR info
- constraints: ensure hr_id exists
- example
```
{
    "company_id": "1",
    "first_name": "srujan",
    "last_name": "pat",
    "email": "srupat@gmail.com",
    "phone": "1234567890",
    "gender": "Male",
    "username": "srupat",
    "password": "srupat1234",
    "staff_id": "E-AUTO-1762737117527"
}
```

5) delete hr by id: `/hr/<hr_id>`
- method: DELETE
- desc: delete hr by id
- constraints: ensure HR id exists

### Job APIs
1) create new job (JD - gdrive): `/job`
- method: POST
- desc: create a new job by giving job info in payload
- example body:
```
{
    "hr_id": 2,
    "company_id": 1,
    "job_title": "SRE",
    "level": "II",
    "basic_salary": 5000000,
    "required_skills": "scripting",
    "additional_skills": "willingness to learn",
    "employment_type": "fulltime",
    "job_description_ai": "devops",
    "job_description": "devops",
    "key_responsibilities": "devops",
    "required_experience": "2 yoe",
    "required_education": "bachelors",
    "location": "Pune",
    "notice_period": "3 months",
    "attachment_type": "gdrive",
    "attachment_url": "https://drive.google.com/file/d/1q4ItwGSPBf59hZoWX5tB4ly3lBgfD0Tb/view?usp=drive_link"
}
```
- constraints: upload a gdrive link

2) create new job (JD - upload file): `/job`
- method: POST
- desc: create a new job by giving job info in payload
- example body:
```
{
    "hr_id": 2,
    "company_id": 1,
    "job_title": "SRE",
    "level": "II",
    "basic_salary": 5000000,
    "required_skills": "scripting",
    "additional_skills": "willingness to learn",
    "employment_type": "fulltime",
    "job_description_ai": "devops",
    "job_description": "devops",
    "key_responsibilities": "devops",
    "required_experience": "2 yoe",
    "required_education": "bachelors",
    "location": "Pune",
    "notice_period": "3 months",
    "attachment_type": "file",
    "attachment_url": ""
}
```
- constraints: attachment_url field is of file type, upload a file for the JD. content type should be `multipart/form-data`

3) get single job: `/job/<job_id>`
- method: GET
- desc: get job by id
- constraints: ensure job_id exists

4) get all HRs: `/job`
- method: GET
- desc: get all jobs

5) update HR: `/job/<job_id>`
- method: PUT
- desc: update HR info
- constraints: ensure job_id exists
- example
```
{
    "hr_id": 2,
    "company_id": 1,
    "job_title": "SRE",
    "level": "III"
}
```

6) delete job by id: `/job/<job_id>`
- method: DELETE
- desc: delete job by id
- constraints: ensure job id exists

### Applicant APIs
1) create new applicant: `/applicant`
- method: POST
- desc: create a new applicant if applicant does not exist, else upserts values in db
- example body:
```
applicant_id:3
name:john
address:pune
highest_qualification:bachelors
institution_name:iitm
graduation_year:2026
skills:flask
preferred_location:pune
years_of_experience:1
current_job_title:AI intern
linkedin_url:https://linkedin.com/srupat
github_url:https://github.com/srupat
portfolio_url:https://srupat.me
resume: <upload_file>
cover_letter: <upload_file>
```
- constraints: content-type should be `multipart/form-data`

2) get single applicant: `/applicant/<applicant_id>`
- method: GET
- desc: get applicant by id
- constraints: ensure applicant_id exists

3) get all applicants: `/applicant`
- method: GET
- desc: get all applicants

4) update applicant: `/applicant/<applicant_id>`
- method: PUT
- desc: update applicant info. Supports multipart/form-data for file uploads. Note: When updating profile, work experiences, education, and certifications should be managed separately using their respective endpoints (DELETE existing, then POST new ones).
- constraints: ensure applicant_id exists
- example (multipart/form-data):
```
applicant_id:3
name:srujan
address:pune
highest_qualification:bachelors
institution_name:iitm
graduation_year:2026
skills:flask
preferred_location:pune
years_of_experience:1
current_job_title:AI intern
linkedin_url:https://linkedin.com/srupat
github_url:https://github.com/srupat
portfolio_url:https://srupat.me
resume: <upload_file>
cover_letter: <upload_file>
profile_photo: <upload_file> (optional)
```
- note: To update work experiences, education, or certifications, first DELETE all existing records using the respective DELETE endpoints, then POST new ones. This prevents duplicate entries.

5) delete applicant by id: `/applicant/<applicant_id>`
- method: DELETE
- desc: delete applicant by id
- constraints: ensure applicant id exists

### Application APIs
1) create new application: `/application`
- method: POST
- desc: create a new application by giving job_id and applicant_id
- example body:
```
{
    "job_id": 4,
    "applicant_id": 2,
    "status": "under_review",
    "resume_score": 91,
    "ai_feedback": "good"
}
```
- constraints: make sure job_id and applicant_id exists

2) get single application: `/application/<application_id>`
- method: GET
- desc: get application by id
- constraints: ensure application_id exists

3) get all applications: `/application`
- method: GET
- desc: get all applications

4) update application: `/application/<application_id>`
- method: PUT
- desc: update application info
- constraints: make sure job_id and applicant_id exists
- example
```
{
    "job_id": 4,
    "applicant_id": 2,
    "status": "under_review",
    "resume_score": 91,
    "ai_feedback": "good"
}
```

5) delete application by id: `/application/<application_id>`
- method: DELETE
- desc: delete application by id
- constraints: ensure application id exists

### Offer Letter APIs
1) create new offer letter: `/offer_letter`
- method: POST
- desc: create a new offer letter by giving application_id, candidate_id, company_id, joining_date, ctc
- example body: 
```
{
    "application_id": 1,
    "candidate_id": 2,
    "company_id": 1,
    "joining_date": "2025-12-01",
    "ctc": 6000000,
    "status": "issued"
}
```
- constraints: make sure application_id, candidate_id, company_id exists

2) get single offer letter: `/offer_letter/<offer_letter_id>`
- method: GET
- desc: get offer letter by id
- constraints: ensure offer_letter_id exists

3) get all offer letters: `/offer_letter`
- method: GET
- desc: get all offer letters

4) update offer letter: `/offer_letter/<offer_letter_id>`
- method: PUT
- desc: update offer letter info
- constraints: make sure application_id, candidate_id, company_id exists
- example
```
{
    "application_id": 1,
    "candidate_id": 2,
    "company_id": 1,
    "joining_date": "2025-12-01",
    "ctc": 6000000,
    "status": "issued"
}
```

5) delete offer letter by id: `/offer_letter/<offer_letter_id>`
- method: DELETE
- desc: delete offer letter by id
- constraints: ensure offer letter id exists

### Interview APIs
1) create new interview: `/interview`
- method: POST
- desc: create a new interview by giving application_id, interview_date, mode, slot_start_time, slot_end_time, interviewer_id, interviewee_id, status, result
- example body:
```
{
    "application_id": 1,
    "interview_date": "2025-10-15",
    "mode": "online",
    "slot_start_time": "10:00:00",
    "slot_end_time": "11:00:00",
    "interviewer_id": 2,
    "interviewee_id": 3,
    "interview_recording_url": "https://recordings.com/interview123",
    "status": "scheduled",
    "result": "pending"
}
```
- constraints: make sure application_id, interviewer_id, interviewee_id exists

2) get single interview: `/interview/<interview_id>`
- method: GET
- desc: get interview by id
- constraints: ensure interview_id exists

3) get all interviews: `/interview`
- method: GET
- desc: get all interviews

4) update interview: `/interview/<interview_id>`
- method: PUT
- desc: update interview info
- constraints: make sure application_id, interviewer_id, interviewee_id exists
- example
```
{
    "application_id": 1,
    "interview_date": "2025-10-15",
    "mode": "online",
    "slot_start_time": "10:00:00",
    "slot_end_time": "11:00:00",
    "interviewer_id": 2,
    "interviewee_id": 3,
    "interview_recording_url": "https://recordings.com/interview123",
    "status": "scheduled",
    "result": "pending"
}
```

5) delete interview by id: `/interview/<interview_id>`
- method: DELETE
- desc: delete interview by id
- constraints: ensure interview id exists

### Onboarding APIs
1) create new onboarding: `/onboarding`
- method: POST
- desc: create a new onboarding by giving candidate_id, offer_letter_id, contact_email, contact_phone, offer_accepted, joining_date
- example body:
```
{
    "candidate_id": 2,
    "offer_letter_id": 1,
    "contact_email": "example@gmail.com",
    "contact_phone": "1234567890",
    "offer_accepted": true,
    "joining_date": "2025-12-01"
}
```
- constraints: make sure candidate_id, offer_letter_id exists

2) get single onboarding: `/onboarding/<onboarding_id>`
- method: GET
- desc: get onboarding by id
- constraints: ensure onboarding_id exists

3) get all onboardings: `/onboarding`
- method: GET
- desc: get all onboardings

4) update onboarding: `/onboarding/<onboarding_id>`
- method: PUT
- desc: update onboarding info
- constraints: make sure candidate_id, offer_letter_id exists
- example
```
{
    "candidate_id": 2,
    "offer_letter_id": 1,
    "contact_email": "example@gmail.com",
    "contact_phone": "1234567890",
    "offer_accepted": true,
    "joining_date": "2025-12-01"
}
```

5) delete onboarding by id: `/onboarding/<onboarding_id>`
- method: DELETE
- desc: delete onboarding by id
- constraints: ensure onboarding id exists

# Additional APIs
## HR side
### HR Dashboard APIs
#### Get offer acceptance rate
- endpoint: `/offer/acceptance_rate/<company_id>`
- method: GET
- desc: get offer acceptance rate for a company
- constraints: ensure company_id exists
- example response:
```
{
    "acceptance_rate": 75.0
}
```

#### Get count of 'pending' onboardings
- endpoint: `/onboarding/pending_count/<company_id>`
- method: GET
- desc: get count of 'pending' onboardings for a company
- constraints: ensure company_id exists
- example response:
```
{
    "pending_onboardings_count": 5
}
```

#### Get count of pending interview feedbacks according to company
- endpoint: `/interview/feedback_pending/<company_id>`
- method: GET
- desc: get count of pending interview feedbacks for a company (interviews with status `feedback_pending`)
- constraints: ensure company_id exists
- example response:
```
{
    "pending_interview_feedback_count": 8
}
```
- note: This is the correct endpoint for HR dashboard. The frontend should use `pending_interview_feedback_count` from the response.

#### Get all scheduled interviews sorted by date (latest first) for a particular hr
- endpoint: `/interview/sorted_by_date/<hr_id>`
- method: GET
- desc: get all scheduled interviews sorted by date (latest first) for a particular hr
- constraints: ensure hr_id exists
- example response:
```
{
    "interviews": [
        {
            "interview_id": 5,
            "application_id": 10,
            "interview_date": "2025-10-20",
            "mode": "online",
            "slot_start_time": "14:00:00",
            "slot_end_time": "15:00:00",
            "interviewer_id": 2,
            "interviewee_id": 3,
            "status": "scheduled",
            "result": "pending"
        },
        ...
    ]
}
```

#### Get all job statistics for a particular company
- endpoint: `/job/stats/<company_id>`
- method: GET
- desc: get all job statistics for a particular company
- constraints: ensure company_id exists
- example response:
```
[
    {
        "applications_count": 2,
        "days_ago_posted": 3,
        "feedback_pending_count": 3,
        "interviewed_count": 4,
        "job_id": 4,
        "job_title": "SRE",
        "num_positions": 5,
        "offered_count": 2,
        "positions_left": 3,
        "rejected_count": 0
    },
    {
        "applications_count": 1,
        "days_ago_posted": 0,
        "feedback_pending_count": 0,
        "interviewed_count": 1,
        "job_id": 5,
        "job_title": "Software Engineer",
        "num_positions": 2,
        "offered_count": 1,
        "positions_left": 1,
        "rejected_count": 0
    }
]
```

### Create Job page APIs
#### create a new job
- refer to the Job CRUD endpoint above to create a new job either using gdrive link or file upload for job description

### All candidates page APIs
#### get all candidates for a particular company
- endpoint: `/applications/<company_id>/candidates`
- method: GET
- desc: get all candidates who have applied to jobs of a particular company
- constraints: ensure company_id exists
- example:
```
{
    "candidates": [
        {
            "action_url": "/candidate/2",
            "ai_match_score": 91,
            "first_name": "srupat",
            "gender": "Male",
            "last_name": "",
            "role": "SRE",
            "sn": 1
        },
        {
            "action_url": "/candidate/3",
            "ai_match_score": 78,
            "first_name": "Rohan",
            "gender": "Male",
            "last_name": "Desai",
            "role": "SRE",
            "sn": 2
        },
        {
            "action_url": "/candidate/4",
            "ai_match_score": 85,
            "first_name": "Ananya",
            "gender": "Male",
            "last_name": "Rao",
            "role": "Software Engineer",
            "sn": 3
        }
    ],
    "page": 1,
    "per_page": 12,
    "total": 3
}
```

#### get all candidates, filter by role
- endpoint: `/applications/<company_id>/candidates?role=<role>`
- method: GET
- desc: get all candidates who have applied to jobs of a particular company, filter by role
- constraints: ensure company_id exists
- example:
```
{
    "candidates": [
        {
            "action_url": "/candidate/4",
            "ai_match_score": 85,
            "first_name": "Ananya",
            "gender": "Male",
            "last_name": "Rao",
            "role": "Software Engineer",
            "sn": 1
        }
    ],
    "page": 1,
    "per_page": 12,
    "total": 1
}
```

#### search candidates by name
- endpoint: `/applications/<company_id>/candidates?search=<search_term>`
- method: GET
- desc: get all candidates who have applied to jobs of a particular company, search by name
- constraints: ensure company_id exists
- example:
```
{
    "candidates": [
        {
            "action_url": "/candidate/2",
            "ai_match_score": 91,
            "first_name": "srupat",
            "gender": "Male",
            "last_name": "",
            "role": "SRE",
            "sn": 1
        }
    ],
    "page": 1,
    "per_page": 12,
    "total": 1
}
```

#### get candidates by page by specifying page number and per page count
- endpoint: `/applications/<company_id>/candidates?page=<page_number>&per_page=<per_page_count>`
- method: GET
- desc: get candidates who have applied to jobs of a particular company, by page
- constraints: ensure company_id exists
- example:
```
{
    "candidates": [
        {
            "action_url": "/candidate/2",
            "ai_match_score": 91,
            "first_name": "srupat",
            "gender": "Male",
            "last_name": "",
            "role": "SRE",
            "sn": 1
        }
    ],
    "page": 1,
    "per_page": 12,
    "total": 1
}
```

#### search by role and name
- endpoint: `/applications/<company_id>/candidates?role=<role>&search=<search_term>`
- method: GET
- desc: get all candidates who have applied to jobs of a particular company, filter by role and search by name
- constraints: ensure company_id exists

#### get count of candidates by company
- endpoint: `/applications/<company_id>/candidates/count`
- method: GET
- desc: get count of candidates who have applied to jobs of a particular company
- constraints: ensure company_id exists
- example:
```
{
    "count": 25
}
```

#### get all roles by company
- endpoint: `/applications/<company_id>/roles`
- method: GET
- desc: get all distinct roles for which candidates have applied to jobs of a particular company
- constraints: ensure company_id exists
- example:
```
{
    "roles": [
        "SRE",
        "Software Engineer",
        "Data Scientist"
    ]
}
```

### Candidate Profile page APIs
#### get candidate profile by application_id
- endpoint: `/applicant/profile/<application_id>`
- method: GET
- desc: get candidate profile by application_id
- constraints: ensure application_id exists
- example:
```
{
    "application_status": "under_review",
    "certifications": [],
    "cover_letter": {
        "filename": "dummy2.docx",
        "path": "/uploads/cover_letters/dummy2.docx",
        "uploaded_at": "2025-11-14 13:32:12"
    },
    "educations": [],
    "email": "srupat@gmail.com",
    "experiences": [],
    "github": "https://github.com/srupat",
    "interview_feedback": null,
    "linkedin": "https://linkedin.com/srupat",
    "name": "srupat",
    "phone": "1234567890",
    "portfolio": "https://srupat.me",
    "projects": [],
    "resume": {
        "filename": "BALI_5N-6D_FIT_.pdf",
        "path": "D:\\Srujan\\IITM\\SE\\project\\soft-engg-project-sep-2025-se-SEP-22\\app\\backend\\uploads\\resumes\\dca922de9b9445f3ac1259ba8bd0cdae.pdf",
        "uploaded_at": "2025-11-11 03:14:39.468554"
    },
    "skills": "flask"
}
```

#### get candidate experience
- endpoint: `/applicant/<applicant_id>/experiences`
- method: GET
- desc: get candidate experience by applicant_id
- constraints: ensure applicant_id exists
- example:
```
[
    {
        "company": "TechNova",
        "description": "Worked on backend Python APIs",
        "end": "2023-06-01",
        "id": 1,
        "position": "Software Developer Intern",
        "start": "2023-01-01"
    },
    {
        "company": "SoftLabs",
        "description": "Assisted in building microservices",
        "end": "2024-03-01",
        "id": 2,
        "position": "Junior Developer",
        "start": "2023-07-01"
    }
]
```

#### create candidate experience
- endpoint: `/applicant/<applicant_id>/experiences`
- method: POST
- desc: create candidate experience by applicant_id
- constraints: ensure applicant_id exists
- example:
```
{
    "company": "InnoTech",
    "position": "Software Engineer",
    "start_date": "2024-06-01",
    "end_date": "2025-06-01",
    "description": "Worked on AI projects"
}
```

#### delete all candidate experiences
- endpoint: `/applicant/<applicant_id>/experiences`
- method: DELETE
- desc: delete all experiences for a candidate by applicant_id
- constraints: ensure applicant_id exists
- example response:
```
{
    "message": "All experiences deleted"
}
```

#### get candidate education
- endpoint: `/applicant/<applicant_id>/education`
- method: GET
- desc: get candidate education by applicant_id
- constraints: ensure applicant_id exists
- example:
```
[
    {
        "degree": "Masters",
        "end": "2026-05-01",
        "field": "Computer Science",
        "grade": "8.5",
        "grade_out_of": "10",
        "id": 1,
        "start": "2024-07-01",
        "university": "IIT Madras"
    }
]
```

#### create candidate education
- endpoint: `/applicant/<applicant_id>/education`
- method: POST
- desc: create candidate education by applicant_id
- constraints: ensure applicant_id exists
- example:
```
{
    "degree": "Bachelors",
    "field": "Computer Science",
    "university": "IIT Madras",
    "start_date": "2022-07-01",
    "end_date": "2026-05-01",
    "grade": "8.5",
    "grade_out_of": "10"
}
```

#### delete all candidate education
- endpoint: `/applicant/<applicant_id>/education`
- method: DELETE
- desc: delete all education records for a candidate by applicant_id
- constraints: ensure applicant_id exists
- example response:
```
{
    "message": "All education deleted"
}
```

#### get candidate projects
- endpoint: `/applicant/<applicant_id>/projects`
- method: GET
- desc: get candidate projects by applicant_id
- constraints: ensure applicant_id exists
- example:
```
[
    {
        "description": "Developed order & payment services",
        "id": 1,
        "project_url": "https://github.com/user/ecom",
        "technologies": "Flask, PostgreSQL, Redis",
        "title": "E-commerce Backend"
    },
    {
        "description": "WebSocket-based chat system",
        "id": 2,
        "project_url": "https://github.com/user/chat",
        "technologies": "Node.js, Socket.io",
        "title": "Real-time Chat App"
    }
]
```

#### create candidate projects
- endpoint: `/applicant/<applicant_id>/projects`
- method: POST
- desc: create candidate projects by applicant_id
- constraints: ensure applicant_id exists
- example:
```
{
    "title": "AI Chatbot",
    "description": "Built an AI-powered chatbot using GPT-4",
    "technologies": "Python, Flask, OpenAI API",
    "project_url": "https://github.com/xyz/aichatbot"
}
```

#### get all candidate certifications
- endpoint: `/applicant/<applicant_id>/certifications`
- method: GET
- desc: get candidate certifications by applicant_id
- constraints: ensure applicant_id exists

#### create candidate certification
- endpoint: `/applicant/<applicant_id>/certifications`
- method: POST
- desc: create candidate certification by applicant_id
- constraints: ensure applicant_id exists
- example:
```
{
    "certificate_name": "AWS Certified Solutions Architect",
    "issuing_organization": "Amazon Web Services",
    "issue_date": "2023-08-01",
    "expiration_date": "2026-08-01",
    "credential_id": "AWS-12345678",
    "credential_url": "https://aws.amazon.com/certification/verify/AWS-12345678"
}
```

#### delete all candidate certifications
- endpoint: `/applicant/<applicant_id>/certifications`
- method: DELETE
- desc: delete all certifications for a candidate by applicant_id
- constraints: ensure applicant_id exists
- example response:
```
{
    "message": "All certifications deleted"
}
```

#### candidate resume download
- endpoint: `/applicant/<applicant_id>/download_resume`
- method: GET
- desc: download candidate resume by applicant_id
- constraints: ensure applicant_id exists

#### candidate cover letter download
- endpoint: `/applicant/<applicant_id>/download_cover_letter`
- method: GET
- desc: download candidate cover letter by applicant_id
- constraints: ensure applicant_id exists

### Schedule/Reject interview
#### Schedule interview
- endpoint: `/interview/schedule/<application_id>/<hr_id>`
- method: POST
- desc: schedule interview for an application by a particular hr
- constraints: ensure application_id and hr_id exists
- example:
```
{
    "interview_date": "2025-06-10",
    "interview_time": "14:30",
    "duration": 30,
    "stage": "technical"
}
```

#### Reject interview
- endpoint: `/interview/reject/<application_id>`
- method: POST
- desc: reject interview for an application
- constraints: ensure application_id exists

### Interview Slots page
#### get count of interviews scheduled this month
- endpoint: `/interview/stats/scheduled_month/<company_id>`
- method: GET
- desc: get count of interviews scheduled this month
- constraints: ensure company_id exists

#### get count of interviews scheduled this week
- endpoint: `/interview/stats/scheduled_week/<company_id>`
- method: GET
- desc: get count of interviews scheduled this week
- constraints: ensure company_id exists

#### get count of completed interviews according to company_id
- endpoint: `/interview/stats/completed/<company_id>`
- method: GET
- desc: get count of completed interviews according to company_id
- constraints: ensure company_id exists

#### get count of pending interviews according to company_id
- endpoint: `/interview/stats/pending_feedback/<company_id>`
- method: GET
- desc: get count of pending interviews according to company_id
- constraints: ensure company_id exists

#### Interview card information according to company_id
- endpoint: `/interview/cards/<company_id>`
- method: GET
- desc: get interview card information according to company_id
- constraints: ensure company_id exists

### Interview Evaluation page
#### get interview evaluation details
- endpoint: `/interview/evaluation/<interview_id>`
- method: GET
- desc: get interview evaluation details by interview_id
- constraints: ensure interview_id exists

#### submit interview feedback
- endpoint: `/interview/feedback/<interview_id>`
- method: POST
- desc: submit feedback for an interview, changes status from `feedback_pending` to `completed` to allow decision making
- constraints: ensure interview_id exists and interview status is `feedback_pending`
- example response:
```
{
    "message": "Feedback submitted successfully",
    "interview_status": "completed"
}
```

#### approve, reject or keep pending after evaluation
- endpoint: `/interview/decision/<interview_id>`
- method: PUT
- desc: approve, reject or keep pending (on-hold) after evaluation
- constraints: ensure interview_id exists

### Shortlisted Candidates page
#### get all statistics for top modals
- endpoint: `/shortlist/<company_id>/stats`
- method: GET
- desc: get all statistics for top modals
- constraints: ensure company_id exists
- example response:
```
{
    "acceptance_rate": 0.0,
    "offers_sent": 1,
    "pending_interviews": 0,
    "total_shortlisted": 2
}
```

#### get all shortlisted candidates, filter by status, role and search by name or ID
- endpoint: `/shortlist/<company_id>/candidates?status=<status>&role=<role>&search=<search_term>`
- method: GET
- desc: get all shortlisted candidates, filter by status, role and search by name or ID
- constraints: ensure company_id exists
- example response:
```
[
    {
        "ai_match_score": 91,
        "applicant_id": 2,
        "application_id": 2,
        "first_name": "srupat",
        "gender": "Male",
        "last_name": "",
        "role": "SRE",
        "status": "offer sent"
    },
    {
        "ai_match_score": 78,
        "applicant_id": 8,
        "application_id": 3,
        "first_name": "Rohan",
        "gender": "Male",
        "last_name": "Desai",
        "role": "SRE",
        "status": "offer sent"
    },
    {
        "ai_match_score": 85,
        "applicant_id": 9,
        "application_id": 4,
        "first_name": "Ananya",
        "gender": "Male",
        "last_name": "Rao",
        "role": "Software Engineer",
        "status": "offer sent"
    }
]
```

#### view more is same as above candidate's view more view
#### schedule interview is also same as above schedule interview API
#### generate/send offer letter is implemented below this
#### reject candidate
- endpoint: `/shortlist/reject/<application_id>`
- method: PUT
- desc: reject candidate by application_id
- constraints: ensure application_id exists

### Offer letter page
#### get selected candidates for offer letter generation
- endpoint: `/offer/eligible/<company_id>`
- method: GET
- desc: get all candidates eligible for offer letter generation (interviews with status='completed' and result='selected') for a company
- constraints: ensure company_id exists
- example response:
```
[
    {
        "application_id": 4,
        "candidate_id": 2,
        "candidate_name": "John Doe",
        "email": "john@example.com",
        "job_title": "Software Engineer",
        "basic_salary": "1500000",
        "employment_type": "full-time",
        "location": "Remote",
        "company_name": "Tech Corp",
        "interview_id": 5,
        "interview_stage": "technical",
        "interview_date": "2025-11-15",
        "interview_mode": "online",
        "slot_start_time": "10:00",
        "slot_end_time": "11:00",
        "duration_minutes": 60,
        "interviewer_name": "Jane Smith",
        "interview_result": "selected",
        "interview_feedback": "Excellent candidate"
    }
]
```

#### create new offer letter
- endpoint: `/offer_letter`
- method: POST
- desc: create a new offer letter by giving application_id, candidate_id, company_id, joining_date, ctc
- refer to the Offer Letter CRUD endpoint above for more details

#### send offer letter via email
- endpoint: `/offer/send_offer/<application_id>`
- method: POST
- desc: send offer letter via email by application_id. Candidate must have completed interview with result='selected'. Generates PDF and sends via email.
- constraints: ensure application_id exists, interview status='completed' and result='selected'
- request body (JSON, all fields optional except salary if job has no basic_salary):
```
{
    "salary": 1500000,
    "position": "Software Engineer",
    "start_date": "2025-12-01",
    "department": "Engineering",
    "work_mode": "Remote",
    "benefits": "Health insurance, stock options",
    "valid_until": "2025-11-30"
}
```
- note: If salary is not provided, uses job's basic_salary. start_date format: YYYY-MM-DD
- example response:
```
{
    "message": "Offer letter sent",
    "offer_id": 5
}
```

## Applicant side
### Applicant Dashboard APIs
#### Get applicant dashboard all data
- endpoint: `/applicant_dashboard/<applicant_id>`
- method: GET
- desc: get applicant dashboard all data
- constraints: ensure applicant_id exists
- example response:
```
{
    "applicant_name": "srupat",
    "application_status_counts": {
        "Applied": 0,
        "Interview": 0,
        "Offer": 0,
        "Rejected": 1,
        "Shortlisted": 0
    },
    "profile_completion": 100,
    "recent_applications": [
        {
            "application_id": 2,
            "applied_date": "2025-11-12T17:05:52.138794",
            "company": "company1",
            "job_title": "SRE",
            "status": "rejected"
        }
    ],
    "upcoming_interviews": [
        {
            "company": "company1",
            "date": "2025-11-15",
            "interview_id": 1,
            "job_title": "SRE",
            "recording_url": null,
            "stage": "technical",
            "time": "05:30"
        },
        {
            "company": "company1",
            "date": "2025-11-16",
            "interview_id": 3,
            "job_title": "SRE",
            "recording_url": null,
            "stage": "hr",
            "time": "09:30"
        },
        {
            "company": "company1",
            "date": "2025-11-17",
            "interview_id": 4,
            "job_title": "SRE",
            "recording_url": null,
            "stage": "technical",
            "time": "10:00"
        }
    ]
}
```

#### Get applicant profile all data
- endpoint: `/applicant_profile/<applicant_id>`
- method: GET
- desc: get applicant profile all data
- constraints: ensure applicant_id exists
- example response:
```
{
    "certifications": [
        {
            "certificate_name": "Google Data Analytics",
            "credential_id": "GDA-5567",
            "credential_url": "https://google.com/cert/5567",
            "expiry_date": null,
            "id": 2,
            "issue_date": "2022-04-01",
            "issuing_organization": "Google"
        }
    ],
    "cover_letter": {
        "filename": null,
        "path": null,
        "uploaded_at": null
    },
    "education": [
        {
            "degree": "B.Tech",
            "end_date": "2022-05-01",
            "field": "Information Technology",
            "grade": "8.1",
            "grade_out_of": "10",
            "id": 2,
            "start_date": "2018-07-01",
            "university": "IIT Bombay"
        }
    ],
    "personal_info": {
        "bio": "hello",
        "email": "rohan.desai@example.com",
        "location": "pune",
        "name": "Rohan Desai",
        "phone": "9876540001"
    },
    "resume": {
        "filename": "rohan_resume.pdf",
        "path": "/resumes/rohan_resume.pdf",
        "uploaded_at": "2025-11-11T03:14:39.468554"
    },
    "skills": [
        "Python",
        "Flask",
        "SQL"
    ],
    "work_experience": [
        {
            "company": "DataCorp",
            "description": "Worked on ML model training",
            "end_date": "2022-12-01",
            "id": 3,
            "position": "AI Intern",
            "start_date": "2022-05-01"
        },
        {
            "company": "VisionAI",
            "description": "Maintained AI pipelines",
            "end_date": "2024-01-01",
            "id": 4,
            "position": "Software Engineer",
            "start_date": "2023-01-01"
        }
    ]
}
```

#### updating individual components APIs can be found above in Applicant CRUD endpoints and HR modify applicant profile endpoints.

### Job Postings page
#### get all job postings, filter by role, search by job title, with pagination
- endpoint: `/job/opportunities/<applicant_id>?role=<role>&search=<search_term>&page=<page_number>&per_page=<per_page_count>`
- method: GET
- desc: get all job postings, filter by role, search by job title, with pagination
- constraints: ensure applicant_id exists
- example response:
```
{
    "jobs": [
        {
            "company": "company1",
            "job_id": 4,
            "location": "Pune",
            "position": "SRE",
            "skills_matched": "0/1",
            "work_mode": "fulltime"
        },
        {
            "company": "company1",
            "job_id": 5,
            "location": "Bangalore",
            "position": "Software Engineer",
            "skills_matched": "3/3",
            "work_mode": "Full-time"
        },
        {
            "company": "TechCorp Solutions",
            "job_id": 6,
            "location": "Hyderabad",
            "position": "Frontend Developer",
            "skills_matched": "0/3",
            "work_mode": "Full-time"
        },
        {
            "company": "Skyline Innovations",
            "job_id": 7,
            "location": "Pune",
            "position": "Data Analyst",
            "skills_matched": "1/3",
            "work_mode": "Full-time"
        },
        {
            "company": "FutureSoft Technologies",
            "job_id": 8,
            "location": "Chennai",
            "position": "HR Executive",
            "skills_matched": "0/3",
            "work_mode": "Full-time"
        },
        {
            "company": "NeoWorks Labs",
            "job_id": 9,
            "location": "Delhi",
            "position": "Machine Learning Engineer",
            "skills_matched": "1/3",
            "work_mode": "Full-time"
        }
    ],
    "page": 1,
    "per_page": 10,
    "total_jobs": 6,
    "total_pages": 1
}
```

#### get all job details by job_id and applicant_id
- endpoint: `/job/detail/<job_id>/<applicant_id>`
- method: GET
- desc: get all job details by job_id and applicant_id
- constraints: ensure job_id and applicant_id exists
- example response:
```
{
    "basic_salary": "5000000.00",
    "company": "company1",
    "company_info": {
        "company_size": "10,000+ employees",
        "description": "Google is a global technology leader focused on improving the ways people connect with information.",
        "industry": "Technology",
        "website": "https://about.google.com"
    },
    "days_ago_posted": 5,
    "deadline": null,
    "experience_range": "2 yoe",
    "jd_file_url": "/jobs/download_jd/4",
    "job_description": "devops",
    "job_id": 4,
    "job_title": "SRE",
    "key_responsibilities": [
        "Manage and scale infrastructure for high availability",
        "Automate deployment pipelines and scripting tasks",
        "Monitor system reliability and performance"
    ],
    "location": "Pune",
    "required_skills": [
        "scripting"
    ],
    "requirements": [
        "2+ years of experience in SRE or DevOps",
        "Strong scripting knowledge (Python/Bash)",
        "Experience with CI/CD tools and cloud platforms"
    ],
    "skills_match": {
        "matched": 0,
        "percentage": 0.0,
        "total": 1
    },
    "total_applicants": 2,
    "work_mode": "fulltime"
}
```

#### download job description (JD) file
- endpoint: `/job/download_jd/<job_id>`
- method: GET
- desc: download job description (JD) file by job_id
- constraints: ensure job_id exists

#### apply to a job
- endpoint: `/applications/apply`
- method: POST
- desc: apply to a job by giving job_id and applicant_id
- example body:
```
{
    "applicant_id":9,
    "job_id":7,
    "resume_filename":"test.txt"
}
```
NOTE: we may modify this route later according to frontend requirements

### Interview slots page
#### get summary of scheduled, upcoming, completed interviews for an applicant
- endpoint: `/interview/applicant/<applicant_id>/summary`
- method: GET
- desc: get summary of scheduled, upcoming, completed interviews for an applicant
- constraints: ensure applicant_id exists
- example response:
```
{
    "completed": 1,
    "total": 0,
    "upcoming": 0
}
```

#### get all scheduled interviews for an applicant
- endpoint: `/interview/applicant/<applicant_id>/list`
- method: GET
- desc: get all scheduled interviews for an applicant
- constraints: ensure applicant_id exists
- example response:
```
[
    {
        "application_id": 2,
        "company_name": "company1",
        "end_time": "06:30:00",
        "interview_date": "2025-11-15",
        "interview_id": 1,
        "job_title": "SRE",
        "stage": "technical",
        "start_time": "05:30:00",
        "status": "scheduled"
    },
    {
        "application_id": 2,
        "company_name": "company1",
        "end_time": "10:30:00",
        "interview_date": "2025-11-17",
        "interview_id": 4,
        "job_title": "SRE",
        "stage": "technical",
        "start_time": "10:00:00",
        "status": "scheduled"
    }
]
```

#### cancel interview by interview_id
- endpoint: `/interview/<interview_id>/cancel`
- method: PUT
- desc: cancel interview by interview_id
- constraints: ensure interview_id exists

### My applications page
#### get applications stats according to applicant_id and all applications
- endpoint: `/applications/applicant/<applicant_id>`
- method: GET
- desc: get applications stats according to applicant_id and all applications
- constraints: ensure applicant_id exists
- example response:
```
{
    "applications": [
        {
            "application_id": 2,
            "applied_on": "2025-11-12 17:05:52.138794",
            "company_name": "company1",
            "job_title": "SRE",
            "location": "Pune",
            "status": "rejected",
            "work_mode": "fulltime"
        }
    ],
    "summary": {
        "rejected": 1,
        "shortlisted": 0,
        "total": 1
    }
}
```

## Company Dashboard
### All stats on company dashboard
- endpoint: `/company/dashboard/<company_id>`
- method: GET
- desc: get all stats on company dashboard
- constraints: ensure company_id exists
- example response:
```
{
    "hiring_summary": {
        "interviewing": {
            "2025-11": 1,
            "2025-12": 2
        },
        "onboarded": {},
        "openings": {
            "2025-11": 12
        }
    },
    "onboarded_last_month": 0,
    "open_job_openings": 12,
    "total_employees": 1,
    "total_hrs": 1
}
```

### Manage HR page
> HR CRUD endpoints are already defined above