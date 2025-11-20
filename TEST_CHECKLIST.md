# Test Checklist - Admin User Management Fix

## Pre-Test Setup
- [ ] Backend is running (`docker-compose up -d` or `python -m uvicorn app.main:app`)
- [ ] Frontend is running (`npm run dev`)
- [ ] Logged in as admin user: `riajurpbl@gmail.com`

## Test 1: Dashboard User Management
- [ ] Navigate to `http://localhost:5173/dashboard`
- [ ] Verify "Administrator Access" card is visible (purple background)
- [ ] Verify "User Management" card is visible below
- [ ] Verify user list is displayed in the User Management card
- [ ] Verify search box is present
- [ ] Verify role filter dropdown is present
- [ ] Verify user count badge shows correct number

## Test 2: Search and Filter
- [ ] Type in search box - verify users are filtered by email/name
- [ ] Select "Buyers" from role filter - verify only buyers shown
- [ ] Select "Farmers" from role filter - verify only farmers shown
- [ ] Select "Admins" from role filter - verify only admins shown
- [ ] Select "All Roles" - verify all users shown again

## Test 3: User Actions from Dashboard
- [ ] Click role dropdown for a user - verify can change role
- [ ] Change a user's role - verify success toast appears
- [ ] Click "Suspend" button - verify confirmation dialog
- [ ] Confirm suspension - verify success toast
- [ ] Click "Delete" button - verify confirmation dialog with warnings
- [ ] Cancel deletion - verify user not deleted
- [ ] Verify cannot modify own account (buttons disabled)

## Test 4: UserManagement Page (/users)
- [ ] Click "User Management" button in Administrator Access card
- [ ] Verify redirected to `/users`
- [ ] Verify page loads WITHOUT "Network Error"
- [ ] Verify user list is displayed
- [ ] Verify "Add User" button is present
- [ ] Verify all users are shown in table

## Test 5: User Actions from /users Page
- [ ] Click edit icon for a user
- [ ] Verify edit dialog opens
- [ ] Modify user details
- [ ] Save changes - verify success toast
- [ ] Click suspend icon - verify user suspended
- [ ] Click delete icon - verify confirmation dialog
- [ ] Delete a test user - verify success

## Test 6: Admin Dashboard (/admin)
- [ ] Navigate to `http://localhost:5173/admin`
- [ ] Verify admin dashboard loads
- [ ] Click "Users" tab
- [ ] Verify user list is displayed
- [ ] Verify all functionality works (search, filter, update, suspend, delete)

## Test 7: Error Handling
- [ ] Logout and login as non-admin user
- [ ] Navigate to `/dashboard` - verify NO user management card
- [ ] Try to access `/users` - verify "Access Denied" message
- [ ] Try to access `/admin` - verify "Access Denied" message

## Test 8: Browser Console
- [ ] Open DevTools (F12)
- [ ] Check Console tab - verify NO errors
- [ ] Check Network tab - verify `/api/admin/users` request succeeds (200 OK)
- [ ] Verify Authorization header is present in request

## Expected Results

### ✅ All tests should pass with:
- No "Network Error" messages
- No 403 Forbidden errors
- No 401 Unauthorized errors
- User list loads successfully
- All CRUD operations work
- Toast notifications appear for all actions
- Cannot modify own admin account

### ❌ If any test fails:
1. Check browser console for errors
2. Check Network tab for failed requests
3. Verify logged in as admin user
4. Check backend logs
5. Verify database has users
6. See `ADMIN_USER_MANAGEMENT_DEBUG.md` for detailed debugging

## Quick Verification Commands

### Check if logged in as admin:
```javascript
// In browser console
JSON.parse(localStorage.getItem('current_user'))
// Should show: { ..., role: "admin", ... }
```

### Check API endpoint:
```bash
# Get your access token from localStorage
# Then test the endpoint:
curl -X GET http://localhost:8000/admin/users \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Check backend logs:
```bash
docker-compose logs backend -f
# or if running locally, check terminal output
```

## Success Criteria

✅ **Fix is successful if:**
1. Admin user can see user list in `/dashboard`
2. Clicking "User Management" navigates to `/users` without errors
3. `/users` page loads user list successfully
4. All user management operations work (search, filter, update, suspend, delete)
5. No "Network Error" or API errors in console
6. Both `/dashboard` and `/admin` show user management functionality

## Rollback Plan

If issues persist:
1. Check `FIX_SUMMARY.md` for what was changed
2. Verify `frontend/src/pages/UserManagement.tsx` uses `listAllUsers`
3. Verify `frontend/src/lib/api.ts` has correct endpoints
4. Clear browser cache and localStorage
5. Restart frontend and backend servers
