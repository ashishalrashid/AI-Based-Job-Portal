"""
Retry utilities with exponential backoff
"""
import time
import logging
from typing import Callable, Any, Optional, Type
from functools import wraps

logger = logging.getLogger(__name__)


def exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for exponential backoff retry logic.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential calculation
        exceptions: Tuple of exceptions to catch and retry
    
    Example:
        @exponential_backoff(max_retries=3, base_delay=0.5)
        def flaky_api_call():
            # ... potentially failing code
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        logger.error(f"❌ {func.__name__} failed after {max_retries} attempts: {e}")
                        raise
                    
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    logger.warning(
                        f"⚠️ {func.__name__} attempt {attempt + 1} failed: {type(e).__name__}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)
            
            return None
        
        return wrapper
    return decorator


def retry_on_condition(
    condition: Callable[[Any], bool],
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: bool = True
):
    """
    Retry if result satisfies condition.
    
    Args:
        condition: Function that returns True if should retry
        max_retries: Maximum retry attempts
        delay: Base delay between retries
        backoff: Use exponential backoff if True
    
    Example:
        @retry_on_condition(lambda result: result is None, max_retries=3)
        def might_return_none():
            # ... code that might return None
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_retries):
                result = func(*args, **kwargs)
                
                if not condition(result):
                    return result
                
                if attempt < max_retries - 1:
                    wait_time = delay * (2 ** attempt) if backoff else delay
                    logger.warning(
                        f"⚠️ {func.__name__} result unsatisfactory (attempt {attempt + 1}). "
                        f"Retrying in {wait_time:.2f}s..."
                    )
                    time.sleep(wait_time)
            
            logger.error(f"❌ {func.__name__} failed condition after {max_retries} attempts")
            return result  # Return last attempt result
        
        return wrapper
    return decorator

