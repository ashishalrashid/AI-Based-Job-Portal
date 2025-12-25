#import env variables.
from dotenv import load_dotenv, find_dotenv
import os

dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
else:
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

import os
import logging
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify, send_from_directory
from flask_migrate import Migrate
from flask_socketio import SocketIO
from application.auth.auth import auth_bp

# API Imports
from application.controller.apis.user_apis import UserAPI
from application.controller.apis.hr_apis import HRApi
from application.controller.apis.job_apis import JobAPI
from application.controller.apis.applicant_apis import ApplicantAPI
from application.controller.apis.application_apis import ApplicationApi
from application.controller.apis.offer_letter_apis import OfferLetterApi
from application.controller.apis.interview_apis import ScheduleInterviewResource, InterviewByApplication, InterviewApi, HRInterviewList, HRInterviewDetail
from application.controller.apis.onboarding_apis import OnboardingApi

# Controller Blueprints Imports
from application.controller.controllers import main_bp
from application.controller.company.controllers import company_bp
from application.controller.offer_letter.controllers import offer_bp
from application.controller.onboarding.controllers import onboarding_bp
from application.controller.interview.controllers import interview_bp
from application.controller.job.controllers import job_bp
from application.controller.applications.controllers import applications_bp
from application.controller.applicant.controllers import applicant_bp
from application.controller.shortlist.controllers import shortlist_bp
from application.controller.applicant.dashboard import applicant_dashboard_bp
from application.controller.applicant.profile import applicant_profile_bp
from application.controller.resume_parser.parser_service import resume_parser_bp

from application.utils.config import LocalDevelopmentConfig

from flask_restful import Api
from application.data.database import db
from flask_security import Security, SQLAlchemySessionUserDatastore
from application.data.models import *
from flask_cors import CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request
from flask_caching import Cache
from flask_mail import Mail
from celery import Celery

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_roles():
    """Initialize default roles in the database if they don't exist"""
    try:
        existing_roles = Role.query.all()
        if existing_roles:
            logger.info(f"Database already has {len(existing_roles)} roles, skipping...")
            return

        logger.info("Creating initial roles...")
        roles = [
            {'name': 'applicant', 'description': 'Job applicant'},
            {'name': 'admin', 'description': 'Administrator'},
            {'name': 'hr', 'description': 'Human Resources'},
            {'name': 'company', 'description': 'Company Representative'}
        ]

        for role_data in roles:
            role = Role(name=role_data['name'], description=role_data['description'])
            db.session.add(role)

        db.session.commit()
        logger.info("✅ Database initialized successfully with roles!")

    except Exception as e:
        logger.error(f"❌ Error initializing roles: {e}")
        db.session.rollback()
        raise

def make_celery(app):
    """Create and configure Celery instance"""
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

def register_routes(app):
    """Register all Flask blueprints"""
    
    app.register_blueprint(offer_bp, url_prefix='/offer')
    app.register_blueprint(company_bp, url_prefix='/company')
    app.register_blueprint(onboarding_bp, url_prefix='/onboarding')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(interview_bp, url_prefix='/interview')
    app.register_blueprint(job_bp, url_prefix='/job')
    app.register_blueprint(applications_bp, url_prefix='/applications')
    app.register_blueprint(applicant_bp, url_prefix='/applicant')
    app.register_blueprint(shortlist_bp, url_prefix='/shortlist')
    app.register_blueprint(applicant_dashboard_bp, url_prefix='/applicant_dashboard')
    app.register_blueprint(applicant_profile_bp, url_prefix='/applicant_profile')
    app.register_blueprint(resume_parser_bp, url_prefix='/resumeparser')
    app.register_blueprint(main_bp)

    # 🚨 FIXED: Video interview blueprint with graceful error handling
    try:
        from application.controller.videointerview.routes import interview_routes_bp
        app.register_blueprint(interview_routes_bp, url_prefix='/video-interview')
        logger.info("✅ Video interview blueprint registered successfully!")
    except ImportError as e:
        logger.error(f"❌ Failed to import video interview blueprint: {e}")
        logger.info("⏭️ Continuing without video interview blueprint - other routes work")
    except Exception as e:
        logger.error(f"❌ Error registering video interview blueprint: {e}")

