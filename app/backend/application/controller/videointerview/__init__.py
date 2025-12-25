"""
Video Interview Module - Main package initializer
"""
from flask import Blueprint
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Import routes blueprint
from .routes.interview_routes import interview_routes_bp

# Import socket initializer  
from .socket_handlers.interview_socket import init_socketio

# [FIX] Import the cleanup scheduler
from .cleanup_scheduler import start_cleanup_scheduler

# Create main blueprint (for backward compatibility)
video_interview_bp = interview_routes_bp

__all__ = ['video_interview_bp', 'init_socketio']

# [FIX] Start the scheduler (runs every 5 minutes by default)
start_cleanup_scheduler()
logger.info("🧹 Cleanup Scheduler Auto-Started")

logger.info("✅ Video Interview module initialized")

