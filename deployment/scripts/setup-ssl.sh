#!/bin/bash
# Let's Encrypt SSL Certificate Setup for AgriDAO

echo "🔒 Setting up SSL certificates for AgriDAO..."

# Install certbot
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

# Stop nginx temporarily
sudo systemctl stop nginx

# Get certificates
sudo certbot certonly --standalone -d agridao.com -d www.agridao.com --email admin@agridao.com --agree-tos --non-interactive

# Setup auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -

# Start nginx with SSL config
sudo systemctl start nginx

echo "✅ SSL certificates configured successfully"
