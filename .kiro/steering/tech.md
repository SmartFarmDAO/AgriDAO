# Tech Stack & Build System

## Backend (Python/FastAPI)

**Framework**: FastAPI 0.111+ with Python 3.12+
**Database**: PostgreSQL 15+ (SQLAlchemy ORM, Alembic migrations)
**Cache**: Redis 7+
**Authentication**: JWT tokens with passlib bcrypt
**File Upload**: Pillow for image processing, aiofiles for async I/O
**AI Agents**: Custom multi-agent system with async orchestration

### Key Libraries
- `fastapi` - Web framework
- `sqlalchemy` - ORM and database toolkit
- `alembic` - Database migrations
- `pydantic` - Data validation
- `redis` - Caching layer
- `pytest` - Testing framework
- `uvicorn` - ASGI server

### Agent System Architecture
- **BaseAgent**: Abstract class for all agents
- **AgentFleet**: Agricultural intelligence orchestrator
- **AgriDAODevFleet**: Development automation orchestrator
- **Specialized Agents**: Market analysis, weather, supply chain, development

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

# Agent Development CLI
python agridao_dev_cli.py status
python agridao_dev_cli.py crud CropVariety
python agridao_dev_cli.py api-component get_weather WeatherWidget
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

### Agent Integration
- **AgentOrchestration Component**: Real-time agent management UI
- **Generated Components**: Agent-created React components with TypeScript
- **Admin Dashboard**: Agent monitoring and control interface

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

## AI Agent System

**Architecture**: Multi-agent orchestration with async coordination
**Languages**: Python with asyncio for concurrent execution
**Patterns**: Factory pattern, Observer pattern, Command pattern

### Agricultural Agents
- **MarketAnalysisAgent**: Market trends and price predictions
- **WeatherAgent**: Weather data and agricultural forecasts
- **SupplyChainAgent**: Logistics optimization and cost estimation

### Development Agents
- **BackendDevAgent**: FastAPI/Python code generation
- **FrontendDevAgent**: React/TypeScript component creation
- **DatabaseDevAgent**: Migration and schema management

### Agent Orchestration
```python
# Agricultural workflow
result = await fleet.orchestrate_workflow({
    "farmer_id": "farmer_123",
    "crop_type": "rice",
    "location": "Dhaka, Bangladesh"
})

# Development workflow
result = await dev_fleet.run_development_workflow("full_stack_crud", {
    "entity": "CropVariety",
    "fields": [{"name": "name", "type": "String"}]
})
```

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
- **Agents**: Specialized agent testing with mock data
- Test files colocated with source or in dedicated test directories

## API Documentation

FastAPI auto-generates OpenAPI docs at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Agent API Endpoints
- `/api/agents/orchestrate` - Agricultural analysis workflow
- `/api/agents/status` - Agent fleet monitoring
- `/api/dev/develop-feature` - Custom feature development
- `/api/dev/workflow/{type}` - Predefined development workflows
- `/api/dev/quick-crud` - Rapid CRUD generation

## Development Workflow Integration

### Agent-Driven Development
1. **Specification**: Define feature requirements in JSON
2. **Generation**: Agents create backend, frontend, and database code
3. **Integration**: Generated code follows AgriDAO conventions
4. **Testing**: Automated testing of generated components
5. **Deployment**: Seamless integration with existing system

### Example Generated Files
```
# Backend
backend/app/routers/cropvariety.py      # API endpoints
backend/app/models/cropvariety.py       # SQLAlchemy model

# Frontend  
frontend/src/components/CropVarietyForm.tsx     # Form component
frontend/src/pages/CropVarietyManagement.tsx    # Management page
```

## Performance Optimization

### Agent Performance
- **Concurrent Execution**: All agents run simultaneously using asyncio
- **Task Queue**: Efficient task distribution and processing
- **Status Monitoring**: Real-time agent status tracking
- **Error Recovery**: Graceful failure handling and retry logic

### Application Performance
- Static assets served with cache headers
- Redis caching for frequently accessed data
- Image compression and optimization
- Gzip compression enabled in Nginx
- Lazy loading for images and components
- Pagination for large result sets
- Database indexes for common queries
- Frontend bundle size <500KB initial load

## Monitoring & Observability

### Agent Monitoring
- Real-time status dashboard in admin interface
- Task execution metrics and timing
- Error tracking and alerting
- Performance analytics and optimization

### Application Monitoring
- Structured logging with correlation IDs
- Prometheus metrics collection
- Grafana visualization dashboards
- Health check endpoints
- Performance monitoring and alerting

## Security Implementation

### Agent Security
- Input validation and sanitization for all agent inputs
- Rate limiting on agent execution endpoints
- Authentication required for agent management
- Secure error handling without information leakage

### Application Security
- JWT authentication with refresh tokens
- CORS configuration for cross-origin requests
- Security headers (CSP, HSTS, X-Frame-Options)
- Input validation and SQL injection prevention
- File upload security and validation
- Rate limiting on all public endpoints

## Current System Capabilities

### Operational Features
- ✅ **25 API Routers**: Complete backend functionality
- ✅ **24 Frontend Pages**: Full user interface
- ✅ **6 AI Agents**: Agricultural and development automation
- ✅ **2 Orchestrators**: Coordinated multi-agent workflows
- ✅ **CLI Interface**: Command-line development tools
- ✅ **Admin Dashboard**: Agent management and monitoring
- ✅ **Production Deployment**: SSL, monitoring, backups

### Agent Capabilities
- ✅ **Agricultural Intelligence**: Market analysis, weather, supply chain
- ✅ **Development Automation**: Full-stack code generation
- ✅ **Real-time Orchestration**: Concurrent multi-agent execution
- ✅ **CLI Integration**: Command-line development workflows
- ✅ **Frontend Integration**: Visual agent management interface

The system demonstrates a mature, production-ready platform with advanced AI agent capabilities for both agricultural intelligence and development automation.
