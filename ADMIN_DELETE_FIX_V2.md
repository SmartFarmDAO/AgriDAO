# Admin User Delete - Fix Version 2

## Issue
After the first fix, the delete function is now showing 500 errors, likely due to trying to access tables or set fields that don't allow NULL values.

## Solution Applied

Simplified the delete function to:

1. **Focus on Essential Cleanup**
   - Only delete records from tables that definitely exist
   - Use try-except blocks for optional tables

2. **Removed Complex Updates**
   - Removed attempts to set NOT NULL fields to NULL
   - Removed references to tables that might not exist (OrderReview, Dispute, etc.)

3. **Core Cleanup Only**
   - UserSession (required - causes the original 400 error)
   - Notification (optional)
   - Cart (optional)

4. **Better Error Handling**
   - Wrapped entire function in try-except
   - Returns clear error message on failure
   - Re-raises HTTPException for proper status codes

## Code Changes

### Before (Complex - Causing 500 errors):
```python
# Tried to update many tables
# Set NOT NULL fields to NULL
# Referenced tables that might not exist
```

### After (Simple - Should work):
```python
# Delete only essential records
# Use try-except for optional tables
# Proper error handling
# Clear error messages
```

## What Gets Deleted

✅ **Always Deleted:**
- User sessions (prevents 400 error)

✅ **Deleted if exists:**
- Notifications
- Shopping carts

❌ **Not Deleted (Protected):**
- Users with orders (returns 400 error with message)

## Testing

1. **Restart backend:**
   ```bash
   docker-compose restart backend
   ```

2. **Test deletion:**
   - Try to delete a user without orders
   - Should succeed with 204 No Content

3. **Check logs:**
   ```bash
   docker-compose logs backend --tail=50
   ```

## If Still Getting 500 Errors

The error message will now show the actual problem. Check:

1. **Backend logs** for the specific error
2. **Database schema** - ensure UserSession table exists
3. **Foreign key constraints** - check what's blocking deletion

## Alternative: Simplest Solution

If issues persist, use the absolute simplest version:

```python
@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, current_user: User = Depends(require_admin)):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot delete yourself")
        
        # Delete sessions only
        from ..models import UserSession
        sessions = session.exec(select(UserSession).where(UserSession.user_id == user_id)).all()
        for s in sessions:
            session.delete(s)
        session.commit()
        
        # Delete user
        session.delete(user)
        session.commit()
```

This minimal version:
- Only handles UserSession (the main cause of 400 error)
- No complex logic
- Should work reliably

## Status

✅ Simplified version applied
✅ Better error handling added
✅ Ready for testing

Next: Restart backend and test
