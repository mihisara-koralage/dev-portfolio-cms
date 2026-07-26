# ============================================================
# Stage 1: Base Python environment
# ============================================================
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# Stage 2: Development
# ============================================================
FROM base AS development

COPY backend/requirements/base.txt .
COPY backend/requirements/development.txt .
RUN pip install -r development.txt

COPY backend/ .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ============================================================
# Stage 3: Production builder (populated in Phase 7)
# ============================================================
FROM base AS production

COPY backend/requirements/production.txt .
RUN pip install -r production.txt

COPY backend/ .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]