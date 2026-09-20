# ============================================================
# Stage 1: Builder
# Install dependencies into an isolated virtual environment.
# Nothing from this stage leaks into the final image.
# ============================================================
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System dependencies needed to compile Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install production dependencies only
COPY backend/requirements/ requirements/
RUN pip install --upgrade pip && pip install -r requirements/production.txt


# ============================================================
# Stage 2: Development
# Used by docker-compose.yml for local development.
# Includes dev dependencies and runs Django dev server.
# ============================================================
FROM python:3.11-slim AS development

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.development

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements/ requirements/
RUN pip install --upgrade pip && pip install -r requirements/development.txt

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


# ============================================================
# Stage 3: Production
# Lean runtime image — no build tools, no dev dependencies.
# Runs as a non-root user for security.
# ============================================================
FROM python:3.11-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Runtime system dependencies only — no gcc, no build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from builder — not pip itself
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY backend/ .

# Create a non-root user and hand ownership to it
# Running as root in a container is a security risk —
# if the container is compromised, root inside = root outside
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser && \
    mkdir -p /app/staticfiles /app/media && \
    chown -R appuser:appgroup /app

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

USER appuser

EXPOSE 8000

# Health check — Docker will mark the container unhealthy
# if this fails, and the orchestrator will restart it
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]

# Gunicorn: production WSGI server
# Workers = (2 × CPU cores) + 1 is the standard formula
# On a t3.micro (1 vCPU): 3 workers is correct
CMD ["gunicorn", "config.wsgi:application", "--config", "gunicorn.conf.py"]