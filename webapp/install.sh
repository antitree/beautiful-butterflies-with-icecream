#!/bin/bash
set -euxo pipefail

# Ensure running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root or use sudo"
  exit 1
fi

# -------- Install Python and dependencies --------
apt-get update
apt-get install -y python3 python3-pip
pip3 install --upgrade pip
pip3 install -r "$(dirname "$0")/../requirements.txt"

# -------- Copy webapp files --------
install_dir=/opt/webapp
mkdir -p "$install_dir"
cp -r "$(dirname "$0")"/*.py "$install_dir"/
mkdir -p "$install_dir/templates"
cp -r "$(dirname "$0")"/templates/* "$install_dir/templates/"

# -------- Create systemd service --------
cat <<SERVICE > /etc/systemd/system/webapp.service
[Unit]
Description=Log Dashboard Web Application
After=network.target

[Service]
WorkingDirectory=$install_dir
ExecStart=/usr/bin/python3 $install_dir/app.py
Restart=on-failure
User=nobody
Environment=LOG_ROOT=$install_dir/logs
NoNewPrivileges=yes

[Install]
WantedBy=multi-user.target
SERVICE

# Start and enable the service
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable webapp
systemctl start webapp

echo "✅ Webapp installed and running"
