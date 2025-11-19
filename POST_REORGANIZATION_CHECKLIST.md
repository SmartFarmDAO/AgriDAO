# Post-Reorganization Checklist

## ✅ Completed

- [x] Created `frontend/` directory
- [x] Moved all source code to `frontend/src/`
- [x] Moved public assets to `frontend/public/`
- [x] Moved E2E tests to `frontend/e2e/`
- [x] Moved all configuration files to `frontend/`
- [x] Moved Docker files to `frontend/`
- [x] Moved environment files to `frontend/`
- [x] Created `frontend/README.md`
- [x] Created `frontend/.gitignore`
- [x] Updated main `README.md`
- [x] Created reorganization documentation

## 🔄 Pending (Required)

### 1. Update Docker Compose Files

#### `docker-compose.yml`
```yaml
# Find and update:
frontend:
  build:
    context: ./frontend  # ← Change from . to ./frontend
    dockerfile: Dockerfile
  volumes:
    - ./frontend:/app  # ← Update volume paths
```

#### `docker-compose.prod.yml`
```yaml
# Find and update:
frontend:
  build:
    context: ./frontend  # ← Change from . to ./frontend
    dockerfile: Dockerfile.prod
```

### 2. Update CI/CD Workflows

#### `.github/workflows/ci.yml`
```yaml
# Add working-directory to frontend jobs:
- name: Install dependencies
  working-directory: ./frontend  # ← Add this
  run: npm install

- name: Run tests
  working-directory: ./frontend  # ← Add this
  run: npm test

- name: Build
  working-directory: ./frontend  # ← Add this
  run: npm run build
```

### 3. Update Deployment Scripts

Check these files and update paths if needed:
- [ ] `scripts/deploy.sh`
- [ ] `scripts/integration-test.sh`
- [ ] `scripts/validate-system.sh`

Look for references to:
- `npm install` → `cd frontend && npm install`
- `npm run build` → `cd frontend && npm run build`
- Docker build contexts

### 4. Test the New Structure

```bash
# Test 1: Frontend development
cd frontend
npm install
npm run dev
# ✓ Should start on http://localhost:5173

# Test 2: Frontend tests
npm test
npm run test:e2e
# ✓ All tests should pass

# Test 3: Frontend build
npm run build
# ✓ Should create dist/ directory

# Test 4: Backend (unchanged)
cd ../backend
docker-compose up
# ✓ Should start on http://localhost:8000

# Test 5: Full stack
# Terminal 1:
cd frontend && npm run dev
# Terminal 2:
cd backend && docker-compose up
# ✓ Both should work together
```

## 📝 Optional Improvements

### 1. Add Workspace Configuration (Optional)

Create `package.json` in root for monorepo setup:
```json
{
  "name": "agridao",
  "private": true,
  "workspaces": [
    "frontend",
    "mobile"
  ]
}
```

### 2. Update .gitignore (Optional)

Add to root `.gitignore`:
```
# Frontend
frontend/node_modules
frontend/dist
frontend/.env.local
```

### 3. Add VS Code Workspace (Optional)

Create `.vscode/agridao.code-workspace`:
```json
{
  "folders": [
    {
      "name": "Frontend",
      "path": "../frontend"
    },
    {
      "name": "Backend",
      "path": "../backend"
    },
    {
      "name": "Root",
      "path": ".."
    }
  ]
}
```

## 🧪 Verification Commands

Run these to verify everything works:

```bash
# 1. Check structure
ls -la frontend/
ls -la frontend/src/
ls -la frontend/public/

# 2. Check dependencies
cd frontend
cat package.json
npm list --depth=0

# 3. Check configuration
ls -la *.config.*
cat vite.config.ts

# 4. Test development
npm run dev

# 5. Test build
npm run build
ls -la dist/

# 6. Test tests
npm test
npm run test:e2e
```

## 📊 Success Criteria

- [ ] Frontend dev server starts successfully
- [ ] All tests pass
- [ ] Production build completes
- [ ] Backend still works unchanged
- [ ] Docker compose builds successfully
- [ ] CI/CD pipeline passes
- [ ] No broken imports or paths
- [ ] Documentation is accurate

## 🆘 Troubleshooting

### Issue: npm install fails
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: Import paths broken
Check that all imports in `src/` use relative paths:
```typescript
// ✓ Correct
import { Button } from '@/components/ui/button'
import { api } from '@/lib/api'

// ✗ Wrong
import { Button } from 'components/ui/button'
```

### Issue: Docker build fails
Update docker-compose.yml:
```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
```

### Issue: Tests fail
```bash
cd frontend
npm run test -- --clearCache
npm test
```

## 📞 Support

If you encounter issues:

1. Check `REORGANIZATION.md` for details
2. Review `frontend/README.md`
3. Verify all files are in `frontend/`
4. Check Docker compose configuration
5. Review CI/CD workflows

## ✅ Sign-off

Once all pending items are complete:

- [ ] Docker compose updated and tested
- [ ] CI/CD workflows updated and passing
- [ ] Deployment scripts updated
- [ ] Full stack tested locally
- [ ] Documentation reviewed
- [ ] Team notified of changes

**Completed by**: _________________
**Date**: _________________
**Verified by**: _________________
