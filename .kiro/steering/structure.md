# Project Structure & Organization

## Repository Layout

AgriDAO follows a monorepo structure with clear separation of concerns:

```
AgriDAO/
├── backend/           # FastAPI Python backend
├── frontend/          # React TypeScript frontend
├── blockchain/        # Solidity smart contracts
├── mobile/           # React Native mobile app
├── deployment/       # Deployment configs and scripts
├── docs/            # Documentation
├── scripts/         # Utility scripts
└── docker-compose.yml
```

## Backend Structure (`backend/`)

```
backend/
├── app/
│   ├── routers/          # API route handlers (one per domain)
│   ├── services/         # Business logic layer
│   ├── models/           # SQLAlchemy models
│   ├── middleware/       # Custom middleware (security, logging, errors)
│   ├── core/            # Core utilities (logging, monitoring, storage)
│   ├── database/        # Database utilities and views
│   ├── main.py          # FastAPI app initialization
│   ├── database.py      # Database connection setup
│   └── deps.py          # Dependency injection
├── alembic/             # Database migrations
│   └── versions/        # Migration files
├── tests/               # Test files (mirror app structure)
├── uploads/             # User-uploaded files
├── utils/               # Standalone utility scripts
├── requirements.txt     # Python dependencies
├── alembic.ini         # Alembic configuration
└── Dockerfile
```

### Backend Patterns

- **Routers**: Handle HTTP requests, validate input, call services
- **Services**: Contain business logic, interact with database
- **Models**: SQLAlchemy ORM models for database tables
- **Middleware**: Cross-cutting concerns (auth, rate limiting, CORS)
- **Dependencies**: Shared dependencies injected via FastAPI's `Depends()`

### Key Backend Files

- `app/main.py` - Application entry point, middleware setup, router registration
- `app/database.py` - Database session management
- `app/deps.py` - Common dependencies (get_db, get_current_user)
- `app/routers/*.py` - Domain-specific API endpoints
- `app/services/*.py` - Business logic implementations

## Frontend Structure (`frontend/`)

```
frontend/
├── src/
│   ├── components/       # Reusable React components
│   │   ├── ui/          # shadcn/ui components
│   │   └── layout/      # Layout components
│   ├── pages/           # Page components (route targets)
│   ├── hooks/           # Custom React hooks
│   ├── services/        # API client functions
│   ├── lib/             # Utilities and helpers
│   ├── config/          # Configuration files
│   ├── contexts/        # React contexts
│   ├── i18n/            # Internationalization
│   ├── types/           # TypeScript type definitions
│   ├── utils/           # Utility functions
│   ├── App.tsx          # Root component with routing
│   └── main.tsx         # Application entry point
├── public/              # Static assets
├── e2e/                # Playwright E2E tests
├── dist/               # Build output (gitignored)
├── package.json
├── vite.config.ts
├── tailwind.config.ts
└── Dockerfile
```

### Frontend Patterns

- **Pages**: Top-level route components in `src/pages/`
- **Components**: Reusable UI components in `src/components/`
- **Hooks**: Custom hooks for shared logic (use-auth, use-toast, etc.)
- **Services**: API calls abstracted in `src/services/`
- **State**: TanStack Query for server state, Zustand for client state
- **Routing**: React Router with protected routes in `App.tsx`

### Key Frontend Files

- `src/App.tsx` - Root component, routing, providers
- `src/main.tsx` - Entry point, renders App
- `src/hooks/use-auth.tsx` - Authentication context and hook
- `src/lib/api.ts` - Axios instance and API utilities
- `src/components/layout/AppLayout.tsx` - Main layout wrapper

## Blockchain Structure (`blockchain/`)

```
blockchain/
├── contracts/          # Solidity smart contracts
│   ├── AgriDAO.sol    # DAO governance contract
│   └── MarketplaceEscrow.sol
├── scripts/           # Deployment scripts
│   └── deploy.js
├── test/             # Contract tests
├── hardhat.config.js
└── package.json
```

## Mobile Structure (`mobile/`)

```
mobile/
├── app/              # Expo Router pages
├── components/       # React Native components
├── ui/              # UI components
├── assets/          # Images, fonts
├── constants/       # App constants
└── package.json
```

## Deployment Structure (`deployment/`)

