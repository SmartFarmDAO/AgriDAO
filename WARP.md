# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

AgriDAO is a production-ready blockchain-enabled agricultural marketplace connecting farmers with consumers, restaurants, and retailers. The stack consists of:
- **Frontend**: React 18 + TypeScript + Vite 5
- **Backend**: FastAPI (Python 3.11+) with PostgreSQL and Redis
- **Testing**: Vitest (unit), Playwright (E2E), pytest (backend)
- **Deployment**: Docker Compose with blue-green deployment support

## Common Development Commands

### Frontend Development

```bash
# Development
npm run dev                    # Start Vite dev server (http://localhost:5173)
npm run build                  # Production build with TypeScript compilation
npm run preview                # Preview production build locally

# Testing
npm test                       # Run Vitest unit tests with watch mode
npm run test:coverage          # Generate test coverage report
npm run test:ui                # Interactive Vitest UI
npm run test:e2e               # Run Playwright E2E tests (all browsers)
npm run test:e2e:ui            # Playwright UI mode for debugging
npm run test:e2e:headed        # Run E2E tests with browser visible
npm run test:security          # Security-specific E2E tests
npm run test:performance       # Performance and Core Web Vitals tests
npm run test:load              # Artillery load testing (1000+ users)

# Code Quality
npm run lint                   # ESLint analysis
npm run format                 # Prettier formatting
npm run format:check           # Check formatting without changes
npm run typecheck              # TypeScript type checking (no emit)
npm run analyze                # Bundle size analysis
```

### Backend Development

```bash
# Development (from backend/ directory)
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload  # Start FastAPI on http://localhost:8000

# Database Migrations (Alembic)
alembic upgrade head           # Apply all migrations
alembic downgrade -1           # Rollback one migration
alembic revision --autogenerate -m "description"  # Generate migration
alembic current                # Show current migration version

# Testing (from backend/ directory)
pytest                         # Run all backend tests
pytest -v                      # Verbose output
pytest -k test_name            # Run specific test
pytest --cov=app               # Run with coverage
pytest tests/test_auth_service.py  # Run specific test file
```

### Docker Development

```bash
# Full Stack Development
docker compose up --build      # Start all services (postgres, redis, backend, frontend, mailhog)
docker compose down            # Stop all services
docker compose down -v         # Stop and remove volumes (clean slate)

# Individual Services
docker compose up db           # Start only PostgreSQL
docker compose up redis        # Start only Redis
docker compose logs -f backend # Follow backend logs
docker compose exec backend bash  # Shell into backend container

# Production Deployment
docker compose -f docker-compose.prod.yml up --build -d
./scripts/deploy.sh deploy production blue-green
```

### Testing Commands

```bash
# Integration Testing
./scripts/integration-test.sh         # Full system integration tests
./scripts/integration-test.sh health  # Health check verification only
./scripts/validate-system.sh          # System validation

# Run Single E2E Test
npm run test:e2e -- e2e/auth.spec.ts
npm run test:e2e -- e2e/marketplace.spec.ts --headed

# Backend Single Test
cd backend
pytest tests/test_auth_service.py::test_user_registration
pytest tests/test_inventory_service.py -v
```

## Architecture Overview

### Frontend Architecture

The frontend follows a feature-based structure with clear separation of concerns:

**Key Patterns:**
- **Authentication**: Handled via `AuthProvider` context (`src/hooks/use-auth.tsx`) with JWT tokens stored securely
- **State Management**: 
  - Global state: Zustand stores (imported in components as needed)
  - Server state: TanStack Query for API data fetching/caching
  - Local state: React hooks
- **Routing**: React Router v6 with protected routes (see `src/App.tsx`)
- **API Communication**: Centralized API client in `src/lib/api.ts` with axios interceptors

**Directory Structure Logic:**
- `src/pages/`: Route-level components (one per URL path)
- `src/components/`: Reusable UI components
  - `src/components/layout/`: Layout wrapper components
  - `src/components/ui/`: Radix UI primitives (50+ components)
- `src/hooks/`: Custom React hooks for reusable logic
- `src/lib/`: Core utilities (API client, security, wallet integration)
- `src/services/`: Business logic services
- `src/utils/`: Helper functions and utilities
- `src/config/`: Configuration management (API endpoints, wagmi/Web3)

**Key Files:**
- `src/App.tsx`: Main application entry with routing and providers
- `src/hooks/use-auth.tsx`: Authentication state and logic
- `src/lib/api.ts`: Centralized API client with error handling
- `src/config/wagmi.ts`: Web3/blockchain configuration

### Backend Architecture

