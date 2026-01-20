#!/bin/bash

# AgriDAO Production Deployment Script
# This script handles blue-green deployment with zero downtime

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOY_ENV="${1:-production}"
DEPLOY_TYPE="${2:-blue-green}"
BACKUP_ENABLED="${3:-true}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    # Check if required environment files exist
    if [[ ! -f "$PROJECT_ROOT/.env.${DEPLOY_ENV}" ]]; then
        error "Environment file .env.${DEPLOY_ENV} not found"
        exit 1
    fi
    
    if [[ ! -f "$PROJECT_ROOT/backend/.env.${DEPLOY_ENV}" ]]; then
        error "Backend environment file backend/.env.${DEPLOY_ENV} not found"
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Backup database and volumes
backup_data() {
    if [[ "$BACKUP_ENABLED" != "true" ]]; then
        log "Backup disabled, skipping..."
        return 0
    fi
    
    log "Creating backup..."
    
    BACKUP_DIR="$PROJECT_ROOT/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    if docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" ps | grep -q postgres; then
        log "Backing up PostgreSQL database..."
        docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" exec -T db \
            pg_dump -U postgres -d agridb > "$BACKUP_DIR/database.sql"
    fi
    
    # Backup uploaded files and volumes
    log "Backing up volumes..."
    docker run --rm \
        -v agridao_postgres_data:/source:ro \
        -v "$BACKUP_DIR":/backup \
        alpine tar czf /backup/postgres_data.tar.gz -C /source .
    
    success "Backup created at $BACKUP_DIR"
    echo "$BACKUP_DIR" > "$PROJECT_ROOT/.last_backup"
}

# Build images
build_images() {
    log "Building production images..."
    
    cd "$PROJECT_ROOT"
    
    # Copy environment files
    cp ".env.${DEPLOY_ENV}" .env
    cp "backend/.env.${DEPLOY_ENV}" backend/.env
    
    # Build frontend
    log "Building frontend..."
    docker build -f Dockerfile.prod -t agridao-frontend:latest .
    
    # Build backend
    log "Building backend..."
    docker build -f backend/Dockerfile -t agridao-backend:latest ./backend
    
    success "Images built successfully"
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    # Start database if not running
    if ! docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" ps | grep -q db; then
        log "Starting database for migrations..."
        docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" up -d db
        sleep 10
    fi
    
    # Run migrations
    docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" exec -T backend \
        alembic upgrade head
    
    success "Database migrations completed"
}

# Health check function
health_check() {
    local service_url=$1
    local max_attempts=30
    local attempt=1
    
    log "Performing health check on $service_url"
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "$service_url/health" > /dev/null; then
            success "Health check passed"
            return 0
        fi
        
        log "Health check attempt $attempt/$max_attempts failed, retrying in 10 seconds..."
        sleep 10
        ((attempt++))
    done
    
    error "Health check failed after $max_attempts attempts"
    return 1
}

# Blue-green deployment
blue_green_deploy() {
    log "Starting blue-green deployment..."
    
    # Determine current and next environments
    CURRENT_ENV="blue"
    NEXT_ENV="green"
    
    if docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" ps | grep -q green; then
        CURRENT_ENV="green"
        NEXT_ENV="blue"
    fi
    
    log "Current environment: $CURRENT_ENV"
    log "Deploying to: $NEXT_ENV"
    
    # Deploy to next environment
    COMPOSE_PROJECT_NAME="agridao_${NEXT_ENV}" \
    docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" \
        -f "$PROJECT_ROOT/docker-compose.${NEXT_ENV}.yml" up -d
    
    # Wait for services to be ready
    sleep 20
    
    # Health check
    if ! health_check "http://localhost:8001"; then
        error "Health check failed for $NEXT_ENV environment"
        
        # Rollback
        warning "Rolling back $NEXT_ENV environment"
        COMPOSE_PROJECT_NAME="agridao_${NEXT_ENV}" \
        docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" \
            -f "$PROJECT_ROOT/docker-compose.${NEXT_ENV}.yml" down
        
        exit 1
    fi
    
    # Switch traffic to new environment
    log "Switching traffic to $NEXT_ENV environment"
    
    # Update nginx configuration or load balancer
    # This is a placeholder - implement based on your infrastructure
    switch_traffic "$NEXT_ENV"
    
    # Wait a bit to ensure traffic is flowing
    sleep 30
    
    # Final health check
    if ! health_check "http://localhost:8000"; then
        error "Final health check failed"
        # Rollback traffic
        switch_traffic "$CURRENT_ENV"
        exit 1
    fi
    
    # Shutdown old environment
    log "Shutting down $CURRENT_ENV environment"
    COMPOSE_PROJECT_NAME="agridao_${CURRENT_ENV}" \
    docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" \
        -f "$PROJECT_ROOT/docker-compose.${CURRENT_ENV}.yml" down
    
    success "Blue-green deployment completed successfully"
}

