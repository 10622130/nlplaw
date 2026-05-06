FROM python:3.10-slim

WORKDIR /app

# Install dependencies first for layer caching
COPY api/flask_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source — both api/ and core/ are needed
COPY api/ api/
COPY core/ core/

ENV PYTHONPATH=/app

EXPOSE 5002

CMD ["gunicorn", "-b", "0.0.0.0:5002", "api.flask_app.app:app"]
