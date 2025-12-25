Frontend quickstart
===================

This page consolidates the old `app/frontend/README.md` content (Vue/Vite starter instructions) with the current HR App workflow, so developers and advanced users have one authoritative source.

Local development
-----------------

1. Install dependencies::

     cd app/frontend
     npm install

2. Start the dev server::

     npm run dev

3. Visit `http://localhost:5173`. The Vite server proxies API calls under ``/api`` to the backend service.

Docker workflow (recommended)
------------------------------

The recommended way to run the frontend is using Docker Compose. From the project root:

.. code-block:: bash

   docker compose up --build

The frontend service:
- Automatically detects Docker environment and configures proxy to ``http://backend:8086``
- Uses environment variables ``DOCKER_ENV`` and ``BACKEND_HOST`` for configuration
- Falls back to ``http://localhost:8086`` when running locally
- Waits for backend health check before starting
- Supports hot module replacement for development

Useful npm scripts
------------------

.. list-table::
   :header-rows: 1

   * - Script
     - Command
     - Purpose
   * - ``npm run dev``
     - Starts Vite in dev mode
     - Hot Module Replacement + proxy to ``/api``.
   * - ``npm run build``
     - Runs ``vite build``
     - Produces production-ready assets.
   * - ``npm run preview``
     - ``vite preview``
     - Serves the built assets locally for smoke testing.
   * - ``npm run lint``
     - ``eslint . --fix --cache``
     - Applies lint fixes where possible.
   * - ``npm run format``
     - ``prettier --write src/``
     - Enforces formatting on the `src` tree.

Recommended tooling
-------------------

* **IDE:** VS Code with the official Vue extension (disable Vetur).
* **Browser tooling:** Vue DevTools (Chromium or Firefox variants). Remember to enable “Custom Object Formatter” in the devtools settings.

Configuration tips
------------------

* Environment variables: Set ``VITE_API_BASE_URL`` if you need to point the SPA at a non-standard backend (otherwise it falls back to ``/api``).
* Proxy: See :doc:`architecture` for an explanation of the dev server proxy block inside ``vite.config.js``.
* Linting/formatting: run the scripts above before pushing to avoid CI issues.

Where to go next
----------------

* :doc:`architecture` for directory layout and build tooling.
* :doc:`data_flow` for store/actions/API lifecycle details.
* :doc:`components` for reusable UI primitives.
* :doc:`user_guide` for persona-based, user-facing walkthroughs.

