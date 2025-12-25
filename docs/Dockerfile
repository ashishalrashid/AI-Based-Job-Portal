FROM python:3.11-slim AS builder

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements first for better caching
COPY docs/requirements.txt docs/requirements.txt
RUN pip install --no-cache-dir -r docs/requirements.txt

# Copy source files
COPY docs docs
COPY app app

# Build documentation
RUN make -C docs html || (echo "Build failed, checking what exists..." && ls -la docs/build 2>/dev/null || true && exit 1)

# Verify index.html was copied
RUN if [ ! -f docs/build/index.html ]; then \
    echo "Copying index.html to build directory..."; \
    cp docs/index.html docs/build/index.html || true; \
    fi

FROM python:3.11-slim
WORKDIR /site

# Copy built documentation
COPY --from=builder /workspace/docs/build ./build

# Ensure index.html exists (fallback)
RUN if [ ! -f ./build/index.html ]; then \
    echo "Warning: index.html not found, creating default"; \
    mkdir -p ./build; \
    echo '<!DOCTYPE html><html><head><title>Documentation</title></head><body><h1>Documentation</h1><p><a href="backend/index.html">Backend Docs</a></p><p><a href="frontend/index.html">Frontend Docs</a></p></body></html>' > ./build/index.html; \
    fi

EXPOSE 8090

# Use Python's http.server with proper binding
CMD ["python", "-m", "http.server", "8090", "--bind", "0.0.0.0", "--directory", "build"]

