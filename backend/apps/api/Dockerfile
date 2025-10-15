# apps/api/Dockerfile
FROM python:3.11-slim as base

# Prevents Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1         PIP_NO_CACHE_DIR=1

# Workdir
WORKDIR /app

# System deps (optional: ca-certificates for HTTPS to S3 endpoints)
RUN apt-get update && apt-get install -y --no-install-recommends         ca-certificates       && rm -rf /var/lib/apt/lists/*

# Python deps
COPY apps/api/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# ===== Test Stage =====
FROM base as test
COPY apps/api/ /app/
CMD ["pytest", "tests/", "-v"]

# ===== Production Stage =====
FROM base as production
COPY apps/api/src /app/src
EXPOSE 8080
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8080"]