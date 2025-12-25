# Documentation stack

- `docs/backend`: Sphinx project that introspects the Flask code under `app/backend`.
- `docs/frontend`: Sphinx project that documents the Vue client using reStructuredText.
- `docs/Makefile`: orchestrates both builds and places HTML in `docs/build/{backend,frontend}` with a shared landing page.
- `docs/requirements.txt`: shared Python dependencies (Sphinx + Furo theme).
- `scripts/build_docs.sh`: helper script that bootstraps a virtualenv and runs `make -C docs html`.

Run `./scripts/build_docs.sh` (or `make -C docs html` once requirements are installed) to regenerate everything.

