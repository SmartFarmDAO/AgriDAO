#!/bin/bash
# Quick backend restart script

set -e

echo "🔄 Restarting backend with auth fixes..."

cd /Users/sohagmahamud/Projects/AgriDAO

# Rebuild backend
echo "📦 Rebuilding backend..."
docker-compose -f deployment/lightsail/docker-compose.lightsail.yml build backend

# Restart backend
echo "🚀 Restarting backend..."
docker-compose -f deployment/lightsail/docker-compose.lightsail.yml restart backend

# Wait for backend to be ready
echo "⏳ Waiting for backend to start..."
sleep 10

# Test health
echo "🏥 Testing health..."
curl -s http://54.251.65.124/api/health | jq .

# Test login
echo ""
echo "🔐 Testing login..."
curl -s -X POST http://54.251.65.124/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@agridao.com","password":"admin123"}' | jq .

echo ""
echo "✅ Backend restarted!"
