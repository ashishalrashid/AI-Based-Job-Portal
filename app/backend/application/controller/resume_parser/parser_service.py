"""
Critical-correct resume parser service.

Key fixes:
 - Correct Application lookup by (applicant_id, job_id)
 - Idempotency (skip re-score unless force=true)
 - Robust download with timeouts + retries
 - Prompt size guard + truncated logging
 - Returns candidate paths tried on resume-not-found errors
 - ✅ MODEL FALLBACK for quota exhaustion
 - ✅ NATIVE JSON MODE for reliable parsing
 - ✅ ROBUST REGEX for cleaning responses
 - ✅ STRUCTURED METADATA with validation
"""
from flask import Blueprint, request, jsonify, current_app
import os
import json
import re
from uuid import uuid4
from werkzeug.utils import secure_filename
import docx2txt
from PyPDF2 import PdfReader
import requests
from requests.adapters import HTTPAdapter, Retry
import google.generativeai as genai
from application.data.models import Application, JobPosting
from application.data.database import db

resume_parser_bp = Blueprint('resume_parser', __name__)

# ----- CONFIG -----
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception:
        # don't crash at import; will surface on call
        pass

MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Adjust these paths relative to your actual project structure
UPLOAD_RESUMES = os.path.join(BASE_DIR, '../..', 'uploads', 'resumes')
UPLOAD_JDS = os.path.join(BASE_DIR, '../..', 'uploads', 'jds')
os.makedirs(UPLOAD_RESUMES, exist_ok=True)
os.makedirs(UPLOAD_JDS, exist_ok=True)

# HTTP session for downloads with retries/timeouts
_session = requests.Session()
_retries = Retry(total=3, backoff_factor=0.5, status_forcelist=(429, 502, 503, 504))
_adapter = HTTPAdapter(max_retries=_retries)
_session.mount("https://", _adapter)
_session.mount("http://", _adapter)

# Guards
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
MAX_PROMPT_CHARS = 15000
PROMPT_RESUME_CHARS = 8000
PROMPT_JD_CHARS = 6000
DOWNLOAD_TIMEOUT = (5, 30)

# ----- Helpers: file extraction -----
def extract_text_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    parts = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            parts.append(t)
    full = "\n".join(parts)
    if not full or not full.strip():
        raise ValueError("No text extracted from PDF")
    return full

def extract_text_from_docx(path: str) -> str:
    txt = docx2txt.process(path)
    if not txt or not txt.strip():
        raise ValueError("No text extracted from DOCX")
    return txt

