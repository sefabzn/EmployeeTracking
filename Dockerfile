# Use Python 3.9 as base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.4.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn psycopg2-binary

# Copy project files
COPY . .

# Create and set permissions for media and static directories
RUN mkdir -p /app/media /app/static \
    && chmod -R 755 /app/media /app/static

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Create and switch to non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "config.wsgi:application"]
