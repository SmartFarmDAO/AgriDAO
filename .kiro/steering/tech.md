# Tech Stack & Build System

## Backend (Python/FastAPI)

**Framework**: FastAPI 0.111+ with Python 3.12+
**Database**: PostgreSQL 15+ (SQLAlchemy ORM, Alembic migrations)
**Cache**: Redis 7+
**Authentication**: JWT tokens with passlib bcrypt
**File Upload**: Pillow for image processing, aiofiles for async I/O

### Key Libraries
- `fastapi` - Web framework
- `sqlalchemy` - ORM and database toolkit
- `alembic` - Database migrations
- `pydantic` - Data validation
- `redis` - Caching layer
- `pytest` - Testing framework
- `uvicorn` - ASGI server

### Common Commands
```bash
# Development
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "description"

# Testing
pytest
pytest -v  # verbose
pytest --cov  # with coverage

# Create admin user
python create_admin.py
```

### Code Style
- Black formatter (line length 100)
- isort for imports
- Type hints encouraged
- Async/await for I/O operations

## Frontend (React/TypeScript)

**Framework**: React 18 with TypeScript
**Build Tool**: Vite 5
**UI Library**: shadcn/ui + Tailwind CSS 3
**State Management**: Zustand + TanStack Query (React Query)
**Routing**: React Router v6
**Forms**: React Hook Form + Zod validation
**Blockchain**: wagmi, RainbowKit, ethers.js

### Key Libraries
- `react` + `react-dom` - UI framework
- `typescript` - Type safety
- `vite` - Build tool and dev server
- `tailwindcss` - Utility-first CSS
- `@tanstack/react-query` - Server state management
- `zustand` - Client state management
- `react-router-dom` - Routing
- `react-hook-form` - Form handling
- `zod` - Schema validation
- `axios` - HTTP client
- `@rainbow-me/rainbowkit` - Wallet connection
- `wagmi` - Ethereum hooks
- `framer-motion` - Animations

### Common Commands
```bash
# Development
cd frontend
npm install
npm run dev  # Starts on http://localhost:5173

# Build
npm run build
npm run preview  # Preview production build

# Testing
npm test  # Unit tests with Vitest
npm run test:e2e  # E2E tests with Playwright
npm run test:coverage  # Coverage report

# Linting & Type Checking
npm run lint
npm run typecheck
npm run format
```

### Code Style
- ESLint for linting
- Prettier for formatting
- Functional components with hooks
- TypeScript strict mode
- Component composition over inheritance

## Blockchain (Solidity/Hardhat)

**Framework**: Hardhat
**Language**: Solidity 0.8.20
**Network**: Ethereum (Sepolia testnet, local Hardhat network)

### Common Commands
```bash
cd blockchain
npm install
npx hardhat compile
npx hardhat test
npx hardhat node  # Local blockchain
npx hardhat run scripts/deploy.js --network localhost
```

## Mobile (React Native/Expo)

**Framework**: React Native with Expo
**Language**: TypeScript

### Common Commands
```bash
cd mobile
npm install
npm start  # Start Expo dev server
```

## Docker & Deployment

### Development
```bash
# Start all services
docker-compose up -d

# Rebuild specific service
docker-compose up -d --build backend

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down
```

### Production
```bash
# Production build
docker-compose -f docker-compose.yml -f deployment/docker/docker-compose.prod.yml up -d

# Lightsail deployment
bash deployment/lightsail/lightsail-setup.sh
```

## Environment Variables

### Backend (.env)
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT secret
- `CORS_ORIGINS` - Allowed origins (comma-separated)

### Frontend (.env)
- `VITE_API_URL` - Backend API URL
- `VITE_FIREBASE_*` - Firebase config (optional)

## Testing Strategy

- **Backend**: pytest with async support, fixtures in conftest.py
- **Frontend**: Vitest for unit tests, Playwright for E2E
- **Blockchain**: Hardhat test framework
- Test files colocated with source or in dedicated test directories

## API Documentation

FastAPI auto-generates OpenAPI docs at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
