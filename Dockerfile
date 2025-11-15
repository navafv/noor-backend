# Build stage
FROM node:18 AS node-build
WORKDIR /app/frontend
COPY noor-frontend/package*.json ./
RUN npm ci
COPY noor-frontend/ .
RUN npm run build

# Python stage
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# system deps for Pillow/psycopg2 if needed
RUN apt-get update && apt-get install -y build-essential libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static from Django and copy frontend build
ENV STATIC_ROOT=/vol/web/static
RUN python manage.py collectstatic --noinput

# Copy frontend build into Django static files (adjust as necessary)
RUN cp -r /app/frontend/dist/* /app/static/

CMD ["gunicorn", "noor_backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--log-level", "info"]
