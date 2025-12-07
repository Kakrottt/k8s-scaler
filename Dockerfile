# Use a small Python base image
FROM python:3.11-slim

# Install OS deps (curl only if you want debugging)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python deps first (for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy operator code
COPY generalscaler/ ./generalscaler/
# COPY setup.py pyproject.toml* . 2>/dev/null || true

# Create non-root user with a name that doesn't clash
RUN useradd -u 1001 -m gs-operator
USER gs-operator

# Run the operator via kopf
# Either:
#   - make generalscaler/main.py call kopf.run(), or
#   - expose a console script via setup.py/pyproject
ENTRYPOINT ["python", "-m", "generalscaler.main"]
