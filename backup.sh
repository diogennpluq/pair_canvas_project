#!/bin/bash

# Backup script for Pair Canvas
# Usage: ./backup.sh [backup_dir]

set -e

BACKUP_DIR=${1:-./backups}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="pair_canvas_backup_$TIMESTAMP"

echo "🗄️  Starting backup..."

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Database backup
echo "💾 Backing up database..."
if command -v docker-compose &> /dev/null; then
    docker-compose exec -T db pg_dump -U pair_canvas pair_canvas > "$BACKUP_DIR/${BACKUP_NAME}_db.sql"
else
    python manage.py dbbackup --output-filename "$BACKUP_DIR/${BACKUP_NAME}_db.sql" 2>/dev/null || \
    cp db.sqlite3 "$BACKUP_DIR/${BACKUP_NAME}_db.sqlite3"
fi

# Media backup
echo "📸 Backing up media files..."
if [ -d "media" ]; then
    tar -czf "$BACKUP_DIR/${BACKUP_NAME}_media.tar.gz" media/
fi

# Env backup (without sensitive data)
echo "📋 Backing up configuration..."
if [ -f ".env.example" ]; then
    cp .env.example "$BACKUP_DIR/${BACKUP_NAME}_env_example.txt"
fi

# Create manifest
echo "📝 Creating backup manifest..."
cat > "$BACKUP_DIR/${BACKUP_NAME}_manifest.txt" << EOF
Backup created: $(date)
Database: ${BACKUP_NAME}_db.sql
Media: ${BACKUP_NAME}_media.tar.gz

To restore:
1. Restore database:
   docker-compose exec -T db psql -U pair_canvas pair_canvas < ${BACKUP_NAME}_db.sql

2. Restore media:
   tar -xzf ${BACKUP_NAME}_media.tar.gz

3. Update .env file with your settings
EOF

# Cleanup old backups (keep last 7)
echo "🧹 Cleaning up old backups..."
ls -t "$BACKUP_DIR"/pair_canvas_backup_*.sql 2>/dev/null | tail -n +8 | xargs -r rm -- || true

echo "✅ Backup completed: $BACKUP_DIR/$BACKUP_NAME"
echo "📦 Total size: $(du -sh "$BACKUP_DIR/$BACKUP_NAME"* | tail -1 | cut -f1)"
