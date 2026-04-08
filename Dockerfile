FROM python:3.11-slim

WORKDIR /app

# PostgreSQL client libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# Cloud Run uses PORT env var (default 8080)
CMD exec gunicorn app:app --bind 0.0.0.0:${PORT:-8080} --workers 2 --threads 4 --worker-class gthread --timeout 120
