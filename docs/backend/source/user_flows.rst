User-facing API flows
=====================

This section translates backend capabilities into the user journeys surfaced in the product. Each persona consumes a small slice of the API layer; the tables below show the routes, payloads, and expected responses so stakeholders (product, QA, integrators) can reason about behaviour without reading code.

Applicant journey
------------------

Registration & account lifecycle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Step
     - Endpoint
     - Request payload
     - Response excerpt
   * - Create account
     - ``POST /auth/register``
     - ``{"email": "...", "password": "...", "role": "applicant"}``
     - ``201`` + ``{"message": "Registered", "user": {...}}`` plus a JWT cookie that immediately authenticates the browser.
   * - Login
     - ``POST /auth/login``
     - ``{"email": "...", "password": "..."}``
     - ``200`` + cookie refresh and user profile for the Vue store.
   * - Forgot password
     - ``POST /auth/forgot-password``
     - ``{"email": "..."}``
     - ``202`` + email dispatch handled by ``application.utils.email_utils``.
   * - Reset password
     - ``POST /auth/reset-password``
     - link token + new password
     - ``200`` with confirmation; login required afterwards.

.. tip::
   Cookies are HTTP-only and scoped to ``/`` so the SPA does not manually manage tokens.

Applications & interviews
~~~~~~~~~~~~~~~~~~~~~~~~~

1. ``GET /job`` – fetch listings to render the job board.
2. ``POST /application`` – submits an application body containing resume link, cover letter, and referenced job ID.
3. ``GET /application`` – dashboard view lists every application with statuses (``submitted``, ``shortlisted``, ``interview``, ``offer``).
4. ``POST /interview`` – books a slot using ``{"application_id": 42, "slot_id": 17}``; validation ensures the slot is available.
5. ``PUT /applicant/<applicant_id>`` – update profile information. Note: Work experiences, education, and certifications should be managed via their respective DELETE/POST endpoints to prevent duplicates.
6. ``GET /offer_letter/<application_id>`` – once HR generates the offer, this streams the ReportLab PDF for download.

Status timeline emitted to the UI:

``submitted → shortlisted → interview scheduled → offer generated → onboarding``

HR journey
----------

Daily workflow checklist
~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Action
     - Endpoint(s)
     - Purpose
   * - Review new applicants
     - ``GET /applications?status=submitted``
     - Feeds candidate queue on `HRDashboard.vue`.
   * - Shortlist promising candidates
     - ``POST /shortlist`` with ``application_id`` and optional notes
     - Moves candidate to the “Shortlisted” tab and notifies the applicant.
   * - Schedule interviews
     - ``POST /interview`` (HR variant) with interviewer, slot, and location metadata
     - Blocks slot for all parties and mirrors to the Upcoming Meetings widget.
   * - Submit interview feedback
     - ``POST /interview/feedback/<interview_id>``
     - Changes interview status from `feedback_pending` to `completed`, allowing decision making.
   * - Publish / update roles
     - ``POST /job`` to create, ``PUT /job/<id>`` to update
     - Keeps the public job board in sync with staffing needs.
   * - Issue offers
     - ``POST /offer_letter`` with ``application_id``, ``salary``, ``joining_date``, ``benefits``
     - Triggers PDF generation, records the offer in the DB, and emails the applicant.

Service level targets (SLAs):

* **Response time** – endpoints respond within 1s under normal load thanks to caching and SQL indexes.
* **Audit** – key transitions log to ``application.controller.controllers.audit_event`` for future compliance.

Organization administrators
---------------------------

.. list-table::
   :header-rows: 1

   * - Scenario
     - Endpoint
     - Description
   * - Build onboarding plan
     - ``POST /onboarding``
     - Provide ``employee_id``, checklist items, due dates. Response returns plan ID used by dashboard widgets.
   * - Track onboarding progress
     - ``GET /onboarding/<id>``
     - Returns task completion percentages and outstanding documents for the tracker UI.
   * - Review staffing campaigns
     - ``GET /campaign``
     - Designed for leadership dashboards; surfaces channel performance and budget usage.
   * - Manage staff roster
     - ``GET/POST /staff`` (through organization blueprint)
     - CRUD endpoints backing the “Staff” view in the SPA.

Common behaviours
-----------------

* **Authentication:** All routes outside the allowlist in ``main.global_jwt_protect`` require a valid JWT cookie. Frontend consumers rely on automatic cookie forwarding (`withCredentials: true`).
* **Validation errors:** Controllers standardise errors via ``application.utils.validation`` and respond with a JSON payload ``{"errors": {...}}`` and HTTP ``422``.
* **Caching:** ``Flask-Caching`` decorates frequently accessed endpoints (e.g., job listings). Cached responses honour the same authentication/authorization rules.

How to use this section
-----------------------

* **Product / UX** – reference the tables when designing new screens so each button maps to an existing API.
* **QA** – treat the sequences as test plans; each step corresponds to a concrete HTTP call and expected status code.
* **Customer success** – share snippets with customers who integrate externally (e.g., pre-populating applications via API).

