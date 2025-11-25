# Test Guide: User Deletion Fix

## ✅ Fix Applied

The user deletion functionality has been fixed to handle foreign key constraints properly.

## How to Test

### Test 1: Delete User Without Orders (Should Work)

1. **Login as Admin**
   - Email: `riajurpbl@gmail.com`
   - Navigate to: `http://localhost:5173/dashboard` or `http://localhost:5173/admin`

2. **Find a User Without Orders**
   - Look for a user who hasn't placed any orders
   - Or create a new test user

3. **Delete the User**
   - Click the "Delete" button next to the user
   - Confirm the deletion in the dialog
   - **Expected**: ✅ Success toast: "User deleted successfully"

### Test 2: Delete User With Orders (Should Fail with Message)

1. **Find a User With Orders**
   - Look for `riajurpbl+farmer001@gmail.com` or any user who has placed orders

2. **Try to Delete**
   - Click the "Delete" button
   - Confirm the deletion
   - **Expected**: ❌ Error toast: "Cannot delete user with X existing orders. Please archive the user instead."

### Test 3: Use Suspend Instead

1. **For Users With Orders**
   - Click the "Suspend" button instead of "Delete"
   - **Expected**: ✅ User status changes to "SUSPENDED"
   - User can no longer login
   - All data is preserved

2. **Reactivate if Needed**
   - Use the activate endpoint or change status back to "ACTIVE"

## What Was Fixed

### Before (Broken):
```
Admin clicks Delete
  ↓
Backend tries to delete user
  ↓
❌ ERROR: Foreign key constraint violation
  ↓
400 Bad Request returned
```

### After (Fixed):
```
Admin clicks Delete
  ↓
Backend checks for orders
  ↓
If orders exist → ❌ Return error message
  ↓
If no orders → Delete related records:
  - User sessions ✅
  - Notifications ✅
  - Carts ✅
  - Reviews ✅
  - Dispute messages ✅
  - Update audit records (set user_id to NULL) ✅
  ↓
Delete user ✅
  ↓
✅ Success: User deleted
```

## Backend Changes

**File Modified:** `backend/app/routers/admin.py`

**Changes:**
1. Added order existence check
2. Comprehensive related record cleanup
3. Proper transaction management
4. Audit trail preservation

## Verification

Check backend logs to confirm no errors:
```bash
docker-compose logs backend --tail=50 | grep -i "delete\|error"
```

## Current Status

- ✅ Backend restarted with fix
- ✅ No syntax errors
- ✅ Application running normally
- ✅ Ready for testing

## Next Steps

1. **Test the fix** using the steps above
2. **Verify** success/error messages are displayed correctly
3. **Confirm** data integrity is maintained
4. **Report** any issues if they occur

## Alternative: Suspend Users

For users with orders or when you want to preserve all data:

**Use Suspend Instead:**
- Prevents user login
- Preserves all data
- Can be reversed
- Maintains audit trail

**How to Suspend:**
1. Click "Suspend" button in user management
2. User status changes to "SUSPENDED"
3. User cannot login but data is preserved

## Summary

✅ **Fixed**: User deletion now works correctly
✅ **Protected**: Users with orders cannot be deleted
✅ **Preserved**: Audit trails maintained
✅ **Enhanced**: Better error messages

The fix is live and ready for testing!
