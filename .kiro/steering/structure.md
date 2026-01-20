# Project Structure & Organization

## Repository Layout

AgriDAO follows a monorepo structure with clear separation of concerns:

```
AgriDAO/
├── backend/           # FastAPI Python backend
├── frontend/          # React TypeScript frontend
├── blockchain/        # Solidity smart contracts
├── mobile/           # React Native mobile app (Expo)
├── deployment/       # Deployment configs and scripts
├── docs/            # Documentation
├── scripts/         # Utility scripts
├── .kiro/           # Kiro CLI configuration and steering docs
├── agridao_dev_cli.py # Development agents CLI
└── docker-compose.yml
```

## Backend Structure (`backend/`)

```
backend/
├── app/
│   ├── routers/          # API route handlers (25 routers)
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── marketplace.py # Product marketplace
│   │   ├── commerce.py   # E-commerce functionality
│   │   ├── orders.py     # Order management
│   │   ├── cart.py       # Shopping cart
│   │   ├── finance.py    # Financial operations
│   │   ├── admin.py      # Admin panel
│   │   ├── analytics.py  # Analytics and metrics
│   │   ├── agents.py     # AI agent orchestration
│   │   ├── dev_agents.py # Development agents
│   │   ├── cropvariety.py # Generated CRUD example
│   │   └── ...          # 14 more specialized routers
│   ├── services/         # Business logic layer (23 services)
│   ├── models/           # SQLAlchemy models
│   │   ├── cropvariety.py # Generated model example
│   │   └── models.py     # Main models file
│   ├── agents/           # AI Agent system
│   │   ├── base.py       # Base agent class
│   │   ├── implementations.py # Agricultural agents
│   │   ├── orchestrator.py # Agent fleet orchestrator
│   │   ├── dev_agents.py # Development agents
│   │   ├── dev_orchestrator.py # Dev agent orchestrator
│   │   └── advisory_agent.py # Agricultural advisory
│   ├── middleware/       # Custom middleware (8 modules)
│   │   ├── security.py   # Security middleware
│   │   └── error_handlers.py # Error handling
│   ├── core/            # Core utilities (9 modules)
│   │   └── logging.py    # Structured logging
│   ├── database/        # Database utilities and views
│   ├── main.py          # FastAPI app initialization
│   ├── database.py      # Database connection setup
│   └── deps.py          # Dependency injection
├── alembic/             # Database migrations
│   └── versions/        # Migration files (10 migrations)
├── tests/               # Test files (32 test modules)
├── uploads/             # User-uploaded files
├── utils/               # Standalone utility scripts (15 utilities)
├── requirements.txt     # Python dependencies
├── alembic.ini         # Alembic configuration
└── Dockerfile
```

### Backend Patterns

- **Routers**: Handle HTTP requests, validate input, call services
- **Services**: Contain business logic, interact with database
- **Models**: SQLAlchemy ORM models for database tables
- **Agents**: AI agents for agricultural insights and development automation
- **Middleware**: Cross-cutting concerns (auth, rate limiting, CORS, security)
- **Dependencies**: Shared dependencies injected via FastAPI's `Depends()`

### Key Backend Files

- `app/main.py` - Application entry point, middleware setup, router registration
- `app/database.py` - Database session management
- `app/deps.py` - Common dependencies (get_db, get_current_user)
- `app/agents/orchestrator.py` - AI agent fleet management
- `app/agents/dev_orchestrator.py` - Development agent coordination

## Frontend Structure (`frontend/`)

```
frontend/
├── src/
│   ├── components/       # Reusable React components (24 components)
│   │   ├── ui/          # shadcn/ui components
│   │   ├── layout/      # Layout components
│   │   ├── AgentOrchestration.tsx # Agent management UI
│   │   └── CropVarietyForm.tsx # Generated component example
│   ├── pages/           # Page components (24 pages)
│   │   ├── AdminDashboard.tsx # Admin interface with agent tab
│   │   └── CropVarietyManagement.tsx # Generated page example
│   ├── hooks/           # Custom React hooks (9 hooks)
│   ├── services/        # API client functions
│   ├── lib/             # Utilities and helpers (7 modules)
│   ├── config/          # Configuration files (4 configs)
│   ├── contexts/        # React contexts
│   ├── i18n/            # Internationalization
│   ├── types/           # TypeScript type definitions
│   ├── utils/           # Utility functions (5 utilities)
│   ├── App.tsx          # Root component with routing
│   └── main.tsx         # Application entry point
├── public/              # Static assets (10 files)
├── e2e/                # Playwright E2E tests (10 test files)
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

## Agent System Structure (`backend/app/agents/`)

```
agents/
├── base.py              # BaseAgent abstract class
├── implementations.py   # Agricultural analysis agents
│   ├── MarketAnalysisAgent
│   ├── WeatherAgent
│   └── SupplyChainAgent
├── orchestrator.py      # AgentFleet orchestrator
├── dev_agents.py        # Development automation agents
│   ├── BackendDevAgent
│   ├── FrontendDevAgent
│   └── DatabaseDevAgent
├── dev_orchestrator.py  # AgriDAODevFleet orchestrator
├── advisory_agent.py    # Agricultural advisory system
└── factory.py          # Agent factory pattern
```

### Agent Capabilities

- **Agricultural Agents**: Market analysis, weather forecasting, supply chain optimization
- **Development Agents**: Automated code generation, CRUD creation, testing
- **Orchestration**: Multi-agent workflows, task distribution, result aggregation
- **CLI Integration**: Command-line interface for development automation

## Blockchain Structure (`blockchain/`)

```
blockchain/
├── contracts/          # Solidity smart contracts
│   ├── AgriDAO.sol    # DAO governance contract
│   └── MarketplaceEscrow.sol # Escrow system
├── scripts/           # Deployment scripts
│   └── deploy.js
├── test/             # Contract tests
├── hardhat.config.js
└── package.json
```

## Mobile Structure (`mobile/`)

```
mobile/
├── app/              # Expo Router pages (13 pages)
│   ├── (tabs)/      # Tab navigation (5 tabs)
│   ├── login.tsx    # Authentication
│   ├── cart.tsx     # Shopping cart
│   └── orders.tsx   # Order management
├── components/       # React Native components (11 components)
├── ui/              # UI components (2 components)
├── assets/          # Images, fonts (3 directories)
├── constants/       # App constants (4 files)
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
│   ├── docker-compose.ssl.yml
│   ├── lightsail-setup.sh
│   ├── setup-ssl.sh
│   └── nginx.conf
├── nginx/
│   ├── nginx.conf
│   └── ssl.conf
├── monitoring/
│   ├── docker-compose.monitoring.yml
│   └── prometheus.yml
└── scripts/
    ├── deploy.sh
    ├── backup-database.sh
    └── test-*.sh (11 test scripts)
