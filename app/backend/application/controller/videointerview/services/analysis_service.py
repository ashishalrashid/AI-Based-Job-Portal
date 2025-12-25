"""
Analysis Service - Real-time answer analysis (thread-safe)
"""
import logging
from typing import Dict
from threading import Lock

logger = logging.getLogger(__name__)

# Lock for session signal updates
_analysis_lock = Lock()


class AnalysisService:
    """Analyzes answers in real-time with thread safety"""
    
    def __init__(self):
        from .ai_service import get_ai_service
        self.ai_service = get_ai_service()
    
    def analyze_answer_quick(self, question: str, answer: str) -> Dict:
        """Quick answer analysis (lightweight)"""
        return self.ai_service.analyze_answer(question, answer)
    
    def update_session_signals(self, session, analysis: Dict) -> bool:
        """
        Update session with analysis signals (thread-safe).
        
        Args:
            session: InterviewSession object
            analysis: Analysis dict from AI
        
        Returns:
            bool: Success status
        """
        try:
            with _analysis_lock:
                # Add topics (thread-safe)
                if analysis.get("topics_mentioned"):
                    session.topics_covered.update(analysis["topics_mentioned"])
                
                # Update expertise level
                if analysis.get("suggests_level"):
                    self._update_expertise_level(session, analysis["suggests_level"])
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Error updating signals: {e}")
            return False
    
    @staticmethod
    def _update_expertise_level(session, suggested_level: str):
        """Update candidate expertise level with weighted average"""
        level_scores = {"junior": 1, "mid": 2, "senior": 3}
        
        if session.candidate_expertise_level == "unknown":
            session.candidate_expertise_level = suggested_level
        else:
            current = level_scores.get(session.candidate_expertise_level, 2)
            new = level_scores.get(suggested_level, 2)
            
            # Weighted average (current has 60% weight, new has 40%)
            avg = (current * 0.6) + (new * 0.4)
            
            if avg < 1.5:
                session.candidate_expertise_level = "junior"
            elif avg < 2.5:
                session.candidate_expertise_level = "mid"
            else:
                session.candidate_expertise_level = "senior"

