#!/bin/bash
set -e

echo "== Detect OS =="

if [ -f /etc/os-release ]; then
  . /etc/os-release
  OS_ID=$ID
  OS_CODENAME=$VERSION_CODENAME
else
  echo "Cannot detect OS"
  exit 1
fi

echo "OS Detected: $OS_ID ($OS_CODENAME)"

# Update system
sudo apt update
sudo apt install -y ca-certificates curl gnupg

# Prepare keyrings
sudo install -m 0755 -d /etc/apt/keyrings

# Add Docker GPG key (based on OS)
if [[ "$OS_ID" == "ubuntu" ]]; then
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
elif [[ "$OS_ID" == "debian" ]]; then
  curl -fsSL https://download.docker.com/linux/debian/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
else
  echo "Unsupported OS: $OS_ID"
  exit 1
fi

sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/$OS_ID $OS_CODENAME stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Enable Docker
sudo systemctl enable docker
sudo systemctl start docker

# Allow non-root docker usage
sudo usermod -aG docker $USER

echo "Docker installation completed successfully."
echo "Please logout/login or run: newgrp docker"
