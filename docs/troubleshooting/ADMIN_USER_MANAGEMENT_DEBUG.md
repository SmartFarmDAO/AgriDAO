# Admin User Management - Debugging Guide

## Changes Made

### 1. Frontend API Fix
- **Fixed**: `suspendUser` endpoint in `frontend/src/lib/api.ts`
  - Changed from `/users/{id}/suspend` to `/admin/users/{id}/suspend`

### 2. Enhanced Error Handling in Dashboard
- Added error state display in user list
- Added toast notifications for API errors
- Added console logging for debugging
- Added retry button for failed requests

### 3. User Management Features
Both `/dashboard` and `/admin` now have full user management:
- Search users by email/name
- Filter by role (All, Buyer, Farmer, Admin)
- Update user roles inline
- Suspend users
- Delete users with confirmation

## Backend Endpoints

All endpoints are at `/admin/*` and require admin authentication:

```
GET    /admin/users              - List all users
PUT    /admin/users/{id}/role    - Update user role
POST   /admin/users/{id}/suspend - Suspend user
DELETE /admin/users/{id}         - Delete user
```

## Debugging Steps

### 1. Check if you're logged in as an admin user

Open browser console and run:
```javascript
JSON.parse(localStorage.getItem('current_user'))
```

The `role` field should be `"admin"` or `"ADMIN"`.

### 2. Check the API request

Open Network tab in DevTools and look for:
- Request to `/api/admin/users`
- Check if Authorization header is present
- Check response status code

### 3. Check backend logs

Look for:
- Authentication errors (401)
- Authorization errors (403)
- Any Python exceptions

### 4. Verify admin user exists

Run this SQL query in your database:
```sql
SELECT id, email, role, status FROM user WHERE role = 'admin';
```

### 5. Create an admin user if needed

If no admin user exists, create one:

```python
# In Python shell or create a script
from app.database import engine
from app.models import User, UserRole, UserStatus
from sqlmodel import Session

with Session(engine) as session:
    admin = User(
        name="Admin User",
        email="admin@example.com",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE
    )
    session.add(admin)
    session.commit()
    print(f"Admin user created with ID: {admin.id}")
```

### 6. Test the endpoint directly

Use curl or Postman:
```bash
curl -X GET http://localhost:8000/admin/users \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Common Issues

### Issue 1: "Access Denied" or 403 Error
**Cause**: User is not an admin
**Solution**: Verify user role in database, update if needed

### Issue 2: "Invalid or expired token" or 401 Error
**Cause**: Authentication token is missing or expired
**Solution**: Log out and log back in

### Issue 3: "No users found" but users exist
**Cause**: API endpoint not returning data
**Solution**: Check backend logs, verify database connection

### Issue 4: CORS errors
**Cause**: Frontend and backend on different origins
**Solution**: Verify vite proxy configuration in `frontend/vite.config.ts`

## Testing Checklist

- [ ] Admin user exists in database
- [ ] Can log in as admin user
- [ ] Dashboard shows "Administrator Access" card
- [ ] Dashboard shows "User Management" card
- [ ] Can see user list in dashboard
- [ ] Can search/filter users
- [ ] Can update user roles
- [ ] Can suspend users
- [ ] Can delete users
- [ ] `/admin` route shows full admin dashboard
- [ ] Users tab in admin dashboard works

## Files Modified

1. `frontend/src/lib/api.ts` - Fixed suspendUser endpoint
2. `frontend/src/pages/Dashboard.tsx` - Added user management UI and error handling
3. `backend/app/routers/admin.py` - Already had correct endpoints
4. `backend/app/main.py` - Admin router already registered

## Next Steps if Still Not Working

1. Check browser console for JavaScript errors
2. Check Network tab for failed API requests
3. Check backend logs for Python errors
4. Verify database has users
5. Verify admin user role is correctly set
6. Test backend endpoint directly with curl
7. Clear browser cache and localStorage
8. Restart both frontend and backend servers