# Switch traffic function (implement based on your load balancer)
switch_traffic() {
    local target_env=$1
    log "Switching traffic to $target_env"
    
    # Update nginx upstream or load balancer configuration
    # This is a placeholder implementation
    if [[ "$target_env" == "blue" ]]; then
        # Point to blue environment (port 8001)
        sed -i 's/server backend_green:8000/server backend_blue:8000/g' \
            "$PROJECT_ROOT/nginx/nginx.conf"
    else
        # Point to green environment (port 8002)
        sed -i 's/server backend_blue:8000/server backend_green:8000/g' \
            "$PROJECT_ROOT/nginx/nginx.conf"
    fi
    
    # Reload nginx
    docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" exec nginx \
        nginx -s reload
}

# Rolling deployment (alternative to blue-green)
rolling_deploy() {
    log "Starting rolling deployment..."
    
    # Update images in-place
    docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" pull
    docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" up -d
    
    # Health check
    if ! health_check "http://localhost:8000"; then
        error "Rolling deployment health check failed"
        exit 1
    fi
    
    success "Rolling deployment completed successfully"
}

# Rollback function
rollback() {
    log "Starting rollback procedure..."
    
    # Find last backup
    if [[ -f "$PROJECT_ROOT/.last_backup" ]]; then
        BACKUP_DIR=$(cat "$PROJECT_ROOT/.last_backup")
        
        if [[ -d "$BACKUP_DIR" ]]; then
            log "Rolling back to backup: $BACKUP_DIR"
            
            # Stop services
            docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" down
            
            # Restore database
            if [[ -f "$BACKUP_DIR/database.sql" ]]; then
                log "Restoring database..."
                docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" up -d db
                sleep 10
                cat "$BACKUP_DIR/database.sql" | \
                    docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" exec -T db \
                    psql -U postgres -d agridb
            fi
            
            # Restore volumes
            if [[ -f "$BACKUP_DIR/postgres_data.tar.gz" ]]; then
                log "Restoring volumes..."
                docker run --rm \
                    -v agridao_postgres_data:/target \
                    -v "$BACKUP_DIR":/backup \
                    alpine tar xzf /backup/postgres_data.tar.gz -C /target
            fi
            
            success "Rollback completed"
        else
            error "Backup directory not found: $BACKUP_DIR"
            exit 1
        fi
    else
        error "No backup found for rollback"
        exit 1
    fi
}

# Cleanup old images and containers
cleanup() {
    log "Cleaning up old images and containers..."
    
    # Remove old images (keep last 3 versions)
    docker image prune -f
    
    # Remove unused containers
    docker container prune -f
    
    # Remove unused volumes (be careful with this in production)
    # docker volume prune -f
    
    success "Cleanup completed"
}

# Main deployment function
main() {
    log "Starting AgriDAO deployment (Environment: $DEPLOY_ENV, Type: $DEPLOY_TYPE)"
    
    case "$1" in
        "deploy")
            check_prerequisites
            backup_data
            build_images
            run_migrations
            
            if [[ "$DEPLOY_TYPE" == "blue-green" ]]; then
                blue_green_deploy
            else
                rolling_deploy
            fi
            
            cleanup
            success "Deployment completed successfully!"
            ;;
        
        "rollback")
            rollback
            ;;
        
        "health")
            health_check "${2:-http://localhost:8000}"
            ;;
        
        "backup")
            backup_data
            ;;
        
        *)
            echo "Usage: $0 {deploy|rollback|health|backup} [environment] [deploy_type]"
            echo "  deploy     - Deploy the application"
            echo "  rollback   - Rollback to previous version"
            echo "  health     - Check application health"
            echo "  backup     - Create backup only"
            echo ""
            echo "Environment: production, staging (default: production)"
            echo "Deploy type: blue-green, rolling (default: blue-green)"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"