# Quick Fix Guide - Admin User Management

## 🔴 Problem: User list not showing

### Fix #1: Create Admin User (Most Common Issue)
```bash
cd backend
python create_admin.py
```
Enter your email and name when prompted.

### Fix #2: Check Your Role
Open browser console (F12) and run:
```javascript
JSON.parse(localStorage.getItem('current_user'))?.role
```
Should return `"admin"` or `"ADMIN"`

### Fix #3: Refresh Token
1. Logout
2. Login again
3. Navigate to `/dashboard`

## 🟡 Problem: 403 Forbidden

You're not an admin. Run:
```bash
cd backend
python create_admin.py
```

## 🟢 Problem: 401 Unauthorized

Token expired. Logout and login again.

## ⚪ Problem: CORS Error

Restart frontend:
```bash
cd frontend
npm run dev
```

## 🔵 Verify Everything Works

1. **Backend running?**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Admin user exists?**
   ```bash
   cd backend
   python create_admin.py
   ```

3. **Logged in as admin?**
   ```javascript
   // Browser console
   JSON.parse(localStorage.getItem('current_user'))
   ```

4. **Can see user list?**
   - Go to `http://localhost:5173/dashboard`
   - Should see "User Management" card

## 📍 Where to Find User Management

### Option 1: Main Dashboard
`http://localhost:5173/dashboard`
- Scroll down to "User Management" card

### Option 2: Admin Dashboard
`http://localhost:5173/admin`
- Click "Users" tab

## ✅ What Should Work

- ✅ Search users by email/name
- ✅ Filter by role (All/Buyer/Farmer/Admin)
- ✅ Update user roles (dropdown)
- ✅ Suspend users (button)
- ✅ Delete users (button with confirmation)
- ✅ Cannot modify your own account

## 🚨 Emergency Reset

If nothing works:
```bash
# 1. Stop everything
docker-compose down

# 2. Restart
docker-compose up -d

# 3. Create admin
cd backend
python create_admin.py

# 4. Clear browser
# - Open DevTools (F12)
# - Application tab
# - Clear Storage
# - Reload page

# 5. Login again
```

## 📞 Need More Help?

See detailed guides:
- `ADMIN_SETUP_INSTRUCTIONS.md` - Full setup guide
- `ADMIN_USER_MANAGEMENT_DEBUG.md` - Debugging steps
