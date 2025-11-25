# Project Structure

## 📂 Main Folders

### `frontend/` - React Application
```
frontend/
├── src/
│   ├── components/    # Reusable UI components
│   ├── pages/         # Page components (routes)
│   ├── hooks/         # Custom React hooks
│   ├── lib/           # Utilities & helpers
│   └── services/      # API calls
├── public/            # Static files
└── e2e/               # End-to-end tests
```

### `backend/` - FastAPI Server
```
backend/
├── app/
│   ├── routers/       # API endpoints
│   ├── models.py      # Database models
│   ├── schemas.py     # Request/response schemas
│   └── main.py        # App entry point
├── tests/             # Backend tests
└── utils/             # Helper scripts
```

### `docs/` - Documentation
```
docs/
├── reports/           # Academic & project reports
├── fixes/             # Bug fix documentation
├── guides/            # How-to guides
└── troubleshooting/   # Common issues & solutions
```

### `scripts/` - Automation
```
scripts/
├── deploy.sh          # Deployment automation
├── integration-test.sh # System tests
└── test-marketplace.sh # Marketplace tests
```

## 🎯 Key Files

| File | Purpose |
|------|---------|
| `QUICK_START.md` | Get started in 3 steps |
| `README.md` | Full project documentation |
| `docker-compose.yml` | Development environment |
| `docker-compose.prod.yml` | Production environment |

## 🔍 Finding Things

- **API endpoints**: `backend/app/routers/`
- **UI components**: `frontend/src/components/`
- **Database models**: `backend/app/models.py`
- **Tests**: `frontend/e2e/` and `backend/tests/`
- **Configuration**: `.env` files in frontend/ and backend/
