# AgriDAO

**A Production-Ready Agricultural Marketplace Platform**

AgriDAO is a comprehensive web-based marketplace that connects farmers directly with buyers, featuring advanced capabilities including AI-powered recommendations, blockchain transaction tracking, supply chain management, and social community features.

[![Status](https://img.shields.io/badge/status-production--ready-success)](https://github.com/SmartFarmDAO/AgriDAO)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/SmartFarmDAO/AgriDAO)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)

> **New to AgriDAO?** Start with [QUICK_START.md](./QUICK_START.md) for a 3-step setup guide.

---

## Overview

AgriDAO is a full-featured agricultural marketplace platform designed to eliminate intermediaries and enable direct farmer-to-buyer transactions. The platform includes 45 implemented user stories covering core marketplace functionality, advanced features, and enterprise capabilities.

### Key Capabilities

- **🛒 Complete Marketplace** - Product listings, search, cart, and checkout
- **💳 Payment Processing** - Integrated Stripe payment gateway
- **🤖 AI Recommendations** - Personalized product suggestions
- **⛓️ Blockchain Integration** - Transparent transaction tracking
- **📦 Supply Chain Tracking** - Real-time product journey monitoring
- **👥 Social Features** - Community posts, comments, and engagement
- **🌍 Multi-Language Support** - English and Bengali localization
- **📊 Analytics Dashboard** - Comprehensive business insights
- **🔐 Enterprise Security** - JWT authentication, role-based access control

---

## Technology Stack

### Frontend Architecture
```
React 18.2 + TypeScript 5.2
├── Build Tool: Vite 5.0
├── Styling: TailwindCSS 3.3 + Radix UI
├── State Management: Zustand 4.4
├── Data Fetching: TanStack Query 5.8
├── Forms: React Hook Form 7.48
├── Routing: React Router 6.18
├── Web3: Wagmi 2.19 + Viem 2.39
└── Testing: Vitest + Playwright
```

### Backend Architecture
```
FastAPI 0.111 + Python 3.11+
├── Database: PostgreSQL 16 + SQLModel
├── Caching: Redis 7
├── Authentication: JWT + Passlib
├── Payments: Stripe 10.6
├── Email: SMTP with OTP
├── File Storage: Local + Pillow
├── Migrations: Alembic 1.13
└── Testing: Pytest 8.3
```

### Infrastructure
```
Docker + Docker Compose
├── PostgreSQL Container
├── Redis Container
├── Backend Container (FastAPI)
├── Frontend Container (Vite)
└── Nginx (Production)

```

---

## Quick Start

### Prerequisites
- Node.js 18+
- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/SmartFarmDAO/AgriDAO.git
cd AgriDAO
```

2. **Set up environment variables**
```bash
# Frontend
cp frontend/.env.example frontend/.env
# Edit frontend/.env with your configuration

# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration
```

3. **Start the application**
```bash
# Start all services (backend, database, redis)
docker-compose up

# In a new terminal, start frontend
cd frontend
npm install
npm run dev
```

4. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

---

## Project Structure

```
AgriDAO/
├── frontend/              # React application
│   ├── src/
│   │   ├── components/   # UI components (53+ components)
│   │   ├── pages/        # Page components (20+ pages)
│   │   ├── hooks/        # Custom hooks
│   │   └── services/     # API services
│   └── package.json
│
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── routers/     # API endpoints (21 routers)
│   │   ├── models.py    # Database models (25+ tables)
│   │   └── main.py      # Application entry
│   └── requirements.txt
│
├── docs/                 # Documentation (50+ documents)
└── docker-compose.yml    # Development environment
```

---

## Core Features

### For Farmers
- Product listing and management
- Order tracking and fulfillment
- Sales analytics
- Profile management
- Inventory control

### For Buyers
- Browse and search products
- Shopping cart and checkout
- Order history
- Saved addresses
- Product reviews

### For Administrators
- User management
- Order oversight
- Platform analytics
- Dispute resolution
- Content moderation

---

## Advanced Features

### AI-Powered Recommendations
- Personalized product suggestions based on user behavior
- Collaborative filtering algorithms
- Real-time recommendation updates

### Blockchain Integration
- Transparent transaction recording
- SHA-256 hashing for data integrity
- Immutable transaction history
- Verification system

### Supply Chain Tracking
- Real-time product location updates
- Visual tracking timeline
- QR code support
- Complete product journey visibility

### Social Community
- Create and share posts
- Comment and engage with community
- Like and reaction system
- Image support for posts

### Multi-Language Support
- English and Bengali interfaces
- Dynamic language switching
- Localized content

---

## Development

### Available Commands

**Frontend**
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm test             # Run unit tests
npm run test:e2e     # Run E2E tests
npm run lint         # Lint code
```

**Backend**
```bash
docker-compose up    # Start backend services
pytest               # Run tests
alembic upgrade head # Run database migrations
```

### Running Tests

```bash
# Frontend tests
cd frontend
npm test                    # Unit tests
npm run test:e2e           # E2E tests
npm run test:coverage      # Coverage report

# Backend tests
cd backend
pytest                     # All tests
pytest tests/test_api.py   # Specific test file
```

---

## API Documentation

When the backend is running, interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key API Endpoints

**Authentication**
- `POST /auth/send-otp` - Send OTP to email
- `POST /auth/verify-otp` - Verify OTP and login
- `POST /auth/logout` - Logout user

**Products**
- `GET /products` - List all products
- `POST /products` - Create product (farmer only)
- `GET /products/{id}` - Get product details
- `PUT /products/{id}` - Update product (farmer only)

**Orders**
- `POST /orders` - Create order
- `GET /orders` - List user orders
- `GET /orders/{id}` - Get order details
- `PUT /orders/{id}/status` - Update order status

**Payments**
- `POST /payments/create-intent` - Create payment intent
- `POST /payments/webhook` - Stripe webhook handler

**Social**
- `GET /social/posts` - List community posts
- `POST /social/posts` - Create post
- `POST /social/posts/{id}/like` - Like post
- `POST /social/posts/{id}/comments` - Add comment

**Supply Chain**
- `GET /supplychain/assets` - List tracked assets
- `POST /supplychain/assets` - Register asset
- `POST /supplychain/assets/{id}/track` - Update location

**Blockchain**
- `GET /blockchain/transactions` - List transactions
- `POST /blockchain/transactions` - Record transaction
- `GET /blockchain/stats` - Get statistics

---

## Environment Variables

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=your-firebase-key
VITE_FIREBASE_PROJECT_ID=your-project-id
```

### Backend (.env)
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/agridb
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-secret-key
STRIPE_SECRET_KEY=your-stripe-key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

See `.env.example` files in each directory for complete configuration options.

---

## Deployment

### Production Build

```bash
# Build frontend
cd frontend
npm run build

# Build backend
cd backend
docker build -t agridao-backend .
```

### Using Docker Compose

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

See [docs/deployment/](./docs/deployment/) for detailed deployment guides.

---

## Database

The application uses PostgreSQL with the following main tables:
- `users` - User accounts and authentication
- `farmers` - Farmer profiles
- `products` - Product listings
- `orders` - Order records
- `order_items` - Order line items
- `cart_items` - Shopping cart data
- `social_posts` - Community posts
- `social_comments` - Post comments
- `supply_chain_assets` - Tracked products
- `blockchain_transactions` - Transaction records

### Migrations

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -ti:5173  # Frontend
lsof -ti:8000  # Backend

# Kill the process
lsof -ti:5173 | xargs kill -9
```

### Docker Issues
```bash
# Clean restart
docker-compose down
docker-compose up --build

# Remove volumes
docker-compose down -v
```

### Database Connection Issues
- Verify PostgreSQL is running: `docker-compose ps`
- Check DATABASE_URL in backend/.env
- Ensure migrations are applied: `alembic upgrade head`

See [docs/troubleshooting/](./docs/troubleshooting/) for more solutions.

---

## Documentation

- [Quick Start Guide](./QUICK_START.md) - Get started in 3 steps
- [Project Structure](./STRUCTURE.md) - Codebase organization
- [Developer Cheat Sheet](./CHEAT_SHEET.md) - Common commands
- [Full Documentation](./docs/INDEX.md) - Complete documentation index
- [User Stories](./docs/project/userstory.md) - All 45 implemented features
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute
- [Security Policy](./SECURITY.md) - Security guidelines

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

- **Documentation**: [docs/](./docs/)
- **Issues**: [GitHub Issues](https://github.com/SmartFarmDAO/AgriDAO/issues)
- **Discussions**: [GitHub Discussions](https://github.com/SmartFarmDAO/AgriDAO/discussions)

---

## Acknowledgments

Built with modern web technologies and open-source tools. Special thanks to all contributors and the open-source community.

---

**Status**: Production Ready  
**Version**: 1.0.0  
**Completion**: 100% (45/45 User Stories)  
**Node**: ≥18.0.0  
**Python**: ≥3.11
