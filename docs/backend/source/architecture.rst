Architecture overview
=====================

Entry point
-----------

The Flask app boots from ``app/backend/main.py``. The ``create_app`` factory wires:

* configuration from ``application.utils.config.LocalDevelopmentConfig``
* SQLAlchemy models in ``application.data.models`` via ``db``
* JWT, CORS, caching, and Flask-Security
* blueprints under ``application.controller`` (``auth``, ``job``, ``offer_letter``, etc.)

When the module runs as ``__main__`` it binds to ``0.0.0.0:8086``. In Docker, Gunicorn serves the WSGI app with 2 workers and proper timeout settings for production use.

The application automatically:
- Creates the database directory if it doesn't exist
- Initializes database tables using SQLAlchemy
- Creates default roles (applicant, admin, hr, company) on first startup
- Sets up CORS to allow requests from the frontend container

Data access
-----------

``application/data`` contains the persistence layer:

* ``database.py`` holds the SQLAlchemy instance shared across modules.
* ``models.py`` defines ``User``, ``Role``, ``Job``, ``Application`` and the relationships leveraged by the REST resources.
* ``data_access.py`` provides helper functions for complex querying.

Blueprints and REST resources
-----------------------------

The ``application/controller`` tree mirrors feature domains. Each sub-package exports a blueprint that is registered in ``main.register_routes``. The REST resources exposed via ``flask_restful.Api`` live under ``application/controller/apis``. For example:

* ``application/controller/apis/hr_apis.py`` exposes ``HRApi`` for CRUD on HR records.
* ``application/controller/apis/job_apis.py`` handles job postings and uses the job blueprint for HTML-rendered routes.
* ``offer_letter_apis.py`` calls into ``application.utils.pdf_utils.generate_offer_letter_pdf`` to render PDFs with ReportLab.

Utilities
---------

Supporting modules are grouped under ``application/utils``:

* ``config.py`` centralises environment-driven settings, including Redis/Celery URLs used by Docker.
* ``email_utils.py`` sends transactional messages through Flask-Mail.
* ``pdf_utils.py`` wraps ReportLab for offer-letter generation.
* ``validation.py`` contains shared validators for form inputs and payloads.

Background infrastructure
-------------------------

Celery and Redis endpoints are defined via configuration but tasks can be added under a future ``application/tasks`` module. Within Docker the ``redis`` service defined in ``docker-compose.yml`` supplies the broker/result backend, matching the defaults in ``LocalDevelopmentConfig``.

