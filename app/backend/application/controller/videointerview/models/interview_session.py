"""
Interview Session Model - Pure data structure (Pickle-safe)
"""
import uuid
import os
from datetime import datetime, timezone
from typing import Set, List, Dict, Optional
import logging

from ..config import RECORDINGS_FOLDER
from ..utils.file_utils import create_session_directory

logger = logging.getLogger(__name__)


class InterviewSession:
    """
    Interview session state - PURE DATA, NO RESOURCES
    
    Design principles:
    - No file handles (pickle-safe for Redis)
    - Immutable identifiers
    - Serializable state only
    """
    
    def __init__(self, interview_id: int, job_title: str, job_description: str, 
        candidate_background: dict, session_id: str = None, recording_path: str = None):
        # Core identifiers (immutable)
        self.session_id = session_id if session_id else str(uuid.uuid4())
        self.interview_id = interview_id
        
        # ... (keep ALL your existing fields exactly the same) ...
        self.job_title = job_title
        self.job_description = job_description
        self.candidate_background = candidate_background
        self.started_at = datetime.now(timezone.utc)
        self.last_active_at = datetime.now(timezone.utc)
        self.current_question: Optional[str] = None
        self.question_count: int = 0
        self.conversation_history: List[Dict] = []
        self.is_ai_speaking: bool = False
        self.speech_mode: str = 'browser'
        self.topics_covered: Set[str] = set()
        self.topics_to_cover: Set[str] = self._extract_required_topics()
        self.candidate_expertise_level: str = "unknown"
        self.interview_depth_level: int = 1
        self.red_flags: List[str] = []
        self.green_flags: List[str] = []
        self.interview_ended: bool = False

        # ✅ FIXED: NO directory creation here!
        self.recording_path: Optional[str] = recording_path
        self.video_file: Optional[str] = None
        self.audio_file: Optional[str] = None
        
        if self.recording_path:
            self.video_file = os.path.join(self.recording_path, 'video_stream.webm')
            self.audio_file = os.path.join(self.recording_path, 'audio_stream.webm')

        
        self.full_transcript: List[str] = []
        self.current_transcript: str = ""
        self.technical_signals: List[str] = []
        self.communication_signals: List[str] = []
        self.problem_solving_signals: List[str] = []    

    def _extract_required_topics(self) -> Set[str]:
        """Extract key topics from job description"""
        topics = set()
        
        tech_keywords = [
            'python', 'javascript', 'react', 'vue', 'node', 'api', 'database',
            'sql', 'mongodb', 'docker', 'kubernetes', 'aws', 'azure', 'git',
            'testing', 'agile', 'microservices', 'architecture', 'security',
            'machine learning', 'data', 'algorithm', 'system design'
        ]
        
        desc_lower = (self.job_description or "").lower()
        for keyword in tech_keywords:
            if keyword in desc_lower:
                topics.add(keyword)
        
        # Core areas always included
        topics.update(['experience', 'projects', 'teamwork', 'challenges'])
        
        return topics
    
    def add_exchange(self, question: str, answer: str):
        """Add Q&A exchange to history"""
        exchange = {
            "question": question,
            "answer": answer,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "question_number": len(self.conversation_history) + 1
        }
        self.conversation_history.append(exchange)
        
        # Update transcript with better formatting
        question_num = exchange['question_number']
        self.full_transcript.append(f"AI (Q{question_num}): {question}")
        self.full_transcript.append(f"Candidate (A{question_num}): {answer}")
        
        # Update activity timestamp
        self.last_active_at = datetime.now(timezone.utc)

    
    def should_end(self) -> bool:
        """Check if interview should end"""
        from ..config import MAX_QUESTIONS, MAX_INTERVIEW_MINUTES
        
        # Duration check
        elapsed_minutes = (datetime.now(timezone.utc) - self.started_at).total_seconds() / 60
        
        # End conditions
        if len(self.conversation_history) >= MAX_QUESTIONS:
            return True
        
        if elapsed_minutes >= MAX_INTERVIEW_MINUTES:
            return True
        
        # Early end for critical red flags
        if len(self.red_flags) >= 5:
            logger.info("Ending early due to red flags")
            return True
        
        return False
    
    def get_duration_minutes(self) -> float:
        """Get interview duration in minutes"""
        return (datetime.now(timezone.utc) - self.started_at).total_seconds() / 60
    
    def touch(self):
        """Update last activity timestamp"""
        self.last_active_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> dict:
        """Serialize to dictionary for API responses and JSON storage"""
        return {
            "session_id": self.session_id,
            "interview_id": self.interview_id,
            "job_title": self.job_title,
            "job_description": self.job_description,
            "candidate_background": self.candidate_background,
            "started_at": self.started_at.isoformat(),
            "last_active_at": self.last_active_at.isoformat(),
            "current_question": self.current_question,
            "question_count": self.question_count,
            "conversation_history": self.conversation_history,
            "topics_covered": list(self.topics_covered),
            "topics_to_cover": list(self.topics_to_cover),
            "candidate_expertise_level": self.candidate_expertise_level,
            "interview_depth_level": self.interview_depth_level,
            "red_flags": self.red_flags,
            "green_flags": self.green_flags,
            "recording_path": self.recording_path,
            "video_file": self.video_file,
            "audio_file": self.audio_file,
            "full_transcript": self.full_transcript,
            "current_transcript": self.current_transcript,
            "technical_signals": self.technical_signals,
            "communication_signals": self.communication_signals,
            "problem_solving_signals": self.problem_solving_signals
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'InterviewSession':
        """Create InterviewSession instance from dictionary (e.g. after JSON deserialization)"""
        instance = cls(
            interview_id=data.get("interview_id"),
            job_title=data.get("job_title"),
            job_description=data.get("job_description"),
            candidate_background=data.get("candidate_background"),
            session_id=data.get("session_id"),           # ✅ PASS EXISTING ID
            recording_path=data.get("recording_path")    # ✅ PASS EXISTING PATH
        )
        
        # Hydrate ALL other fields (your complete existing logic)
        instance.started_at = datetime.fromisoformat(data["started_at"]) if data.get("started_at") else datetime.now(timezone.utc)
        instance.last_active_at = datetime.fromisoformat(data["last_active_at"]) if data.get("last_active_at") else datetime.now(timezone.utc)
        instance.current_question = data.get("current_question")
        instance.question_count = data.get("question_count", 0)
        instance.conversation_history = data.get("conversation_history", [])
        instance.topics_covered = set(data.get("topics_covered", []))
        instance.topics_to_cover = set(data.get("topics_to_cover", []))
        instance.candidate_expertise_level = data.get("candidate_expertise_level", "unknown")
        instance.interview_depth_level = data.get("interview_depth_level", 1)
        instance.red_flags = data.get("red_flags", [])
        instance.green_flags = data.get("green_flags", [])
        instance.video_file = data.get("video_file")
        instance.audio_file = data.get("audio_file")
        instance.full_transcript = data.get("full_transcript", [])
        instance.current_transcript = data.get("current_transcript", "")
        instance.technical_signals = data.get("technical_signals", [])
        instance.communication_signals = data.get("communication_signals", [])
        instance.problem_solving_signals = data.get("problem_solving_signals", [])
        
        return instance


