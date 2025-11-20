# AgriDAO Project Structure

## 📁 Root Directory Structure

```
AgriDAO/
├── frontend/              # React frontend application
├── backend/               # FastAPI backend application
├── mobile/                # React Native mobile app
├── docs/                  # Comprehensive documentation
├── scripts/               # Automation and utility scripts
├── .github/               # GitHub workflows and actions
├── .kiro/                 # Kiro CLI configuration
├── docker-compose.yml     # Development Docker configuration
├── docker-compose.prod.yml # Production Docker configuration
├── nginx.conf             # Development Nginx configuration
├── nginx.prod.conf        # Production Nginx configuration
├── prometheus.yml         # Monitoring configuration
├── load-tests.yml         # Load testing configuration
├── init.sql               # Database initialization
├── README.md              # Main project documentation
├── SECURITY.md            # Security policies
└── PROJECT_STRUCTURE.md   # This file
```

## 📚 Documentation Structure

```
docs/
├── INDEX.md                    # Documentation index and navigation
├── README.md                   # Documentation overview
│
├── guides/                     # User and developer guides
│   ├── DEMO_GUIDE.md
│   ├── DEMO_QUICK_REFERENCE.md
│   ├── MARKETPLACE_FEATURES.md
│   ├── QUICK_START_CART.md
│   ├── GUEST_CART_FEATURE.md
│   ├── CHANGE_USER_ROLE_GUIDE.md
│   ├── QUICK_ROLE_CHANGE.md
│   ├── MULTI_IMAGE_UPLOAD.md
│   ├── INTEGRATION_TESTING.md
│   ├── TEST_CHECKLIST.md
│   └── POST_REORGANIZATION_CHECKLIST.md
│
├── architecture/               # System architecture documentation
│   ├── SYSTEM_ANALYSIS.md
│   ├── BACKEND_ARCHITECTURE.md
│   ├── FRONTEND_REORGANIZATION_COMPLETE.md
│   └── REORGANIZATION.md
│
├── deployment/                 # Deployment and setup guides
│   ├── DOCKER_DEPLOYMENT.md
│   ├── DOCKER_SETUP_SUMMARY.md
│   ├── ADMIN_SETUP_INSTRUCTIONS.md
│   ├── GMAIL_OTP_SETUP.md
│   └── FREE_OTP_SETUP_GUIDE.md
│
├── troubleshooting/           # Problem resolution guides
│   ├── QUICK_FIX_GUIDE.md
│   ├── QUICK_ACTION_NEEDED.md
│   ├── AUTH_FIXED.md
│   ├── FIX_SUMMARY.md
│   ├── USER_MANAGEMENT_FIX.md
│   ├── ADMIN_USER_MANAGEMENT_DEBUG.md
│   ├── CHECK_BACKEND_STATUS.md
│   ├── USER_ALREADY_FARMER.md
│   ├── CART_FIX_SUMMARY.md
│   ├── ISSUE_RESOLVED.md
│   ├── PRODUCT_MODERATION_FIX.md
│   └── CONSOLE_WARNINGS_EXPLAINED.md
│
├── project/                   # Project management documentation
│   ├── requirements.md
│   ├── roadmap.md
│   ├── userstory.md
│   ├── AGRIDAO_SUMMARY.md
│   └── WARP.md
│
├── api/                       # API documentation
│   └── README.md
│
├── development/               # Development guidelines
│   ├── architecture.md
│   └── testing.md
│
├── operations/                # Operations documentation
│   └── deployment-guide.md
│
├── user-guide/                # End-user documentation
│   └── README.md
│
├── user-stories/              # User stories and scenarios
│   └── MARKETPLACE.md
│
├── getting-started/           # Quick start guides
│   └── README.md
│
└── legacy/                    # Historical documentation
    ├── COMPLETION_SUMMARY.md
    └── IMPLEMENTATION_SUMMARY.md
```

## 🎨 Frontend Structure

```
frontend/
├── src/
│   ├── components/            # Reusable UI components
│   │   ├── layout/           # Layout components
│   │   └── ui/               # UI primitives (Radix UI)
│   ├── pages/                # Route pages
│   ├── hooks/                # Custom React hooks
│   ├── lib/                  # Utility libraries
│   ├── services/             # API services
│   ├── config/               # Configuration files
│   ├── utils/                # Utility functions
│   └── test/                 # Test utilities
│
├── e2e/                      # End-to-end tests
│   └── utils/                # Test utilities
│
├── public/                   # Static assets
│   ├── manifest.json         # PWA manifest
│   ├── sw.js                 # Service worker
│   └── offline.html          # Offline fallback
│
├── dist/                     # Production build output
├── node_modules/             # Dependencies
├── index.html                # Entry HTML
├── package.json              # Dependencies and scripts
├── vite.config.ts            # Vite configuration
├── vitest.config.ts          # Vitest configuration
├── playwright.config.ts      # Playwright configuration
├── tailwind.config.ts        # Tailwind CSS configuration
├── tsconfig.json             # TypeScript configuration
├── eslint.config.js          # ESLint configuration
├── .env                      # Environment variables
├── .env.example              # Environment template
├── .env.production           # Production environment
├── Dockerfile                # Development Dockerfile
├── Dockerfile.prod           # Production Dockerfile
├── nginx.frontend.conf       # Frontend Nginx config
└── README.md                 # Frontend documentation
```

## 🔧 Backend Structure

```
backend/
├── app/
│   ├── routers/              # API route handlers
│   ├── middleware/           # Custom middleware
│   ├── database/             # Database configuration
│   ├── core/                 # Core functionality
│   ├── models/               # Database models
│   ├── services/             # Business logic services
│   ├── api/                  # API utilities
│   ├── __pycache__/          # Python cache
│   ├── models.py             # Legacy models
│   ├── database.py           # Database setup
│   ├── deps.py               # Dependencies
│   └── main.py               # Application entry point
│
├── tests/                    # Backend tests
│   └── __pycache__/          # Test cache
│
├── alembic/                  # Database migrations
│   └── versions/             # Migration versions
│
├── uploads/                  # File uploads
│   └── images/               # Image uploads
│
├── scripts/                  # Utility scripts
├── .venv/                    # Python virtual environment
├── .pytest_cache/            # Pytest cache
├── requirements.txt          # Python dependencies
├── alembic.ini               # Alembic configuration
├── pyproject.toml            # Python project config
├── Dockerfile                # Backend Dockerfile
├── .env                      # Environment variables
├── .env.example              # Environment template
├── .env.production           # Production environment
├── .gitignore                # Git ignore rules
├── README.md                 # Backend documentation
├── create_admin.py           # Admin creation script
├── update_user_role.py       # Role update script
├── check_status.py           # Status check script
├── describe_product.sql      # SQL utility
├── show_products.sql         # SQL utility
├── show_all_tables.sql       # SQL utility
└── update_admin.sql          # SQL utility
```

## 📱 Mobile Structure

```
mobile/
├── app/                      # App screens and navigation
│   ├── (tabs)/              # Tab navigation
│   └── product/             # Product screens
│
├── components/               # Reusable components
│   └── __tests__/           # Component tests
│
├── constants/                # App constants
├── assets/                   # Static assets
│   ├── images/              # Image assets
│   └── fonts/               # Font files
│
├── ui/                       # UI primitives
├── .expo/                    # Expo configuration
├── node_modules/             # Dependencies
├── app.json                  # Expo app config
├── package.json              # Dependencies and scripts
├── tsconfig.json             # TypeScript configuration
├── expo-env.d.ts             # Expo type definitions
├── .env                      # Environment variables
└── .gitignore                # Git ignore rules
```

## 🔨 Scripts Structure

```
scripts/
├── setup/                    # Setup scripts
│   └── setup-free-otp.sh    # OTP setup
│
├── deployment/               # Deployment scripts
│   ├── deploy.sh            # Deployment automation
│   └── integration-test.sh  # Integration testing
│
├── testing/                  # Testing scripts
│   ├── test-marketplace.sh  # Marketplace tests
│   └── validate-system.sh   # System validation
│
└── maintenance/              # Maintenance scripts
```

## 🔐 Configuration Files

### Root Level
- `.gitignore` - Git ignore patterns
- `.editorconfig` - Editor configuration
- `.pre-commit-config.yaml` - Pre-commit hooks
- `.env` - Environment variables (not in git)

### Frontend
- `vite.config.ts` - Vite bundler configuration
- `vitest.config.ts` - Unit test configuration
- `playwright.config.ts` - E2E test configuration
- `tailwind.config.ts` - Tailwind CSS configuration
- `tsconfig.json` - TypeScript configuration
- `eslint.config.js` - Linting rules
- `components.json` - UI components config

### Backend
- `alembic.ini` - Database migration configuration
- `pyproject.toml` - Python project metadata
- `requirements.txt` - Python dependencies

### Docker
- `docker-compose.yml` - Development services
- `docker-compose.prod.yml` - Production services
- `docker-compose.override.yml` - Local overrides

### Nginx
- `nginx.conf` - Development proxy
- `nginx.prod.conf` - Production proxy
- `frontend/nginx.frontend.conf` - Frontend-specific

## 📊 Key Directories Explained

### `/frontend/src/components`
Reusable React components organized by function:
- `layout/` - Page layouts and structure
- `ui/` - Radix UI primitives and custom UI components

### `/frontend/src/pages`
Route-based page components:
- Each file represents a route in the application
- Contains page-specific logic and composition

### `/backend/app/routers`
API endpoint definitions:
- Organized by feature/domain
- Contains route handlers and validation

### `/backend/app/services`
Business logic layer:
- Separated from route handlers
- Reusable across different endpoints

### `/docs`
Comprehensive documentation:
- Organized by category for easy navigation
- Includes guides, architecture, and troubleshooting

## 🚀 Quick Navigation

- **Start Development**: See [Getting Started](./docs/getting-started/README.md)
- **Deploy to Production**: See [Deployment Guide](./docs/deployment/DOCKER_DEPLOYMENT.md)
- **Run Tests**: See [Testing Guide](./docs/development/testing.md)
- **Troubleshoot Issues**: See [Troubleshooting](./docs/troubleshooting/)
- **API Reference**: See [API Documentation](./docs/api/README.md)
- **Architecture Details**: See [Architecture](./docs/architecture/)

## 📝 File Naming Conventions

- **Documentation**: `UPPERCASE_WITH_UNDERSCORES.md`
- **Configuration**: `lowercase-with-dashes.config.ts`
- **Components**: `PascalCase.tsx`
- **Utilities**: `camelCase.ts`
- **Tests**: `*.test.ts` or `*.spec.ts`
- **Scripts**: `kebab-case.sh`

## 🔍 Finding Files

Use these patterns to locate specific types of files:

```bash
# Find all TypeScript components
find frontend/src -name "*.tsx"

# Find all test files
find . -name "*.test.ts" -o -name "*.spec.ts"

# Find all documentation
find docs -name "*.md"

# Find all configuration files
find . -name "*.config.*" -o -name "*.conf"

# Find all Python files
find backend -name "*.py"
```

## 📦 Build Artifacts

These directories contain generated files (not in git):

- `frontend/dist/` - Production frontend build
- `frontend/node_modules/` - Frontend dependencies
- `backend/.venv/` - Python virtual environment
- `backend/__pycache__/` - Python bytecode cache
- `mobile/node_modules/` - Mobile dependencies
- `.mypy_cache/` - MyPy type checking cache
- `.kiro/` - Kiro CLI cache

## 🔄 Version Control

Key files tracked in git:
- Source code (`*.ts`, `*.tsx`, `*.py`)
- Configuration files
- Documentation (`*.md`)
- Package manifests (`package.json`, `requirements.txt`)
- Docker configurations
- CI/CD workflows

Files ignored by git:
- Dependencies (`node_modules/`, `.venv/`)
- Build artifacts (`dist/`, `__pycache__/`)
- Environment files (`.env`)
- IDE settings (`.vscode/`, `.idea/`)
- OS files (`.DS_Store`)
