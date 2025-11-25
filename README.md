# AgriDAO

A web-based agricultural marketplace connecting farmers directly with buyers. Built with React, FastAPI, and PostgreSQL.

> **New here?** See [START_HERE.md](./START_HERE.md) or [QUICK_START.md](./QUICK_START.md)

## What It Does

AgriDAO is a marketplace platform that enables:

- **Direct Sales** - Farmers list products, buyers purchase directly
- **Order Management** - Track orders from placement to delivery
- **User Roles** - Separate interfaces for farmers, buyers, and administrators
- **Analytics** - Sales insights and performance metrics
- **Payment Processing** - Integrated Stripe payment handling

## Tech Stack

**Frontend**
- React 18 with TypeScript
- Vite for development and builds
- TailwindCSS for styling
- Zustand for state management
- React Query for data fetching

**Backend**
- FastAPI (Python)
- PostgreSQL database
- Redis for caching
- JWT authentication
- Stripe for payments

**Infrastructure**
- Docker & Docker Compose
- Nginx for production
- Playwright for E2E testing

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

## Project Structure

```
AgriDAO/
├── frontend/              # React application
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom hooks
│   │   └── services/     # API services
│   └── package.json
│
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── routers/     # API endpoints
│   │   ├── models.py    # Database models
│   │   └── main.py      # Application entry
│   └── requirements.txt
│
├── docs/                 # Documentation
└── docker-compose.yml    # Development environment
```

## Core Features

### For Farmers
- Product listing and management
- Order tracking and fulfillment
- Sales analytics
- Profile management

### For Buyers
- Browse and search products
- Shopping cart and checkout
- Order history
- Saved addresses

### For Administrators
- User management
- Order oversight
- Platform analytics
- Dispute resolution

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

## API Documentation

When the backend is running, interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

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
```

See `.env.example` files in each directory for complete configuration options.

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

## Database

The application uses PostgreSQL with the following main tables:
- `users` - User accounts and authentication
- `products` - Product listings
- `orders` - Order records
- `order_items` - Order line items
- `cart_items` - Shopping cart data

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

## Documentation

- [Quick Start Guide](./QUICK_START.md) - Get started in 3 steps
- [Project Structure](./STRUCTURE.md) - Codebase organization
- [Developer Cheat Sheet](./CHEAT_SHEET.md) - Common commands
- [Full Documentation](./docs/INDEX.md) - Complete documentation index
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute
- [Security Policy](./SECURITY.md) - Security guidelines

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [docs/](./docs/)
- **Issues**: [GitHub Issues](https://github.com/SmartFarmDAO/AgriDAO/issues)
- **Discussions**: [GitHub Discussions](https://github.com/SmartFarmDAO/AgriDAO/discussions)

## Acknowledgments

Built with modern web technologies and open-source tools. Special thanks to all contributors and the open-source community.

---

**Status**: Active Development  
**Version**: 1.0.0  
**Node**: ≥18.0.0  
**Python**: ≥3.11
