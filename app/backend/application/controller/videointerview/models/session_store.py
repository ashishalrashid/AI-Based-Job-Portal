"""
Redis Session Store - Production-Ready with Reverse Mapping

Critical fix: Early end for critical red flags...
"""
import json
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
import redis
from redis.connection import ConnectionPool
from .interview_session import InterviewSession

logger = logging.getLogger(__name__)


class RedisSessionStore:
    """Redis-backed session store with reverse mapping support"""

    def __init__(self, redis_url: str = "redis://localhost:6379/0", 
                 session_ttl_hours: int = 24, max_connections: int = 50):
        try:
            self.pool = ConnectionPool.from_url(
                redis_url,
                max_connections=max_connections,
                socket_timeout=5,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30
            )
            self.client = redis.Redis(
                connection_pool=self.pool,
                decode_responses=True
            )
            self.redis_client = self.client  # Keep backward compatibility
            self.session_ttl = timedelta(hours=session_ttl_hours)
            self.client.ping()
            logger.info(f"Redis initialized at {redis_url}")
        except Exception as e:
            logger.error(f"Redis Connection Error: {e}")
            raise

    def _key(self, session_id: str) -> str:
        """Generate key for session"""
        return f"session:{session_id}"

    def _meta_key(self, session_id: str) -> str:
        """Generate metadata key"""
        return f"interview:session:{session_id}:meta"

    def add(self, session: InterviewSession) -> bool:
        """
        Store session in Redis with proper serialization
        ✅ FIXED: Converts sets to lists and handles None values
        """
        try:
            # ✅ Convert sets to lists for Redis storage
            session_dict = {
                'session_id': session.session_id,
                'interview_id': session.interview_id,
                'job_title': session.job_title,
                'job_description': session.job_description,
                'candidate_background': session.candidate_background,
                'started_at': session.started_at.isoformat() if session.started_at else None,
                'last_active_at': session.last_active_at.isoformat() if session.last_active_at else None,
                'current_question': session.current_question,
                'question_count': session.question_count,
                'conversation_history': session.conversation_history,
                'is_ai_speaking': session.is_ai_speaking,
                'speech_mode': session.speech_mode,
                'topics_covered': list(session.topics_covered) if hasattr(session, 'topics_covered') else [],
                'topics_to_cover': list(session.topics_to_cover) if hasattr(session, 'topics_to_cover') else [],
                'candidate_expertise_level': getattr(session, 'candidate_expertise_level', 'unknown'),
                'interview_depth_level': getattr(session, 'interview_depth_level', 1),
                'red_flags': getattr(session, 'red_flags', []),
                'green_flags': getattr(session, 'green_flags', []),
                'recording_path': session.recording_path,
                'video_file': session.video_file,
                'audio_file': session.audio_file,
                'full_transcript': getattr(session, 'full_transcript', []),
                'current_transcript': getattr(session, 'current_transcript', ''),
                'technical_signals': getattr(session, 'technical_signals', []),
                'communication_signals': getattr(session, 'communication_signals', []),
                'problem_solving_signals': getattr(session, 'problem_solving_signals', [])
            }
            
            # Store as JSON string
            self.client.setex(
                self._key(session.session_id),
                int(self.session_ttl.total_seconds()),
                json.dumps(session_dict)
            )
            
            # ✅ Store reverse mapping: interview_id -> session_id
            if session.interview_id:
                reverse_key = f"interview:mapping:{session.interview_id}"
                self.client.setex(
                    reverse_key,
                    int(self.session_ttl.total_seconds()),
                    session.session_id
                )
            
            logger.info(f"✅ Session {session.session_id} stored in Redis")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add session: {e}", exc_info=True)
            return False

    def get(self, session_id: str) -> Optional[InterviewSession]:
        """
        Retrieve session from Redis with proper deserialization
        ✅ FIXED: Let from_dict() handle all conversions
        """
        try:
            data = self.client.get(self._key(session_id))
            if not data:
                logger.warning(f"⚠️ Session {session_id} not found in Redis")
                return None
            
            session_dict = json.loads(data)
            
            # ✅ Don't convert here - from_dict() will handle it
            # Just ensure lists are present for set conversion
            if 'topics_covered' not in session_dict:
                session_dict['topics_covered'] = []
            if 'topics_to_cover' not in session_dict:
                session_dict['topics_to_cover'] = []
            
            # ✅ Use from_dict() - it handles all conversions
            session = InterviewSession.from_dict(session_dict)
            logger.info(f"✅ Retrieved session {session_id} from Redis")
            return session
            
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}", exc_info=True)
            return None


    def add_session(self, session) -> bool:
        """Backward compatibility wrapper"""
        return self.add(session)

    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        """Backward compatibility wrapper"""
        return self.get(session_id)

    def get_session_by_interview_id(self, interview_id: int) -> Optional[InterviewSession]:
        """
        Get session by interview_id (O(1) lookup using reverse mapping)

        CRITICAL FIX: This uses a reverse mapping key stored when session is created:
        interview:mapping:{interview_id} -> session_id

        This eliminates the O(N) loop that was crashing the server under load.
        """
        try:
            reverse_key = f"interview:mapping:{interview_id}"
            session_id = self.client.get(reverse_key)

            if not session_id:
                logger.debug(f"No session found for interview_id: {interview_id}")
                return None

            # Get the actual session using O(1) lookup
            return self.get(session_id)

        except Exception as e:
            logger.error(f"Error getting session by interview_id {interview_id}: {e}")
            return None

    def session_exists(self, session_id: str) -> bool:
        """Check if session exists"""
        try:
            return self.client.exists(self._key(session_id)) > 0
        except Exception as e:
            logger.error(f"Error checking session existence: {e}")
            return False

    def remove_session(self, session_id: str) -> bool:
        """Remove session and its reverse mapping"""
        try:
            # Get session to find interview_id before deletion
            session = self.get(session_id)

            deleted = self.client.delete(self._key(session_id))

            # Remove reverse mapping if session was found
            if session and hasattr(session, 'interview_id') and session.interview_id:
                reverse_key = f"interview:mapping:{session.interview_id}"
                self.client.delete(reverse_key)
                logger.info(f"Removed reverse mapping for interview_id: {session.interview_id}")

            logger.info(f"Session {session_id} removed, deleted count: {deleted}")
            return deleted > 0

        except Exception as e:
            logger.error(f"Failed to remove session {session_id}: {e}")
            return False

    def get_all_sessions(self) -> Dict[str, InterviewSession]:
        """Get all sessions"""
        sessions = {}
        try:
            pattern = "session:*"
            keys = self.client.keys(pattern)

            for key in keys:
                # Extract session_id from key
                session_id = key.replace("session:", "")
                session = self.get(session_id)
                if session:
                    sessions[session_id] = session

            return sessions

        except Exception as e:
            logger.error(f"Failed to get all sessions: {e}")
            return sessions

    def health_check(self) -> bool:
        """Check Redis health"""
        try:
            return self.client.ping()
        except Exception:
            return False


