Component catalogue
===================

Dashboard primitives
--------------------

``DashboardLayout.vue``
   Wraps sidebar, navbar, and the routed view slot. Reacts to route metadata to update breadcrumbs and wires theme toggles to the ``theme`` store module.

``NavBar.vue`` / ``Sidebar.vue``
   Navigation chrome that highlights the active route and exposes profile/log-out actions. Side effects (such as logging out) happen through store actions.

``Overview.vue``
   Displays KPI cards for open roles, offers sent, etc. Props are type-checked and default to ``0`` so async data does not cause layout thrash.

Data displays
-------------

``CandidatesTable.vue``
   Configurable table component with column metadata, slot-based cells, and events for ``sort-change``, ``filter-change``, and ``row-click``. Parents typically dispatch ``hr/setActiveCandidate`` when a row is selected.

``DataTable.vue``
   Lightweight wrapper used in organization views when pagination happens client-side. Ideal for simple searchable tables without the heavier hooks from ``CandidatesTable``.

``UpcomingMeetings.vue``
   Renders the next three interview slots by consuming ``interviewSlots`` from the applicant module. Emits ``book-slot`` to push actions like ``applicant/bookSlot``.

Forms and editors
-----------------

``SearchSection.vue``
   Stateless search + filter bar. Emits ``search`` / ``filter`` events so parent dashboards can re-fetch data with new query params.

``OfferLetterEditor.vue``
   HR view that gathers compensation + start-date inputs, posts to ``/offer_letter`` through the Axios client, and downloads the generated ReportLab PDF.

Reuse tips
----------

* Keep layout components presentational; fetch data in stores or route views, then pass via props.
* Prefer store actions over direct Axios calls so loading/error states are centralised.
* Extend global styles via ``src/assets/styles/global.css`` and the theme tokens in ``src/theme`` instead of scattering bespoke CSS.

