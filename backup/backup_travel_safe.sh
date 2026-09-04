#!/bin/bash

BACKUP_DIR="/mnt/backup"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/travel_safe_${DATE}.sql"

mysqldump --defaults-extra-file=/home/backup/.my.cnf travel_safe > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "$(date) - 백업 성공: $BACKUP_FILE"
else
    echo "$(date) - 백업 실패"
    rm -f "$BACKUP_FILE"
    exit 1
fi

cd /tmp

find "$BACKUP_DIR" -type f -name "travel_safe_*.sql" -mtime +7 -delete