FastAPI backend with modular router-based structure:

**Key Patterns:**
- **Routers**: Each domain has its own router in `backend/app/routers/`
  - `auth.py`: Authentication (register, login, refresh tokens)
  - `commerce.py`: Product/marketplace operations
  - `orders.py`: Order management
  - `cart.py`: Shopping cart
  - `disputes.py`: Dispute resolution
  - `analytics.py`: System analytics
  - `health.py`: Health checks and monitoring
- **Services**: Business logic in `backend/app/services/`
- **Models**: SQLModel definitions in `backend/app/models.py`
- **Middleware**: Security, CSRF, rate limiting in `backend/app/middleware/`
- **Database**: PostgreSQL with SQLAlchemy ORM, Alembic migrations

**Key Files:**
- `backend/app/main.py`: FastAPI app initialization, middleware setup, router registration
- `backend/app/database.py`: Database connection and session management
- `backend/app/models.py`: Database models (SQLModel)
- `backend/alembic/`: Database migration files

**Important Backend Concepts:**
- All routes return JSON responses with consistent error handling
- CORS is configured for Vite dev server (`http://localhost:5173`)
- JWT authentication with refresh tokens
- Redis used for caching and session management
- Security middleware includes CSRF, XSS protection, rate limiting

### Testing Architecture

**Frontend Tests:**
- Unit tests: Vitest with `@testing-library/react`
- E2E tests: Playwright with multi-browser support (Chromium, Firefox, WebKit)
- Test files: `src/test/` and `e2e/`
- Configuration: `vitest.config.ts`, `playwright.config.ts`

**Backend Tests:**
- Framework: pytest with async support
- Test files: `backend/tests/test_*.py`
- Fixtures: `backend/tests/conftest.py`
- Coverage target: 90%+

**Integration Tests:**
- Full stack testing via `scripts/integration-test.sh`
- Tests health endpoints, authentication flow, and API endpoints

### State Management Patterns

**Frontend State:**
1. **Server State** (API data): TanStack Query
   - Automatic caching, refetching, and synchronization
   - Used for all API calls
2. **Global UI State**: Zustand stores
   - Cart state, user preferences, UI toggles
3. **Authentication State**: React Context (`AuthProvider`)
   - User session, tokens, role-based access
4. **Local Component State**: React hooks
   - Form inputs, UI interactions

**Backend State:**
- Session data: Redis
- Persistent data: PostgreSQL
- Caching: Redis with TTL

## Environment Configuration

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=your-firebase-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-bucket
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=your-app-id
```

### Backend (backend/.env)
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/agridb
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-jwt-secret-here
JWT_REFRESH_SECRET=your-refresh-token-secret
STRIPE_SECRET_KEY=sk_test_your-stripe-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

**Environment Setup:**
```bash
# First time setup
cp .env.example .env
cp backend/.env.example backend/.env
# Edit both files with appropriate values
```

## Key Development Workflows

### Adding a New Frontend Route
1. Create page component in `src/pages/YourPage.tsx`
2. Add route in `src/App.tsx` (inside AppLayout or ProtectedRoute)
3. Add navigation link in `src/components/AppHeader.tsx` if needed
4. Create E2E test in `e2e/your-page.spec.ts`

### Adding a New API Endpoint
1. Create/update router in `backend/app/routers/your_router.py`
2. Add business logic to `backend/app/services/your_service.py`
3. Update models in `backend/app/models.py` if needed
4. Create database migration: `alembic revision --autogenerate -m "description"`
5. Write tests in `backend/tests/test_your_router.py`
6. Register router in `backend/app/main.py` if new file

### Running Full Test Suite
```bash
# Frontend
npm run typecheck
npm run lint
npm test
npm run test:e2e

# Backend
cd backend
pytest --cov=app

