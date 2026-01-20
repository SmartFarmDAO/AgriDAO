#!/bin/bash
set -e

echo "=========================================="
echo "AgriDAO Lightsail Setup Script"
echo "Ubuntu 24.04 LTS (Noble) - 2GB RAM"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential tools
print_status "Installing essential tools..."
sudo apt install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    ufw \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Install Docker
print_status "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
rm get-docker.sh

# Install Docker Compose
print_status "Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Node.js 20 LTS
print_status "Installing Node.js 20 LTS..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install Python 3.12 and pip
print_status "Installing Python and pip..."
sudo apt install -y python3 python3-pip python3-venv

# Configure swap (1GB swap for 2GB RAM)
print_status "Configuring swap space..."
if [ ! -f /swapfile ]; then
    sudo fallocate -l 1G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    print_status "Swap configured: 1GB"
else
    print_warning "Swap file already exists, skipping..."
fi

# Configure firewall
print_status "Configuring firewall..."
sudo ufw --force enable
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000/tcp  # Backend API
sudo ufw allow 3000/tcp  # Frontend dev server (optional)
sudo ufw allow 5432/tcp  # PostgreSQL (for external access if needed)
print_status "Firewall configured"

# Optimize system for 2GB RAM
print_status "Optimizing system settings..."
sudo tee -a /etc/sysctl.conf > /dev/null <<EOF

# AgriDAO optimizations for 2GB RAM
vm.swappiness=10
vm.vfs_cache_pressure=50
net.core.somaxconn=1024
net.ipv4.tcp_max_syn_backlog=2048
EOF
sudo sysctl -p

# Create project directory
print_status "Creating project directory..."
mkdir -p ~/agridao
cd ~/agridao

# Install PM2 for process management (optional but recommended)
print_status "Installing PM2 for process management..."
sudo npm install -g pm2

# Setup log rotation
print_status "Configuring log rotation..."
sudo tee /etc/logrotate.d/agridao > /dev/null <<EOF
/home/ubuntu/agridao/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
}
EOF

# Create logs directory
mkdir -p ~/agridao/logs

# Display versions
print_status "Installation complete! Versions installed:"
echo "----------------------------------------"
echo "Docker: $(docker --version)"
echo "Docker Compose: $(docker-compose --version)"
echo "Node.js: $(node --version)"
echo "npm: $(npm --version)"
echo "Python: $(python3 --version)"
echo "pip: $(pip3 --version)"
echo "----------------------------------------"

print_warning "IMPORTANT: You need to log out and log back in for Docker group changes to take effect!"
print_warning "After re-login, run: docker ps (to verify Docker works without sudo)"

echo ""
print_status "Next steps:"
echo "1. Log out and log back in (or run: newgrp docker)"
echo "2. Clone your repository: git clone <your-repo-url> ~/agridao"
echo "3. Navigate to project: cd ~/agridao"
echo "4. Create .env file with your configuration"
echo "5. Run: docker-compose up -d"
echo ""
print_status "Setup script completed successfully!"
