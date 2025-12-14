#!/bin/bash
# AgriDAO Database Backup Script

BACKUP_DIR="/var/backups/agridao"
DB_NAME="agridao_db"
DB_USER="postgres"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/agridao_backup_$TIMESTAMP.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
echo "📦 Creating database backup..."
pg_dump -h localhost -U $DB_USER -d $DB_NAME > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

# Verify backup
if [ -f "$BACKUP_FILE.gz" ]; then
    echo "✅ Backup created successfully: $BACKUP_FILE.gz"
    echo "📊 Backup size: $(du -h $BACKUP_FILE.gz | cut -f1)"
else
    echo "❌ Backup failed!"
    exit 1
fi
