# Getting Started with AgriDAO

This guide will help you set up and run AgriDAO locally for development.

## Prerequisites

- **Docker** and **Docker Compose** (recommended)
- **Node.js** 20.x or higher
- **Python** 3.12 or higher
- **Git**

## Quick Start with Docker

The fastest way to get started:

```bash
# Clone the repository
git clone https://github.com/yourusername/AgriDAO.git
cd AgriDAO

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Wait for services to start (30-60 seconds)
# Access the application at http://localhost:3000
```

## Manual Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Create admin user
python create_admin.py

# Start server
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Database Setup

If not using Docker:

```bash
# Install PostgreSQL 15+
# Create database
createdb agridao

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost/agridao
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Backend
DATABASE_URL=postgresql://postgres:postgres@db:5432/agridao
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Frontend
VITE_API_URL=http://localhost:8000
```

## Verify Installation

1. **Backend Health Check**: Visit `http://localhost:8000/health`
2. **API Documentation**: Visit `http://localhost:8000/docs`
3. **Frontend**: Visit `http://localhost:3000`

## Default Credentials

After running `create_admin.py`:

- **Email**: admin@agridao.com
- **Password**: admin123

⚠️ Change these credentials immediately in production!

## Next Steps

- Read the [API Documentation](../api/README.md)
- Check out the [Demo Guide](../guides/DEMO_GUIDE.md)
- Learn about [Deployment](../deployment/QUICK_START.md)
- Review [Contributing Guidelines](../../CONTRIBUTING.md)

## Troubleshooting

### Port Already in Use

```bash
# Stop existing services
docker-compose down

# Or change ports in docker-compose.yml
```

### Database Connection Issues

```bash
# Check database is running
docker-compose ps

# View logs
docker-compose logs db
```

### Frontend Build Errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Development Workflow

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Run tests: `npm test` (frontend) or `pytest` (backend)
4. Commit and push
5. Open a pull request

For more details, see [CONTRIBUTING.md](../../CONTRIBUTING.md)
