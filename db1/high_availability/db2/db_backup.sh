#!/bin/bash

source /etc/travel-db.env

# Replica가 되는 순간부터 쓰기 차단
/usr/bin/mariadb -e "SET GLOBAL read_only=ON;"

# 기존 복제 중지
/usr/bin/mariadb -e "STOP SLAVE;" 2>/dev/null

# 기존 복제 연결 정보/relay log 정리
/usr/bin/mariadb -e "RESET SLAVE ALL;"

# 새로운 Primary(DB1)로 연결
/usr/bin/mariadb -e "
CHANGE MASTER TO
    MASTER_HOST='${DB1_IP}',
    MASTER_USER='${REPL_USER}',
    MASTER_PASSWORD='${REPL_PASSWORD}',
    MASTER_PORT=${DB_PORT},
    MASTER_USE_GTID=current_pos;

START SLAVE;
"
