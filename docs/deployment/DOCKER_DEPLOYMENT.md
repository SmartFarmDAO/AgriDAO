# Docker Deployment Guide

## Development Environment

### Quick Start
```bash
# Start all services (frontend, backend, database, redis)
docker-compose up --build

# Access services:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

### Development Services
- **Frontend**: React + Vite dev server with hot reload
- **Backend**: FastAPI with auto-reload
- **Database**: PostgreSQL 16
- **Cache**: Redis 7

### Environment Setup
1. Copy environment files:
   ```bash
   cp .env.example .env
   cp backend/.env.example backend/.env
   ```

2. Update environment variables in both files

3. Start services:
   ```bash
   docker-compose up -d
   ```

## Production Environment

### Quick Start
```bash
# Build and start production services
docker-compose -f docker-compose.prod.yml up --build -d

# Access services:
# - Application: http://localhost (port 80)
# - Backend API: http://localhost:8000
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3001
```

### Production Services
- **Frontend**: Nginx serving optimized React build
- **Backend**: FastAPI production server
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Reverse Proxy**: Nginx with SSL support
- **Monitoring**: Prometheus + Grafana

### Production Architecture
```
Internet → Nginx (Port 80/443)
           ├─→ Frontend (Port 80) → Static React App
           └─→ Backend (Port 8000) → FastAPI API
                ├─→ PostgreSQL (Port 5432)
                └─→ Redis (Port 6379)
```

### Environment Variables
Set these in your environment or `.env` file:
```bash
# Required
JWT_SECRET=your-secret-key
STRIPE_SECRET_KEY=your-stripe-key
STRIPE_WEBHOOK_SECRET=your-webhook-secret

# Optional
PLATFORM_FEE_RATE=0.10
GRAFANA_PASSWORD=admin
```

### SSL Configuration
1. Place SSL certificates in `./ssl/` directory:
   - `cert.pem` - SSL certificate
   - `key.pem` - Private key

2. Update `nginx.prod.conf` to enable HTTPS

### Monitoring
- **Prometheus**: Metrics collection at http://localhost:9090
- **Grafana**: Dashboards at http://localhost:3001
  - Default credentials: admin / (set via GRAFANA_PASSWORD)

## Useful Commands

### Development
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f
docker-compose logs -f frontend
docker-compose logs -f backend

# Restart a service
docker-compose restart frontend

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Production
```bash
# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Update services
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Stop production stack
docker-compose -f docker-compose.prod.yml down
```

### Database Management
```bash
# Access PostgreSQL
docker-compose exec db psql -U postgres -d agridb

# Backup database
docker-compose exec db pg_dump -U postgres agridb > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres agridb < backup.sql
```

### Troubleshooting
```bash
# Check service status
docker-compose ps

# Inspect a container
docker-compose exec frontend sh
docker-compose exec backend sh

# View resource usage
docker stats

# Clean up unused resources
docker system prune -a
```
