# AgriDAO Deployment

This directory contains all deployment configurations and scripts for AgriDAO.

## 📁 Directory Structure

```
deployment/
├── docker/              # Docker configurations
│   ├── docker-compose.prod.yml
│   ├── docker-compose.override.yml
│   ├── nginx.prod.conf
│   ├── prometheus.yml
│   └── load-tests.yml
├── lightsail/          # AWS Lightsail deployment
│   ├── lightsail-setup.sh
│   ├── docker-compose.lightsail.yml
│   └── .env.lightsail.example
└── scripts/            # Deployment scripts
    ├── deploy.sh
    ├── check_admin.sh
    ├── test-new-features.sh
    └── find-hardcoded-text.sh
```

## 🚀 Deployment Options

### 1. Local Development (Docker)

**Best for**: Development and testing

```bash
# From project root
docker-compose up -d
```

**Access**:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Documentation**: [Docker Deployment Guide](../docs/deployment/DOCKER_DEPLOYMENT.md)

### 2. AWS Lightsail (2GB Instance)

**Best for**: Development/staging server

**Quick Setup**:
```bash
# On your Lightsail instance
wget https://raw.githubusercontent.com/yourusername/AgriDAO/main/deployment/lightsail/lightsail-setup.sh
chmod +x lightsail-setup.sh
./lightsail-setup.sh
```

**Documentation**: [Lightsail Deployment Guide](../docs/deployment/LIGHTSAIL_DEPLOYMENT.md)

### 3. Production Deployment

**Best for**: Production environment

```bash
# Use production docker-compose
docker-compose -f deployment/docker/docker-compose.prod.yml up -d
```

**Documentation**: [Production Deployment Guide](../docs/deployment/PRODUCTION.md)

## 📋 Pre-Deployment Checklist

### Environment Configuration
- [ ] Copy `.env.example` to `.env`
- [ ] Set `DB_PASSWORD` to a strong password
- [ ] Generate and set `SECRET_KEY` (32+ characters)
- [ ] Generate and set `JWT_SECRET`
- [ ] Configure `SMTP_*` variables for email
- [ ] Set `VITE_API_URL` to your backend URL
- [ ] Set `VITE_BLOCKCHAIN_RPC` to your blockchain RPC

### Security
- [ ] Change all default passwords
- [ ] Configure firewall rules
- [ ] Setup SSL/TLS certificates (production)
- [ ] Enable CORS for your domain only
- [ ] Review and update security settings

### Infrastructure
- [ ] Ensure sufficient resources (2GB RAM minimum)
- [ ] Configure backup strategy
- [ ] Setup monitoring (optional)
- [ ] Configure log rotation
- [ ] Test database connectivity

## 🔧 Configuration Files

### Docker Compose Files

| File | Purpose | Use Case |
|------|---------|----------|
| `docker-compose.yml` | Base configuration | Local development |
| `docker-compose.prod.yml` | Production overrides | Production deployment |
| `docker-compose.lightsail.yml` | Optimized for 2GB RAM | AWS Lightsail |
| `docker-compose.override.yml` | Local overrides | Development customization |

### Environment Files

| File | Purpose |
|------|---------|
| `.env.example` | Template with all variables |
| `.env.lightsail.example` | Lightsail-specific template |
| `.env` | Your actual configuration (not in git) |

## 🛠️ Deployment Scripts

### `scripts/deploy.sh`
Automated deployment script that:
- Pulls latest code
- Builds frontend
- Starts Docker services
- Runs database migrations
- Shows deployment status

**Usage**:
```bash
cd deployment/scripts
chmod +x deploy.sh
./deploy.sh
```

### `lightsail/lightsail-setup.sh`
Initial server setup script that:
- Installs Docker, Node.js, Python
- Configures firewall
- Sets up swap space
- Optimizes system for 2GB RAM

**Usage**:
```bash
chmod +x lightsail-setup.sh
./lightsail-setup.sh
```

### `scripts/check_admin.sh`
Checks admin user status and permissions.

### `scripts/test-new-features.sh`
Tests newly deployed features.

### `scripts/find-hardcoded-text.sh`
Finds hardcoded text that should be translated.

## 📊 Resource Requirements

### Minimum (Development)
- **RAM**: 1 GB
- **CPU**: 1 vCPU
- **Storage**: 20 GB
- **Network**: 512 GB transfer

### Recommended (Staging/Production)
- **RAM**: 2 GB
- **CPU**: 2 vCPUs
- **Storage**: 60 GB SSD
- **Network**: 1 TB transfer

### Service Resource Allocation (2GB Instance)

| Service | Memory Limit | CPU Limit |
|---------|-------------|-----------|
| PostgreSQL | 512 MB | 0.5 |
| Redis | 128 MB | 0.25 |
| Backend | 512 MB | 0.75 |
| Blockchain | 256 MB | 0.5 |
| Frontend | 256 MB | 0.5 |
| Nginx | 128 MB | 0.25 |

## 🔍 Health Checks

After deployment, verify all services:

```bash
# Check service status
docker-compose ps

# Test backend
curl http://localhost:8000/health

# Test frontend
curl http://localhost:80

# Check database
docker-compose exec db psql -U postgres -d agridao -c "SELECT version();"

# View logs
docker-compose logs -f
```

## 📈 Monitoring

### Resource Monitoring
```bash
# System resources
htop
free -h
df -h

# Docker resources
docker stats

# Service logs
docker-compose logs --tail=100 -f
```

### Application Monitoring
- **Prometheus**: http://localhost:9090 (if enabled)
- **Backend Logs**: `docker-compose logs backend`
- **Frontend Logs**: `docker-compose logs frontend`
- **Database Logs**: `docker-compose logs db`

## 🔄 Updates and Maintenance

### Update Application
```bash
cd ~/agridao
git pull origin main
./deployment/scripts/deploy.sh
```

### Backup Database
```bash
docker-compose exec db pg_dump -U postgres agridao > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
cat backup_20240101.sql | docker-compose exec -T db psql -U postgres agridao
```

### Clean Up
```bash
# Remove stopped containers
docker-compose down

# Remove unused images
docker system prune -a

# Remove volumes (WARNING: deletes data)
docker-compose down -v
```

## 🆘 Troubleshooting

### Services Won't Start
```bash
# Check logs
docker-compose logs <service-name>

# Check if ports are in use
sudo netstat -tulpn | grep <port>

# Restart service
docker-compose restart <service-name>
```

### Out of Memory
```bash
# Check memory usage
free -h
docker stats

# Restart services
docker-compose restart
```

### Database Connection Issues
```bash
# Check database status
docker-compose ps db

# View database logs
docker-compose logs db

# Connect to database
docker-compose exec db psql -U postgres -d agridao
```

## 📚 Additional Resources

- [Docker Deployment Guide](../docs/deployment/DOCKER_DEPLOYMENT.md)
- [Lightsail Deployment Guide](../docs/deployment/LIGHTSAIL_DEPLOYMENT.md)
- [Quick Start Guide](../docs/deployment/QUICK_START.md)
- [Troubleshooting Guide](../docs/troubleshooting/QUICK_FIX_GUIDE.md)

## 🤝 Support

Need help with deployment?
- Check the [documentation](../docs/deployment/)
- Open an [issue](https://github.com/yourusername/AgriDAO/issues)
- Contact the team

---

**Last Updated**: December 2024
