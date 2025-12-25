Architecture
============

Tooling
-------

* **Vite + Vue 3** power the SPA, configured via ``vite.config.js`` and bootstrapped in ``src/main.js``.
* **Vuex (Pinia-style modules)** live under ``src/store`` with domain-specific modules in ``src/store/modules``.
* **Vue Router** defines guarded routes inside ``src/router/index.js`` to separate HR, applicant, and organization flows.
* **Axios** centralises HTTP in ``src/services/api.js`` where cookies are forwarded to the backend API.

Directory tour
--------------

.. list-table::
   :header-rows: 1

   * - Path
     - Purpose
   * - ``src/views/hr/HRDashboard.vue``
     - HR landing page that composes analytics tiles, tables, and upcoming interviews through ``DashboardLayout``.
   * - ``src/views/applicant/ApplicantDashboard.vue``
     - Applicant experience that reuses the shared layout but swaps in applicant-specific widgets.
   * - ``src/components/CandidatesTable.vue``
     - Sortable/filterable table component, reused by HR and organization modules.
   * - ``src/components/Overview.vue``
     - KPI cards fed by getters from ``modules/hr.js``.
   * - ``src/components/NavBar.vue`` / ``Sidebar.vue``
     - Navigation chrome that reacts to router metadata and theme toggles.
   * - ``src/theme``
     - Token definitions for light/dark palettes consumed by ``src/assets/styles/global.css``.

Runtime data flow
-----------------

1. ``src/main.js`` initialises Vue, mounts the router + store, and renders ``<App />``.
2. Route components dispatch actions like ``hr/fetchCandidates`` defined in ``src/store/modules/hr.js``.
3. Actions call the shared Axios client (``src/services/api.js``) which injects cookies via ``withCredentials``.
4. Components read state through getters/computed props so a single source of truth drives the UI.

Environment-sensitive pieces
----------------------------

* API base URL is defined inside ``src/services/api.js`` (defaults to ``/api``). The Vite dev proxy automatically detects the environment:
  - In Docker: proxies to ``http://backend:8086`` (using service name)
  - Locally: proxies to ``http://localhost:8086``
  - Can be overridden with ``VITE_API_BASE_URL`` environment variable
* CORS is configured on the backend to allow requests from both local and Docker frontend instances.
* Authentication flows rely on ``src/store/modules/auth.js``. Keep its reducers in sync with backend cookie lifetimes.
* Themes are sourced from ``modules/theme.js`` and the CSS variables declared under ``src/assets/styles``.