def extract_text_from_txt(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        txt = f.read()
    if not txt or not txt.strip():
        raise ValueError("No text extracted from TXT")
    return txt

def extract_text_from_file(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    ext = path.rsplit('.', 1)[-1].lower()
    if ext == 'pdf':
        return extract_text_from_pdf(path)
    if ext in ('docx', 'doc'):
        return extract_text_from_docx(path)
    if ext == 'txt':
        return extract_text_from_txt(path)
    raise ValueError(f"Unsupported file extension: {ext}")

# ----- JSON cleaning -----
def _find_first_balanced_json(text: str):
    start = None
    depth = 0
    for i, ch in enumerate(text):
        if ch == '{':
            if start is None:
                start = i
            depth += 1
        elif ch == '}':
            if start is not None:
                depth -= 1
                if depth == 0:
                    return text[start:i+1]
    return None

def clean_json_response(response_text: str) -> str:
    if not response_text:
        return ""
    text = response_text.strip()
    
    # ✅ FIXED 1: Correct regex for Markdown JSON blocks
    fenced = re.search(r'```(?:json)?\s*(.*?)```', text, re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()
    
    balanced = _find_first_balanced_json(text)
    if balanced:
        return balanced.strip()
    return text


# ----- ✅ FIXED Gemini call wrapper with NATIVE JSON & FALLBACK -----
def call_gemini_once(prompt: str) -> str:
    """
    Call Gemini API with native JSON enforcement and model fallback support.
    """
    if not GEMINI_API_KEY:
        raise RuntimeError("Gemini API key missing. Set GEMINI_API_KEY in environment.")
    
    # ✅ FIXED 2: Updated model list (Removed 1.5, added 2.0/2.5/Lite)
    models_to_try = [
        MODEL,
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash", 
        "gemini-2.5-flash-lite",
        "gemini-flash-latest",
        "gemini-2.5-pro"
    ]
    
    # ✅ FIXED 3: Using simple dict for config
    gen_config = {
        "response_mime_type": "application/json"
    }
    
    last_error = None
    for model_name in models_to_try:
        try:
            current_app.logger.info(f"🔄 Resume Parser trying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            
            # Pass generation_config as dict
            response = model.generate_content(prompt, generation_config=gen_config)
            
            if hasattr(response, "text"):
                result = response.text
            elif isinstance(response, dict):
                result = response.get("text") or json.dumps(response)
            else:
                # Fallback for complex response objects
                result = getattr(response, "parts", [{}])[0].text
            
            if result and result.strip():
                current_app.logger.info(f"✅ Resume Parser SUCCESS with model: {model_name}")
                return result
                
        except Exception as e:
            error_msg = str(e).lower()
            error_type = type(e).__name__
            
            # Quota handling
            if "resourceexhausted" in error_type.lower() or "quota" in error_msg or "429" in error_msg:
                current_app.logger.warning(f"⚠️ {model_name} quota exhausted: {error_type}")
                last_error = e
                continue
            
            current_app.logger.error(f"❌ {model_name} failed: {error_type} - {error_msg}")
            last_error = e
            continue
    
    current_app.logger.error(f"❌ ALL MODELS FAILED in Resume Parser")
    raise RuntimeError(f"All Gemini models failed. Last error: {str(last_error)[:200]}")

# ----- Utilities -----
GDRIVE_ID_RE = re.compile(r"(?:/d/|id=)([a-zA-Z0-9_-]{10,})")

def _gdrive_direct_download_url(url: str) -> str:
    m = GDRIVE_ID_RE.search(url)
    if m:
        file_id = m.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return url

def _download_url_to_path(url: str, folder: str, prefix: str = "file", timeout: tuple = DOWNLOAD_TIMEOUT) -> str:
    url2 = _gdrive_direct_download_url(url)
    try:
        resp = _session.get(url2, stream=True, timeout=timeout)
        resp.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"Failed to download file from {url}: {e}")

    # determine filename
    cd = resp.headers.get("content-disposition", "") or ""
    filename = None
    if "filename=" in cd:
        m = re.search(r'filename\*?="?([^";]+)"?', cd)
        if m:
            filename = m.group(1).strip().strip('"')

    if not filename:
        filename = os.path.basename(url.split("?", 1)[0]) or f"{prefix}_{uuid4().hex}.bin"

    safe = secure_filename(filename)
    path = os.path.join(folder, safe)

    try:
        with open(path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    except Exception as e:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
        raise RuntimeError(f"Failed saving downloaded file: {e}")

    return path

# ----- Resume retrieval (explicit resume_file_path) -----
def get_resume_text_from_application(application: Application, tried_paths_out: list = None):
    """
    Primary: ApplicantProfile.resume_file_path (absolute or filename in uploads/resumes)
    """
    tried = []
    applicant_profile = getattr(application, "applicant", None)
    if not applicant_profile:
        # Check if the relationship is named differently in your model
        raise ValueError("Application has no associated applicant profile")

    resume_file_path = getattr(applicant_profile, "resume_file_path", None)
    if not resume_file_path:
        raise FileNotFoundError("Applicant profile has no resume_file_path configured")

    # absolute
    if os.path.isabs(resume_file_path):
        tried.append(str(resume_file_path))
        if os.path.exists(resume_file_path):
            return extract_text_from_file(resume_file_path)
    
    # relative to uploads
    relative_path = os.path.join(UPLOAD_RESUMES, resume_file_path)
    tried.append(relative_path)
    if os.path.exists(relative_path):
        return extract_text_from_file(relative_path)
    
    # as-is (project root)
    tried.append(resume_file_path)
    if os.path.exists(resume_file_path):
        return extract_text_from_file(resume_file_path)

    if tried_paths_out is not None:
        tried_paths_out.extend(tried)
    raise FileNotFoundError(f"Resume not found. Tried: {tried}")

# ----- JD retrieval (job_description or attachment_url) -----
def get_jd_text_from_job(job: JobPosting):
    """
    Priority:
     - job.job_description (inline text)
     - job.attachment_url (HTTP/GDrive)
     - attachment_filename / attachment_path (local)
    """
    jd_field = getattr(job, "job_description", None)
    if jd_field and isinstance(jd_field, str) and jd_field.strip():
        return jd_field.strip()

    # attachment_url
    attachment_url = getattr(job, "attachment_url", None)
    if attachment_url and isinstance(attachment_url, str) and attachment_url.strip():
        url = attachment_url.strip()
        if url.lower().startswith(("http://", "https://")):
            saved = _download_url_to_path(url, UPLOAD_JDS, prefix="jd")
            current_app.logger.info(f"Downloaded JD to {saved}")
            return extract_text_from_file(saved)
        # treat as file path
        if os.path.isabs(url) and os.path.exists(url):
            return extract_text_from_file(url)
        candidate = os.path.join(UPLOAD_JDS, url)
        if os.path.exists(candidate):
            return extract_text_from_file(candidate)
        raise FileNotFoundError(f"JD attachment_url present but file not accessible: {url}")

    # local attachment fields fallback
    for attr in ("attachment_filename", "attachment_path"):
        # ✅ FIXED: getattr with default to avoid crash
        v = getattr(job, attr, None)
        if not v:
            continue
        
        cand = v if os.path.isabs(v) else os.path.join(UPLOAD_JDS, v)
        if os.path.exists(cand):
            return extract_text_from_file(cand)

    raise FileNotFoundError("No job_description text or accessible JD file found on JobPosting")

# ✅ NEW: Metadata validation helper
# Replace lines 284-357 in your resume_parser.py
def validate_and_fix_metadata(metadata: dict) -> dict:
    """Ensure metadata has correct structure with all required fields - AGGRESSIVE MODE"""
    
    if not isinstance(metadata, dict):
        metadata = {}
    
    # Validate skills
    if not isinstance(metadata.get("skills", []), list):
        metadata["skills"] = []
    
    # ✅ FORCE EXPERIENCE TO OBJECTS - NO EXCEPTIONS
    raw_experience = metadata.get("experience", [])
    if not isinstance(raw_experience, list):
        raw_experience = []
    
    fixed_experience = []
    for exp in raw_experience:
        if isinstance(exp, str):
            # ✅ STRING DETECTED - FORCE CONVERT TO OBJECT
            current_app.logger.warning(f"⚠️ Converting string experience: {exp[:80]}")
            
            # Extract components from string patterns
            role = "Not specified"
            company = "Not specified"
            duration = ""
            responsibilities = []
            
            # Pattern 1: "Title at Company (Duration)"
            if " at " in exp:
                parts = exp.split(" at ", 1)
                role = parts[0].strip()
                rest = parts[1]
                
                # Check for duration in parentheses
                if "(" in rest:
                    company = rest.split("(")[0].strip()
                    duration = rest.split("(")[1].split(")")[0].strip()
                else:
                    company = rest.strip()
            
            # Pattern 2: "Title (Company)"
            elif "(" in exp and ")" in exp:
                role = exp.split("(")[0].strip()
                company = exp.split("(")[1].split(")")[0].strip()
            
            # Pattern 3: "Title: Description" or just "Title"
            elif ":" in exp:
                role = exp.split(":")[0].strip()
                responsibilities = [exp.split(":", 1)[1].strip()]
            else:
                role = exp.strip()
            
            fixed_experience.append({
                "role": role,
                "company": company,
                "duration": duration,
                "responsibilities": responsibilities
            })
            
        elif isinstance(exp, dict):
            # Already an object - just validate fields
            fixed_exp = {
                "role": exp.get("role") or exp.get("position") or "Role not specified",
                "company": exp.get("company") or "Company not specified",
                "duration": exp.get("duration") or exp.get("period") or "",
                "responsibilities": exp.get("responsibilities", [])
            }
            
            # Ensure responsibilities is array
            if not isinstance(fixed_exp["responsibilities"], list):
                fixed_exp["responsibilities"] = [str(fixed_exp["responsibilities"])] if fixed_exp["responsibilities"] else []
            
            fixed_experience.append(fixed_exp)
        else:
            # Skip invalid entries
            current_app.logger.warning(f"⚠️ Skipping invalid experience entry: {type(exp)}")
    
    metadata["experience"] = fixed_experience
    
    # ✅ FORCE EDUCATION TO OBJECTS - NO EXCEPTIONS
    raw_education = metadata.get("education", [])
    if not isinstance(raw_education, list):
        raw_education = []
    
    fixed_education = []
    for edu in raw_education:
        if isinstance(edu, str):
            # ✅ STRING DETECTED - FORCE CONVERT TO OBJECT
            current_app.logger.warning(f"⚠️ Converting string education: {edu[:80]}")
            
            degree = edu.strip()
            field = "Not specified"
            university = "Not specified"
            graduation_year = ""
            
            # Pattern 1: "Degree in Field from University (Year)"
            if " in " in edu:
                parts = edu.split(" in ", 1)
                degree = parts[0].strip()
                rest = parts[1]
                
                if " from " in rest:
                    field = rest.split(" from ")[0].strip()
                    university_part = rest.split(" from ")[1]
                    
                    if "(" in university_part:
                        university = university_part.split("(")[0].strip()
                        graduation_year = university_part.split("(")[1].split(")")[0].strip()
                    else:
                        university = university_part.strip()
                else:
                    field = rest.strip()
            
            # Pattern 2: "Degree from University"
            elif " from " in edu:
                parts = edu.split(" from ", 1)
                degree = parts[0].strip()
                university = parts[1].strip()
            
            # Pattern 3: "Degree, Field"
            elif "," in edu:
                parts = edu.split(",", 1)
                degree = parts[0].strip()
                field = parts[1].strip()
            
            fixed_education.append({
                "degree": degree,
                "field": field,
                "university": university,
                "graduation_year": graduation_year
            })
            
        elif isinstance(edu, dict):
            # Already an object - just validate fields
            fixed_edu = {
                "degree": edu.get("degree") or "Degree not specified",
                "field": edu.get("field") or edu.get("major") or "Field not specified",
                "university": edu.get("university") or edu.get("institution") or "Institution not specified",
                "graduation_year": str(edu.get("graduation_year") or edu.get("year") or "")
            }
            fixed_education.append(fixed_edu)
        else:
            # Skip invalid entries
            current_app.logger.warning(f"⚠️ Skipping invalid education entry: {type(edu)}")
    
    metadata["education"] = fixed_education
    
    # Validate projects
    if not isinstance(metadata.get("projects", []), list):
        metadata["projects"] = []
    
    # Validate certifications
    if not isinstance(metadata.get("certifications", []), list):
        metadata["certifications"] = []
    
    # Ensure basic contact fields
    metadata.setdefault("name", "")
    metadata.setdefault("email", "")
    metadata.setdefault("phone", "")
    
    return metadata


# ----- Endpoint: parse-resume ----- 
@resume_parser_bp.route('/parse-resume', methods=['POST'])
def parse_resume_from_db():
    try:
        if 'applicantid' not in request.form or 'jobid' not in request.form:
            return jsonify({"error": "applicantid and jobid are required"}), 400

        try:
            applicantid = int(request.form['applicantid'])
            jobid = int(request.form['jobid'])
        except ValueError:
            return jsonify({"error": "Invalid applicantid/jobid format"}), 400

        # find the Application row
        application = Application.query.filter_by(applicant_id=applicantid, job_id=jobid).first()
        if not application:
            return jsonify({"error": "Application for given applicantid and jobid not found"}), 404

        # idempotency check
        force = str(request.form.get("force", "")).lower() in ("1", "true", "yes")
        if application.resume_score is not None and not force:
            metadata = None
            if getattr(application, "ai_metadata", None):
                try:
                    metadata = json.loads(application.ai_metadata)
                except Exception:
                    metadata = {"raw": application.ai_metadata}
            return jsonify({
                "success": True,
                "message": "Already processed",
                "applicantid": applicantid,
                "jobid": jobid,
                "score": application.resume_score,
                "feedback": application.ai_feedback,
                "metadata": metadata
            }), 200

        # get resume text
        tried = []
        try:
            resume_text = get_resume_text_from_application(application, tried_paths_out=tried)
            current_app.logger.info("Extracted resume text (len=%d)", len(resume_text))
        except FileNotFoundError:
            return jsonify({
                "error": "Could not find resume file",
                "attempted_paths": tried
            }), 400
        except Exception as e:
            return jsonify({"error": f"Resume extraction error: {str(e)}"}), 400

        # get JD text
        try:
            jd_text = get_jd_text_from_job(JobPosting.query.get(jobid))
            current_app.logger.info("Extracted JD text (len=%d)", len(jd_text))
        except Exception as e:
            return jsonify({"error": f"Could not obtain JD text: {str(e)}"}), 400

        # Truncate to guard limits
        resume_snip = resume_text
        jd_snip = jd_text
        combined = f"Resume Text:\n{resume_snip}\n\nJob Description:\n{jd_snip}"
        
        if len(combined) > MAX_PROMPT_CHARS:
            resume_snip = resume_text[:PROMPT_RESUME_CHARS]
            jd_snip = jd_text[:PROMPT_JD_CHARS]
            combined = f"Resume Text (truncated):\n{resume_snip}\n\nJob Description (truncated):\n{jd_snip}"

        # ✅ FIXED: Enhanced prompt with structured output
        prompt = (
            "You are an expert HR AI specialized in resume analysis.\n\n"
            "Analyze the Resume and Job Description below and return a JSON object with this EXACT schema:\n\n"
            "{\n"
            '  "metadata": {\n'
            '    "name": "Full Name from resume",\n'
            '    "email": "email@example.com",\n'
            '    "phone": "+1234567890",\n'
            '    "skills": ["Python", "JavaScript", "SQL"],\n'
            '    "experience": [\n'
            '      {\n'
            '        "role": "Software Engineer",\n'
            '        "company": "Company Name",\n'
            '        "duration": "Jan 2020 - Dec 2022",\n'
            '        "responsibilities": ["Built APIs", "Led team of 3"]\n'
            '      }\n'
            '    ],\n'
            '    "education": [\n'
            '      {\n'
            '        "degree": "Bachelor of Science",\n'
            '        "field": "Computer Science",\n'
            '        "university": "University Name",\n'
            '        "graduation_year": "2020"\n'
            '      }\n'
            '    ],\n'
            '    "certifications": ["AWS Certified", "PMP"],\n'
            '    "projects": [\n'
            '      {\n'
            '        "title": "E-commerce Platform",\n'
            '        "description": "Built full-stack application",\n'
            '        "technologies": ["React", "Node.js"]\n'
            '      }\n'
            '    ]\n'
            '  },\n'
            '  "score": 85,\n'
            '  "feedback": "Strong candidate with 5 years experience in relevant technologies. Skills align well with job requirements."\n'
            "}\n\n"
            "CRITICAL RULES:\n"
            "1. Extract REAL data from the resume - NEVER use placeholder text\n"
            "2. If a field is missing, use empty string \"\" or empty array []\n"
            "3. For experience: Include job title, company name, dates, and key responsibilities\n"
            "4. For education: Include degree type, field of study, university name, and year\n"
            "5. Skills should be a flat array of technology/skill names\n"
            "6. Score (0-100) should reflect how well the candidate matches the job requirements\n"
            "7. Feedback should be 2-3 sentences explaining the score\n"
            "8. Return ONLY valid JSON - no markdown, no explanations\n\n"
            + combined
        )

        # Call Gemini
        try:
            raw = call_gemini_once(prompt)
            current_app.logger.debug("Raw AI response (first 300 chars): %s", raw[:300])
        except Exception as e:
            current_app.logger.error("Gemini call failed", exc_info=True)
            return jsonify({"error": f"LLM error: {str(e)}"}), 500

        cleaned = clean_json_response(raw)
        try:
            parsed = json.loads(cleaned)
        except Exception as parse_error:
            current_app.logger.error("Failed to parse JSON from LLM", exc_info=True)
            current_app.logger.debug("Cleaned response: %s", cleaned[:500])
            return jsonify({"error": "Failed to parse response from AI"}), 500

        # ✅ FIXED: Validate and fix metadata structure
        metadata = parsed.get("metadata", {})
        metadata = validate_and_fix_metadata(metadata)
        
        score_raw = parsed.get("score", 0)
        feedback = parsed.get("feedback", "") or ""

        # normalize score
        try:
            score = float(score_raw)
        except Exception:
            nums = re.findall(r'\d+\.?\d*', str(score_raw))
            score = float(nums[0]) if nums else 0.0
        score = max(0.0, min(100.0, score))

        # ✅ ADDED: Debug logging
        current_app.logger.info(f"Parsed metadata - Experience entries: {len(metadata.get('experience', []))}, Education entries: {len(metadata.get('education', []))}")
        current_app.logger.debug(f"Metadata structure: {json.dumps(metadata, indent=2)[:500]}")

        # persist
        try:
            application.resume_score = int(round(score))
            application.ai_feedback = feedback
            # ✅ FIXED: Removed hasattr check - always try to save
            try:
                application.ai_metadata = json.dumps(metadata)
            except AttributeError:
                current_app.logger.warning("Application model missing ai_metadata column")
            
            db.session.commit()
            current_app.logger.info(f"✅ Successfully saved to DB - Score: {application.resume_score}, Metadata size: {len(json.dumps(metadata))} bytes")
        except Exception as e:
            current_app.logger.error("DB commit failed", exc_info=True)
            db.session.rollback()
            return jsonify({"error": "Failed to persist results"}), 500

        return jsonify({
            "success": True,
            "applicantid": applicantid,
            "jobid": jobid,
            "score": round(score, 2),
            "feedback": feedback,
            "metadata": metadata
        }), 200

    except Exception as exc:
        current_app.logger.error("Unhandled error", exc_info=True)
        return jsonify({"error": str(exc)}), 500

# ----- Endpoint: read results -----
@resume_parser_bp.route('/application/<int:applicationid>/ai-results', methods=['GET'])
def get_application_ai_results(applicationid):
    try:
        application = Application.query.get(applicationid)
        if not application:
            return jsonify({"error": "Application not found"}), 404

        score = getattr(application, "resume_score", None)
        feedback = getattr(application, "ai_feedback", None)
        metadata_raw = getattr(application, "ai_metadata", None)

        # ✅ FIXED: Strict check - all three must exist
        processed = (
            score is not None 
            and feedback is not None 
            and metadata_raw is not None
        )

        metadata = {}
        if metadata_raw:
            try:
                metadata = json.loads(metadata_raw) if isinstance(metadata_raw, str) else metadata_raw
                # Validate structure
                metadata = validate_and_fix_metadata(metadata)
            except Exception as e:
                current_app.logger.error(f"Failed to parse ai_metadata: {e}", exc_info=True)
                metadata = {}

        # ✅ FIXED: Return null for unprocessed data instead of defaults
        return jsonify({
            "processed": processed,
            "application_id": application.id,
            "score": score if processed else None,
            "feedback": feedback if processed else None,
            "metadata": metadata if processed else None,
            "message": "Resume parsed successfully" if processed else "Resume not yet parsed. Click 'Parse Resume' to analyze."
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching AI results: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# ✅ NEW: Debug endpoint
@resume_parser_bp.route('/debug/metadata/<int:applicationid>', methods=['GET'])
def debug_metadata(applicationid):
    """Debug endpoint to inspect stored metadata structure"""
    try:
        app = Application.query.get(applicationid)
        if not app:
            return jsonify({"error": "Application not found"}), 404
        
        metadata_raw = app.ai_metadata
        if not metadata_raw:
            return jsonify({"error": "No metadata stored"}), 404
        
        try:
            metadata = json.loads(metadata_raw)
            return jsonify({
                "application_id": applicationid,
                "raw_length": len(metadata_raw),
                "parsed_successfully": True,
                "metadata": metadata,
                "structure": {
                    "has_experience": bool(metadata.get("experience")),
                    "experience_count": len(metadata.get("experience", [])),
                    "experience_is_array": isinstance(metadata.get("experience"), list),
                    "first_exp_structure": metadata.get("experience", [{}])[0] if metadata.get("experience") else None,
                    "has_education": bool(metadata.get("education")),
                    "education_count": len(metadata.get("education", [])),
                    "education_is_array": isinstance(metadata.get("education"), list),
                    "first_edu_structure": metadata.get("education", [{}])[0] if metadata.get("education") else None
                }
            }), 200
        except Exception as e:
            return jsonify({
                "application_id": applicationid,
                "raw_preview": metadata_raw[:500],
                "parse_error": str(e)
            }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----- Health -----
@resume_parser_bp.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy" if GEMINI_API_KEY else "degraded",
        "gemini_configured": bool(GEMINI_API_KEY),
        "active_model": MODEL,
        "json_mode": "enabled",
        "structured_metadata": "enabled"
    }), 200

