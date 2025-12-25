"""
Configuration for Video Interview System
"""
import os
from pathlib import Path

# === Gemini AI Configuration ===
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
GEMINI_TIMEOUT_SECONDS = int(os.getenv('GEMINI_TIMEOUT_SECONDS', 15))  # Max AI API call timeout

# === Evaluation Configuration ===
EVALUATION_TIMEOUT_SECONDS = int(os.getenv('EVALUATION_TIMEOUT_SECONDS', 30))  # Longer for final evaluation

# === Azure Speech Service Configuration ===
AZURE_SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY')
AZURE_SPEECH_REGION = os.getenv('AZURE_SPEECH_REGION', 'eastus')
USE_AZURE_SPEECH = os.getenv('USE_AZURE_SPEECH', 'true').lower() == 'true'

# === Redis Session Store Configuration ===
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
SESSION_TTL_HOURS = int(os.getenv('SESSION_TTL_HOURS', 24))

# === Interview Flow Configuration ===
MAXQUESTIONS = int(os.getenv('MAXQUESTIONS', 10))
MAX_INTERVIEW_MINUTES = int(os.getenv('MAX_INTERVIEW_MINUTES', 30))
VIDEO_CHUNK_INTERVAL_MS = int(os.getenv('VIDEO_CHUNK_INTERVAL_MS', 2000))  # milliseconds

# === Storage Configuration ===
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent
RECORDINGS_FOLDER = BACKEND_DIR / 'recordings'
RECORDINGS_FOLDER.mkdir(parents=True, exist_ok=True)

# === Performance and Processing Flags ===
ASYNC_AI_PROCESSING = os.getenv('ASYNC_AI_PROCESSING', 'true').lower() == 'true'  # AI background processing
USE_FALLBACK_QUESTIONS = os.getenv('USE_FALLBACK_QUESTIONS', 'true').lower() == 'true'

# === Conversational AI Settings ===
AI_QUESTION_TIMEOUT = float(os.getenv('AI_QUESTION_TIMEOUT', 2.5))  # Seconds to wait for AI question
THINKING_PAUSE_MIN = float(os.getenv('THINKING_PAUSE_MIN', 0.8))   # Seconds before next question (min)
THINKING_PAUSE_MAX = float(os.getenv('THINKING_PAUSE_MAX', 1.5))   # Seconds before next question (max)
USE_ACKNOWLEDGMENTS = os.getenv('USE_ACKNOWLEDGMENTS', 'true').lower() == 'true'

# Acknowledgments pool (used if enabled)
ACKNOWLEDGMENTS = [
    "Interesting, let me think about that...",
    "I see, that's helpful...",
    "Got it, thanks for sharing...",
    "That makes sense...",
    "Okay, let me consider this...",
    "Hmm, interesting perspective...",
    "I'm following, give me a moment...",
    "That's insightful...",
    "Let me dig deeper into that...",
    "Alright, I understand..."
]

# === NLP Enhancement Settings ===
USE_NLP_ANALYSIS = os.getenv('USE_NLP_ANALYSIS', 'true').lower() == 'true'
MIN_ANSWER_LENGTH_FOR_NLP = int(os.getenv('MIN_ANSWER_LENGTH_FOR_NLP', 20))  # Minimum words for NLP analysis
TECH_DEPTH_THRESHOLD = int(os.getenv('TECH_DEPTH_THRESHOLD', 3))  # Tech terms to trigger depth questions

# === Question Complexity Multipliers ===
# Affects AI timeout multiplier for question generation
QUESTION_COMPLEXITY = {
    'early': 1.0,      # Questions 1-2
    'middle': 1.2,     # Questions 3-7
    'late': 1.5,       # Questions 8+
    'deep_dive': 1.8   # Follow-up depth questions
}

# === Retry and Circuit Breaker Settings ===
MAX_AI_RETRIES = int(os.getenv('MAX_AI_RETRIES', 3))
RETRY_BASE_DELAY = float(os.getenv('RETRY_BASE_DELAY', 1.0))

CIRCUIT_BREAKER_THRESHOLD = int(os.getenv('CIRCUIT_BREAKER_THRESHOLD', 5))
CIRCUIT_BREAKER_TIMEOUT = int(os.getenv('CIRCUIT_BREAKER_TIMEOUT', 60))  # seconds

# === Cleanup Scheduler Settings ===
ENABLE_CLEANUP_SCHEDULER = os.getenv('ENABLE_CLEANUP_SCHEDULER', 'true').lower() == 'true'
CLEANUP_INTERVAL_SECONDS = int(os.getenv('CLEANUP_INTERVAL_SECONDS', 300))
MAX_STREAM_IDLE_SECONDS = int(os.getenv('MAX_STREAM_IDLE_SECONDS', 300))

# === Path Security ===
ALLOWED_VIDEO_EXTENSIONS = ['.webm', '.mp4', '.mkv']
MAX_FILENAME_LENGTH = int(os.getenv('MAX_FILENAME_LENGTH', 255))

# === Feature Flags ===
USE_REDIS = os.getenv('USE_REDIS', 'false').lower() == 'true'
ENABLE_JSON_VALIDATION = os.getenv('ENABLE_JSON_VALIDATION', 'true').lower() == 'true'

