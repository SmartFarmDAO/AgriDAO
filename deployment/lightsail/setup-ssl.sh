#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

echo "=========================================="
echo "AgriDAO SSL Setup Script"
echo "Let's Encrypt SSL Certificate Setup"
echo "=========================================="

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found! Please create it first."
    exit 1
fi

# Load environment variables
source .env

# Check required variables
if [ -z "$DOMAIN_NAME" ] || [ -z "$CERTBOT_EMAIL" ]; then
    print_error "DOMAIN_NAME and CERTBOT_EMAIL must be set in .env file"
    exit 1
fi

print_status "Setting up SSL for domain: $DOMAIN_NAME"
print_status "Email for Let's Encrypt: $CERTBOT_EMAIL"

# Create directories for certbot
print_status "Creating certbot directories..."
mkdir -p ./certbot/conf
mkdir -p ./certbot/www

# Create temporary nginx config for initial certificate request
print_status "Creating temporary nginx configuration..."
cat > nginx-temp.conf << EOF
events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name $DOMAIN_NAME;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 200 'SSL setup in progress...';
            add_header Content-Type text/plain;
        }
    }
}
EOF

# Start temporary nginx for certificate validation
print_status "Starting temporary nginx for certificate validation..."
docker run -d --name temp_nginx \
    -p 80:80 \
    -v $(pwd)/nginx-temp.conf:/etc/nginx/nginx.conf:ro \
    -v $(pwd)/certbot/www:/var/www/certbot:ro \
    nginx:alpine

# Wait for nginx to start
sleep 5

# Request SSL certificate
print_status "Requesting SSL certificate from Let's Encrypt..."
docker run --rm \
    -v $(pwd)/certbot/conf:/etc/letsencrypt \
    -v $(pwd)/certbot/www:/var/www/certbot \
    certbot/certbot \
    certonly --webroot \
    --webroot-path=/var/www/certbot \
    --email $CERTBOT_EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN_NAME

# Stop temporary nginx
print_status "Stopping temporary nginx..."
docker stop temp_nginx
docker rm temp_nginx
rm nginx-temp.conf

# Update nginx config with actual domain name
print_status "Updating nginx configuration with domain name..."
sed "s/DOMAIN_NAME/$DOMAIN_NAME/g" nginx.conf > nginx-ssl.conf
mv nginx-ssl.conf nginx.conf

# Set up certificate renewal cron job
print_status "Setting up automatic certificate renewal..."
(crontab -l 2>/dev/null; echo "0 12 * * * cd $(pwd) && docker-compose -f docker-compose.ssl.yml exec certbot renew --quiet && docker-compose -f docker-compose.ssl.yml exec nginx nginx -s reload") | crontab -

print_status "SSL setup completed successfully!"
print_warning "Next steps:"
echo "1. Start the SSL-enabled services: docker-compose -f docker-compose.ssl.yml up -d"
echo "2. Verify SSL is working: https://$DOMAIN_NAME"
echo "3. Check certificate auto-renewal: certbot renew --dry-run"
