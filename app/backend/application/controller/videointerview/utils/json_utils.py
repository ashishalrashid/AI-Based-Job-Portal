"""
JSON utilities with schema validation
"""
import json
import re
import logging
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Try to import jsonschema for validation
try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    logger.warning("jsonschema not installed, using basic validation only")


def extract_json_from_model_output(raw_text: str) -> str:
    """
    Extract JSON-like substring from model output using multiple strategies.

    Strategies (in order):
    1. If the full text is valid JSON, return it.
    2. Extract text inside triple-backtick fences (``` or ```json) and return it.
    3. Return the first balanced {...} block, if any.
    4. Return the first balanced [...] block, if any.
    5. Fallback: return '{}' (empty JSON object)

    This function *returns a string* which should then be passed to json.loads().
    """
    if not raw_text or not raw_text.strip():
        return "{}"

    text = raw_text.strip()

    # Strategy 1: Full text is valid JSON
    try:
        json.loads(text)
        return text
    except Exception:
        pass  # not a full valid JSON, proceed

    # Strategy 2: Triple-backtick fenced code block (``` or ```json)
    # Capture the content between fences (non-greedy)
    fence_pattern = re.compile(r"``````", re.IGNORECASE)
    m = fence_pattern.search(text)
    if m:
        candidate = m.group(1).strip()
        if candidate:
            return candidate

    # Helper: find first balanced block of the given type
    def extract_balanced_block(s: str, open_ch: str, close_ch: str) -> Optional[str]:
        depth = 0
        start = None
        for i, ch in enumerate(s):
            if ch == open_ch:
                if depth == 0:
                    start = i
                depth += 1
            elif ch == close_ch and depth > 0:
                depth -= 1
                if depth == 0 and start is not None:
                    return s[start : i + 1]
        return None

    # Strategy 3: balanced object {}
    obj_candidate = extract_balanced_block(text, "{", "}")
    if obj_candidate:
        return obj_candidate

    # Strategy 4: balanced array []
    arr_candidate = extract_balanced_block(text, "[", "]")
    if arr_candidate:
        return arr_candidate

    logger.debug("No JSON structure found in model output; returning empty JSON object")
    return "{}"


def _trim_non_json_edges(text: str) -> str:
    """
    Attempt to strip leading/trailing non-JSON characters to help parsing.
    This is a best-effort helper for retry attempts.
    """
    # Remove leading characters up to first { or [
    trimmed = re.sub(r'^[^\[\{]*', '', text, count=1)
    # Remove trailing characters after last } or ]
    trimmed = re.sub(r'[^\]\}]*$', '', trimmed, count=1)
    return trimmed.strip() or text


def safe_json_parse(text: str, fallback: dict = None, max_retries: int = 2) -> dict:
    """
    Safely parse JSON with fallback and limited retry logic.

    Approach:
    1. Try parsing the raw text directly (fast path).
    2. Extract candidate JSON using extract_json_from_model_output() and try parsing.
    3. On failure, perform small cleanups (trim edges, remove code fences/newlines) and retry up to max_retries.
    4. If all attempts fail, return the provided fallback (or {} if None).

    Returns:
        dict: parsed JSON object or the fallback
    """
    fallback = fallback or {}

    # Fast path: try parsing the entire text first
    try:
        parsed = json.loads(text)
        logger.debug("JSON parsed successfully from raw text (fast path)")
        return parsed
    except json.JSONDecodeError:
        pass
    except Exception as e:
        logger.warning("Unexpected error while parsing raw JSON: %s", e)

    attempt_text = text
    for attempt in range(1, max_retries + 1):
        try:
            candidate = extract_json_from_model_output(attempt_text)
            parsed = json.loads(candidate)
            logger.debug("JSON parsed successfully on attempt %d", attempt)
            return parsed
        except json.JSONDecodeError as e:
            logger.warning("JSON decode error on attempt %d: %s", attempt, e)
            # Log a truncated problematic snippet for debugging (do not log full user data in prod)
            logger.debug("Problematic input (truncated): %r", (attempt_text[:500] + "...") if len(attempt_text) > 500 else attempt_text)
            # Prepare for next attempt: do some cleanup and trimming
            if attempt < max_retries:
                # Remove code fences, collapse whitespace, and try trimming non-json edges
                attempt_text = re.sub(r'```(?:json)?', '', attempt_text, flags=re.IGNORECASE)
                attempt_text = attempt_text.replace('```', '')
                attempt_text = attempt_text.replace('\r', ' ').replace('\n', ' ')
                attempt_text = _trim_non_json_edges(attempt_text)
                # continue retry loop
        except Exception as e:
            logger.error("Unexpected error parsing JSON on attempt %d: %s", attempt, e)
            break

    logger.error("All JSON parsing attempts failed; returning fallback")
    return fallback


def validate_json_schema(data: dict, schema: dict) -> Tuple[bool, Optional[str]]:
    """
    Validate JSON dict against JSON Schema.

    Returns:
        (is_valid, error_message) — error_message is None when valid.
    """
    if not JSONSCHEMA_AVAILABLE:
        logger.debug("jsonschema not available; skipping validation")
        return True, None

    try:
        jsonschema.validate(instance=data, schema=schema)
        return True, None
    except jsonschema.ValidationError as e:
        return False, str(e)
    except Exception as e:
        logger.error("Schema validation error: %s", e)
        return False, str(e)


# Example schemas for common responses
QUESTION_SCHEMA = {
    "type": "object",
    "properties": {
        "question": {"type": "string", "minLength": 10, "maxLength": 500}
    },
    "required": ["question"]
}

ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "quality_score": {"type": "number", "minimum": 0, "maximum": 10},
        "depth": {"type": "string", "enum": ["shallow", "moderate", "deep"]},
        "topics_mentioned": {"type": "array", "items": {"type": "string"}},
        "suggests_level": {"type": "string", "enum": ["junior", "mid", "senior"]},
        "needs_followup": {"type": "boolean"}
    },
    "required": ["quality_score", "depth", "topics_mentioned", "suggests_level", "needs_followup"]
}

EVALUATION_SCHEMA = {
    "type": "object",
    "properties": {
        "overall_rating": {"type": "number", "minimum": 0, "maximum": 5},
        "ratings": {"type": "object"},
        "strengths": {"type": "array", "items": {"type": "string"}},
        "areas_of_concern": {"type": "array", "items": {"type": "string"}},
        "recommendation": {"type": "object"}
    },
    "required": ["overall_rating", "ratings", "recommendation"]
}


def parse_and_validate_json(text: str, schema: dict = None, fallback: dict = None) -> dict:
    """
    Parse JSON text and (optionally) validate against a schema.

    Args:
        text: The JSON text to parse.
        schema: Optional JSON Schema dict for validation.
        fallback: Fallback dict in case of parse or validation failure.

    Returns:
        Parsed and (if requested) validated JSON dict, or fallback.
    """
    fallback = fallback or {}
    parsed = safe_json_parse(text, fallback=fallback, max_retries=2)

    if JSONSCHEMA_AVAILABLE and schema:
        is_valid, error = validate_json_schema(parsed, schema)
        if not is_valid:
            logger.error("JSON validation failed: %s", error)
            return fallback

    return parsed