```
deployment/
├── docker/
│   ├── docker-compose.prod.yml
│   ├── nginx.prod.conf
│   └── prometheus.yml
├── lightsail/
│   ├── docker-compose.lightsail.yml
│   ├── lightsail-setup.sh
│   └── nginx.conf
├── nginx/
│   └── nginx.conf
└── scripts/
    ├── deploy.sh
    └── test-*.sh
```

## Documentation Structure (`docs/`)

```
docs/
├── README.md            # Documentation index
├── getting-started/     # Setup and installation guides
├── api/                 # API documentation
├── architecture/        # System architecture docs
├── deployment/          # Deployment guides
└── guides/              # Feature guides
```

## Naming Conventions

### Backend (Python)
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

### Frontend (TypeScript)
- Files: `PascalCase.tsx` for components, `kebab-case.ts` for utilities
- Components: `PascalCase`
- Functions/variables: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Types/Interfaces: `PascalCase`

### Database
- Tables: `snake_case` (plural)
- Columns: `snake_case`
- Foreign keys: `{table}_id`

## Import Organization

### Backend
```python
# Standard library
import os
from typing import List

# Third-party
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Local
from ..database import get_db
from ..models import User
from ..services.auth import AuthService
```

### Frontend
```typescript
// React and core libraries
import React from 'react';
import { useNavigate } from 'react-router-dom';

// Third-party UI
import { Button } from '@/components/ui/button';

// Local components and utilities
import { useAuth } from '@/hooks/use-auth';
import { api } from '@/lib/api';
```

## Configuration Files

- `.env` - Environment variables (gitignored, use `.env.example` as template)
- `docker-compose.yml` - Development Docker setup
- `alembic.ini` - Database migration config
- `vite.config.ts` - Vite build configuration
- `tailwind.config.ts` - Tailwind CSS configuration
- `hardhat.config.js` - Hardhat blockchain configuration

## Key Architectural Decisions

1. **Monorepo**: All code in single repository for easier coordination
2. **API-first**: Backend exposes RESTful API, frontend consumes it
3. **Type safety**: TypeScript in frontend, type hints in backend
4. **Containerization**: Docker for consistent dev/prod environments
5. **Separation of concerns**: Clear boundaries between layers
6. **Feature-based routing**: Backend routers organized by domain (auth, marketplace, finance, etc.)
7. **Component composition**: Frontend uses small, reusable components

## Development Best Practices

### Documentation
- Do not create markdown files after each session
- Do not create any irrelevant documents
- Always update existing documentation when implementing features
- Keep documentation minimal and professional (see docs/ structure above)

### Version Control
- Always git commit with proper descriptive messages after successful feature implementation
- Use conventional commit format: `type(scope): message` (e.g., `feat(auth): add JWT refresh token`)
- Commit types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Always ignore sensitive files from git (.env, secrets, credentials, API keys)
- Review .gitignore before committing to ensure no sensitive data is tracked

### Security
- Never commit secrets, API keys, or credentials to version control
- Use environment variables for all sensitive configuration
- Always use `.env.example` as template with placeholder values
- Validate and sanitize all user inputs
- Use parameterized queries to prevent SQL injection
- Implement proper authentication and authorization checks

### Code Quality
- Write self-documenting code with clear variable and function names
- Keep functions small and focused (single responsibility principle)
- Add comments only when code intent is not obvious
- Remove commented-out code before committing
- Run linters and formatters before committing (Black, ESLint, Prettier)
- Write tests for critical business logic

### Database
- Always create migrations for schema changes (never modify database directly)
- Use descriptive migration names: `alembic revision -m "add user profile fields"`
- Test migrations both upgrade and downgrade paths
- Never delete migrations that have been deployed to production

### API Development
- Follow RESTful conventions for endpoint design
- Use appropriate HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Return proper HTTP status codes (200, 201, 400, 401, 403, 404, 500)
- Validate request data with Pydantic models
- Document API changes in docs/api/README.md

### Error Handling
- Use try-except blocks for operations that can fail
- Log errors with appropriate context
- Return user-friendly error messages (never expose stack traces to users)
- Handle edge cases and validate inputs

### Performance
- Use database indexes for frequently queried fields
- Implement caching for expensive operations (Redis)
- Optimize N+1 queries with proper joins or eager loading
- Use pagination for large datasets
- Minimize bundle size in frontend (code splitting, lazy loading)
