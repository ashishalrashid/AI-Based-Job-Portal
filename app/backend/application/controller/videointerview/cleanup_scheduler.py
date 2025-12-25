"""
Background cleanup scheduler for orphaned resources
"""
from __future__ import annotations

import logging
import time
import threading
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class CleanupScheduler:
    """
    Background janitor for cleaning orphaned streams and sessions.

    Usage:
        sched = CleanupScheduler(interval_seconds=300)
        sched.start()
        ...
        sched.stop()
    """

    def __init__(self, interval_seconds: int = 300):
        """
        Args:
            interval_seconds: How often to run cleanup (default 5 minutes)
        """
        self.interval_seconds = int(interval_seconds)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start the cleanup scheduler (no-op if already running)."""
        with self._lock:
            if self.is_running():
                logger.warning("⚠️ Cleanup scheduler already running")
                return

            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._run_loop, daemon=True, name="CleanupScheduler"
            )
            self._thread.start()
            logger.info("✅ Cleanup scheduler started (interval: %ds)", self.interval_seconds)

    def stop(self, join_timeout: float = 5.0) -> None:
        """Signal the scheduler to stop and wait (briefly) for the thread to finish."""
        with self._lock:
            if not self.is_running():
                logger.debug("Cleanup scheduler not running; stop() is a no-op")
                return

            self._stop_event.set()
            if self._thread is not None:
                self._thread.join(timeout=join_timeout)
                if self._thread.is_alive():
                    logger.warning("⚠️ Cleanup scheduler thread did not exit within timeout")
            self._thread = None
            logger.info("🛑 Cleanup scheduler stopped")

    def is_running(self) -> bool:
        """Return True if the scheduler is currently running."""
        return self._thread is not None and not self._stop_event.is_set()

    def _run_loop(self) -> None:
        """Main loop that periodically runs cleanup tasks until stopped."""
        try:
            while not self._stop_event.is_set():
                try:
                    self._run_cleanup()
                except Exception as e:
                    logger.exception("❌ Error in cleanup loop: %s", e)

                # Wait for either the interval to pass or a stop event to be set
                # We break the total interval into one-second waits so stop is responsive.
                waited = 0
                while waited < self.interval_seconds and not self._stop_event.is_set():
                    remaining = min(1, self.interval_seconds - waited)
                    self._stop_event.wait(timeout=remaining)
                    waited += remaining
        except Exception as e:
            logger.exception("❌ Unexpected error in cleanup scheduler thread: %s", e)

    def _run_cleanup(self) -> None:
        """Run all cleanup tasks and log a summary."""
        logger.debug("🧹 Running scheduled cleanup at %s", datetime.utcnow().isoformat())

        cleaned_streams = 0
        cleaned_sessions = 0

        # Cleanup transcription streams (if available)
        try:
            # Import inside function to avoid hard import-time dependency
            from videointerview.services.transcription_service import get_transcription_service
        except Exception as e:
            logger.debug("Transcription service not available for cleanup: %s", e)
            get_transcription_service = None

        if get_transcription_service:
            try:
                transcription = get_transcription_service()
                # defensive: check attribute exists and callable
                if transcription and hasattr(transcription, "cleanup_inactive_streams"):
                    # caller may expect a count; default to 0 if None/invalid
                    result = transcription.cleanup_inactive_streams(max_idle_seconds=300)
                    cleaned_streams = int(result or 0)
                else:
                    logger.debug("Transcription service present but no cleanup_inactive_streams() method")
            except Exception as e:
                logger.exception("❌ Error cleaning transcription streams: %s", e)

        # Cleanup old sessions (in-memory store) — optional
        try:
            from videointerview.models.session_store import cleanup_old_sessions
        except Exception as e:
            logger.debug("Session store cleanup not available: %s", e)
            cleanup_old_sessions = None

        if cleanup_old_sessions:
            try:
                # If cleanup_old_sessions returns an integer count, capture it.
                result = cleanup_old_sessions(max_age_hours=24)
                cleaned_sessions = int(result or 0)
            except Exception as e:
                logger.exception("❌ Error cleaning old sessions: %s", e)

        if cleaned_streams > 0 or cleaned_sessions > 0:
            logger.info(
                "🧹 Cleanup complete: %d streams cleaned, %d sessions cleaned",
                cleaned_streams,
                cleaned_sessions,
            )
        else:
            logger.debug("🧹 Cleanup complete: nothing to clean")


# Module-level scheduler and lock to prevent races when starting/stopping
_scheduler: Optional[CleanupScheduler] = None
_scheduler_lock = threading.Lock()


def start_cleanup_scheduler(interval_seconds: int = 300) -> CleanupScheduler:
    """Start (or return) the global cleanup scheduler in a thread-safe manner."""
    global _scheduler
    with _scheduler_lock:
        if _scheduler is None:
            _scheduler = CleanupScheduler(interval_seconds=interval_seconds)
            _scheduler.start()
        else:
            # If scheduler exists, allow updating interval (optional)
            if _scheduler.interval_seconds != int(interval_seconds):
                logger.info("Updating cleanup interval from %d to %d", _scheduler.interval_seconds, interval_seconds)
                _scheduler.interval_seconds = int(interval_seconds)
        return _scheduler


def stop_cleanup_scheduler() -> None:
    """Stop and clear the global cleanup scheduler."""
    global _scheduler
    with _scheduler_lock:
        if _scheduler:
            _scheduler.stop()
            _scheduler = None

