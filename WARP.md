# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

AgriDAO is a comprehensive blockchain-enabled agricultural marketplace built with React/TypeScript frontend and FastAPI/Python backend. It connects farmers directly with consumers, restaurants, and retailers through smart contracts, real-time market data, and decentralized governance.

## Development Commands

### Frontend (React/TypeScript/Vite)

```bash
# Development
npm run dev          # Start development server on http://localhost:5174
npm run build        # Build for production
npm run preview      # Preview production build

# Testing
npm test            # Run unit tests with Vitest
npm run test:ui     # Run tests with UI
npm run test:coverage  # Run tests with coverage
npm run test:e2e    # Run Playwright end-to-end tests
npm run test:e2e:ui # Run E2E tests with UI
npm run test:e2e:headed  # Run E2E tests in headed mode
npm run test:security    # Run security-specific E2E tests
npm run test:performance # Run performance E2E tests
npm run test:load        # Run Artillery load tests

# Code Quality
npm run lint        # Run ESLint
npm run format      # Format with Prettier
npm run format:check # Check formatting
npm run typecheck   # TypeScript type checking
npm run analyze     # Bundle analysis
```

### Backend (FastAPI/Python)

```bash
# Docker development (recommended)
docker compose up --build  # Start full stack with hot reload
docker compose down        # Stop all services

# Local development
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/agridb
alembic upgrade head       # Run database migrations
uvicorn app.main:app --reload  # Start backend server

# Database operations
alembic revision --autogenerate -m "description"  # Create migration
alembic upgrade head       # Apply migrations
alembic downgrade -1       # Rollback one migration
```

### Mobile (React Native/Expo)

```bash
cd mobile
npm run start       # Start Expo development server
npm run android     # Run on Android
npm run ios         # Run on iOS
npm run web         # Run on web
npm run test        # Run mobile tests
npm run lint        # Lint mobile code
npm run typecheck   # Type check mobile code
```

### Production Deployment

```bash
# Production build and deploy
docker build -f Dockerfile.prod -t agridao:latest .
docker-compose -f docker-compose.prod.yml up -d

# View production logs
docker-compose -f docker-compose.prod.yml logs -f

# Access production services
# App: https://localhost
# Grafana: http://localhost:3001
# Prometheus: http://localhost:9090
```

## Architecture Overview

### Multi-Tier Architecture

The application follows a comprehensive 3-tier architecture:

1. **Frontend Layer**: React SPA, Mobile PWA, Admin Dashboard
2. **API Gateway**: FastAPI with JWT auth and role-based authorization  
3. **Business Logic**: Microservices for User, Product, Order, Payment, Analytics
4. **Data Layer**: PostgreSQL, Redis cache, S3-compatible file storage

### Key Architectural Decisions

- **State Management**: Zustand for global state, React Query for server state
- **Authentication**: JWT with refresh tokens, role-based access control (buyer/farmer/admin)
- **Database**: PostgreSQL with SQLModel ORM, Alembic migrations
- **Caching**: Redis for sessions, rate limiting, and performance
- **File Storage**: Cloud storage (S3/CloudFlare) for images and assets
- **Testing**: Multi-level testing with Vitest, Playwright, Artillery
- **Deployment**: Docker containers with production-ready configuration

### Core Services Architecture

```typescript
// Authentication Service - JWT with refresh tokens
interface AuthService {
  login(credentials: LoginCredentials): Promise<AuthResult>
  refreshToken(): Promise<string>
  validateSession(): Promise<boolean>
}

// Product Management - With image handling and inventory
interface ProductService {
  createProduct(product: CreateProductRequest): Promise<Product>
  updateProduct(id: number, updates: UpdateProductRequest): Promise<Product>
  searchProducts(criteria: SearchCriteria): Promise<Product[]>
}

// Order Processing - Complete lifecycle management
interface OrderService {
  createOrder(orderData: CreateOrderRequest): Promise<Order>
  updateOrderStatus(orderId: number, status: OrderStatus): Promise<Order>
  getOrderHistory(userId: number): Promise<Order[]>
}
```