# ============================================================================
# Module-level singleton and wrapper functions
# ============================================================================

_redis_store = None


def get_redis_store() -> RedisSessionStore:
    """Get or create Redis store singleton"""
    global _redis_store
    if _redis_store is None:
        from ..config import REDIS_URL, SESSION_TTL_HOURS
        _redis_store = RedisSessionStore(redis_url=REDIS_URL, session_ttl_hours=SESSION_TTL_HOURS)
    return _redis_store


# Create global session_store instance for convenience
session_store = get_redis_store()


def add_session(session) -> bool:
    """Module-level wrapper for add_session"""
    return session_store.add(session)


def get_session(session_id: str):
    """Module-level wrapper for get_session"""
    return session_store.get(session_id)


def get_session_by_interview_id(interview_id: int):
    """
    Module-level wrapper for get_session_by_interview_id
    CRITICAL FIX: O(1) lookup instead of O(N) loop
    """
    return session_store.get_session_by_interview_id(interview_id)


def session_exists(session_id: str) -> bool:
    """Module-level wrapper for session_exists"""
    return session_store.session_exists(session_id)


def remove_session(session_id: str) -> bool:
    """Module-level wrapper for remove_session"""
    return session_store.remove_session(session_id)


def get_all_sessions() -> Dict[str, InterviewSession]:
    """Module-level wrapper for get_all_sessions"""
    return session_store.get_all_sessions()

