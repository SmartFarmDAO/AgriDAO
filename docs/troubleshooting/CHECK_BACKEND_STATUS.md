# Check Backend Status and Logs

## Quick Backend Health Check

### 1. Check if Backend is Running

```bash
# Check backend health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy"}
```

### 2. Check Backend Logs

#### If using Docker:
```bash
# View live logs
docker-compose logs backend -f

# View last 50 lines
docker-compose logs backend --tail=50

# View logs with timestamps
docker-compose logs backend -t --tail=100
```

#### If running locally:
Check the terminal where you ran:
```bash
python -m uvicorn app.main:app --reload
```

### 3. Test Admin Endpoints

```bash
# First, get your access token from browser localStorage
# Open browser console and run:
# localStorage.getItem('access_token')

# Then test the admin users endpoint:
curl -X GET http://localhost:8000/admin/users \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"

# Expected: JSON array of users
```

### 4. Check Specific User

```bash
cd backend
python update_user_role.py
```

This will show:
- User details for `riajurpbl+farmer001@gmail.com`
- Current role
- Whether farmer profile exists
- Option to update role

## Common Backend Issues

### Issue 1: Backend Not Running

**Symptoms:**
- `curl http://localhost:8000/health` fails
- Network errors in browser console
- "Failed to fetch" errors

**Solution:**
```bash
# Start backend
docker-compose up -d backend

# Or if running locally:
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Issue 2: Database Connection Error

**Symptoms:**
- Backend logs show database errors
- "Connection refused" errors
- SQLAlchemy errors

**Solution:**
```bash
# Check database is running
docker-compose ps

# Restart database
docker-compose restart db

# Check database logs
docker-compose logs db --tail=50
```

### Issue 3: Authentication Errors

**Symptoms:**
- 401 Unauthorized errors
- "Invalid token" errors
- User logged out unexpectedly

**Solution:**
1. User needs to logout and login again
2. Clear browser localStorage
3. Check backend logs for JWT errors

### Issue 4: Admin Endpoint 403 Forbidden

**Symptoms:**
- Can access `/dashboard` but not user list
- "Admin access required" error
- 403 status code

**Solution:**
```bash
# Check user role in database
cd backend
python update_user_role.py

# Or manually check:
# SELECT email, role FROM user WHERE email = 'riajurpbl@gmail.com';
```

## Backend Log Patterns to Look For

### ✅ Good Logs (Normal Operation):
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:xxxxx - "GET /admin/users HTTP/1.1" 200 OK
```

### ⚠️ Warning Logs (May Need Attention):
```
WARNING:  CORS: Origin 'http://localhost:5173' not in allowed origins
WARNING:  Rate limit exceeded for IP xxx.xxx.xxx.xxx
```

### ❌ Error Logs (Need Fixing):
```
ERROR:    Exception in ASGI application
ERROR:    Database connection failed
ERROR:    Invalid token
ERROR:    User not found
ERROR:    Admin access required
```

## Specific Checks for User Role Issue

### 1. Check User Exists and Role
```bash
cd backend
python -c "
from app.database import engine
from app.models import User
from sqlmodel import Session, select

with Session(engine) as session:
    user = session.exec(
        select(User).where(User.email == 'riajurpbl+farmer001@gmail.com')
    ).first()
    if user:
        print(f'User found: {user.email}')
        print(f'Role: {user.role}')
        print(f'Status: {user.status}')
    else:
        print('User not found')
"
```

### 2. Check Farmer Profile Exists
```bash
cd backend
python -c "
from app.database import engine
from app.models import Farmer
from sqlmodel import Session, select

with Session(engine) as session:
    farmer = session.exec(
        select(Farmer).where(Farmer.email == 'riajurpbl+farmer001@gmail.com')
    ).first()
    if farmer:
        print(f'Farmer profile found: {farmer.name}')
        print(f'Location: {farmer.location}')
    else:
        print('No farmer profile found')
"
```

### 3. Check Admin User
```bash
cd backend
python -c "
from app.database import engine
from app.models import User
from sqlmodel import Session, select

with Session(engine) as session:
    admin = session.exec(
        select(User).where(User.email == 'riajurpbl@gmail.com')
    ).first()
    if admin:
        print(f'Admin user: {admin.email}')
        print(f'Role: {admin.role}')
    else:
        print('Admin user not found')
"
```

## Quick Diagnostic Script

Run this to check everything at once:

```bash
cd backend
python << 'EOF'
from app.database import engine
from app.models import User, Farmer
from sqlmodel import Session, select

print("=" * 60)
print("Backend Diagnostic Check")
print("=" * 60)

with Session(engine) as session:
    # Check admin user
    print("\n1. Admin User Check:")
    admin = session.exec(
        select(User).where(User.email == 'riajurpbl@gmail.com')
    ).first()
    if admin:
        print(f"   ✓ Admin found: {admin.email} (Role: {admin.role})")
    else:
        print("   ✗ Admin user not found!")
    
    # Check buyer/farmer user
    print("\n2. Buyer/Farmer User Check:")
    user = session.exec(
        select(User).where(User.email == 'riajurpbl+farmer001@gmail.com')
    ).first()
    if user:
        print(f"   ✓ User found: {user.email}")
        print(f"   - Role: {user.role}")
        print(f"   - Status: {user.status}")
    else:
        print("   ✗ User not found!")
    
    # Check farmer profile
    print("\n3. Farmer Profile Check:")
    farmer = session.exec(
        select(Farmer).where(Farmer.email == 'riajurpbl+farmer001@gmail.com')
    ).first()
    if farmer:
        print(f"   ✓ Farmer profile found: {farmer.name}")
        print(f"   - Location: {farmer.location}")
    else:
        print("   ✗ No farmer profile found")
    
    # Count all users
    print("\n4. Total Users:")
    total = session.exec(select(User)).all()
    print(f"   Total users in database: {len(total)}")
    
    # Count farmers
    print("\n5. Total Farmers:")
    farmers = session.exec(select(Farmer)).all()
    print(f"   Total farmer profiles: {len(farmers)}")

print("\n" + "=" * 60)
EOF
```

## Next Steps Based on Logs

### If Backend Shows Errors:
1. Copy the error message
2. Check if it's a database connection issue
3. Check if it's an authentication issue
4. Restart backend if needed

### If No Errors in Backend:
1. Issue is likely in frontend
2. Check browser console
3. Check Network tab for failed requests
4. Clear browser cache and localStorage

### If User Role Issue:
1. Run `python update_user_role.py`
2. Update role to FARMER
3. User must logout and login
4. Verify in admin dashboard

## Support Commands

```bash
# Restart everything
docker-compose restart

# View all logs
docker-compose logs -f

# Check running services
docker-compose ps

# Stop and start fresh
docker-compose down
docker-compose up -d

# Check database
docker-compose exec db psql -U postgres -d agridao -c "SELECT email, role FROM user;"
```