def register_static_routes(app):
    """Register routes to serve static files (uploads, recordings, etc.)"""
    
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        """Serve uploaded files (resumes, cover letters, JDs)"""
        upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
        logger.info(f"📁 Serving upload: {filename} from {upload_folder}")
        
        try:
            return send_from_directory(upload_folder, filename)
        except FileNotFoundError:
            logger.error(f"❌ File not found: {filename}")
            return jsonify({"error": "File not found"}), 404
    
    @app.route('/recordings/<path:filename>')
    def serve_recording(filename):
        """Serve video interview recordings"""
        recordings_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'recordings')
        logger.info(f"🎥 Serving recording: {filename} from {recordings_folder}")
        
        try:
            return send_from_directory(recordings_folder, filename)
        except FileNotFoundError:
            logger.error(f"❌ Recording not found: {filename}")
            return jsonify({"error": "Recording not found"}), 404

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(LocalDevelopmentConfig)

    # Initialize database
    db.init_app(app)
    api = Api(app)

    # Initialize Flask-Mail
    mail = Mail(app)
    logger.info("✅ Flask-Mail initialized successfully!")

    # Flask-Security setup
    user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
    security = Security(app, user_datastore)

    # Register all blueprints
    register_routes(app)
    
    # ✅ Register static file serving routes
    register_static_routes(app)

    # CORS configuration for REST endpoints (both local and Docker)
    cors = CORS(app, 
        origins=[
            "http://localhost:5173", 
            "http://localhost:5174", 
            "http://127.0.0.1:5173", 
            "http://127.0.0.1:5174",
            "http://frontend:5173"  # Docker internal
        ], 
        supports_credentials=True
    )

    # JWT setup
    jwt = JWTManager(app)
    migrate = Migrate(app, db)

    # ✅ SocketIO with video-optimized config
    socketio = SocketIO(
        app, 
        cors_allowed_origins=[
            "http://localhost:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://frontend:5173"
        ],
        async_mode='eventlet',
        logger=True, 
        engineio_logger=True,
        ping_timeout=120,
        ping_interval=20,
        allow_upgrades=True,
        manage_session=False,
        max_http_buffer_size=1e8,
        transports=['websocket', 'polling']
    )
    logger.info("✅ SocketIO initialized with eventlet mode!")

    # 🚨 FIXED: Video interview SocketIO handlers with graceful error handling
    try:
        from application.controller.videointerview.socket_handlers import init_socketio
        init_socketio(socketio)
        logger.info("✅ Video interview SocketIO handlers registered!")
    except ImportError as e:
        logger.error(f"❌ Error importing video interview SocketIO: {e}")
        logger.info("⏭️ SocketIO handlers skipped - basic SocketIO still works")
    except Exception as e:
        logger.error(f"❌ Error initializing video interview SocketIO: {e}")

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user['id']

    @jwt.additional_claims_loader
    def add_claims_to_access_token(identity):
        return {'role': identity['role']}

    @app.before_request
    def global_jwt_protect():
        """Protect all routes with JWT except public paths"""
        public_paths = [
            "/auth/login",
            "/auth/register",
            "/auth/forgot-password",
            "/auth/reset-password",
            "/health",
            "/",
            "/favicon.ico",
            "/resumeparser/health",
            "/video-interview/health",
            "/video-interview/start",
            "/socket.io/",
            "/uploads/",
            "/recordings/",
        ]

        # Allow static files
        if request.path.startswith("/static"):
            return

        # Allow public routes
        if any(request.path.startswith(p) for p in public_paths):
            return

        # Require JWT for all other routes
        try:
            verify_jwt_in_request(optional=False)
        except Exception as e:
            return jsonify({
                "error": "Unauthorized",
                "message": str(e)
            }), 401

    with app.app_context():
        try:
            db_dir = app.config.get('SQLITE_DB_DIR')
            if db_dir:
                os.makedirs(os.path.abspath(db_dir), exist_ok=True)
            db.create_all()
            initialize_roles()
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")

        # Create recordings directory
        try:
            recordings_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                'recordings'
            )
            os.makedirs(recordings_dir, exist_ok=True)
        except Exception as e:
            logger.warning(f"⚠️ Could not create recordings directory: {e}")

    cache = Cache(app)

    return app, api, cache, mail, socketio

# Create app and get instances
app, api, cache, mail, socketio = create_app()

celery = make_celery(app)
logger.info("✅ Celery initialized!")

# Register REST API resources
api.add_resource(HRApi, '/hr', '/hr/<int:hr_id>')
api.add_resource(JobAPI, '/job', '/job/<int:job_id>')
api.add_resource(ApplicantAPI, '/applicant', '/applicant/<int:applicant_id>')
api.add_resource(ApplicationApi, '/application', '/application/<int:application_id>')
api.add_resource(OfferLetterApi, '/offer_letter', '/offer_letter/<int:offer_letter_id>')
api.add_resource(InterviewApi, '/interview', '/interview/<int:interview_id>')
api.add_resource(OnboardingApi, '/onboarding', '/onboarding/<int:onboarding_id>')
api.add_resource(HRInterviewList, '/api/hr/interviews/<int:company_id>')
api.add_resource(HRInterviewDetail, '/api/hr/interview/<string:session_id>')
api.add_resource(UserAPI, '/api/user', '/api/user/<int:user_id>')
api.add_resource(ScheduleInterviewResource, '/api/interview/schedule/<int:application_id>/<int:hr_id>')
api.add_resource(InterviewByApplication, '/api/interview/by-application/<int:application_id>')

if __name__ == '__main__':
    app.debug = True

    logger.info("=" * 70)
    logger.info("🚀 HR MANAGEMENT SYSTEM - STARTING (Eventlet Mode)")
    logger.info("=" * 70)
    
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=8086, 
        debug=True,
        use_reloader=False, 
        log_output=True
    )

