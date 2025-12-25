# 📧 HR Offer Letter Email System - Test Guide

## 🎯 Test Candidates Created

**These candidates have COMPLETED + SELECTED interviews and are ELIGIBLE for offer letters:**

1. **Alice Johnson** - alice.johnson@test.com
   - Skills: Python, SQL, Flask
   - Experience: 3 years

2. **Bob Smith** - bob.smith@test.com  
   - Skills: React, Node.js, JavaScript
   - Experience: 2 years

3. **Carol Davis** - carol.davis@test.com
   - Skills: Java, Spring Boot, MySQL  
   - Experience: 4 years

## 🚀 Quick Start Commands

### 1. Initialize Database with Test Data
```bash
cd /home/jyoti/Documents/iitm/se/soft-engg-project-sep-2025-se-SEP-22/app/backend
python test_db_init.py
```

### 2. Start Services
```bash
# Terminal 1: Start MailDev
npm install -g maildev && maildev

# Terminal 2: Start Backend  
cd soft-engg-project-sep-2025-se-SEP-22/app/backend
python main.py

# Terminal 3: Start Frontend
cd soft-engg-project-sep-2025-se-SEP-22/app/frontend  
npm run dev
```

### 3. HR Login Credentials
- **Email**: hr1@test.com
- **Password**: password123

## 🔧 Curl Commands for Testing

### Step 1: Get JWT Token for HR User
```bash
curl -X POST http://localhost:8086/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "hr1@test.com",
    "password": "password123"
  }'
```

**Response will include:** `{"access_token": "YOUR_JWT_TOKEN_HERE"}`

### Step 2: Get Eligible Candidates
```bash
curl -X GET http://localhost:8086/offer/eligible/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

**Expected Response:** List of candidates with completed + selected interviews

### Step 3: Send Offer Letter to a Candidate
```bash
curl -X POST http://localhost:8086/offer/send/APPLICATION_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_path": "/home/jyoti/Documents/iitm/se/soft-engg-project-sep-2025-se-SEP-22/app/backend/sample_offer_alice.pdf"
  }'
```

### Step 4: Check Email in MailDev
- Open http://localhost:1080 in your browser
- You should see the offer letter email with PDF attachment

## 📊 Complete Test Workflow

### Frontend Testing
1. **Login** as HR: http://localhost:5173/login
2. **Navigate** to Eligible Candidates: http://localhost:5173/hr/eligible-candidates  
3. **View** shortlisted candidates
4. **Send** offer letters
5. **Check** MailDev for emails: http://localhost:1080

### API Testing  
1. **Authenticate** HR user with JWT token
2. **Fetch** eligible candidates using company ID
3. **Send** offer letters via API calls
4. **Verify** emails appear in MailDev

## 🎯 Key Features to Test

✅ **Dynamic HR Sender Email** - Uses hr1@test.com as sender
✅ **Personalized Subject Lines** - "Job Offer - [Position] at [Company]"  
✅ **PDF Attachment** - Offer letter PDF sent with email
✅ **Candidate Filtering** - Only shows completed + selected interviews
✅ **Status Tracking** - Email sending success/failure feedback
✅ **MailDev Integration** - Development email preview interface

## 🔍 Troubleshooting

**If you get connection errors:**
- Verify backend is running on http://localhost:8086
- Check vite.config.js proxy configuration (already fixed)

**If no candidates appear:**
- Ensure database was initialized with `python test_db_init.py`
- Verify HR user has correct company_id

**If emails don't send:**
- Check MailDev is running on http://localhost:1080
- Verify Flask-Mail configuration in backend

## 📧 Sample Email Content

**Subject**: Job Offer - Senior Software Engineer at TechCorp1 Pvt Ltd

**Body**:
```
Dear [Candidate Name],

We are pleased to offer you the position of Senior Software Engineer at TechCorp1 Pvt Ltd!

We were impressed by your qualifications and experience, and believe you will be a great addition to our team.

This email includes your official offer letter as a PDF attachment. Please review it carefully and let us know if you have any questions.

We look forward to welcoming you to TechCorp1 Pvt Ltd!

Best regards,
HR Team
TechCorp1 Pvt Ltd
```

---
**🎉 READY FOR TESTING! Run the database initialization and start testing the HR Offer Letter Email System.**
