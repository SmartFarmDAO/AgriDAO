---
inclusion: always
---

# AgriDAO Project Conventions

## Project Structure

- Separate backend/ and frontend/ directories at the root level for independent deployment
- Backend uses FastAPI (Python) at backend/ root with functions/routers/ subdirectory
- Frontend follows standard React structure with src/ containing components, pages, services (API layer), and hooks
- Each major feature gets its own router in backend/app/routers/ with dedicated service file
- Shared code goes in backend/app/services/ or backend/app/core/
- Use .env files for environment-specific configuration

## Backend Configuration (FastAPI/Python)

- Use Python 3.12+ for all backend code
- FastAPI application structure with routers, services, models, middleware
- SQLAlchemy ORM with Alembic for database migrations
- Default timeout: 30 seconds (increase to 90 seconds for image processing operations)
- Memory: 768MB minimum for backend service
- Enable structured logging with correlation IDs for all requests
- Use Pydantic/SQLModel for data validation and type safety

## Frontend Configuration (React/TypeScript)

- Use Node.js 20.x runtime for all frontend operations
- React 18 with TypeScript strict mode
- Vite as build tool and dev server
- Memory: 256MB minimum for frontend service
- Use TanStack Query (React Query) for server state management
- Use Zustand for client state management
- Tailwind CSS + shadcn/ui for styling

## Database Configuration

- PostgreSQL 15+ as primary database
- Use connection pooling (pool_pre_ping=True)
- All schema changes via Alembic migrations
- Never use SQLModel.metadata.create_all() in production
- Run migrations via: `alembic upgrade head`
- Foreign keys must be explicitly defined
- Create indexes for frequently queried columns

## Redis Configuration

- Redis 7+ for caching and session management
- Memory limits configured based on environment
- Persistence enabled (appendonly yes)
- Use for: session storage, rate limiting, caching frequently accessed data
- Cache TTL: 5 minutes for product listings, 24 hours for sessions

## API Design

- Enable CORS with Authorization header support
- Use JWT authorizers for protected endpoints
- Return descriptive error messages with proper HTTP status codes
- Validate all input at handler entry point
- Use correlation IDs for request tracing
- Implement rate limiting on all public endpoints
- All endpoints should return JSON responses

## Authentication & Security

- JWT tokens with expiration and refresh token rotation
- bcrypt for password hashing with appropriate salt rounds
- Session management with secure cookies (httpOnly, secure flags)
- CSRF protection for state-changing operations
- XSS protection middleware
- Security headers: X-Content-Type-Options, X-Frame-Options, CSP
- Never log sensitive data (passwords, tokens, API keys)
- Use parameterized queries, never string concatenation
- HTTPS only, no mixed content
- Implement rate limiting on APIs

## Deployment and Testing

- Always run `pytest` after building from backend/ directory
- Use `docker-compose up -d` for local development
- Test all API endpoints after deployment
- Verify responses match expected format
- Run E2E tests for critical user flows
- Load test before production deployment
- Verify health checks pass before marking deployment successful

## Multi-language Support

- Platform supports English and Bengali
- All UI text must have translation keys
- Use i18n system for all user-facing strings
- Error messages must be translated
- Language preference persists across sessions
- Browser language detection for default language

## Blockchain Integration

- Ethereum smart contracts for DAO governance and escrow
- Use wagmi and RainbowKit for Web3 integration
- Contract addresses loaded from environment variables
- Handle transaction failures gracefully
- Provide transaction status updates to users
- Test on testnet before mainnet deployment

## Payment Processing

- Stripe for payment processing
- Verify webhook signatures before processing
- Log all payment events with correlation IDs
- Handle payment failures with user notification
- Support partial and full refunds
- Retry failed operations with exponential backoff
- Platform fee rate: 10% (configurable via PLATFORM_FEE_RATE)

## Monitoring and Logging

- Structured logging with correlation IDs
- Log all errors with stack traces
- Log slow queries (>1 second)
- Track business metrics (orders, revenue, active users)
- Prometheus for metrics collection
- Grafana for visualization
- Alert on: error rate >5%, response time >2s, CPU >80%, memory >90%

## Code Style

- Python: Follow PEP 8, use type hints, add docstrings
- TypeScript: Strict mode, no implicit any, ESLint + Prettier
- 2-space indentation for JS/TS, 4-space for Python
- camelCase for functions and variables (JS/TS)
- snake_case for functions and variables (Python)
- PascalCase for components and classes
- SCREAMING_SNAKE_CASE for constants
- Descriptive variable names, avoid abbreviations

## Git Conventions

- Follow Conventional Commits format
- Types: feat, fix, docs, refactor, test, chore
- Format: `type(scope): description`
- Example: `feat(auth): add JWT token refresh`
- Branch naming: `feature/xxx`, `fix/xxx`, `docs/xxx`
- Commit changes grouped by single logical purpose
- Keep commits under 150 lines of code + 150 lines of test code

## Documentation

- Add docstrings for all public functions (Python)
- Add JSDoc for complex functions (TypeScript)
- Keep README files updated
- Document all environment variables
- Include setup instructions in README
- API documentation auto-generated at /docs endpoint

## Testing Standards

- Minimum 80% coverage for business logic
- Test files in `backend/tests/` and `frontend/src/` directories
- Use pytest for Python, Vitest for TypeScript
- Playwright for E2E tests
- Arrange-Act-Assert pattern
- Descriptive test names (it should...)
- Mock external dependencies (Stripe, blockchain)
- Property-based tests for correctness properties

## Performance Optimization

- Static assets served with cache headers
- Redis caching for frequently accessed data
- Image compression and optimization
- Gzip compression enabled in Nginx
- Lazy loading for images and components
- Pagination for large result sets
- Database indexes for common queries
- Frontend bundle size <500KB initial load

## What NOT to Include in Code

- API keys or secrets (use environment variables)
- Database credentials
- Internal URLs or endpoints
- Customer data or PII
- Hardcoded passwords or tokens
- Sensitive configuration values

**ALWAYS FOLLOW THESE RULES WHEN YOU WORK IN THIS PROJECT**
