# Admin User Management - Setup Instructions

## ✅ What Was Fixed

### 1. API Endpoint Correction
- Fixed `suspendUser` function to call `/admin/users/{id}/suspend` instead of `/users/{id}/suspend`

### 2. Enhanced Error Handling
- Added error display in Dashboard user list
- Added toast notifications for API errors
- Added detailed console logging
- Added retry functionality

### 3. User Management UI
Admin users can now manage users from **both** `/dashboard` and `/admin` routes with:
- Search by email/name
- Filter by role
- Update roles inline
- Suspend users
- Delete users

## 🚀 Quick Start

### Step 1: Ensure Backend is Running

```bash
# Start the backend with docker-compose
docker-compose up -d backend

# Or if running locally
cd backend
python -m uvicorn app.main:app --reload
```

### Step 2: Create an Admin User

```bash
cd backend
python create_admin.py
```

Follow the prompts to create or update an admin user.

### Step 3: Start Frontend

```bash
cd frontend
npm run dev
```

### Step 4: Login as Admin

1. Go to `http://localhost:5173/auth`
2. Login with your admin email
3. Navigate to `/dashboard` or `/admin`

## 🔍 Troubleshooting

### Problem: "No users found" or empty user list

**Solution 1: Check if you're logged in as admin**
```javascript
// In browser console
const user = JSON.parse(localStorage.getItem('current_user'));
console.log('Role:', user?.role);
// Should show "admin" or "ADMIN"
```

**Solution 2: Verify admin user exists in database**
```bash
cd backend
python create_admin.py
```

**Solution 3: Check browser console for errors**
- Open DevTools (F12)
- Check Console tab for JavaScript errors
- Check Network tab for failed API requests

### Problem: 403 Forbidden Error

**Cause**: User is not an admin

**Solution**: Update user role to admin
```bash
cd backend
python create_admin.py
# Enter your email when prompted
```

### Problem: 401 Unauthorized Error

**Cause**: Token expired or invalid

**Solution**: 
1. Logout
2. Clear browser localStorage
3. Login again

### Problem: CORS errors

**Cause**: Frontend/backend communication issue

**Solution**: Verify vite proxy is working
```bash
# Check vite.config.ts has:
proxy: {
  '/api': {
    target: 'http://backend:8000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, '')
  }
}
```

## 📋 Testing Checklist

Run through this checklist to verify everything works:

- [ ] Backend is running (`http://localhost:8000/docs`)
- [ ] Frontend is running (`http://localhost:5173`)
- [ ] Admin user exists in database
- [ ] Can login as admin user
- [ ] Dashboard shows "Administrator Access" card
- [ ] Dashboard shows "User Management" card with user list
- [ ] Can search users
- [ ] Can filter users by role
- [ ] Can update user roles
- [ ] Can suspend users
- [ ] Can delete users (with confirmation)
- [ ] `/admin` route shows full admin dashboard
- [ ] Users tab in `/admin` works

## 🔧 Manual Database Check

If you need to manually check/update the database:

```sql
-- Check all users
SELECT id, email, name, role, status FROM user;

-- Update a user to admin
UPDATE user SET role = 'admin', status = 'active' WHERE email = 'your@email.com';

-- Create a new admin user
INSERT INTO user (name, email, role, status, email_verified, created_at, updated_at)
VALUES ('Admin User', 'admin@example.com', 'admin', 'active', 1, NOW(), NOW());
```

## 📁 Files Modified

### Frontend
- `frontend/src/lib/api.ts` - Fixed suspendUser endpoint
- `frontend/src/pages/Dashboard.tsx` - Added user management UI

### Backend
- `backend/app/routers/admin.py` - Already correct
- `backend/app/main.py` - Admin router already registered
- `backend/create_admin.py` - **NEW** - Helper script to create admin users

## 🎯 API Endpoints

All admin endpoints require authentication with admin role:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/users` | List all users |
| PUT | `/admin/users/{id}/role` | Update user role |
| POST | `/admin/users/{id}/suspend` | Suspend user |
| DELETE | `/admin/users/{id}` | Delete user |

## 💡 Tips

1. **Always use the create_admin.py script** to create/update admin users
2. **Check browser console** for detailed error messages
3. **Check Network tab** to see actual API requests/responses
4. **Clear cache** if you see stale data
5. **Restart servers** if changes don't appear

## 🆘 Still Not Working?

1. Check `ADMIN_USER_MANAGEMENT_DEBUG.md` for detailed debugging steps
2. Verify all services are running: `docker-compose ps`
3. Check backend logs: `docker-compose logs backend`
4. Check database connection
5. Verify environment variables are set correctly

## 📞 Support

If you're still experiencing issues:
1. Check browser console for errors
2. Check backend logs for Python exceptions
3. Verify database has users with admin role
4. Test backend endpoint directly with curl
5. Review the debug guide in `ADMIN_USER_MANAGEMENT_DEBUG.md`
