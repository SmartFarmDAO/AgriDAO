# AgriDAO Lightsail Quick Start

## 🚀 One-Command Setup

```bash
# On your Lightsail instance
wget -O - https://raw.githubusercontent.com/<your-username>/AgriDAO/main/deployment/lightsail/lightsail-setup.sh | bash
```

## 📋 Manual Setup (5 Steps)

### 1️⃣ SSH into Lightsail
```bash
ssh ubuntu@<your-lightsail-ip>
```

### 2️⃣ Run Setup Script
```bash
curl -fsSL https://raw.githubusercontent.com/<your-username>/AgriDAO/main/deployment/lightsail/lightsail-setup.sh -o setup.sh
chmod +x setup.sh
./setup.sh
```

**⚠️ IMPORTANT**: Log out and log back in after setup!

### 3️⃣ Clone Repository
```bash
git clone https://github.com/<your-username>/AgriDAO.git ~/agridao
cd ~/agridao
```

### 4️⃣ Configure Environment
```bash
cp deployment/lightsail/.env.lightsail.example .env
nano .env
```

Update these values:
- `DB_PASSWORD` - Strong database password
- `SECRET_KEY` - Random 32+ character string
- `JWT_SECRET` - Random 32+ character string
- `VITE_API_URL` - Replace `<YOUR_LIGHTSAIL_IP>` with your actual IP
- `VITE_BLOCKCHAIN_RPC` - Replace `<YOUR_LIGHTSAIL_IP>` with your actual IP

### 5️⃣ Deploy
```bash
chmod +x deployment/scripts/deploy.sh
./deployment/scripts/deploy.sh
```

## ✅ Verify Deployment

```bash
# Check services
docker-compose ps

# View logs
docker-compose logs -f

# Test backend
curl http://localhost:8000/health

# Test frontend
curl http://localhost:80
```

## 🌐 Access Your Application

- **Frontend**: `http://<your-lightsail-ip>`
- **Backend API**: `http://<your-lightsail-ip>:8000`
- **API Docs**: `http://<your-lightsail-ip>:8000/docs`

## 🔧 Common Commands

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Update and redeploy
./deployment/scripts/deploy.sh

# Check resource usage
docker stats
htop

# Backup database
docker-compose exec db pg_dump -U postgres agridao > backup.sql
```

## 🆘 Troubleshooting

### Services won't start
```bash
docker-compose logs <service-name>
docker-compose restart <service-name>
```

### Out of memory
```bash
free -h
docker-compose restart
```

### Can't connect to database
```bash
docker-compose logs db
docker-compose restart db
```

## 📚 Full Documentation

See `LIGHTSAIL_DEPLOYMENT.md` for complete documentation.

## 🔐 Security Checklist

- [ ] Changed all default passwords in `.env`
- [ ] Updated `SECRET_KEY` and `JWT_SECRET`
- [ ] Configured firewall (done by setup script)
- [ ] Setup SSL certificate (optional, see SSL_SETUP.md)
- [ ] Enabled automatic security updates

## 💡 Tips

1. **Monitor resources**: Run `htop` to watch CPU/RAM usage
2. **Check logs regularly**: `docker-compose logs --tail=100`
3. **Backup database weekly**: Use the backup command above
4. **Keep system updated**: `sudo apt update && sudo apt upgrade -y`
5. **Use PM2 for Node processes**: Already installed by setup script

## 📞 Need Help?

1. Check logs: `docker-compose logs`
2. Check system resources: `htop`
3. Review `LIGHTSAIL_DEPLOYMENT.md`
4. Check Docker status: `docker ps -a`
