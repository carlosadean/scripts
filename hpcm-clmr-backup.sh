#!/bin/bash
#
# author: carlosadean@linea.org.br
# version: 1.0
# date: 2023-09-01
# 
# usage: ./backup-hpcm-clmr.sh
#
ROOT_BKP=/root/Documents
CLMR_FILE_BKP="`date +'%Y%m%d-%H%M%S'`-cluster-definition-file.config"
DB_FILE_BKP="`date +'%Y%m%d-%H%M%S'`-cmu-backup.sqlite3"

echo "Backup HPCM started!"

echo "Backup HPCM cluster configuration..."
discover --show-configfile --images --kernel --bmc-info \--kernel-parameters --ips > "${ROOT_BKP}/${CLMR_FILE_BKP}"

echo "Backup HPCM database..."
systemctl stop config_manager.service
systemctl stop clmgr-power.service
systemctl stop cmdb.service

# backup the HPCM clmr database
sqlite3 /opt/clmgr/database/db/cmu.sqlite3 ".backup ${ROOT_BKP}/${DB_FILE_BKP}"

# start services
systemctl start config_manager.service
systemctl start clmgr-power.service
systemctl start cmdb.service

echo "Backup HPCM finished!"
echo "
HPCM configuration file: ${ROOT_BKP}/${CLMR_FILE_BKP}
HPCM database backup: ${ROOT_BKP}/${DB_FILE_BKP}
"
