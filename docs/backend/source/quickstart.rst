Backend quickstart
==================

This page mirrors everything that used to live in `app/backend/README.md` (now moved to `docs/backend/API.md`), so both newcomers and power users can get productive immediately.

Local setup (outside Docker)
----------------------------

1. Create and activate a virtualenv (Python 3.11 recommended)::

     python -m venv .venv
     source .venv/bin/activate

2. Install dependencies::

     pip install -r app/backend/requirements.txt

3. Run the app directly (Flask development server)::

     python app/backend/main.py

Docker workflow (recommended)
-----------------------------

The recommended way to run the backend is using Docker Compose. From the project root:

.. code-block:: bash

   docker compose up --build

This command starts all services:
- **Backend** - Flask API on port 8086
- **Frontend** - Vue.js SPA on port 5173
- **Redis** - Cache and task queue on port 6379
- **Documentation** - Sphinx docs on port 8090

The backend service:
- Automatically initializes the database and default roles on first startup
- Connects to Redis for caching and Celery task processing
- Exposes a health check endpoint at ``/health``
- Uses Gunicorn with 2 workers for production-ready performance

Environment variables can be set in ``docker-compose.yml`` to configure:
- Redis connection (defaults to ``redis://redis:6379``)
- Database location (persisted in Docker volume)
- Flask environment mode

Architecture diagrams
---------------------

Links from the legacy README are preserved here for reference:

* `Class diagram <https://drive.google.com/file/d/1PY9zYjBwsHSZ9kHZm41uIoUKGvXIuc-C/view>`__
* `ER diagram <https://drive.google.com/file/d/1uaieWI7njWXFMnriHEG8-WRkvzKjNwpw/view>`__

API catalogue overview
----------------------

Detailed, auto-generated descriptions live in :doc:`api`, but the following table captures the high-level coverage that used to be in the README.

.. list-table::
   :header-rows: 1

   * - Domain
     - Representative endpoints
     - Notes
   * - Health & Status
     - ``GET /health``
     - Public health check endpoint for monitoring and Docker health checks. Returns status, message, and timestamp.
   * - Authentication
     - ``POST /auth/register``, ``POST /auth/login``, ``POST /auth/logout``, ``POST /auth/forgot-password``, ``POST /auth/reset-password``
     - Role is inferred from email domain (``@company.com`` → admin, ``@hr.com`` → HR, everything else → applicant). Responses include the entity ID so the frontend can cache it.
   * - HR management
     - ``POST /hr``, ``GET /hr/<id>``, ``PUT /hr/<id>``, ``DELETE /hr/<id>``
     - Payloads include staff metadata (company, name, username, staff_id). All endpoints ensure company/HR IDs exist.
   * - Job lifecycle
     - ``POST /job`` (supports file upload or GDrive link), ``GET /job``, ``PUT /job/<id>``, ``DELETE /job/<id>``
     - Mirrors the hiring workflow (JD creation, updates, removal). Attachments must be either file uploads (multipart/form-data) or verified links.
   * - Applicants & applications
     - ``POST /applicant`` (multipart), ``GET /applicant/<id>``, ``POST /application``, ``PUT /application/<id>``
     - Applicants can be upserted; applications tie job + applicant IDs and track status, resume score, AI feedback.
   * - Interviews
     - ``POST /interview``, ``GET /interview/<id>``, ``PUT /interview/<id>``, ``DELETE /interview/<id>``
     - Schedules include slot data, interviewer/interviewee IDs, and optional recording URLs.
   * - Offer letters & onboarding
     - ``POST /offer_letter``, ``GET /offer_letter/<id>``, ``POST /onboarding``
     - Uses ReportLab to generate PDFs and seeds onboarding plans for org admins.

All of these routes now funnel into :doc:`user_flows`, which explains the same journeys from an end-user angle.

Frontend backlog notes (historical)
-----------------------------------

The original README listed two UI tweaks:

* Add a phone number field to both applicant and company login.
* Decide whether "Candidates" and "Onboardings" need to stay in the HR dashboard navigation.

Those items are tracked in the product backlog rather than the code repo, but the notes are recorded here for completeness.

Where to go next
----------------

* :doc:`architecture` for an in-depth view of the Flask app structure.
* :doc:`api` for auto-generated reference of every module/class.
* :doc:`user_flows` for persona-based walkthroughs (applicant, HR, organization).

