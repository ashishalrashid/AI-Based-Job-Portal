SPHINXBUILD ?= sphinx-build
BUILD_DIR    ?= build
BACKEND_SOURCE = backend/source
FRONTEND_SOURCE = frontend/source
BACKEND_BUILD = $(BUILD_DIR)/backend
FRONTEND_BUILD = $(BUILD_DIR)/frontend

.PHONY: help clean backend frontend html

help:
	@echo "Available targets:"
	@echo "  make backend  - build backend docs"
	@echo "  make frontend - build frontend docs"
	@echo "  make html     - build everything"
	@echo "  make clean    - remove build artifacts"

clean:
	rm -rf $(BUILD_DIR)

backend:
	$(SPHINXBUILD) -b html $(BACKEND_SOURCE) $(BACKEND_BUILD)

frontend:
	$(SPHINXBUILD) -b html $(FRONTEND_SOURCE) $(FRONTEND_BUILD)

html: backend frontend
	@cp index.html $(BUILD_DIR)/index.html

