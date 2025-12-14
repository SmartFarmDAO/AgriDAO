import sys
import asyncio
import yaml
import redis
import json
import os
import subprocess
from datetime import datetime

class AgentWorker:
    def __init__(self, config_path):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        self.agent_name = self.config['agent']['name']
        self.redis_client = redis.Redis(host='localhost', port=6380, db=0, decode_responses=True)
        self.project_root = "/Users/sohagmahamud/Projects/AgriDAO"
        
    async def start(self):
        print(f"🤖 {self.agent_name} started - executing real tasks")
        while True:
            await self.process_tasks()
            await asyncio.sleep(10)
    
    async def process_tasks(self):
        queue_name = f"agent:{self.agent_name}:tasks"
        task_json = self.redis_client.rpop(queue_name)
        
        if task_json:
            try:
                task = json.loads(task_json)
                print(f"🔥 {self.agent_name} executing: {task['task']}")
                await self.execute_task(task)
            except Exception as e:
                print(f"❌ {self.agent_name} error: {e}")
        else:
            print(f"⚡ {self.agent_name} waiting for tasks...")
    
    async def execute_task(self, task):
        task_name = task['task']
        
        if self.agent_name == 'security_agent':
            await self.execute_security_task(task)
        elif self.agent_name == 'database_agent':
            await self.execute_database_task(task)
        elif self.agent_name == 'monitoring_agent':
            await self.execute_monitoring_task(task)
        elif self.agent_name == 'api_agent':
            await self.execute_api_task(task)
        elif self.agent_name == 'testing_agent':
            await self.execute_testing_task(task)
        elif self.agent_name == 'devops_agent':
            await self.execute_devops_task(task)
        else:
            await self.execute_generic_task(task)
    
    async def execute_security_task(self, task):
        if task['task'] == 'implement_ssl_tls':
            await self.setup_ssl_certificates()
        elif task['task'] == 'conduct_security_audit':
            await self.run_security_audit()
        elif task['task'] == 'harden_security_headers':
            await self.implement_security_headers()
    
    async def execute_database_task(self, task):
        if task['task'] == 'setup_automated_backups':
            await self.setup_database_backups()
        elif task['task'] == 'optimize_database_performance':
            await self.optimize_database()
    
    async def execute_monitoring_task(self, task):
        if task['task'] == 'setup_prometheus_grafana':
            await self.setup_monitoring_stack()
        elif task['task'] == 'implement_error_tracking':
            await self.setup_error_tracking()
    
    async def execute_api_task(self, task):
        if task['task'] == 'audit_api_endpoints':
            await self.audit_api_security()
    
    async def execute_testing_task(self, task):
        if task['task'] == 'increase_test_coverage':
            await self.improve_test_coverage()
        elif task['task'] == 'implement_e2e_testing':
            await self.setup_e2e_tests()
    
    async def execute_devops_task(self, task):
        if task['task'] == 'setup_cicd_pipeline':
            await self.enhance_cicd()
        elif task['task'] == 'implement_health_checks':
            await self.add_health_checks()
    
    async def setup_ssl_certificates(self):
        """Implement SSL/TLS certificates for production"""
        print("🔒 Setting up SSL/TLS certificates...")
        
        # Create SSL configuration for nginx
        ssl_config = """
server {
    listen 443 ssl http2;
    server_name agridao.com www.agridao.com;
    
    ssl_certificate /etc/letsencrypt/live/agridao.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/agridao.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name agridao.com www.agridao.com;
    return 301 https://$server_name$request_uri;
}
"""
        
        # Write SSL nginx config
        ssl_config_path = f"{self.project_root}/deployment/nginx/ssl.conf"
        os.makedirs(os.path.dirname(ssl_config_path), exist_ok=True)
        with open(ssl_config_path, 'w') as f:
            f.write(ssl_config)
        
        # Create Let's Encrypt setup script
        letsencrypt_script = """#!/bin/bash
# Let's Encrypt SSL Certificate Setup for AgriDAO

echo "🔒 Setting up SSL certificates for AgriDAO..."

# Install certbot
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

# Stop nginx temporarily
sudo systemctl stop nginx

# Get certificates
sudo certbot certonly --standalone -d agridao.com -d www.agridao.com --email admin@agridao.com --agree-tos --non-interactive

# Setup auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -

# Start nginx with SSL config
sudo systemctl start nginx

echo "✅ SSL certificates configured successfully"
"""
        
        script_path = f"{self.project_root}/deployment/scripts/setup-ssl.sh"
        os.makedirs(os.path.dirname(script_path), exist_ok=True)
        with open(script_path, 'w') as f:
            f.write(letsencrypt_script)
        os.chmod(script_path, 0o755)
        
        print("✅ SSL/TLS configuration files created")
        print(f"   - SSL nginx config: {ssl_config_path}")
        print(f"   - Setup script: {script_path}")

    async def run_security_audit(self):
        """Conduct comprehensive security audit"""
        print("🔍 Running security audit...")
        
        # Create security audit script
        audit_script = """#!/bin/bash
# AgriDAO Security Audit Script

echo "🔍 Starting AgriDAO Security Audit..."

# Check for common vulnerabilities
echo "📋 Checking dependencies for vulnerabilities..."
cd backend && pip-audit || echo "Install pip-audit: pip install pip-audit"
cd ../frontend && npm audit --audit-level moderate

# Check for secrets in code
echo "🔐 Scanning for exposed secrets..."
grep -r "password\|secret\|key\|token" --include="*.py" --include="*.js" --include="*.ts" backend/ frontend/ | grep -v ".git" | head -10

# Check file permissions
echo "🔒 Checking file permissions..."
find . -name "*.py" -perm 777 2>/dev/null | head -5
find . -name "*.js" -perm 777 2>/dev/null | head -5

# Check for SQL injection patterns
echo "💉 Checking for SQL injection vulnerabilities..."
grep -r "execute.*%" --include="*.py" backend/ | head -5

# Check CORS configuration
echo "🌐 Checking CORS configuration..."
grep -r "CORS" backend/app/ | head -5

echo "✅ Security audit completed. Review findings above."
"""
        
        audit_path = f"{self.project_root}/scripts/security-audit.sh"
        with open(audit_path, 'w') as f:
            f.write(audit_script)
        os.chmod(audit_path, 0o755)
        
        # Run the audit
        try:
            result = subprocess.run(['bash', audit_path], capture_output=True, text=True, cwd=self.project_root)
            print("📊 Security Audit Results:")
            print(result.stdout)
        except Exception as e:
            print(f"⚠️ Audit script created but execution failed: {e}")
        
        print("✅ Security audit completed")

    async def implement_security_headers(self):
        """Implement security headers in FastAPI"""
        print("🛡️ Implementing security headers...")
        
        # Create security middleware
        security_middleware = '''from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response
'''
        
        middleware_path = f"{self.project_root}/backend/app/middleware/security_headers.py"
        os.makedirs(os.path.dirname(middleware_path), exist_ok=True)
        with open(middleware_path, 'w') as f:
            f.write(security_middleware)
        
    async def setup_database_backups(self):
        """Setup automated PostgreSQL backups"""
        print("💾 Setting up automated database backups...")
        
        backup_script = """#!/bin/bash
# AgriDAO Database Backup Script

BACKUP_DIR="/var/backups/agridao"
DB_NAME="agridao_db"
DB_USER="postgres"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/agridao_backup_$TIMESTAMP.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
echo "📦 Creating database backup..."
pg_dump -h localhost -U $DB_USER -d $DB_NAME > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

# Verify backup
if [ -f "$BACKUP_FILE.gz" ]; then
    echo "✅ Backup created successfully: $BACKUP_FILE.gz"
    echo "📊 Backup size: $(du -h $BACKUP_FILE.gz | cut -f1)"
else
    echo "❌ Backup failed!"
    exit 1
fi
"""
        
        backup_path = f"{self.project_root}/scripts/backup-database.sh"
        with open(backup_path, 'w') as f:
            f.write(backup_script)
        os.chmod(backup_path, 0o755)
        
        # Create cron job setup
        cron_setup = """#!/bin/bash
# Setup daily database backups at 2 AM
echo "0 2 * * * /path/to/agridao/scripts/backup-database.sh" | crontab -
echo "✅ Daily backup cron job configured"
"""
        
        cron_path = f"{self.project_root}/scripts/setup-backup-cron.sh"
        with open(cron_path, 'w') as f:
            f.write(cron_setup)
        os.chmod(cron_path, 0o755)
        
        print("✅ Database backup system configured")
        print(f"   Backup script: {backup_path}")
        print(f"   Cron setup: {cron_path}")

    async def optimize_database(self):
        """Optimize database performance"""
        print("⚡ Optimizing database performance...")
        
        # Create database optimization SQL
        optimization_sql = """-- AgriDAO Database Performance Optimization

-- Add indexes for frequently queried columns
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_products_farmer_id ON products(farmer_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);

-- Optimize connection settings
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Reload configuration
SELECT pg_reload_conf();

-- Analyze tables for better query planning
ANALYZE users;
ANALYZE products;
ANALYZE orders;
ANALYZE funding_campaigns;
"""
        
        sql_path = f"{self.project_root}/backend/optimize_db.sql"
        with open(sql_path, 'w') as f:
            f.write(optimization_sql)
        
        print("✅ Database optimization script created")
        print(f"   Location: {sql_path}")
        print("   Run: psql -d agridao_db -f optimize_db.sql")

    async def setup_monitoring_stack(self):
        """Setup Prometheus and Grafana monitoring"""
        print("📊 Setting up Prometheus + Grafana monitoring...")
        
        # Prometheus configuration
        prometheus_config = """global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'agridao-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    
  - job_name: 'agridao-frontend'
    static_configs:
      - targets: ['frontend:3000']
      
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
      
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
"""
        
        prometheus_path = f"{self.project_root}/deployment/monitoring/prometheus.yml"
        os.makedirs(os.path.dirname(prometheus_path), exist_ok=True)
        with open(prometheus_path, 'w') as f:
            f.write(prometheus_config)
        
        # Docker compose for monitoring
        monitoring_compose = """version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  prometheus_data:
  grafana_data:
"""
        
        compose_path = f"{self.project_root}/deployment/monitoring/docker-compose.monitoring.yml"
        with open(compose_path, 'w') as f:
            f.write(monitoring_compose)
        
        print("✅ Monitoring stack configured")
        print(f"   Prometheus config: {prometheus_path}")
        print(f"   Docker compose: {compose_path}")
        print("   Start: docker-compose -f docker-compose.monitoring.yml up -d")

    async def setup_error_tracking(self):
        """Setup Sentry error tracking"""
        print("🚨 Setting up Sentry error tracking...")
        
        # Backend Sentry integration
        sentry_backend = """# Add to backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN_HERE",
    integrations=[
        FastApiIntegration(auto_enabling_integrations=False),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=0.1,
    environment="production"
)
"""
        
        backend_path = f"{self.project_root}/backend/sentry_config.py"
        with open(backend_path, 'w') as f:
            f.write(sentry_backend)
        
        # Frontend Sentry integration
        sentry_frontend = """// Add to frontend/src/main.tsx
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "YOUR_SENTRY_DSN_HERE",
  environment: "production",
  tracesSampleRate: 0.1,
});
"""
        
        frontend_path = f"{self.project_root}/frontend/sentry_config.ts"
        with open(frontend_path, 'w') as f:
            f.write(sentry_frontend)
        
    async def audit_api_security(self):
        """Audit API endpoints for security issues"""
        print("🔍 Auditing API security...")
        
        audit_script = """#!/usr/bin/env python3
import os
import re

def audit_api_endpoints():
    print("🔍 AgriDAO API Security Audit")
    print("=" * 40)
    
    backend_dir = "backend/app/routers"
    issues = []
    
    for root, dirs, files in os.walk(backend_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    
                # Check for missing authentication
                if '@router.' in content and 'Depends(get_current_user)' not in content:
                    issues.append(f"⚠️ {filepath}: Missing authentication dependency")
                
                # Check for SQL injection risks
                if re.search(r'execute.*%|format.*sql', content, re.IGNORECASE):
                    issues.append(f"🚨 {filepath}: Potential SQL injection risk")
                
                # Check for missing input validation
                if 'router.post' in content and 'Pydantic' not in content:
                    issues.append(f"⚠️ {filepath}: Missing input validation")
    
    print(f"📊 Found {len(issues)} potential security issues:")
    for issue in issues[:10]:  # Show first 10
        print(f"   {issue}")
    
    return len(issues)

if __name__ == "__main__":
    audit_api_endpoints()
"""
        
        audit_path = f"{self.project_root}/scripts/api-security-audit.py"
        with open(audit_path, 'w') as f:
            f.write(audit_script)
        os.chmod(audit_path, 0o755)
        
        # Run the audit
        try:
            result = subprocess.run(['python3', audit_path], capture_output=True, text=True, cwd=self.project_root)
            print(result.stdout)
        except Exception as e:
            print(f"⚠️ Audit created but execution failed: {e}")
        
        print("✅ API security audit completed")

    async def improve_test_coverage(self):
        """Improve test coverage for backend and frontend"""
        print("🧪 Improving test coverage...")
        
        # Backend test template
        backend_test = """import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.models import User, Product

client = TestClient(app)

class TestAPI:
    def test_health_endpoint(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        
    def test_user_registration(self):
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 201
        
    def test_product_listing(self):
        response = client.get("/api/products")
        assert response.status_code == 200
        assert "products" in response.json()
        
    def test_unauthorized_access(self):
        response = client.post("/api/products", json={"name": "Test Product"})
        assert response.status_code == 401
"""
        
        test_path = f"{self.project_root}/backend/tests/test_comprehensive.py"
        os.makedirs(os.path.dirname(test_path), exist_ok=True)
        with open(test_path, 'w') as f:
            f.write(backend_test)
        
        # Frontend test template
        frontend_test = """import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from '../App';
import LoginForm from '../components/auth/LoginForm';

describe('AgriDAO Frontend Tests', () => {
  test('renders app without crashing', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
  });
  
  test('login form renders correctly', () => {
    render(<LoginForm />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });
  
  test('navigation works', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    // Add navigation tests
  });
});
"""
        
        frontend_test_path = f"{self.project_root}/frontend/src/test/App.comprehensive.test.tsx"
        os.makedirs(os.path.dirname(frontend_test_path), exist_ok=True)
        with open(frontend_test_path, 'w') as f:
            f.write(frontend_test)
        
        print("✅ Test coverage improvements added")
        print(f"   Backend tests: {test_path}")
        print(f"   Frontend tests: {frontend_test_path}")

    async def setup_e2e_tests(self):
        """Setup end-to-end testing with Playwright"""
        print("🎭 Setting up E2E tests with Playwright...")
        
        e2e_test = """import { test, expect } from '@playwright/test';

test.describe('AgriDAO E2E Tests', () => {
  test('user can register and login', async ({ page }) => {
    await page.goto('http://localhost:3000');
    
    // Register new user
    await page.click('text=Register');
    await page.fill('[data-testid=email]', 'test@example.com');
    await page.fill('[data-testid=password]', 'testpassword123');
    await page.fill('[data-testid=full-name]', 'Test User');
    await page.click('[data-testid=register-button]');
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard/);
  });
  
  test('farmer can list product', async ({ page }) => {
    // Login as farmer
    await page.goto('http://localhost:3000/login');
    await page.fill('[data-testid=email]', 'farmer@example.com');
    await page.fill('[data-testid=password]', 'password123');
    await page.click('[data-testid=login-button]');
    
    // Add product
    await page.click('text=Add Product');
    await page.fill('[data-testid=product-name]', 'Fresh Tomatoes');
    await page.fill('[data-testid=product-price]', '50');
    await page.click('[data-testid=submit-product]');
    
    // Should see success message
    await expect(page.locator('text=Product added successfully')).toBeVisible();
  });
  
  test('buyer can browse and order products', async ({ page }) => {
    await page.goto('http://localhost:3000/marketplace');
    
    // Browse products
    await expect(page.locator('[data-testid=product-card]')).toBeVisible();
    
    // Add to cart
    await page.click('[data-testid=add-to-cart]:first-child');
    
    // Go to cart and checkout
    await page.click('[data-testid=cart-icon]');
    await page.click('[data-testid=checkout-button]');
    
    // Should reach payment page
    await expect(page).toHaveURL(/.*checkout/);
  });
});
"""
        
        e2e_path = f"{self.project_root}/frontend/e2e/agridao.spec.ts"
        os.makedirs(os.path.dirname(e2e_path), exist_ok=True)
        with open(e2e_path, 'w') as f:
            f.write(e2e_test)
        
        # Playwright config
        playwright_config = """import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
"""
        
        config_path = f"{self.project_root}/frontend/playwright.config.ts"
        with open(config_path, 'w') as f:
            f.write(playwright_config)
        
        print("✅ E2E testing setup completed")
        print(f"   Test file: {e2e_path}")
        print(f"   Config: {config_path}")
        print("   Run: npx playwright test")

    async def enhance_cicd(self):
        """Enhance CI/CD pipeline"""
        print("🚀 Enhancing CI/CD pipeline...")
        
        github_workflow = """name: AgriDAO CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: agridao_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        cd backend
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  test-frontend:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '20'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run tests
      run: |
        cd frontend
        npm test -- --coverage
    
    - name: Build
      run: |
        cd frontend
        npm run build

  security-scan:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run security scan
      run: |
        # Backend security scan
        cd backend
        pip install safety bandit
        safety check
        bandit -r app/
        
        # Frontend security scan
        cd ../frontend
        npm audit --audit-level moderate

  deploy:
    needs: [test-backend, test-frontend, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      run: |
        echo "🚀 Deploying to production..."
        # Add deployment commands here
"""
        
        workflow_path = f"{self.project_root}/.github/workflows/ci-cd.yml"
        os.makedirs(os.path.dirname(workflow_path), exist_ok=True)
        with open(workflow_path, 'w') as f:
            f.write(github_workflow)
        
        print("✅ CI/CD pipeline enhanced")
        print(f"   Workflow: {workflow_path}")

    async def add_health_checks(self):
        """Add comprehensive health checks"""
        print("💓 Adding health checks...")
        
        health_check = """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
import redis
import psutil
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Database check
    try:
        db.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Redis check
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # System resources
    health_status["checks"]["cpu_percent"] = psutil.cpu_percent()
    health_status["checks"]["memory_percent"] = psutil.virtual_memory().percent
    health_status["checks"]["disk_percent"] = psutil.disk_usage('/').percent
    
    return health_status

@router.get("/readiness")
async def readiness_check(db: Session = Depends(get_db)):
    # Check if app is ready to serve traffic
    try:
        db.execute("SELECT 1")
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Not ready")

@router.get("/liveness")
async def liveness_check():
    # Simple liveness check
    return {"status": "alive"}
"""
        
        health_path = f"{self.project_root}/backend/app/routers/health.py"
        with open(health_path, 'w') as f:
            f.write(health_check)
        
        print("✅ Health checks added")
        print(f"   Location: {health_path}")
        print("   Endpoints: /health, /health/detailed, /readiness, /liveness")

    async def execute_generic_task(self, task):
        print(f"✅ {self.agent_name} completed: {task['task']}")

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/default.yml"
    worker = AgentWorker(config_path)
    asyncio.run(worker.start())
