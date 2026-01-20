#!/bin/bash
# Setup daily database backups at 2 AM
echo "0 2 * * * /path/to/agridao/scripts/backup-database.sh" | crontab -
echo "✅ Daily backup cron job configured"
