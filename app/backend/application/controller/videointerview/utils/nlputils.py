"""
NLP utilities for analyzing candidate answers and generating context-aware follow-ups
"""
import logging
import re
from typing import Dict, List, Set
from collections import Counter

logger = logging.getLogger(__name__)

# Lazy imports for performance
_nltk_initialized = False
_spacy_nlp = None

def initialize_nlp():
    """Lazy initialization of NLP libraries"""
    global _nltk_initialized, _spacy_nlp
    
    if _nltk_initialized and _spacy_nlp:
        return True
    
    try:
        # NLTK
        import nltk
        from nltk.sentiment import SentimentIntensityAnalyzer
        _nltk_initialized = True
        
        # Spacy (optional, fallback to simple tokenization)
        try:
            import spacy
            _spacy_nlp = spacy.load("en_core_web_sm")
            logger.info("✓ NLP initialized with spaCy")
        except:
            logger.warning("spaCy not available, using basic NLP")
            _spacy_nlp = None
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize NLP: {e}")
        return False


class AnswerAnalyzer:
    """Analyzes candidate answers using NLP techniques"""
    
    # Technical term categories
    TECH_TERMS = {
        'languages': ['python', 'javascript', 'java', 'typescript', 'go', 'rust', 'c++', 'ruby', 'php'],
        'frameworks': ['react', 'vue', 'angular', 'django', 'flask', 'fastapi', 'express', 'spring', 'rails'],
        'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'dynamodb'],
        'devops': ['docker', 'kubernetes', 'aws', 'azure', 'gcp', 'jenkins', 'ci/cd', 'terraform'],
        'concepts': ['api', 'rest', 'graphql', 'microservices', 'algorithm', 'cache', 'queue', 'async'],
        'testing': ['test', 'testing', 'unittest', 'pytest', 'jest', 'tdd', 'integration', 'e2e']
    }
    
    # Confidence indicators
    CONFIDENT_MARKERS = ['definitely', 'absolutely', 'certainly', 'clearly', 'obviously', 'always', 'exactly']
    UNCERTAIN_MARKERS = ['maybe', 'perhaps', 'possibly', 'probably', 'think so', 'not sure', 'might', 'could be']
    
    # Problem-solving indicators
    PROBLEM_WORDS = ['problem', 'issue', 'bug', 'challenge', 'difficult', 'error', 'failed', 'struggled']
    SOLUTION_WORDS = ['solved', 'fixed', 'resolved', 'debugged', 'optimized', 'improved', 'refactored']
    
    # Collaboration indicators
    TEAM_WORDS = ['team', 'collaborated', 'pair', 'reviewed', 'discussed', 'meeting', 'colleague']
    
    def __init__(self):
        initialize_nlp()
    
    def analyze(self, answer: str) -> Dict:
        """
        Comprehensive answer analysis
        Returns dict with metrics and insights
        """
        if not answer or len(answer.strip()) < 10:
            return self._get_default_analysis()
        
        answer_lower = answer.lower()
        words = self._tokenize(answer)
        
        analysis = {
            'word_count': len(words),
            'tech_density': self._calculate_tech_density(answer_lower),
            'tech_categories': self._identify_tech_categories(answer_lower),
            'confidence_level': self._detect_confidence(answer_lower),
            'mentions_problem_solving': self._detect_problem_solving(answer_lower),
            'mentions_teamwork': self._detect_teamwork(answer_lower),
            'answer_depth': self._calculate_depth(words, answer_lower),
            'key_entities': self._extract_entities(answer),
            'sentiment': self._analyze_sentiment(answer),
            'question_type_hint': self._suggest_question_type(answer_lower, words)
        }
        
        return analysis
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple word tokenization"""
        # Remove punctuation and split
        words = re.findall(r'\b\w+\b', text.lower())
        return [w for w in words if len(w) > 2]
    
    def _calculate_tech_density(self, text: str) -> int:
        """Count technical terms mentioned"""
        count = 0
        for category, terms in self.TECH_TERMS.items():
            for term in terms:
                # Use word boundary to avoid partial matches
                if re.search(rf'\b{term}\b', text):
                    count += 1
        return count
    
    def _identify_tech_categories(self, text: str) -> List[str]:
        """Identify which tech categories are mentioned"""
        categories = []
        for category, terms in self.TECH_TERMS.items():
            if any(re.search(rf'\b{term}\b', text) for term in terms):
                categories.append(category)
        return categories
    
    def _detect_confidence(self, text: str) -> str:
        """Detect confidence level from language markers"""
        confident_count = sum(1 for marker in self.CONFIDENT_MARKERS if marker in text)
        uncertain_count = sum(1 for marker in self.UNCERTAIN_MARKERS if marker in text)
        
        if uncertain_count > confident_count:
            return 'uncertain'
        elif confident_count > 0:
            return 'confident'
        return 'neutral'
    
    def _detect_problem_solving(self, text: str) -> bool:
        """Check if answer discusses problem-solving"""
        problem_mentions = sum(1 for word in self.PROBLEM_WORDS if word in text)
        solution_mentions = sum(1 for word in self.SOLUTION_WORDS if word in text)
        return (problem_mentions + solution_mentions) >= 2
    
    def _detect_teamwork(self, text: str) -> bool:
        """Check if answer mentions collaboration"""
        return any(word in text for word in self.TEAM_WORDS)
    
    def _calculate_depth(self, words: List[str], text: str) -> str:
        """Estimate answer depth based on length and complexity"""
        word_count = len(words)
        
        # Check for depth indicators
        has_example = any(phrase in text for phrase in ['for example', 'such as', 'like when', 'instance'])
        has_metrics = bool(re.search(r'\d+%|\d+x faster|\d+ times', text))
        has_comparison = any(word in text for word in ['versus', 'compared to', 'better than', 'instead of'])
        
        depth_score = 0
        if word_count > 50:
            depth_score += 1
        if has_example:
            depth_score += 1
        if has_metrics:
            depth_score += 1
        if has_comparison:
            depth_score += 1
        
        if depth_score >= 3:
            return 'deep'
        elif depth_score >= 1:
            return 'moderate'
        return 'shallow'
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract key entities (technologies, tools, concepts)"""
        entities = []
        
        # Use spaCy if available
        if _spacy_nlp:
            try:
                doc = _spacy_nlp(text[:500])  # Limit length for performance
                entities = [ent.text for ent in doc.ents if ent.label_ in ['PRODUCT', 'ORG', 'GPE']]
            except:
                pass
        
        # Fallback: extract capitalized words (likely proper nouns)
        if not entities:
            entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        return list(set(entities))[:5]  # Top 5 unique entities
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment (positive/negative/neutral)"""
        try:
            from nltk.sentiment import SentimentIntensityAnalyzer
            sia = SentimentIntensityAnalyzer()
            scores = sia.polarity_scores(text)
            
            if scores['compound'] >= 0.05:
                return 'positive'
            elif scores['compound'] <= -0.05:
                return 'negative'
            return 'neutral'
        except:
            # Fallback: simple keyword matching
            positive_words = ['good', 'great', 'excellent', 'love', 'enjoyed', 'success']
            negative_words = ['bad', 'difficult', 'hard', 'failed', 'struggled', 'problem']
            
            text_lower = text.lower()
            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)
            
            if pos_count > neg_count:
                return 'positive'
            elif neg_count > pos_count:
                return 'negative'
            return 'neutral'
    
    def _suggest_question_type(self, text: str, words: List[str]) -> str:
        """Suggest what type of follow-up would work best"""
        
        # Technical depth follow-up
        if len(words) < 30 and any(cat in ['languages', 'frameworks'] for cat in self._identify_tech_categories(text)):
            return 'technical_depth'
        
        # Problem-solving follow-up
        if self._detect_problem_solving(text):
            return 'problem_solving_depth'
        
        # Team/collaboration follow-up
        if self._detect_teamwork(text):
            return 'collaboration_depth'
        
        # Example request (answer is abstract)
        if len(words) < 40 and 'example' not in text:
            return 'request_example'
        
        # Reflection question (detailed answer)
        if len(words) > 80:
            return 'reflection'
        
        return 'general_followup'
    
    def _get_default_analysis(self) -> Dict:
        """Default analysis for short/empty answers"""
        return {
            'word_count': 0,
            'tech_density': 0,
            'tech_categories': [],
            'confidence_level': 'neutral',
            'mentions_problem_solving': False,
            'mentions_teamwork': False,
            'answer_depth': 'shallow',
            'key_entities': [],
            'sentiment': 'neutral',
            'question_type_hint': 'general_followup'
        }


# Singleton instance
_analyzer_instance = None

def get_answer_analyzer() -> AnswerAnalyzer:
    """Get singleton analyzer instance"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = AnswerAnalyzer()
    return _analyzer_instance

