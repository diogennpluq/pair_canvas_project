FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --settings=pair_canvas.settings_prod || true

# Create logs directory
RUN mkdir -p /var/log/pair_canvas

# Expose port
EXPOSE 8000

# Run Daphne for WebSocket support
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "pair_canvas.asgi:application"]
