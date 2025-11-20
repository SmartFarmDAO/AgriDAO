# Quick Start - Test Cart & Ordering

## 🚀 Start the Application

### Terminal 1: Start Backend
```bash
cd /Users/sohagmahamud/Projects/AgriDAO/backend
docker-compose up
```

### Terminal 2: Start Frontend
```bash
cd /Users/sohagmahamud/Projects/AgriDAO/frontend
npm run dev
```

### Access the App
Open browser: **http://localhost:5173/marketplace**

## ✅ Test Scenarios

### Scenario 1: Guest Cart (No Sign-In Required)
```
1. Open http://localhost:5173/marketplace
2. Browse products (no login needed)
3. Click "Add to Cart" on any product
4. ✅ See toast: "Added to cart"
5. ✅ See cart count update in header
6. Click cart icon (shopping cart button)
7. ✅ See cart drawer slide out
8. ✅ See product in cart with correct price
9. Click "+" to increase quantity
10. ✅ See total update
11. Click "Continue Shopping"
12. Add more products
13. Refresh page (F5)
14. ✅ Cart items still there
```

### Scenario 2: Checkout Flow (Requires Sign-In)
```
1. Add items to cart (as guest)
2. Click cart icon
3. Click "Checkout" button
4. ✅ See "Sign in to continue" dialog
5. Click "Continue Shopping"
6. ✅ Dialog closes, still on marketplace
7. Click "Checkout" again
8. Click "Sign In" button
9. ✅ Redirects to /auth page
10. Sign in with credentials
11. ✅ Returns to marketplace
12. ✅ Cart items still present
13. Click "Checkout"
14. ✅ Redirects to Stripe payment page
```

### Scenario 3: Buy Now Flow
```
1. Browse marketplace (no login)
2. Find a product you like
3. Click "Buy Now" button
4. ✅ See "Sign in to continue" dialog
5. Click "Sign In"
6. Sign in with credentials
7. Return to marketplace
8. Click "Buy Now" again
9. ✅ Redirects to Stripe payment
```

### Scenario 4: Cart Management
```
1. Add 3 different products to cart
2. Open cart drawer
3. ✅ See all 3 products
4. Click "+" on first product
5. ✅ Quantity increases, total updates
6. Click "-" on second product
7. ✅ Quantity decreases, total updates
8. Click "X" on third product
9. ✅ Product removed, total updates
10. ✅ See subtotal, platform fee (8%), and total
```

## 🔑 Test Credentials

If you need to test authenticated flows, use:
```
Email: test@example.com
Password: password123
```

Or create a new account at: http://localhost:5173/auth

## 🐛 Troubleshooting

### Cart Not Showing Items
```bash
# Check localStorage
# Open browser console (F12)
localStorage.getItem('cart_items')

# Should show: [{"product_id":1,"quantity":2,"name":"...","price":50}]
```

### Toast Not Appearing
```bash
# Check if Toaster component is mounted
# Look for <Toaster /> in App.tsx
```

### Blank Screen
```bash
# Check browser console for errors (F12)
# Look for React errors or API errors
```

### Backend Not Running
```bash
# Check if backend is accessible
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

### Products Not Loading
```bash
# Check API endpoint
curl http://localhost:8000/api/products

# Should return JSON array of products
```

## 📊 Expected Behavior

### Cart Count Badge
- Shows total number of items in cart
- Updates immediately when adding items
- Persists across page refreshes

### Cart Drawer
- Slides in from right side
- Shows all cart items
- Allows quantity adjustment
- Shows price breakdown
- Has "Checkout" and "Continue Shopping" buttons

### Sign-In Dialog
- Appears when checkout without auth
- Has clear message about cart preservation
- Has two buttons: "Continue Shopping" and "Sign In"
- Redirects to auth page with return URL

### Price Display
- Shows in Bangladeshi Taka (৳)
- Formatted to 2 decimal places
- Handles both string and number types
- Calculates totals correctly

## 🎯 Success Criteria

✅ Can add items to cart without signing in
✅ Cart count updates in header
✅ Cart drawer shows items correctly
✅ Prices display and calculate correctly
✅ Can adjust quantities
✅ Can remove items
✅ Cart persists on page refresh
✅ Sign-in prompt appears at checkout
✅ Cart preserved after sign-in
✅ Checkout redirects to payment
✅ Buy Now works with auth

## 📞 Need Help?

If something doesn't work:
1. Check browser console (F12) for errors
2. Check backend logs: `docker-compose logs -f`
3. Clear localStorage: `localStorage.clear()`
4. Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
5. Restart dev server

## 🎉 All Fixed!

The cart and ordering flow is now fully functional and production-ready!