# Integration
./scripts/integration-test.sh
```

### Database Migration Workflow
```bash
cd backend
# 1. Modify models in app/models.py
# 2. Generate migration
alembic revision --autogenerate -m "Add new field to User table"
# 3. Review generated file in alembic/versions/
# 4. Apply migration
alembic upgrade head
# 5. Test with: pytest
```

## Important Technical Details

### API Communication
- Base URL configured via `VITE_API_URL` environment variable
- All API calls go through `src/lib/api.ts` which handles:
  - Authentication headers (JWT tokens)
  - Request/response interceptors
  - Error handling and retry logic
- Backend runs on port 8000, frontend on 5173
- CORS is configured in `backend/app/main.py`

### Authentication Flow
1. User logs in via `/auth/login` endpoint
2. Backend returns JWT access token and refresh token
3. Frontend stores tokens in `AuthProvider` context
4. `api.ts` interceptor adds `Authorization: Bearer <token>` to all requests
5. On token expiry, automatic refresh via `/auth/refresh` endpoint
6. Protected routes use `ProtectedRoute` wrapper in `src/App.tsx`

### Database Connection
- PostgreSQL connection string in `DATABASE_URL` env var
- Database name: `agridb` (development), configurable for production
- Connection pooling handled by SQLAlchemy
- Sessions managed via dependency injection in FastAPI

### PWA and Offline Support
- Service worker: `public/sw.js`
- Manifest: `public/manifest.json`
- Offline sync hooks: `src/hooks/useOfflineSync.ts`
- Mobile optimization: `src/hooks/useMobileOptimization.ts`

### Security Considerations
- CSRF protection enabled in backend (via middleware)
- Rate limiting configured per endpoint
- Input validation via Pydantic models (backend) and Zod schemas (frontend)
- SQL injection prevention via SQLAlchemy parameterized queries
- XSS protection via React's default escaping + CSP headers

## Common Issues and Solutions

### Port Conflicts
- Frontend runs on 5173 (Vite default)
- Backend runs on 8000 (FastAPI default)
- E2E tests expect app on 5174 (see `playwright.config.ts`)
- Postgres: 5432, Redis: 6379, MailHog: 8025

### Database Connection Issues
```bash
# Check if postgres is running
docker compose ps
# Reset database completely
docker compose down -v
docker compose up db -d
cd backend && alembic upgrade head
```

### Module Not Found Errors
```bash
# Frontend
rm -rf node_modules package-lock.json
npm install

# Backend
cd backend
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### CORS Errors
- Ensure `CORS_ORIGINS` in `backend/.env` includes your frontend URL
- Check `backend/app/main.py` for CORS middleware configuration
- During development: `http://localhost:5173` and `http://127.0.0.1:5173`

### Test Failures
```bash
# Frontend: Clear test cache
npm run test -- --clearCache

# Backend: Run with verbose output
cd backend
pytest -vv --log-cli-level=DEBUG
```

## Code Style and Conventions

### TypeScript/React
- Use functional components with hooks
- Prefer named exports for components
- Path aliases: `@/` maps to `src/`
- TypeScript: Relaxed mode (see `tsconfig.json`) - `noImplicitAny: false`
- ESLint rules: React Hooks rules enforced, unused vars warning disabled

### Python/FastAPI
- Type hints required for all function signatures
- Async/await for all database operations
- Pydantic models for request/response validation
- Router functions follow pattern: `async def route_name(dependencies) -> ResponseModel`
- Service layer for business logic, routers stay thin

### Testing
- Frontend: Test user interactions, not implementation details
- Backend: Test business logic in services, integration tests for routers
- E2E: Test complete user workflows across multiple pages
- Minimum coverage: 90% (enforced in CI)

### Git Workflow
- Feature branches: `feature/your-feature-name`
- Commit messages: Descriptive, present tense
- PR requirements: All tests pass, no lint errors, coverage maintained

## Project-Specific Context

### User Roles
The system has three main user roles:
- **Farmer**: Can list products, manage inventory, fulfill orders
- **Buyer**: Can browse marketplace, place orders, leave reviews
- **Admin**: Full system access, user management, dispute resolution

Role is stored in `user.role` field and checked via authentication middleware.

### Key Business Logic
- **Escrow System**: Orders use smart contract escrow (Web3 integration ready)
- **Dispute Resolution**: Managed via `disputes.py` router with admin escalation
- **Shopping Cart**: Persistent cart stored in database, synced across sessions
- **Order States**: pending → confirmed → processing → shipped → delivered

### External Integrations
- **Stripe**: Payment processing (requires API keys in .env)
- **Firebase**: Push notifications and analytics
- **Cloud Storage**: Multi-cloud support (AWS S3, Google Cloud, Azure)
- **Web3**: Wallet integration via wagmi and RainbowKit

### Performance Requirements
- API response time: <200ms (95th percentile)
- Frontend LCP: <2.0s
- E2E test execution: <5 minutes full suite
- Load capacity: 1000+ concurrent users

## Additional Resources

- **Full Documentation**: `README.md` (comprehensive project overview)
- **API Documentation**: http://localhost:8000/docs (Swagger UI when backend running)
- **Integration Testing Guide**: `INTEGRATION_TESTING.md`
- **Docker Deployment**: `DOCKER_DEPLOYMENT.md`
- **Security Policy**: `SECURITY.md`
- **System Analysis**: `SYSTEM_ANALYSIS.md`
