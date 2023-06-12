#!/bin/bash

sudo rm -rf /opt/HomeGuard

sudo systemctl disable homeguard.service

sudo rm -rf /etc/systemd/system/homeguard.service

killall python3
