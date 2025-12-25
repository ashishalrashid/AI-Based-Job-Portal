#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "📚 Building documentation (backend + frontend)..."
python -m venv "${REPO_ROOT}/.docs-venv" >/dev/null 2>&1 || true
source "${REPO_ROOT}/.docs-venv/bin/activate"
pip install -q -r "${REPO_ROOT}/docs/requirements.txt"
make -C "${REPO_ROOT}/docs" html
deactivate

echo ""
echo "✅ Docs generated:"
echo "  - Backend HTML: docs/build/backend/index.html"
echo "  - Frontend HTML: docs/build/frontend/index.html"
echo "  - Landing page: docs/build/index.html"

