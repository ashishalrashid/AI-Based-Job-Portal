"""
Evaluation Service - Generates final interview evaluation
"""
import logging
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)


class EvaluationService:
    """Handles final interview evaluation generation"""
    
    def __init__(self):
        from .ai_service import get_ai_service
        from ..models.session_store import get_session
        self.ai_service = get_ai_service()
    
    def generate_evaluation(self, session) -> Dict:
        """Generate comprehensive evaluation"""
        
        # Build conversation text
        conversation_lines = []
        for idx, ex in enumerate(session.conversation_history, 1):
            conversation_lines.append(f"Q{idx}: {ex.get('question')}")
            conversation_lines.append(f"A{idx}: {ex.get('answer')}")
        
        conversation_text = "\n\n".join(conversation_lines)
        
        # Build metadata
        metadata = {
            'duration_minutes': round(session.get_duration_minutes(), 1),
            'questions_asked': len(session.conversation_history),
            'topics_covered': list(session.topics_covered),
            'detected_level': session.candidate_expertise_level,
            'depth_achieved': session.interview_depth_level
        }
        
        # Prepare data for AI
        session_data = {
            'conversation': conversation_text,
            'metadata': metadata,
            'job_title': session.job_title,
            'job_description': session.job_description,
            'green_flags': session.green_flags[:5],
            'red_flags': session.red_flags[:5]
        }
        
        # Generate with AI (has timeout protection)
        logger.info(f"🧠 Generating evaluation for {session.session_id}...")
        evaluation = self.ai_service.generate_evaluation(session_data, timeout=30)
        
        # Ensure metadata is included
        evaluation['interview_metadata'] = metadata
        
        logger.info(f"✅ Evaluation complete: {evaluation.get('overall_rating', 'N/A')}/5")
        return evaluation
    
    def get_fallback_evaluation(self, session_id: str) -> Dict:
        """Get fallback evaluation when AI fails"""
        from ..models.session_store import get_session
        session = get_session(session_id)
        
        metadata = {}
        if session:
            metadata = {
                'duration_minutes': round(session.get_duration_minutes(), 1),
                'questions_asked': len(session.conversation_history),
                'topics_covered': list(session.topics_covered),
                'detected_level': session.candidate_expertise_level
            }
        
        return {
            "ratings": {
                "technical_skills": {"stars": 3, "description": "Average performance"},
                "communication": {"stars": 3, "description": "Clear communication"},
                "problem_solving": {"stars": 3, "description": "Adequate approach"},
                "cultural_fit": {"stars": 3, "description": "Reasonable fit"}
            },
            "overall_rating": 3.0,
            "strengths": ["Completed interview", "Engaged with questions"],
            "areas_of_concern": ["Manual review recommended"],
            "recommendation": {
                "decision": "Maybe",
                "reasoning": "Interview completed. Manual review needed.",
                "confidence": "Medium (65%)"
            },
            "interview_metadata": metadata
        }

