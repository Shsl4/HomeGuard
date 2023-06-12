#!/bin/bash

if [ "$(id -u)" -ne 0 ]; then echo "Please run as root." >&2; exit 1; fi

cp -a . /opt/HomeGuard

SCRIPT_PATH="/opt/HomeGuard/main.py"

SERVICE_FILE="/etc/systemd/system/homeguard.service"

echo "[Unit]
Description=HomeGuard

[Service]
ExecStart=sudo python3 $SCRIPT_PATH

[Install]
WantedBy=multi-user.target" > $SERVICE_FILE

sudo chmod 644 $SERVICE_FILE

sudo systemctl enable homeguard.service

sudo systemctl start homeguard.service

sudo systemctl status homeguard.service
