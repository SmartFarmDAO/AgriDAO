#!/bin/bash

# AgriDAO Production Deployment Script

set -e

echo "🚀 Starting AgriDAO Production Deployment..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this script as root"
    exit 1
fi

# Check required environment variables
if [ ! -f ".env.production" ]; then
    echo "❌ .env.production file not found"
    echo "Please copy .env.production.example and configure it"
    exit 1
fi

# Load production environment
export $(grep -v '^#' .env.production | xargs)

# Validate critical environment variables
if [ -z "$DATABASE_URL" ] || [ -z "$JWT_SECRET" ]; then
    echo "❌ Critical environment variables missing"
    echo "Please configure DATABASE_URL and JWT_SECRET in .env.production"
    exit 1
fi

# Check if at least one email provider is configured
EMAIL_CONFIGURED=false
if [ -n "$SMTP_PASSWORD" ] && [ -n "$SMTP_USERNAME" ]; then
    EMAIL_CONFIGURED=true
    echo "✅ Gmail SMTP configured"
fi
if [ -n "$SENDGRID_API_KEY" ]; then
    EMAIL_CONFIGURED=true
    echo "✅ SendGrid configured"
fi
if [ -n "$MAILGUN_API_KEY" ] && [ -n "$MAILGUN_DOMAIN" ]; then
    EMAIL_CONFIGURED=true
    echo "✅ Mailgun configured"
fi

if [ "$EMAIL_CONFIGURED" = false ]; then
    echo "❌ No email provider configured"
    echo "Please configure at least one email provider in .env.production"
    exit 1
fi

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose down

# Backup database
echo "💾 Creating database backup..."
mkdir -p backups
BACKUP_FILE="backups/agridb_backup_$(date +%Y%m%d_%H%M%S).sql"
if docker-compose exec -T db pg_dump -U postgres agridb > "$BACKUP_FILE" 2>/dev/null; then
    echo "✅ Database backup created: $BACKUP_FILE"
else
    echo "⚠️  Database backup failed (database might not exist yet)"
fi

# Build production images
echo "🔨 Building production images..."
docker-compose -f docker-compose.yml -f deployment/docker/docker-compose.prod.yml build

# Copy production environment to containers
echo "📋 Configuring production environment..."
cp .env.production backend/.env
cp .env.production frontend/.env

# Start services
echo "🚀 Starting production services..."
docker-compose -f docker-compose.yml -f deployment/docker/docker-compose.prod.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose exec backend alembic upgrade head

# Test services
echo "🧪 Testing services..."

# Test backend health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    docker-compose logs backend --tail=20
    exit 1
fi

# Test email service
echo "📧 Testing email service..."
TEST_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/otp/request \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com"}' || echo "failed")

if echo "$TEST_RESPONSE" | grep -q '"sent":true'; then
    echo "✅ Email service is working"
else
    echo "❌ Email service test failed"
    echo "Response: $TEST_RESPONSE"
    exit 1
fi

# Show service status
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🎉 Production deployment completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Configure your domain DNS to point to this server"
echo "2. Set up SSL certificates (run setup-ssl.sh)"
echo "3. Configure monitoring and backups"
echo "4. Test the complete user flow"
echo ""
echo "🔗 Access your application:"
echo "   Frontend: http://$(curl -s ifconfig.me)"
echo "   Backend API: http://$(curl -s ifconfig.me):8000"
echo "   API Docs: http://$(curl -s ifconfig.me):8000/docs"
echo ""
echo "⚠️  Remember to:"
echo "   - Keep your .env.production file secure"
echo "   - Set up regular database backups"
echo "   - Monitor application logs"
echo "   - Update dependencies regularly"
