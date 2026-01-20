# AgriDAO Lightsail Deployment Guide

## Instance Specifications
- **RAM**: 2 GB
- **vCPUs**: 2
- **Storage**: 60 GB SSD
- **OS**: Ubuntu 24.04 LTS (Noble)
- **Cost**: ~$10/month

## Step-by-Step Deployment

### 1. Setup Static IP (Important!)

Before starting, attach a static IP to your Lightsail instance:
1. Go to Lightsail Console → Networking → Create static IP
2. Attach it to your instance
3. Use this static IP for all configurations below

### 2. Initial Server Setup

SSH into your Lightsail instance:
```bash
ssh ubuntu@<your-static-ip>
```
*Replace `<your-static-ip>` with the static IP from step 1*

Download and run the setup script:
```bash
wget https://raw.githubusercontent.com/<your-github-username>/AgriDAO/main/deployment/lightsail/lightsail-setup.sh
chmod +x lightsail-setup.sh
./lightsail-setup.sh
```
*Replace `<your-github-username>` with your actual GitHub username*

**Important**: Log out and log back in after the script completes!

### 3. Clone Your Repository

```bash
cd ~
git clone https://github.com/<your-github-username>/AgriDAO.git agridao
cd agridao
```
*Replace `<your-github-username>` with your actual GitHub username*

### 4. Configure Environment Variables

Create a `.env` file:
```bash
nano .env
```

Add the following (replace with your actual values):
```env
# Database
DB_PASSWORD=your_secure_db_password_here

# Backend
SECRET_KEY=your_secret_key_min_32_chars_long
JWT_SECRET=your_jwt_secret_key_here
ENVIRONMENT=production

# Blockchain
BLOCKCHAIN_RPC_URL=http://blockchain:8545
PRIVATE_KEY=your_blockchain_private_key

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Frontend
VITE_API_URL=http://<your-lightsail-ip>:8000
VITE_BLOCKCHAIN_RPC=http://<your-lightsail-ip>:8545
```

Save and exit (Ctrl+X, then Y, then Enter)

### 5. Build and Start Services

Use the optimized docker-compose file:
```bash
# Copy the optimized config from deployment directory
cp deployment/lightsail/docker-compose.lightsail.yml docker-compose.yml

# Build and start services
docker-compose up -d --build
```

### 6. Monitor Services

Check if all services are running:
```bash
docker-compose ps
```

View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

Check resource usage:
```bash
docker stats
```

### 7. Initialize Database

Run database migrations:
```bash
docker-compose exec backend python -m alembic upgrade head
```

Create admin user (optional, if script exists):
```bash
docker-compose exec backend python scripts/create_admin.py
```

### 8. Verify Deployment

Test the services:
```bash
# Backend API check
curl http://localhost:8000/docs

# Frontend
curl http://localhost:3000

# Database connection
docker-compose exec db psql -U postgres -d agridao -c "SELECT version();"
```

Access your application:
- Frontend: `http://<your-static-ip>:3000`
- Backend API: `http://<your-static-ip>:8000`
- API Docs: `http://<your-static-ip>:8000/docs`

## Maintenance Commands

### Update Application
```bash
cd ~/agridao
git pull origin main
docker-compose down
docker-compose up -d --build
```

### Backup Database
```bash
docker-compose exec db pg_dump -U postgres agridao > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
cat backup_20251201.sql | docker-compose exec -T db psql -U postgres agridao
```

### View Logs
```bash
# Last 100 lines
docker-compose logs --tail=100

# Follow logs
docker-compose logs -f backend

# Specific time range
docker-compose logs --since 30m
```

### Restart Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart backend
```

### Clean Up
```bash
# Remove stopped containers
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Clean up unused images
docker system prune -a
```

## Performance Monitoring

### Check Memory Usage
```bash
free -h
htop
docker stats
```

### Check Disk Usage
```bash
df -h
du -sh ~/agridao/*
```

### Monitor Logs
```bash
# View container logs
docker-compose logs -f
```

## Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs <service-name>

# Check if port is in use
sudo netstat -tulpn | grep <port>

# Restart service
docker-compose restart <service-name>
```

### Out of Memory
```bash
# Check memory
free -h

# Check swap
swapon --show

# Restart services to free memory
docker-compose restart
```

### Database Connection Issues
```bash
# Check if database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Connect to database
docker-compose exec db psql -U postgres -d agridao
```

### Frontend Not Loading
```bash
# Rebuild frontend
docker-compose up -d --build frontend

# Check frontend logs
docker-compose logs frontend

# Verify frontend is running
docker-compose ps frontend
```

## Security Recommendations

1. **Change default passwords** in `.env` file
2. **Setup SSL/TLS** using Let's Encrypt:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```
3. **Configure firewall** properly (done by setup script)
4. **Regular updates**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
5. **Enable automatic security updates**:
   ```bash
   sudo apt install unattended-upgrades
   sudo dpkg-reconfigure -plow unattended-upgrades
   ```

## Useful Links

- Lightsail Console: https://lightsail.aws.amazon.com/
- Your Application: http://<your-static-ip>:3000
- API Documentation: http://<your-static-ip>:8000/docs

## Support

If you encounter issues:
1. Check logs: `docker-compose logs`
2. Check system resources: `htop` or `docker stats`
3. Restart services: `docker-compose restart`
4. Review this guide for troubleshooting steps
