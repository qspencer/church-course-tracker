#!/bin/bash
# Database backup script for local development
# Creates timestamped backups of the development database

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
DB_PATH="$PROJECT_ROOT/backend/data/church_course_tracker.db"

if [ ! -f "$DB_PATH" ]; then
    echo "⚠️  Database file not found: $DB_PATH"
    exit 0
fi

BACKUP_DIR="$PROJECT_ROOT/backend/data/backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/church_course_tracker_${TIMESTAMP}.db"

echo "💾 Creating database backup..."
cp "$DB_PATH" "$BACKUP_FILE"

# Compress old backups (keep uncompressed for last 3)
echo "🗜️  Compressing old backups..."
find "$BACKUP_DIR" -name "church_course_tracker_*.db" -type f -mtime +1 | while read backup; do
    if [ ! -f "${backup}.gz" ]; then
        gzip "$backup"
    fi
done

# Keep only last 10 backups (compressed or not)
echo "🧹 Cleaning up old backups (keeping last 10)..."
ls -t "$BACKUP_DIR"/church_course_tracker_*.db* 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true

echo "✅ Backup created: $BACKUP_FILE"
echo "📊 Backup size: $(du -h "$BACKUP_FILE" | cut -f1)"
