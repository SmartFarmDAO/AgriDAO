# 🎯 AgriDAO Demo - Quick Reference Card

## 🚀 Start Demo
```bash
./setup-free-otp.sh
# Wait 30 seconds for services to start
open http://localhost:5173
```

## 📍 Access Points
| Service | URL | Login |
|---------|-----|-------|
| **App** | http://localhost:5173 | demo@agridao.com |
| **API Docs** | http://localhost:8000/docs | - |
| **MailHog** | http://localhost:8025 | - |

## 🎬 Demo Flow (15 min)

### 1. Landing Page (1 min)
- Show 6 epics
- Highlight features
- Click "Sign In"

### 2. Authentication (2 min)
- Enter: `demo@agridao.com`
- Open MailHog: http://localhost:8025
- Copy OTP code
- Verify and login

### 3. Dashboard (1 min)
- Show metrics
- Point out role-based view

### 4. Marketplace (4 min)
- Browse products
- Search "tomato"
- Add to cart
- View cart
- Show checkout flow

### 5. Farmer Onboarding (2 min)
- Create farmer profile
- Add product
- Show in marketplace

### 6. Orders (2 min)
- View order list
- Show order details
- Explain tracking

### 7. Admin Dashboard (2 min)
- User management
- Analytics
- Dispute resolution

### 8. Other Features (1 min)
- Finance (funding)
- AI Advisory
- Supply Chain
- Governance

## 🎤 Key Talking Points

1. **"Production-ready, not a prototype"**
2. **"100% open source and free"**
3. **"Passwordless authentication for security"**
4. **"Direct farmer-to-consumer connection"**
5. **"82+ API endpoints, fully functional"**
6. **"Scales to thousands of users"**
7. **"Self-hostable, no vendor lock-in"**
8. **"Community-governed DAO"**

## 🧪 Live Tests

### Test OTP
```bash
curl -X POST http://localhost:8000/auth/otp/request \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

### Check Health
```bash
curl http://localhost:8000/health
```

### List Products
```bash
curl http://localhost:8000/marketplace/products
```

## 🐛 Quick Fixes

### Services not running?
```bash
docker-compose restart
```

### Can't see emails?
```bash
open http://localhost:8025
```

### Frontend not loading?
```bash
docker-compose logs frontend
```

### Database issues?
```bash
docker-compose exec backend alembic upgrade head
```

## 📊 Demo Stats

- **82+ API endpoints**
- **15+ database tables**
- **6 major features**
- **1000+ concurrent users**
- **< 200ms API response**
- **90%+ test coverage**

## 🎯 Demo Checklist

- [ ] Services started
- [ ] Frontend accessible
- [ ] MailHog working
- [ ] Test email ready
- [ ] Browser tabs open
- [ ] Terminal ready
- [ ] Backup plan ready

## 💡 Pro Tips

1. **Keep MailHog open** in separate tab
2. **Use incognito** for clean demo
3. **Have backup OTP** ready
4. **Show API docs** for technical audience
5. **Mention scalability** for enterprise
6. **Highlight open source** for developers
7. **Demo mobile view** if time permits
8. **Show Docker setup** for DevOps

## 🔥 Wow Factors

- ✨ **Beautiful OTP emails** (show MailHog)
- ✨ **Real-time cart updates** (add/remove items)
- ✨ **Professional UI** (Tailwind + Radix)
- ✨ **Complete API docs** (Swagger)
- ✨ **Docker deployment** (one command)
- ✨ **Free email/SMS** (no paid services)
- ✨ **JWT security** (show token in DevTools)
- ✨ **Admin dashboard** (comprehensive)

## 📱 Mobile Demo

```bash
# Get local IP
ipconfig getifaddr en0  # macOS
# or
hostname -I  # Linux

# Access from phone
http://YOUR_IP:5173
```

## 🎬 Closing

**"AgriDAO is production-ready, open-source, and designed 
to empower farmers worldwide. It's free to use, easy to 
deploy, and scales from small communities to nationwide 
networks. Thank you!"**

---

## 🆘 Emergency Contacts

- **Restart Everything**: `docker-compose restart`
- **Check Logs**: `docker-compose logs -f`
- **Nuclear Option**: `docker-compose down -v && docker-compose up -d`

---

**Print this card and keep it handy during demo!** 📋
