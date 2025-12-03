#!/bin/bash
set -e

echo "=========================================="
echo "AgriDAO Deployment Script"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if .env exists
if [ ! -f .env ]; then
    print_error ".env file not found!"
    print_warning "Please create .env file with required variables"
    print_warning "See .env.example for reference"
    exit 1
fi

print_success ".env file found"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running!"
    print_warning "Please start Docker and try again"
    exit 1
fi

print_success "Docker is running"

# Pull latest changes
print_warning "Pulling latest changes from git..."
git pull origin main || print_warning "Git pull failed or not a git repository"

# Stop existing containers
print_warning "Stopping existing containers..."
docker-compose down

# Build frontend
print_warning "Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Build and start services
print_warning "Building and starting services..."
docker-compose -f docker-compose.lightsail.yml up -d --build

# Wait for services to be healthy
print_warning "Waiting for services to be healthy..."
sleep 10

# Check service status
print_warning "Checking service status..."
docker-compose ps

# Run database migrations
print_warning "Running database migrations..."
docker-compose exec -T backend python -m alembic upgrade head || print_warning "Migration failed or already up to date"

# Show logs
print_warning "Recent logs:"
docker-compose logs --tail=50

echo ""
print_success "Deployment completed!"
echo ""
echo "Services:"
echo "  Frontend: http://$(curl -s ifconfig.me)"
echo "  Backend:  http://$(curl -s ifconfig.me):8000"
echo "  API Docs: http://$(curl -s ifconfig.me):8000/docs"
echo ""
print_warning "To view logs: docker-compose logs -f"
print_warning "To check status: docker-compose ps"
