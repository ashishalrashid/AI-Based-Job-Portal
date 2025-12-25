Data flow
=========

Authentication
--------------

* ``src/store/modules/auth.js`` stores the active user, role, and CSRF metadata.
* Login/registration forms call ``auth/login`` and ``auth/register`` actions; on success they persist the payload to both Vuex and ``localStorage``.
* The global router guard in ``src/router/index.js`` checks the store/``localStorage`` before entering protected routes such as ``/hr-dashboard``.

API client lifecycle
--------------------

The shared Axios client is defined in ``src/services/api.js``::

   const api = axios.create({
     baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
     headers: { 'Content-Type': 'application/json' },
     withCredentials: true,
   })

* Requests pass through an interceptor hook where additional headers can be injected.
* Responses that return ``401`` or ``422`` clear ``currentUser`` / ``userRole`` from ``localStorage``, allowing the router guard to redirect to ``/login``.
* By default the browser calls ``/api`` relative to the frontend host. Vite’s dev server proxies that path to ``http://backend:8086`` inside Docker, and you can override the URL with ``VITE_API_BASE_URL`` for non-Docker scenarios.

Store-driven workflow
---------------------

.. list-table::
   :header-rows: 1

   * - Module
     - Responsibilities
     - Consumed by
   * - ``modules/hr.js``
     - Candidate funnel, pipeline stats, hiring goals
     - ``HRDashboard.vue``, ``CandidatesTable.vue``
   * - ``modules/applicant.js``
     - Applications, interview slots, offer status
     - Applicant views under ``src/views/applicant``
   * - ``modules/organization.js``
     - Staff roster, onboarding progress
     - ``OrganizationDashboard.vue``, ``Staff.vue``
   * - ``modules/theme.js``
     - Theme tokens, dark/light flag
     - ``DashboardLayout.vue``, ``NavBar.vue``

Components dispatch store actions instead of calling Axios directly so caching and error handling remain centralised.

Component communication
-----------------------

* Layout primitives (``DashboardLayout.vue``, ``Sidebar.vue``, ``NavBar.vue``) emit events such as ``toggle-theme`` handled at the layout level before mutating the ``theme`` module.
* Visualization components like ``Overview.vue`` accept props rather than reading the store directly, keeping them pure and testable.
* ``CandidatesTable.vue`` emits ``sort-change``, ``filter-change``, and ``row-click``; parent views convert those into store actions or router pushes.

