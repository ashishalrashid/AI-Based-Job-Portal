"""
AI Service - Handles all Gemini API interactions with retries and circuit breaker
"""
import logging
import time
from typing import Optional, Dict, List
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

logger = logging.getLogger(__name__)

# Thread pool for async AI processing
_ai_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="AIService")


class CircuitBreaker:
    """Simple circuit breaker to prevent cascading failures"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def call_failed(self):
        """Record a failure"""
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.failures >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"⚠️ Circuit breaker OPEN after {self.failures} failures")
    
    def call_succeeded(self):
        """Record a success"""
        self.failures = 0
        self.state = "closed"
    
    def can_attempt(self) -> bool:
        """Check if we can attempt a call"""
        if self.state == "closed":
            return True
        
        if self.state == "open":
            # Check if timeout has passed
            if self.last_failure_time and (time.time() - self.last_failure_time) > self.timeout:
                self.state = "half-open"
                logger.info("🔄 Circuit breaker HALF-OPEN, attempting recovery")
                return True
            return False
        
        # half-open: allow one attempt
        return True


class AIService:
    """Handles all AI/Gemini interactions with timeout protection and retries"""
    
    def __init__(self):
        from ..config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TIMEOUT_SECONDS
        
        # ✅ PRIMARY MODEL + FALLBACK MODELS
        self.primary_model = GEMINI_MODEL
        self.fallback_models = [
            "gemini-2.0-flash-lite",
            "gemini-2.0-flash", 
            "gemini-2.5-flash-lite",
            "gemini-flash-latest",
            "gemini-pro-latest",
            "gemini-2.5-pro"
        ]
        
        self.timeout = GEMINI_TIMEOUT_SECONDS
        self.initialized = False
        self.circuit_breaker = CircuitBreaker(failure_threshold=20, timeout=30)
        
        if GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.initialized = True
                logger.info(f"✅ AI Service initialized - Primary: {self.primary_model}, Fallbacks: {self.fallback_models}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize AI service: {e}")
        else:
            logger.error("❌ GEMINI_API_KEY not found!")
    
    def _call_gemini_with_retry(self, prompt: str, timeout: int = None, max_retries: int = 3) -> Optional[str]:
        """
        Call Gemini API with retry logic, exponential backoff, AND model fallback.
        ✅ NEW: Tries multiple models if rate limited!
        """
        if not self.initialized:
            logger.error("AI Service not initialized")
            return None
        
        if not self.circuit_breaker.can_attempt():
            logger.warning("⚠️ Circuit breaker OPEN, skipping API call")
            return None
        
        if timeout is None:
            timeout = self.timeout
        
        # ✅ Build list of models to try
        models_to_try = [self.primary_model] + self.fallback_models
        
        # ✅ Try each model
        for model_name in models_to_try:
            logger.info(f"🔄 Trying model: {model_name}")
            
            for attempt in range(max_retries):
                try:
                    def _call():
                        try:
                            model = genai.GenerativeModel(model_name)
                            response = model.generate_content(prompt)
                            return getattr(response, "text", None) or ""
                        except Exception as e:
                            error_msg = str(e)
                            error_type = type(e).__name__
                            
                            # ✅ Check if it's a rate limit error
                            if "ResourceExhausted" in error_type or "quota" in error_msg.lower() or "429" in error_msg:
                                logger.warning(f"⚠️ {model_name} quota exhausted: {error_type}")
                                raise  # Re-raise to try next model
                            
                            logger.error(f"Gemini API error with {model_name} (attempt {attempt + 1}): {error_type}")
                            return None
                    
                    # Use thread pool to enforce timeout
                    future = _ai_executor.submit(_call)
                    result = future.result(timeout=timeout)
                    
                    if result:
                        self.circuit_breaker.call_succeeded()
                        logger.info(f"✅ SUCCESS with model: {model_name}")
                        return result
                    else:
                        self.circuit_breaker.call_failed()
                    
                except FuturesTimeoutError:
                    logger.warning(f"⏰ AI call timed out after {timeout}s with {model_name} (attempt {attempt + 1})")
                    self.circuit_breaker.call_failed()
                    
                except Exception as e:
                    error_msg = str(e)
                    
                    # ✅ If quota exhausted, skip to next model immediately
                    if "ResourceExhausted" in type(e).__name__ or "quota" in error_msg.lower():
                        logger.warning(f"❌ {model_name} quota exhausted, trying next model...")
                        self.circuit_breaker.call_failed()
                        break  # Skip retries for this model, try next one
                    
                    logger.error(f"Error with {model_name} (attempt {attempt + 1}): {type(e).__name__}")
                    self.circuit_breaker.call_failed()
                
                # Exponential backoff between retries (for same model)
                if attempt < max_retries - 1:
                    backoff = (2 ** attempt) * 0.5  # 0.5s, 1s, 2s
                    logger.info(f"🔄 Retrying {model_name} in {backoff}s...")
                    time.sleep(backoff)
            
            # After all retries for this model failed, try next model
            logger.warning(f"❌ All retries failed for {model_name}, trying next model...")
        
        # All models exhausted
        logger.error(f"❌ ALL MODELS FAILED after trying: {models_to_try}")
        return None
    
    def generate_question_async(self, prompt: str, callback, fallback: str):
        """
        Generate question asynchronously using executor pool (not raw threads).
        """
        def _generate():
            result = self._call_gemini_with_retry(prompt, timeout=10, max_retries=2)
            if result:
                question = self._clean_question(result)
                if question:
                    callback(question)
        
        # Use executor instead of manual threading.Thread
        _ai_executor.submit(_generate)
        return fallback
    
    def generate_question(self, prompt: str, fallback: str = "") -> str:
        """Generate question synchronously with timeout"""
        result = self._call_gemini_with_retry(prompt, timeout=8, max_retries=2)
        if result:
            question = self._clean_question(result)
            return question if question else fallback
        return fallback
    
    # ... rest of your methods remain the same ...
    def analyze_answer(self, question: str, answer: str) -> Dict:
        """Analyze answer quality (quick version)"""
        prompt = f"""Analyze this interview answer briefly.