## File Structure Context

```
AgriDAO/
├── src/
│   ├── components/          # Reusable UI components (Radix UI, custom components)
│   │   ├── layout/          # AppLayout, navigation components
│   │   ├── ui/              # Shadcn/ui components
│   │   └── *                # Feature-specific components
│   ├── pages/              # Route-based pages (Index, Auth, Dashboard, etc.)
│   ├── hooks/              # Custom React hooks (auth, mobile, config)
│   ├── lib/                # Utilities (API client, security, wallet)
│   ├── stores/             # Zustand state stores
│   ├── types/              # TypeScript definitions
│   └── config/             # App configuration (API, Wagmi)
├── backend/                # FastAPI Python backend
│   ├── app/
│   │   ├── routers/        # API route handlers
│   │   ├── services/       # Business logic services
│   │   ├── models/         # SQLModel database models
│   │   └── main.py         # FastAPI app configuration
├── e2e/                    # Playwright end-to-end tests
├── mobile/                 # React Native/Expo mobile app
└── public/                 # Static assets, PWA files
```

## Development Context

### Current Implementation Status (Based on .kiro specs)

**✅ Completed Features:**
- Enhanced Authentication System (JWT refresh tokens, RBAC)
- Product Management System (image upload, inventory tracking)
- Shopping Cart & Checkout (Stripe integration, order confirmation)
- Order Tracking & Management (status updates, notifications)
- Analytics & Reporting (real-time dashboards, user analytics)
- Mobile Optimization (PWA features, responsive design)
- Testing Infrastructure (unit, integration, E2E with Playwright)
- Production Deployment (Docker, monitoring, security)
- Security & Privacy (data encryption, GDPR compliance)

**🔄 Current Focus Areas:**
- System integration and final testing validation
- Admin dashboard completion and router integration
- Frontend test infrastructure enhancement
- Production deployment finalization

### Technology Stack

**Frontend:**
- React 18 + TypeScript + Vite
- Tailwind CSS + Radix UI components
- Zustand (state) + React Query (server state)
- React Hook Form + Zod validation
- Framer Motion animations

**Backend:**
- FastAPI + Python 3.11+
- PostgreSQL + SQLModel ORM
- Redis caching + Alembic migrations
- Stripe payments + JWT authentication

**Testing:**
- Vitest (unit) + React Testing Library
- Playwright (E2E) + Artillery (load)
- Comprehensive security and performance testing

**Mobile:**
- React Native + Expo
- Progressive Web App (PWA) capabilities
- Offline-first architecture

## Development Guidelines

### Working with the Codebase

1. **API Development**: All endpoints follow FastAPI patterns with Pydantic validation
2. **Component Development**: Use Radix UI components, follow established patterns in `src/components/`
3. **State Management**: Use Zustand for global state, React Query for server state
4. **Database Changes**: Always create Alembic migrations for schema changes
5. **Testing**: Write tests for new features following existing patterns in test directories

### Common Patterns

- **Error Handling**: Comprehensive error boundaries and API error handling
- **Authentication**: JWT tokens with automatic refresh, role-based routing
- **Image Handling**: Cloud storage integration with automatic optimization
- **Mobile Optimization**: Touch-friendly interfaces, PWA capabilities
- **Payment Processing**: Stripe integration with webhook handling

### Environment Setup

The project requires several environment variables for full functionality:

```bash
# Frontend (.env)
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=your-firebase-key
# ... other Firebase config

# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/agridb
REDIS_URL=redis://localhost:6379
STRIPE_SECRET_KEY=sk_test_...
```

### Testing Strategy

- **Unit Tests**: Focus on business logic and utilities
- **Integration Tests**: API endpoints and database operations  
- **E2E Tests**: Critical user journeys (auth, purchase, order management)
- **Performance Tests**: Load testing with Artillery, Core Web Vitals
- **Security Tests**: OWASP compliance, input validation

This is a production-ready agricultural marketplace with comprehensive security, testing, and mobile optimization.