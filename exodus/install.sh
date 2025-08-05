#!/bin/bash
set -euxo pipefail

# Ensure running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root or use sudo"
  exit 1
fi

install_dir=/opt/exodus/

# -------- Install Go --------
#GO_VERSION=1.22.4
#GO_TARBALL=go${GO_VERSION}.linux-amd64.tar.gz
#GO_URL=https://go.dev/dl/${GO_TARBALL}

#echo "📦 Installing Go ${GO_VERSION}..."
#curl -LO ${GO_URL}
#rm -rf /usr/local/go
#tar -C /usr/local -xzf ${GO_TARBALL}
#rm ${GO_TARBALL}

# Setup Go environment
#export PATH=$PATH:/usr/local/go/bin
#echo 'export PATH=$PATH:/usr/local/go/bin' >> /etc/profile

# -------- Install dependencies --------
#apt-get update
#apt-get install -y git make

# -------- Clone and build ExodusDNS --------
git clone https://github.com/cpl/exodus.git /tmp/exodus
rsync -a /tmp/exodus $install_dir
cd $install_dir
make build

# Install the server binary
install -m 0755 out/exodus-server /usr/local/bin/

# -------- Create systemd service --------
cat <<EOF > /etc/systemd/system/exodus.service
[Unit]
Description=Exodus DNS Exfiltration Server
After=network.target

[Service]
ExecStart=/usr/local/bin/exodus-server \
  -port 53 -data $install_dir/data
Restart=on-failure
User=root
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_BIND_SERVICE
NoNewPrivileges=yes

[Install]
WantedBy=multi-user.target
EOF

# Start and enable the service
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable exodus
systemctl start exodus

rm -rf /tmp/exodus

echo "✅ Exodus server installed and running on UDP port 53"

