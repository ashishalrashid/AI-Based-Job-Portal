User guide
==========

This guide explains the product from each persona’s point of view so non-developers understand what the system offers and how to interact with it today.

Accessing the app
-----------------

1. Start the stack (``docker compose up --build``) and wait for all services to show ``Up`` in ``docker compose ps``.
2. Visit `http://localhost:5173` for the UI and `http://localhost:8090` for the docs portal. The backend API stays inside the Docker network and is consumed via the frontend proxy (``/api``).
3. Choose the appropriate persona tab on the landing page (Applicant, HR, Organization) to reveal the tailored login/registration forms.

Applicant experience
--------------------

Registration and login
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - UI action
     - Screen
     - Outcome
   * - Click "Create account"
     - Landing page → Applicant tab
     - Opens a modal requesting email, password, name, phone, resume link.
   * - Submit application profile
     - Same modal
     - On success you’re redirected to ``/applicant-dashboard`` with a welcome toast.
   * - Existing login
     - ``/login`` → Applicant tab
     - Stores JWT cookie server-side and reloads saved applications instantly.

Dashboard tour
~~~~~~~~~~~~~~

* **Applications timeline** – visual chips showing each stage (`Submitted → Shortlisted → Interview → Offer`).
* **Upcoming interviews** – pulls from the interview API; clicking an entry reveals meeting details and video links.
* **Recommended jobs** – filters roles by skills/location; provides “Quick Apply” without leaving the dashboard.

Task checklist
~~~~~~~~~~~~~~

1. Browse ``/job-postings`` and apply using the “Apply” button; required fields are validated before submission.
2. Confirm the new application appears in ``/applications-review`` with status “Submitted”.
3. Navigate to ``/interview-slot-booking`` to pick a convenient time; the slot locks immediately.
4. When HR issues an offer, ``/offer-letter`` displays a download chip; click to retrieve the PDF.

HR experience
-------------

Login & landing
~~~~~~~~~~~~~~~

Select the HR tab on ``/login``. Successful authentication routes to ``/hr-dashboard`` and loads the recruiter profile (name, avatar, notification settings).

Dashboard widgets
~~~~~~~~~~~~~~~~~

* **Overview cards** – open requisitions, active interviews, offers pending approval, hires this quarter.
* **Candidates table** – supports column sorting, stage filters, and quick actions (shortlist, reject, schedule).
* **Upcoming meetings** – lists today’s interviews with join links and the ability to reassign interviewers.

Guided workflow
~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Step
     - Screen / route
     - Details
   * - Triage new applicants
     - ``/hr-dashboard`` → “Submitted” tab
     - Review resume preview, add private notes, and move to “Shortlisted”.
   * - Publish job
     - ``/create-job``
     - Fill job metadata, preview SEO summary, and hit “Publish” to push to the applicant portal.
   * - Manage interviews
     - ``/interview-details`` / ``/interview-slots``
     - Assign panelists, update agenda, resend invites.
   * - Generate offers
     - ``/offer-letter-editor``
     - Merge template fields (salary band, joining date, manager). Saving triggers PDF + email to the candidate.

Organization / admin experience
-------------------------------

* **Leadership dashboard** – ``/organization-dashboard`` outlines hiring velocity, pipeline health, onboarding blockers.
* **Staff management** – ``/staff`` lists employees with “Add Staff” and inline edit options; each change syncs with backend roster APIs.
* **Onboarding tracker** – ``/onboarding-tracker`` shows each hire’s checklist (documents, hardware, benefits). HR can mark steps complete, and candidates see updates on their dashboard.

Journeys for success & training teams
-------------------------------------

.. tip::
   Share these sequences with beta customers and enablement teams so they understand the entire lifecycle without reading implementation docs.

* **New company onboarding**
  1. Org admin logs in → adds HR/staff accounts via ``/add-staff`` wizard.
  2. HR team creates initial job postings.
  3. Applicants apply; org dashboard charts update automatically.
* **Offer to onboarding**
  1. HR generates an offer → applicant downloads the PDF instantly.
  2. Org admin opens ``/onboarding-tracker`` → tasks are auto-created for IT, HR, finance.
  3. As tasks complete, applicants see status badges flip from “Pending” to “Done”.

Support & troubleshooting
-------------------------

* Backend health: run `docker compose exec backend curl http://localhost:8086/` (inside the container) to verify the API if needed, or expose the port temporarily by adding a mapping in `docker-compose.yml`.
* Redis status: run ``redis-cli -h localhost -p 6379 ping`` for a quick connectivity check.
* Documentation portal: `http://localhost:8090` exposes both developer references and this user guide for cross-linking in onboarding materials.

Use this guide when onboarding customers, preparing demos, or writing release notes—the journeys mirror the live product and align with the backend “User-facing API flows” reference.

