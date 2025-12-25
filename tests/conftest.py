import os
import sys
import types
import traceback
import importlib
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Try multiple possible paths for Docker and local environments
APP_BACKEND_APPLICATION = os.path.join(PROJECT_ROOT, "app", "backend", "application")
if not os.path.isdir(APP_BACKEND_APPLICATION):
    # Try Docker path: /app/backend/application
    APP_BACKEND_APPLICATION = os.path.join(PROJECT_ROOT, "backend", "application")
if not os.path.isdir(APP_BACKEND_APPLICATION):
    # Try absolute Docker path
    APP_BACKEND_APPLICATION = "/app/backend/application"
if not os.path.isdir(APP_BACKEND_APPLICATION):
    raise RuntimeError(
        f"Expected directory not found. Tried:\n"
        f"  {os.path.join(PROJECT_ROOT, 'app', 'backend', 'application')}\n"
        f"  {os.path.join(PROJECT_ROOT, 'backend', 'application')}\n"
        f"  /app/backend/application\n"
        f"PROJECT_ROOT: {PROJECT_ROOT}\n"
        f"Ensure your code is at app/backend/application/..."
    )

if "application" not in sys.modules:
    application_mod = types.ModuleType("application")
    application_mod.__path__ = [APP_BACKEND_APPLICATION]
    sys.modules["application"] = application_mod

# Try multiple possible paths for Docker and local environments
BACKEND_DIR = os.path.join(PROJECT_ROOT, "app", "backend")
if not os.path.isdir(BACKEND_DIR):
    BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if not os.path.isdir(BACKEND_DIR):
    BACKEND_DIR = "/app/backend"
if BACKEND_DIR not in sys.path and os.path.isdir(BACKEND_DIR):
    sys.path.insert(0, BACKEND_DIR)

CONFIG_MODULE_NAME = "application.utils.config"
if CONFIG_MODULE_NAME not in sys.modules:
    cfg_mod = types.ModuleType(CONFIG_MODULE_NAME)

    class LocalDevelopmentConfig:
        DEBUG = False
        TESTING = True
        SECRET_KEY = "test-secret-key"
        JWT_SECRET_KEY = "test-jwt-secret"
        SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SQLITE_DB_DIR = None
        CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
        CACHE_TYPE = "null"  # Disable caching in tests to avoid warnings

    cfg_mod.LocalDevelopmentConfig = LocalDevelopmentConfig
    sys.modules[CONFIG_MODULE_NAME] = cfg_mod

# Try multiple import paths for Docker and local environments
try:
    from app.backend.main import create_app
except ImportError:
    try:
        # Docker path: /app/backend/main.py
        from main import create_app
    except ImportError:
        try:
            # Alternative: direct import
            import sys
            sys.path.insert(0, BACKEND_DIR)
            from main import create_app
        except Exception as exc:
            print("ERROR importing create_app")
            print(f"Tried: app.backend.main, main (from {BACKEND_DIR})")
            traceback.print_exc()
            raise

_db = None
db_import_attempts = [
    "application.data.database",              
    "app.backend.application.data.database",   
]

for modname in db_import_attempts:
    try:
        mod = importlib.import_module(modname)
        if hasattr(mod, "db"):
            _db = getattr(mod, "db")
            break
    except Exception:
        pass

if _db is None:
    raise ImportError(
        "Could not locate SQLAlchemy `db` object. Tried:\n  "
        + "\n  ".join(db_import_attempts)
        + "\nAdjust tests/conftest.py to point to the correct module if needed."
    )

@pytest.fixture(scope="session")
def app():
    """
    Create and configure the Flask app for tests.
    Handles create_app() returning either app or (app, api, cache).
    """
    result = create_app()
    app_obj = result[0] if isinstance(result, tuple) else result

    app_obj.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:"),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SQLITE_DB_DIR": None,
    })

    try:
        orig_register = app_obj.register_blueprint

        def _test_allow_register(bp, **options):
            try:
                return orig_register(bp, **options)
            except AssertionError as exc:
                msg = str(exc).lower()
                if "can no longer be called" in msg or "already handled its first request" in msg:
                    try:
                        app_obj._got_first_request = False
                    except Exception:
                        raise
                    return orig_register(bp, **options)
                raise

        app_obj.register_blueprint = _test_allow_register
    except Exception:
        pass

    with app_obj.app_context():
        try:
            if hasattr(_db, "init_app"):
                _db.init_app(app_obj)
        except Exception:
            pass

        try:
            _db.create_all()
        except Exception as e:
            print("\n\n=== FAILED: _db.create_all() in app fixture ===")
            traceback.print_exc()
            raise RuntimeError("Failed to create DB tables during test app setup") from e

    yield app_obj

    with app_obj.app_context():
        try:
            _db.session.remove()
        except Exception:
            pass
        try:
            _db.drop_all()
        except Exception:
            pass


@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        _db.drop_all()
        _db.create_all()
        yield _db
        try:
            _db.session.rollback()
        except Exception:
            pass
        _db.session.remove()


@pytest.fixture
def client(app, db):
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    from flask_jwt_extended import create_access_token

    def _make(role="admin", user_id=1):
        identity = {"id": user_id, "role": role}
        with app.app_context():
            token = create_access_token(identity=identity)
        return {"Authorization": f"Bearer {token}"}

    return _make


# Register Flask-RESTful resources for tests that need them
@pytest.fixture(scope="session", autouse=True)
def register_restful_resources(app):
    """Register Flask-RESTful API resources for testing"""
    from flask import Blueprint
    from flask_restful import Api as RestfulApi
    from application.controller.apis.applicant_apis import ApplicantAPI
    from application.controller.apis.application_apis import ApplicationApi
    from application.controller.apis.hr_apis import HRApi
    from application.controller.apis.job_apis import JobAPI
    from application.controller.apis.offer_letter_apis import OfferLetterApi
    from application.controller.apis.interview_apis import InterviewApi
    from application.controller.apis.onboarding_apis import OnboardingApi
    
    # Register ApplicantAPI for test_applicant_apis.py
    test_applicant_bp = Blueprint("test_applicant_restful_bp", __name__)
    test_applicant_api = RestfulApi(test_applicant_bp)
    test_applicant_api.add_resource(ApplicantAPI, "/applicant", "/applicant/<int:applicant_id>")
    app.register_blueprint(test_applicant_bp, url_prefix="/_test_applicant")
    
    # Register ApplicationApi for test_application_apis.py
    test_application_bp = Blueprint("test_application_restful_bp", __name__)
    test_application_api = RestfulApi(test_application_bp)
    test_application_api.add_resource(ApplicationApi, "/application", "/application/<int:application_id>")
    app.register_blueprint(test_application_bp, url_prefix="/_test_application")
    
    # Register HRApi for test_hr_apis.py
    test_hr_bp = Blueprint("test_hr_restful_bp", __name__)
    test_hr_api = RestfulApi(test_hr_bp)
    test_hr_api.add_resource(HRApi, "/hr", "/hr/<int:hr_id>")
    app.register_blueprint(test_hr_bp, url_prefix="/_test_hr")
    
    yield

