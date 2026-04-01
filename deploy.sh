#!/bin/bash

# Production deployment script for Pair Canvas

set -e

echo "🚀 Starting deployment..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Build and start containers
echo "📦 Building Docker images..."
docker-compose build

echo "🗄️  Running database migrations..."
docker-compose run --rm web python manage.py migrate --noinput --settings=pair_canvas.settings_prod

echo "🎨 Collecting static files..."
docker-compose run --rm web python manage.py collectstatic --noinput --settings=pair_canvas.settings_prod

echo "🚀 Starting services..."
docker-compose up -d

echo "✅ Deployment complete!"
echo "📊 Check status with: docker-compose ps"
echo "📋 View logs with: docker-compose logs -f"
