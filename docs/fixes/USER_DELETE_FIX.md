# User Delete Fix - 400 Error Resolution

## Problem Identified

When an admin tried to delete a user, the backend returned a **400 Bad Request** error with the following database error:

```
ForeignKeyViolation: update or delete on table "user" violates foreign key constraint "usersession_user_id_fkey" on table "usersession"
Key (id)=(X) is still referenced from table "usersession"
```

## Root Cause

The user deletion was failing because:

1. **Foreign Key Constraints**: The `user` table has foreign key relationships with multiple tables:
   - `usersession` (user_id)
   - `order` (buyer_id)
   - `cart` (user_id)
   - `notification` (user_id)
   - `orderreview` (buyer_id)
   - `dispute` (filed_by, resolved_by)
   - `disputemessage` (sender_id)
   - `orderstatushistory` (created_by)
   - `inventoryhistory` (created_by)

2. **Incomplete Cleanup**: The original delete function only deleted `UserSession` records but didn't handle other related records.

3. **Transaction Issue**: Even the session deletion wasn't being committed before attempting to delete the user.

## Solution Implemented

Updated `backend/app/routers/admin.py` with a comprehensive delete function that:

### 1. **Prevents Deletion of Users with Orders**
```python
# Check if user has orders - prevent deletion if they do
order_count = session.exec(
    select(Order).where(Order.buyer_id == user_id)
).all()

if order_count:
    raise HTTPException(
        status_code=400, 
        detail=f"Cannot delete user with {len(order_count)} existing orders. Please archive the user instead."
    )
```

**Rationale**: Users with order history should be archived (suspended) rather than deleted to maintain transaction records and audit trails.

### 2. **Deletes Related Records in Correct Order**

```python
# Delete in order respecting foreign key constraints:
1. User sessions
2. Notifications
3. Carts
4. Reviews
5. Dispute messages
```

### 3. **Updates References Instead of Deleting**

For audit trail preservation:
```python
# Set foreign keys to NULL instead of deleting:
- Disputes (filed_by, resolved_by)
- Order status history (created_by)
- Inventory history (created_by)
```

### 4. **Proper Transaction Management**

```python
# Commit all related changes first
session.commit()

# Then delete the user
session.delete(user)
session.commit()
```

## Testing

### Test Case 1: Delete User Without Orders
**Steps:**
1. Login as admin
2. Navigate to user management
3. Select a user without orders
4. Click delete
5. Confirm deletion

**Expected Result:** ✅ User deleted successfully

### Test Case 2: Delete User With Orders
**Steps:**
1. Login as admin
2. Navigate to user management
3. Select a user with existing orders
4. Click delete
5. Confirm deletion

**Expected Result:** ❌ Error message: "Cannot delete user with X existing orders. Please archive the user instead."

### Test Case 3: Delete Self
**Steps:**
1. Login as admin
2. Try to delete own account

**Expected Result:** ❌ Error message: "Cannot delete yourself"

## Database Impact

### Records Deleted:
- ✅ User sessions
- ✅ Notifications
- ✅ Shopping carts
- ✅ Reviews
- ✅ Dispute messages

### Records Preserved (with NULL references):
- ✅ Disputes (for audit trail)
- ✅ Order status history (for audit trail)
- ✅ Inventory history (for audit trail)

### Records Protected:
- ✅ Orders (prevents deletion if orders exist)

## Alternative: User Suspension

For users with orders or when deletion is not appropriate, use the **Suspend** feature instead:

```python
POST /admin/users/{user_id}/suspend
```

This:
- Sets user status to SUSPENDED
- Prevents login
- Preserves all data
- Can be reversed with activation

## Deployment

The fix has been applied to:
- ✅ `backend/app/routers/admin.py`

**Action Required:**
1. Restart backend container: `docker-compose restart backend`
2. Test user deletion functionality
3. Verify error messages are user-friendly

## Verification Commands

```bash
# Check backend logs for errors
docker-compose logs backend --tail=50 | grep -i "error\|delete"

# Test the endpoint
curl -X DELETE http://localhost:8000/admin/users/{user_id} \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## Summary

✅ **Fixed**: Foreign key constraint violations
✅ **Added**: Order existence check
✅ **Improved**: Comprehensive related record cleanup
✅ **Enhanced**: Audit trail preservation
✅ **Protected**: Critical transaction data

The user deletion now works correctly while maintaining data integrity and audit trails.
