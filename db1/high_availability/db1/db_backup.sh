#!/bin/bash

source /etc/travel-db.env

/usr/bin/mariadb -e "SET GLOBAL read_only=ON;"

/usr/bin/mariadb -e "
STOP SLAVE;
CHANGE MASTER TO
    MASTER_HOST='${DB2_IP}',
    MASTER_USER='${REPL_USER}',
    MASTER_PASSWORD='${REPL_PASSWORD}',
    MASTER_PORT=${DB_PORT},
    MASTER_USE_GTID=slave_pos;
START SLAVE;
"
