# Developer Cheat Sheet

## 🚀 Quick Commands

### Start Development
```bash
# Terminal 1: Frontend
cd frontend && npm run dev

# Terminal 2: Backend
cd backend && docker-compose up
```

### Testing
```bash
# Frontend tests
cd frontend
npm test                    # Unit tests
npm run test:e2e           # E2E tests
npm run test:coverage      # Coverage report

# Backend tests
cd backend
pytest                     # All tests
pytest tests/test_api.py   # Specific test
```

### Build & Deploy
```bash
# Frontend build
cd frontend && npm run build

# Production deployment
./scripts/deploy.sh deploy production

# Check system health
./scripts/integration-test.sh health
```

## 📁 Where to Find Things

| What | Where |
|------|-------|
| Add new page | `frontend/src/pages/` |
| Add UI component | `frontend/src/components/` |
| Add API endpoint | `backend/app/routers/` |
| Database models | `backend/app/models.py` |
| API schemas | `backend/app/schemas.py` |
| Tests | `frontend/e2e/` or `backend/tests/` |
| Documentation | `docs/` |

## 🔧 Common Tasks

### Add a New Feature
1. Create branch: `git checkout -b feature/your-feature`
2. Add code in appropriate folder (see table above)
3. Write tests
4. Run tests: `npm test` or `pytest`
5. Commit: `git commit -m "feat: your feature"`
6. Push: `git push origin feature/your-feature`

### Fix a Bug
1. Create branch: `git checkout -b fix/bug-name`
2. Fix the issue
3. Add test to prevent regression
4. Run tests
5. Commit: `git commit -m "fix: bug description"`
6. Push and create PR

### Add Database Model
1. Edit `backend/app/models.py`
2. Create migration: `alembic revision --autogenerate -m "description"`
3. Apply migration: `alembic upgrade head`
4. Update schemas in `backend/app/schemas.py`

### Add API Endpoint
1. Add route in `backend/app/routers/`
2. Add schema in `backend/app/schemas.py`
3. Test with: `curl http://localhost:8000/your-endpoint`
4. Add tests in `backend/tests/`

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5173 (frontend)
lsof -ti:5173 | xargs kill -9

# Kill process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9
```

### Docker Issues
```bash
# Clean restart
docker-compose down
docker-compose up --build

# Remove all containers
docker-compose down -v
```

### Database Issues
```bash
# Reset database
cd backend
rm agri.db
alembic upgrade head
python create_admin.py
```

### Frontend Build Issues
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

## 📚 Documentation Quick Links

- [Getting Started](./QUICK_START.md)
- [Project Structure](./STRUCTURE.md)
- [Full Documentation](./docs/INDEX.md)
- [API Docs](http://localhost:8000/docs) (when backend running)
- [Troubleshooting](./docs/troubleshooting/)

## 🔑 Environment Variables

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=your-key
```

### Backend (.env)
```bash
DATABASE_URL=postgresql://user:pass@localhost/agridao
JWT_SECRET=your-secret
REDIS_URL=redis://localhost:6379
```

## 💡 Pro Tips

- Use `npm run dev` for hot reload during development
- Check `http://localhost:8000/docs` for interactive API documentation
- Run tests before committing: `npm test && pytest`
- Use `git status` frequently to track changes
- Read error messages carefully - they usually tell you what's wrong!

## 🆘 Need Help?

1. Check [Troubleshooting](./docs/troubleshooting/)
2. Search [GitHub Issues](https://github.com/SmartFarmDAO/AgriDAO/issues)
3. Ask in team chat
4. Create new issue with details

---

**Remember**: When in doubt, check START_HERE.md!
