#!/bin/bash

# SSL certificate setup script using Let's Encrypt

set -e

DOMAIN=${1:-localhost}
EMAIL=${2:-admin@example.com}

echo "🔒 Setting up SSL certificates for $DOMAIN..."

# Create directories
mkdir -p ./certbot/www
mkdir -p ./nginx/ssl

# Generate self-signed certificate for development
echo "📝 Generating self-signed certificate..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ./nginx/ssl/privkey.pem \
    -out ./nginx/ssl/fullchain.pem \
    -subj "/C=RU/ST=Moscow/L=Moscow/O=Pair Canvas/CN=$DOMAIN"

echo "✅ Self-signed certificates generated!"
echo "⚠️  For production, use Let's Encrypt:"
echo "   docker-compose run --rm certbot certonly --webroot --webroot-path=/var/www/certbot --email $EMAIL --agree-tos --no-eff-email -d $DOMAIN"
