#!/bin/bash
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