```

## Documentation Structure (`docs/`)

```
docs/
├── README.md            # Documentation index
├── getting-started/     # Setup and installation guides
├── api/                 # API documentation
├── architecture/        # System architecture docs
│   └── AI_AGENT_ARCHITECTURE.md
├── deployment/          # Deployment guides (5 guides)
└── guides/              # Feature guides (6 guides)
    ├── DEMO_GUIDE.md
    ├── funding-feature.md
    └── BLOCKCHAIN_INTEGRATION.md
```

## Kiro Configuration (`.kiro/`)

```
.kiro/
├── steering/           # Project steering documents
│   ├── structure.md    # This file
│   ├── agridao-conventions.md
│   ├── kiro-global.md
│   ├── product.md
│   └── tech.md
├── agents/            # Agent specifications
│   ├── agent-definitions.md
│   ├── implementation.md
│   ├── orchestrator.md
│   └── workflows.md
├── settings/          # Kiro CLI settings
│   └── mcp.json
└── specs/            # Project specifications
    └── production-launch/
```

## Development CLI (`agridao_dev_cli.py`)

Command-line interface for development agents:
- `crud <entity>` - Generate full-stack CRUD
- `api-component <api> <component>` - Create API with frontend
- `setup-db` - Database setup and migrations
- `test` - Run all tests
- `status` - Show agent status
- `feature <spec.json>` - Custom feature development

## Key Architectural Decisions

1. **Monorepo**: All code in single repository for easier coordination
2. **API-first**: Backend exposes RESTful API, frontend consumes it
3. **Agent-driven Development**: AI agents for both agricultural insights and development automation
4. **Type safety**: TypeScript in frontend, type hints in backend
5. **Containerization**: Docker for consistent dev/prod environments
6. **Separation of concerns**: Clear boundaries between layers
7. **Feature-based routing**: Backend routers organized by domain
8. **Component composition**: Frontend uses small, reusable components
9. **Multi-agent orchestration**: Coordinated AI workflows for complex tasks

## Development Best Practices

### Agent-Driven Development
- Use development agents for rapid prototyping and code generation
- Follow generated code patterns and conventions
- Leverage agent orchestration for full-stack feature development
- Integrate agricultural agents for domain-specific insights

### Documentation
- Update existing documentation when implementing features
- Keep documentation minimal and professional
- Use agent-generated code as examples and templates

### Version Control
- Commit agent-generated code with descriptive messages
- Use conventional commit format: `type(scope): message`
- Always ignore sensitive files from git
- Review .gitignore before committing

### Security
- Never commit secrets, API keys, or credentials
- Use environment variables for sensitive configuration
- Validate and sanitize all user inputs
- Implement proper authentication and authorization

### Code Quality
- Use agent-generated code as starting point, then refine
- Follow established patterns from existing codebase
- Write tests for critical business logic
- Run linters and formatters before committing

### Database
- Use development agents for migration generation
- Test migrations both upgrade and downgrade paths
- Never delete migrations deployed to production

### API Development
- Use development agents for consistent endpoint generation
- Follow RESTful conventions
- Return proper HTTP status codes
- Document API changes

### Performance
- Use agent insights for optimization recommendations
- Implement caching for expensive operations
- Use pagination for large datasets
- Monitor agent performance and resource usage

## Current System Status

- **Backend**: 25 routers, 23 services, 32 test modules, full agent system
- **Frontend**: 24 pages, 24 components, 10 E2E tests, agent management UI
- **Agents**: 6 specialized agents, 2 orchestrators, CLI interface
- **Database**: 10 migrations, comprehensive models
- **Deployment**: Production-ready with SSL, monitoring, backups
- **Testing**: Comprehensive test coverage across all layers
- **Documentation**: Complete guides and architecture docs

The system demonstrates successful integration of AI agents for both agricultural domain expertise and development automation, creating a self-improving platform that can generate its own features and provide intelligent insights to farmers.
