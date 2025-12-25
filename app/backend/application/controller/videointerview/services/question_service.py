"""
Question Service - Handles question generation with NLP-enhanced adaptive fallbacks
"""
import logging
from typing import Optional, Callable

logger = logging.getLogger(__name__)

class QuestionService:
    """Manages question generation with intelligent fallback strategy"""
    
    # Instant fallback questions (last resort)
    FALLBACK_QUESTIONS = [
        "Tell me about a recent project you're proud of. What was your role and what challenges did you overcome?",
        "Describe a technical problem you solved recently. Walk me through your approach.",
        "How do you stay updated with new technologies and best practices in your field?",
        "Tell me about a time you had to collaborate with a difficult team member. How did you handle it?",
        "What's your approach to writing maintainable, scalable code? Give me a specific example.",
        "Describe a situation where you had to learn a new technology quickly. How did you approach it?",
        "Tell me about a mistake you made in your code. How did you discover and fix it?",
        "What's your process for debugging a complex issue? Walk me through a recent example.",
        "How do you handle code reviews? What do you look for when reviewing others' code?",
        "Tell me about a time you had to make a technical decision with incomplete information."
    ]
    
    def __init__(self):
        from .ai_service import get_ai_service
        self.ai_service = get_ai_service()
        logger.info(f"✅ QuestionService initialized with AI service: {self.ai_service is not None}")
    
    def generate_first_question(self, session) -> str:
        """Generate opening question with company and candidate context. Uses AI with timeout fallback."""
        
        # ✅ Get comprehensive company and candidate information
        candidate_bg = getattr(session, 'candidate_background', {}) or {}
        company_name = candidate_bg.get('company_name') or candidate_bg.get('company') or 'our company'
        company_info = candidate_bg.get('company_info', {}) or {}
        candidate_name = candidate_bg.get('name') or 'you'
        candidate_skills = candidate_bg.get('skills', [])
        candidate_experience = candidate_bg.get('experience') or candidate_bg.get('years_of_experience') or ''
        candidate_resume = candidate_bg.get('resume_summary') or candidate_bg.get('resume_text') or ''
        candidate_experiences = candidate_bg.get('experiences', [])
        job_desc = getattr(session, 'job_description', '') or ''
        
        # Extract company from job description if not in candidate background
        if not company_name or company_name == 'our company':
            import re
            company_match = re.search(r'at\s+([A-Z][a-zA-Z\s&]+)', job_desc, re.IGNORECASE)
            if company_match:
                company_name = company_match.group(1).strip()
        
        # Build context strings
        company_context = f"Company: {company_name}"
        if company_info.get('description'):
            company_context += f" ({company_info.get('description')[:150]}...)"
        if company_info.get('industry'):
            company_context += f" - Industry: {company_info.get('industry')}"
        
        candidate_context = f"Candidate: {candidate_name}"
        if candidate_skills:
            candidate_context += f"\nSkills: {', '.join(candidate_skills[:6])}"
        if candidate_experience:
            candidate_context += f"\nExperience: {candidate_experience}"
        if candidate_resume:
            candidate_context += f"\nResume highlights: {candidate_resume[:300]}..."
        if candidate_experiences:
            recent_exp = candidate_experiences[0] if candidate_experiences else {}
            if recent_exp.get('position'):
                candidate_context += f"\nCurrent role: {recent_exp.get('position')} at {recent_exp.get('company', '')}"
        
        prompt = f"""You are conducting an interview for {company_name} for the position of {session.job_title}.

{company_context}

{candidate_context}

Job Description: {job_desc[:300] if job_desc else 'Full-stack development role'}

Generate a warm, engaging opening question that:
1. Makes the candidate comfortable
2. References {company_name} and the {session.job_title} role specifically
3. Mentions their background from their resume ({', '.join(candidate_skills[:2]) if candidate_skills else 'their experience'}) when relevant
4. Assesses their background naturally
5. Reveals their experience level
6. Shows you've reviewed their resume and are interested in their specific background

Return ONLY the question (1-2 sentences)."""
        
        fallback = f"Welcome! I'd love to hear about your background. What draws you to this {session.job_title} role at {company_name}, and what recent projects are you most proud of?"
        
        question = self.ai_service.generate_question(prompt, fallback)
        logger.info(f"First question: {question[:80]}...")
        return question
    
    def generate_next_question(self, session, previous_answer: str) -> str:
        """
        Generate the next interview question based on conversation history.
        This is the main method called by socket handlers.
        """
        try:
            # Validate answer
            if not previous_answer or len(previous_answer.strip()) < 5:
                logger.warning("Short/empty answer, using instant fallback")
                return self.get_instant_fallback(session.question_count + 1)
            
            # Try adaptive followup (includes AI generation)
            logger.info(f"Generating question #{session.question_count + 1}")
            question = self.generate_adaptive_followup(session, previous_answer)
            
            if question:
                return question
            
            # Final fallback
            return self.get_instant_fallback(session.question_count + 1)
            
        except Exception as e:
            logger.error(f"Error generating next question: {e}", exc_info=True)
            return self.get_instant_fallback(session.question_count + 1)
    
    def get_instant_fallback(self, question_number: int) -> str:
        """Get instant fallback question (no AI delay)"""
        idx = (question_number - 1) % len(self.FALLBACK_QUESTIONS)
        return self.FALLBACK_QUESTIONS[idx]
    
    def generate_adaptive_followup(self, session, previous_answer: str) -> str:
        """
        Generate AI-powered adaptive follow-up question.
        ✅ FIXED: Now actually calls AI service first!
        """
        try:
            # Validate answer
            if not previous_answer or len(previous_answer) < 10:
                logger.warning("Answer too short for AI generation")
                return self.get_instant_fallback(session.question_count + 1)
            
            # ✅ STEP 1: TRY AI GENERATION FIRST (Gemini)
            if self.ai_service:
                try:
                    prompt = self._build_question_prompt(session, previous_answer)
                    logger.info(f"🤖 Calling AI service for question #{session.question_count + 1}")
                    
                    # Get fallback ready in case AI fails
                    fallback = self._generate_keyword_based(session, previous_answer)
                    
                    # ✅ CALL AI SERVICE
                    ai_question = self.ai_service.generate_question(prompt, fallback)
                    
                    if ai_question and len(ai_question) > 10:
                        logger.info(f"✅ AI generated: {ai_question[:80]}...")
                        return ai_question
                    else:
                        logger.warning("⚠️ AI returned empty/short question, using fallback")
                        
                except Exception as e:
                    logger.error(f"❌ AI generation failed: {e}")
            else:
                logger.warning("⚠️ AI service not available")
            
            # ✅ STEP 2: TRY NLP-ENHANCED GENERATION (Optional)
            try:
                from ..config import USE_NLP_ANALYSIS, MIN_ANSWER_LENGTH_FOR_NLP
                from ..utils.nlp_utils import get_answer_analyzer
                
                if USE_NLP_ANALYSIS and len(previous_answer.split()) >= MIN_ANSWER_LENGTH_FOR_NLP:
                    analyzer = get_answer_analyzer()
                    analysis = analyzer.analyze(previous_answer)
                    logger.info(f"📊 NLP Analysis: {analysis}")
                    
                    question = self._generate_from_analysis(analysis, session, previous_answer)
                    if question:
                        logger.info("✅ Using NLP-generated question")
                        return question
            except ImportError:
                logger.debug("NLP module not available (this is okay)")
            except Exception as e:
                logger.debug(f"NLP analysis skipped: {e}")
            
            # ✅ STEP 3: KEYWORD-BASED FALLBACK
            logger.info("Using keyword-based generation")
            return self._generate_keyword_based(session, previous_answer)
            
        except Exception as e:
            logger.error(f"Error in adaptive followup: {e}", exc_info=True)
            return self._generate_keyword_based(session, previous_answer)
    
    def _generate_from_analysis(self, analysis: dict, session, answer: str) -> Optional[str]:
        """Generate question based on NLP analysis"""
        
        question_type = analysis.get('question_type_hint')
        confidence = analysis.get('confidence_level')
        depth = analysis.get('answer_depth')
        tech_density = analysis.get('tech_density', 0)
        tech_categories = analysis.get('tech_categories', [])
        
        # Handle uncertain candidates gently
        if confidence == 'uncertain':
            gentle_questions = [
                "I sense some uncertainty. What aspects would you like to explore more deeply?",
                "Let's break that down. What part are you most confident about?",
                "That's okay. Can you walk me through your thought process step by step?"
            ]
            return gentle_questions[session.question_count % len(gentle_questions)]
        
        # Technical depth questions
        if question_type == 'technical_depth' or tech_density >= 3:
            if 'databases' in tech_categories:
                return "You mentioned database work. Can you explain how you designed the schema and handled performance?"
            elif 'frameworks' in tech_categories:
                return "Tell me more about your architecture. Why did you choose that framework over alternatives?"
            elif 'devops' in tech_categories:
                return "Walk me through your deployment process. How do you handle rollbacks and monitoring?"
            else:
                return "That's quite technical. Can you break down the architecture and trade-offs you considered?"
        
        # Problem-solving depth
        if question_type == 'problem_solving_depth' or analysis.get('mentions_problem_solving'):
            if 'solved' in answer.lower() or 'fixed' in answer.lower():
                return "How did you identify the root cause? What debugging strategies did you use?"
            else:
                return "What alternatives did you consider? How did you decide on your approach?"
        
        # Collaboration depth
        if question_type == 'collaboration_depth' or analysis.get('mentions_teamwork'):
            return "Tell me about a time you disagreed with a teammate on a technical decision. How did you resolve it?"
        
        # Request examples (shallow answers)
        if question_type == 'request_example' or depth == 'shallow':
            return "Can you give me a specific example where you applied that? Walk me through the details."
        
        # Reflection (detailed answers)
        if question_type == 'reflection' or depth == 'deep':
            return "Looking back, what would you do differently? What did that experience teach you?"
        
        return None  # Fall through to keyword-based
    
    def _generate_keyword_based(self, session, answer: str) -> str:
        """Fallback keyword-based question generation"""
        answer_lower = answer.lower()
        
        # Technical implementation
        if any(word in answer_lower for word in ['built', 'developed', 'created', 'implemented', 'designed', 'coded']):
            questions = [
                "What was the most challenging technical aspect of that?",
                "What technologies did you choose and why?",
                "How did you ensure code quality and maintainability?",
                "What performance optimizations did you implement?"
            ]
            return questions[session.question_count % len(questions)]
        
        # Team/collaboration
        if any(word in answer_lower for word in ['team', 'collaborated', 'worked with', 'colleagues', 'pair']):
            questions = [
                "How did you handle coordination within the team?",
                "Tell me about a disagreement you had with a teammate. How did you resolve it?",
                "What's your approach to code reviews with team members?",
                "How do you ensure knowledge sharing in your team?"
            ]
            return questions[session.question_count % len(questions)]
        
        # Problem-solving
        if any(word in answer_lower for word in ['problem', 'issue', 'bug', 'challenge', 'difficult', 'error']):
            questions = [
                "Walk me through your debugging process. How did you approach it?",
                "What tools or techniques helped you solve it?",
                "How long did it take to resolve, and what did you learn?",
                "How did you prevent similar issues in the future?"
            ]
            return questions[session.question_count % len(questions)]
        
        # Learning/growth
        if any(word in answer_lower for word in ['learned', 'new', 'first time', 'unfamiliar', 'research']):
            questions = [
                "What resources did you use to get up to speed?",
                "How long did it take you to become comfortable with it?",
                "What would you teach someone else about it now?",
                "What surprised you most when learning it?"
            ]
            return questions[session.question_count % len(questions)]
        
        # Performance/optimization
        if any(word in answer_lower for word in ['performance', 'optimize', 'faster', 'slow', 'scale', 'efficient']):
            questions = [
                "What metrics did you use to measure the improvement?",
                "What trade-offs did you consider?",
                "How did you identify the bottleneck?",
                "How do you balance performance with maintainability?"
            ]
            return questions[session.question_count % len(questions)]
        
        # Testing
        if any(word in answer_lower for word in ['test', 'testing', 'qa', 'coverage', 'unit test']):
            questions = [
                "What's your testing strategy for a new feature?",
                "How do you balance test coverage with development speed?",
                "Tell me about a bug that slipped through testing.",
                "How do you approach integration testing?"
            ]
            return questions[session.question_count % len(questions)]
        
        # Default: reflection questions
        reflection_questions = [
            "What would you do differently if you faced that situation again?",
            "What did that experience teach you about software development?",
            "How has that influenced your approach to similar problems since?",
            "What advice would you give to someone in a similar situation?"
        ]
        return reflection_questions[session.question_count % len(reflection_questions)]
    
    def generate_next_question_async(self, session, previous_answer: str, callback: Callable):
        """
        Generate next question asynchronously.
        Calls callback(question) when ready.
        """
        prompt = self._build_question_prompt(session, previous_answer)
        fallback = self.generate_adaptive_followup(session, previous_answer)
        
        # Start async generation
        self.ai_service.generate_question_async(prompt, callback, fallback)
    
    def _build_question_prompt(self, session, previous_answer: str) -> str:
        """Build smart prompt for next question with company and candidate context"""
        
        # Get recent context (last 2 exchanges)
        recent = []
        for ex in session.conversation_history[-2:]:
            recent.append(f"Q: {ex.get('question')}")
            recent.append(f"A: {ex.get('answer', '')[:200]}...")
        context = "\n".join(recent)
        
        # Get uncovered topics (with safe defaults)
        topics_covered = getattr(session, 'topics_covered', set())
        topics_to_cover = getattr(session, 'topics_to_cover', set())
        uncovered = topics_to_cover - topics_covered
        
        # ✅ Get comprehensive company and candidate information
        candidate_bg = getattr(session, 'candidate_background', {}) or {}
        company_name = candidate_bg.get('company_name') or candidate_bg.get('company') or 'our company'
        company_info = candidate_bg.get('company_info', {}) or {}
        candidate_name = candidate_bg.get('name') or 'the candidate'
        candidate_skills = candidate_bg.get('skills', [])
        candidate_experience = candidate_bg.get('experience') or candidate_bg.get('years_of_experience') or 'unknown'
        candidate_resume = candidate_bg.get('resume_summary') or candidate_bg.get('resume_text') or candidate_bg.get('background') or ''
        candidate_experiences = candidate_bg.get('experiences', [])
        candidate_educations = candidate_bg.get('educations', [])
        
        # Extract company info from job description if available
        job_desc = getattr(session, 'job_description', '') or ''
        if not company_name or company_name == 'our company':
            # Try to extract company name from job description
            import re
            company_match = re.search(r'at\s+([A-Z][a-zA-Z\s&]+)', job_desc, re.IGNORECASE)
            if company_match:
                company_name = company_match.group(1).strip()
        
        # Build company context
        company_context = f"Company: {company_name}"
        if company_info.get('description'):
            company_context += f"\nCompany Description: {company_info.get('description')[:200]}..."
        if company_info.get('industry'):
            company_context += f"\nIndustry: {company_info.get('industry')}"
        if company_info.get('company_size'):
            company_context += f"\nCompany Size: {company_info.get('company_size')}"
        
        # Build candidate context with resume and experience
        candidate_context = f"Candidate: {candidate_name}"
        if candidate_skills:
            candidate_context += f"\nSkills: {', '.join(candidate_skills[:8])}"
        if candidate_experience and candidate_experience != 'unknown':
            candidate_context += f"\nExperience: {candidate_experience}"
        if candidate_resume:
            candidate_context += f"\nResume Summary: {candidate_resume[:400]}..."
        if candidate_experiences:
            recent_exp = candidate_experiences[0] if candidate_experiences else {}
            if recent_exp.get('position'):
                candidate_context += f"\nCurrent/Recent Role: {recent_exp.get('position')} at {recent_exp.get('company', '')}"
        if candidate_educations:
            recent_ed = candidate_educations[0] if candidate_educations else {}
            if recent_ed.get('degree'):
                candidate_context += f"\nEducation: {recent_ed.get('degree')} in {recent_ed.get('field', '')}"
        
        return f"""You are conducting an interview for {company_name} for the position of {session.job_title}.

{company_context}

{candidate_context}

Job Description: {job_desc[:400] if job_desc else 'Full-stack development role'}

Progress: Question {session.question_count}/10
Topics covered: {', '.join(list(topics_covered)[:5]) if topics_covered else 'None yet'}
Topics needed: {', '.join(list(uncovered)[:3]) if uncovered else 'General assessment'}

Recent conversation:
{context}

Latest answer: "{previous_answer[:300]}..."

Generate the next question that:
- Is specific to {company_name} ({company_info.get('industry', 'technology company')}) and the {session.job_title} role
- References the candidate's resume, experience ({', '.join(candidate_skills[:3]) if candidate_skills else 'their background'}), and past work when relevant
- Explores their skills naturally based on their answer
- Digs deeper into what they mentioned, especially if it relates to their resume or experience
- Covers new ground related to the job requirements and company needs
- Is conversational, engaging, and personalized to this specific candidate

Return ONLY the question (1-2 sentences)."""
    
    def get_question_complexity(self, session) -> float:
        """
        Return AI timeout multiplier based on question complexity.
        Later questions need more thinking time.
        """
        try:
            from ..config import QUESTION_COMPLEXITY
            
            if session.question_count <= 2:
                return QUESTION_COMPLEXITY.get('early', 1.0)
            elif session.question_count >= 8:
                return QUESTION_COMPLEXITY.get('late', 1.5)
            else:
                return QUESTION_COMPLEXITY.get('middle', 1.2)
        except ImportError:
            # Config not available, use defaults
            if session.question_count <= 2:
                return 1.0
            elif session.question_count >= 8:
                return 1.5
            else:
                return 1.2


# Convenience function for backward compatibility
def get_question_service():
    """Get or create singleton QuestionService instance"""
    return QuestionService()