Question: {question}
Answer: {answer}

Return JSON:
{{
    "quality_score": 7,
    "depth": "moderate",
    "topics_mentioned": ["python"],
    "suggests_level": "mid",
    "needs_followup": false
}}"""
        
        result = self._call_gemini_with_retry(prompt, timeout=5, max_retries=1)
        if result:
            from ..utils.json_utils import safe_json_parse
            return safe_json_parse(result, self._get_default_analysis())
        return self._get_default_analysis()
    
    def generate_evaluation(self, session_data: Dict, timeout: int = 30) -> Dict:
        """Generate final evaluation with extended timeout - LENIENT: Only fail if absolutely terrible"""
        conversation = session_data.get('conversation', '')
        metadata = session_data.get('metadata', {})
        
        prompt = f"""Evaluate this interview. Be LENIENT and GENEROUS. Only recommend "Fail" if the candidate's answers are ABSOLUTELY TERRIBLE (completely wrong, no knowledge, incoherent, or clearly unqualified).

IMPORTANT EVALUATION CRITERIA:
- PASS if candidate shows ANY reasonable understanding, effort, or relevant experience
- PASS if answers are partially correct or show learning potential
- PASS if candidate communicates clearly even if technical depth is limited
- PASS if candidate shows enthusiasm, willingness to learn, or cultural fit
- Only FAIL if answers are completely wrong, show zero knowledge, are incoherent, or demonstrate clear unqualification

Conversation:
{conversation}

Duration: {metadata.get('duration_minutes', 0):.1f} minutes
Questions: {metadata.get('questions_asked', 0)}

Return JSON with:
- ratings: technical_skills, communication, problem_solving, cultural_fit (each with stars 1-5 and description)
- overall_rating: number 1-5
- strengths: array of positive points
- areas_of_concern: array of concerns (only if significant)
- recommendation: {{"decision": "Pass" or "Fail" (only fail if absolutely terrible), "reasoning": "explanation", "confidence": "percentage"}}

Remember: Be generous. Default to PASS unless answers are clearly terrible."""
        
        result = self._call_gemini_with_retry(prompt, timeout=timeout, max_retries=2)
        if result:
            from ..utils.json_utils import safe_json_parse
            evaluation = safe_json_parse(result, self._get_default_evaluation(session_data))
            # ✅ Ensure lenient default - if decision is unclear, default to Pass
            if evaluation.get('recommendation', {}).get('decision', '').lower() not in ['pass', 'fail']:
                evaluation['recommendation'] = {
                    'decision': 'Pass',
                    'reasoning': 'Interview completed. Candidate showed engagement and effort.',
                    'confidence': 'Medium (70%)'
                }
            return evaluation
        return self._get_default_evaluation(session_data)
    
    @staticmethod
    def _clean_question(text: str) -> str:
        """Clean question text from AI output"""
        if not text:
            return ""
        
        question = text.strip().strip('"').strip()
        
        # Remove common prefixes
        for prefix in ["Question:", "Q:", "Next Question:", "Interview Question:"]:
            if question.startswith(prefix):
                question = question.replace(prefix, "", 1).strip()
        
        # Handle accidental JSON wrapping
        if question.startswith("{") or question.startswith("["):
            return ""
        
        # Truncate if too long
        if len(question) > 500:
            question = question[:500].rsplit(".", 1)[0] + "?"
        
        return question
    
    @staticmethod
    def _get_default_analysis() -> Dict:
        """Default analysis when AI fails"""
        return {
            "quality_score": 5,
            "depth": "moderate",
            "topics_mentioned": [],
            "suggests_level": "mid",
            "needs_followup": False
        }
    
    @staticmethod
    def _get_default_evaluation(session_data: Dict) -> Dict:
        """Default evaluation when AI fails - LENIENT: Default to Pass"""
        metadata = session_data.get('metadata', {})
        return {
            "ratings": {
                "technical_skills": {"stars": 3, "description": "Average technical performance"},
                "communication": {"stars": 3, "description": "Clear communication"},
                "problem_solving": {"stars": 3, "description": "Adequate problem-solving"},
                "cultural_fit": {"stars": 3, "description": "Reasonable fit"}
            },
            "overall_rating": 3.0,
            "strengths": ["Completed interview", "Engaged with questions"],
            "areas_of_concern": [],
            "recommendation": {
                "decision": "Pass",
                "reasoning": "Interview completed. Candidate showed engagement and effort. Manual review recommended for final decision.",
                "confidence": "Medium (70%)"
            },
            "interview_metadata": metadata
        }


# Singleton instance
_ai_service_instance = None

def get_ai_service() -> AIService:
    """Get singleton AI service instance"""
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance

