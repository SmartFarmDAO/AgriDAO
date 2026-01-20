# Production Launch Design Document

## Overview

This design document outlines the comprehensive approach for launching AgriDAO into production. The platform is a full-stack decentralized agricultural marketplace built with FastAPI (Python), React (TypeScript), PostgreSQL, Redis, and Ethereum smart contracts. The launch strategy focuses on ensuring security, reliability, scalability, and operational excellence.

The design covers infrastructure setup, security hardening, deployment automation, monitoring, testing, and operational procedures. The goal is to create a production-ready environment that can handle real user traffic while maintaining high availability and data integrity.

## Architecture

### Current System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Users                                │
│              (Web Browsers, Mobile Devices)                  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Nginx Reverse Proxy                       │
│              (SSL Termination, Load Balancing)               │
└────────────┬────────────────────────────┬────────────────────┘
             │                            │
             │ HTTP                       │ HTTP
             ▼                            ▼
┌────────────────────────┐    ┌──────────────────────────────┐
│   React Frontend       │    │   FastAPI Backend            │
│   (Port 3000/80)       │    │   (Port 8000)                │
│   - Vite Build         │    │   - 19 API Routers           │
│   - Static Assets      │    │   - JWT Authentication       │
│   - Service Workers    │    │   - Middleware Stack         │
└────────────────────────┘    └──────────┬───────────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
         ┌──────────────────┐ ┌──────────────────┐ ┌─────────────────┐
         │   PostgreSQL     │ │      Redis       │ │   Blockchain    │
         │   (Port 5432)    │ │   (Port 6379)    │ │   (Ethereum)    │
         │   - User Data    │ │   - Sessions     │ │   - DAO Gov     │
         │   - Products     │ │   - Cache        │ │   - Escrow      │
         │   - Orders       │ │   - Rate Limit   │ └─────────────────┘
         └──────────────────┘ └──────────────────┘
```

### Production Infrastructure Components

1. **Frontend Layer**
   - React 18 SPA with TypeScript
   - Vite build system for optimized bundles
   - Static asset serving via Nginx
   - Service worker for offline support
   - Multi-language support (English/Bengali)

2. **Backend Layer**
   - FastAPI Python 3.12 application
   - 19 domain-specific routers (auth, marketplace, finance, AI, governance, etc.)
   - SQLAlchemy ORM with Alembic migrations
   - JWT-based authentication with refresh tokens
   - Middleware: CORS, rate limiting, security headers, XSS/CSRF protection

3. **Data Layer**
   - PostgreSQL 15+ for relational data
   - Redis 7+ for caching and session management
   - File storage for product images (uploads directory)

4. **Blockchain Layer**
   - Ethereum smart contracts (AgriDAO governance, MarketplaceEscrow)
   - Web3 integration via wagmi and RainbowKit
   - Hardhat for contract deployment and testing

5. **Infrastructure Layer**
   - Docker containers for all services
   - Nginx as reverse proxy and SSL terminator
   - Prometheus for metrics collection
   - Grafana for visualization

## Components and Interfaces

### 1. Deployment Pipeline Component

**Purpose**: Automate building, testing, and deploying code changes

**Interfaces**:
- GitHub Actions workflows (`.github/workflows/ci.yml`, `.github/workflows/deploy.yml`)
- Docker build and push operations
- SSH deployment to production server
- Database migration execution

**Key Functions**:
- `build_docker_images()`: Build backend and frontend Docker images
- `run_tests()`: Execute unit, integration, and E2E tests
- `deploy_to_production()`: SSH to server, pull code, restart containers
- `run_migrations()`: Execute Alembic database migrations
- `health_check()`: Verify services are running after deployment

### 2. Infrastructure Configuration Component

**Purpose**: Define and manage production infrastructure

**Interfaces**:
- Docker Compose files (`docker-compose.yml`, `deployment/docker/docker-compose.prod.yml`)
- Nginx configuration (`deployment/nginx/nginx.conf`, `deployment/docker/nginx.prod.conf`)
- Environment variable files (`.env`, `.env.production`)

**Key Functions**:
- `configure_docker_resources()`: Set memory and CPU limits for containers
- `configure_nginx()`: Set up reverse proxy, SSL, compression
- `configure_database()`: Set PostgreSQL connection pooling and memory settings
- `configure_redis()`: Set Redis memory limits and persistence
- `setup_ssl_certificates()`: Install and configure SSL certificates

### 3. Security Hardening Component

**Purpose**: Implement security measures across the stack

**Interfaces**:
- Backend middleware (`backend/app/middleware/security.py`)
- Frontend security utilities (`frontend/src/lib/security.ts`)
- Environment variable management

**Key Functions**:
- `validate_input()`: Sanitize and validate all user inputs
- `rate_limit_requests()`: Implement per-endpoint rate limiting
- `enforce_https()`: Redirect HTTP to HTTPS
- `set_security_headers()`: Add CSP, X-Frame-Options, etc.
- `hash_passwords()`: Use bcrypt for password hashing
- `validate_jwt_tokens()`: Verify and refresh JWT tokens
- `protect_csrf()`: Implement CSRF token validation

### 4. Database Management Component

**Purpose**: Manage database schema, migrations, and backups

**Interfaces**:
- Alembic migrations (`backend/alembic/versions/`)
- Database connection (`backend/app/database.py`)
- Backup scripts

**Key Functions**:
- `run_migrations()`: Apply database schema changes
- `create_admin_user()`: Initialize admin account
- `backup_database()`: Create encrypted database backups
- `verify_backup()`: Test backup restoration
- `optimize_queries()`: Add indexes and optimize slow queries

### 5. Monitoring and Logging Component

**Purpose**: Track system health, performance, and errors

**Interfaces**:
- Structured logging (`backend/app/core/logging.py`)
- Prometheus metrics (`deployment/docker/prometheus.yml`)
- Grafana dashboards
- Log aggregation

**Key Functions**:
- `log_request()`: Log API requests with correlation IDs
- `log_error()`: Log errors with stack traces
- `track_metric()`: Record custom business metrics
- `send_alert()`: Notify team of critical issues
- `rotate_logs()`: Prevent disk space exhaustion

### 6. Payment Processing Component

**Purpose**: Handle payment transactions via Stripe

**Interfaces**:
- Stripe API integration (`backend/app/services/payment_service.py`)
- Webhook handlers (`backend/app/routers/commerce.py`)
- Order management (`backend/app/services/order_service.py`)

**Key Functions**:
- `create_checkout_session()`: Initialize Stripe payment
- `handle_webhook()`: Process payment events
- `process_refund()`: Handle refund requests
- `verify_webhook_signature()`: Validate webhook authenticity
- `update_order_status()`: Update order after payment

### 7. Testing Framework Component

**Purpose**: Ensure code quality through automated testing

**Interfaces**:
- Backend tests (`backend/tests/`)
- Frontend tests (`frontend/src/`)
- E2E tests (`frontend/e2e/`)
- Load testing configuration

**Key Functions**:
- `run_unit_tests()`: Execute pytest tests
- `run_integration_tests()`: Test API endpoints
- `run_e2e_tests()`: Execute Playwright tests
- `run_load_tests()`: Simulate concurrent users
- `measure_coverage()`: Track test coverage

### 8. Backup and Recovery Component

**Purpose**: Protect data through regular backups

**Interfaces**:
- Backup scripts
- PostgreSQL pg_dump
- Cloud storage integration

**Key Functions**:
- `create_backup()`: Generate database backup
- `encrypt_backup()`: Encrypt backup files
- `upload_backup()`: Store backup remotely
- `restore_backup()`: Recover from backup
- `verify_backup()`: Test backup integrity

## Data Models

The application uses the following key data models (defined in `backend/app/models.py`):

### Core Models

1. **User**
   - Fields: id, role (buyer/farmer/admin), name, email, phone, status, timestamps
   - Relationships: orders, cart, notifications, posts, disputes

2. **Product**
   - Fields: id, name, description, category, price, quantity_available, unit, farmer_id, status, images, metadata
   - Relationships: farmer, order_items, cart_items, inventory_history

3. **Order**
   - Fields: id, buyer_id, status, subtotal, platform_fee, shipping_fee, total, payment_status, shipping_address
   - Relationships: buyer, order_items, status_history, payment_events, reviews, disputes

4. **Cart**
   - Fields: id, user_id, session_id, status, expires_at
   - Relationships: cart_items

5. **FundingRequest**
   - Fields: id, farmer_name, purpose, amount_needed, amount_raised, days_left, status

6. **Proposal** (DAO Governance)
   - Fields: id, title, description, status (open/passed/rejected)

7. **Post** (Social Features)
   - Fields: id, user_id, content, image_url, likes_count, comments_count
   - Relationships: comments, likes

8. **Dispute**
   - Fields: id, order_id, filed_by, dispute_type, status, subject, description, resolution
   - Relationships: order, messages

### Authentication Models

- **UserSession**: Tracks active user sessions with tokens
- **TokenBlacklist**: Invalidated JWT tokens

### Supporting Models

- **OrderItem**, **CartItem**, **ProductImage**, **InventoryHistory**
- **Notification**, **OrderReview**, **DisputeMessage**
- **Comment**, **Like**, **ProvenanceAsset**

All models use SQLModel (Pydantic + SQLAlchemy) for type safety and validation.

## Error Handling

### Error Handling Strategy

1. **API Error Responses**
   - Standardized error format: `{"detail": "message", "error_code": "CODE"}`
   - HTTP status codes: 400 (validation), 401 (auth), 403 (forbidden), 404 (not found), 500 (server error)
   - Correlation IDs for tracking errors across services

2. **Frontend Error Handling**
   - User-friendly error messages in selected language
   - Toast notifications for transient errors
   - Error boundaries for React component errors
   - Retry logic for network failures

3. **Database Error Handling**
   - Transaction rollback on errors
   - Integrity error handling (duplicate keys, foreign key violations)
   - Connection pool exhaustion handling
   - Query timeout handling

4. **Payment Error Handling**
   - Stripe API error handling with retry logic
   - Webhook signature verification failures
   - Payment declined handling
   - Refund failure handling

5. **Blockchain Error Handling**
   - Transaction failure handling
   - Gas estimation errors
   - Network connectivity issues
   - Contract interaction failures

### Error Logging

- All errors logged with stack traces and context
- Correlation IDs for request tracing
- Structured logging in JSON format
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Sensitive data redaction in logs

### Error Monitoring

- Real-time error tracking
- Error rate alerts
- Error grouping and deduplication
- Error trend analysis
- Automated incident creation for critical errors

## Testing Strategy

### Testing Pyramid

```
           ┌─────────────┐
          /   E2E Tests   \     (6 tests - critical flows)
         /─────────────────\
        /  Integration Tests \   (API endpoint tests)
       /─────────────────────\
      /     Unit Tests        \  (7,823 lines of tests)
     /───────────────────────\
```

### 1. Unit Testing

**Backend (pytest)**
- Test coverage: 25 test files covering services, routers, and models
- Key test areas:
  - Authentication and authorization
  - Cart and checkout logic
  - Order management
  - Payment processing
  - Product validation
  - Inventory management
  - Dispute resolution
  - Notification service
  - Rate limiting
  - Redis caching

**Frontend (Vitest)**
- Component testing with React Testing Library
- Hook testing
- Utility function testing
- Service layer testing

**Execution**:
```bash
# Backend
cd backend && pytest --cov --cov-report=html

# Frontend
cd frontend && npm test -- --coverage
```

### 2. Integration Testing

**API Integration Tests**
- Test complete request/response cycles
- Test authentication flows
- Test database interactions
- Test external service integrations (Stripe, blockchain)

**Database Integration Tests**
- Test migrations
- Test data integrity
- Test transaction handling
- Test query performance

### 3. End-to-End Testing

**Playwright E2E Tests** (6 test files)
- `auth.spec.ts`: Login, registration, logout flows
- `marketplace.spec.ts`: Product browsing, search, filtering
- `new-features.spec.ts`: Recent feature testing
- `performance.spec.ts`: Page load times, resource usage
- `security.spec.ts`: Security vulnerability testing
- `components-exist.spec.ts`: Critical component rendering

**Critical User Flows**:
1. User registration and login
2. Browse marketplace and add to cart
3. Checkout and payment
4. Order tracking
5. Farmer product listing
6. DAO proposal creation and voting

**Execution**:
```bash
cd frontend && npm run test:e2e
```

### 4. Load Testing

**Artillery Load Tests**
- Simulate concurrent users
- Test API endpoint performance under load
- Identify bottlenecks
- Verify rate limiting
- Test database connection pooling

**Test Scenarios**:
- 100 concurrent users browsing marketplace
- 50 concurrent checkout operations
- 200 requests/second to API
- Sustained load for 5 minutes

**Execution**:
```bash
cd frontend && npm run test:load
```

### 5. Security Testing

**Automated Security Scans**
- Dependency vulnerability scanning
- OWASP Top 10 testing
- SQL injection testing
- XSS testing
- CSRF testing
- Authentication bypass testing

**Manual Security Review**
- Code review for security issues
- Configuration review
- Access control verification
- Sensitive data handling review

### 6. Performance Testing

**Metrics to Track**:
- Page load time (target: <3s)
- Time to interactive (target: <5s)
- API response time (target: <500ms for 95th percentile)
- Database query time (target: <100ms for 95th percentile)
- Lighthouse scores (target: >70 for mobile, >90 for desktop)

### 7. Smoke Testing

**Post-Deployment Smoke Tests**:
- Health check endpoints return 200
- Database connectivity
- Redis connectivity
- Frontend loads successfully
- API authentication works
- Critical endpoints respond correctly

### Testing in CI/CD

**GitHub Actions Workflow**:
1. Lint and format check
2. Type checking (TypeScript, mypy)
3. Unit tests
4. Build Docker images
5. Integration tests
6. E2E tests (on staging)
7. Security scans
8. Deploy to production (if all pass)

### Test Data Management

- Use factories for test data generation
- Seed database with realistic test data
- Clean up test data after tests
- Use separate test database
- Mock external services (Stripe, blockchain) in tests


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Infrastructure and Configuration Properties

Property 1: Health check availability
*For any* critical service (backend, database, Redis, frontend), the service should expose a health check endpoint that returns a successful status when the service is operational
**Validates: Requirements 1.4**

Property 2: Request routing correctness
*For any* HTTP request to the Nginx reverse proxy, the request should be routed to the correct service (frontend or backend) based on the request path
**Validates: Requirements 1.5**

Property 3: No hardcoded credentials
*For any* configuration value that is sensitive (API keys, passwords, secrets), the value should be loaded from environment variables and not hardcoded in the codebase
**Validates: Requirements 1.8**

### Security Properties

Property 4: HTTPS enforcement
*For any* HTTP request to the platform, the request should be redirected to HTTPS when SSL is configured
**Validates: Requirements 3.1**

Property 5: SQL injection prevention
*For any* user input that is used in database queries, malicious SQL payloads should be rejected or sanitized to prevent SQL injection attacks
**Validates: Requirements 3.2**

Property 6: XSS protection
*For any* user input that is rendered in HTML, malicious JavaScript payloads should be sanitized or escaped to prevent XSS attacks
**Validates: Requirements 3.3**

Property 7: CSRF protection
*For any* state-changing API request (POST, PUT, DELETE), the request should be rejected if it lacks a valid CSRF token
**Validates: Requirements 3.4**

Property 8: JWT token expiration
*For any* JWT token, the token should be rejected if it has expired, and refresh tokens should enable obtaining new access tokens
**Validates: Requirements 3.6**

Property 9: Rate limiting enforcement
*For any* API endpoint with rate limiting configured, requests exceeding the rate limit should be rejected with a 429 status code
**Validates: Requirements 3.7**

Property 10: Sensitive data protection in logs
*For any* error or log message, sensitive data (passwords, API keys, tokens) should never be included in the logged output
**Validates: Requirements 3.8**

Property 11: File upload validation
*For any* file upload request, files that don't meet validation criteria (type, size, content) should be rejected
**Validates: Requirements 3.9**

Property 12: Security headers presence
*For any* HTTP response from the backend, the response should include appropriate security headers (X-Content-Type-Options, X-Frame-Options, CSP, etc.)
**Validates: Requirements 3.10**

Property 13: Session security
*For any* user session, the session should expire after the configured timeout period and session cookies should have secure and httpOnly flags set
**Validates: Requirements 3.11**

### Payment Processing Properties

Property 14: Webhook signature verification
*For any* payment webhook received from Stripe, the webhook should be rejected if the signature is invalid
**Validates: Requirements 4.3**

Property 15: Payment failure handling
*For any* failed payment, the system should log the error with details and notify the user of the failure
**Validates: Requirements 4.4**

Property 16: Payment success handling
*For any* successful payment, the system should update the order status to paid and send a confirmation notification to the user
**Validates: Requirements 4.5**

Property 17: Refund processing
*For any* refund request (partial or full), the system should update the order payment status and refund amount correctly
**Validates: Requirements 4.6**

Property 18: Payment retry with backoff
*For any* payment operation that fails due to Stripe unavailability, the system should retry the operation with exponential backoff
**Validates: Requirements 4.7**

### Monitoring and Logging Properties

Property 19: Error logging completeness
*For any* error that occurs in the system, the error should be logged with a correlation ID, timestamp, and stack trace
**Validates: Requirements 5.2**

Property 20: Request logging
*For any* API request, the system should log the request method, path, status code, and response time
**Validates: Requirements 5.4**

Property 21: Slow query logging
*For any* database query that takes longer than 1 second, the query should be logged for performance analysis
**Validates: Requirements 5.5**

### Performance Properties

Property 22: Static asset caching
*For any* static asset (JS, CSS, images), the response should include appropriate cache-control headers to enable browser caching
**Validates: Requirements 6.1**

Property 23: Cache utilization
*For any* frequently accessed data, subsequent requests for the same data should be served from Redis cache rather than querying the database
**Validates: Requirements 6.2**

Property 24: Image optimization
*For any* uploaded image, the image should be compressed and optimized before being stored
**Validates: Requirements 6.3**

Property 25: Pagination for large results
*For any* API endpoint that returns a list of items, if the total count exceeds the page size, the response should be paginated
**Validates: Requirements 6.5**

Property 26: Response compression
*For any* text-based HTTP response (HTML, JSON, CSS, JS), the response should be gzip compressed when the client supports it
**Validates: Requirements 6.7**

### Testing Properties

Property 27: API endpoint smoke tests
*For any* critical API endpoint, after deployment the endpoint should return a successful response for valid requests
**Validates: Requirements 7.5**

### Deployment Properties

Property 28: Docker image tagging
*For any* Docker image built in the CI/CD pipeline, the image should be tagged with both the commit SHA and a version number
**Validates: Requirements 8.2**

Property 29: Deployment rollback on failure
*For any* deployment that fails health checks, the system should automatically rollback to the previous working version
**Validates: Requirements 8.5**

Property 30: Health check verification before completion
*For any* deployment, the deployment should not be marked as successful until all service health checks pass
**Validates: Requirements 8.6**

### Data Management Properties

Property 31: Soft delete implementation
*For any* critical user data deletion request, the data should be marked as deleted rather than permanently removed from the database
**Validates: Requirements 9.6**

### User Communication Properties

Property 32: Error messages with support info
*For any* user-facing error, the error message should include support contact information
**Validates: Requirements 11.2**

### Compliance Properties

Property 33: Terms of service acceptance
*For any* user registration, the registration should not complete unless the user has accepted the terms of service
**Validates: Requirements 12.2**

Property 34: User data deletion
*For any* user data deletion request, the system should provide a mechanism to delete or anonymize the user's data
**Validates: Requirements 12.4**

### Blockchain Properties

Property 35: Blockchain transaction error handling
*For any* blockchain transaction that fails, the system should handle the failure gracefully without crashing and provide feedback to the user
**Validates: Requirements 13.3**

Property 36: Transaction status updates
*For any* pending blockchain transaction, the system should provide status updates to the user about the transaction progress
**Validates: Requirements 13.4**

### Multi-language Properties

Property 37: Language detection and setting
*For any* user accessing the platform, the system should detect the browser language and set the default language accordingly
**Validates: Requirements 14.1**

Property 38: Language preference persistence
*For any* user who changes their language preference, the preference should be saved and restored in subsequent sessions
**Validates: Requirements 14.2**

Property 39: Translation completeness
*For any* UI element, the element should have translations available in both English and Bengali
**Validates: Requirements 14.3**

Property 40: Error message translation
*For any* error message displayed to users, the message should be shown in the user's selected language
**Validates: Requirements 14.4**

### Mobile Responsiveness Properties

Property 41: Responsive layout
*For any* page accessed on a mobile device, the layout should adapt to the mobile screen size and remain usable
**Validates: Requirements 15.1**

Property 42: Touch-friendly controls
*For any* interactive element on mobile, the element should meet minimum touch target size requirements (44x44px)
**Validates: Requirements 15.2**

Property 43: Responsive images
*For any* image loaded on a mobile device, the system should serve an appropriately sized image for mobile bandwidth
**Validates: Requirements 15.3**

## Deployment Architecture

### Production Deployment Options

#### Option 1: AWS Lightsail (Recommended for MVP)

**Specifications**:
- Instance: 2GB RAM, 1 vCPU, 60GB SSD
- Cost: ~$10-20/month
- Suitable for: 100-500 concurrent users

**Setup**:
```bash
# Automated setup script
curl -fsSL https://raw.githubusercontent.com/yourusername/AgriDAO/main/deployment/lightsail/lightsail-setup.sh | bash

# Manual deployment
cd ~/agridao
docker-compose -f deployment/lightsail/docker-compose.lightsail.yml up -d
```

**Resource Allocation**:
- PostgreSQL: 512MB RAM, 0.5 CPU
- Redis: 256MB RAM, 0.25 CPU
- Backend: 768MB RAM, 0.5 CPU
- Frontend: 256MB RAM, 0.25 CPU
- Nginx: 256MB RAM, 0.25 CPU

#### Option 2: Docker Compose (Development/Staging)

**Setup**:
```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.yml -f deployment/docker/docker-compose.prod.yml up -d
```

#### Option 3: Kubernetes (Future Scaling)

For scaling beyond 1000 concurrent users, consider Kubernetes deployment with:
- Horizontal pod autoscaling
- Load balancing across multiple instances
- Managed database services (RDS, ElastiCache)
- CDN for static assets

### Deployment Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    Developer Workflow                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Code Commit to main branch                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  2. GitHub Actions CI Workflow                               │
│     - Lint and format check                                  │
│     - Type checking                                          │
│     - Unit tests                                             │
│     - Build Docker images                                    │
│     - Integration tests                                      │
│     - Security scans                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  3. GitHub Actions Deploy Workflow                           │
│     - SSH to production server                               │
│     - Pull latest code                                       │
│     - Run docker-compose up -d --build                       │
│     - Run database migrations                                │
│     - Verify health checks                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Post-Deployment Verification                             │
│     - Smoke tests                                            │
│     - Health check monitoring                                │
│     - Error rate monitoring                                  │
│     - Rollback if issues detected                            │
└─────────────────────────────────────────────────────────────┘
```

### Environment Configuration

#### Production Environment Variables

**Backend (.env)**:
```bash
# Database
DATABASE_URL=postgresql://user:password@db:5432/agridao_prod
REDIS_URL=redis://redis:6379/0

# Security
JWT_SECRET=<strong-random-secret>
SECRET_KEY=<strong-random-secret>

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Platform
PLATFORM_FEE_RATE=0.10
CORS_ORIGINS=https://yourdomain.com

# Monitoring
LOG_LEVEL=INFO
LOG_FILE=/var/log/agridao/backend.log
```

**Frontend (.env.production)**:
```bash
VITE_API_URL=https://api.yourdomain.com
VITE_PLATFORM_FEE_RATE=0.10

# Blockchain
VITE_AGRIDAO_ADDRESS=0x...
VITE_ESCROW_ADDRESS=0x...
```

### SSL/TLS Configuration

**Let's Encrypt Setup**:
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (already configured by certbot)
sudo certbot renew --dry-run
```

**Nginx SSL Configuration**:
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

### Database Migration Strategy

**Pre-Deployment**:
1. Backup current database
2. Test migrations on staging environment
3. Review migration SQL for potential issues

**During Deployment**:
```bash
# Automated in deployment script
docker-compose exec backend alembic upgrade head
```

**Rollback Procedure**:
```bash
# Rollback one migration
docker-compose exec backend alembic downgrade -1

# Rollback to specific version
docker-compose exec backend alembic downgrade <revision>

# Restore from backup if needed
psql -U postgres -d agridao_prod < backup.sql
```

### Monitoring Setup

**Prometheus Configuration** (`deployment/docker/prometheus.yml`):
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
  
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

**Grafana Dashboards**:
- System metrics (CPU, memory, disk, network)
- Application metrics (requests/sec, error rate, response time)
- Database metrics (connections, query time, cache hit rate)
- Business metrics (orders, revenue, active users)

**Alerting Rules**:
- Error rate > 5% for 5 minutes
- Response time p95 > 2 seconds for 5 minutes
- CPU usage > 80% for 10 minutes
- Memory usage > 90% for 5 minutes
- Disk usage > 85%
- Database connection pool exhaustion

### Backup and Recovery

**Automated Backup Script**:
```bash
#!/bin/bash
# /opt/agridao/backup.sh

BACKUP_DIR="/opt/agridao/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/agridao_$DATE.sql.gz"

# Create backup
docker-compose exec -T db pg_dump -U postgres agridao_prod | gzip > $BACKUP_FILE

# Encrypt backup
gpg --encrypt --recipient admin@agridao.com $BACKUP_FILE

# Upload to S3 (optional)
aws s3 cp $BACKUP_FILE.gpg s3://agridao-backups/

# Delete backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz*" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE"
```

**Cron Schedule**:
```cron
# Daily backup at 2 AM
0 2 * * * /opt/agridao/backup.sh >> /var/log/agridao/backup.log 2>&1

# Weekly backup verification
0 3 * * 0 /opt/agridao/verify-backup.sh >> /var/log/agridao/backup-verify.log 2>&1
```

**Recovery Procedure**:
```bash
# Stop application
docker-compose down

# Restore database
gunzip < backup.sql.gz | docker-compose exec -T db psql -U postgres agridao_prod

# Restart application
docker-compose up -d

# Verify health
curl http://localhost:8000/health
```

### Security Checklist

**Pre-Launch Security Audit**:
- [ ] All environment variables configured (no defaults)
- [ ] SSL certificates installed and auto-renewal configured
- [ ] Firewall rules configured (only 22, 80, 443 open)
- [ ] Database passwords changed from defaults
- [ ] Admin user created with strong password
- [ ] CORS origins restricted to production domains
- [ ] Rate limiting configured on all endpoints
- [ ] CSRF protection enabled
- [ ] XSS protection middleware active
- [ ] Security headers configured in Nginx
- [ ] File upload validation implemented
- [ ] SQL injection prevention verified (parameterized queries)
- [ ] Sensitive data not logged
- [ ] Session timeout configured
- [ ] JWT expiration configured
- [ ] Stripe webhook signature verification enabled
- [ ] Dependency vulnerability scan completed
- [ ] Code security review completed

### Performance Optimization Checklist

**Pre-Launch Performance Audit**:
- [ ] Database indexes created for common queries
- [ ] Redis caching enabled for frequently accessed data
- [ ] Static assets served with cache headers
- [ ] Gzip compression enabled in Nginx
- [ ] Images optimized and compressed
- [ ] Frontend bundle size optimized (<500KB initial)
- [ ] Lazy loading implemented for images and components
- [ ] API pagination implemented for large result sets
- [ ] Database connection pooling configured
- [ ] Slow query logging enabled
- [ ] CDN configured for static assets (optional)
- [ ] Service worker configured for offline support
- [ ] Lighthouse scores: Mobile >70, Desktop >90

### Launch Checklist

**Pre-Launch Tasks**:
- [ ] All requirements reviewed and implemented
- [ ] All tests passing (unit, integration, E2E)
- [ ] Load testing completed successfully
- [ ] Security audit completed
- [ ] Performance audit completed
- [ ] Documentation completed
- [ ] Backup and recovery procedures tested
- [ ] Monitoring and alerting configured
- [ ] SSL certificates installed
- [ ] Domain DNS configured
- [ ] Terms of service and privacy policy published
- [ ] Support email configured
- [ ] Status page created
- [ ] Incident response procedures documented
- [ ] Team trained on operations and troubleshooting

**Launch Day Tasks**:
- [ ] Final backup of staging data
- [ ] Deploy to production
- [ ] Run database migrations
- [ ] Verify all services healthy
- [ ] Run smoke tests
- [ ] Monitor error rates and performance
- [ ] Announce launch to users
- [ ] Monitor user feedback and issues

**Post-Launch Tasks**:
- [ ] Monitor system for 24 hours
- [ ] Address any critical issues immediately
- [ ] Review logs for errors and warnings
- [ ] Verify backups are running
- [ ] Verify monitoring and alerts working
- [ ] Collect user feedback
- [ ] Plan first post-launch improvements

### Rollback Plan

**Rollback Triggers**:
- Critical bugs affecting core functionality
- Security vulnerabilities discovered
- Performance degradation >50%
- Error rate >10%
- Database corruption

**Rollback Procedure**:
```bash
# 1. Stop current deployment
docker-compose down

# 2. Checkout previous version
git checkout <previous-commit>

# 3. Restore database if needed
gunzip < backup.sql.gz | docker-compose exec -T db psql -U postgres agridao_prod

# 4. Restart services
docker-compose up -d

# 5. Verify health
curl http://localhost:8000/health

# 6. Notify team
echo "Rollback completed at $(date)" | mail -s "AgriDAO Rollback" team@agridao.com
```

### Scaling Strategy

**Vertical Scaling** (First 1000 users):
- Upgrade to 4GB RAM, 2 vCPU instance
- Increase database connection pool
- Increase Redis memory limit

**Horizontal Scaling** (1000+ users):
- Multiple backend instances behind load balancer
- Separate database server (managed RDS)
- Separate Redis server (managed ElastiCache)
- CDN for static assets (CloudFront, Cloudflare)
- Read replicas for database
- Kubernetes for orchestration

**Database Scaling**:
- Connection pooling (already implemented)
- Query optimization and indexing
- Read replicas for read-heavy operations
- Partitioning for large tables
- Caching layer (Redis) for frequently accessed data

**Caching Strategy**:
- Product listings: 5 minute TTL
- User sessions: 24 hour TTL
- API rate limiting: 1 minute TTL
- Search results: 10 minute TTL
- Static content: 1 day TTL
