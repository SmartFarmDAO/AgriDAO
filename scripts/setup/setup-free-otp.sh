#!/bin/bash

# Setup script for free OTP system
echo "🆓 Setting up Free OTP System for AgriDAO"
echo "=========================================="

# Check if .env files exist
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating backend/.env from example..."
    cp backend/.env.example backend/.env
fi

# Add MailHog configuration
echo ""
echo "📧 Configuring MailHog (Free Email Testing)..."
cat >> backend/.env << 'EOF'

# MailHog Configuration (Free Email Testing)
SMTP_HOST=mailhog
SMTP_PORT=1025
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=false
FROM_EMAIL=noreply@agridao.local
FROM_NAME=AgriDAO

# SMS Configuration (Optional)
SMS_PROVIDER=none
# Uncomment and configure one of these for SMS:
# SMS_PROVIDER=android
# ANDROID_SMS_API_URL=http://192.168.1.100:8080
# ANDROID_SMS_API_KEY=your-api-key
EOF

echo "✅ Configuration complete!"
echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "✅ Setup complete!"
echo ""
echo "📧 MailHog Web UI: http://localhost:8025"
echo "🌐 Frontend: http://localhost:5173"
echo "🔌 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "🧪 Test OTP:"
echo "curl -X POST http://localhost:8000/auth/otp/request \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"email\": \"test@example.com\"}'"
echo ""
echo "Then check MailHog UI at http://localhost:8025 for the email!"
