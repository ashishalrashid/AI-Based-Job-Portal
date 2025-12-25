# Backend documentation

This Sphinx project documents the Flask application that lives under `app/backend`.

## Documentation Files

- **API.md** - Comprehensive API endpoint documentation with request/response examples
- **sample_offer_letters.md** - Test guide for offer letter email system

## Build the docs

```bash
python -m venv .docs-venv
source .docs-venv/bin/activate
pip install -r docs/requirements.txt
make -C docs backend
```

Open `docs/build/backend/index.html` to browse the rendered site.

