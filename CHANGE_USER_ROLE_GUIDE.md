# Guide: Change User Role from Buyer to Farmer

## Situation
User `riajurpbl+farmer001@gmail.com` is currently a BUYER but has completed the farmer registration form and needs to be changed to FARMER role.

## Solution Options

### Option 1: Using Admin Dashboard (Recommended - Easiest)

1. **Login as admin** (`riajurpbl@gmail.com`)

2. **Navigate to Dashboard**
   - Go to `http://localhost:5173/dashboard`

3. **Find the User**
   - Scroll down to "User Management" card
   - Use the search box to search for: `riajurpbl+farmer001@gmail.com`
   - Or scroll through the user list

4. **Change Role**
   - Find the "Role" column for this user
   - Click the dropdown (currently shows "Buyer")
   - Select "Farmer" from the dropdown
   - The role will be updated automatically
   - You'll see a success toast notification

5. **Verify**
   - The user's role should now show "Farmer" in the list
   - A green dot indicator will appear next to "Farmer"

6. **User Must Logout/Login**
   - The user `riajurpbl+farmer001@gmail.com` must logout and login again
   - After login, they will see farmer features in their dashboard

### Option 2: Using /admin Dashboard

1. **Login as admin** (`riajurpbl@gmail.com`)

2. **Navigate to Admin Dashboard**
   - Go to `http://localhost:5173/admin`

3. **Click Users Tab**
   - Click on the "Users" tab at the top

4. **Find and Update User**
   - Search for `riajurpbl+farmer001@gmail.com`
   - Change role from "Buyer" to "Farmer" using dropdown
   - Success toast will appear

5. **User Must Logout/Login**
   - User needs to logout and login to see changes

### Option 3: Using /users Page

1. **Login as admin** (`riajurpbl@gmail.com`)

2. **Navigate to User Management**
   - Go to `http://localhost:5173/users`

3. **Find User**
   - Search for `riajurpbl+farmer001@gmail.com` in the table

4. **Edit User**
   - Click the edit icon (pencil) for this user
   - In the edit dialog, change role to "Farmer"
   - Click "Save Changes"

5. **User Must Logout/Login**
   - User needs to logout and login to see changes

### Option 4: Using Backend Script (For Database Issues)

If the UI methods don't work, use the backend script:

```bash
cd backend
python update_user_role.py
```

The script will:
- Check if user exists
- Show current role
- Show if farmer profile exists
- Offer to update role to FARMER
- List all farmer profiles

Follow the prompts to update the user role.

## Verification Steps

After changing the role:

1. **Check in Admin Dashboard**
   - User should show as "Farmer" in user list
   - Green dot indicator next to role

2. **User Logs Out and Back In**
   - User `riajurpbl+farmer001@gmail.com` must logout
   - Login again with same credentials
   - Navigate to `/dashboard`

3. **Verify Farmer Features**
   - Dashboard should show farmer-specific features:
     - "My Products" section
     - "Add New Product" button
     - Product management tools
     - No "Become a Farmer" CTA

4. **Check Farmer Profile**
   - User should be able to add products
   - Products should be linked to their farmer profile

## Common Issues

### Issue 1: Role changes but user still sees buyer dashboard

**Cause**: User hasn't logged out and back in

**Solution**: 
1. User must logout completely
2. Clear browser cache (optional but recommended)
3. Login again
4. Navigate to `/dashboard`

### Issue 2: No farmer profile exists

**Cause**: User submitted form but it failed or wasn't saved

**Solution**:
1. Check if farmer profile exists:
   ```bash
   cd backend
   python update_user_role.py
   ```
2. If no farmer profile, user should:
   - Go to `/onboarding`
   - Complete the farmer registration form again
   - Submit the form

### Issue 3: Role update fails in UI

**Cause**: API error or permission issue

**Solution**:
1. Check browser console for errors
2. Check Network tab for failed requests
3. Use backend script instead:
   ```bash
   cd backend
   python update_user_role.py
   ```

## Quick Command Reference

### Check user and farmer profile:
```bash
cd backend
python update_user_role.py
```

### Manually update in database (if needed):
```sql
-- Check current role
SELECT id, email, name, role FROM user WHERE email = 'riajurpbl+farmer001@gmail.com';

-- Update role to FARMER
UPDATE user SET role = 'FARMER' WHERE email = 'riajurpbl+farmer001@gmail.com';

-- Verify update
SELECT id, email, name, role FROM user WHERE email = 'riajurpbl+farmer001@gmail.com';

-- Check if farmer profile exists
SELECT * FROM farmer WHERE email = 'riajurpbl+farmer001@gmail.com';
```

## Expected Result

After successful role change:

✅ User role in database: `FARMER`
✅ User can see farmer dashboard features
✅ User can add products
✅ User can manage their products
✅ Products are linked to their farmer profile
✅ User appears as "Farmer" in admin user list

## Important Notes

1. **User MUST logout and login** after role change
2. **Farmer profile should exist** - if not, user needs to complete onboarding form
3. **Admin can change roles anytime** using the dashboard dropdown
4. **Changes are immediate** in database but require re-login to take effect in UI
5. **Cannot change own role** - admin cannot change their own role via UI

## Support

If issues persist:
1. Check `update_user_role.py` script output
2. Verify database has correct role
3. Verify farmer profile exists
4. Check browser console for errors
5. Clear browser cache and localStorage
6. Restart backend if needed
