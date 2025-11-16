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

# --- FIX 3: Copy frontend build to a new 'frontend_build' dir ---
# This dir will be added to STATICFILES_DIRS in base.py
RUN mkdir -p /app/frontend_build
RUN cp -r /app/frontend/dist/* /app/frontend_build/

# --- FIX 2: Set production settings *before* collectstatic ---
ENV DJANGO_SETTINGS_MODULE=core.settings.development

# Collect static from Django (it will now find the frontend build)
RUN python manage.py collectstatic --noinput

# --- FIX 1: Use correct WSGI application path ---
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--log-level", "info"]