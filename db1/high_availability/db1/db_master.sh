#!/bin/bash

source /etc/travel-db.env

/usr/bin/mariadb -e "STOP SLAVE;" 2>/dev/null
/usr/bin/mariadb -e "SET GLOBAL read_only=OFF;"
