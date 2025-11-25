# AgriDAO - Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Install Dependencies
```bash
# Frontend
cd frontend
npm install

# Backend (in new terminal)
cd backend
pip install -r requirements.txt
```

### 2. Setup Environment
```bash
# Frontend - Copy and edit
cp frontend/.env.example frontend/.env

# Backend - Copy and edit
cp backend/.env.example backend/.env
```

### 3. Run the App
```bash
# Start backend (from backend folder)
docker-compose up

# Start frontend (from frontend folder)
npm run dev
```

**That's it!** Open http://localhost:5173

---

## 📁 Project Structure

```
AgriDAO/
├── frontend/          # React app (npm run dev)
├── backend/           # FastAPI server (docker-compose up)
├── docs/              # All documentation
├── scripts/           # Deployment & testing scripts
└── mobile/            # React Native app (future)
```

## 🔧 Common Commands

```bash
# Frontend
npm run dev            # Start dev server
npm run build          # Build for production
npm test               # Run tests

# Backend
docker-compose up      # Start all services
docker-compose down    # Stop all services
```

## 📚 Need Help?

- **Full Documentation**: [README.md](./README.md)
- **API Docs**: http://localhost:8000/docs (when backend running)
- **Troubleshooting**: [docs/troubleshooting/](./docs/troubleshooting/)

## 🐛 Issues?

1. Check [docs/troubleshooting/](./docs/troubleshooting/)
2. Verify `.env` files are configured
3. Ensure Docker is running
4. Check ports 5173 (frontend) and 8000 (backend) are free
