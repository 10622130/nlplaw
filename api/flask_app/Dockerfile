# ---- Builder: install Python dependencies into an isolated venv ----
FROM python:3.10-slim AS builder

WORKDIR /app

COPY api/flask_app/requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---- Runtime: copy only the built venv + source, no build tooling ----
FROM python:3.10-slim

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Source — both api/ and core/ are needed
COPY api/ api/
COPY core/ core/

# Run as non-root
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 5002

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import sys,urllib.request; sys.exit(0 if urllib.request.urlopen('http://localhost:5002/auth/me', timeout=3).status == 200 else 1)"

# Single worker, not multiple: `app = create_app()` in app.py runs
# `db.create_all()` at module-import time, so workers > 1 they race to CREATE TABLE concurrently, which Postgres
CMD ["gunicorn", "-b", "0.0.0.0:5002", "--workers", "1", "--threads", "4", "--timeout", "60", "api.flask_app.app:app"]
