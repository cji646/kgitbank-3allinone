#!/bin/bash

umask 077
set -o pipefail

BACKUP_DIR="/mnt/backup"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/travel_safe_${DATE}.sql.gpg"

GPG_RECIPIENT="F876047F7967079C"
export GNUPGHOME="/home/backup/.gnupg"

# 현재 서버가 Primary인지 확인
READ_ONLY=$(mariadb \
    --defaults-extra-file=/home/backup/.my.cnf \
    -Nse "SELECT @@global.read_only;")

# Replica이면 백업하지 않음
if [ "$READ_ONLY" != "0" ]; then
    echo "$(date) - Replica 서버이므로 백업 생략"
    exit 0
fi

# NFS가 정상적으로 마운트되어 있는지 확인
if ! mountpoint -q "$BACKUP_DIR"; then
    echo "$(date) - 백업 실패: NFS가 마운트되어 있지 않음"
    exit 1
fi

# travel_safe DB 백업 후 바로 GPG 암호화
mysqldump \
    --defaults-extra-file=/home/backup/.my.cnf \
    travel_safe \
| gpg \
    --batch \
    --yes \
    --trust-model always \
    --recipient "$GPG_RECIPIENT" \
    --output "$BACKUP_FILE" \
    --encrypt

if [ $? -eq 0 ]; then
    echo "$(date) - 암호화 백업 성공: $BACKUP_FILE"
else
    echo "$(date) - 암호화 백업 실패"
    rm -f "$BACKUP_FILE"
    exit 1
fi

cd /tmp || exit 1

# 7일 지난 암호화 백업 파일 삭제
find "$BACKUP_DIR" \
    -type f \
    -name "travel_safe_*.sql.gpg" \
    -mtime +7 \
    -delete
