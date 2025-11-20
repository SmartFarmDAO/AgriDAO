# Quick Guide: Change riajurpbl+farmer001@gmail.com to Farmer

## Fastest Method (30 seconds)

1. **Login as admin**: `riajurpbl@gmail.com`

2. **Go to dashboard**: `http://localhost:5173/dashboard`

3. **Search for user**: Type `riajurpbl+farmer001` in search box

4. **Change role**: Click dropdown → Select "Farmer"

5. **Done!** ✅ Success toast will appear

## User Must Do This

The user `riajurpbl+farmer001@gmail.com` must:
1. **Logout**
2. **Login again**
3. Go to `/dashboard` to see farmer features

## Alternative: Use Script

```bash
cd backend
python update_user_role.py
```

Follow prompts to update role.

## Verify It Worked

After user logs back in:
- ✅ Dashboard shows "My Products" section
- ✅ "Add New Product" button visible
- ✅ No "Become a Farmer" CTA
- ✅ Can create and manage products

## If It Doesn't Work

1. Check browser console for errors
2. User must clear cache and logout/login
3. Run `python update_user_role.py` to verify database
4. Check if farmer profile exists

---

**That's it!** The role change takes 30 seconds via the admin dashboard.
